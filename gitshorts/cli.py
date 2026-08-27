import sys
from gitshorts.utils.colors import Printer
from gitshorts import __version__
from gitshorts.core.installer import install
from gitshorts.core.uninstaller import uninstall
from gitshorts.core.updater import update, check_for_updates
from gitshorts.token.manager import gtoken
from gitshorts.core.setup_wizard import gsetup


def main():
    """Main CLI entry point — gitfast command"""
    args = sys.argv[1:]

    if not args:
        install()
        return

    cmd = args[0]

    if cmd == "install":
        install()

    elif cmd == "uninstall":
        uninstall()

    elif cmd == "update":
        update()

    elif cmd == "check":
        check_for_updates()

    elif cmd == "version":
        print(f"gitfast v{__version__}")

    elif cmd == "setup":
         gsetup()

    elif cmd == "token":
        action = args[1] if len(args) > 1 else "info"
        gtoken(action)

    else:
        Printer.error(f"Unknown command: {cmd}")
        help_cmd()


def help_cmd():
    """Show all available commands"""
    Printer.header(f"gitfast v{__version__}")
    print("  USAGE: gitfast <command>")
    print("")
    print("  COMMANDS:")
    print("  install      install shortcuts into your shell")
    print("  uninstall    remove gitfast from all shells")
    print("  update       update to latest version")
    print("  check        check if update available")
    print("  version      show current version")
    print("  token        manage GitHub token")
    print("")
    print("  TOKEN:")
    print("  token setup    store token securely")
    print("  token test     verify token works")
    print("  token refresh  update expired token")
    print("  token revoke   remove token")
    print("  token info     show token status")
    print("")
    print("  SHORTCUTS (after install):")
    print("  ghelp          show all git shortcuts")
    print("  gcp 'msg'      add + commit + push")
    print("  gmerge         auto resolve conflicts")
    Printer.divider()
