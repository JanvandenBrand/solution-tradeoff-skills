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

WRITTEN_STEPS = {
    1: ("Frame", "references/frame.md"),
    2: ("Gather", "references/gather.md"),
    3: ("Propose perspectives", "references/propose-perspectives.md"),
    4: ("Verify perspectives", "references/verify-perspectives.md"),
}
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


def test_frame_reference_checks_its_output_by_instruction_not_script():
    # Decision 12: the assistant writes the frame, so its checks are instructions.
    text = (SKILL_DIR / "references" / "frame.md").read_text(encoding="utf-8")
    assert "validate_run_record.py" not in text
    output = text.split("## Output", 1)[1]
    for rule in ["two candidates", "status quo", "hypothesis", "outcome", "confirmed_at"]:
        assert rule in output, rule


def test_skill_text_names_no_host_tools():
    files = [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").rglob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for name in HOST_TOOL_NAMES:
            assert name not in text, f"{path.name} names the host tool '{name}'"


def test_gather_reference_has_its_sections():
    assert _reference_sections("references/gather.md") == ["Rule", "Sequence", "Output"]


def test_gather_reference_names_the_script_for_every_count():
    text = (SKILL_DIR / "references" / "gather.md").read_text(encoding="utf-8")
    for command in [
        "check_prerequisites.py",
        "load_requirements.py",
        "moscow_filter.py",
        "--decision",
        "--include-draft",
        "--requirement",
        "origin: assistant",
        "budget.py",
        "validate_run_record.py",
        "--section gather",
        "scope.max_requirements",
        "assets/shared-context-template.md",
    ]:
        assert command in text, command


def test_gather_sequence_has_ten_steps():
    text = (SKILL_DIR / "references" / "gather.md").read_text(encoding="utf-8")
    sequence = text.split("## Sequence", 1)[1].split("\n## ", 1)[0]
    numbered = [line.split(".", 1)[0] for line in sequence.splitlines() if line[:1].isdigit()]
    assert numbered == [str(i) for i in range(1, 11)]


SHARED_CONTEXT_SECTIONS = [
    "Decision",
    "Problem",
    "Candidates",
    "Planning horizon and plateau",
    "Constraints",
    "In-scope requirements",
    "Principles",
    "Background",
]


def test_shared_context_template_has_its_sections_in_order():
    assert _template_sections() == SHARED_CONTEXT_SECTIONS


def test_shared_context_template_has_no_place_for_preferences_or_points():
    for section in _template_sections():
        for word in ("perspective", "preference", "point", "priorit", "weight", "rating"):
            assert word not in section.lower(), section


def _template_sections() -> list[str]:
    text = (SKILL_DIR / "assets" / "shared-context-template.md").read_text(encoding="utf-8")
    return [line[3:] for line in text.splitlines() if line.startswith("## ")]


def test_frame_reference_says_the_solution_check_is_a_judgment():
    text = (SKILL_DIR / "references" / "frame.md").read_text(encoding="utf-8")
    check = text.split("## Problem validation", 1)[1].split("\n## ", 1)[0]
    assert "judgment in the conversation" in check


# Propose perspectives (step 3)


def _reference(name: str) -> str:
    return (SKILL_DIR / "references" / name).read_text(encoding="utf-8")


def test_propose_perspectives_reference_has_its_sections():
    assert _reference_sections("references/propose-perspectives.md") == [
        "Rule",
        "Sequence",
        "Output",
    ]


def test_propose_perspectives_reads_the_user_library_before_the_defaults():
    text = _reference("propose-perspectives.md")
    assert text.index("user's perspective folder") < text.index("references/perspectives/")
    assert "the user's copy wins" in text


def test_propose_perspectives_proposes_one_block_and_lists_what_is_left_out():
    text = _reference("propose-perspectives.md")
    for phrase in ["4 to 7", "one block", "left out", "one-line reason"]:
        assert phrase in text, phrase


def test_propose_perspectives_drafts_a_missing_stakeholder_unverified():
    text = _reference("propose-perspectives.md")
    assert "perspective-format.md" in text
    assert "verified: false" in text


# Decision 12: perspective steps add no scripts


def test_scripts_folder_has_no_new_scripts():
    scripts = sorted(p.name for p in (SKILL_DIR / "scripts").glob("*.py"))
    assert scripts == [
        "budget.py",
        "check_budget.py",
        "check_prerequisites.py",
        "dates.py",
        "elimination.py",
        "load_requirements.py",
        "moscow_filter.py",
        "settings.py",
        "validate_perspective.py",
        "validate_rating.py",
        "validate_response.py",
        "validate_run_record.py",
        "verification_gate.py",
    ]


# Verify perspectives (step 4)


def test_verify_perspectives_reference_has_its_sections():
    assert _reference_sections("references/verify-perspectives.md") == [
        "Rule",
        "Sequence",
        "Output",
    ]


def test_verify_perspectives_confirms_verified_ones_together():
    text = _reference("verify-perspectives.md")
    assert '"Are these still correct?"' in text
    assert "perspective_confirmations" in text


def test_verify_perspectives_shows_unverified_ones_one_at_a_time():
    text = _reference("verify-perspectives.md")
    assert "one at a time" in text
    for field in ["verified: true", "verified_by", "verified_at"]:
        assert field in text, field


def test_verify_perspectives_hands_the_file_to_the_user_library():
    text = _reference("verify-perspectives.md")
    assert "project files" in text
    assert "user's folder" in text


def test_verify_perspectives_runs_the_gate_and_stops_when_blocked():
    text = _reference("verify-perspectives.md")
    assert "python scripts/verification_gate.py --perspective" in text
    assert "--run-record run/run.yaml" in text
    assert "stop" in text.split("verification_gate.py --perspective", 1)[1]


# Prioritize (step 5)


def test_prioritize_reference_has_its_sections():
    assert _reference_sections("references/prioritize.md") == ["Rule", "Sequence", "Output"]


def test_prioritize_names_the_four_inputs_and_nothing_else():
    text = _reference("prioritize.md")
    for item in [
        "run/shared-context.md",
        "run/gate.json",
        "run/budget.json",
        "assets/tradeoff-output.schema.json",
    ]:
        assert item in text, item
    assert "never sees another perspective's response" in text


def test_prioritize_records_limited_independence_without_subagents():
    text = _reference("prioritize.md")
    assert "independent subagents" in text
    assert "prioritize: limited" in text
    assert "run/responses/" in text


def test_prioritize_asks_nothing_and_summarizes_at_the_end():
    text = _reference("prioritize.md")
    assert "Ask the user nothing" in text
    assert "Must challenge" in text
    assert "return to Gather" in text
    assert "Never change the scope" in text
