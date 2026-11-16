"""Unit tests for scripts/rank.py."""

import json

import pytest
import yaml

from rank import lead, main, rank, ranked_candidates, read_details, read_responses

# Budget 10 over three requirements; ratings on a 0-10 scale.
_POINTS = {
    "security": {"REQ001": 6, "REQ002": 4},
    "financial": {"REQ002": 2, "REQ005": 8},
}
_SCORES = {
    "A": {"REQ001": 8, "REQ002": 7, "REQ005": 9},
    "B": {"REQ001": 5, "REQ002": 8, "REQ005": 4},
    "C": {"REQ001": 9, "REQ002": 9, "REQ005": 2},
}


def _ranking(candidates=("A", "B", "C"), drafted=()):
    return rank(_POINTS, _SCORES, list(candidates), 10, set(drafted))


# ranked_candidates


def test_ranked_candidates_are_the_remaining_ones():
    elimination = {"eliminated": {"C": []}, "at_risk": {}, "remaining": ["A", "B"]}
    assert ranked_candidates(elimination, []) == ["A", "B"]


def test_ranked_candidates_keep_at_risk_candidates_the_user_kept():
    elimination = {"eliminated": {}, "at_risk": {"B": [], "C": []}, "remaining": ["A", "B", "C"]}
    decisions = [
        {"candidate": "B", "decision": "keep"},
        {"candidate": "C", "decision": "eliminate"},
    ]
    assert ranked_candidates(elimination, decisions) == ["A", "B"]


def test_ranked_candidates_need_a_decision_for_every_at_risk_candidate():
    elimination = {"eliminated": {}, "at_risk": {"B": [], "C": []}, "remaining": ["A", "B", "C"]}
    with pytest.raises(ValueError) as exc:
        ranked_candidates(elimination, [{"candidate": "B", "decision": "keep"}])
    assert "'C'" in str(exc.value)


# rank


def test_rank_scores_points_times_rating_over_budget():
    by_candidate = {r["candidate"]: r for r in _ranking()}
    # security: (6*8 + 4*7) / 10 = 7.6; financial: (2*7 + 8*9) / 10 = 8.6
    assert by_candidate["A"]["per_perspective"] == {"security": 7.6, "financial": 8.6}
    assert by_candidate["A"]["overall"] == 8.1


def test_rank_sorts_highest_first():
    # A 8.1, B (6.2 + 4.8) / 2 = 5.5, C (9.0 + 3.4) / 2 = 6.2
    assert [r["candidate"] for r in _ranking()] == ["A", "C", "B"]


def test_rank_breaks_ties_by_identifier():
    points = {"p": {"REQ001": 10}}
    scores = {"B": {"REQ001": 5}, "A": {"REQ001": 5}}
    assert [r["candidate"] for r in rank(points, scores, ["B", "A"], 10, set())] == ["A", "B"]


def test_rank_ranks_only_the_given_candidates():
    assert [r["candidate"] for r in _ranking(candidates=["B", "C"])] == ["C", "B"]


def test_rank_reports_the_share_from_drafted_requirements():
    by_candidate = {r["candidate"]: r for r in _ranking(drafted=["REQ005"])}
    # A: REQ005 gives 8*9 = 72 of 48 + 28 + 14 + 72 = 162
    assert by_candidate["A"]["drafted_share"] == pytest.approx(0.44, abs=0.005)
    assert {r["candidate"]: r["drafted_share"] for r in _ranking()} == {"A": 0, "B": 0, "C": 0}


def test_rank_drafted_share_is_zero_without_any_score():
    scores = {"A": {"REQ001": 0}, "B": {"REQ001": 0}}
    ranking = rank({"p": {"REQ001": 10}}, scores, ["A", "B"], 10, {"REQ001"})
    assert [r["drafted_share"] for r in ranking] == [0, 0]


# lead


def _details(basis="source"):
    return {
        (c, r): {"basis": basis, "source": "Datasheet" if basis == "source" else None}
        for c, per_req in _SCORES.items()
        for r in per_req
    }


def test_lead_reports_gap_and_close_call():
    result = lead(_ranking(), _POINTS, _SCORES, 10, _details(), close_call=0.5)
    assert result["gap"] == 1.9
    assert result["close_call"] is False
    result = lead(_ranking(), _POINTS, _SCORES, 10, _details(), close_call=2.0)
    assert result["close_call"] is True


def test_lead_names_the_requirements_that_decide_the_lead():
    result = lead(_ranking(), _POINTS, _SCORES, 10, _details("judgment"), close_call=0.5)
    # A over C per requirement, mean over perspectives:
    # REQ001 6*(8-9)/10/2 = -0.3; REQ002 (4+2)*(7-9)/10/2 = -0.6; REQ005 8*(9-2)/10/2 = 2.8
    assert [d["requirement_id"] for d in result["decisive"]] == ["REQ005"]
    entry = result["decisive"][0]
    assert entry["contribution"] == 2.8
    assert entry["first"] == {"candidate": "A", "rating": 9, "basis": "judgment", "source": None}
    assert entry["second"]["candidate"] == "C"


def test_lead_is_empty_with_fewer_than_two_candidates():
    result = lead(_ranking(candidates=["A"]), _POINTS, _SCORES, 10, _details(), close_call=0.5)
    assert result == {"gap": None, "close_call": None, "decisive": []}


def test_lead_has_no_decisive_requirement_on_a_tie():
    points = {"p": {"REQ001": 5, "REQ002": 5}}
    scores = {"A": {"REQ001": 8, "REQ002": 2}, "B": {"REQ001": 2, "REQ002": 8}}
    ranking = rank(points, scores, ["A", "B"], 10, set())
    details = {(c, r): {"basis": "source", "source": "S"} for c in scores for r in scores[c]}
    result = lead(ranking, points, scores, 10, details, close_call=0.5)
    assert result["gap"] == 0
    assert result["close_call"] is True
    assert result["decisive"] == []


# read_responses


def _write_response(folder, pid, allocations):
    data = {
        "perspective_id": pid,
        "point_allocations": [
            {"criterion_id": r, "points": p, "rationale": "x"} for r, p in allocations.items()
        ],
    }
    (folder / f"{pid}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def test_read_responses_returns_points_per_perspective(tmp_path):
    for pid, allocations in _POINTS.items():
        _write_response(tmp_path, pid, allocations)
    assert read_responses([tmp_path], ["REQ001", "REQ002", "REQ005"]) == _POINTS


def test_read_responses_rejects_out_of_scope_requirements(tmp_path):
    _write_response(tmp_path, "security", {"REQ001": 6, "REQ900": 4})
    with pytest.raises(ValueError) as exc:
        read_responses([tmp_path], ["REQ001"])
    assert "REQ900" in str(exc.value)


def test_read_responses_needs_response_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_responses([tmp_path], ["REQ001"])
    with pytest.raises(FileNotFoundError):
        read_responses([tmp_path / "missing.yaml"], ["REQ001"])


# read_details


def test_read_details_returns_basis_and_source_per_rating(fixtures):
    details = read_details(fixtures / "ratings_valid.yaml")
    assert details[("A", "REQ001")] == {"basis": "source", "source": "Synthetic vendor datasheet"}


def test_read_details_gives_null_source_when_absent(tmp_path):
    path = tmp_path / "ratings.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "candidates": ["A"],
                "ratings": [
                    {
                        "candidate": "A",
                        "requirement_id": "REQ001",
                        "rating": 5,
                        "rationale": "r",
                        "basis": "judgment",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert read_details(path) == {("A", "REQ001"): {"basis": "judgment", "source": None}}


# main


def _run_folder(tmp_path, fixtures, at_risk=None, decisions=None):
    responses = tmp_path / "responses"
    responses.mkdir()
    for pid, allocations in {
        "security": {"REQ001": 6, "REQ002": 6, "REQ005": 3},
        "financial": {"REQ001": 3, "REQ002": 2, "REQ005": 10},
    }.items():
        _write_response(responses, pid, allocations)
    elimination = {
        "threshold": 6,
        "eliminated": {},
        "at_risk": at_risk or {},
        "remaining": ["A", "B"],
    }
    (tmp_path / "elimination.json").write_text(json.dumps(elimination), encoding="utf-8")
    record = {
        "gather": {"drafted_requirements": [{"id": "REQ005", "origin": "assistant"}]},
        "validate": {"at_risk": decisions or []},
    }
    (tmp_path / "run.yaml").write_text(yaml.safe_dump(record), encoding="utf-8")
    return [
        str(responses),
        "--ratings",
        str(fixtures / "ratings_valid.yaml"),
        "--elimination",
        str(tmp_path / "elimination.json"),
        "--run-record",
        str(tmp_path / "run.yaml"),
        "--requirements",
        str(fixtures / "requirements_filtered.json"),
    ]


def test_main_prints_the_ranking(tmp_path, fixtures, capsys):
    assert main(_run_folder(tmp_path, fixtures)) == 0
    out = json.loads(capsys.readouterr().out)
    # Three requirements give the minimum budget of 15.
    assert out["budget"] == 15
    # A: security (48+42+27)/15 = 7.8, financial (24+14+90)/15 = 8.53;
    # B: security (30+48+12)/15 = 6.0, financial (15+16+40)/15 = 4.73
    assert [r["candidate"] for r in out["ranking"]] == ["A", "B"]
    assert out["ranking"][0]["overall"] == 8.17
    assert out["gap"] == 2.8
    assert out["close_call"] is False
    # No single requirement carries a lead of 2.8: REQ005 gives 2.17 of it.
    assert out["decisive"] == []
    assert out["ranking"][0]["drafted_share"] > 0


def test_main_returns_1_when_an_at_risk_candidate_has_no_decision(tmp_path, fixtures, capsys):
    assert main(_run_folder(tmp_path, fixtures, at_risk={"B": []})) == 1
    assert "'B'" in capsys.readouterr().err


def test_main_leaves_out_at_risk_candidates_the_user_eliminated(tmp_path, fixtures, capsys):
    decisions = [{"candidate": "B", "decision": "eliminate"}]
    assert main(_run_folder(tmp_path, fixtures, at_risk={"B": []}, decisions=decisions)) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["candidate"] for r in out["ranking"]] == ["A"]
    assert out["gap"] is None


def test_main_returns_1_when_a_file_is_missing(tmp_path, fixtures, capsys):
    args = _run_folder(tmp_path, fixtures)
    (tmp_path / "elimination.json").unlink()
    assert main(args) == 1
    assert "error:" in capsys.readouterr().err
