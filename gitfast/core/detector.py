import sys
from gitfast.utils.os_utils import (
    get_os,
    get_shell,
    get_shell_config,
    get_package_manager,
    is_git_installed,
)
from gitfast.utils.colors import Printer


class SystemInfo:
    def __init__(self):
        self.os      = get_os()
        self.shell   = get_shell()
        self.config  = get_shell_config()
        self.pkg_mgr = get_package_manager()
        self.git_ok  = is_git_installed()

    def display(self):
        Printer.header("System Detection")
        print(f"  OS              : {self.os}")
        print(f"  Shell           : {self.shell}")
        print(f"  Config file     : {self.config}")
        print(f"  Package manager : {self.pkg_mgr}")
        print(f"  Git installed   : {'yes' if self.git_ok else 'no'}")
        Printer.divider()

    def is_supported(self):
        if self.os == "unknown":
            Printer.error("Unsupported OS detected")
            return False

        if not self.git_ok:
            Printer.error("Git is not installed")
            Printer.info(f"Install it with: {self._git_install_cmd()}")
            return False

        return True

    def _git_install_cmd(self):
        cmds = {
            "ubuntu": "sudo apt install git",
            "arch":   "sudo pacman -S git",
            "fedora": "sudo dnf install git",
            "macos":  "brew install git",
            "wsl2":   "sudo apt install git",
            "gitbash":"winget install git",
        }
        return cmds.get(self.os, "sudo apt install git")


def detect():
    """Run full system detection and return SystemInfo"""
    info = SystemInfo()
    info.display()

    if not info.is_supported():
        Printer.error("System not supported — exiting")
        sys.exit(1)

    Printer.success("System supported — ready to install")
    return info
