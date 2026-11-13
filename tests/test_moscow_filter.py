"""Unit tests for scripts/moscow_filter.py (ported from the old test_moscow_filter.py)."""

import json

import pytest
import yaml

from moscow_filter import filter_requirements, linked_principles, main, scope_summary

_ROWS = [
    {"req_id": "R001", "domain": "Security", "moscow": "Must", "plateau": 1, "status": "Active"},
    {"req_id": "R002", "domain": "Security", "moscow": "Must", "plateau": 1, "status": "Active"},
    {"req_id": "R003", "domain": "Clinical", "moscow": "Must", "plateau": 2, "status": "Active"},
    {"req_id": "R004", "domain": "Clinical", "moscow": "Should", "plateau": 2, "status": "Active"},
    {
        "req_id": "R005",
        "domain": "Security",
        "moscow": "Should",
        "plateau": 1,
        "status": "Deprecated",
    },
    {"req_id": "R006", "domain": "Security", "moscow": "Could", "plateau": 1, "status": "Active"},
]

_EXCLUDED = ["deprecated", "rejected"]


def _run(rows=_ROWS, moscow=("Must", "Should"), domains=(), plateau=None):
    result = filter_requirements(
        rows, moscow=moscow, domains=domains, plateau=plateau, excluded_statuses=_EXCLUDED
    )
    return result.must, result.should


def _ids(must, should):
    return {r["req_id"] for r in must + should}


# Basic filtering


def test_filter_requirements_to_must_only():
    must, should = _run(moscow=["Must"])
    assert should == []
    assert all(r["moscow"] == "Must" for r in must)


def test_filter_requirements_must_and_should():
    must, should = _run()
    assert len(must) == 3  # R001, R002, R003
    assert len(should) == 1  # R004 (R005 deprecated)


def test_filter_requirements_excludes_deprecated():
    assert "R005" not in _ids(*_run())


def test_filter_requirements_excludes_rejected():
    rows = [{"req_id": "RX", "domain": "D", "moscow": "Must", "plateau": 1, "status": "Rejected"}]
    must, _ = _run(rows=rows)
    assert must == []


def test_filter_requirements_excludes_could():
    assert "R006" not in _ids(*_run())


def test_filter_requirements_excluded_statuses_are_configurable():
    result = filter_requirements(_ROWS, moscow=["Must", "Should"], excluded_statuses=["active"])
    assert _ids(result.must, result.should) == {"R005"}


# Domain filter


def test_filter_requirements_by_domain():
    ids = _ids(*_run(domains=["Security"]))
    assert "R003" not in ids
    assert "R004" not in ids
    assert "R001" in ids


def test_filter_requirements_empty_domain_filter_includes_all_domains():
    ids = _ids(*_run())
    assert {"R001", "R003"} <= ids


# Plateau filter


def test_filter_requirements_plateau_excludes_higher():
    ids = _ids(*_run(plateau=1))
    assert "R003" not in ids
    assert "R004" not in ids


def test_filter_requirements_plateau_none_includes_all():
    must, _ = _run(moscow=["Must"], plateau=None)
    assert len(must) == 3


def test_filter_requirements_keeps_row_when_plateau_value_missing():
    rows = [{"req_id": "RX", "domain": "D", "moscow": "Must", "plateau": None, "status": "Active"}]
    must, _ = _run(rows=rows, moscow=["Must"], plateau=1)
    assert len(must) == 1


def test_filter_requirements_keeps_row_when_plateau_value_not_a_number():
    rows = [{"req_id": "RX", "domain": "D", "moscow": "Must", "plateau": "n/a", "status": "Active"}]
    must, _ = _run(rows=rows, moscow=["Must"], plateau=1)
    assert len(must) == 1


# Sort order and edge cases


def test_filter_requirements_sorts_by_req_id():
    must, _ = _run(rows=[_ROWS[2], _ROWS[0], _ROWS[1]], moscow=["Must"])
    ids = [r["req_id"] for r in must]
    assert ids == sorted(ids)


def test_filter_requirements_empty_input_returns_empty():
    assert _run(rows=[]) == ([], [])


def test_filter_requirements_case_insensitive_moscow():
    rows = [{"req_id": "R1", "domain": "D", "moscow": "MUST", "plateau": 1, "status": "Active"}]
    must, _ = _run(rows=rows, moscow=["Must"])
    assert len(must) == 1


def test_filter_requirements_case_insensitive_status():
    rows = [{"req_id": "R1", "domain": "D", "moscow": "Must", "plateau": 1, "status": "DEPRECATED"}]
    must, _ = _run(rows=rows, moscow=["Must"])
    assert must == []


# Command line


def test_main_filters_json_file(tmp_path, capsys):
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps(_ROWS))
    assert main([str(rows), "--domain", "Security"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["req_id"] for r in out["must"]] == ["R001", "R002"]
    # Default settings exclude only "removed", so the deprecated R005 stays.
    assert [r["req_id"] for r in out["should"]] == ["R005"]


def test_main_applies_moscow_and_plateau_options(tmp_path, capsys):
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps(_ROWS))
    assert main([str(rows), "--moscow", "Must", "--plateau", "1"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["req_id"] for r in out["must"]] == ["R001", "R002"]


def test_main_accepts_loader_output_shape(tmp_path, capsys):
    rows = tmp_path / "loaded.json"
    rows.write_text(json.dumps({"requirements": _ROWS, "principles": []}))
    assert main([str(rows)]) == 0
    assert len(json.loads(capsys.readouterr().out)["must"]) == 3


def test_main_returns_1_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.json")]) == 1
    assert "missing.json" in capsys.readouterr().err


# Default status settings (decision 8)


def test_main_excludes_removed_requirements_by_default(tmp_path, capsys):
    rows = [
        {"req_id": "R1", "domain": "D", "moscow": "Must", "plateau": 1, "status": "Removed"},
        {"req_id": "R2", "domain": "D", "moscow": "Must", "plateau": 1, "status": "Deprecated"},
    ]
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(rows))
    assert main([str(path)]) == 0
    assert [r["req_id"] for r in json.loads(capsys.readouterr().out)["must"]] == ["R2"]


# Drafts scoped by decision reference (decision 7)

_DRAFTS = [
    {"req_id": "D1", "domain": "D", "moscow": "Must", "status": "Draft", "ad_ref": "AD-012"},
    {"req_id": "D2", "domain": "D", "moscow": "Should", "status": "draft", "ad_ref": "AD-011"},
    {"req_id": "D3", "domain": "D", "moscow": "Must", "status": "Draft", "ad_ref": None},
    {"req_id": "D4", "domain": "D", "moscow": "Must", "status": "Draft", "ad_ref": "AD-3; ad-012"},
    {"req_id": "D5", "domain": "D", "moscow": "Could", "status": "Draft", "ad_ref": "AD-011"},
    {"req_id": "A1", "domain": "D", "moscow": "Must", "status": "Active", "ad_ref": "AD-011"},
]


def _drafts(decision_ref):
    return filter_requirements(
        _DRAFTS,
        moscow=["must", "should"],
        excluded_statuses=["removed"],
        draft_statuses=["draft"],
        decision_ref=decision_ref,
    )


def test_filter_requirements_keeps_drafts_tagged_with_the_decision():
    result = _drafts("AD-012")
    assert [r["req_id"] for r in result.must] == ["A1", "D1", "D4"]
    assert result.should == []


def test_filter_requirements_matches_one_of_several_references_ignoring_case():
    assert "D4" in {r["req_id"] for r in _drafts("ad-012").must}


def test_filter_requirements_does_not_match_partial_references():
    assert "D4" not in {r["req_id"] for r in _drafts("AD-01").must}


def test_filter_requirements_keeps_non_drafts_whatever_their_reference():
    assert [r["req_id"] for r in _drafts("AD-012").must][0] == "A1"


def test_filter_requirements_reports_excluded_drafts_that_were_otherwise_in_scope():
    # D5 is a Could, so it is out of scope anyway and not reported.
    assert _drafts("AD-012").excluded_drafts == ["D2", "D3"]


def test_filter_requirements_excludes_every_draft_without_decision_ref():
    result = _drafts(None)
    assert [r["req_id"] for r in result.must] == ["A1"]
    assert result.excluded_drafts == ["D1", "D2", "D3", "D4"]


def test_filter_requirements_keeps_draft_status_on_kept_rows():
    assert {r["status"] for r in _drafts("AD-012").must} == {"Active", "Draft"}


def test_main_reports_drafts_for_the_given_decision(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_DRAFTS))
    assert main([str(path), "--decision", "AD-012"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["req_id"] for r in out["must"]] == ["A1", "D1", "D4"]
    assert out["excluded_drafts"] == {"count": 2, "req_ids": ["D2", "D3"]}


# Unknown domains


def test_filter_requirements_raises_value_error_when_domain_unknown():
    with pytest.raises(ValueError) as exc:
        _run(domains=["Security", "Finances"])
    message = str(exc.value)
    assert "Finances" in message
    assert "Clinical, Security" in message


def test_filter_requirements_domain_check_ignores_case():
    assert _run(domains=["security"])[0]


def test_main_returns_1_when_domain_unknown(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_ROWS))
    assert main([str(path), "--domain", "Finances"]) == 1
    assert "Clinical, Security" in capsys.readouterr().err


# Drafts chosen by the user when the decision-reference column is missing (decision 7)


def _chosen(include, decision_ref=None):
    return filter_requirements(
        _DRAFTS,
        moscow=["must", "should"],
        excluded_statuses=["removed"],
        draft_statuses=["draft"],
        decision_ref=decision_ref,
        include_drafts=include,
    )


def test_filter_requirements_keeps_drafts_the_user_chose():
    result = _chosen(["D3", "d2"])
    assert [r["req_id"] for r in result.must] == ["A1", "D3"]
    assert [r["req_id"] for r in result.should] == ["D2"]
    assert result.included_drafts == ["D2", "D3"]
    assert result.excluded_drafts == ["D1", "D4"]


def test_filter_requirements_combines_chosen_and_tagged_drafts():
    result = _chosen(["D3"], decision_ref="AD-012")
    assert [r["req_id"] for r in result.must] == ["A1", "D1", "D3", "D4"]
    assert result.included_drafts == ["D3"]
    assert result.excluded_drafts == ["D2"]


def test_filter_requirements_chosen_draft_out_of_scope_stays_out():
    result = _chosen(["D5"])
    assert "D5" not in {r["req_id"] for r in result.must + result.should}
    assert result.included_drafts == []


def test_filter_requirements_rejects_chosen_ids_that_are_not_drafts():
    with pytest.raises(ValueError) as exc:
        _chosen(["A1", "NOPE"])
    message = str(exc.value)
    assert "A1" in message and "NOPE" in message


def test_filter_requirements_included_drafts_defaults_to_empty():
    assert _drafts("AD-012").included_drafts == []


def test_main_includes_chosen_drafts(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_DRAFTS))
    assert main([str(path), "--include-draft", "D3", "--include-draft", "D2"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["req_id"] for r in out["must"]] == ["A1", "D3"]
    assert out["included_drafts"] == ["D2", "D3"]
    assert out["excluded_drafts"] == {"count": 2, "req_ids": ["D1", "D4"]}


def test_main_returns_1_when_chosen_id_is_not_a_draft(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_DRAFTS))
    assert main([str(path), "--include-draft", "A1"]) == 1
    assert "A1" in capsys.readouterr().err


# Scope size (scope.max_requirements)


def test_scope_summary_under_the_cap():
    result = filter_requirements(_ROWS, moscow=["must", "should"], excluded_statuses=["removed"])
    assert scope_summary(result, 60) == {
        "count": 5,
        "must": 3,
        "should": 2,
        "max_requirements": 60,
        "exceeds": False,
    }


def test_scope_summary_at_the_cap_does_not_exceed():
    result = filter_requirements(_ROWS, moscow=["must", "should"], excluded_statuses=["removed"])
    assert scope_summary(result, 5)["exceeds"] is False


def test_scope_summary_above_the_cap_exceeds():
    result = filter_requirements(_ROWS, moscow=["must", "should"], excluded_statuses=["removed"])
    assert scope_summary(result, 4)["exceeds"] is True


def _config_with_cap(tmp_path, cap):
    from settings import load_settings

    settings = load_settings()
    settings["scope"]["max_requirements"] = cap
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(settings))
    return path


def test_main_reports_scope_without_warning_under_the_cap(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_ROWS))
    assert main([str(path)]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["scope"]["count"] == 5
    assert "warning" not in captured.err


def test_main_warns_when_scope_exceeds_the_cap(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_ROWS))
    assert main([str(path), "--config", str(_config_with_cap(tmp_path, 4))]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["scope"]["exceeds"] is True
    assert "warning: 5 requirements in scope, more than the 4 allowed" in captured.err


# Principles linked from in-scope requirements (apr_ref)

_PRINCIPLES = [
    {"principle_id": "P01", "description": "Reuse before buy"},
    {"principle_id": "P02", "description": "Data stays in the region"},
    {"principle_id": "P03", "description": "Open standards"},
]


def test_linked_principles_collects_each_reference_once_in_order():
    rows = [
        {"req_id": "R1", "apr_ref": "P02, p01"},
        {"req_id": "R2", "apr_ref": "P02"},
        {"req_id": "R3", "apr_ref": None},
    ]
    assert linked_principles(rows, _PRINCIPLES) == {
        "linked": [
            {"principle_id": "P01", "description": "Reuse before buy"},
            {"principle_id": "P02", "description": "Data stays in the region"},
        ],
        "unknown": [],
    }


def test_linked_principles_reports_references_missing_from_the_principles_sheet():
    rows = [{"req_id": "R1", "apr_ref": "P03; P09"}]
    result = linked_principles(rows, _PRINCIPLES)
    assert [p["principle_id"] for p in result["linked"]] == ["P03"]
    assert result["unknown"] == ["P09"]


def test_linked_principles_without_a_principles_sheet_lists_ids_only():
    rows = [{"req_id": "R1", "apr_ref": "P03"}]
    assert linked_principles(rows, None) == {
        "linked": [{"principle_id": "P03", "description": None}],
        "unknown": [],
    }


def test_main_lists_principles_linked_from_kept_requirements(tmp_path, capsys):
    rows = [
        {"req_id": "R1", "domain": "D", "moscow": "Must", "status": "Active", "apr_ref": "P01"},
        {"req_id": "R2", "domain": "D", "moscow": "Could", "status": "Active", "apr_ref": "P02"},
    ]
    path = tmp_path / "loaded.json"
    path.write_text(json.dumps({"requirements": rows, "principles": _PRINCIPLES}))
    assert main([str(path)]) == 0
    principles = json.loads(capsys.readouterr().out)["principles"]
    assert principles == {
        "linked": [{"principle_id": "P01", "description": "Reuse before buy"}],
        "unknown": [],
    }


# Scope by requirement identifier


def _by_id(ids, domains=()):
    return filter_requirements(
        _ROWS,
        moscow=["must", "should"],
        excluded_statuses=["removed"],
        domains=domains,
        requirement_ids=ids,
    )


def test_filter_requirements_keeps_only_the_named_requirements():
    result = _by_id(["R001", "r004"])
    assert [r["req_id"] for r in result.must + result.should] == ["R001", "R004"]


def test_filter_requirements_combines_named_requirements_with_domains():
    result = _by_id(["R004"], domains=["Security"])
    assert [r["req_id"] for r in result.must] == ["R001", "R002"]
    assert [r["req_id"] for r in result.should] == ["R004", "R005"]


def test_filter_requirements_named_requirements_still_pass_the_moscow_filter():
    result = _by_id(["R006"])
    assert result.must == [] and result.should == []


def test_filter_requirements_raises_value_error_on_unknown_identifiers():
    with pytest.raises(ValueError) as exc:
        _by_id(["R001", "R999", "X1"])
    message = str(exc.value)
    assert "R999" in message and "X1" in message and "R001" not in message


def test_main_scopes_by_requirement(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_ROWS))
    assert main([str(path), "--requirement", "R003", "--requirement", "R001"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [r["req_id"] for r in out["must"]] == ["R001", "R003"]


def test_main_returns_1_on_unknown_requirement(tmp_path, capsys):
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(_ROWS))
    assert main([str(path), "--requirement", "R999"]) == 1
    assert "R999" in capsys.readouterr().err


# Principle identifiers in free-text APR Link cells

_APR_PRINCIPLES = [
    {"principle_id": "APR02", "description": "Ease of use"},
    {"principle_id": "APR15", "description": "Open standards"},
]


def test_linked_principles_extracts_identifiers_from_free_text():
    rows = [{"req_id": "R1", "apr_ref": "APR02: promotes ease-of-use, APR15: …"}]
    assert linked_principles(rows, _APR_PRINCIPLES) == {
        "linked": [
            {"principle_id": "APR02", "description": "Ease of use"},
            {"principle_id": "APR15", "description": "Open standards"},
        ],
        "unknown": [],
    }


def test_linked_principles_free_text_without_a_principles_sheet():
    rows = [{"req_id": "R1", "apr_ref": "APR02: promotes ease-of-use, APR15: …"}]
    linked = linked_principles(rows, None)["linked"]
    assert [p["principle_id"] for p in linked] == ["APR02", "APR15"]


def test_linked_principles_lists_other_identifier_like_words_as_unknown():
    rows = [{"req_id": "R1", "apr_ref": "APR02: supports the NIS2 Directive"}]
    result = linked_principles(rows, _APR_PRINCIPLES)
    assert [p["principle_id"] for p in result["linked"]] == ["APR02"]
    assert result["unknown"] == ["NIS2"]
