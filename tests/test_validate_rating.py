"""Unit tests for scripts/validate_rating.py."""

import pytest
import yaml

from validate_rating import (
    DEFAULT_SCHEMA,
    load_ratings,
    main,
    rating_errors,
    read_scope,
)

_SCOPE = (["REQ001", "REQ002"], ["REQ005"])


def _data():
    return yaml.safe_load(
        """
candidates: [A, B]
ratings:
  - {candidate: A, requirement_id: REQ001, rating: 8, rationale: r, basis: source}
  - {candidate: A, requirement_id: REQ002, rating: 7, rationale: r, basis: source}
  - {candidate: A, requirement_id: REQ005, rating: 9, rationale: r, basis: source}
  - {candidate: B, requirement_id: REQ001, rating: 5, rationale: r, basis: source}
  - {candidate: B, requirement_id: REQ002, rating: 8, rationale: r, basis: source}
  - {candidate: B, requirement_id: REQ005, rating: 4, rationale: r, basis: source}
"""
    )


def _errors(data):
    return rating_errors(data, *_SCOPE, minimum=0, maximum=10)


def test_default_schema_is_shipped_asset(skill_dir):
    assert DEFAULT_SCHEMA == skill_dir / "assets" / "rating.schema.json"


def test_read_scope_returns_must_and_should_ids(fixtures):
    assert read_scope(fixtures / "requirements_filtered.json") == _SCOPE


def test_rating_errors_accepts_complete_ratings():
    assert _errors(_data()) == []


# Schema


def test_rating_errors_rejects_missing_rationale():
    data = _data()
    del data["ratings"][0]["rationale"]
    assert any("rationale" in e for e in _errors(data))


def test_rating_errors_rejects_missing_basis():
    data = _data()
    del data["ratings"][0]["basis"]
    assert any("basis" in e for e in _errors(data))


@pytest.mark.parametrize("basis", ["source", "judgment", "unread_source"])
def test_rating_errors_accepts_each_basis(basis):
    data = _data()
    data["ratings"][0]["basis"] = basis
    assert _errors(data) == []


def test_rating_errors_accepts_a_source_title():
    data = _data()
    data["ratings"][0]["source"] = "Vendor security whitepaper"
    assert _errors(data) == []


def test_rating_errors_rejects_an_empty_source():
    data = _data()
    data["ratings"][0]["source"] = ""
    assert any("source" in e for e in _errors(data))


def test_rating_errors_rejects_unknown_basis():
    data = _data()
    data["ratings"][0]["basis"] = "guess"
    assert any("guess" in e for e in _errors(data))


def test_rating_errors_rejects_preference_fields():
    data = _data()
    data["preferred_option"] = "A"
    data["ratings"][0]["points"] = 10
    errors = _errors(data)
    assert any("preferred_option" in e for e in errors)
    assert any("points" in e for e in errors)


def test_rating_errors_rejects_non_integer_rating():
    data = _data()
    data["ratings"][0]["rating"] = 6.5
    assert any("integer" in e for e in _errors(data))


def test_rating_errors_rejects_single_candidate():
    data = _data()
    data["candidates"] = ["A"]
    assert _errors(data)


def test_rating_errors_rejects_non_mapping():
    assert _errors(["a"])


# Rules from settings and scope


def test_rating_errors_rejects_rating_out_of_range():
    data = _data()
    data["ratings"][0]["rating"] = 11
    data["ratings"][1]["rating"] = -1
    errors = _errors(data)
    assert sum("between 0 and 10" in e for e in errors) == 2


def test_rating_errors_range_comes_from_arguments():
    assert rating_errors(_data(), *_SCOPE, minimum=5, maximum=10)


def test_rating_errors_rejects_unlisted_candidate():
    data = _data()
    data["ratings"][0]["candidate"] = "C"
    assert any("'C'" in e and "not listed" in e for e in _errors(data))


def test_rating_errors_rejects_out_of_scope_requirement():
    data = _data()
    data["ratings"][0]["requirement_id"] = "REQ999"
    assert any("REQ999" in e and "not in scope" in e for e in _errors(data))


def test_rating_errors_rejects_duplicate_pair():
    data = _data()
    data["ratings"].append(dict(data["ratings"][0]))
    assert any("more than once" in e for e in _errors(data))


def test_rating_errors_reports_every_missing_pair():
    data = _data()
    data["ratings"] = data["ratings"][:4]
    errors = _errors(data)
    assert any("'B'" in e and "REQ002" in e for e in errors)
    assert any("'B'" in e and "REQ005" in e for e in errors)


# Loading for other scripts


def test_load_ratings_returns_scores_per_candidate(fixtures):
    scores = load_ratings(fixtures / "ratings_valid.yaml", *_SCOPE, minimum=0, maximum=10)
    assert scores == {
        "A": {"REQ001": 8, "REQ002": 7, "REQ005": 9},
        "B": {"REQ001": 5, "REQ002": 8, "REQ005": 4},
    }


def test_load_ratings_raises_value_error_with_every_problem(tmp_path):
    data = _data()
    data["ratings"] = data["ratings"][:4]
    path = tmp_path / "ratings.yaml"
    path.write_text(yaml.dump(data))
    with pytest.raises(ValueError) as exc:
        load_ratings(path, *_SCOPE, minimum=0, maximum=10)
    assert "REQ002" in str(exc.value) and "REQ005" in str(exc.value)


def test_load_ratings_raises_value_error_when_invalid_yaml(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("candidates: [\n")
    with pytest.raises(ValueError, match="not valid YAML"):
        load_ratings(path, *_SCOPE, minimum=0, maximum=10)


# Command line


def test_main_returns_0_when_valid(fixtures, capsys):
    args = [str(fixtures / "ratings_valid.yaml")]
    args += ["--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 0
    assert "valid" in capsys.readouterr().out


def test_main_returns_1_and_lists_errors(tmp_path, fixtures, capsys):
    data = _data()
    data["ratings"] = data["ratings"][:5]
    path = tmp_path / "ratings.yaml"
    path.write_text(yaml.dump(data))
    assert main([str(path), "--requirements", str(fixtures / "requirements_filtered.json")]) == 1
    assert "REQ005" in capsys.readouterr().err


def test_main_returns_1_when_file_missing(tmp_path, fixtures, capsys):
    args = [str(tmp_path / "missing.yaml")]
    args += ["--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 1
    assert "missing.yaml" in capsys.readouterr().err
