"""Validate the run record after a step has written its section.

The run record (YAML) holds what one run established, step by step:

- ``frame``: the decision, the validated problem and the candidates (step 1);
- ``gather``: the scope, counts, budget, principles and background (step 2);
- ``perspective_confirmations``: read by ``verification_gate.py`` (step 4);
- ``independence``: ``full`` or ``limited`` for the Prioritize and Rate passes
  (steps 5 and 6).

The format is ``assets/run-record.schema.json``; every section present is
checked against it. Dates are parsed by ``dates.parse_date``, exactly as by
``verification_gate.py``, so a quoted date fails both.

Beyond the format, a script checks only what the assistant did not write
itself (decision 12). For the gather section, with ``--requirements``, the
counts, the chosen drafts and the budget must match the script outputs. The
frame is written by the assistant, so its rules are instructions in
``references/frame.md``, not checks here.

Usage:
    python validate_run_record.py <run.yaml> [--section gather]
        [--requirements <filtered.json>] [--schema <schema file>]
        [--config <settings file>]

Without ``--section``, only the format and the dates are checked, as when a
run is resumed (decision 15). A null ``confirmed_by`` or ``confirmed_at``
means the section is not confirmed yet: it is valid format here, and
``verification_gate.py`` blocks on it.

Exit code 0 when valid, 1 otherwise; every error is listed on standard error.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from budget import point_budget
from dates import parse_date
from settings import load_settings

DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "assets" / "run-record.schema.json"
SECTIONS = ("frame", "gather")
# Sections with rules beyond the format. The frame is written by the assistant,
# so its rules are instructions in references/frame.md, not checks (decision 12).
CHECKED = ("gather",)


def _plain(value: Any) -> Any:
    """Return ``value`` with YAML dates turned into ISO strings, for the schema."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def _date_errors(data: Any) -> list[str]:
    """Parse every date field with the parser the verification gate uses."""
    if not isinstance(data, dict):
        return []
    fields: list[tuple[str, Any]] = []
    for section in SECTIONS:
        if isinstance(data.get(section), dict) and "confirmed_at" in data[section]:
            fields.append((f"{section}.confirmed_at", data[section]["confirmed_at"]))
    confirmations = data.get("perspective_confirmations")
    for i, entry in enumerate(confirmations if isinstance(confirmations, list) else []):
        if isinstance(entry, dict) and "confirmed_at" in entry:
            fields.append((f"perspective_confirmations.{i}.confirmed_at", entry["confirmed_at"]))
    errors: list[str] = []
    for where, value in fields:
        if value is None:  # not yet confirmed (decision 15); the gate blocks on it
            continue
        try:
            parse_date(value, "confirmed_at")
        except ValueError as exc:
            errors.append(f"{where}: {exc}")
    return errors


def _schema_errors(data: Any, schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(_plain(data)), key=lambda e: str(e.path))
    ]


def _gather_errors(
    gather: dict[str, Any], filtered: dict[str, Any] | None, budget_settings: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    name = str(gather["spreadsheet"])
    if "/" in name or "\\" in name:
        errors.append(f"gather: spreadsheet must be a file name only, not a path: {name}")
    if filtered is None:
        return errors

    actual = {
        "must": len(filtered["must"]),
        "should": len(filtered["should"]),
        "excluded_drafts": int(filtered["excluded_drafts"]["count"]),
    }
    for key, value in actual.items():
        if gather["counts"][key] != value:
            errors.append(
                f"gather: counts.{key} is {gather['counts'][key]}, the filter output has {value}"
            )
    recorded = sorted(str(i) for i in gather["included_drafts"])
    expected = sorted(str(i) for i in filtered.get("included_drafts") or [])
    if recorded != expected:
        errors.append(f"gather: included_drafts is {recorded}, the filter output has {expected}")
    count = actual["must"] + actual["should"]
    budget = point_budget(count, **budget_settings)
    if gather["budget"] != budget:
        errors.append(
            f"gather: budget is {gather['budget']}, the point budget for {count} "
            f"requirements is {budget}"
        )
    return errors


def run_record_errors(
    data: Any,
    section: str | None,
    filtered: dict[str, Any] | None = None,
    budget_settings: dict[str, Any] | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
) -> list[str]:
    """Return every problem with a parsed run record; empty when valid.

    Args:
        data: The parsed run record.
        section: ``gather`` to also check the gather section against the
            script outputs, or None to check the format only.
        filtered: The ``moscow_filter.py`` output, to check the gather
            counts and budget against.
        budget_settings: The ``budget`` settings; defaults to the shipped
            ``config.yaml``.
        schema_path: JSON Schema for the run record.
    """
    errors = _date_errors(data) + _schema_errors(data, schema_path)
    if errors or section is None:
        return errors
    if section not in data:
        return [*errors, f"no {section} section"]
    settings = budget_settings or load_settings()["budget"]
    return [*errors, *_gather_errors(data["gather"], filtered, settings)]


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Validate a run record section.")
    parser.add_argument("run_record", type=Path, help="Run record (YAML).")
    parser.add_argument(
        "--section", choices=CHECKED, help="Section to check; without it, the format only."
    )
    parser.add_argument("--requirements", type=Path, help="Output of moscow_filter.py.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="JSON Schema file.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        if not args.run_record.exists():
            raise FileNotFoundError(f"Run record not found: {args.run_record}")
        try:
            data = yaml.safe_load(args.run_record.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Run record '{args.run_record}' is not valid YAML: {exc}") from exc
        filtered = None
        if args.requirements:
            filtered = json.loads(args.requirements.read_text(encoding="utf-8"))
        budget_settings = load_settings(args.config)["budget"]
        errors = run_record_errors(data, args.section, filtered, budget_settings, args.schema)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    if errors:
        return 1
    if args.section is None:
        print("Run record valid: format.")
    else:
        print(f"Run record valid: {args.section} section.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
