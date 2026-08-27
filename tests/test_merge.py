import os
import tempfile
import pytest


CONFLICT_CONTENT = """def hello():
<<<<<<< HEAD
    return 'ours'
=======
    return 'theirs'
>>>>>>> feature-branch
"""

TWO_CONFLICTS = """
<<<<<<< HEAD
ours 1
=======
theirs 1
>>>>>>> branch
some code
<<<<<<< HEAD
ours 2
=======
theirs 2
>>>>>>> branch
"""


def make_conflict_file(content):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(content)
        return f.name


# ─────────────────────────────────────────
# parser tests
# ─────────────────────────────────────────

def test_parse_no_conflicts():
    from gitshorts.merge.parser import parse_conflicts
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write("def hello():\n    return 'world'\n")
        path = f.name
    conflicts = parse_conflicts(path)
    assert len(conflicts) == 0
    os.unlink(path)


def test_parse_one_conflict():
    from gitshorts.merge.parser import parse_conflicts
    path = make_conflict_file(CONFLICT_CONTENT)
    conflicts = parse_conflicts(path)
    assert len(conflicts) == 1
    assert "ours" in conflicts[0].ours
    assert "theirs" in conflicts[0].theirs
    os.unlink(path)


def test_parse_two_conflicts():
    from gitshorts.merge.parser import parse_conflicts
    path = make_conflict_file(TWO_CONFLICTS)
    conflicts = parse_conflicts(path)
    assert len(conflicts) == 2
    os.unlink(path)


def test_count_conflicts():
    from gitshorts.merge.parser import count_conflicts
    path = make_conflict_file(TWO_CONFLICTS)
    count = count_conflicts(path)
    assert count == 2
    os.unlink(path)


def test_has_conflicts_true():
    from gitshorts.merge.parser import has_conflicts
    path = make_conflict_file(CONFLICT_CONTENT)
    assert has_conflicts(path) == True
    os.unlink(path)


def test_has_conflicts_false():
    from gitshorts.merge.parser import has_conflicts
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write("clean code here")
        path = f.name
    assert has_conflicts(path) == False
    os.unlink(path)


# ─────────────────────────────────────────
# strategy tests
# ─────────────────────────────────────────

def test_strategy_ours():
    from gitshorts.merge.parser import parse_conflicts
    from gitshorts.merge.strategies import resolve_ours
    path = make_conflict_file(CONFLICT_CONTENT)
    conflicts = parse_conflicts(path)
    result = resolve_ours(conflicts[0])
    assert "ours" in result
    os.unlink(path)


def test_strategy_theirs():
    from gitshorts.merge.parser import parse_conflicts
    from gitshorts.merge.strategies import resolve_theirs
    path = make_conflict_file(CONFLICT_CONTENT)
    conflicts = parse_conflicts(path)
    result = resolve_theirs(conflicts[0])
    assert "theirs" in result
    os.unlink(path)


def test_strategy_longer():
    from gitshorts.merge.parser import Conflict
    from gitshorts.merge.strategies import resolve_longer
    conflict = Conflict(
        ours="line1\nline2\nline3",
        theirs="line1",
        branch="feature",
        start_line=0,
        end_line=5
    )
    result = resolve_longer(conflict)
    assert "line2" in result


def test_strategy_smart_empty_ours():
    from gitshorts.merge.parser import Conflict
    from gitshorts.merge.strategies import resolve_smart
    conflict = Conflict(
        ours="",
        theirs="their code here",
        branch="feature",
        start_line=0,
        end_line=5
    )
    result = resolve_smart(conflict)
    assert "their code" in result


def test_strategy_smart_empty_theirs():
    from gitshorts.merge.parser import Conflict
    from gitshorts.merge.strategies import resolve_smart
    conflict = Conflict(
        ours="our code here",
        theirs="",
        branch="feature",
        start_line=0,
        end_line=5
    )
    result = resolve_smart(conflict)
    assert "our code" in result


def test_strategy_smart_equal():
    from gitshorts.merge.parser import Conflict
    from gitshorts.merge.strategies import resolve_smart
    conflict = Conflict(
        ours="same code",
        theirs="same code",
        branch="feature",
        start_line=0,
        end_line=5
    )
    result = resolve_smart(conflict)
    assert "same code" in result


def test_apply_strategy_all():
    from gitshorts.merge.parser import parse_conflicts
    from gitshorts.merge.strategies import apply_strategy_to_all, Strategy
    path = make_conflict_file(TWO_CONFLICTS)
    conflicts = parse_conflicts(path)
    resolved = apply_strategy_to_all(conflicts, Strategy.OURS)
    assert len(resolved) == 2
    os.unlink(path)


# ─────────────────────────────────────────
# backup tests
# ─────────────────────────────────────────

def test_backup_create():
    from gitshorts.merge.backup import create_backup, delete_backup
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write("original content")
        path = f.name
    backup = create_backup(path)
    assert backup is not None
    assert os.path.exists(backup)
    assert "gitfast_backup" in backup
    delete_backup(backup)
    os.unlink(path)


def test_backup_restore():
    from gitshorts.merge.backup import create_backup, restore_backup
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write("original content")
        path = f.name
    backup = create_backup(path)
    with open(path, "w") as f:
        f.write("modified content")
    restore_backup(backup)
    with open(path, "r") as f:
        content = f.read()
    assert "original content" in content
    os.unlink(path)


def test_list_backups_empty():
    from gitshorts.merge.backup import list_backups
    tmp = tempfile.mkdtemp()
    backups = list_backups(tmp)
    assert backups == []
