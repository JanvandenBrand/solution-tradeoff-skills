"""Apply the Must elimination threshold to the Must ratings.

A Must rating below the threshold eliminates a candidate only when its basis
is ``source``: a source that was read in this run. Below-threshold Must ratings
with basis ``judgment`` or ``unread_source`` mark the candidate at risk, and
the user decides (decision 14). A candidate with any source-based failure is
eliminated and not listed as at risk.

Ratings come from the separate rating pass and are validated first; the
threshold uses the same scale.

Usage:
    python elimination.py <ratings.yaml> --requirements <filtered.json>
        [--threshold <n>] [--config <settings file>]

``filtered.json`` is the output of ``moscow_filter.py``; its Must requirements
are the ones that can eliminate a candidate. Prints::

    {"threshold": n,
     "eliminated": {candidate: [{"requirement_id": id, "basis": basis}]},
     "at_risk": {candidate: [{"requirement_id": id, "basis": basis}]},
     "remaining": [candidates not eliminated, at-risk ones included]}
"""

import argparse
import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path

import yaml

from settings import load_settings
from validate_rating import load_ratings, read_scope

Scores = Mapping[str, Mapping[str, float]]
Bases = Mapping[str, Mapping[str, str]]
Failures = dict[str, list[dict[str, str]]]

ELIMINATING_BASIS = "source"


def read_bases(path: Path) -> dict[str, dict[str, str]]:
    """Return the basis per requirement per candidate from a validated rating file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    bases: dict[str, dict[str, str]] = {c: {} for c in data["candidates"]}
    for r in data["ratings"]:
        bases[r["candidate"]][r["requirement_id"]] = r["basis"]
    return bases


def eliminate(
    scores: Scores, bases: Bases, must_ids: Iterable[str], threshold: float
) -> tuple[Failures, Failures]:
    """Return the eliminated and the at-risk candidates, with their failing Musts.

    Args:
        scores: Score per requirement identifier, per candidate.
        bases: Basis per requirement identifier, per candidate.
        must_ids: Identifiers of the Must requirements, in reporting order.
        threshold: Lowest passing score.

    Returns:
        ``(eliminated, at_risk)``: each maps a candidate to its failing Must
        requirements, as ``{"requirement_id", "basis"}``. A candidate is
        eliminated when any failing rating has basis ``source``; otherwise a
        candidate with failing ratings is at risk. Candidates without failures
        appear in neither.

    Raises:
        ValueError: If any candidate lacks a numeric score for a Must
            requirement. All problems are reported together.
    """
    musts = list(must_ids)
    errors: list[str] = []
    eliminated: Failures = {}
    at_risk: Failures = {}
    for candidate, per_req in scores.items():
        failing: list[dict[str, str]] = []
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
                basis = str(bases.get(candidate, {}).get(req_id, "judgment"))
                failing.append({"requirement_id": req_id, "basis": basis})
        if any(f["basis"] == ELIMINATING_BASIS for f in failing):
            eliminated[candidate] = failing
        elif failing:
            at_risk[candidate] = failing
    if errors:
        raise ValueError("\n".join(errors))
    return eliminated, at_risk


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
        eliminated, at_risk = eliminate(scores, read_bases(args.ratings), must_ids, threshold)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        for line in str(exc).splitlines():
            print(f"error: {line}", file=sys.stderr)
        return 1
    if isinstance(threshold, float) and threshold.is_integer():
        threshold = int(threshold)
    output = {
        "threshold": threshold,
        "eliminated": eliminated,
        "at_risk": at_risk,
        "remaining": [c for c in scores if c not in eliminated],
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
