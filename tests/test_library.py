"""The packaged perspective library holds the user's files, which git never tracks (decision 18)."""

import shutil
import subprocess  # nosec B404: runs git on this repository only

import pytest

from conftest import REPO_ROOT, SKILL_DIR

LIBRARY = SKILL_DIR / "library"
MAKEFILE = REPO_ROOT / "Makefile"
GIT = shutil.which("git")

needs_git = pytest.mark.skipif(
    GIT is None or not (REPO_ROOT / ".git").exists(), reason="needs a git checkout"
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    assert GIT is not None
    return subprocess.run(  # nosec B603: fixed git arguments, no shell
        [GIT, *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )


def test_library_has_a_readme_that_explains_it():
    text = (LIBRARY / "README.md").read_text(encoding="utf-8")
    assert "verified" in text and "make package" in text
    assert "never committed" in text


@needs_git
def test_only_the_readme_in_library_is_tracked():
    tracked = _git("ls-files", "skills/solution-tradeoff/library").stdout.split()
    assert tracked == ["skills/solution-tradeoff/library/README.md"]


@needs_git
def test_a_perspective_file_in_library_is_ignored():
    result = _git("check-ignore", "--no-index", "skills/solution-tradeoff/library/example.md")
    assert result.returncode == 0, "library/*.md must be git-ignored"
    readme = _git("check-ignore", "--no-index", "skills/solution-tradeoff/library/README.md")
    assert readme.returncode == 1, "the library README must stay tracked"


def test_package_leaves_out_the_library_readme():
    package = MAKEFILE.read_text(encoding="utf-8").split("package:", 1)[1]
    assert "solution-tradeoff/library/README.md" in package
