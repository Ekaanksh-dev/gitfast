import getpass
from gitfast.utils.colors import Printer
from gitfast.utils.git import run_git
from gitfast.token.storage import TokenStorage
from gitfast.token.validator import validate_token, display_token_info
from gitfast.token.expiry import check_expiry, format_expiry_display


storage = TokenStorage()


def gtoken_setup(host="github.com"):
    """
    Full token setup in one command
    Ask → Validate → Store → Configure git
    """
    Printer.header(f"gitfast — Token Setup ({host})")

    # Step 1 — get token securely
    print("  Create token at:")
    print("  https://github.com/settings/tokens/new")
    print("")
    print("  Required permissions:")
    print("  [x] repo")
    print("  [x] workflow")
    print("  [x] read:org")
    print("")

    token = getpass.getpass("  Paste your token (hidden): ").strip()

    if not token:
        Printer.error("No token entered")
        return False

    # Step 2 — validate token
    info = validate_token(token, host)
    if not info or not info.valid:
        Printer.error("Token validation failed — not saved")
        return False

    # Step 3 — store securely
    Printer.step("Storing token securely...")
    saved = storage.save(token, info.username, host)
    if not saved:
        Printer.error("Failed to store token")
        return False

    # Step 4 — configure git credential helper
    _configure_git_credential(host, info.username, token)

    # Step 5 — check expiry
    if info.expires:
        check_expiry(info.expires)

    # Step 6 — summary
    Printer.divider()
    print(f"  [OK] Token saved for: {info.username}")
    print(f"  [OK] Git configured — no more password prompts")
    if info.expires:
        print(f"  Expires: {format_expiry_display(info.expires)}")
    Printer.divider()

    return True


def gtoken_test(host="github.com"):
    """Test if stored token works"""
    Printer.header("Token Test")

    token = storage.load(host)
    if not token:
        Printer.error("No token found — run: gtoken setup")
        return False

    info = validate_token(token, host)
    display_token_info(info)

    if info and info.expires:
        check_expiry(info.expires)

    return info.valid if info else False


def gtoken_refresh(host="github.com"):
    """Update expired or expiring token"""
    Printer.header("Token Refresh")

    print("  Generate new token at:")
    print("  https://github.com/settings/tokens/new")
    print("")

    token = getpass.getpass("  Paste new token (hidden): ").strip()
    if not token:
        Printer.error("No token entered")
        return False

    # validate
    info = validate_token(token, host)
    if not info or not info.valid:
        Printer.error("New token is invalid — keeping old token")
        return False

    # delete old
    storage.delete(host)

    # save new
    saved = storage.save(token, info.username, host)
    if not saved:
        Printer.error("Failed to save new token")
        return False

    # reconfigure git
    _configure_git_credential(host, info.username, token)

    Printer.success("Token refreshed successfully")
    if info.expires:
        check_expiry(info.expires)

    return True


def gtoken_revoke(host="github.com"):
    """Remove stored token"""
    Printer.header("Token Revoke")

    confirm = input("  Remove stored token? (y/N): ").strip().lower()
    if confirm != "y":
        Printer.info("Cancelled")
        return False

    deleted = storage.delete(host)
    if deleted:
        Printer.success("Token removed from secure storage")
        Printer.info("Remember to revoke it on GitHub too:")
        print("  https://github.com/settings/tokens")
    else:
        Printer.error("Failed to remove token")

    return deleted


def gtoken_info(host="github.com"):
    """Show token status without revealing token"""
    Printer.header("Token Info")

    token = storage.load(host)
    if not token:
        Printer.error("No token stored — run: gtoken setup")
        return

    # validate to get fresh info
    info = validate_token(token, host)
    display_token_info(info)

    if info and info.expires:
        check_expiry(info.expires)


def _configure_git_credential(host, username, token):
    """Configure git to use token automatically"""
    Printer.step("Configuring git credential helper...")

    # set credential helper to store
    run_git("config --global credential.helper store")

    # write to git credentials file
    import os
    cred_file = os.path.expanduser("~/.git-credentials")

    try:
        # read existing
        content = ""
        if os.path.exists(cred_file):
            with open(cred_file, "r") as f:
                content = f.read()

        # remove old entry
        lines = [
            l for l in content.splitlines()
            if host not in l
        ]

        # add new entry
        lines.append(f"https://{username}:{token}@{host}")

        # write back
        with open(cred_file, "w") as f:
            f.write("\n".join(lines))

        # secure permissions
        import stat
        os.chmod(cred_file, stat.S_IRUSR | stat.S_IWUSR)
        Printer.success("Git credential helper configured")

    except Exception as e:
        Printer.error(f"Failed to configure git credentials: {e}")


def gtoken(action="info", host="github.com"):
    """
    Main entry point for gtoken command
    gtoken setup / test / refresh / revoke / info
    """
    actions = {
        "setup":   gtoken_setup,
        "test":    gtoken_test,
        "refresh": gtoken_refresh,
        "revoke":  gtoken_revoke,
        "info":    gtoken_info,
    }

    func = actions.get(action)
    if not func:
        Printer.error(f"Unknown action: {action}")
        print("  Usage: gtoken [setup|test|refresh|revoke|info]")
        return

    func(host)
