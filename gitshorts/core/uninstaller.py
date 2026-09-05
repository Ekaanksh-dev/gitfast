import os
from gitshorts.utils.colors import Printer
from gitshorts.shells import bash, zsh, fish, powershell


def uninstall():
    """
    Remove gitshorts from all shells
    Called when user runs: gitshorts uninstall
    """
    Printer.header("gitshorts Uninstaller")

    confirm = input("  Remove gitshorts from all shells? (y/N): ").strip().lower()
    if confirm != "y":
        Printer.info("Cancelled")
        return False

    home    = os.path.expanduser("~")
    results = {}

    shells = {
        "bash":       os.path.join(home, ".bashrc"),
        "zsh":        os.path.join(home, ".zshrc"),
        "fish":       os.path.join(home, ".config", "fish", "config.fish"),
        "powershell": os.path.join(home, "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1"),
    }

    for shell_name, config_path in shells.items():
        if not os.path.exists(config_path):
            continue

        Printer.step(f"Removing from {shell_name}...")

        if shell_name == "bash":
            results[shell_name] = bash.uninstall(config_path)
        elif shell_name == "zsh":
            results[shell_name] = zsh.uninstall(config_path)
        elif shell_name == "fish":
            results[shell_name] = fish.uninstall(config_path)
        elif shell_name == "powershell":
            results[shell_name] = powershell.uninstall(config_path)

    # remove token
    _remove_token()

    # remove backups
    _remove_backups()

    # summary
    Printer.divider()
    for shell_name, ok in results.items():
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} removed from {shell_name}")

    print("")
    Printer.success("gitshorts uninstalled")
    print("")
    print("  To fully remove:")
    print("  pip uninstall gitshorts")
    Printer.divider()

    return True


def _remove_token():
    """Remove stored token"""
    try:
        from gitshorts.token.storage import TokenStorage
        storage = TokenStorage()

        for host in ["github.com", "gitlab.com", "bitbucket.org"]:
            storage.delete(host)

        Printer.success("Tokens removed from secure storage")

    except Exception as e:
        Printer.warning(f"Could not remove tokens: {e}")


def _remove_backups():
    """Remove all gitshorts backup files"""
    try:
        from gitshorts.merge.backup import cleanup_backups
        cleanup_backups()
    except Exception as e:
        Printer.warning(f"Could not remove backups: {e}")
