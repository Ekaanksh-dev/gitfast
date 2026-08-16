from gitfast.utils.git import (
    is_git_repo,
    current_branch,
    stage_all,
    commit,
    push,
    pull,
    get_status,
)
from gitfast.utils.colors import Printer


def gs():
    """Show git status short"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    status = get_status()
    if not status:
        Printer.success("Working tree clean")
    else:
        print(status)


def gc(message):
    """git add + commit only — no push"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not message:
        Printer.error("Usage: gc <message>")
        return False

    # stage
    Printer.step("Staging all changes...")
    if not stage_all():
        Printer.error("Staging failed")
        return False

    # commit
    Printer.save(f"Committing: {message}")
    if not commit(message):
        Printer.error("Commit failed")
        return False

    Printer.success("Committed locally — run gcp to push")
    return True

def gcp(message):
    """git add + commit + push in one command"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not message:
        Printer.error("Usage: gcp <message>")
        return False

    branch = current_branch()

    # stage
    Printer.step("Staging all changes...")
    if not stage_all():
        Printer.error("Staging failed")
        return False

    # commit
    Printer.save(f"Committing: {message}")
    if not commit(message):
        Printer.error("Commit failed")
        return False

    # push
    Printer.push(f"Pushing to {branch}...")
    ok, err = push(branch)
    if not ok:
        Printer.error(f"Push failed: {err}")
        return False

    Printer.success("Done!")
    return True


def gpl():
    """Pull from current branch"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    branch = current_branch()
    Printer.step(f"Pulling from {branch}...")
    ok, out = pull(branch)

    if ok:
        Printer.success("Pull complete")
        if out:
            print(out)
    else:
        Printer.error(f"Pull failed: {out}")

    return ok
