"""Unit tests for scripts/check_budget.py."""

import yaml

from check_budget import budget_errors, main


def _response(tmp_path, points, name="security.yaml"):
    data = {
        "perspective_id": name.removesuffix(".yaml"),
        "concerns": [{"concern": "X", "risk": "Y"}],
        "point_allocations": [
            {"criterion_id": f"REQ{i:03d}", "points": p, "rationale": "Z"}
            for i, p in enumerate(points, start=1)
        ],
        "preferred_option": "A",
    }
    path = tmp_path / name
    path.write_text(yaml.dump(data))
    return path


def test_budget_errors_accepts_exact_total(tmp_path):
    assert budget_errors(_response(tmp_path, [10, 5]), budget=15) == []


def test_budget_errors_rejects_total_below_budget(tmp_path):
    errors = budget_errors(_response(tmp_path, [10]), budget=15)
    assert errors == ["security.yaml: point allocations total 10, budget is 15"]


def test_budget_errors_rejects_total_above_budget(tmp_path):
    assert budget_errors(_response(tmp_path, [10, 10]), budget=15)


def test_budget_errors_reports_unreadable_allocations(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("perspective_id: x\n")
    assert any("point_allocations" in e for e in budget_errors(path, budget=15))


def test_budget_errors_reports_non_integer_points(tmp_path):
    path = _response(tmp_path, [10, 5])
    data = yaml.safe_load(path.read_text())
    data["point_allocations"][0]["points"] = "ten"
    path.write_text(yaml.dump(data))
    assert any("not a whole number" in e for e in budget_errors(path, budget=15))


def test_budget_errors_reports_invalid_yaml(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("key: [\n")
    assert any("not valid YAML" in e for e in budget_errors(path, budget=15))


# Command line: budget derives from the filtered requirements (3 -> 15 points)


def test_main_returns_0_when_every_response_spends_the_budget(tmp_path, fixtures, capsys):
    _response(tmp_path, [10, 5], "security.yaml")
    _response(tmp_path, [15], "clinical.yaml")
    args = [str(tmp_path), "--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 0
    assert "2 response file(s) spend exactly 15 points" in capsys.readouterr().out


def test_main_returns_1_and_lists_every_wrong_total(tmp_path, fixtures, capsys):
    _response(tmp_path, [10], "security.yaml")
    _response(tmp_path, [20], "clinical.yaml")
    args = [str(tmp_path), "--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 1
    err = capsys.readouterr().err
    assert "security.yaml" in err and "clinical.yaml" in err


def test_main_returns_1_when_path_missing(tmp_path, fixtures, capsys):
    args = [str(tmp_path / "none.yaml")]
    args += ["--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 1
    assert "none.yaml" in capsys.readouterr().err


def test_main_returns_1_when_directory_has_no_responses(tmp_path, fixtures, capsys):
    args = [str(tmp_path), "--requirements", str(fixtures / "requirements_filtered.json")]
    assert main(args) == 1
    assert "no response files" in capsys.readouterr().err
