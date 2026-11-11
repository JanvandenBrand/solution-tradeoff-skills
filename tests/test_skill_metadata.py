"""SKILL.md frontmatter stays within the Agent Skill limits this repository sets."""

import yaml

from conftest import SKILL_DIR

MAX_DESCRIPTION = 200


def _frontmatter() -> dict:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def test_skill_description_is_at_most_200_characters():
    description = _frontmatter()["description"]
    assert len(description) <= MAX_DESCRIPTION, f"{len(description)} characters"


def test_skill_name_matches_folder_name():
    assert _frontmatter()["name"] == SKILL_DIR.name
