from gitshorts.core.installer import install
from gitshorts.core.uninstaller import uninstall
from gitshorts.core.updater import update, check_for_updates
from gitshorts.utils.colors import Printer
from gitshorts import __version__


def run():
    """Main entry point"""
    install()
