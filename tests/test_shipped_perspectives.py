"""Every shipped perspective follows references/perspective-format.md and is unverified."""

import pytest
import yaml

from conftest import SKILL_DIR
from validate_perspective import validate_perspective

_FILES = sorted((SKILL_DIR / "references" / "perspectives").glob("*.md"))


def test_shipped_perspectives_exist():
    assert len(_FILES) == 12


@pytest.mark.parametrize("path", _FILES, ids=lambda p: p.stem)
def test_shipped_perspective_is_valid(path):
    assert validate_perspective(path) == []


@pytest.mark.parametrize("path", _FILES, ids=lambda p: p.stem)
def test_shipped_perspective_is_unverified(path):
    header = yaml.safe_load(path.read_text().split("---")[1])
    assert header["verified"] is False
