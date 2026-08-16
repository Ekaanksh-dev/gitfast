import os
from gitfast.utils.git import run_git, is_git_repo
from gitfast.utils.colors import Printer
from gitfast.merge.parser import has_conflicts, count_conflicts


def get_conflicted_files():
    """Get all files with merge conflicts from git"""
    out, _, code = run_git("diff --name-only --diff-filter=U")
    if code != 0 or not out:
        return []
    return [f.strip() for f in out.splitlines() if f.strip()]


def scan_repo():
    """
    Scan entire repo for conflicts
    Returns dict of {filepath: conflict_count}
    """
    if not is_git_repo():
        Printer.error("Not a git repo")
        return {}

    conflicted = get_conflicted_files()

    if not conflicted:
        Printer.success("No conflicts found")
        return {}

    results = {}
    for filepath in conflicted:
        if os.path.exists(filepath):
            count = count_conflicts(filepath)
            if count > 0:
                results[filepath] = count

    return results


def display_conflicts(results):
    """Display conflict scan results"""
    if not results:
        Printer.success("No conflicts found")
        return

    total = sum(results.values())

    Printer.header("Conflict Scan Results")
    print(f"  Found {total} conflict(s) in {len(results)} file(s)\n")

    for filepath, count in results.items():
        print(f"  {filepath:<40} {count} conflict(s)")

    Printer.divider()


def gconflicts():
    """Scan and display all conflicts"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return {}

    Printer.scan("Scanning for conflicts...")
    results = scan_repo()
    display_conflicts(results)
    return results


def is_mid_merge():
    """Check if we are in middle of a merge"""
    merge_head = os.path.exists(".git/MERGE_HEAD")
    rebase_dir = os.path.exists(".git/rebase-merge")
    cherry     = os.path.exists(".git/CHERRY_PICK_HEAD")
    return merge_head or rebase_dir or cherry


def get_merge_state():
    """Get current merge state"""
    if os.path.exists(".git/MERGE_HEAD"):
        return "merge"
    elif os.path.exists(".git/rebase-merge"):
        return "rebase"
    elif os.path.exists(".git/CHERRY_PICK_HEAD"):
        return "cherry-pick"
    else:
        return "clean"


def check_before_push():
    """
    Check for conflicts before pushing
    Called automatically by gcp
    Returns True if safe to push
    """
    results = scan_repo()

    if not results:
        return True

    Printer.error("Cannot push — unresolved conflicts found")
    display_conflicts(results)
    Printer.info("Run: gmerge to auto resolve conflicts")
    return False
