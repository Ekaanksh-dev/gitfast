import subprocess
import urllib.request
import json
from gitshorts import __version__
from gitshorts.utils.colors import Printer


PYPI_URL = "https://pypi.org/pypi/gitshorts/json"


def get_latest_version():
    """Get latest version from PyPI"""
    try:
        req = urllib.request.Request(
            PYPI_URL,
            headers={"User-Agent":    "gitshorts"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]

    except Exception:
        return None


def is_update_available():
    """Check if newer version exists on PyPI"""
    latest = get_latest_version()
    if not latest:
        return False, None

    current = __version__
    return latest != current, latest


def check_for_updates():
    """Check and display update status"""
    Printer.scan("Checking for updates...")

    available, latest = is_update_available()

    if available:
        Printer.warning(f"Update available: v{__version__} → v{latest}")
        print("")
        print("  Run: gitshorts update")
        print("  Or:  pip install --upgrade gitshorts")
        print("")
        return True

    Printer.success(f"Already on latest version: v{__version__}")
    return False


def update():
    """Update gitshorts to latest version"""
    Printer.header("gitshorts Updater")

    # check if update available
    available, latest = is_update_available()

    if not available:
        Printer.success(f"Already on latest: v{__version__}")
        return True

    Printer.step(f"Updating v{__version__} → v{latest}...")

    try:
        result = subprocess.run(
            ["pip", "install", "--upgrade", "gitshorts"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            Printer.success(f"Updated to v{latest}")
            print("")
            print("  Restart your terminal or run:")
            print("  source ~/.bashrc")
            return True
        else:
            Printer.error(f"Update failed: {result.stderr}")
            print("")
            print("  Try manually:")
            print("  pip install --upgrade gitshorts")
            return False

    except Exception as e:
        Printer.error(f"Update error: {e}")
        return False


def auto_check_on_startup():
    """
    Silently check for updates on startup
    Only shows message if update available
    """
    try:
        available, latest = is_update_available()
        if available:
            print("")
            Printer.warning(
                f"gitshorts v{latest} available — run: gitshorts update"
            )
            print("")
    except Exception:
        pass
