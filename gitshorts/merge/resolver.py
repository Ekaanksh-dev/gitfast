import sys
from gitshorts.utils.git import run_git, is_git_repo, stage_file, current_branch
from gitshorts.utils.colors import Printer
from gitshorts.merge.detector import scan_repo, display_conflicts, get_merge_state
from gitshorts.merge.parser import parse_conflicts, write_resolved
from gitshorts.merge.backup import create_backup, restore_backup
from gitshorts.merge.strategies import Strategy, apply_strategy_to_all
from gitshorts.merge.interactive import run_interactive


def gmerge(strategy=Strategy.SMART, interactive=False, backup=True, dry_run=False):
    from gitshorts.config import get

    # load from config if not specified
    if strategy is None:
        strategy_name = get("merge", "strategy", "smart")
        strategy = {
            "smart":  Strategy.SMART,
            "ours":   Strategy.OURS,
            "theirs": Strategy.THEIRS,
            "longer": Strategy.LONGER,
        }.get(strategy_name, Strategy.SMART)

    if backup is None:
        backup = get("merge", "auto_backup", True)

    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    Printer.scan("Scanning for conflicts...")
    results = scan_repo()

    if not results:
        Printer.success("No conflicts found — nothing to resolve")
        return True

    display_conflicts(results)

    if dry_run:
        Printer.info("Dry run — no changes made")
        return True

    all_resolved = True
    backups      = {}

    for filepath, count in results.items():
        print(f"\n  Resolving: {filepath} ({count} conflict(s))")

        conflicts = parse_conflicts(filepath)
        if not conflicts:
            continue

        if backup:
            backup_path = create_backup(filepath)
            if backup_path:
                backups[filepath] = backup_path

        if interactive:
            resolved = run_interactive(filepath, conflicts)
        else:
            resolved = apply_strategy_to_all(conflicts, strategy)

        if not resolved:
            Printer.warning(f"No conflicts resolved in {filepath}")
            all_resolved = False
            continue

        success = write_resolved(filepath, resolved)
        if not success:
            Printer.error(f"Failed to write: {filepath}")
            if filepath in backups:
                Printer.step("Restoring backup...")
                restore_backup(backups[filepath])
            all_resolved = False
            continue

        stage_file(filepath)
        Printer.success(f"Resolved: {filepath}")

    if all_resolved:
        _commit_resolved()
    else:
        Printer.warning("Some conflicts need manual fixing")
        Printer.info("Fix remaining then run: git add . && git commit")

    return all_resolved


def _commit_resolved():
    import subprocess
    Printer.save("Committing resolved conflicts...")
    result = subprocess.run(
        ["git", "commit", "--no-edit"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        Printer.success("Conflicts resolved and committed")
    else:
        result = subprocess.run(
            ["git", "commit", "-m", "fix: resolved merge conflicts"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            Printer.success("Conflicts resolved and committed")
        else:
            Printer.warning("Could not auto-commit — run: git commit manually")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="gitfast — auto merge conflict resolver")
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("--ours",    action="store_true")
    parser.add_argument("--theirs",  action="store_true")
    parser.add_argument("--longer",  action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    if args.ours:
        strategy = Strategy.OURS
    elif args.theirs:
        strategy = Strategy.THEIRS
    elif args.longer:
        strategy = Strategy.LONGER
    else:
        strategy = Strategy.SMART

    gmerge(
        strategy    = strategy,
        interactive = args.interactive,
        backup      = not args.no_backup,
        dry_run     = args.dry_run,
    )
