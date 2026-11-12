"""Supply-chain rules for the GitHub Actions workflows."""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
USES = re.compile(r"^\s*-?\s*uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
VERSION_COMMENT = re.compile(r"^\s+#\s*v\d+(\.\d+)*\s*$")


def _uses_lines(path: Path) -> list[tuple[str, str]]:
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = USES.match(line)
        if match:
            found.append((match["ref"], match["rest"]))
    return found


def _steps(path: Path) -> list[dict[str, object]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [step for job in data["jobs"].values() for step in job.get("steps", [])]


def test_there_is_at_least_one_workflow() -> None:
    assert WORKFLOWS


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_every_action_is_pinned_to_a_commit_with_its_version(path: Path) -> None:
    uses = _uses_lines(path)
    assert uses
    for ref, rest in uses:
        assert PINNED.match(ref), f"{ref} is not pinned to a full commit SHA"
        assert VERSION_COMMENT.match(rest), f"{ref} has no '# vX.Y.Z' comment"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_default_token_is_read_only(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["permissions"] == {"contents": "read"}


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_checkout_does_not_persist_credentials(path: Path) -> None:
    checkouts = [s for s in _steps(path) if str(s.get("uses", "")).startswith("actions/checkout@")]
    for step in checkouts:
        assert step.get("with", {}).get("persist-credentials") is False  # type: ignore[union-attr]


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_references_no_secrets(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"\bsecrets\.|GITHUB_TOKEN|github\.token", text)
