"""Filter requirements by MoSCoW level, status, domain, plateau and decision.

Usage:
    python moscow_filter.py <rows.json> [--moscow Must --moscow Should]
        [--domain <name> ...] [--plateau <n>] [--decision <reference>]
        [--config <settings file>]

``rows.json`` is either a list of requirement rows or the output of
``load_requirements.py`` (an object with a ``requirements`` list). Prints
``{"must": [...], "should": [...], "excluded_drafts": {"count": n, "req_ids": [...]}}``
as JSON.

Draft requirements are kept only when their ``ad_ref`` cell names the current
decision (``--decision``). Drafts that would otherwise be in scope but are not
tagged with the decision are reported as excluded drafts.
"""

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, NamedTuple

from settings import load_settings

Row = dict[str, Any]
_REF_SEPARATORS = re.compile(r"[,;\s]+")


class FilterResult(NamedTuple):
    """Rows kept by the filter, and the drafts left out for lack of a decision tag."""

    must: list[Row]
    should: list[Row]
    excluded_drafts: list[str]


def normalize(value: Any) -> str:
    """Return ``value`` as a trimmed, lowercase string (empty for None)."""
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


def is_tagged(row: Row, decision_ref: str | None) -> bool:
    """Return whether the row's ``ad_ref`` cell names ``decision_ref``."""
    if not decision_ref:
        return False
    refs = {normalize(r) for r in _REF_SEPARATORS.split(str(row.get("ad_ref") or "")) if r}
    return normalize(decision_ref) in refs


def filter_requirements(
    rows: list[Row],
    moscow: Iterable[str],
    excluded_statuses: Iterable[str],
    domains: Iterable[str] = (),
    plateau: int | None = None,
    draft_statuses: Iterable[str] = (),
    decision_ref: str | None = None,
) -> FilterResult:
    """Split requirement rows into Must and Should lists.

    Args:
        rows: Requirement rows keyed by logical column names.
        moscow: MoSCoW levels to keep (case-insensitive).
        excluded_statuses: Statuses that remove a row (case-insensitive).
        domains: Domains to keep; empty keeps every domain.
        plateau: If set, drop rows whose plateau is higher than this. Rows
            without a numeric plateau are kept.
        draft_statuses: Statuses that mark a draft (case-insensitive).
        decision_ref: The current decision reference. A draft is kept only
            when its ``ad_ref`` cell contains this reference; without it, every
            draft is excluded.

    Returns:
        The Must and Should rows, each sorted by ``req_id``, and the sorted
        identifiers of drafts that passed every other filter but were not
        tagged with ``decision_ref``.

    Raises:
        ValueError: If a requested domain does not occur in ``rows``. The
            message lists the domains present.
    """
    keep_moscow = {normalize(m) for m in moscow}
    keep_domains = {normalize(d) for d in domains}
    present = sorted({str(r.get("domain")).strip() for r in rows if normalize(r.get("domain"))})
    unknown = [d for d in domains if normalize(d) not in {normalize(p) for p in present}]
    if unknown:
        raise ValueError(
            f"Unknown domain(s): {', '.join(unknown)}. "
            f"Domains present in the requirements: {', '.join(present) or 'none'}."
        )
    excluded = {normalize(s) for s in excluded_statuses}
    drafts = {normalize(s) for s in draft_statuses}

    in_scope = [
        row
        for row in rows
        if normalize(row.get("status")) not in excluded
        and (not keep_domains or normalize(row.get("domain")) in keep_domains)
        and normalize(row.get("moscow")) in keep_moscow
        and not _above_plateau(row, plateau)
    ]
    kept: list[Row] = []
    excluded_drafts: list[str] = []
    for row in in_scope:
        if normalize(row.get("status")) in drafts and not is_tagged(row, decision_ref):
            excluded_drafts.append(str(row.get("req_id") or ""))
        else:
            kept.append(row)
    kept.sort(key=lambda r: str(r.get("req_id") or ""))
    must = [r for r in kept if normalize(r.get("moscow")) == "must"]
    should = [r for r in kept if normalize(r.get("moscow")) == "should"]
    return FilterResult(must, should, sorted(excluded_drafts))


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Filter requirements by MoSCoW level.")
    parser.add_argument("rows", type=Path, help="JSON file with requirement rows.")
    parser.add_argument("--moscow", action="append", help="MoSCoW level to keep (repeatable).")
    parser.add_argument("--domain", action="append", default=[], help="Domain to keep.")
    parser.add_argument("--plateau", type=int, help="Highest plateau to keep.")
    parser.add_argument(
        "--decision", help="Current decision reference; keeps drafts tagged with it."
    )
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        cfg = load_settings(args.config)["filter"]
        data = json.loads(args.rows.read_text(encoding="utf-8"))
        rows = data["requirements"] if isinstance(data, dict) else data
        result = filter_requirements(
            rows,
            moscow=args.moscow or cfg["default_moscow"],
            excluded_statuses=cfg["excluded_statuses"],
            domains=args.domain,
            plateau=args.plateau,
            draft_statuses=cfg.get("draft_statuses") or [],
            decision_ref=args.decision,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    output = {
        "must": result.must,
        "should": result.should,
        "excluded_drafts": {
            "count": len(result.excluded_drafts),
            "req_ids": result.excluded_drafts,
        },
    }
    print(json.dumps(output, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
