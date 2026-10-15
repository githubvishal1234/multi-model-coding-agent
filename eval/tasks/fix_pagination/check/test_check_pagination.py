import pytest

from pagination import paginate, total_pages

ITEMS = list(range(1, 26))  # 25 items


def test_first_page_starts_at_first_item():
    assert paginate(ITEMS, 1, 10) == list(range(1, 11))


def test_middle_and_last_partial_page():
    assert paginate(ITEMS, 2, 10) == list(range(11, 21))
    assert paginate(ITEMS, 3, 10) == [21, 22, 23, 24, 25]


def test_page_past_the_end_is_empty():
    assert paginate(ITEMS, 4, 10) == []


def test_every_item_appears_exactly_once():
    pages = [paginate(ITEMS, p, 7) for p in range(1, total_pages(len(ITEMS), 7) + 1)]
    assert [x for page in pages for x in page] == ITEMS


@pytest.mark.parametrize("page,per_page", [(0, 10), (-1, 10), (1, 0)])
def test_invalid_arguments_still_raise(page, per_page):
    with pytest.raises(ValueError):
        paginate(ITEMS, page, per_page)


def test_total_pages_unchanged():
    assert total_pages(0, 10) == 1
    assert total_pages(25, 10) == 3
