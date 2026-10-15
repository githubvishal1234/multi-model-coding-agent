from importer import parse_rows


def test_parse_rows():
    assert parse_rows(["a,1", "b,2"]) == [("a", 1), ("b", 2)]
