from gitshorts.utils.git import run_git, is_git_repo, current_branch
from gitshorts.utils.colors import Printer


def gf():
    """Fetch all remotes"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    Printer.step("Fetching all remotes...")
    _, err, code = run_git("fetch --all --prune")
    if code != 0:
        Printer.error(f"Fetch failed: {err}")
        return False

    Printer.success("Fetched all remotes")
    return True


def gtag(tag, message=None):
    """Tag a release and push"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not tag:
        Printer.error("Usage: gtag <v1.0> [message]")
        return False

    msg = message or f"Release {tag}"

    Printer.step(f"Creating tag: {tag}")
    _, err, code = run_git(f"tag -a {tag} -m {msg}")
    if code != 0:
        Printer.error(f"Tag failed: {err}")
        return False

    Printer.push(f"Pushing tag: {tag}")
    _, err, code = run_git(f"push origin {tag}")
    if code != 0:
        Printer.error(f"Push tag failed: {err}")
        return False

    Printer.success(f"Tagged and pushed: {tag}")
    return True


def gtags():
    """List all tags"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    out, _, code = run_git("tag -l --sort=-version:refname")
    if not out:
        Printer.info("No tags found")
    else:
        print(out)


def gwho(filepath):
    """Show who wrote each line"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    if not filepath:
        Printer.error("Usage: gwho <file>")
        return

    out, err, code = run_git(f"blame {filepath}")
    if code != 0:
        Printer.error(f"Blame failed: {err}")
        return

    print(out)


def greflog():
    """Show full git history including deleted"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    out, _, _ = run_git("reflog --color")
    lines = out.splitlines()[:30]
    print("\n".join(lines))


def grecover(hash, name):
    """Recover a deleted branch"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not hash or not name:
        Printer.error("Usage: grecover <hash> <branch-name>")
        return False

    Printer.step(f"Recovering branch {name} from {hash}...")
    _, err, code = run_git(f"checkout -b {name} {hash}")
    if code != 0:
        Printer.error(f"Recovery failed: {err}")
        return False

    Printer.success(f"Recovered: {name} from {hash}")
    return True


def gshow(hash="HEAD"):
    """Show full details of a commit"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    out, err, code = run_git(f"show {hash} --stat")
    if code != 0:
        Printer.error(f"Show failed: {err}")
        return

    print(out)


def gclean():
    """Delete all merged branches"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    out, _, code = run_git("branch --merged")
    if code != 0:
        Printer.error("Failed to list branches")
        return False

    branches = [
        b.strip() for b in out.splitlines()
        if b.strip() not in ["main", "master", "develop"]
        and not b.strip().startswith("*")
    ]

    if not branches:
        Printer.info("No merged branches to clean")
        return True

    Printer.step(f"Deleting {len(branches)} merged branches...")
    for branch in branches:
        _, err, code = run_git(f"branch -d {branch}")
        if code == 0:
            Printer.success(f"Deleted: {branch}")
        else:
            Printer.error(f"Failed to delete {branch}: {err}")

    return True


def gremotes():
    """Show all remotes"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    out, _, _ = run_git("remote -v")
    if not out:
        Printer.info("No remotes configured")
    else:
        print(out)


def gbisect_start(bad, good):
    """Start bisect to find broken commit"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    if not bad or not good:
        Printer.error("Usage: gbisect_start <bad_commit> <good_commit>")
        return False

    run_git("bisect start")
    run_git(f"bisect bad {bad}")
    run_git(f"bisect good {good}")
    Printer.success("Bisect started")
    Printer.info("Test and run: gbisect_good OR gbisect_bad")
    return True


def gbisect_good():
    run_git("bisect good")
    Printer.success("Marked good")


def gbisect_bad():
    run_git("bisect bad")
    Printer.error("Marked bad")


def gbisect_done():
    run_git("bisect reset")
    Printer.success("Bisect finished")
