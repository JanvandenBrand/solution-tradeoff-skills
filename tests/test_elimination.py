"""Unit tests for scripts/elimination.py."""

import json

import pytest
import yaml

from elimination import eliminate, main

_MUSTS = ["REQ001", "REQ002"]


def test_eliminate_keeps_candidate_at_threshold():
    scores = {"A": {"REQ001": 6, "REQ002": 9}}
    assert eliminate(scores, _MUSTS, threshold=6) == {"A": []}


def test_eliminate_flags_candidate_below_threshold():
    scores = {"A": {"REQ001": 5.5, "REQ002": 9}}
    assert eliminate(scores, _MUSTS, threshold=6) == {"A": ["REQ001"]}


def test_eliminate_lists_every_failing_must_in_order():
    scores = {"A": {"REQ002": 1, "REQ001": 2}}
    assert eliminate(scores, _MUSTS, threshold=6) == {"A": ["REQ001", "REQ002"]}


def test_eliminate_ignores_scores_for_non_must_requirements():
    scores = {"A": {"REQ001": 7, "REQ002": 7, "REQ900": 0}}
    assert eliminate(scores, _MUSTS, threshold=6) == {"A": []}


def test_eliminate_handles_several_candidates():
    scores = {"A": {"REQ001": 7, "REQ002": 7}, "B": {"REQ001": 3, "REQ002": 8}}
    assert eliminate(scores, _MUSTS, threshold=6) == {"A": [], "B": ["REQ001"]}


def test_eliminate_threshold_is_a_parameter():
    scores = {"A": {"REQ001": 7, "REQ002": 7}}
    assert eliminate(scores, _MUSTS, threshold=8) == {"A": ["REQ001", "REQ002"]}


def test_eliminate_raises_value_error_when_must_score_missing():
    scores = {"A": {"REQ001": 7}, "B": {}}
    with pytest.raises(ValueError) as exc:
        eliminate(scores, _MUSTS, threshold=6)
    message = str(exc.value)
    assert "A" in message and "REQ002" in message
    assert "B" in message and "REQ001" in message


def test_eliminate_raises_value_error_when_score_not_a_number():
    with pytest.raises(ValueError, match="REQ001"):
        eliminate({"A": {"REQ001": "high", "REQ002": 7}}, _MUSTS, threshold=6)


def test_eliminate_raises_value_error_when_score_is_boolean():
    with pytest.raises(ValueError, match="REQ001"):
        eliminate({"A": {"REQ001": True, "REQ002": 7}}, _MUSTS, threshold=6)


def _args(fixtures, *extra):
    return [
        str(fixtures / "ratings_valid.yaml"),
        "--requirements",
        str(fixtures / "requirements_filtered.json"),
        *extra,
    ]


def test_main_eliminates_on_must_ratings_with_configured_threshold(fixtures, capsys):
    assert main(_args(fixtures)) == 0
    out = json.loads(capsys.readouterr().out)
    # B rates 5 on Must REQ001; its 4 on Should REQ005 does not count.
    assert out == {"threshold": 6, "eliminated": {"B": ["REQ001"]}, "remaining": ["A"]}


def test_main_threshold_option_overrides_config(fixtures, capsys):
    assert main(_args(fixtures, "--threshold", "4")) == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"threshold": 4, "eliminated": {}, "remaining": ["A", "B"]}


def test_main_returns_1_when_rating_file_invalid(tmp_path, fixtures, capsys):
    data = yaml.safe_load((fixtures / "ratings_valid.yaml").read_text())
    data["ratings"] = data["ratings"][:-1]
    path = tmp_path / "ratings.yaml"
    path.write_text(yaml.dump(data))
    args = [str(path), "--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 1
    assert "REQ005" in capsys.readouterr().err


def test_main_returns_1_when_requirements_file_missing(tmp_path, fixtures, capsys):
    args = [str(fixtures / "ratings_valid.yaml"), "--requirements", str(tmp_path / "none.json")]
    assert main(args) == 1
    assert "none.json" in capsys.readouterr().err
