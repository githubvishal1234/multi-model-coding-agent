import pytest

from stack import Stack


def test_push_pop_is_last_in_first_out():
    s = Stack()
    for x in (1, 2, 3):
        s.push(x)
    assert [s.pop(), s.pop(), s.pop()] == [3, 2, 1]


def test_peek_returns_top_without_removing():
    s = Stack()
    s.push("a")
    s.push("b")
    assert s.peek() == "b"
    assert len(s) == 2
    assert s.pop() == "b"


def test_is_empty_and_len():
    s = Stack()
    assert s.is_empty() and len(s) == 0
    s.push(1)
    s.push(2)
    assert not s.is_empty() and len(s) == 2
    s.pop()
    assert len(s) == 1


@pytest.mark.parametrize("method", ["pop", "peek"])
def test_empty_stack_raises(method):
    with pytest.raises(IndexError):
        getattr(Stack(), method)()
