import urllib.request
import urllib.error
import json
from gitshorts.utils.colors import Printer


GITHUB_API    = "https://api.github.com"
GITLAB_API    = "https://gitlab.com/api/v4"
BITBUCKET_API = "https://api.bitbucket.org/2.0"


class TokenInfo:
    def __init__(self):
        self.valid       = False
        self.username    = None
        self.host        = None
        self.permissions = []
        self.expires     = None
        self.error       = None

    def __repr__(self):
        return (
            f"TokenInfo("
            f"valid={self.valid}, "
            f"user={self.username}, "
            f"host={self.host})"
        )


def validate_github(token):
    """Validate GitHub personal access token"""
    info = TokenInfo()
    info.host = "github.com"

    try:
        req = urllib.request.Request(
            f"{GITHUB_API}/user",
            headers={
                "Authorization": f"token {token}",
                "Accept":        "application/vnd.github.v3+json",
                "User-Agent":    "gitshorts"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            info.valid    = True
            info.username = data.get("login")

            # check scopes from headers
            scopes = response.headers.get("X-OAuth-Scopes", "")
            if scopes:
                info.permissions = [s.strip() for s in scopes.split(",")]

            # check expiry
            expiry = response.headers.get("GitHub-Authentication-Token-Expiration")
            if expiry:
                info.expires = expiry

    except urllib.error.HTTPError as e:
        if e.code == 401:
            info.error = "Invalid token — unauthorized"
        elif e.code == 403:
            info.error = "Token lacks required permissions"
        else:
            info.error = f"HTTP error: {e.code}"

    except urllib.error.URLError as e:
        info.error = f"Network error: {e.reason}"

    except Exception as e:
        info.error = f"Unexpected error: {e}"

    return info


def validate_gitlab(token):
    """Validate GitLab personal access token"""
    info = TokenInfo()
    info.host = "gitlab.com"

    try:
        req = urllib.request.Request(
            f"{GITLAB_API}/user",
            headers={
                "PRIVATE-TOKEN": token,
                "User-Agent":    "gitshorts"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            info.valid    = True
            info.username = data.get("username")

    except urllib.error.HTTPError as e:
        if e.code == 401:
            info.error = "Invalid GitLab token"
        else:
            info.error = f"HTTP error: {e.code}"

    except Exception as e:
        info.error = f"Error: {e}"

    return info


def validate_bitbucket(token):
    """Validate Bitbucket app password"""
    info = TokenInfo()
    info.host = "bitbucket.org"

    try:
        req = urllib.request.Request(
            f"{BITBUCKET_API}/user",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent":    "gitshorts"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            info.valid    = True
            info.username = data.get("display_name")

    except urllib.error.HTTPError as e:
        if e.code == 401:
            info.error = "Invalid Bitbucket token"
        else:
            info.error = f"HTTP error: {e.code}"

    except Exception as e:
        info.error = f"Error: {e}"

    return info


def validate_token(token, host="github.com"):
    """Validate token for any supported host"""

    if not token:
        Printer.error("No token provided")
        return None

    Printer.scan(f"Validating token for {host}...")

    if "github" in host:
        info = validate_github(token)
    elif "gitlab" in host:
        info = validate_gitlab(token)
    elif "bitbucket" in host:
        info = validate_bitbucket(token)
    else:
        info = validate_github(token)

    if info.valid:
        Printer.success(f"Token valid — logged in as: {info.username}")
    else:
        Printer.error(f"Token invalid — {info.error}")

    return info


def display_token_info(info):
    """Display token information"""
    if not info:
        return

    Printer.header("Token Status")
    print(f"  Valid       : {'yes' if info.valid else 'no'}")
    print(f"  Host        : {info.host or 'unknown'}")
    print(f"  Username    : {info.username or 'unknown'}")

    if info.permissions:
        print(f"  Permissions : {', '.join(info.permissions)}")

    if info.expires:
        print(f"  Expires     : {info.expires}")
    else:
        print(f"  Expires     : no expiry set")

    if info.error:
        print(f"  Error       : {info.error}")

    Printer.divider()
