import subprocess
import urllib.request
import json
from gitfast import __version__
from gitfast.utils.colors import Printer


PYPI_URL = "https://pypi.org/pypi/gitfast/json"


def get_latest_version():
    """Get latest version from PyPI"""
    try:
        req = urllib.request.Request(
            PYPI_URL,
            headers={"User-Agent": "gitfast"}
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
        print("  Run: gitfast update")
        print("  Or:  pip install --upgrade gitfast")
        print("")
        return True

    Printer.success(f"Already on latest version: v{__version__}")
    return False


def update():
    """Update gitfast to latest version"""
    Printer.header("gitfast Updater")

    # check if update available
    available, latest = is_update_available()

    if not available:
        Printer.success(f"Already on latest: v{__version__}")
        return True

    Printer.step(f"Updating v{__version__} → v{latest}...")

    try:
        result = subprocess.run(
            ["pip", "install", "--upgrade", "gitfast"],
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
            print("  pip install --upgrade gitfast")
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
                f"gitfast v{latest} available — run: gitfast update"
            )
            print("")
    except Exception:
        pass
