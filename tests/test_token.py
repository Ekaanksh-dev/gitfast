import pytest


# ─────────────────────────────────────────
# expiry tests
# ─────────────────────────────────────────

def test_expiry_none():
    from gitfast.token.expiry import days_until_expiry
    result = days_until_expiry(None)
    assert result is None


def test_expiry_future():
    from gitfast.token.expiry import days_until_expiry
    result = days_until_expiry("2099-12-31")
    assert result > 0


def test_expiry_past():
    from gitfast.token.expiry import days_until_expiry
    result = days_until_expiry("2000-01-01")
    assert result < 0


def test_should_warn_false():
    from gitfast.token.expiry import should_warn
    assert should_warn("2099-12-31") == False


def test_should_warn_true():
    from gitfast.token.expiry import should_warn
    assert should_warn("2000-01-01") == True


def test_format_expiry_none():
    from gitfast.token.expiry import format_expiry_display
    result = format_expiry_display(None)
    assert result == "no expiry"


def test_format_expiry_past():
    from gitfast.token.expiry import format_expiry_display
    result = format_expiry_display("2000-01-01")
    assert "EXPIRED" in result


def test_parse_expiry_valid():
    from gitfast.token.expiry import parse_expiry
    result = parse_expiry("2099-12-31")
    assert result is not None


def test_parse_expiry_invalid():
    from gitfast.token.expiry import parse_expiry
    result = parse_expiry("not-a-date")
    assert result is None


# ─────────────────────────────────────────
# storage tests
# ─────────────────────────────────────────

def test_storage_init():
    from gitfast.token.storage import TokenStorage
    storage = TokenStorage()
    assert storage is not None
    assert storage.os_name is not None


def test_netrc_save_load_delete():
    from gitfast.token.storage import TokenStorage
    import tempfile
    import os

    storage = TokenStorage()
    tmp_netrc = tempfile.mktemp()

    # monkey patch netrc path
    import gitfast.token.storage as s
    original = s.NETRC_PATH
    s.NETRC_PATH = tmp_netrc

    # save
    storage._save_netrc("testtoken123", "testuser", "test.example.com")

    # load
    token = storage._load_netrc("test.example.com")
    assert token == "testtoken123"

    # delete
    storage._delete_netrc("test.example.com")
    token = storage._load_netrc("test.example.com")
    assert token is None

    # cleanup
    s.NETRC_PATH = original
    if os.path.exists(tmp_netrc):
        os.unlink(tmp_netrc)
