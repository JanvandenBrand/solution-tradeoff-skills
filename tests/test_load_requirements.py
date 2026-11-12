"""Unit tests for scripts/load_requirements.py (ported from test_requirements_loader.py)."""

import json
import warnings
from pathlib import Path

import openpyxl
import pytest

from load_requirements import count_requirements, load_requirements, main
from settings import load_settings

_CFG = load_settings()["spreadsheet"]
_HEADERS = ["Ref", "Requirement", "Category", "MoSCoW", "Plateau", "Status", "APR Link", "AD Ref"]
_PRINCIPLE_HEADERS = ["Ref", "Architecture Principle", "Category"]

_REQ_ROWS: list[tuple] = [
    ("REQ-001", "Encrypt at rest", "Security", "Must", 1, "Active", "APR-01", None),
    (
        "REQ-002",
        "Enforce multi-factor sign-in",
        "Security",
        "Must",
        1,
        "Active",
        "APR-01",
        "AD-001",
    ),
    ("REQ-003", "Keep raw data on site", "Technology", "Must", 1, "Active", None, None),
    ("REQ-004", "Audit trail", "Security", "Must", 1, "Active", "APR-02", None),
    ("REQ-005", "Support data exchange standard", "Technology", "Must", 2, "Active", None, None),
    ("REQ-006", "Deploy in the cloud", "Technology", "Must", 1, "Active", None, "AD-001"),
    ("REQ-007", "10 concurrent jobs", "Technology", "Should", 2, "Active", None, None),
    ("REQ-008", "Interface for submission", "Technology", "Should", 2, "Active", None, None),
    ("REQ-009", "Differential privacy", "Security", "Should", 2, "Active", "APR-01", None),
    ("REQ-010", "Printable reports", "Technology", "Could", 3, "Active", None, None),
    ("REQ-011", "Old approach", "Technology", "Must", 1, "Deprecated", None, None),
]


def _make_xlsx(
    tmp_path: Path,
    req_rows: list[tuple],
    headers: list[str] = _HEADERS,
    with_principles: bool = True,
) -> Path:
    wb = openpyxl.Workbook()
    req = wb.active
    req.title = "Requirements"
    req.append(headers)
    for row in req_rows:
        req.append(row)
    if with_principles:
        pri = wb.create_sheet("Principles")
        pri.append(_PRINCIPLE_HEADERS)
        pri.append(("APR-01", "Be cloud-agnostic", "Architecture"))
    path = tmp_path / "reqs.xlsx"
    wb.save(path)
    return path


# Happy path


def test_load_requirements_loads_all_rows(tmp_path):
    rows, _ = load_requirements(_make_xlsx(tmp_path, _REQ_ROWS), _CFG)
    assert len(rows) == 11  # deprecated row still loaded; filtering is a separate step
    assert rows[0]["req_id"] == "REQ-001"
    assert rows[0]["moscow"] == "Must"
    assert rows[0]["status"] == "Active"


def test_load_requirements_loads_principles(tmp_path):
    _, principles = load_requirements(_make_xlsx(tmp_path, _REQ_ROWS), _CFG)
    assert principles == [
        {"principle_id": "APR-01", "description": "Be cloud-agnostic", "domain": "Architecture"}
    ]


def test_load_requirements_shipped_sample_loads(fixtures):
    rows, principles = load_requirements(fixtures / "requirements_sample.xlsx", _CFG)
    assert len(rows) == 12  # 11 active + 1 deprecated
    assert len(principles) == 5


def test_load_requirements_preserves_moscow_values(tmp_path):
    rows, _ = load_requirements(_make_xlsx(tmp_path, _REQ_ROWS), _CFG)
    assert {"Must", "Should", "Could"} <= {r["moscow"] for r in rows}


def test_load_requirements_loads_reference_columns(tmp_path):
    rows, _ = load_requirements(_make_xlsx(tmp_path, _REQ_ROWS), _CFG)
    assert rows[0]["apr_ref"] == "APR-01"
    assert rows[2]["apr_ref"] is None
    assert rows[1]["ad_ref"] == "AD-001"
    assert rows[0]["ad_ref"] is None


def test_load_requirements_skips_empty_rows(tmp_path):
    req_rows = [
        ("REQ-001", "X", "Y", "Must", 1, "Active", None, None),
        (None,) * 8,
        ("REQ-002", "Z", "W", "Should", 1, "Active", None, None),
    ]
    rows, _ = load_requirements(_make_xlsx(tmp_path, req_rows), _CFG)
    assert len(rows) == 2


def test_load_requirements_column_names_come_from_config(tmp_path):
    headers = ["ID", *_HEADERS[1:]]
    cfg = {**_CFG, "columns": {**_CFG["columns"], "req_id": "ID"}}
    rows, _ = load_requirements(_make_xlsx(tmp_path, _REQ_ROWS[:1], headers=headers), cfg)
    assert rows[0]["req_id"] == "REQ-001"


# Error paths


def test_load_requirements_raises_file_not_found_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_requirements(tmp_path / "missing.xlsx", _CFG)


def test_load_requirements_raises_value_error_when_required_column_missing(tmp_path):
    path = _make_xlsx(tmp_path, [], headers=["Ref", "Requirement", "Category", "MoSCoW", "Plateau"])
    with pytest.raises(ValueError, match="Status"):
        load_requirements(path, _CFG)


def test_load_requirements_raises_value_error_when_sheet_missing(tmp_path):
    path = _make_xlsx(tmp_path, [], with_principles=False)
    with pytest.raises(ValueError, match="Principles"):
        load_requirements(path, _CFG)


def test_load_requirements_raises_value_error_when_requirements_sheet_missing(tmp_path):
    cfg = {**_CFG, "requirements_sheet": "Needs"}
    with pytest.raises(ValueError, match="Needs"):
        load_requirements(_make_xlsx(tmp_path, []), cfg)


def test_load_requirements_raises_value_error_when_principle_column_missing(tmp_path):
    cfg = {**_CFG, "principles_columns": {**_CFG["principles_columns"], "domain": "Area"}}
    with pytest.raises(ValueError, match="Area"):
        load_requirements(_make_xlsx(tmp_path, []), cfg)


# Optional columns


def test_load_requirements_warns_when_plateau_column_absent(tmp_path):
    headers = ["Ref", "Requirement", "Category", "MoSCoW", "Status"]
    path = _make_xlsx(tmp_path, [("REQ-001", "X", "Y", "Must", "Active")], headers=headers)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        rows, _ = load_requirements(path, _CFG)
    messages = [str(w.message) for w in caught]
    assert any("plateau" in m for m in messages)
    assert any("apr_ref" in m for m in messages)
    assert any("ad_ref" in m for m in messages)
    assert rows[0]["plateau"] is None
    assert rows[0]["apr_ref"] is None


def test_load_requirements_optional_columns_come_from_config(tmp_path):
    headers = ["Ref", "Requirement", "Category", "MoSCoW", "Plateau", "Status"]
    cfg = {**_CFG, "optional_columns": []}
    with pytest.raises(ValueError, match="APR Link"):
        load_requirements(_make_xlsx(tmp_path, [], headers=headers), cfg)


# Command line


def test_main_prints_rows_as_json(fixtures, capsys):
    assert main([str(fixtures / "requirements_sample.xlsx")]) == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["requirements"]) == 12
    assert len(out["principles"]) == 5


def test_main_returns_1_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.xlsx")]) == 1
    assert "missing.xlsx" in capsys.readouterr().err


# Headers


def test_requirement_headers_lists_the_requirements_sheet_headers(fixtures):
    from load_requirements import requirement_headers

    assert requirement_headers(fixtures / "requirements_sample.xlsx", _CFG) == _HEADERS


# Counts


def test_count_requirements_per_domain_moscow_plateau_and_status():
    rows = [
        {"domain": "Security", "moscow": "Must", "plateau": 1, "status": "Active"},
        {"domain": "Security", "moscow": "Should", "plateau": 2, "status": "Draft"},
        {"domain": "Clinical", "moscow": "Must", "plateau": None, "status": ""},
    ]
    assert count_requirements(rows) == {
        "total": 3,
        "domain": {"Clinical": 1, "Security": 2},
        "moscow": {"Must": 2, "Should": 1},
        "plateau": {"(none)": 1, "1": 1, "2": 1},
        "status": {"(none)": 1, "Active": 1, "Draft": 1},
    }


def test_count_requirements_of_no_rows():
    assert count_requirements([]) == {
        "total": 0,
        "domain": {},
        "moscow": {},
        "plateau": {},
        "status": {},
    }


def test_main_prints_counts(fixtures, capsys):
    assert main([str(fixtures / "requirements_sample.xlsx")]) == 0
    counts = json.loads(capsys.readouterr().out)["counts"]
    assert counts["total"] == 12
    assert counts["moscow"] == {"Could": 1, "Must": 6, "Should": 5}
    assert counts["plateau"] == {"1": 10, "2": 2}
    assert counts["status"] == {"Active": 11, "Deprecated": 1}
    assert counts["domain"]["Technology"] == 6
