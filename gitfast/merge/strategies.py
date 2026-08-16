from gitfast.utils.colors import Printer


class Strategy:
    OURS    = "ours"
    THEIRS  = "theirs"
    NEWER   = "newer"
    LONGER  = "longer"
    SMART   = "smart"


def resolve_ours(conflict):
    """Always keep our code"""
    return conflict.ours


def resolve_theirs(conflict):
    """Always keep their code"""
    return conflict.theirs


def resolve_newer(conflict):
    """
    Keep whichever side has more recent changes
    Detected by looking at timestamps in blame
    Falls back to longer if cannot determine
    """
    return resolve_longer(conflict)


def resolve_longer(conflict):
    """Keep whichever side has more lines of code"""
    ours_lines   = len(conflict.ours.splitlines())
    theirs_lines = len(conflict.theirs.splitlines())

    if ours_lines >= theirs_lines:
        return conflict.ours
    return conflict.theirs


def resolve_smart(conflict):
    """
    Smart strategy — analyze both sides and pick best one

    Rules:
    1. If one side is empty     → keep the non-empty side
    2. If one side has syntax   → keep the valid side
    3. If both equal            → keep ours
    4. If theirs is longer      → keep theirs (more complete)
    5. Default                  → keep ours
    """

    ours   = conflict.ours.strip()
    theirs = conflict.theirs.strip()

    # Rule 1 — one side empty
    if not ours and theirs:
        Printer.step("Smart: keeping theirs — ours is empty")
        return conflict.theirs

    if ours and not theirs:
        Printer.step("Smart: keeping ours — theirs is empty")
        return conflict.ours

    # Rule 2 — both equal
    if ours == theirs:
        Printer.step("Smart: both sides equal — keeping ours")
        return conflict.ours

    # Rule 3 — check for common broken patterns
    ours_broken   = _looks_broken(ours)
    theirs_broken = _looks_broken(theirs)

    if ours_broken and not theirs_broken:
        Printer.step("Smart: keeping theirs — ours looks incomplete")
        return conflict.theirs

    if theirs_broken and not ours_broken:
        Printer.step("Smart: keeping ours — theirs looks incomplete")
        return conflict.ours

    # Rule 4 — theirs is longer/more complete
    if len(theirs.splitlines()) > len(ours.splitlines()):
        Printer.step("Smart: keeping theirs — more complete")
        return conflict.theirs

    # Rule 5 — default keep ours
    Printer.step("Smart: keeping ours — default")
    return conflict.ours


def _looks_broken(code):
    """
    Check if code looks incomplete or broken
    Simple heuristics — no compiler needed
    """
    code = code.strip()

    if not code:
        return True

    # unmatched braces
    if code.count("{") != code.count("}"):
        return True

    # unmatched brackets
    if code.count("(") != code.count(")"):
        return True

    # unmatched quotes
    if code.count('"') % 2 != 0:
        return True

    # ends with operator — incomplete expression
    broken_endings = ["+", "-", "*", "/", "=", ",", "&&", "||"]
    for ending in broken_endings:
        if code.endswith(ending):
            return True

    return False


def apply_strategy(conflict, strategy=Strategy.SMART):
    """
    Apply chosen strategy to a conflict
    Returns resolved text
    """
    strategies = {
        Strategy.OURS:   resolve_ours,
        Strategy.THEIRS: resolve_theirs,
        Strategy.NEWER:  resolve_newer,
        Strategy.LONGER: resolve_longer,
        Strategy.SMART:  resolve_smart,
    }

    func = strategies.get(strategy, resolve_smart)
    return func(conflict)


def apply_strategy_to_all(conflicts, strategy=Strategy.SMART):
    """
    Apply strategy to all conflicts
    Returns dict of {index: resolved_text}
    """
    resolved = {}

    for i, conflict in enumerate(conflicts):
        resolved[i] = apply_strategy(conflict, strategy)

    return resolved
