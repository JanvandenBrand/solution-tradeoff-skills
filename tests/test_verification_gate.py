"""Unit tests for scripts/verification_gate.py."""

import json

import pytest
import yaml

import verification_gate
from verification_gate import PACKAGED_LIBRARY, SHIPPED_PERSPECTIVES, gate, main, resolve

_VERIFIED = """---
id: {id}
label: Test
verified: true
verified_by: Test Reviewer
verified_at: 2026-11-01
---

## Role

You are a tester.

## Primary concern

Correctness.

## Failure mode

Silent errors.

## Evaluation lens

- Is it correct?
"""


def _library(tmp_path, *ids, verified=True, name="library"):
    folder = tmp_path / name
    folder.mkdir(exist_ok=True)
    for pid in ids:
        text = _VERIFIED.format(id=pid)
        if not verified:
            text = text.replace("verified: true", "verified: false")
            text = text.replace("verified_by: Test Reviewer", "verified_by: null")
            text = text.replace("verified_at: 2026-11-01", "verified_at: null")
        (folder / f"{pid}.md").write_text(text)
    return folder


def _run_record(tmp_path, *ids, **overrides):
    entries = [
        {"id": pid, "confirmed_by": "Test User", "confirmed_at": "2026-11-12", **overrides}
        for pid in ids
    ]
    path = tmp_path / "run.yaml"
    path.write_text(
        yaml.dump({"perspective_confirmations": entries}).replace("'2026-11-12'", "2026-11-12")
    )
    return path


@pytest.fixture(autouse=True)
def empty_packaged_library(tmp_path, monkeypatch):
    """Keep the user's own git-ignored library/ files out of the tests."""
    folder = tmp_path / "packaged"
    folder.mkdir()
    monkeypatch.setattr(verification_gate, "PACKAGED_LIBRARY", folder)
    return folder


def test_shipped_perspectives_folder(skill_dir):
    assert SHIPPED_PERSPECTIVES == skill_dir / "references" / "perspectives"


def test_packaged_library_folder(skill_dir):
    assert PACKAGED_LIBRARY == skill_dir / "library"


# Sources and precedence (decision 18)


def test_resolve_prefers_a_given_folder_over_the_packaged_library(tmp_path, empty_packaged_library):
    _library(tmp_path, "security", name="packaged")
    given = _library(tmp_path, "security", name="given")
    assert resolve("security", [given]) == given / "security.md"


def test_resolve_prefers_the_packaged_library_over_the_shipped_default(
    tmp_path, empty_packaged_library
):
    _library(tmp_path, "security", name="packaged")
    assert resolve("security", []) == empty_packaged_library / "security.md"


def test_gate_passes_a_verified_perspective_from_the_packaged_library(
    tmp_path, empty_packaged_library
):
    _library(tmp_path, "security", name="packaged")
    used, errors = gate(["security"], [], _run_record(tmp_path, "security"))
    assert errors == []
    assert used == {"security": empty_packaged_library / "security.md"}


def test_gate_passes_a_verified_perspective_from_the_shipped_folder(tmp_path):
    shipped = _library(tmp_path, "security", name="shipped")
    _, errors = gate(["security"], [], _run_record(tmp_path, "security"), shipped=shipped)
    assert errors == []


def test_gate_uses_the_higher_source_even_when_it_is_unverified(tmp_path):
    _library(tmp_path, "security", name="packaged")
    higher = _library(tmp_path, "security", verified=False, name="attached")
    used, errors = gate(["security"], [higher], _run_record(tmp_path, "security"))
    assert used == {"security": higher / "security.md"}
    assert any("not verified" in e for e in errors)


def _config(tmp_path, library):
    path = tmp_path / "config.yaml"
    path.write_text(yaml.dump({"perspectives": {"library": str(library)}}))
    return path


def test_main_searches_the_configured_library(tmp_path, capsys):
    configured = _library(tmp_path, "security", name="configured")
    args = ["--perspective", "security", "--config", str(_config(tmp_path, configured))]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 0
    used = json.loads(capsys.readouterr().out)["perspectives"]
    assert used == {"security": str(configured / "security.md")}


def test_main_prefers_a_given_folder_over_the_configured_library(tmp_path, capsys):
    configured = _library(tmp_path, "security", name="configured")
    given = _library(tmp_path, "security", name="given")
    args = ["--perspective", "security", "--library", str(given)]
    args += ["--config", str(_config(tmp_path, configured))]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 0
    used = json.loads(capsys.readouterr().out)["perspectives"]
    assert used == {"security": str(given / "security.md")}


def test_main_prefers_the_configured_library_over_the_packaged_one(
    tmp_path, capsys, empty_packaged_library
):
    _library(tmp_path, "security", name="packaged")
    configured = _library(tmp_path, "security", name="configured")
    args = ["--perspective", "security", "--config", str(_config(tmp_path, configured))]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 0
    used = json.loads(capsys.readouterr().out)["perspectives"]
    assert used == {"security": str(configured / "security.md")}


def test_main_returns_1_when_the_config_is_missing(tmp_path, capsys):
    args = ["--perspective", "security", "--config", str(tmp_path / "none.yaml")]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 1
    assert "none.yaml" in capsys.readouterr().err


# Resolution


def test_resolve_prefers_the_users_copy(tmp_path):
    library = _library(tmp_path, "security")
    assert resolve("security", [library]) == library / "security.md"


def test_resolve_searches_libraries_in_order(tmp_path):
    first = _library(tmp_path, "security", name="first")
    second = _library(tmp_path, "security", name="second")
    assert resolve("security", [first, second]) == first / "security.md"


def test_resolve_falls_back_to_the_shipped_default(tmp_path):
    assert resolve("security", [tmp_path]) == SHIPPED_PERSPECTIVES / "security.md"


def test_resolve_returns_none_when_unknown(tmp_path):
    assert resolve("no_such_perspective", [tmp_path]) is None


# Gate


def test_gate_passes_when_verified_and_confirmed(tmp_path):
    library = _library(tmp_path, "security", "clinical")
    used, errors = gate(
        ["security", "clinical"], [library], _run_record(tmp_path, "security", "clinical")
    )
    assert errors == []
    assert used == {"security": library / "security.md", "clinical": library / "clinical.md"}


def test_gate_blocks_shipped_unverified_default(tmp_path):
    _, errors = gate(["security"], [], _run_record(tmp_path, "security"))
    assert any("security" in e and "not verified" in e for e in errors)


def test_gate_blocks_unverified_user_copy(tmp_path):
    library = _library(tmp_path, "security", verified=False)
    _, errors = gate(["security"], [library], _run_record(tmp_path, "security"))
    assert any("not verified" in e for e in errors)


def test_gate_blocks_missing_confirmation(tmp_path):
    library = _library(tmp_path, "security", "clinical")
    _, errors = gate(["security", "clinical"], [library], _run_record(tmp_path, "security"))
    assert any("clinical" in e and "not confirmed" in e for e in errors)


def test_gate_blocks_confirmation_without_name_or_date(tmp_path):
    library = _library(tmp_path, "security")
    record = _run_record(tmp_path, "security", confirmed_by="", confirmed_at="soon")
    _, errors = gate(["security"], [library], record)
    assert any("confirmed_by" in e for e in errors)
    assert any("confirmed_at" in e for e in errors)


def test_gate_blocks_unknown_perspective(tmp_path):
    _, errors = gate(["no_such_perspective"], [tmp_path], _run_record(tmp_path))
    assert any("no_such_perspective" in e and "not found" in e for e in errors)


def test_gate_blocks_invalid_perspective_file(tmp_path):
    library = _library(tmp_path, "security")
    (library / "security.md").write_text("no header")
    _, errors = gate(["security"], [library], _run_record(tmp_path, "security"))
    assert any("YAML header" in e for e in errors)


def test_gate_blocks_missing_run_record(tmp_path):
    library = _library(tmp_path, "security")
    _, errors = gate(["security"], [library], tmp_path / "none.yaml")
    assert any("Run record not found" in e for e in errors)


def test_gate_blocks_run_record_without_confirmations_list(tmp_path):
    library = _library(tmp_path, "security")
    record = tmp_path / "run.yaml"
    record.write_text("decision: AD-012\n")
    _, errors = gate(["security"], [library], record)
    assert any("perspective_confirmations" in e for e in errors)


def test_gate_blocks_invalid_run_record_yaml(tmp_path):
    library = _library(tmp_path, "security")
    record = tmp_path / "run.yaml"
    record.write_text("key: [\n")
    _, errors = gate(["security"], [library], record)
    assert any("not valid YAML" in e for e in errors)


def test_gate_reports_every_problem_at_once(tmp_path):
    _, errors = gate(["security", "clinical"], [], _run_record(tmp_path))
    assert len(errors) == 4  # two unverified, two unconfirmed


# Command line


def test_main_returns_0_and_names_the_files_used(tmp_path, capsys):
    library = _library(tmp_path, "security")
    args = ["--perspective", "security", "--library", str(library)]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"passed": True, "perspectives": {"security": str(library / "security.md")}}


def test_main_returns_1_and_lists_every_failure(tmp_path, capsys):
    args = ["--perspective", "security", "--perspective", "clinical"]
    args += ["--run-record", str(_run_record(tmp_path, "security"))]
    assert main(args) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["passed"] is False
    assert "clinical" in captured.err and "security" in captured.err


def test_gate_rejects_a_quoted_confirmation_date(tmp_path):
    library = _library(tmp_path, "security")
    record = tmp_path / "run.yaml"
    record.write_text(
        "perspective_confirmations:\n"
        "  - id: security\n    confirmed_by: Test User\n    confirmed_at: '2026-11-12'\n"
    )
    _, errors = gate(["security"], [library], record)
    assert errors == [
        "Confirmation of 'security': confirmed_at must be a date written as YYYY-MM-DD "
        "without quotes, got '2026-11-12'"
    ]
