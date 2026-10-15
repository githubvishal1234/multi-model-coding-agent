import argparse
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Count words in a text file.")
    parser.add_argument("path", type=Path)
    parser.add_argument("-l", "--lines", action="store_true", help="also print the line count")
    args = parser.parse_args(argv)
    text = args.path.read_text(encoding="utf-8")
    print(f"{len(text.split())} words")
    if args.lines:
        print(f"{len(text.splitlines())} lines")


if __name__ == "__main__":
    main()
