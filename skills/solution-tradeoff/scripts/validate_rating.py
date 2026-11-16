"""Validate a rating file: every candidate rated on every in-scope requirement.

The rater sees only the candidates and the requirements. The schema has no
place for preferences or points. Every rating names its basis (``source``,
``judgment`` or ``unread_source``), and a source-based rating may name its
background item in ``source``; ``elimination.py`` reads the basis.

Usage:
    python validate_rating.py <ratings.yaml> --requirements <filtered.json>
        [--schema <schema file>] [--config <settings file>]

``filtered.json`` is the output of ``moscow_filter.py``; its Must and Should
requirements are the scope. Exit code 0 when valid, 1 otherwise; every error
is listed on standard error.
"""

import argparse
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from settings import load_settings

DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "assets" / "rating.schema.json"

Scores = dict[str, dict[str, int]]


def read_scope(path: Path) -> tuple[list[str], list[str]]:
    """Return ``(must_ids, should_ids)`` from a ``moscow_filter.py`` output file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid JSON.
        KeyError: If the file has no ``must`` or ``should`` list.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return (
        [str(r["req_id"]) for r in data["must"]],
        [str(r["req_id"]) for r in data["should"]],
    )


def rating_errors(
    data: Any,
    must_ids: Sequence[str],
    should_ids: Sequence[str],
    minimum: int,
    maximum: int,
    schema_path: Path = DEFAULT_SCHEMA,
) -> list[str]:
    """Return every problem with parsed rating data; empty when valid.

    Args:
        data: The parsed rating file.
        must_ids: In-scope Must requirement identifiers.
        should_ids: In-scope Should requirement identifiers.
        minimum: Lowest rating allowed.
        maximum: Highest rating allowed.
        schema_path: JSON Schema for the rating file.
    """
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: str(e.path))
    ]
    if schema_errors:
        return schema_errors

    errors: list[str] = []
    candidates = list(data["candidates"])
    scope = [*must_ids, *should_ids]
    pairs = Counter((r["candidate"], r["requirement_id"]) for r in data["ratings"])
    for i, r in enumerate(data["ratings"]):
        where = f"ratings.{i}"
        if not minimum <= r["rating"] <= maximum:
            errors.append(f"{where}: rating {r['rating']} is not between {minimum} and {maximum}")
        if r["candidate"] not in candidates:
            errors.append(f"{where}: candidate '{r['candidate']}' is not listed in candidates")
        if r["requirement_id"] not in scope:
            errors.append(f"{where}: requirement '{r['requirement_id']}' is not in scope")
    for (candidate, req_id), count in sorted(pairs.items()):
        if count > 1:
            errors.append(f"candidate '{candidate}' is rated on '{req_id}' more than once")
    for candidate in candidates:
        for req_id in scope:
            if (candidate, req_id) not in pairs:
                errors.append(f"candidate '{candidate}' has no rating for '{req_id}'")
    return errors


def load_ratings(
    path: Path,
    must_ids: Sequence[str],
    should_ids: Sequence[str],
    minimum: int,
    maximum: int,
    schema_path: Path = DEFAULT_SCHEMA,
) -> Scores:
    """Read and validate a rating file, returning the rating per requirement per candidate.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid YAML or breaks any rule; the
            message lists every problem.
    """
    if not path.exists():
        raise FileNotFoundError(f"Rating file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Rating file '{path}' is not valid YAML: {exc}") from exc
    errors = rating_errors(data, must_ids, should_ids, minimum, maximum, schema_path)
    if errors:
        raise ValueError("\n".join(f"{path.name}: {e}" for e in errors))
    scores: Scores = {c: {} for c in data["candidates"]}
    for r in data["ratings"]:
        scores[r["candidate"]][r["requirement_id"]] = r["rating"]
    return scores


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Validate a rating file.")
    parser.add_argument("ratings", type=Path, help="Rating file (YAML).")
    parser.add_argument(
        "--requirements", type=Path, required=True, help="Output of moscow_filter.py."
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="JSON Schema file.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        scale = load_settings(args.config)["rating"]
        must_ids, should_ids = read_scope(args.requirements)
        scores = load_ratings(
            args.ratings, must_ids, should_ids, scale["minimum"], scale["maximum"], args.schema
        )
    except (OSError, ValueError, KeyError) as exc:
        for line in str(exc).splitlines():
            print(f"error: {line}", file=sys.stderr)
        return 1
    count = len(must_ids) + len(should_ids)
    print(f"Rating file valid: {len(scores)} candidates, {count} requirements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
