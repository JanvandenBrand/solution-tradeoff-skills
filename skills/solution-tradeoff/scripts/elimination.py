"""Apply the Must elimination threshold to candidate scores.

A candidate that scores below the threshold on any Must requirement is
eliminated. The score scale is not fixed here; the threshold must use the
same scale as the scores.

Usage:
    python elimination.py <scores.json> [--threshold <n>] [--config <settings file>]

``scores.json`` holds ``{"must_ids": [...], "scores": {candidate: {req_id: score}}}``.
Prints ``{"threshold": n, "eliminated": {candidate: [req_ids]}, "remaining": [...]}``.
"""

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path

from settings import load_settings

Scores = dict[str, dict[str, float]]


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
    parser.add_argument("scores", type=Path, help="JSON file with must_ids and scores.")
    parser.add_argument("--threshold", type=float, help="Override the configured threshold.")
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        threshold = args.threshold
        if threshold is None:
            threshold = load_settings(args.config)["elimination"]["must_score_threshold"]
        data = json.loads(args.scores.read_text(encoding="utf-8"))
        result = eliminate(data["scores"], data["must_ids"], threshold)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
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
