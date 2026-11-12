"""Apply the Must elimination threshold to the Must ratings.

A candidate that rates below the threshold on any Must requirement is
eliminated. Ratings come from the separate rating pass and are validated
first; the threshold uses the same scale.

Usage:
    python elimination.py <ratings.yaml> --requirements <filtered.json>
        [--threshold <n>] [--config <settings file>]

``filtered.json`` is the output of ``moscow_filter.py``; its Must requirements
are the ones that can eliminate a candidate. Prints
``{"threshold": n, "eliminated": {candidate: [req_ids]}, "remaining": [...]}``.
"""

import argparse
import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path

from settings import load_settings
from validate_rating import load_ratings, read_scope

Scores = Mapping[str, Mapping[str, float]]


def eliminate(scores: Scores, must_ids: Iterable[str], threshold: float) -> dict[str, list[str]]:
    """Return, per candidate, the Must requirements it scores below ``threshold`` on.

    An empty list means the candidate survives.

    Args:
        scores: Score per requirement identifier, per candidate.
        must_ids: Identifiers of the Must requirements, in reporting order.
        threshold: Lowest passing score.

    Returns:
        Mapping of candidate to failing Must identifiers.

    Raises:
        ValueError: If any candidate lacks a numeric score for a Must
            requirement. All problems are reported together.
    """
    musts = list(must_ids)
    errors: list[str] = []
    result: dict[str, list[str]] = {}
    for candidate, per_req in scores.items():
        failing: list[str] = []
        for req_id in musts:
            if req_id not in per_req:
                errors.append(f"candidate '{candidate}' has no score for Must '{req_id}'")
                continue
            score = per_req[req_id]
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                errors.append(
                    f"candidate '{candidate}' score for Must '{req_id}' is not a number: {score!r}"
                )
                continue
            if score < threshold:
                failing.append(req_id)
        result[candidate] = failing
    if errors:
        raise ValueError("\n".join(errors))
    return result


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Apply the Must elimination threshold.")
    parser.add_argument("ratings", type=Path, help="Rating file (YAML).")
    parser.add_argument(
        "--requirements", type=Path, required=True, help="Output of moscow_filter.py."
    )
    parser.add_argument("--threshold", type=float, help="Override the configured threshold.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        settings = load_settings(args.config)
        threshold = args.threshold
        if threshold is None:
            threshold = settings["elimination"]["must_score_threshold"]
        must_ids, should_ids = read_scope(args.requirements)
        scale = settings["rating"]
        scores = load_ratings(
            args.ratings, must_ids, should_ids, scale["minimum"], scale["maximum"]
        )
        result = eliminate(scores, must_ids, threshold)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        for line in str(exc).splitlines():
            print(f"error: {line}", file=sys.stderr)
        return 1
    if isinstance(threshold, float) and threshold.is_integer():
        threshold = int(threshold)
    output = {
        "threshold": threshold,
        "eliminated": {c: reqs for c, reqs in result.items() if reqs},
        "remaining": [c for c, reqs in result.items() if not reqs],
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
