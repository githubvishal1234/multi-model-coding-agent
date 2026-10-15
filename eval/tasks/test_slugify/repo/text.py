import re


def slugify(title):
    """Turn a title into a URL slug: lowercase words joined by '-', punctuation removed."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return "-".join(words)
