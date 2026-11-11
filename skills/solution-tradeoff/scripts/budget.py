"""Calculate the priority point budget each perspective distributes.

Usage:
    python budget.py --count <requirement count> [--config <settings file>]

Prints ``{"count": <n>, "budget": <points>}`` as JSON.
"""

import argparse
import json
import sys
from pathlib import Path

from settings import load_settings


def point_budget(count: int, multiplier: float, round_to: int, minimum: int) -> int:
    """Return the point budget for ``count`` requirements.

    The budget is ``count * multiplier`` rounded to the nearest multiple of
    ``round_to`` (never zero), and never below ``minimum``.

    Args:
        count: Number of Must and Should requirements in the analysis.
        multiplier: Points per requirement before rounding.
        round_to: Round the budget to a multiple of this value.
        minimum: Lowest budget allowed.

    Returns:
        The point budget.

    Raises:
        ValueError: If ``count`` is negative or ``round_to`` is not positive.
    """
    if count < 0:
        raise ValueError(f"count must be zero or more, got {count}")
    if round_to <= 0:
        raise ValueError(f"round_to must be positive, got {round_to}")
    rounded = int(round(count * multiplier / round_to) * round_to)
    if rounded == 0:
        rounded = round_to
    return max(rounded, minimum)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, required=True, help="Requirement count.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        cfg = load_settings(args.config)["budget"]
        budget = point_budget(args.count, cfg["multiplier"], cfg["round_to"], cfg["minimum"])
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"count": args.count, "budget": budget}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
