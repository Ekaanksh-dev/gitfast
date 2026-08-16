import re
from datetime import datetime, timezone
from gitfast.utils.colors import Printer


# warning threshold in days
WARN_DAYS = 14


def parse_expiry(expiry_str):
    """
    Parse expiry string from GitHub API
    Format: 2024-12-01 00:00:00 UTC
    Returns datetime object or None
    """
    if not expiry_str:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(expiry_str.strip(), fmt)
        except ValueError:
            continue

    return None


def days_until_expiry(expiry_str):
    """
    Calculate days until token expires
    Returns int days or None if no expiry
    """
    expiry = parse_expiry(expiry_str)
    if not expiry:
        return None

    now  = datetime.now()
    diff = expiry - now

    return diff.days


def check_expiry(expiry_str):
    """
    Check token expiry and warn if needed
    Returns status string
    """
    days = days_until_expiry(expiry_str)

    # no expiry set
    if days is None:
        Printer.info("Token has no expiry date")
        return "no_expiry"

    # already expired
    if days < 0:
        Printer.error(f"Token EXPIRED {abs(days)} days ago")
        Printer.info("Run: gtoken refresh")
        return "expired"

    # expiring very soon
    if days == 0:
        Printer.error("Token expires TODAY")
        Printer.info("Run: gtoken refresh NOW")
        return "expires_today"

    # expiring soon
    if days <= WARN_DAYS:
        Printer.warning(f"Token expires in {days} days")
        Printer.info("Run: gtoken refresh soon")
        return "expiring_soon"

    # all good
    Printer.success(f"Token valid for {days} more days")
    return "valid"


def format_expiry_display(expiry_str):
    """Format expiry for display"""
    days = days_until_expiry(expiry_str)

    if days is None:
        return "no expiry"

    if days < 0:
        return f"EXPIRED {abs(days)} days ago"

    if days == 0:
        return "expires TODAY"

    if days <= WARN_DAYS:
        return f"{expiry_str} ({days} days — expiring soon)"

    return f"{expiry_str} ({days} days remaining)"


def should_warn(expiry_str):
    """
    Return True if we should warn user about expiry
    Called every time gitfast runs
    """
    days = days_until_expiry(expiry_str)

    if days is None:
        return False

    return days <= WARN_DAYS


def auto_check_on_startup(token_info):
    """
    Run expiry check on every gitfast startup
    Warns user silently if expiring soon
    """
    if not token_info:
        return

    expiry = getattr(token_info, "expires", None)
    if not expiry:
        return

    if should_warn(expiry):
        print("")
        Printer.warning(
            f"Your GitHub token expires in "
            f"{days_until_expiry(expiry)} days — run: gtoken refresh"
        )
        print("")
