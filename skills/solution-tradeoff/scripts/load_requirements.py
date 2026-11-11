"""Load requirements and principles from a requirements spreadsheet (.xlsx).

This is the only script that needs ``openpyxl``. Sheet and column names come
from the ``spreadsheet`` section of the settings file, never from code.

Usage:
    python load_requirements.py <requirements.xlsx> [--config <settings file>]

Prints ``{"requirements": [...], "principles": [...]}`` as JSON, each row keyed
by the logical column names from the settings file.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.worksheet.worksheet import Worksheet

from settings import load_settings

Row = dict[str, Any]


def _headers(sheet: Worksheet) -> dict[str, int]:
    """Map each non-empty header in the first row to its zero-based position."""
    first = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
    return {str(v).strip(): i for i, v in enumerate(first) if v is not None}


def _sheet(workbook: Any, name: str, setting: str) -> Worksheet:
    if name not in workbook.sheetnames:
        raise ValueError(
            f"Sheet '{name}' not found. Available sheets: {workbook.sheetnames}. "
            f"Update 'spreadsheet.{setting}' in the settings file."
        )
    sheet: Worksheet = workbook[name]
    return sheet


def _read_rows(
    sheet: Worksheet, columns: dict[str, str], optional: set[str], setting: str
) -> list[Row]:
    headers = _headers(sheet)
    positions: dict[str, int | None] = {}
    for key, header in columns.items():
        if header in headers:
            positions[key] = headers[header]
        elif key in optional:
            warnings.warn(f"Column '{header}' ({key}) not found in sheet '{sheet.title}'; null.")
            positions[key] = None
        else:
            raise ValueError(
                f"Required column '{header}' not found in sheet '{sheet.title}'. "
                f"Available columns: {list(headers)}. "
                f"Update 'spreadsheet.{setting}.{key}' in the settings file."
            )
    rows: list[Row] = []
    for values in sheet.iter_rows(min_row=2, values_only=True):
        if not any(v is not None and v != "" for v in values):
            continue
        rows.append(
            {
                key: (values[pos] if pos is not None and pos < len(values) else None)
                for key, pos in positions.items()
            }
        )
    return rows


def load_requirements(path: Path, cfg: dict[str, Any]) -> tuple[list[Row], list[Row]]:
    """Read requirement and principle rows from a spreadsheet.

    Args:
        path: The .xlsx file.
        cfg: The ``spreadsheet`` section of the settings file.

    Returns:
        ``(requirement_rows, principle_rows)``. Requirement rows are not
        filtered; use ``moscow_filter.py`` for that.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a readable workbook, or a sheet or
            required column is missing.
    """
    if not path.exists():
        raise FileNotFoundError(f"Requirements file not found: {path}")
    try:
        workbook = load_workbook(path, read_only=True, data_only=True)
    except (InvalidFileException, KeyError, OSError) as exc:
        raise ValueError(f"Cannot read '{path}' as an .xlsx workbook: {exc}") from exc
    try:
        optional = set(cfg.get("optional_columns") or [])
        requirements = _read_rows(
            _sheet(workbook, cfg["requirements_sheet"], "requirements_sheet"),
            cfg["columns"],
            optional,
            "columns",
        )
        principles = _read_rows(
            _sheet(workbook, cfg["principles_sheet"], "principles_sheet"),
            cfg["principles_columns"],
            set(),
            "principles_columns",
        )
    finally:
        workbook.close()
    return requirements, principles


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Load requirements from a spreadsheet.")
    parser.add_argument("spreadsheet", type=Path, help="Requirements .xlsx file.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        cfg = load_settings(args.config)["spreadsheet"]
        requirements, principles = load_requirements(args.spreadsheet, cfg)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"requirements": requirements, "principles": principles}, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
