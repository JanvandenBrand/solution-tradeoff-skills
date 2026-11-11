"""Shared pytest fixtures and paths."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "solution-tradeoff"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def skill_dir() -> Path:
    """Return the skill directory."""
    return SKILL_DIR


@pytest.fixture
def fixtures() -> Path:
    """Return the test fixtures directory."""
    return FIXTURES
