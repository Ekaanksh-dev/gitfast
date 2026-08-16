import subprocess
from gitfast.utils.git import run_git, is_git_repo, current_branch
from gitfast.utils.colors import Printer
from gitfast.merge.detector import scan_repo


# push error types
ERROR_REJECTED        = "rejected"
ERROR_NO_UPSTREAM     = "no_upstream"
ERROR_PERMISSION      = "permission"
ERROR_REPO_NOT_FOUND  = "repo_not_found"
ERROR_LARGE_FILE      = "large_file"
ERROR_UNKNOWN         = "unknown"


def detect_push_error(stderr):
    """Identify what kind of push error occurred"""

    if not stderr:
        return ERROR_UNKNOWN

    stderr_lower = stderr.lower()

    if "rejected" in stderr_lower or "remote contains work" in stderr_lower:
        return ERROR_REJECTED

    if "no upstream branch" in stderr_lower:
        return ERROR_NO_UPSTREAM

    if "permission denied" in stderr_lower:
        return ERROR_PERMISSION

    if "repository not found" in stderr_lower:
        return ERROR_REPO_NOT_FOUND

    if "large file" in stderr_lower or "file size" in stderr_lower:
        return ERROR_LARGE_FILE

    return ERROR_UNKNOWN


def resolve_push_error(stderr, branch=None):
    """
    Auto resolve push errors
    Returns True if resolved and push succeeded
    """
    error_type = detect_push_error(stderr)
    branch     = branch or current_branch()

    Printer.divider()

    if error_type == ERROR_REJECTED:
        return _fix_rejected(branch)

    elif error_type == ERROR_NO_UPSTREAM:
        return _fix_no_upstream(branch)

    elif error_type == ERROR_PERMISSION:
        return _fix_permission()

    elif error_type == ERROR_REPO_NOT_FOUND:
        return _fix_repo_not_found()

    elif error_type == ERROR_LARGE_FILE:
        return _fix_large_file(stderr)

    else:
        Printer.error("Unknown push error")
        print(f"\n  {stderr}\n")
        return False


def _fix_rejected(branch):
    """
    Fix: remote has new work you don't have locally
    Solution: pull + merge + push again
    """
    Printer.warning("Push rejected — remote has new changes")
    Printer.step("Auto-pulling remote changes...")

    # pull
    result = subprocess.run(
        ["git", "pull", "origin", branch],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        stderr = result.stderr

        # check if pull caused conflicts
        if "conflict" in stderr.lower():
            Printer.error("Pull caused merge conflicts")
            Printer.info("Auto-resolving conflicts...")

            # run gmerge
            from gitfast.merge.resolver import gmerge
            resolved = gmerge()

            if not resolved:
                Printer.error("Could not auto-resolve conflicts")
                Printer.info("Run: gmerge -i for interactive resolver")
                return False
        else:
            Printer.error(f"Pull failed: {stderr}")
            return False

    # check for conflicts after pull
    conflicts = scan_repo()
    if conflicts:
        Printer.warning("Conflicts found after pull")
        Printer.info("Auto-resolving...")

        from gitfast.merge.resolver import gmerge
        resolved = gmerge()

        if not resolved:
            Printer.error("Could not resolve conflicts")
            Printer.info("Run: gmerge -i for interactive resolver")
            return False

    # push again
    Printer.push(f"Pushing to {branch}...")
    result = subprocess.run(
        ["git", "push", "origin", branch],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        Printer.success("Push successful after auto-fix")
        return True
    else:
        Printer.error(f"Push still failing: {result.stderr}")
        return False


def _fix_no_upstream(branch):
    """
    Fix: no upstream branch set
    Solution: set upstream and push
    """
    Printer.warning(f"No upstream branch for: {branch}")
    Printer.step("Setting upstream and pushing...")

    result = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        Printer.success(f"Upstream set and pushed: {branch}")
        return True
    else:
        Printer.error(f"Failed: {result.stderr}")
        return False


def _fix_permission():
    """
    Fix: permission denied
    Solution: guide user to fix auth
    """
    Printer.error("Permission denied — auth issue detected")
    print("")
    print("  Possible fixes:")
    print("")
    print("  [1] SSH not set up    → run: gsetup_ssh")
    print("  [2] Token expired     → run: gtoken refresh")
    print("  [3] Wrong remote URL  → run: gauth_info")
    print("  [4] HTTPS not SSH     → run: ghttps_to_ssh")
    print("")
    return False


def _fix_repo_not_found():
    """
    Fix: repository not found
    Solution: show remote URL and guide user
    """
    Printer.error("Repository not found")

    out, _, _ = run_git("remote -v")
    if out:
        print(f"\n  Current remote:\n  {out}\n")

    print("  Possible fixes:")
    print("  [1] Wrong remote URL — run: git remote set-url origin <correct-url>")
    print("  [2] Repo deleted on GitHub — create it again")
    print("  [3] No permission — ask repo owner for access")
    print("")
    return False


def _fix_large_file(stderr):
    """
    Fix: file too large for GitHub (100MB limit)
    Solution: identify file and guide user
    """
    Printer.error("Push rejected — file too large")
    print("")
    print("  GitHub limit: 100MB per file")
    print("")

    # try to find which file
    import re
    match = re.search(r"File (.+?) is", stderr)
    if match:
        large_file = match.group(1)
        print(f"  Large file: {large_file}")
        print("")

    print("  Fixes:")
    print("  [1] Add file to .gitignore")
    print("  [2] Use Git LFS: git lfs track <file>")
    print("  [3] Remove from history: git rm --cached <file>")
    print("")
    return False


def smart_push(branch=None):
    """
    Smart push — auto fixes errors
    Used by gcp internally
    """
    branch = branch or current_branch()

    # first attempt
    result = subprocess.run(
        ["git", "push", "origin", branch],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        Printer.success(f"Pushed to {branch}")
        return True

    # push failed — auto resolve
    Printer.warning("Push failed — attempting auto-fix...")
    return resolve_push_error(result.stderr, branch)
