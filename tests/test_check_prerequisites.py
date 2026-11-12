"""Unit tests for scripts/check_prerequisites.py."""

import json
from pathlib import Path

import openpyxl

from check_prerequisites import check_prerequisites, main
from settings import load_settings

_SETTINGS = load_settings()
_FULL = ["Ref", "Requirement", "Category", "MoSCoW", "Plateau", "Status", "APR Link", "AD Ref"]
_ROWS = [
    ("REQ001", "Encrypt at rest", "Security", "Must", 1, "Active", None, None),
    ("REQ002", "New audit export", "Security", "Should", 1, "Draft", None, "AD-012"),
    ("REQ003", "Other decision's draft", "Technology", "Must", 1, "Draft", None, "AD-011"),
]


def _xlsx(tmp_path: Path, headers=_FULL, rows=_ROWS) -> Path:
    wb = openpyxl.Workbook()
    req = wb.active
    req.title = "Requirements"
    req.append(headers)
    for row in rows:
        req.append(row[: len(headers)])
    pri = wb.create_sheet("Principles")
    pri.append(["Ref", "Architecture Principle", "Category"])
    path = tmp_path / "reqs.xlsx"
    wb.save(path)
    return path


def test_check_prerequisites_passes_when_column_present(tmp_path):
    report = check_prerequisites(_xlsx(tmp_path), _SETTINGS)
    assert report["decision_reference_column"] == {"header": "AD Ref", "present": True}
    assert report["missing"] == []


def test_check_prerequisites_counts_drafts_tagged_with_the_decision(tmp_path):
    report = check_prerequisites(_xlsx(tmp_path), _SETTINGS, decision_ref="AD-012")
    assert report["drafts"] == {"total": 2, "tagged_with_decision": ["REQ002"]}


def test_check_prerequisites_flags_missing_column_and_lists_drafts(tmp_path):
    report = check_prerequisites(_xlsx(tmp_path, headers=_FULL[:7]), _SETTINGS)
    assert report["decision_reference_column"]["present"] is False
    assert any("AD Ref" in m for m in report["missing"])
    assert report["drafts_to_choose_from"] == [
        {"req_id": "REQ002", "description": "New audit export"},
        {"req_id": "REQ003", "description": "Other decision's draft"},
    ]


def test_check_prerequisites_header_name_comes_from_settings(tmp_path):
    settings = {
        **_SETTINGS,
        "spreadsheet": {
            **_SETTINGS["spreadsheet"],
            "columns": {**_SETTINGS["spreadsheet"]["columns"], "ad_ref": "Decision"},
        },
    }
    report = check_prerequisites(_xlsx(tmp_path), settings)
    assert report["decision_reference_column"] == {"header": "Decision", "present": False}


def test_check_prerequisites_passes_on_the_shipped_sample(fixtures):
    report = check_prerequisites(fixtures / "requirements_sample.xlsx", _SETTINGS)
    assert report["missing"] == []


def test_main_returns_0_and_prints_report(tmp_path, capsys):
    assert main([str(_xlsx(tmp_path)), "--decision", "AD-012"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["drafts"]["tagged_with_decision"] == ["REQ002"]


def test_main_returns_1_when_column_missing(tmp_path, capsys):
    assert main([str(_xlsx(tmp_path, headers=_FULL[:7]))]) == 1
    captured = capsys.readouterr()
    assert "AD Ref" in captured.err
    assert json.loads(captured.out)["drafts_to_choose_from"]


def test_main_returns_1_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.xlsx")]) == 1
    assert "missing.xlsx" in capsys.readouterr().err
