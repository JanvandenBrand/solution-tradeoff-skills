"""Unit tests for scripts/budget.py (ported from test_weighter.py)."""

import json

import pytest

from budget import main, point_budget

_DEFAULTS = {"multiplier": 2.5, "round_to": 5, "minimum": 15}


def _budget(count: int) -> int:
    return point_budget(count, **_DEFAULTS)


def test_point_budget_known_input_12():
    assert _budget(12) == 30


def test_point_budget_minimum_enforced():
    assert _budget(4) == 15


def test_point_budget_minimum_enforced_when_zero():
    assert _budget(0) == 15


def test_point_budget_rounds_to_nearest_5():
    assert _budget(7) == 20  # 7 * 2.5 = 17.5 -> round(3.5) * 5 = 20


def test_point_budget_exact_multiple_unchanged():
    assert _budget(8) == 20


def test_point_budget_large_count():
    assert _budget(100) == 250


def test_point_budget_uses_round_to_when_rounded_to_zero():
    assert point_budget(1, multiplier=1, round_to=5, minimum=0) == 5


def test_point_budget_respects_other_settings():
    assert point_budget(10, multiplier=3, round_to=10, minimum=0) == 30


def test_point_budget_raises_value_error_when_count_negative():
    with pytest.raises(ValueError, match="count"):
        _budget(-1)


def test_point_budget_raises_value_error_when_round_to_not_positive():
    with pytest.raises(ValueError, match="round_to"):
        point_budget(5, multiplier=2.5, round_to=0, minimum=15)


def test_main_prints_budget_from_default_config(capsys):
    assert main(["--count", "12"]) == 0
    assert json.loads(capsys.readouterr().out) == {"count": 12, "budget": 30}


def test_main_reads_given_config(tmp_path, capsys):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("budget:\n  multiplier: 1\n  round_to: 1\n  minimum: 0\n")
    assert main(["--count", "7", "--config", str(cfg)]) == 0
    assert json.loads(capsys.readouterr().out)["budget"] == 7


def test_main_returns_1_when_count_negative(capsys):
    assert main(["--count", "-3"]) == 1
    assert "count" in capsys.readouterr().err
