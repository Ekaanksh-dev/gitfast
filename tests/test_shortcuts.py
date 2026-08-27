import os
import subprocess
import tempfile
import pytest


def run(cmd):
    result = subprocess.run(
        cmd, shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def setup_test_repo():
    tmp = tempfile.mkdtemp()
    run(f"git init {tmp}")
    run(f"git -C {tmp} config user.email 'test@test.com'")
    run(f"git -C {tmp} config user.name 'Test'")
    return tmp


# ─────────────────────────────────────────
# utils tests
# ─────────────────────────────────────────

def test_colors_import():
    from gitshorts.utils.colors import Colors, Printer
    assert Colors is not None
    assert Printer is not None
    assert isinstance(Colors.GREEN, str)
    assert isinstance(Colors.RED, str)
    assert isinstance(Colors.RESET, str)

def test_printer_methods():
    from gitshorts.utils.colors import Printer
    Printer.success("test")
    Printer.error("test")
    Printer.warning("test")
    Printer.info("test")


def test_os_detection():
    from gitshorts.utils.os_utils import get_os
    os_name = get_os()
    assert os_name in [
        "ubuntu", "arch", "fedora",
        "macos", "wsl2", "windows",
        "gitbash", "unknown"
    ]


def test_shell_detection():
    from gitshorts.utils.os_utils import get_shell
    shell = get_shell()
    assert shell in ["bash", "zsh", "fish", "powershell"]


def test_shell_config_path():
    from gitshorts.utils.os_utils import get_shell_config
    config = get_shell_config()
    assert config is not None
    assert len(config) > 0


def test_package_manager():
    from gitshorts.utils.os_utils import get_package_manager
    mgr = get_package_manager()
    assert mgr in ["apt", "pacman", "dnf", "brew", "winget"]


# ─────────────────────────────────────────
# git utils tests
# ─────────────────────────────────────────

def test_git_not_repo():
    from gitshorts.utils.git import is_git_repo
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    assert is_git_repo() == False


def test_git_is_repo():
    from gitshorts.utils.git import is_git_repo
    tmp = setup_test_repo()
    os.chdir(tmp)
    assert is_git_repo() == True


def test_current_branch():
    from gitshorts.utils.git import current_branch
    tmp = setup_test_repo()
    os.chdir(tmp)
    run(f"touch {tmp}/file.txt")
    run(f"git -C {tmp} add .")
    run(f"git -C {tmp} commit -m 'init'")
    branch = current_branch()
    assert branch in ["main", "master"]


def test_run_git():
    from gitshorts.utils.git import run_git
    tmp = setup_test_repo()
    os.chdir(tmp)
    out, err, code = run_git("status")
    assert code == 0


def test_get_status():
    from gitshorts.utils.git import get_status
    tmp = setup_test_repo()
    os.chdir(tmp)
    status = get_status()
    assert isinstance(status, str)


def test_stage_all():
    from gitshorts.utils.git import stage_all, is_git_repo
    tmp = setup_test_repo()
    os.chdir(tmp)
    run(f"touch {tmp}/newfile.txt")
    result = stage_all()
    assert result == True


def test_commit():
    from gitshorts.utils.git import stage_all, commit
    tmp = setup_test_repo()
    os.chdir(tmp)
    run(f"git -C {tmp} config user.email 'test@test.com'")
    run(f"git -C {tmp} config user.name 'Test'")
    run(f"touch {tmp}/file.txt")
    stage_all()
    result = commit("test commit")
    assert result == True
