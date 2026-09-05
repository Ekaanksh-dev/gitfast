from gitshorts.utils.colors import Printer
from gitshorts.utils.git import run_git, is_git_repo


# supported platforms
PLATFORMS = {
    "1": {
        "name":     "GitHub",
        "host":     "github.com",
        "ssh":      "git@github.com",
        "token_url":"https://github.com/settings/tokens/new",
        "ssh_test": "Hi",
    },
    "2": {
        "name":     "GitLab",
        "host":     "gitlab.com",
        "ssh":      "git@gitlab.com",
        "token_url":"https://gitlab.com/-/profile/personal_access_tokens",
        "ssh_test": "Welcome",
    },
    "3": {
        "name":     "Bitbucket",
        "host":     "bitbucket.org",
        "ssh":      "git@bitbucket.org",
        "token_url":"https://bitbucket.org/account/settings/app-passwords/new",
        "ssh_test": "logged in",
    },
}


def gsetup():
    """
    Main setup wizard
    Guides user through platform + auth setup
    """
    Printer.header("gitshorts — Setup Wizard")

    # Step 1 — choose platforms
    platforms = _choose_platforms()
    if not platforms:
        return False

    # Step 2 — choose auth method
    auth_method = _choose_auth()

    # Step 3 — setup each platform
    for key, platform in platforms.items():
        _setup_platform(platform, auth_method)

    # Step 4 — save preferences
    _save_preferences(platforms, auth_method)

    # Step 5 — final summary
    _print_summary(platforms, auth_method)

    return True


def _choose_platforms():
    """Ask user which platforms they use"""
    print("")
    print("  Which platforms do you use?")
    print("")
    print("  [1] GitHub")
    print("  [2] GitLab")
    print("  [3] Bitbucket")
    print("  [4] GitHub + GitLab")
    print("  [5] GitHub + Bitbucket")
    print("  [6] All three")
    print("")

    choice = input("  Choice: ").strip()

    mapping = {
        "1": ["1"],
        "2": ["2"],
        "3": ["3"],
        "4": ["1", "2"],
        "5": ["1", "3"],
        "6": ["1", "2", "3"],
    }

    keys = mapping.get(choice)
    if not keys:
        Printer.error("Invalid choice")
        return None

    selected = {k: PLATFORMS[k] for k in keys}

    print("")
    for p in selected.values():
        Printer.success(f"Selected: {p['name']}")

    return selected


def _choose_auth():
    """Ask user which auth method they prefer"""
    print("")
    print("  Which auth method?")
    print("")
    print("  [1] SSH key (recommended — most secure)")
    print("  [2] Personal Access Token (PAT)")
    print("")

    choice = input("  Choice: ").strip()

    if choice == "1":
        Printer.success("Using SSH key auth")
        return "ssh"
    elif choice == "2":
        Printer.success("Using token auth")
        return "token"
    else:
        Printer.warning("Invalid — defaulting to SSH")
        return "ssh"


def _setup_platform(platform, auth_method):
    """Setup auth for one platform"""
    print("")
    Printer.header(f"Setting up {platform['name']}")

    if auth_method == "ssh":
        _setup_ssh(platform)
    else:
        _setup_token(platform)

    # convert remote if in git repo
    if is_git_repo():
        _convert_remote(platform)

    # test connection
    _test_connection(platform)


def _setup_ssh(platform):
    """Setup SSH for a platform"""
    import os
    import subprocess

    Printer.step(f"Setting up SSH for {platform['name']}...")

    email = input("  Your email: ").strip()
    if not email:
        Printer.error("Email required")
        return False

    key_path = os.path.expanduser(
        f"~/.ssh/id_ed25519_{platform['host'].replace('.', '_')}"
    )

    # generate key
    if os.path.exists(key_path):
        Printer.warning(f"SSH key exists: {key_path}")
        overwrite = input("  Overwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            Printer.info("Using existing key")
        else:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519",
                "-C", email,
                "-f", key_path,
                "-N", ""
            ])
    else:
        subprocess.run([
            "ssh-keygen", "-t", "ed25519",
            "-C", email,
            "-f", key_path,
            "-N", ""
        ])

    # add to ssh-agent
    os.system("eval $(ssh-agent -s) > /dev/null 2>&1")
    os.system(f"ssh-add {key_path} 2>/dev/null")

    # show public key
    pub_path = f"{key_path}.pub"
    if os.path.exists(pub_path):
        with open(pub_path, "r") as f:
            pub_key = f.read().strip()

        print("")
        Printer.divider()
        print(f"  Copy this key to {platform['name']}:")
        print("")
        print(f"  {pub_key}")
        print("")
        print(f"  Go to: {platform['name']} -> Settings -> SSH Keys")
        Printer.divider()

    input(f"  Press ENTER after adding key to {platform['name']}...")
    return True


def _setup_token(platform):
    """Setup PAT token for a platform"""
    import getpass
    from gitshorts.token.manager import gtoken_setup

    print("")
    print(f"  Create token at:")
    print(f"  {platform['token_url']}")
    print("")

    gtoken_setup(platform["host"])


def _convert_remote(platform):
    """Convert HTTPS remote to SSH if needed"""
    from gitshorts.shortcuts.auth import ghttps_to_ssh

    out, _, _ = run_git("remote get-url origin 2>/dev/null")
    if not out:
        return

    if platform["host"] in out and out.startswith("https://"):
        Printer.step("Converting remote to SSH...")
        ghttps_to_ssh()


def _test_connection(platform):
    """Test SSH connection to platform"""
    import subprocess

    Printer.scan(f"Testing connection to {platform['name']}...")

    result = subprocess.run(
        ["ssh", "-T",
         "-o", "StrictHostKeyChecking=no",
         f"git@{platform['host']}"],
        capture_output=True,
        text=True,
        timeout=10
    )

    output = result.stdout + result.stderr

    if platform["ssh_test"].lower() in output.lower():
        Printer.success(f"{platform['name']} connected")
        return True
    else:
        Printer.error(f"{platform['name']} connection failed")
        Printer.info("Check your key was added correctly")
        return False


def _save_preferences(platforms, auth_method):
    """Save user preferences to config file"""
    import os
    import json

    config_dir  = os.path.expanduser("~/.config/gitshorts")
    config_file = os.path.join(config_dir, "config.json")

    os.makedirs(config_dir, exist_ok=True)

    config = {
        "platforms":   [p["name"] for p in platforms.values()],
        "primary":     list(platforms.values())[0]["name"],
        "auth_method": auth_method,
        "hosts":       [p["host"] for p in platforms.values()],
    }

    try:
        with open(config_file, "w") as f:
            import json
            json.dump(config, f, indent=2)
        Printer.success(f"Preferences saved to {config_file}")
    except Exception as e:
        Printer.warning(f"Could not save preferences: {e}")


def _print_summary(platforms, auth_method):
    """Print final setup summary"""
    print("")
    Printer.header("Setup Complete")

    print(f"  Auth method : {auth_method}")
    print(f"  Platforms   :")
    for p in platforms.values():
        print(f"    [OK] {p['name']} ({p['host']})")

    print("")
    print("  You can now use:")
    print("  gcp 'msg'     → push to your platform")
    print("  gtoken info   → check token status")
    print("  gtest_ssh     → test connections")
    print("  gsetup        → run setup again")
    Printer.divider()


def load_preferences():
    """Load saved user preferences"""
    import os
    import json

    config_file = os.path.expanduser("~/.config/gitshorts/config.json")

    if not os.path.exists(config_file):
        return None

    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception:
        return None


def get_primary_platform():
    """Get user's primary platform"""
    prefs = load_preferences()
    if not prefs:
        return "github.com"
    return prefs.get("hosts", ["github.com"])[0]
