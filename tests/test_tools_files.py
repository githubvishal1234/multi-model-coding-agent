import pytest
from helpers import call, make_ctx

from ferrule.tools import InvalidToolCall, ToolCall, default_tools, validate

# --- validation (F5) ---

def test_missing_argument_error_names_the_field():
    with pytest.raises(InvalidToolCall, match="path"):
        validate(default_tools(), ToolCall("read_file", {}))


def test_unknown_tool_lists_available_tools():
    with pytest.raises(InvalidToolCall, match="read_file"):
        validate(default_tools(), ToolCall("delete_everything", {}))


# --- read_file (F1) ---

def test_read_file_returns_exact_content(settings, ws):
    (ws / "a.txt").write_bytes("héllo\r\nworld\n".encode())
    ctx, _ = make_ctx(settings)
    r = call(ctx, "read_file", path="a.txt")
    assert r.ok and r.output == "héllo\r\nworld\n"


def test_read_file_line_range(settings, ws):
    (ws / "a.txt").write_bytes(b"1\n2\n3\n4\n")
    ctx, _ = make_ctx(settings)
    assert call(ctx, "read_file", path="a.txt", start_line=2, end_line=3).output == "2\n3\n"


@pytest.mark.parametrize("path", [".env", "../x.txt"])
def test_read_file_refuses_secret_and_escape(settings, ws, path):
    (ws / ".env").write_text("KEY=1")
    ctx, _ = make_ctx(settings)
    r = call(ctx, "read_file", path=path)
    assert not r.ok and r.error.startswith("refused")


def test_read_missing_file(settings):
    ctx, _ = make_ctx(settings)
    assert not call(ctx, "read_file", path="nope.txt").ok


def test_output_is_truncated(settings, ws):
    (ws / "big.txt").write_text("x" * 20000)
    ctx, _ = make_ctx(settings.model_copy(update={"max_output_chars": 500}))
    r = call(ctx, "read_file", path="big.txt")
    assert len(r.output) < 600 and "truncated" in r.output


# --- search_repo (F2) ---

@pytest.fixture
def repo(ws):
    (ws / "pkg").mkdir()
    (ws / "pkg" / "a.py").write_text("def needle():\n    pass\n")
    (ws / "pkg" / "b.py").write_text("x = 1\nneedle()  # call\n")
    (ws / "notes.md").write_text("no match here\nNeedle uppercase\n")
    (ws / ".git").mkdir()
    (ws / ".git" / "HEAD").write_text("needle in git")
    (ws / ".env").write_text("needle=secret")
    (ws / "bin.dat").write_bytes(b"\0needle")
    return ws


def test_search_plain_text(settings, repo):
    ctx, _ = make_ctx(settings)
    r = call(ctx, "search_repo", pattern="needle")
    assert r.output.splitlines() == ["pkg/a.py:1: def needle():", "pkg/b.py:2: needle()  # call"]


def test_search_regex_and_glob(settings, repo):
    ctx, _ = make_ctx(settings)
    assert call(ctx, "search_repo", pattern="[Nn]eedle", regex=True, glob="*.md").output == \
        "notes.md:2: Needle uppercase"


def test_search_bad_regex_and_no_matches(settings, repo):
    ctx, _ = make_ctx(settings)
    assert not call(ctx, "search_repo", pattern="(", regex=True).ok
    assert call(ctx, "search_repo", pattern="zzz").output == "no matches"


# --- create_file (F3) ---

def test_create_denied_leaves_nothing(settings, ws):
    ctx, approver = make_ctx(settings, [False])
    r = call(ctx, "create_file", path="new/a.py", content="print(1)\n")
    assert not r.ok and not (ws / "new" / "a.py").exists()
    assert approver.requests[0].kind == "create_file"


def test_create_approved_writes_file(settings, ws):
    ctx, _ = make_ctx(settings, [True])
    assert call(ctx, "create_file", path="new/a.py", content="print(1)\n").ok
    assert (ws / "new" / "a.py").read_text() == "print(1)\n"


def test_create_refuses_existing_file(settings, ws):
    (ws / "a.py").write_text("old")
    ctx, approver = make_ctx(settings, [True])
    assert not call(ctx, "create_file", path="a.py", content="new").ok
    assert (ws / "a.py").read_text() == "old" and approver.requests == []


# --- edit_file (F4) ---

def test_edit_shows_diff_and_deny_leaves_file(settings, ws):
    (ws / "a.py").write_text("x = 1\ny = 2\n")
    ctx, approver = make_ctx(settings, [False])
    r = call(ctx, "edit_file", path="a.py", old="y = 2", new="y = 3")
    assert not r.ok and (ws / "a.py").read_text() == "x = 1\ny = 2\n"
    assert "-y = 2" in approver.requests[0].detail and "+y = 3" in approver.requests[0].detail


def test_edit_approved_applies(settings, ws):
    (ws / "a.py").write_text("x = 1\ny = 2\n")
    ctx, _ = make_ctx(settings, [True])
    assert call(ctx, "edit_file", path="a.py", old="y = 2", new="y = 3").ok
    assert (ws / "a.py").read_text() == "x = 1\ny = 3\n"


@pytest.mark.parametrize("old", ["missing", "x"])  # 0 matches, 2 matches
def test_edit_requires_exactly_one_match(settings, ws, old):
    (ws / "a.py").write_text("x = 1\nx = 2\n")
    ctx, approver = make_ctx(settings, [True])
    r = call(ctx, "edit_file", path="a.py", old=old, new="z")
    assert not r.ok and "exactly once" in r.error and approver.requests == []


def test_edit_crlf_file_with_lf_old_text(settings, ws):
    (ws / "a.py").write_bytes(b"a = 1\r\nb = 2\r\n")
    ctx, _ = make_ctx(settings, [True])
    assert call(ctx, "edit_file", path="a.py", old="a = 1\nb = 2", new="a = 1\nb = 3").ok
    assert (ws / "a.py").read_bytes() == b"a = 1\r\nb = 3\r\n"
