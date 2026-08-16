import subprocess
from gitfast.utils.git import run_git, is_git_repo
from gitfast.utils.colors import Printer


def gundo():
    """Undo last commit — keep changes staged"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    _, err, code = run_git("reset --soft HEAD~1")
    if code != 0:
        Printer.error(f"Failed: {err}")
        return False

    Printer.success("Last commit undone — changes still staged")
    return True


def gundo2():
    """Undo last commit — unstage changes"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    _, err, code = run_git("reset HEAD~1")
    if code != 0:
        Printer.error(f"Failed: {err}")
        return False

    Printer.success("Last commit undone — changes in working dir")
    return True


def gsave(label="wip"):
    """Stash changes with a label"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    _, err, code = run_git(f"stash push -m {label}")
    if code != 0:
        Printer.error(f"Stash failed: {err}")
        return False

    Printer.success(f"Stashed as: {label}")
    return True


def gpop():
    """Pop latest stash"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    _, err, code = run_git("stash pop")
    if code != 0:
        Printer.error(f"Pop failed: {err}")
        return False

    Printer.success("Stash applied")
    return True


def gstashes():
    """List all stashes"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    out, _, code = run_git("stash list")
    if not out:
        Printer.info("No stashes found")
    else:
        print(out)


def gdrop(index=0):
    """Drop a specific stash"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    _, err, code = run_git(f"stash drop stash@{{{index}}}")
    if code != 0:
        Printer.error(f"Drop failed: {err}")
        return False

    Printer.success(f"Dropped stash@{{{index}}}")
    return True


def gabort():
    """Abort a merge or rebase"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    # try merge abort first
    _, _, code = run_git("merge --abort")
    if code == 0:
        Printer.success("Merge aborted")
        return True

    # try rebase abort
    _, _, code = run_git("rebase --abort")
    if code == 0:
        Printer.success("Rebase aborted")
        return True

    Printer.warning("Nothing to abort")
    return False


def gsquash(n):
    """Interactive rebase to squash last N commits"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not n:
        Printer.error("Usage: gsquash <N>")
        return False

    try:
        n = int(n)
    except ValueError:
        Printer.error("N must be a number")
        return False

    Printer.step(f"Opening rebase for last {n} commits...")
    subprocess.run(["git", "rebase", "-i", f"HEAD~{n}"])
    return True


def gnuke():
    """Wipe ALL uncommitted changes — dangerous"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    Printer.warning("This will destroy ALL uncommitted changes!")
    confirm = input("Type YES to confirm: ")

    if confirm != "YES":
        Printer.info("Cancelled")
        return False

    _, err, code = run_git("reset --hard HEAD")
    if code != 0:
        Printer.error(f"Reset failed: {err}")
        return False

    _, err, code = run_git("clean -fd")
    if code != 0:
        Printer.error(f"Clean failed: {err}")
        return False

    Printer.success("All uncommitted changes wiped")
    return True
