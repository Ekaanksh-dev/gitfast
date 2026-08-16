import os
import subprocess
from gitfast.utils.git import run_git, is_git_repo, get_remote_url
from gitfast.utils.os_utils import get_os
from gitfast.utils.colors import Printer


def gsetup_ssh():
    """Full SSH key setup in one command"""
    Printer.header("SSH Key Setup")

    # Step 1 — get email
    email = input("Enter your GitHub email: ").strip()
    if not email:
        Printer.error("Email required")
        return False

    key_path = os.path.expanduser("~/.ssh/id_ed25519")

    # Step 2 — generate key
    if os.path.exists(key_path):
        Printer.warning(f"SSH key already exists at {key_path}")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            Printer.info("Skipping key generation")
        else:
            _generate_key(email, key_path)
    else:
        _generate_key(email, key_path)

    # Step 3 — start ssh-agent
    Printer.step("Starting ssh-agent...")
    os.system("eval $(ssh-agent -s)")
    os.system(f"ssh-add {key_path}")

    # Step 4 — show public key
    pub_key_path = f"{key_path}.pub"
    if os.path.exists(pub_key_path):
        with open(pub_key_path, "r") as f:
            pub_key = f.read().strip()

        Printer.header("Copy this public key to GitHub")
        print(f"\n{pub_key}\n")
        print("  Go to: GitHub -> Settings -> SSH Keys -> New SSH Key")
        print("  Paste the key above -> Save")
        Printer.divider()

    # Step 5 — test connection
    input("Press ENTER after adding key to GitHub...")
    gtest_ssh()
    return True


def _generate_key(email, key_path):
    Printer.step("Generating SSH key...")
    subprocess.run([
        "ssh-keygen",
        "-t", "ed25519",
        "-C", email,
        "-f", key_path,
        "-N", ""
    ])


def gsetup_creds():
    """Configure OS credential helper"""
    Printer.header("Credential Helper Setup")

    os_name = get_os()

    if os_name == "macos":
        run_git("config --global credential.helper osxkeychain")
        Printer.success("Using macOS Keychain")

    elif os_name in ["ubuntu", "wsl2"]:
        result = subprocess.run(
            ["which", "git-credential-libsecret"],
            capture_output=True
        )
        if result.returncode == 0:
            run_git("config --global credential.helper libsecret")
            Printer.success("Using GNOME Keyring")
        else:
            run_git("config --global credential.helper store")
            Printer.warning("Using plain file store — consider SSH for better security")

    elif os_name == "windows":
        run_git("config --global credential.helper wincred")
        Printer.success("Using Windows Credential Manager")

    elif os_name == "gitbash":
        run_git("config --global credential.helper wincred")
        Printer.success("Using Windows Credential Manager")

    else:
        run_git("config --global credential.helper store")
        Printer.warning("Using plain file store")

    Printer.success("Credentials will be saved after next login")
    return True


def ghttps_to_ssh():
    """Convert HTTPS remote to SSH"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return False

    current = get_remote_url()
    if not current:
        Printer.error("No remote origin found")
        return False

    print(f"Current remote: {current}")

    if current.startswith("git@"):
        Printer.success("Already using SSH — nothing to do")
        return True

    # convert URL
    ssh_url = current
    ssh_url = ssh_url.replace("https://github.com/",  "git@github.com:")
    ssh_url = ssh_url.replace("https://gitlab.com/",  "git@gitlab.com:")
    ssh_url = ssh_url.replace("https://bitbucket.org/","git@bitbucket.org:")

    print(f"New SSH remote:  {ssh_url}")
    confirm = input("Switch to SSH? (y/N): ").strip().lower()

    if confirm != "y":
        Printer.info("Cancelled")
        return False

    _, err, code = run_git(f"remote set-url origin {ssh_url}")
    if code != 0:
        Printer.error(f"Failed: {err}")
        return False

    Printer.success("Remote switched to SSH")
    gtest_ssh()
    return True


def gtest_ssh():
    """Test SSH connections"""
    Printer.scan("Testing SSH connections...")
    print("")

    hosts = [
        ("GitHub",    "git@github.com",    "Hi"),
        ("GitLab",    "git@gitlab.com",    "Welcome"),
        ("Bitbucket", "git@bitbucket.org", "logged in"),
    ]

    for name, host, keyword in hosts:
        result = subprocess.run(
            ["ssh", "-T", "-o", "StrictHostKeyChecking=no", host],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        if keyword.lower() in output.lower():
            Printer.success(f"{name} connected")
        else:
            Printer.error(f"{name} failed")


def gauth_info():
    """Show full auth info for current repo"""
    if not is_git_repo():
        Printer.error("Not a git repo")
        return

    Printer.header("Auth Info")

    url = get_remote_url()
    print(f"  Remote URL  : {url or 'none'}")

    if url:
        if url.startswith("git@"):
            Printer.success("Protocol: SSH — no password needed")
        elif url.startswith("https://"):
            Printer.warning("Protocol: HTTPS — run ghttps_to_ssh to fix")

    out, _, _ = run_git("config --global credential.helper")
    print(f"  Cred helper : {out or 'none configured'}")

    result = subprocess.run(
        ["ssh-add", "-l"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        Printer.success(f"SSH keys loaded: {result.stdout.strip()}")
    else:
        Printer.warning("No SSH keys loaded")

    Printer.divider()
