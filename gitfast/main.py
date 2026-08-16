from gitfast.core.installer import install
from gitfast.core.uninstaller import uninstall
from gitfast.core.updater import update, check_for_updates
from gitfast.utils.colors import Printer
from gitfast import __version__


def run():
    """Main entry point"""
    install()
