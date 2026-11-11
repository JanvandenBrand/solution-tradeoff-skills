"""Filter requirements by MoSCoW level, status, domain and plateau.

Usage:
    python moscow_filter.py <rows.json> [--moscow Must --moscow Should]
        [--domain <name> ...] [--plateau <n>] [--config <settings file>]

``rows.json`` is either a list of requirement rows or the output of
``load_requirements.py`` (an object with a ``requirements`` list). Prints
``{"must": [...], "should": [...]}`` as JSON.
"""

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from settings import load_settings

Row = dict[str, Any]


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _above_plateau(row: Row, plateau: int | None) -> bool:
    if plateau is None:
        return False
    value = row.get("plateau")
    if value is None or value == "":
        return False
    try:
        return int(value) > plateau
    except (ValueError, TypeError):
        return False


def filter_requirements(
    rows: list[Row],
    moscow: Iterable[str],
    excluded_statuses: Iterable[str],
    domains: Iterable[str] = (),
    plateau: int | None = None,
) -> tuple[list[Row], list[Row]]:
    """Split requirement rows into Must and Should lists.

    Args:
        rows: Requirement rows keyed by logical column names.
        moscow: MoSCoW levels to keep (case-insensitive).
        excluded_statuses: Statuses that remove a row (case-insensitive).
        domains: Domains to keep; empty keeps every domain.
        plateau: If set, drop rows whose plateau is higher than this. Rows
            without a numeric plateau are kept.

    Returns:
        ``(must_rows, should_rows)``, each sorted by ``req_id``.
    """
    keep_moscow = {_norm(m) for m in moscow}
    keep_domains = {_norm(d) for d in domains}
    excluded = {_norm(s) for s in excluded_statuses}

    kept = [
        row
        for row in rows
        if _norm(row.get("status")) not in excluded
        and (not keep_domains or _norm(row.get("domain")) in keep_domains)
        and _norm(row.get("moscow")) in keep_moscow
        and not _above_plateau(row, plateau)
    ]
    kept.sort(key=lambda r: str(r.get("req_id") or ""))
    must = [r for r in kept if _norm(r.get("moscow")) == "must"]
    should = [r for r in kept if _norm(r.get("moscow")) == "should"]
    return must, should


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Filter requirements by MoSCoW level.")
    parser.add_argument("rows", type=Path, help="JSON file with requirement rows.")
    parser.add_argument("--moscow", action="append", help="MoSCoW level to keep (repeatable).")
    parser.add_argument("--domain", action="append", default=[], help="Domain to keep.")
    parser.add_argument("--plateau", type=int, help="Highest plateau to keep.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        cfg = load_settings(args.config)["filter"]
        data = json.loads(args.rows.read_text(encoding="utf-8"))
        rows = data["requirements"] if isinstance(data, dict) else data
        must, should = filter_requirements(
            rows,
            moscow=args.moscow or cfg["default_moscow"],
            excluded_statuses=cfg["excluded_statuses"],
            domains=args.domain,
            plateau=args.plateau,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"must": must, "should": should}, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
