"""Check the requirements spreadsheet prerequisites before a first analysis.

Draft requirements are scoped by the decision-reference column (``ad_ref`` in
the settings, "AD Ref" by default). Without that column, drafts cannot be
scoped: the check fails and lists the drafts so the user can choose which ones
belong to the current decision. Pass each chosen draft to ``moscow_filter.py``
with ``--include-draft``.

Usage:
    python check_prerequisites.py <requirements.xlsx> [--decision <reference>]
        [--config <settings file>]

Prints a JSON report. Exit code 0 when every prerequisite is met, 1 otherwise.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

from load_requirements import load_requirements, requirement_headers
from moscow_filter import normalize, is_tagged
from settings import load_settings


def check_prerequisites(
    path: Path, settings: dict[str, Any], decision_ref: str | None = None
) -> dict[str, Any]:
    """Report whether the spreadsheet meets the prerequisites.

    Args:
        path: The requirements .xlsx file.
        settings: The full settings mapping.
        decision_ref: The current decision reference, to count tagged drafts.

    Returns:
        A report with ``decision_reference_column`` (header, present),
        ``missing`` (problems; empty when ready), and either ``drafts``
        (total, tagged with the decision) or ``drafts_to_choose_from``.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file or a required sheet or column cannot be read.
    """
    sheet_cfg = settings["spreadsheet"]
    header = sheet_cfg["columns"]["ad_ref"]
    present = header in requirement_headers(path, sheet_cfg)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rows, _ = load_requirements(path, sheet_cfg)
    draft_statuses = {normalize(s) for s in settings["filter"].get("draft_statuses") or []}
    drafts = [r for r in rows if normalize(r.get("status")) in draft_statuses]

    report: dict[str, Any] = {
        "decision_reference_column": {"header": header, "present": present},
        "missing": [],
    }
    if present:
        report["drafts"] = {
            "total": len(drafts),
            "tagged_with_decision": [
                str(r["req_id"]) for r in drafts if is_tagged(r, decision_ref)
            ],
        }
    else:
        report["missing"].append(
            f"The requirements sheet has no '{header}' column, so draft requirements cannot be "
            f"scoped to a decision. Add the column and tag each draft with its decision, or "
            f"choose the drafts for this decision from the list."
        )
        report["drafts_to_choose_from"] = [
            {"req_id": str(r["req_id"]), "description": str(r.get("description") or "")}
            for r in drafts
        ]
    return report


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Check requirements spreadsheet prerequisites.")
    parser.add_argument("spreadsheet", type=Path, help="Requirements .xlsx file.")
    parser.add_argument("--decision", help="Current decision reference.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        report = check_prerequisites(args.spreadsheet, load_settings(args.config), args.decision)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report))
    for problem in report["missing"]:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if report["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
