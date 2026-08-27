import os
import tempfile
import pytest


def test_bash_shortcuts_contains_gcp():
    from gitshorts.shells.bash import BASH_SHORTCUTS
    assert "gcp" in BASH_SHORTCUTS


def test_bash_shortcuts_contains_gmerge():
    from gitshorts.shells.bash import BASH_SHORTCUTS
    assert "gconflicts" in BASH_SHORTCUTS


def test_bash_shortcuts_contains_gtoken():
    from gitshorts.shells.bash import BASH_SHORTCUTS
    assert "gtoken" in BASH_SHORTCUTS


def test_bash_install_uninstall():
    from gitshorts.shells.bash import install, uninstall
    tmp = tempfile.mktemp(suffix=".bashrc")
    with open(tmp, "w") as f:
        f.write("# existing config\n")
    result = install(tmp)
    assert result == True
    with open(tmp, "r") as f:
        content = f.read()
    assert "gitshorts shortcuts" in content
    uninstall(tmp)
    with open(tmp, "r") as f:
        content = f.read()
    assert "gitshorts shortcuts" not in content
    os.unlink(tmp)


def test_bash_install_skips_duplicate():
    from gitshorts.shells.bash import install
    tmp = tempfile.mktemp(suffix=".bashrc")
    with open(tmp, "w") as f:
        f.write("# existing config\n")
    install(tmp)
    result = install(tmp)
    assert result == True
    os.unlink(tmp)


def test_fish_shortcuts_contains_gcp():
    from gitshorts.shells.fish import FISH_SHORTCUTS
    assert "gcp" in FISH_SHORTCUTS


def test_fish_shortcuts_contains_gtoken():
    from gitshorts.shells.fish import FISH_SHORTCUTS
    assert "gtoken" in FISH_SHORTCUTS


def test_fish_install_uninstall():
    from gitshorts.shells.fish import install, uninstall
    tmp = tempfile.mktemp(suffix=".fish")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, "w") as f:
        f.write("# existing config\n")
    result = install(tmp)
    assert result == True
    uninstall(tmp)
    with open(tmp, "r") as f:
        content = f.read()
    assert "gitshorts shortcuts" not in content
    os.unlink(tmp)


def test_zsh_shortcuts_contains_gcp():
    from gitshorts.shells.zsh import ZSH_SHORTCUTS
    assert "gcp" in ZSH_SHORTCUTS


def test_zsh_install_uninstall():
    from gitshorts.shells.zsh import install, uninstall
    tmp = tempfile.mktemp(suffix=".zshrc")
    with open(tmp, "w") as f:
        f.write("# existing config\n")
    result = install(tmp)
    assert result == True
    uninstall(tmp)
    with open(tmp, "r") as f:
        content = f.read()
    assert "gitshorts shortcuts" not in content
    os.unlink(tmp)
