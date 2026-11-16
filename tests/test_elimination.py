"""Unit tests for scripts/elimination.py."""

import json

import pytest
import yaml

from elimination import eliminate, main, read_bases

_MUSTS = ["REQ001", "REQ002"]


def _bases(scores, basis="source"):
    return {c: {r: basis for r in per_req} for c, per_req in scores.items()}


def _run(scores, threshold=6, bases=None):
    return eliminate(scores, bases or _bases(scores), _MUSTS, threshold)


def test_eliminate_keeps_candidate_at_threshold():
    assert _run({"A": {"REQ001": 6, "REQ002": 9}}) == ({}, {})


def test_eliminate_flags_candidate_below_threshold_on_a_source():
    eliminated, at_risk = _run({"A": {"REQ001": 5.5, "REQ002": 9}})
    assert eliminated == {"A": [{"requirement_id": "REQ001", "basis": "source"}]}
    assert at_risk == {}


def test_eliminate_lists_every_failing_must_in_order():
    eliminated, _ = _run({"A": {"REQ002": 1, "REQ001": 2}})
    assert [f["requirement_id"] for f in eliminated["A"]] == ["REQ001", "REQ002"]


def test_eliminate_ignores_scores_for_non_must_requirements():
    assert _run({"A": {"REQ001": 7, "REQ002": 7, "REQ900": 0}}) == ({}, {})


def test_eliminate_handles_several_candidates():
    eliminated, _ = _run({"A": {"REQ001": 7, "REQ002": 7}, "B": {"REQ001": 3, "REQ002": 8}})
    assert list(eliminated) == ["B"]


def test_eliminate_threshold_is_a_parameter():
    eliminated, _ = _run({"A": {"REQ001": 7, "REQ002": 7}}, threshold=8)
    assert len(eliminated["A"]) == 2


# Decision 14: only a source that was read eliminates


@pytest.mark.parametrize("basis", ["judgment", "unread_source"])
def test_eliminate_marks_at_risk_when_the_basis_is_not_a_read_source(basis):
    scores = {"A": {"REQ001": 3, "REQ002": 9}}
    eliminated, at_risk = _run(scores, bases=_bases(scores, basis))
    assert eliminated == {}
    assert at_risk == {"A": [{"requirement_id": "REQ001", "basis": basis}]}


def test_eliminate_a_source_failure_wins_over_an_at_risk_one():
    scores = {"A": {"REQ001": 3, "REQ002": 2}}
    bases = {"A": {"REQ001": "judgment", "REQ002": "source"}}
    eliminated, at_risk = _run(scores, bases=bases)
    assert eliminated == {
        "A": [
            {"requirement_id": "REQ001", "basis": "judgment"},
            {"requirement_id": "REQ002", "basis": "source"},
        ]
    }
    assert at_risk == {}


def test_eliminate_raises_value_error_when_must_score_missing():
    scores = {"A": {"REQ001": 7}, "B": {}}
    with pytest.raises(ValueError) as exc:
        _run(scores)
    message = str(exc.value)
    assert "A" in message and "REQ002" in message
    assert "B" in message and "REQ001" in message


def test_eliminate_raises_value_error_when_score_not_a_number():
    with pytest.raises(ValueError, match="REQ001"):
        _run({"A": {"REQ001": "high", "REQ002": 7}})


def test_eliminate_raises_value_error_when_score_is_boolean():
    with pytest.raises(ValueError, match="REQ001"):
        _run({"A": {"REQ001": True, "REQ002": 7}})


def test_read_bases_returns_the_basis_per_requirement_per_candidate(fixtures):
    bases = read_bases(fixtures / "ratings_valid.yaml")
    assert bases["B"]["REQ001"] == "source"


# Command line


def _args(fixtures, *extra, ratings=None):
    return [
        str(ratings or fixtures / "ratings_valid.yaml"),
        "--requirements",
        str(fixtures / "requirements_filtered.json"),
        *extra,
    ]


def test_main_eliminates_on_must_ratings_with_configured_threshold(fixtures, capsys):
    assert main(_args(fixtures)) == 0
    out = json.loads(capsys.readouterr().out)
    # B rates 5 on Must REQ001, from a source; its 4 on Should REQ005 does not count.
    assert out == {
        "threshold": 6,
        "eliminated": {"B": [{"requirement_id": "REQ001", "basis": "source"}]},
        "at_risk": {},
        "remaining": ["A"],
    }


def test_main_lists_at_risk_candidates_as_remaining(tmp_path, fixtures, capsys):
    data = yaml.safe_load((fixtures / "ratings_valid.yaml").read_text())
    for rating in data["ratings"]:
        if rating["candidate"] == "B" and rating["requirement_id"] == "REQ001":
            rating["basis"] = "judgment"
    path = tmp_path / "ratings.yaml"
    path.write_text(yaml.dump(data))
    assert main(_args(fixtures, ratings=path)) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["eliminated"] == {}
    assert out["at_risk"] == {"B": [{"requirement_id": "REQ001", "basis": "judgment"}]}
    assert out["remaining"] == ["A", "B"]


def test_main_threshold_option_overrides_config(fixtures, capsys):
    assert main(_args(fixtures, "--threshold", "4")) == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"threshold": 4, "eliminated": {}, "at_risk": {}, "remaining": ["A", "B"]}


def test_main_returns_1_when_rating_file_invalid(tmp_path, fixtures, capsys):
    data = yaml.safe_load((fixtures / "ratings_valid.yaml").read_text())
    data["ratings"] = data["ratings"][:-1]
    path = tmp_path / "ratings.yaml"
    path.write_text(yaml.dump(data))
    assert main(_args(fixtures, ratings=path)) == 1
    assert "REQ005" in capsys.readouterr().err


def test_main_returns_1_when_requirements_file_missing(tmp_path, fixtures, capsys):
    args = [str(fixtures / "ratings_valid.yaml"), "--requirements", str(tmp_path / "none.json")]
    assert main(args) == 1
    assert "none.json" in capsys.readouterr().err
