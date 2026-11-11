"""Validate perspective files against references/perspective-format.md.

Usage:
    python validate_perspective.py <file or directory> [...]

Directories are searched for ``*.md`` files. Exit code 0 when every file is
valid, 1 otherwise; every error is listed on standard error.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

HEADER_FIELDS = ("id", "label", "verified", "verified_by", "verified_at")
SECTIONS = ("Role", "Primary concern", "Failure mode", "Evaluation lens")
_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _split(text: str) -> tuple[str, str] | None:
    """Return ``(header, body)`` or None when there is no closed YAML header."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    return None


def _check_header(header: dict[str, Any], stem: str) -> list[str]:
    errors: list[str] = []
    missing = [f for f in HEADER_FIELDS if f not in header]
    unknown = [f for f in header if f not in HEADER_FIELDS]
    if missing:
        errors.append(f"header is missing field(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"header has unknown field(s): {', '.join(map(str, unknown))}")

    pid = header.get("id")
    if "id" in header:
        if not isinstance(pid, str) or not _ID_PATTERN.match(pid):
            errors.append(
                f"id {pid!r} must use lowercase letters, digits and underscores, "
                "starting with a letter"
            )
        if pid != stem:
            errors.append(f"id {pid!r} does not match the file name '{stem}'")
    if "label" in header and (not isinstance(header["label"], str) or not header["label"].strip()):
        errors.append("label must be a non-empty string")

    verified = header.get("verified")
    if "verified" in header and not isinstance(verified, bool):
        errors.append(f"verified must be a boolean (true or false), got {verified!r}")
    by, at = header.get("verified_by"), header.get("verified_at")
    if verified is True:
        if not isinstance(by, str) or not by.strip():
            errors.append("verified_by must name the person who verified the perspective")
        if not isinstance(at, date):
            errors.append(f"verified_at must be a date (YYYY-MM-DD), got {at!r}")
    elif verified is False:
        if by is not None:
            errors.append("verified_by must be null while verified is false")
        if at is not None:
            errors.append("verified_at must be null while verified is false")
    return errors


def _sections(body: str) -> tuple[list[tuple[int, str]], dict[str, list[str]]]:
    """Return headings found (level, title) and the lines under each level-two heading."""
    headings: list[tuple[int, str]] = []
    content: dict[str, list[str]] = {}
    current: list[str] | None = None
    in_code = False
    for line in body.splitlines():
        if _FENCE.match(line):
            in_code = not in_code
        match = None if in_code else _HEADING.match(line)
        if match:
            level, title = len(match.group(1)), match.group(2)
            headings.append((level, title))
            current = content.setdefault(title, []) if level == 2 else None
        elif current is not None:
            current.append(line)
    return headings, content


def _check_body(body: str) -> list[str]:
    errors: list[str] = []
    headings, content = _sections(body)
    for level, title in headings:
        if level != 2 or title not in SECTIONS:
            errors.append(f"unexpected heading '{'#' * level} {title}'")
    found = [t for lvl, t in headings if lvl == 2 and t in SECTIONS]
    missing = [s for s in SECTIONS if s not in found]
    if missing:
        errors.append(f"body is missing section(s): {', '.join(missing)}")
    elif found != list(SECTIONS):
        errors.append(f"sections must appear once each, in this order: {', '.join(SECTIONS)}")

    for title in SECTIONS:
        lines = [ln for ln in content.get(title, []) if ln.strip()]
        if title in found and not lines:
            errors.append(f"section '{title}' is empty")
    lens = [ln for ln in content.get("Evaluation lens", []) if ln.strip()]
    if lens and not lens[0].lstrip().startswith("- "):
        errors.append("section 'Evaluation lens' must be a bulleted list ('- ')")
    elif lens and any(not (ln.startswith("- ") or ln.startswith("  ")) for ln in lens):
        errors.append("section 'Evaluation lens' must contain only list items")
    return errors


def validate_perspective(path: Path) -> list[str]:
    """Check one perspective file and return every problem found.

    Args:
        path: The perspective Markdown file.

    Returns:
        Error messages prefixed with the file name; empty when valid.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Perspective file not found: {path}")
    parts = _split(path.read_text(encoding="utf-8"))
    if parts is None:
        errors = ["file must start with a YAML header between two '---' lines"]
    else:
        header_text, body = parts
        errors = []
        try:
            header = yaml.safe_load(header_text)
        except yaml.YAMLError as exc:
            header = None
            errors.append(f"header is not valid YAML: {exc}")
        if header is not None and not isinstance(header, dict):
            errors.append("header must be a YAML mapping")
        elif isinstance(header, dict):
            errors.extend(_check_header(header, path.stem))
        errors.extend(_check_body(body))
    return [f"{path.name}: {e}" for e in errors]


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description="Validate perspective files.")
    parser.add_argument("paths", type=Path, nargs="+", help="Perspective files or directories.")
    args = parser.parse_args(argv)
    files: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            found = sorted(path.glob("*.md"))
            if not found:
                print(f"error: {path} contains no perspective files (*.md)", file=sys.stderr)
                return 1
            files.extend(found)
        elif path.exists():
            files.append(path)
        else:
            print(f"error: Perspective file not found: {path}", file=sys.stderr)
            return 1
    errors = [e for f in files for e in validate_perspective(f)]
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    if errors:
        return 1
    print(f"{len(files)} perspective file(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
