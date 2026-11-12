"""Unit tests for scripts/validate_run_record.py."""

import copy
import json

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


# Frame


def test_full_record_frame_is_valid(record):
    assert _errors(record, "frame") == []


def test_frame_section_missing(record):
    del record["frame"]
    assert any("no frame section" in e for e in _errors(record, "frame"))


def test_frame_needs_a_decision_id(record):
    record["frame"]["decision_id"] = ""
    assert any("decision_id" in e for e in _errors(record, "frame"))


def test_frame_needs_at_least_two_candidates(record):
    record["frame"]["candidates"] = record["frame"]["candidates"][:1]
    assert any("candidates" in e for e in _errors(record, "frame"))


def test_frame_candidate_ids_are_unique(record):
    record["frame"]["candidates"][1]["id"] = "a"
    assert any("candidate id 'a' is used more than once" in e for e in _errors(record, "frame"))


def test_frame_candidate_description_is_one_line(record):
    record["frame"]["candidates"][0]["description"] = "First line.\nSecond line."
    assert any("one line" in e for e in _errors(record, "frame"))


def test_frame_status_quo_question_must_be_asked(record):
    record["frame"]["status_quo_asked"] = False
    assert any("status quo" in e for e in _errors(record, "frame"))


def test_frame_without_evidence_must_be_labeled_hypothesis(record):
    record["frame"]["problem"]["evidence"] = []
    record["frame"]["validation"]["evidence_present"] = False
    assert any("hypothesis" in e for e in _errors(record, "frame"))
    record["frame"]["problem"]["label"] = "hypothesis"
    assert _errors(record, "frame") == []


def test_frame_with_evidence_cannot_be_labeled_hypothesis(record):
    record["frame"]["problem"]["label"] = "hypothesis"
    assert any("evidenced" in e for e in _errors(record, "frame"))


def test_frame_evidence_present_must_match_the_evidence(record):
    record["frame"]["validation"]["evidence_present"] = False
    assert any("evidence_present" in e for e in _errors(record, "frame"))


def test_frame_problem_must_not_name_a_solution(record):
    record["frame"]["validation"]["solution_free"] = False
    assert any("names a solution" in e for e in _errors(record, "frame"))


def test_frame_outcome_must_be_named(record):
    record["frame"]["validation"]["outcome_named"] = False
    assert any("outcome" in e for e in _errors(record, "frame"))


def test_frame_needs_a_confirmation(record):
    del record["frame"]["confirmed_by"]
    assert any("confirmed_by" in e for e in _errors(record, "frame"))


def test_frame_confirmed_at_must_be_a_date(record):
    record["frame"]["confirmed_at"] = "soon"
    assert any("confirmed_at" in e for e in _errors(record, "frame"))


def test_frame_rejects_unknown_evidence_kind(record):
    record["frame"]["problem"]["evidence"][0]["kind"] = "rumored"
    assert any("rumored" in e for e in _errors(record, "frame"))


def test_errors_are_collected_together(record):
    record["frame"]["status_quo_asked"] = False
    record["frame"]["validation"]["solution_free"] = False
    record["frame"]["candidates"][1]["id"] = "A"
    assert len(_errors(record, "frame")) == 3


# Gather


def test_full_record_gather_is_valid(record, filtered):
    assert _errors(record, "gather", filtered) == []


def test_gather_needs_a_frame(record):
    del record["frame"]
    assert any("frame" in e for e in _errors(record, "gather"))


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
    assert any("notes" in e for e in _errors(record, "frame"))


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
            {"id": "security", "confirmed_by": "Test User", "confirmed_at": "2026-11-12"}
        ]
    }
    assert run_record_errors(data, None) == []


# Command line


def test_main_returns_0_for_a_valid_gather(fixtures, capsys):
    args = [str(fixtures / "run_record_full.yaml"), "--section", "gather"]
    args += ["--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 0
    assert "valid" in capsys.readouterr().out


def test_main_returns_1_and_lists_every_error(tmp_path, record, capsys):
    broken = copy.deepcopy(record)
    broken["frame"]["status_quo_asked"] = False
    broken["frame"]["validation"]["outcome_named"] = False
    path = tmp_path / "run.yaml"
    path.write_text(yaml.safe_dump(broken))
    assert main([str(path), "--section", "frame"]) == 1
    assert capsys.readouterr().err.count("error:") == 2


def test_main_returns_1_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.yaml"), "--section", "frame"]) == 1
    assert "missing.yaml" in capsys.readouterr().err


def test_main_returns_1_when_yaml_invalid(tmp_path, capsys):
    path = tmp_path / "run.yaml"
    path.write_text("frame: [\n")
    assert main([str(path), "--section", "frame"]) == 1
    assert "not valid YAML" in capsys.readouterr().err
