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


STEPS = [
    "Frame",
    "Gather",
    "Propose perspectives",
    "Verify perspectives",
    "Prioritize",
    "Rate",
    "Validate",
    "Compile",
    "Challenge",
    "Record",
]


def test_skill_steps_are_the_ten_in_order():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    headings = [line[3:] for line in text.splitlines() if line.startswith("## ")]
    numbered = [h for h in headings if h[0].isdigit()]
    assert numbered == [f"{i}. {step}" for i, step in enumerate(STEPS, start=1)]


def test_decision_record_template_has_the_cognitect_sections():
    text = (SKILL_DIR / "assets" / "decision-record-template.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("# ")
    sections = [line[3:] for line in lines if line.startswith("## ")]
    assert sections == ["Context", "Decision", "Status", "Consequences"]


def test_record_step_points_at_the_template():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    record = text.split("## 10. Record", 1)[1].split("\n## ", 1)[0]
    assert "assets/decision-record-template.md" in record
