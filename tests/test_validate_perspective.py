"""Unit tests for scripts/validate_perspective.py."""

import shutil

import pytest

from validate_perspective import main, validate_perspective

_HEADER = """---
id: {id}
label: Test
verified: false
verified_by: null
verified_at: null
---
"""

_BODY = """
## Role

You are a tester.

## Primary concern

Correctness.

## Failure mode

Silent errors.

## Evaluation lens

- Is it correct?
"""


def _write(tmp_path, text, name="sample"):
    path = tmp_path / f"{name}.md"
    path.write_text(text)
    return path


def _errors(tmp_path, header=None, body=_BODY, name="sample"):
    header = _HEADER.format(id=name) if header is None else header
    return validate_perspective(_write(tmp_path, header + body, name))


# Valid files


def test_validate_perspective_accepts_valid_fixture(fixtures):
    assert validate_perspective(fixtures / "perspective_valid.md") == []


def test_validate_perspective_accepts_verified_fixture(fixtures):
    assert validate_perspective(fixtures / "perspective_verified.md") == []


def test_validate_perspective_accepts_minimal_file(tmp_path):
    assert _errors(tmp_path) == []


def test_validate_perspective_accepts_multi_line_lens_items(tmp_path):
    body = _BODY.replace("- Is it correct?", "- Is it correct,\n  even when long?\n- Second?")
    assert _errors(tmp_path, body=body) == []


# Header


def test_validate_perspective_rejects_missing_header(tmp_path):
    errors = _errors(tmp_path, header="")
    assert any("header" in e for e in errors)


def test_validate_perspective_rejects_unclosed_header(tmp_path):
    errors = _errors(tmp_path, header="---\nid: sample\n", body="")
    assert any("header" in e for e in errors)


def test_validate_perspective_rejects_invalid_yaml_header(tmp_path):
    errors = _errors(tmp_path, header="---\nid: [\n---\n")
    assert any("YAML" in e for e in errors)


def test_validate_perspective_rejects_non_mapping_header(tmp_path):
    errors = _errors(tmp_path, header="---\n- a\n---\n")
    assert any("mapping" in e for e in errors)


def test_validate_perspective_rejects_missing_and_unknown_fields(tmp_path):
    header = "---\nid: sample\nlabel: Test\nindex: 3\n---\n"
    errors = _errors(tmp_path, header=header)
    joined = "\n".join(errors)
    assert "verified" in joined
    assert "index" in joined


def test_validate_perspective_rejects_id_not_matching_file_name(tmp_path):
    errors = _errors(tmp_path, header=_HEADER.format(id="other"))
    assert any("file name" in e for e in errors)


def test_validate_perspective_rejects_id_not_snake_case(tmp_path):
    errors = _errors(tmp_path, header=_HEADER.format(id="Data-Mgmt"), name="Data-Mgmt")
    assert any("lowercase" in e for e in errors)


def test_validate_perspective_rejects_empty_label(tmp_path):
    header = _HEADER.format(id="sample").replace("label: Test", "label: ''")
    assert any("label" in e for e in _errors(tmp_path, header=header))


def test_validate_perspective_rejects_verified_not_boolean(tmp_path):
    header = _HEADER.format(id="sample").replace("verified: false", "verified: 'no'")
    assert any("boolean" in e for e in _errors(tmp_path, header=header))


def test_validate_perspective_rejects_verifier_on_unverified_file(tmp_path):
    header = _HEADER.format(id="sample").replace("verified_by: null", "verified_by: Someone")
    assert any("verified_by" in e for e in _errors(tmp_path, header=header))


def test_validate_perspective_rejects_verified_without_name_and_date(tmp_path):
    header = _HEADER.format(id="sample").replace("verified: false", "verified: true")
    errors = _errors(tmp_path, header=header)
    assert any("verified_by" in e for e in errors)
    assert any("verified_at" in e for e in errors)


def test_validate_perspective_rejects_verified_at_not_a_date(tmp_path):
    header = (
        _HEADER.format(id="sample")
        .replace("verified: false", "verified: true")
        .replace("verified_by: null", "verified_by: Someone")
        .replace("verified_at: null", "verified_at: yesterday")
    )
    assert any("verified_at" in e for e in _errors(tmp_path, header=header))


# Body


def test_validate_perspective_rejects_missing_section(tmp_path):
    body = _BODY.replace("## Failure mode\n\nSilent errors.\n", "")
    assert any("Failure mode" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_rejects_sections_out_of_order(tmp_path):
    body = "\n## Primary concern\n\nX\n\n## Role\n\nY\n\n## Failure mode\n\nZ\n\n"
    body += "## Evaluation lens\n\n- Q\n"
    assert any("order" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_rejects_extra_heading(tmp_path):
    body = _BODY + "\n## Notes\n\nExtra.\n"
    assert any("Notes" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_rejects_title_heading(tmp_path):
    body = "\n# Title\n" + _BODY
    assert any("Title" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_ignores_hash_lines_in_code_blocks(tmp_path):
    body = _BODY.replace("Correctness.", "Correctness.\n\n```\n# not a heading\n```")
    assert _errors(tmp_path, body=body) == []


def test_validate_perspective_rejects_empty_section(tmp_path):
    body = _BODY.replace("Correctness.", "")
    assert any("Primary concern" in e and "empty" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_rejects_lens_without_bullets(tmp_path):
    body = _BODY.replace("- Is it correct?", "Is it correct?")
    assert any("Evaluation lens" in e for e in _errors(tmp_path, body=body))


def test_validate_perspective_reports_all_errors_at_once(tmp_path):
    header = _HEADER.format(id="other").replace("label: Test", "label: ''")
    body = _BODY.replace("- Is it correct?", "text")
    assert len(_errors(tmp_path, header=header, body=body)) >= 3


def test_validate_perspective_prefixes_errors_with_file_name(tmp_path):
    errors = _errors(tmp_path, header=_HEADER.format(id="other"))
    assert all(e.startswith("sample.md: ") for e in errors)


def test_validate_perspective_raises_file_not_found_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_perspective(tmp_path / "missing.md")


# Command line


def test_main_returns_0_for_valid_directory(tmp_path, fixtures, capsys):
    shutil.copy(fixtures / "perspective_valid.md", tmp_path)
    shutil.copy(fixtures / "perspective_verified.md", tmp_path)
    assert main([str(tmp_path)]) == 0
    assert "2 perspective file(s) valid" in capsys.readouterr().out


def test_main_returns_1_and_lists_errors(tmp_path, capsys):
    path = _write(tmp_path, _HEADER.format(id="other") + _BODY)
    assert main([str(path)]) == 1
    assert "file name" in capsys.readouterr().err


def test_main_returns_1_when_path_missing(tmp_path, capsys):
    assert main([str(tmp_path / "missing.md")]) == 1
    assert "missing.md" in capsys.readouterr().err


def test_main_returns_1_when_directory_has_no_perspectives(tmp_path, capsys):
    assert main([str(tmp_path)]) == 1
    assert "no perspective files" in capsys.readouterr().err


# Documentation


def test_format_reference_example_is_valid(tmp_path, skill_dir):
    text = (skill_dir / "references" / "perspective-format.md").read_text()
    example = text.split("```markdown\n", 1)[1].split("\n```", 1)[0]
    assert validate_perspective(_write(tmp_path, example + "\n", name="security")) == []
