from gitfast.utils.git import run_git, is_git_repo, current_branch
from gitfast.utils.colors import Printer


def gb():
    """List all branches"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return
    out, _, _ = run_git("branch -a")
    print(out)


def gnb(name):
    """Create new branch and push upstream"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not name:
        Printer.error("Usage: gnb <branch-name>")
        return False

    Printer.step(f"Creating branch: {name}")
    _, err, code = run_git(f"checkout -b {name}")
    if code != 0:
        Printer.error(f"Failed to create branch: {err}")
        return False

    Printer.push(f"Pushing {name} upstream...")
    _, err, code = run_git(f"push -u origin {name}")
    if code != 0:
        Printer.error(f"Failed to push: {err}")
        return False

    Printer.success(f"Created and pushed: {name}")
    return True


def gsw(branch):
    """Switch to a branch"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not branch:
        Printer.error("Usage: gsw <branch>")
        return False

    _, err, code = run_git(f"switch {branch}")
    if code != 0:
        Printer.error(f"Failed to switch: {err}")
        return False

    Printer.success(f"Switched to: {branch}")
    return True


def gm(branch):
    """Merge branch into current"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not branch:
        Printer.error("Usage: gm <branch>")
        return False

    current = current_branch()
    Printer.step(f"Merging {branch} into {current}...")
    out, err, code = run_git(f"merge {branch}")

    if code != 0:
        Printer.error(f"Merge failed — conflicts detected")
        Printer.info("Run: gmerge to auto resolve conflicts")
        return False

    Printer.success(f"Merged {branch} into {current}")
    return True


def gd():
    """Show diff summary"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return
    out, _, _ = run_git("diff --stat")
    print(out) if out else Printer.success("No changes")


def gdf(filepath):
    """Show diff for specific file"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    if not filepath:
        Printer.error("Usage: gdf <file>")
        return

    out, _, _ = run_git(f"diff {filepath}")
    print(out) if out else Printer.success("No changes in file")


def gcl(url):
    """Clone a repository"""
    if not url:
        Printer.error("Usage: gcl <url>")
        return False

    Printer.step(f"Cloning: {url}")
    _, err, code = run_git(f"clone {url}")

    if code != 0:
        Printer.error(f"Clone failed: {err}")
        return False

    Printer.success("Cloned successfully")
    return True


def gl():
    """Pretty git log last 20"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return
    out, _, _ = run_git("log --oneline --graph --decorate --color -20")
    print(out)


def gll():
    """Git log with file stats"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return
    out, _, _ = run_git("log --stat --color -10")
    print(out)
