import os
import stat
import subprocess
from gitshorts.utils.os_utils import get_os
from gitshorts.utils.colors import Printer


NETRC_PATH = os.path.expanduser("~/.netrc")


class TokenStorage:

    def __init__(self):
        self.os_name = get_os()

    def save(self, token, username, host="github.com"):
        """Save token to OS secure storage"""

        if self.os_name == "macos":
            return self._save_keychain(token, username, host)

        elif self.os_name in ["ubuntu", "wsl2", "arch", "fedora"]:
            # try libsecret first
            if self._has_libsecret():
                return self._save_libsecret(token, username, host)
            else:
                return self._save_netrc(token, username, host)

        elif self.os_name in ["windows", "gitbash"]:
            return self._save_wincred(token, username, host)

        else:
            return self._save_netrc(token, username, host)


    def load(self, host="github.com"):
        """Load token from OS secure storage"""

        if self.os_name == "macos":
            return self._load_keychain(host)

        elif self.os_name in ["ubuntu", "wsl2", "arch", "fedora"]:
            if self._has_libsecret():
                return self._load_libsecret(host)
            else:
                return self._load_netrc(host)

        elif self.os_name in ["windows", "gitbash"]:
            return self._load_wincred(host)

        else:
            return self._load_netrc(host)


    def delete(self, host="github.com"):
        """Remove token from storage"""

        if self.os_name == "macos":
            return self._delete_keychain(host)

        elif self.os_name in ["ubuntu", "wsl2", "arch", "fedora"]:
            if self._has_libsecret():
                return self._delete_libsecret(host)
            else:
                return self._delete_netrc(host)

        else:
            return self._delete_netrc(host)


    # ── macOS Keychain ──────────────────────

    def _save_keychain(self, token, username, host):
        try:
            subprocess.run([
                "security", "add-internet-password",
                "-a", username,
                "-s", host,
                "-w", token,
                "-U"
            ], check=True, capture_output=True)
            Printer.success("Token saved to macOS Keychain")
            return True
        except Exception as e:
            Printer.error(f"Keychain save failed: {e}")
            return self._save_netrc(token, username, host)


    def _load_keychain(self, host):
        try:
            result = subprocess.run([
                "security", "find-internet-password",
                "-s", host,
                "-w"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


    def _delete_keychain(self, host):
        try:
            subprocess.run([
                "security", "delete-internet-password",
                "-s", host
            ], check=True, capture_output=True)
            Printer.success("Token removed from Keychain")
            return True
        except Exception as e:
            Printer.error(f"Keychain delete failed: {e}")
            return False


    # ── Linux libsecret ─────────────────────

    def _has_libsecret(self):
        result = subprocess.run(
            ["which", "secret-tool"],
            capture_output=True
        )
        return result.returncode == 0


    def _save_libsecret(self, token, username, host):
        try:
            proc = subprocess.Popen(
                ["secret-tool", "store",
                 "--label", f"gitfast:{host}",
                 "host", host,
                 "user", username],
                stdin=subprocess.PIPE
            )
            proc.communicate(input=token.encode())
            Printer.success("Token saved to GNOME Keyring")
            return True
        except Exception as e:
            Printer.error(f"libsecret save failed: {e}")
            return self._save_netrc(token, username, host)


    def _load_libsecret(self, host):
        try:
            result = subprocess.run([
                "secret-tool", "lookup",
                "host", host
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


    def _delete_libsecret(self, host):
        try:
            subprocess.run([
                "secret-tool", "clear",
                "host", host
            ], check=True, capture_output=True)
            Printer.success("Token removed from GNOME Keyring")
            return True
        except Exception as e:
            Printer.error(f"libsecret delete failed: {e}")
            return False


    # ── Windows Credential Manager ───────────

    def _save_wincred(self, token, username, host):
        try:
            subprocess.run([
                "cmdkey",
                f"/generic:{host}",
                f"/user:{username}",
                f"/pass:{token}"
            ], check=True, capture_output=True)
            Printer.success("Token saved to Windows Credential Manager")
            return True
        except Exception as e:
            Printer.error(f"Windows cred save failed: {e}")
            return False


    def _load_wincred(self, host):
        # Windows credential manager doesn't easily expose passwords
        # so we check if credential exists
        try:
            result = subprocess.run([
                "cmdkey", f"/list:{host}"
            ], capture_output=True, text=True)
            if host in result.stdout:
                return "stored"
        except Exception:
            pass
        return None


    def _delete_wincred(self, host):
        try:
            subprocess.run([
                "cmdkey", f"/delete:{host}"
            ], check=True, capture_output=True)
            Printer.success("Token removed from Windows Credential Manager")
            return True
        except Exception as e:
            Printer.error(f"Windows cred delete failed: {e}")
            return False


    # ── .netrc fallback ──────────────────────

    def _save_netrc(self, token, username, host):
        try:
            # read existing
            content = ""
            if os.path.exists(NETRC_PATH):
                with open(NETRC_PATH, "r") as f:
                    content = f.read()

            # remove old entry for this host
            content = self._remove_netrc_entry(content, host)

            # add new entry
            content += f"\nmachine {host}\nlogin {username}\npassword {token}\n"

            # write
            with open(NETRC_PATH, "w") as f:
                f.write(content)

            # secure permissions
            os.chmod(NETRC_PATH, stat.S_IRUSR | stat.S_IWUSR)
            Printer.success(f"Token saved to {NETRC_PATH} (chmod 600)")
            return True

        except Exception as e:
            Printer.error(f"netrc save failed: {e}")
            return False


    def _load_netrc(self, host):
        if not os.path.exists(NETRC_PATH):
            return None
        try:
            with open(NETRC_PATH, "r") as f:
                lines = f.readlines()
            in_machine = False
            for line in lines:
                line = line.strip()
                if line.startswith(f"machine {host}"):
                    in_machine = True
                elif in_machine and line.startswith("password"):
                    return line.split(" ", 1)[1]
        except Exception:
            pass
        return None


    def _delete_netrc(self, host):
        if not os.path.exists(NETRC_PATH):
            return True
        try:
            with open(NETRC_PATH, "r") as f:
                content = f.read()
            content = self._remove_netrc_entry(content, host)
            with open(NETRC_PATH, "w") as f:
                f.write(content)
            Printer.success(f"Token removed from {NETRC_PATH}")
            return True
        except Exception as e:
            Printer.error(f"netrc delete failed: {e}")
            return False


    def _remove_netrc_entry(self, content, host):
        """Remove existing machine entry for host"""
        lines      = content.splitlines()
        result     = []
        skip       = False

        for line in lines:
            if line.strip().startswith(f"machine {host}"):
                skip = True
            elif skip and line.strip().startswith("machine"):
                skip = False

            if not skip:
                result.append(line)

        return "\n".join(result)
