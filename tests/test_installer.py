import pytest


def test_version():
    from gitfast import __version__
    assert __version__ == "1.0.4"


def test_banner():
    from gitfast import banner
    banner()


def test_detector_init():
    from gitfast.core.detector import SystemInfo
    info = SystemInfo()
    assert info.os is not None
    assert info.shell is not None
    assert info.config is not None


def test_updater_version():
    from gitfast.core.updater import get_latest_version
    version = get_latest_version()
    assert version is None or isinstance(version, str)


def test_is_update_available():
    from gitfast.core.updater import is_update_available
    available, latest = is_update_available()
    assert isinstance(available, bool)
