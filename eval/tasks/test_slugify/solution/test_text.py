from text import slugify


def test_words_and_capitals():
    assert slugify("Hello World") == "hello-world"


def test_punctuation_removed():
    assert slugify("Hi, there! It's me.") == "hi-there-it-s-me"


def test_extra_whitespace():
    assert slugify("  many   spaces  here ") == "many-spaces-here"
