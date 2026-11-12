"""Block prioritization until every selected perspective is verified and confirmed.

A person fully verifies a perspective once (``verified``, ``verified_by`` and
``verified_at`` in its header). In each run the user confirms it is still
correct, and that confirmation goes into the run record. Both are required.

Perspectives are looked up in the user's library folders, in the order given,
then in the shipped defaults; the user's copy wins on a matching id.

Usage:
    python verification_gate.py --perspective <id> [--perspective <id> ...]
        [--library <folder> ...] --run-record <run.yaml>

The gate reads only this section of the run record (the full format is
``assets/run-record.schema.json``)::

    perspective_confirmations:
      - id: security
        confirmed_by: <name>
        confirmed_at: 2026-11-12

Prints ``{"passed": bool, "perspectives": {id: file used}}`` as JSON. Exit code
0 when the gate passes, 1 otherwise; every failure is listed on standard error.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from validate_perspective import read_header, validate_perspective

SHIPPED_PERSPECTIVES = Path(__file__).resolve().parent.parent / "references" / "perspectives"


def resolve(
    perspective_id: str, libraries: Sequence[Path], shipped: Path = SHIPPED_PERSPECTIVES
) -> Path | None:
    """Return the file to use for a perspective, or None if no folder has it.

    Args:
        perspective_id: The perspective id (file name without ``.md``).
        libraries: The user's perspective folders, searched in order.
        shipped: The shipped defaults, searched last.
    """
    for folder in [*libraries, shipped]:
        candidate = folder / f"{perspective_id}.md"
        if candidate.is_file():
            return candidate
    return None


def _confirmations(run_record: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not run_record.exists():
        return {}, [f"Run record not found: {run_record}"]
    try:
        data = yaml.safe_load(run_record.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {}, [f"Run record '{run_record}' is not valid YAML: {exc}"]
    entries = data.get("perspective_confirmations") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return {}, [f"Run record '{run_record}' has no perspective_confirmations list"]
    found = {str(e.get("id")): e for e in entries if isinstance(e, dict) and e.get("id")}
    return found, []


def gate(
    perspective_ids: Sequence[str],
    libraries: Sequence[Path],
    run_record: Path,
    shipped: Path = SHIPPED_PERSPECTIVES,
) -> tuple[dict[str, Path], list[str]]:
    """Check every selected perspective; return the files used and every failure.

    Args:
        perspective_ids: The perspectives selected for this run.
        libraries: The user's perspective folders, searched before ``shipped``.
        run_record: The run record holding this run's confirmations.
        shipped: The shipped default perspectives.

    Returns:
        ``(files_used, errors)``. The gate passes when ``errors`` is empty.
    """
    confirmations, errors = _confirmations(run_record)
    record_readable = not errors
    used: dict[str, Path] = {}
    for pid in perspective_ids:
        path = resolve(pid, libraries, shipped)
        if path is None:
            folders = ", ".join(str(f) for f in [*libraries, shipped])
            errors.append(f"Perspective '{pid}' not found in: {folders}")
            continue
        used[pid] = path
        problems = validate_perspective(path)
        if problems:
            errors.extend(problems)
        elif (read_header(path) or {}).get("verified") is not True:
            errors.append(
                f"Perspective '{pid}' ({path}) is not verified; a person must review and "
                "verify it before it is used"
            )
        if record_readable:
            errors.extend(_confirmation_errors(pid, confirmations.get(pid)))
    return used, errors


def _confirmation_errors(pid: str, entry: dict[str, Any] | None) -> list[str]:
    if entry is None:
        return [f"Perspective '{pid}' is not confirmed for this run"]
    errors: list[str] = []
    by, at = entry.get("confirmed_by"), entry.get("confirmed_at")
    if not isinstance(by, str) or not by.strip():
        errors.append(f"Confirmation of '{pid}': confirmed_by must name a person")
    if not isinstance(at, date):
        errors.append(f"Confirmation of '{pid}': confirmed_at must be a date, got {at!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Check that perspectives may be used.")
    parser.add_argument("--perspective", action="append", required=True, help="Selected id.")
    parser.add_argument(
        "--library", action="append", type=Path, default=[], help="User perspective folder."
    )
    parser.add_argument("--run-record", type=Path, required=True, help="Run record (YAML).")
    args = parser.parse_args(argv)
    used, errors = gate(args.perspective, args.library, args.run_record)
    report = {"passed": not errors, "perspectives": {pid: str(p) for pid, p in used.items()}}
    print(json.dumps(report))
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
