"""Unit tests for scripts/validate_run_record.py."""

import copy
import json
from datetime import date

import pytest
import yaml

from validate_run_record import DEFAULT_SCHEMA, main, run_record_errors
from verification_gate import gate


@pytest.fixture
def record(fixtures):
    return yaml.safe_load((fixtures / "run_record_full.yaml").read_text())


@pytest.fixture
def filtered(fixtures):
    return json.loads((fixtures / "requirements_filtered.json").read_text())


def _errors(data, section, filtered=None):
    return run_record_errors(data, section, filtered=filtered)


def test_default_schema_is_shipped_asset(skill_dir):
    assert DEFAULT_SCHEMA == skill_dir / "assets" / "run-record.schema.json"


# Frame: the rules are instructions in references/frame.md (decision 12);
# the script only checks the format.


def test_full_record_format_is_valid(record):
    assert run_record_errors(record, None) == []


def test_frame_format_is_still_checked(record):
    record["frame"]["problem"]["evidence"][0]["kind"] = "rumored"
    assert any("rumored" in e for e in run_record_errors(record, None))


def test_frame_rules_are_not_checked_by_the_script(record):
    record["frame"]["status_quo_asked"] = False
    record["frame"]["validation"]["outcome_named"] = False
    record["frame"]["candidates"][1]["id"] = "A"
    assert run_record_errors(record, "gather") == []


def test_main_has_no_frame_section(fixtures):
    with pytest.raises(SystemExit) as exc:
        main([str(fixtures / "run_record_full.yaml"), "--section", "frame"])
    assert exc.value.code == 2


# Gather


def test_full_record_gather_is_valid(record, filtered):
    assert _errors(record, "gather", filtered) == []


def test_gather_spreadsheet_is_a_file_name_only(record):
    record["gather"]["spreadsheet"] = "/private/folder/requirements.xlsx"
    assert any("file name" in e for e in _errors(record, "gather"))


def test_gather_counts_must_match_the_filter_output(record, filtered):
    record["gather"]["counts"]["must"] = 3
    record["gather"]["counts"]["excluded_drafts"] = 1
    errors = _errors(record, "gather", filtered)
    assert any("counts.must is 3, the filter output has 2" in e for e in errors)
    assert any("counts.excluded_drafts is 1, the filter output has 0" in e for e in errors)


def test_gather_budget_must_match_the_budget_script(record, filtered):
    record["gather"]["budget"] = 30
    errors = _errors(record, "gather", filtered)
    assert any("budget is 30, the point budget for 3 requirements is 15" in e for e in errors)


def test_gather_included_drafts_must_match_the_filter_output(record, filtered):
    record["gather"]["included_drafts"] = ["REQ005"]
    assert any("included_drafts" in e for e in _errors(record, "gather", filtered))


def test_gather_without_filter_output_checks_the_format_only(record):
    record["gather"]["budget"] = 30
    assert _errors(record, "gather") == []


def test_gather_section_missing(record):
    del record["gather"]
    assert any("no gather section" in e for e in _errors(record, "gather"))


def test_unknown_top_level_section_is_rejected(record):
    record["notes"] = "free text"
    assert any("notes" in e for e in run_record_errors(record, None))


# The verification gate still reads the same confirmations


def test_gate_accepts_the_full_record(tmp_path, fixtures):
    library = tmp_path / "library"
    library.mkdir()
    text = (fixtures / "perspective_verified.md").read_text()
    (library / "security.md").write_text(text.replace("id: perspective_verified", "id: security"))
    _, errors = gate(["security"], [library], fixtures / "run_record_full.yaml")
    assert errors == []


def test_minimal_gate_record_is_valid(tmp_path):
    data = {
        "perspective_confirmations": [
            {"id": "security", "confirmed_by": "Test User", "confirmed_at": date(2026, 11, 12)}
        ]
    }
    assert run_record_errors(data, None) == []


# Command line


def test_main_returns_0_for_a_valid_gather(fixtures, capsys):
    args = [str(fixtures / "run_record_full.yaml"), "--section", "gather"]
    args += ["--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 0
    assert "valid" in capsys.readouterr().out


def test_main_returns_1_and_lists_every_error(tmp_path, record, fixtures, capsys):
    broken = copy.deepcopy(record)
    broken["gather"]["counts"]["must"] = 9
    broken["gather"]["budget"] = 99
    path = tmp_path / "run.yaml"
    path.write_text(yaml.safe_dump(broken))
    filtered = str(fixtures / "requirements_filtered.json")
    assert main([str(path), "--section", "gather", "--requirements", filtered]) == 1
    assert capsys.readouterr().err.count("error:") == 2


def test_main_returns_1_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.yaml"), "--section", "gather"]) == 1
    assert "missing.yaml" in capsys.readouterr().err


def test_main_returns_1_when_yaml_invalid(tmp_path, capsys):
    path = tmp_path / "run.yaml"
    path.write_text("frame: [\n")
    assert main([str(path), "--section", "gather"]) == 1
    assert "not valid YAML" in capsys.readouterr().err


# Dates are parsed the same way as by the verification gate

_QUOTED = "must be a date written as YYYY-MM-DD without quotes, got '2026-11-12'"


@pytest.mark.parametrize("section", ["frame", "gather"])
def test_quoted_confirmation_date_is_rejected(record, section):
    record[section]["confirmed_at"] = "2026-11-12"
    assert f"{section}.confirmed_at: confirmed_at {_QUOTED}" in run_record_errors(record, None)


def test_quoted_perspective_confirmation_date_is_rejected(record):
    record["perspective_confirmations"][0]["confirmed_at"] = "2026-11-12"
    expected = f"perspective_confirmations.0.confirmed_at: confirmed_at {_QUOTED}"
    assert expected in run_record_errors(record, None)


# Drafted requirements carry their origin (decision 11)


def test_drafted_requirements_with_origin_are_valid(record):
    record["gather"]["drafted_requirements"] = [
        {"id": "NEW01", "origin": "assistant"},
        {"id": "NEW02", "origin": "user"},
        {"id": "NEW03"},
    ]
    assert run_record_errors(record, None) == []


def test_drafted_requirement_origin_must_be_known(record):
    record["gather"]["drafted_requirements"] = [{"id": "NEW01", "origin": "model"}]
    assert any("model" in e for e in run_record_errors(record, None))
