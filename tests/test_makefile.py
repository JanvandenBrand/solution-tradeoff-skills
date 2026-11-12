"""The Makefile runs every recipe so that a failing command in a pipe fails the target."""

from pathlib import Path

MAKEFILE = Path(__file__).resolve().parent.parent / "Makefile"


def _settings() -> dict[str, str]:
    found = {}
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if ":=" in line and not line.startswith("\t"):
            name, value = line.split(":=", 1)
            found[name.strip()] = value.strip()
    return found


def test_recipes_run_in_bash() -> None:
    assert _settings().get("SHELL") == "bash"


def test_recipes_fail_on_errors_unset_variables_and_pipes() -> None:
    assert _settings().get(".SHELLFLAGS") == "-eu -o pipefail -c"
