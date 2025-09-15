import argparse
import json
from pathlib import Path
import sys


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse a JSON file and print the resulting object."
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file to parse",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (default pretty-prints)",
    )
    return parser.parse_args(argv)


def load_json_file(file_path):
    path = Path(file_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Not a file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    args = parse_arguments(argv)
    try:
        data = load_json_file(args.json_file)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except IsADirectoryError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        location = f"line {exc.lineno}, column {exc.colno}"
        print(f"Invalid JSON in {args.json_file}: {exc.msg} ({location})", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"Unexpected error reading {args.json_file}: {exc}", file=sys.stderr)
        return 1

    if args.compact:
        print(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())