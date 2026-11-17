"""Block prioritization until every selected perspective is verified and confirmed.

A person fully verifies a perspective once (``verified``, ``verified_by`` and
``verified_at`` in its header). In each run the user confirms it is still
correct, and that confirmation goes into the run record. Both are required.
Dates are parsed by ``dates.parse_date``, as in ``validate_run_record.py``.

Perspectives are looked up in this order (decision 18), and the first match on
the id wins:

1. the ``--library`` folders, in the order given: the copies verified in this
   run, the files attached to the chat, and a folder the user named;
2. ``perspectives.library`` in the settings, if set;
3. the packaged library, ``library/`` in the skill folder;
4. the shipped defaults, ``references/perspectives/``.

Where a file lives does not make it verified: every source is judged by the
header and the run's confirmation alone.

Usage:
    python verification_gate.py --perspective <id> [--perspective <id> ...]
        [--library <folder> ...] --run-record <run.yaml> [--config <settings file>]

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
from pathlib import Path
from typing import Any

import yaml

from dates import parse_date
from settings import load_settings
from validate_perspective import read_header, validate_perspective

SKILL_FOLDER = Path(__file__).resolve().parent.parent
SHIPPED_PERSPECTIVES = SKILL_FOLDER / "references" / "perspectives"
PACKAGED_LIBRARY = SKILL_FOLDER / "library"


def _folders(libraries: Sequence[Path], shipped: Path) -> list[Path]:
    return [*libraries, PACKAGED_LIBRARY, shipped]


def resolve(
    perspective_id: str, libraries: Sequence[Path], shipped: Path = SHIPPED_PERSPECTIVES
) -> Path | None:
    """Return the file to use for a perspective, or None if no folder has it.

    Args:
        perspective_id: The perspective id (file name without ``.md``).
        libraries: The given perspective folders, searched in order, before the
            packaged library.
        shipped: The shipped defaults, searched last.
    """
    for folder in _folders(libraries, shipped):
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
        libraries: The given perspective folders, searched before the packaged
            library and ``shipped``.
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
            folders = ", ".join(str(f) for f in _folders(libraries, shipped))
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
    try:
        parse_date(at, "confirmed_at")
    except ValueError as exc:
        errors.append(f"Confirmation of '{pid}': {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Check that perspectives may be used.")
    parser.add_argument("--perspective", action="append", required=True, help="Selected id.")
    parser.add_argument(
        "--library", action="append", type=Path, default=[], help="Perspective folder."
    )
    parser.add_argument("--run-record", type=Path, required=True, help="Run record (YAML).")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        configured = (load_settings(args.config).get("perspectives") or {}).get("library")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    libraries = [*args.library, *([Path(configured)] if configured else [])]
    used, errors = gate(args.perspective, libraries, args.run_record)
    report = {"passed": not errors, "perspectives": {pid: str(p) for pid, p in used.items()}}
    print(json.dumps(report))
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
