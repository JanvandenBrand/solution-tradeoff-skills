"""Unit tests for scripts/validate_response.py (ported from test_schema_validator.py)."""

import shutil

import pytest
import yaml

from validate_response import DEFAULT_SCHEMA, ResponseError, main, validate_directory, validate_file

_MINIMAL = {
    "perspective_id": "clinical",
    "concerns": [{"concern": "X", "risk": "Y"}],
    "point_allocations": [{"criterion_id": "REQ001", "points": 10, "rationale": "Z"}],
    "preferred_option": "A",
}


def _write(tmp_path, data, name="response.yaml"):
    path = tmp_path / name
    path.write_text(yaml.dump(data))
    return path


# Schema location


def test_default_schema_is_shipped_asset(skill_dir):
    assert DEFAULT_SCHEMA == skill_dir / "assets" / "tradeoff-output.schema.json"


def test_validate_file_raises_file_not_found_when_schema_missing(tmp_path, fixtures):
    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        validate_file(fixtures / "response_valid.yaml", tmp_path / "missing.json")


# Valid input


def test_validate_file_valid_fixture_passes(fixtures):
    assert validate_file(fixtures / "response_valid.yaml") == []


def test_validate_file_valid_minimal_passes(tmp_path):
    assert validate_file(_write(tmp_path, _MINIMAL)) == []


# Invalid input


def test_validate_file_invalid_fixture_fails(fixtures):
    assert validate_file(fixtures / "response_invalid.yaml")


def test_validate_file_reports_missing_required_fields(tmp_path):
    path = _write(tmp_path, {"perspective_id": "clinical", "preferred_option": "A"})
    messages = [e.message for e in validate_file(path)]
    assert any("concerns" in m for m in messages)
    assert any("point_allocations" in m for m in messages)


def test_validate_file_rejects_negative_points(tmp_path):
    data = {
        **_MINIMAL,
        "point_allocations": [{"criterion_id": "R", "points": -5, "rationale": "Z"}],
    }
    assert any("points" in e.message for e in validate_file(_write(tmp_path, data)))


def test_validate_file_rejects_extra_field(tmp_path):
    assert validate_file(_write(tmp_path, {**_MINIMAL, "unknown_field": "bad"}))


def test_validate_file_returns_error_when_invalid_yaml(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("key: [\nunclosed bracket")
    errors = validate_file(path)
    assert len(errors) == 1
    assert "Invalid YAML" in errors[0].message


def test_validate_file_returns_error_when_not_a_mapping(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text("- a\n- b\n")
    assert len(validate_file(path)) == 1


# Directories


def test_validate_directory_valid(tmp_path, fixtures):
    shutil.copy(fixtures / "response_valid.yaml", tmp_path / "clinical.yaml")
    results = validate_directory(tmp_path)
    assert list(results.values()) == [[]]


def test_validate_directory_mixed(tmp_path, fixtures):
    shutil.copy(fixtures / "response_valid.yaml", tmp_path / "clinical.yaml")
    shutil.copy(fixtures / "response_invalid.yaml", tmp_path / "security.yaml")
    by_name = {p.name: errs for p, errs in validate_directory(tmp_path).items()}
    assert by_name["clinical.yaml"] == []
    assert by_name["security.yaml"]


def test_validate_directory_raises_file_not_found_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="Responses directory not found"):
        validate_directory(tmp_path / "nonexistent")


def test_validate_directory_empty_returns_empty_dict(tmp_path):
    assert validate_directory(tmp_path) == {}


def test_response_error_str_names_file_and_message(tmp_path):
    err = ResponseError(tmp_path / "clinical.yaml", "concerns: required")
    assert str(err) == "clinical.yaml: concerns: required"


# Command line


def test_main_returns_0_when_all_valid(fixtures, capsys):
    assert main([str(fixtures / "response_valid.yaml")]) == 0
    assert "valid" in capsys.readouterr().out


def test_main_returns_1_and_lists_errors_when_invalid(fixtures, capsys):
    assert (
        main([str(fixtures / "response_valid.yaml"), str(fixtures / "response_invalid.yaml")]) == 1
    )
    err = capsys.readouterr().err
    assert "response_invalid.yaml" in err
    assert "response_valid.yaml" not in err


def test_main_validates_directory(tmp_path, fixtures):
    shutil.copy(fixtures / "response_valid.yaml", tmp_path / "clinical.yaml")
    assert main([str(tmp_path)]) == 0


def test_main_returns_1_when_path_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.yaml")]) == 1
    assert "missing.yaml" in capsys.readouterr().err
