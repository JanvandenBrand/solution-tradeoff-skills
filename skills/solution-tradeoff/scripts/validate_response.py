"""Validate perspective response files against the output schema.

Usage:
    python validate_response.py <file or directory> [...] [--schema <schema file>]

Directories are searched for ``*.yaml`` files. Exit code 0 when every file is
valid, 1 otherwise; every error is listed on standard error.
"""

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml

DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "assets" / "tradeoff-output.schema.json"


class ResponseError:
    """One schema problem in one response file."""

    def __init__(self, file: Path, message: str) -> None:
        self.file = file
        self.message = message

    def __str__(self) -> str:
        return f"{self.file.name}: {self.message}"


def _load_schema(schema_path: Path) -> dict[str, object]:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    schema: dict[str, object] = json.loads(schema_path.read_text(encoding="utf-8"))
    return schema


def validate_file(path: Path, schema_path: Path = DEFAULT_SCHEMA) -> list[ResponseError]:
    """Validate one YAML response file.

    Args:
        path: Response file to check.
        schema_path: JSON Schema (draft 2020-12) to check against.

    Returns:
        Every problem found; empty when the file is valid.

    Raises:
        FileNotFoundError: If the schema file does not exist.
    """
    schema = _load_schema(schema_path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [ResponseError(path, f"Invalid YAML: {exc}")]
    if not isinstance(data, dict):
        return [ResponseError(path, f"Expected a YAML mapping, got {type(data).__name__}")]

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: str(e.path))
    return [
        ResponseError(path, f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}")
        for e in errors
    ]


def validate_directory(
    responses_dir: Path, schema_path: Path = DEFAULT_SCHEMA
) -> dict[Path, list[ResponseError]]:
    """Validate every ``*.yaml`` file in a directory.

    Returns:
        Mapping of file to its problems (empty list when valid).

    Raises:
        FileNotFoundError: If the directory or the schema does not exist.
    """
    if not responses_dir.exists():
        raise FileNotFoundError(f"Responses directory not found: {responses_dir}")
    return {path: validate_file(path, schema_path) for path in sorted(responses_dir.glob("*.yaml"))}


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Validate perspective response files.")
    parser.add_argument("paths", type=Path, nargs="+", help="Response files or directories.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="JSON Schema file.")
    args = parser.parse_args(argv)
    results: dict[Path, list[ResponseError]] = {}
    try:
        for path in args.paths:
            if path.is_dir():
                results.update(validate_directory(path, args.schema))
            elif path.exists():
                results[path] = validate_file(path, args.schema)
            else:
                raise FileNotFoundError(f"Response file not found: {path}")
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    problems = [err for errs in results.values() for err in errs]
    for err in problems:
        print(f"error: {err}", file=sys.stderr)
    if problems:
        return 1
    print(f"{len(results)} response file(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
