from stats import mean, median


def test_more_cases():
    assert median([1, 2]) == 1.5
    assert median([5]) == 5
    assert median([10, 2, 38, 23, 38, 23]) == 23
    assert mean([2, 4]) == 3
