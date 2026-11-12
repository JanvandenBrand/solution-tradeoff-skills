# CLAUDE.md: solution-tradeoff-skills

Instructions for assistants and contributors working on this repository.

## Purpose

An Agent Skill (`skills/solution-tradeoff/`) that runs a multi-stakeholder trade-off analysis through conversation. It replaces the command-line tool `solution-tradeoff-tool`.

## Source of intent

The architecture decision records in [docs/adr/](docs/adr/README.md) say what the repository must do and why. Read the relevant record before changing behavior. When code or skill text disagrees with a record, the record wins: fix the code, or write a new record that supersedes the old one. Never edit an accepted record's decision; supersede it.

## Confidentiality (never violate)

Real decision material is confidential.

- Never read, copy, quote or commit real requirement spreadsheets, decision files, run records, ratings, perspective responses or background knowledge.
- The only spreadsheet in the repository is the synthetic `tests/fixtures/requirements_sample.xlsx`. Every other `*.xlsx` is git-ignored; keep it that way.
- Test fixtures are synthetic. Do not base them on real requirements, organizations, vendors or people.
- Before every commit, check `git status` for staged decision material, and unstage it.
- The old repository `solution-tradeoff-tool` is frozen: read only its git-tracked files, never modify it ([decision 1](docs/adr/0001-new-repository-command-line-tool-frozen.md)).

## Test first

1. Write or port the test.
2. Run it and see it fail.
3. Write the code until it passes.
4. Run `make check` without a pipe, so a failure is not hidden, and commit only when it passes.

Commit tests and code together, one concern per commit, so no commit is red. Every script has a test file in `tests/`, including its command-line entry point.

## Skill text is host-neutral

`SKILL.md` and everything under `references/` describe capabilities as conditions ("if the host can start independent subagents…"), never a specific assistant's tool names ([decision 2](docs/adr/0002-host-neutral-skill-text-claude-only.md)). Only Claude is supported for now.

## Judgment in instructions, arithmetic in scripts

Deterministic rules (budget, filters, elimination, totals, validation, gates) live in `skills/solution-tradeoff/scripts/` and read their settings from `assets/config.yaml`; never hardcode a threshold, status, column name or budget value ([decision 3](docs/adr/0003-judgment-in-instructions-arithmetic-in-scripts.md)). Scripts:

- are plain Python 3.11 modules with an `argparse` entry point, print JSON or a short summary, write errors to standard error, and exit 1 on failure;
- collect every error and report them together;
- depend only on `pyyaml`, `jsonschema` and, in `load_requirements.py` only, `openpyxl`.

## Writing

American English. Spell out generic abbreviations and acronyms in prose; official names that are acronyms (OMOP, FHIR, NIS2 Directive, SQL) may stay. If code or behavior changes, the README and docstrings change in the same commit.

## Quality gate

```bash
make check     # flake8, black --check, bandit, mypy (strict), pytest with coverage of at least 90%
make package   # dist/solution-tradeoff.zip for upload to claude.ai
```

Requires Poetry 2.x. If `poetry` on the path is older, pass its location: `make check POETRY=/path/to/poetry`. Unset `VIRTUAL_ENV` if another project's environment is active.
