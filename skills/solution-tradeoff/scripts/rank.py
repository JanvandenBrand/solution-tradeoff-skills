"""Rank the candidates from the perspectives' points and the separate ratings.

For each candidate and perspective, the score is the sum over the in-scope
requirements of points x rating, divided by the point budget, so it uses the
rating scale. The overall score is the mean across perspectives.

The candidates ranked are the ones ``elimination.py`` left remaining, minus the
at-risk candidates the user chose to eliminate (``validate.at_risk`` in the run
record). Every at-risk candidate needs a decision first.

Per candidate, ``drafted_share`` is the part of its overall score that comes
from requirements the assistant drafted (``gather.drafted_requirements`` with
``origin: assistant``; decision 11). ``gap`` is the first candidate's overall
score minus the second's; below ``compile.close_call`` in the settings, the
result is a close call. ``decisive`` lists the requirements that each carry at
least the whole lead: without any one of them, the lead would vanish.

Usage:
    python rank.py <response file or directory> [...] --ratings <ratings.yaml>
        --elimination <elimination.json> --run-record <run.yaml>
        --requirements <filtered.json> [--config <settings file>]

Run it after the Validate step, on files that passed every check. Prints::

    {"budget": n,
     "ranking": [{"candidate", "overall", "per_perspective": {id: score},
                  "drafted_share"}],
     "gap": n or null, "close_call": true, false or null,
     "decisive": [{"requirement_id", "contribution",
                   "first": {"candidate", "rating", "basis", "source"},
                   "second": {...}}]}
"""

import argparse
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from budget import point_budget
from settings import load_settings
from validate_rating import load_ratings, read_scope

Points = Mapping[str, Mapping[str, int]]
Scores = Mapping[str, Mapping[str, int]]
Details = Mapping[tuple[str, str], Mapping[str, Any]]

DECIMALS = 2


def read_responses(paths: Iterable[Path], scope: Sequence[str]) -> dict[str, dict[str, int]]:
    """Return the points per requirement per perspective from response files.

    Args:
        paths: Response files, or directories searched for ``*.yaml`` files.
        scope: In-scope requirement identifiers.

    Raises:
        FileNotFoundError: If a path does not exist or a directory has no responses.
        ValueError: If a response gives points to a requirement out of scope;
            every such problem is reported together.
    """
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            found = sorted(path.glob("*.yaml"))
            if not found:
                raise FileNotFoundError(f"{path} contains no response files (*.yaml)")
            files.extend(found)
        elif path.exists():
            files.append(path)
        else:
            raise FileNotFoundError(f"Response file not found: {path}")
    points: dict[str, dict[str, int]] = {}
    errors: list[str] = []
    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        allocation: dict[str, int] = {}
        for item in data["point_allocations"]:
            req_id = str(item["criterion_id"])
            if req_id not in scope:
                errors.append(f"{file.name}: points for '{req_id}', which is not in scope")
            allocation[req_id] = allocation.get(req_id, 0) + int(item["points"])
        points[str(data["perspective_id"])] = allocation
    if errors:
        raise ValueError("\n".join(errors))
    return points


def read_details(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Return the basis and source of each rating, by candidate and requirement."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        (r["candidate"], r["requirement_id"]): {"basis": r["basis"], "source": r.get("source")}
        for r in data["ratings"]
    }


def ranked_candidates(elimination: Mapping[str, Any], decisions: Iterable[Any]) -> list[str]:
    """Return the candidates to rank: the remaining ones the user did not eliminate.

    Raises:
        ValueError: If an at-risk candidate has no decision in the run record.
    """
    decided = {str(d["candidate"]): d["decision"] for d in decisions}
    missing = [c for c in elimination["at_risk"] if c not in decided]
    if missing:
        raise ValueError(
            "\n".join(
                f"at-risk candidate '{c}' has no decision in validate.at_risk" for c in missing
            )
        )
    return [
        c
        for c in elimination["remaining"]
        if not (c in elimination["at_risk"] and decided[c] == "eliminate")
    ]


def _score(allocation: Mapping[str, int], ratings: Mapping[str, int], budget: int) -> float:
    return sum(p * ratings[r] for r, p in allocation.items()) / budget


def rank(
    points: Points,
    scores: Scores,
    candidates: Sequence[str],
    budget: int,
    drafted: set[str],
) -> list[dict[str, Any]]:
    """Return the candidates ranked by overall score, highest first.

    Args:
        points: Points per requirement, per perspective.
        scores: Rating per requirement, per candidate.
        candidates: The candidates to rank.
        budget: The point budget each perspective spent.
        drafted: Identifiers of the requirements the assistant drafted.

    Returns:
        One entry per candidate: ``candidate``, ``overall``, ``per_perspective``
        and ``drafted_share``, rounded. Ties are ordered by identifier.
    """
    rows: list[tuple[float, str, dict[str, float], float]] = []
    for candidate in candidates:
        ratings = scores[candidate]
        per_perspective = {pid: _score(a, ratings, budget) for pid, a in points.items()}
        total = sum(p * ratings[r] for a in points.values() for r, p in a.items())
        from_drafted = sum(
            p * ratings[r] for a in points.values() for r, p in a.items() if r in drafted
        )
        overall = sum(per_perspective.values()) / len(per_perspective)
        share = from_drafted / total if total else 0.0
        rows.append((overall, candidate, per_perspective, share))
    rows.sort(key=lambda row: (-row[0], row[1]))
    return [
        {
            "candidate": candidate,
            "overall": round(overall, DECIMALS),
            "per_perspective": {k: round(v, DECIMALS) for k, v in per_perspective.items()},
            "drafted_share": round(share, DECIMALS),
        }
        for overall, candidate, per_perspective, share in rows
    ]


def lead(
    ranking: Sequence[Mapping[str, Any]],
    points: Points,
    scores: Scores,
    budget: int,
    details: Details,
    close_call: float,
) -> dict[str, Any]:
    """Return the gap between the first two candidates and what decides it.

    Args:
        ranking: Output of :func:`rank`.
        points: Points per requirement, per perspective.
        scores: Rating per requirement, per candidate.
        budget: The point budget each perspective spent.
        details: Basis and source per ``(candidate, requirement)``.
        close_call: A gap below this is a close call.

    Returns:
        ``gap``, ``close_call`` and ``decisive``. With fewer than two
        candidates, ``gap`` and ``close_call`` are null and ``decisive`` is empty.
    """
    if len(ranking) < 2:
        return {"gap": None, "close_call": None, "decisive": []}
    first, second = ranking[0]["candidate"], ranking[1]["candidate"]
    overall = {
        c: sum(_score(a, scores[c], budget) for a in points.values()) / len(points)
        for c in (first, second)
    }
    gap = overall[first] - overall[second]
    requirements = sorted({r for a in points.values() for r in a})
    decisive = []
    for req_id in requirements:
        difference = scores[first][req_id] - scores[second][req_id]
        contribution = (
            sum(a.get(req_id, 0) * difference for a in points.values()) / budget / len(points)
        )
        if gap > 0 and contribution >= gap:
            decisive.append(
                {
                    "requirement_id": req_id,
                    "contribution": round(contribution, DECIMALS),
                    "first": _side(first, req_id, scores, details),
                    "second": _side(second, req_id, scores, details),
                }
            )
    return {
        "gap": round(gap, DECIMALS),
        "close_call": bool(round(gap, DECIMALS) < close_call),
        "decisive": decisive,
    }


def _side(candidate: str, req_id: str, scores: Scores, details: Details) -> dict[str, Any]:
    detail = details.get((candidate, req_id), {})
    return {
        "candidate": candidate,
        "rating": scores[candidate][req_id],
        "basis": detail.get("basis"),
        "source": detail.get("source"),
    }


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Rank the candidates.")
    parser.add_argument("paths", type=Path, nargs="+", help="Response files or directories.")
    parser.add_argument("--ratings", type=Path, required=True, help="Rating file (YAML).")
    parser.add_argument("--elimination", type=Path, required=True, help="Output of elimination.py.")
    parser.add_argument("--run-record", type=Path, required=True, help="Run record (YAML).")
    parser.add_argument(
        "--requirements", type=Path, required=True, help="Output of moscow_filter.py."
    )
    parser.add_argument("--config", type=Path, help="Settings file (default: assets/config.yaml).")
    args = parser.parse_args(argv)
    try:
        settings = load_settings(args.config)
        must_ids, should_ids = read_scope(args.requirements)
        scope = [*must_ids, *should_ids]
        cfg = settings["budget"]
        budget = point_budget(len(scope), cfg["multiplier"], cfg["round_to"], cfg["minimum"])
        scale = settings["rating"]
        scores = load_ratings(
            args.ratings, must_ids, should_ids, scale["minimum"], scale["maximum"]
        )
        points = read_responses(args.paths, scope)
        elimination = json.loads(args.elimination.read_text(encoding="utf-8"))
        record = yaml.safe_load(args.run_record.read_text(encoding="utf-8")) or {}
        decisions = (record.get("validate") or {}).get("at_risk") or []
        drafted = {
            str(d["id"])
            for d in (record.get("gather") or {}).get("drafted_requirements") or []
            if d.get("origin") == "assistant"
        }
        candidates = ranked_candidates(elimination, decisions)
        ranking = rank(points, scores, candidates, budget, drafted)
        result = lead(
            ranking,
            points,
            scores,
            budget,
            read_details(args.ratings),
            settings["compile"]["close_call"],
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        for line in str(exc).splitlines():
            print(f"error: {line}", file=sys.stderr)
        return 1
    print(json.dumps({"budget": budget, "ranking": ranking, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
