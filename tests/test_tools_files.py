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


# --- write_file (F3) ---

def test_write_new_file_denied_leaves_nothing(settings, ws):
    ctx, approver = make_ctx(settings, [False])
    r = call(ctx, "write_file", path="new/a.py", content="print(1)\n")
    assert not r.ok and not (ws / "new" / "a.py").exists()
    assert approver.requests[0].kind == "write_file"


def test_write_new_file_approved(settings, ws):
    ctx, _ = make_ctx(settings, [True])
    r = call(ctx, "write_file", path="new/a.py", content="print(1)\n")
    assert r.output == "created new/a.py"
    assert (ws / "new" / "a.py").read_text() == "print(1)\n"


def test_replace_shows_diff_and_deny_keeps_file(settings, ws):
    (ws / "a.py").write_bytes(b"x = 1\ny = 2\n")
    ctx, approver = make_ctx(settings, [False])
    r = call(ctx, "write_file", path="a.py", content="x = 1\ny = 3\n")
    assert not r.ok and (ws / "a.py").read_bytes() == b"x = 1\ny = 2\n"
    req = approver.requests[0]
    assert req.summary == "replace a.py" and "-y = 2" in req.detail and "+y = 3" in req.detail


def test_replace_approved(settings, ws):
    (ws / "a.py").write_bytes(b"x = 1\n")
    ctx, _ = make_ctx(settings, [True])
    assert call(ctx, "write_file", path="a.py", content="x = 2\n").output == "replaced a.py"
    assert (ws / "a.py").read_bytes() == b"x = 2\n"


def test_replace_keeps_crlf_line_endings(settings, ws):
    (ws / "a.py").write_bytes(b"a = 1\r\nb = 2\r\n")
    ctx, _ = make_ctx(settings, [True])
    assert call(ctx, "write_file", path="a.py", content="a = 1\nb = 3\n").ok
    assert (ws / "a.py").read_bytes() == b"a = 1\r\nb = 3\r\n"


def test_unchanged_content_needs_no_approval(settings, ws):
    (ws / "a.py").write_bytes(b"x = 1\n")
    ctx, approver = make_ctx(settings, [True])
    assert call(ctx, "write_file", path="a.py", content="x = 1\n").ok and approver.requests == []


@pytest.mark.parametrize("path", ["../out.txt", ".env", "sub"])
def test_write_refuses_escape_secret_and_directory(settings, ws, path):
    (ws / "sub").mkdir()
    ctx, approver = make_ctx(settings, [True])
    assert not call(ctx, "write_file", path=path, content="x").ok and approver.requests == []


def test_edit_missing_file_points_to_write_file(settings):
    ctx, _ = make_ctx(settings, [True])
    assert "write_file" in call(ctx, "edit_file", path="nope.py", old="a", new="b").error


def test_invalid_arguments_include_usage():
    # Seen in eval: edit_file with old="" repeated 3 times; the error must say what to do.
    with pytest.raises(InvalidToolCall, match="use write_file"):
        validate(default_tools(), ToolCall("edit_file", {"path": "A.txt", "old": "", "new": "5"}))


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
