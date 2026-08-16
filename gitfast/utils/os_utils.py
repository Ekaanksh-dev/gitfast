import os
import sys
import platform
import subprocess


def get_os():
    system = platform.system()

    if system == "Linux":
        # check if WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl2"
        except FileNotFoundError:
            pass

        # check distro
        if os.path.exists("/etc/arch-release"):
            return "arch"
        elif os.path.exists("/etc/fedora-release"):
            return "fedora"
        else:
            return "ubuntu"

    elif system == "Darwin":
        return "macos"

    elif system == "Windows":
        return "windows"

    elif "MSYSTEM" in os.environ:
        return "gitbash"

    return "unknown"


def get_shell():
    shell = os.environ.get("SHELL", "")

    if "fish" in shell:
        return "fish"
    elif "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"

    # windows powershell
    if sys.platform == "win32":
        return "powershell"

    return "bash"  # default fallback


def get_shell_config():
    shell = get_shell()
    home  = os.path.expanduser("~")

    configs = {
        "bash":       os.path.join(home, ".bashrc"),
        "zsh":        os.path.join(home, ".zshrc"),
        "fish":       os.path.join(home, ".config", "fish", "config.fish"),
        "powershell": os.path.join(home, "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1"),
    }

    return configs.get(shell, os.path.join(home, ".bashrc"))


def get_package_manager():
    os_name = get_os()

    managers = {
        "ubuntu": "apt",
        "arch":   "pacman",
        "fedora": "dnf",
        "macos":  "brew",
        "wsl2":   "apt",
        "gitbash":"winget",
        "windows":"winget",
    }

    return managers.get(os_name, "apt")


def is_command_available(cmd):
    try:
        subprocess.run(
            ["which", cmd],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_git_installed():
    return is_command_available("git")


def is_git_repo():
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0
