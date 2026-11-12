"""Check that every perspective response spends exactly the point budget.

The budget comes from the number of in-scope requirements and the budget
settings in ``assets/config.yaml`` (see ``budget.py``).

Usage:
    python check_budget.py <response file or directory> [...]
        --requirements <filtered.json> [--config <settings file>]

``filtered.json`` is the output of ``moscow_filter.py``. Directories are
searched for ``*.yaml`` files. Exit code 0 when every total equals the budget,
1 otherwise; every wrong total is listed on standard error.
"""

import argparse
import sys
from pathlib import Path

import yaml

from budget import point_budget
from settings import load_settings
from validate_rating import read_scope


def budget_errors(path: Path, budget: int) -> list[str]:
    """Return the problems with one response's point total; empty when it equals ``budget``.

    Args:
        path: Perspective response file (YAML).
        budget: Points the response must distribute.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{path.name}: not valid YAML: {exc}"]
    allocations = data.get("point_allocations") if isinstance(data, dict) else None
    if not isinstance(allocations, list):
        return [f"{path.name}: no point_allocations list; run validate_response.py first"]
    total = 0
    for i, item in enumerate(allocations):
        points = item.get("points") if isinstance(item, dict) else None
        if isinstance(points, bool) or not isinstance(points, int):
            return [f"{path.name}: point_allocations.{i}.points is not a whole number: {points!r}"]
        total += points
    if total != budget:
        return [f"{path.name}: point allocations total {total}, budget is {budget}"]
    return []


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Check response point totals against the budget.")
    parser.add_argument("paths", type=Path, nargs="+", help="Response files or directories.")
    parser.add_argument(
        "--requirements", type=Path, required=True, help="Output of moscow_filter.py."
    )
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        cfg = load_settings(args.config)["budget"]
        must_ids, should_ids = read_scope(args.requirements)
        budget = point_budget(
            len(must_ids) + len(should_ids), cfg["multiplier"], cfg["round_to"], cfg["minimum"]
        )
        files: list[Path] = []
        for path in args.paths:
            if path.is_dir():
                found = sorted(path.glob("*.yaml"))
                if not found:
                    raise FileNotFoundError(f"{path} contains no response files (*.yaml)")
                files.extend(found)
            elif path.exists():
                files.append(path)
            else:
                raise FileNotFoundError(f"Response file not found: {path}")
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    errors = [e for f in files for e in budget_errors(f, budget)]
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    if errors:
        return 1
    print(f"{len(files)} response file(s) spend exactly {budget} points.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
