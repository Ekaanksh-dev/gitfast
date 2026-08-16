import subprocess
from gitfast.utils.colors import Printer


def run_git(command):
    """Run any git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + command.split(),
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    except FileNotFoundError:
        Printer.error("Git is not installed")
        return "", "git not found", 1


def current_branch():
    """Get current git branch name"""
    out, err, code = run_git("branch --show-current")
    if code == 0 and out:
        return out
    return "main"  # fallback


def is_git_repo():
    """Check if current directory is a git repo"""
    _, _, code = run_git("rev-parse --is-inside-work-tree")
    return code == 0


def has_conflicts():
    """Check if repo has merge conflicts"""
    out, _, code = run_git("diff --name-only --diff-filter=U")
    return code == 0 and bool(out)


def conflicted_files():
    """Return list of files with conflicts"""
    out, _, code = run_git("diff --name-only --diff-filter=U")
    if code == 0 and out:
        return out.splitlines()
    return []


def stage_file(filepath):
    """Stage a specific file"""
    _, err, code = run_git(f"add {filepath}")
    return code == 0


def stage_all():
    """Stage all changes"""
    _, err, code = run_git("add .")
    return code == 0


def commit(message):
    """Commit with message"""
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def push(branch=None):
    """Push to remote"""
    branch = branch or current_branch()
    try:
        result = subprocess.run(
            ["git", "push", "origin", branch],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stderr.strip()
    except FileNotFoundError:
        return False, "git not found"


def pull(branch=None):
    """Pull from remote"""
    branch = branch or current_branch()
    try:
        result = subprocess.run(
            ["git", "pull", "origin", branch],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, "git not found"


def get_remote_url():
    """Get remote origin URL"""
    out, _, code = run_git("remote get-url origin")
    if code == 0:
        return out
    return None


def get_status():
    """Get short git status"""
    out, _, code = run_git("status -s")
    if code == 0:
        return out
    return ""
