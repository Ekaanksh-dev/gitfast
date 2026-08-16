import pytest


def test_detect_push_error_rejected():
    from gitfast.core.push_resolver import detect_push_error, ERROR_REJECTED
    stderr = "error: failed to push some refs\nhint: remote contains work"
    assert detect_push_error(stderr) == ERROR_REJECTED


def test_detect_push_error_no_upstream():
    from gitfast.core.push_resolver import detect_push_error, ERROR_NO_UPSTREAM
    stderr = "error: no upstream branch"
    assert detect_push_error(stderr) == ERROR_NO_UPSTREAM


def test_detect_push_error_permission():
    from gitfast.core.push_resolver import detect_push_error, ERROR_PERMISSION
    stderr = "ERROR: permission denied"
    assert detect_push_error(stderr) == ERROR_PERMISSION


def test_detect_push_error_not_found():
    from gitfast.core.push_resolver import detect_push_error, ERROR_REPO_NOT_FOUND
    stderr = "ERROR: repository not found"
    assert detect_push_error(stderr) == ERROR_REPO_NOT_FOUND


def test_detect_push_error_unknown():
    from gitfast.core.push_resolver import detect_push_error, ERROR_UNKNOWN
    stderr = "some random error"
    assert detect_push_error(stderr) == ERROR_UNKNOWN


def test_detect_push_error_empty():
    from gitfast.core.push_resolver import detect_push_error, ERROR_UNKNOWN
    assert detect_push_error("") == ERROR_UNKNOWN
    assert detect_push_error(None) == ERROR_UNKNOWN
