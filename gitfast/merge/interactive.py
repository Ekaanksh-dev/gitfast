from gitfast.utils.colors import Printer, Colors


def show_conflict(index, total, conflict):
    """Display one conflict side by side"""

    print(f"\n  Conflict {index + 1} of {total}")
    Printer.divider()

    # get lines from both sides
    ours_lines   = conflict.ours.splitlines()
    theirs_lines = conflict.theirs.splitlines()

    # pad shorter side with empty lines
    max_lines = max(len(ours_lines), len(theirs_lines))
    ours_lines   += [""] * (max_lines - len(ours_lines))
    theirs_lines += [""] * (max_lines - len(theirs_lines))

    # header
    print(f"  {'OURS':<35} {'THEIRS':<35}")
    print(f"  {'-'*35} {'-'*35}")

    # print side by side
    for our_line, their_line in zip(ours_lines, theirs_lines):
        our_display   = our_line[:33].ljust(35)
        their_display = their_line[:33].ljust(35)

        print(
            f"  {Colors.GREEN}{our_display}{Colors.RESET}"
            f" {Colors.BLUE}{their_display}{Colors.RESET}"
        )

    Printer.divider()


def ask_choice(conflict):
    """Ask user which side to keep"""

    while True:
        print(f"\n  [1] Keep OURS")
        print(f"  [2] Keep THEIRS")
        print(f"  [3] Keep BOTH")
        print(f"  [4] Skip this conflict")
        print(f"  [s] Show full conflict again")
        print(f"  [q] Quit interactive mode")

        choice = input("\n  Choice: ").strip().lower()

        if choice == "1":
            Printer.success("Keeping ours")
            return conflict.ours

        elif choice == "2":
            Printer.success("Keeping theirs")
            return conflict.theirs

        elif choice == "3":
            Printer.success("Keeping both")
            return conflict.ours + "\n" + conflict.theirs

        elif choice == "4":
            Printer.warning("Skipped — conflict left as is")
            return None

        elif choice == "s":
            _show_full(conflict)

        elif choice == "q":
            Printer.warning("Quit — remaining conflicts left as is")
            return "quit"

        else:
            Printer.error("Invalid choice — enter 1, 2, 3, 4, s or q")


def _show_full(conflict):
    """Show full conflict without truncation"""
    Printer.divider()
    print(f"\n  {Colors.GREEN}--- OURS ---{Colors.RESET}")
    print(conflict.ours)
    print(f"\n  {Colors.BLUE}--- THEIRS ---{Colors.RESET}")
    print(conflict.theirs)
    Printer.divider()


def run_interactive(filepath, conflicts):
    """
    Run interactive conflict resolver
    User picks ours/theirs/both for each conflict
    Returns dict of {index: resolved_text}
    """
    if not conflicts:
        Printer.success("No conflicts to resolve")
        return {}

    Printer.header(f"Interactive Resolver — {filepath}")
    print(f"  {len(conflicts)} conflict(s) to resolve\n")

    resolved  = {}
    total     = len(conflicts)

    for i, conflict in enumerate(conflicts):

        # show conflict
        show_conflict(i, total, conflict)

        # ask choice
        choice = ask_choice(conflict)

        if choice == "quit":
            Printer.warning("Stopped — remaining conflicts untouched")
            break

        if choice is not None:
            resolved[i] = choice
        else:
            # skipped — keep original markers
            pass

    # summary
    print("")
    Printer.divider()
    print(f"  Resolved : {len(resolved)} of {total}")
    print(f"  Skipped  : {total - len(resolved)}")
    Printer.divider()

    return resolved
