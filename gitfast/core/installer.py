import os
import sys
from gitfast.utils.colors import Printer
from gitfast.core.detector import detect
from gitfast.shells import bash, zsh, fish, powershell


def install():
    """
    Main installer — detects system and injects shortcuts
    Called when user runs: pip install gitfast
    """
    Printer.header("gitfast Installer")

    # Step 1 — detect system
    info = detect()

    # Step 2 — install for detected shell
    Printer.step(f"Installing for {info.shell}...")

    success = False

    if info.shell == "bash":
        success = bash.install(info.config)

    elif info.shell == "zsh":
        success = zsh.install(info.config)

    elif info.shell == "fish":
        success = fish.install(info.config)

    elif info.shell == "powershell":
        success = powershell.install(info.config)

    else:
        # unknown shell — try bash as fallback
        Printer.warning(f"Unknown shell: {info.shell} — trying bash")
        fallback = os.path.expanduser("~/.bashrc")
        success  = bash.install(fallback)

    # Step 3 — result
    if success:
        _print_success(info)
    else:
        _print_failure(info)

    return success


def _print_success(info):
    """Print success message after install"""
    Printer.divider()
    print(f"  [OK] gitfast installed for {info.shell}")
    print(f"  [OK] Config: {info.config}")
    print("")
    print("  Next steps:")
    print(f"  1. Run: source {info.config}")
    print(f"  2. Run: ghelp")
    print(f"  3. Run: gcp \"your first commit\"")
    print("")
    print("  Token setup (optional but recommended):")
    print("  Run: gtoken setup")
    Printer.divider()


def _print_failure(info):
    """Print failure message"""
    Printer.divider()
    Printer.error("Installation failed")
    print("")
    print("  Manual install:")
    print(f"  Add this to {info.config}:")
    print("")
    print("  source $(python3 -c 'import gitfast; print(gitfast.__file__)')")
    Printer.divider()


def install_all_shells():
    """Install for ALL shells at once"""
    Printer.header("gitfast — Install All Shells")

    home    = os.path.expanduser("~")
    results = {}

    shells = {
        "bash":       os.path.join(home, ".bashrc"),
        "zsh":        os.path.join(home, ".zshrc"),
        "fish":       os.path.join(home, ".config", "fish", "config.fish"),
        "powershell": os.path.join(home, "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1"),
    }

    for shell_name, config_path in shells.items():
        Printer.step(f"Installing for {shell_name}...")

        if shell_name == "bash":
            results[shell_name] = bash.install(config_path)
        elif shell_name == "zsh":
            results[shell_name] = zsh.install(config_path)
        elif shell_name == "fish":
            results[shell_name] = fish.install(config_path)
        elif shell_name == "powershell":
            results[shell_name] = powershell.install(config_path)

    # summary
    Printer.divider()
    for shell_name, ok in results.items():
        status = "[OK]" if ok else "[SKIP]"
        print(f"  {status} {shell_name}")
    Printer.divider()

    return all(results.values())
