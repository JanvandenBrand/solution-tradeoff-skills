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
    "Propose perspectives",
    "Verify perspectives",
    "Gather",
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
    2: ("Propose perspectives", "references/propose-perspectives.md"),
    3: ("Verify perspectives", "references/verify-perspectives.md"),
    4: ("Gather", "references/gather.md"),
    5: ("Prioritize", "references/prioritize.md"),
    6: ("Rate", "references/rate.md"),
    7: ("Validate", "references/validate.md"),
    8: ("Compile", "references/compile.md"),
    9: ("Challenge", "references/challenge.md"),
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


def _gather_sequence() -> str:
    return _reference("gather.md").split("## Sequence", 1)[1].split("\n## ", 1)[0]


def test_gather_sequence_has_twelve_steps():
    sequence = _gather_sequence()
    numbered = [line.split(".", 1)[0] for line in sequence.splitlines() if line[:1].isdigit()]
    assert numbered == [str(i) for i in range(1, 13)]


def test_gather_reviews_the_scope_with_the_perspectives_before_the_budget():
    sequence = _gather_sequence()
    review = sequence.index("**Review the scope with the perspectives.**")
    assert review < sequence.index("budget.py")
    for phrase in ["run/gate.json", "independent subagents", "must_challenges", "one block"]:
        assert phrase in sequence, phrase


def test_gather_settles_challenges_once_and_freezes_the_scope():
    text = _reference("gather.md")
    for phrase in [
        "scope.requirements",
        "decision 11",
        "settles them once",
        "the scope is frozen",
        "No later step adds or changes requirements",
    ]:
        assert phrase in text, phrase


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
        "rank.py",
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
    assert "Never change the scope" in text


def test_prioritize_records_must_challenges_for_the_challenge_step_only():
    # Decision 13: the scope is frozen; Prioritize never returns to Gather.
    text = _reference("prioritize.md")
    assert "return to Gather" not in text
    assert "for the Challenge step only" in text


# Rate (step 6)


def test_gather_records_scope_review_independence():
    text = _reference("gather.md")
    assert "scope_review: full" in text
    assert "scope_review: limited" in text


def test_rate_reference_has_its_sections():
    assert _reference_sections("references/rate.md") == ["Rule", "Sequence", "Output"]


def test_rate_never_receives_prioritization_output():
    text = _reference("rate.md")
    rule = text.split("## Rule", 1)[1].split("\n## ", 1)[0]
    assert "run/shared-context.md" in rule
    assert "assets/rating.schema.json" in rule
    assert "run/responses/" not in text.split("## Sequence", 1)[1]
    for forbidden in ["responses", "preferred options", "point allocations"]:
        assert forbidden in rule, forbidden


def test_rate_records_limited_independence_without_subagents():
    text = _reference("rate.md")
    assert "independent subagent" in text
    assert "rate: limited" in text


def test_rate_names_the_basis_and_asks_one_dispute_question():
    text = _reference("rate.md")
    for basis in ["basis: source", "basis: judgment", "basis: unread_source"]:
        assert basis in text, basis
    assert "Basis:" not in text
    assert "rating.minimum" in text and "rating.maximum" in text
    assert '"Do you dispute any rating?"' in text
    assert "run/ratings.yaml" in text


def test_rate_defines_the_bases_without_their_consequences():
    # The consequences of a basis are stated in validate.md only.
    text = _reference("rate.md")
    assert "eliminat" not in text
    assert "Never choose a basis" not in text


def test_rate_names_the_source_of_a_source_based_rating():
    assert "source: <background title>" in _reference("rate.md")


# Validate (step 7)

VALIDATE_COMMANDS = [
    "python scripts/validate_response.py run/responses",
    "python scripts/check_budget.py run/responses --requirements run/filtered.json",
    "python scripts/validate_rating.py run/ratings.yaml --requirements run/filtered.json",
    "python scripts/elimination.py run/ratings.yaml --requirements run/filtered.json",
]


def test_validate_reference_has_its_sections():
    assert _reference_sections("references/validate.md") == ["Rule", "Sequence", "Output"]


def test_validate_runs_the_four_checks_in_order():
    text = _reference("validate.md")
    positions = [text.index(command) for command in VALIDATE_COMMANDS]
    assert positions == sorted(positions)


def test_validate_sends_failures_back_and_never_fixes_numbers():
    text = _reference("validate.md")
    assert "Never fix numbers by hand" in text
    assert "step 5" in text and "step 6" in text
    assert "eliminated" in text


# Decision 13: perspectives before Gather


@pytest.mark.parametrize(
    "reference, heading",
    [
        ("frame.md", "# Step 1: Frame"),
        ("propose-perspectives.md", "# Step 2: Propose perspectives"),
        ("verify-perspectives.md", "# Step 3: Verify perspectives"),
        ("gather.md", "# Step 4: Gather"),
        ("prioritize.md", "# Step 5: Prioritize"),
        ("rate.md", "# Step 6: Rate"),
        ("validate.md", "# Step 7: Validate"),
        ("compile.md", "# Step 8: Compile"),
        ("challenge.md", "# Step 9: Challenge"),
    ],
)
def test_reference_heading_carries_its_step_number(reference, heading):
    assert _reference(reference).splitlines()[0] == heading


def test_propose_starts_after_the_frame_and_gather_after_the_gate():
    assert "confirmed the frame" in _reference("propose-perspectives.md").split("\n## ", 1)[0]
    gather_intro = _reference("gather.md").split("\n## ", 1)[0]
    assert "verification gate" in gather_intro
    assert "Do not start Gather until the gate passes" in _reference("verify-perspectives.md")


def test_validate_presents_at_risk_candidates_in_one_block():
    # Decision 14: a judgment-based failure marks a candidate at risk; the user decides.
    text = _reference("validate.md")
    for phrase in [
        "at_risk",
        "one block",
        "validate.at_risk",
        "keep",
        "eliminate",
        "basis",
        "its `source`",
    ]:
        assert phrase in text, phrase


# Decision 15: a run resumes only from its own record


def test_skill_has_a_resuming_section_before_feedback():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    headings = [line[3:] for line in text.splitlines() if line.startswith("## ")]
    assert headings[-2:] == ["Resuming a run", "Feedback"]
    section = text.split("## Resuming a run", 1)[1].split("\n## ", 1)[0]
    for phrase in [
        "python scripts/validate_run_record.py run/run.yaml",
        "first unfinished step",
        "never write a confirmation taken from a transcript or from memory",
        "null",
        "one block",
    ]:
        assert phrase in section, phrase


# Compile (step 8)


def test_compile_reference_has_its_sections():
    assert _reference_sections("references/compile.md") == ["Rule", "Sequence", "Output"]


def test_compile_runs_rank_and_asks_nothing():
    text = _reference("compile.md")
    assert "python scripts/rank.py run/responses --ratings run/ratings.yaml" in text
    assert "run/ranking.json" in text and "run/analysis.md" in text
    assert "Ask the user nothing" in text


def test_compile_reports_a_close_call_as_a_shortlist():
    text = _reference("compile.md")
    assert "close_call" in text and "compile.close_call" in text
    assert "shortlist" in text and "not a winner" in text


@pytest.mark.parametrize(
    "flag",
    [
        "frame.problem.label",
        "drafted share",
        "`limited`",
        "unread_source",
        "must_challenges",
    ],
)
def test_compile_lists_each_flag(flag):
    assert flag in _reference("compile.md")


def test_compile_shows_each_perspective_score_next_to_its_preferred_option():
    text = _reference("compile.md")
    assert "preferred option" in text and "basis" in text and "`source`" in text


# Challenge (step 9)


def test_challenge_reference_has_its_sections():
    assert _reference_sections("references/challenge.md") == ["Rule", "Sequence", "Output"]


def test_challenge_runs_in_its_own_subagent_and_records_independence():
    text = _reference("challenge.md")
    assert "independent subagent" in text
    assert "challenge: full" in text and "challenge: limited" in text
    for source in ["run/analysis.md", "run/run.yaml", "run/ratings.yaml", "run/responses/"]:
        assert source in text, source


@pytest.mark.parametrize(
    "point",
    [
        "drafted requirements",
        "hypothesis",
        "at-risk",
        "after the freeze",
        "close call",
        "unread_source",
        "judgment",
        "principles",
    ],
)
def test_challenge_tests_each_point(point):
    assert point in _reference("challenge.md")


def test_challenge_classifies_findings_and_settles_them_in_one_block():
    text = _reference("challenge.md")
    assert "strongest case against the leading candidate" in text
    assert "run/challenge.md" in text
    for phrase in ["execution", "premise", "one block", "settled: accepted", "Frame step"]:
        assert phrase in text, phrase
