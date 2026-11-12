"""Unit tests for scripts/settings.py."""

from pathlib import Path

import pytest

from settings import DEFAULT_CONFIG, load_settings


def test_default_config_points_at_shipped_asset(skill_dir):
    assert DEFAULT_CONFIG == skill_dir / "assets" / "config.yaml"


def test_load_settings_reads_default_config():
    cfg = load_settings()
    assert cfg["budget"] == {"multiplier": 2.5, "round_to": 5, "minimum": 15}
    assert cfg["elimination"]["must_score_threshold"] == 6


def test_load_settings_reads_given_path(tmp_path):
    path = tmp_path / "custom.yaml"
    path.write_text("budget:\n  multiplier: 3\n")
    assert load_settings(path) == {"budget": {"multiplier": 3}}


def test_load_settings_raises_file_not_found_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing.yaml"):
        load_settings(tmp_path / "missing.yaml")


def test_load_settings_raises_value_error_when_not_a_mapping(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text("- a\n")
    with pytest.raises(ValueError, match="mapping"):
        load_settings(path)


def test_load_settings_raises_value_error_when_invalid_yaml(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("key: [\n")
    with pytest.raises(ValueError, match="not valid YAML"):
        load_settings(Path(path))


def test_default_excluded_statuses_are_the_spreadsheet_values():
    assert load_settings()["filter"]["excluded_statuses"] == ["removed"]
