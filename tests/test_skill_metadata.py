"""SKILL.md frontmatter stays within the Agent Skill limits this repository sets."""

import pytest
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


# Steps whose instructions are written

WRITTEN_STEPS = {1: ("Frame", "references/frame.md")}
HOST_TOOL_NAMES = [
    "AskUserQuestion",
    "TodoWrite",
    "WebFetch",
    "WebSearch",
    "Task tool",
    "Agent tool",
    "Bash tool",
    "Read tool",
    "Write tool",
    "Edit tool",
    "Skill tool",
]


def _step(number: int, name: str) -> str:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    return text.split(f"## {number}. {name}", 1)[1].split("\n## ", 1)[0]


@pytest.mark.parametrize("number", sorted(WRITTEN_STEPS))
def test_written_step_has_no_todo_and_points_at_its_reference(number):
    name, reference = WRITTEN_STEPS[number]
    body = _step(number, name)
    assert "TODO" not in body
    assert f"]({reference})" in body
    assert (SKILL_DIR / reference).is_file()


def _reference_sections(reference: str) -> list[str]:
    text = (SKILL_DIR / reference).read_text(encoding="utf-8")
    return [line[3:] for line in text.splitlines() if line.startswith("## ")]


def test_frame_reference_has_its_sections():
    assert _reference_sections("references/frame.md") == [
        "Purpose",
        "Conversation rules",
        "What to collect",
        "Problem validation",
        "Exit",
        "Return rule",
        "Output",
    ]


def test_frame_reference_checks_its_output_with_the_script():
    text = (SKILL_DIR / "references" / "frame.md").read_text(encoding="utf-8")
    assert "validate_run_record.py" in text and "--section frame" in text


def test_skill_text_names_no_host_tools():
    files = [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").rglob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for name in HOST_TOOL_NAMES:
            assert name not in text, f"{path.name} names the host tool '{name}'"
