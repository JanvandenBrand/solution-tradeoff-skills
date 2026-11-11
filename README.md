# Solution Trade-off Skills

An [Agent Skill](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) that runs a structured, multi-stakeholder trade-off analysis through conversation. It compares two or more candidate solutions against prioritized requirements and architecture principles, from the point of view of stakeholder perspectives that a person has verified first.

This skill replaces the command-line tool `solution-tradeoff-tool`.

> **Status:** early. The skill instructions are a skeleton; the scripts and the shipped perspectives are ready.

## Installing

| Host | How to install | Status |
|------|----------------|--------|
| Claude Code (plugin) | `/plugin marketplace add JanvandenBrand/solution-tradeoff-skills`, then `/plugin install solution-tradeoff@solution-tradeoff-skills` | Supported |
| Claude (claude.ai) | Zip the `skills/solution-tradeoff/` folder, then upload the zip under **Settings > Capabilities > Skills**. Code execution must be enabled for the scripts. | Supported |
| OpenAI Codex | | Planned |
| GitHub Copilot | | Planned |
| Mistral | | Planned |

To install by hand in Claude Code, copy `skills/solution-tradeoff/` to `~/.claude/skills/`.

## Skills

| Skill | Useful for |
|-------|------------|
| solution-tradeoff | Comparing candidate solutions and preparing a trade-off analysis for an architecture decision |

## What is in the skill

```
skills/solution-tradeoff/
├── SKILL.md                  # the steps the assistant follows
├── references/
│   ├── perspective-format.md # format of a perspective file
│   ├── perspectives/         # shipped default perspectives (unverified)
│   └── skill-feedback.md     # how to report a problem with the skill
├── scripts/                  # deterministic steps, run by the host
└── assets/
    ├── config.yaml           # thresholds, budget and spreadsheet column names
    └── tradeoff-output.schema.json
```

### Scripts

Every script prints JSON or a short summary, writes errors to standard error, exits with 1 on failure, and accepts `--help`. Settings come from `assets/config.yaml`; pass `--config <file>` to use another copy.

| Script | Purpose |
|--------|---------|
| `load_requirements.py <file.xlsx>` | Read requirements and principles from the requirements spreadsheet |
| `moscow_filter.py <rows.json>` | Keep Must and Should requirements, filtered by status, domain and plateau |
| `budget.py --count <n>` | Point budget each perspective distributes |
| `elimination.py <scores.json>` | Candidates that score below the threshold on any Must requirement |
| `validate_response.py <file or directory>` | Check perspective responses against the output schema |
| `validate_perspective.py <file or directory>` | Check perspective files against the perspective format |

### Dependencies

The scripts need Python 3.11 or later with:

- `pyyaml`: settings, perspective headers and responses
- `jsonschema`: response validation
- `openpyxl`: spreadsheet reading, used only by `load_requirements.py`

## Development

Requires [Poetry](https://python-poetry.org) 2.x and Python 3.11.

```bash
poetry env use python3.11
poetry install
make check        # flake8, black, bandit, mypy, pytest with coverage of at least 90%
```

If `poetry` on your path is older than 2.0, run `make check POETRY=/path/to/poetry`.

Tests live in `tests/`. The only spreadsheet in the repository is the synthetic sample `tests/fixtures/requirements_sample.xlsx`; every other `.xlsx` file is ignored, because real requirements and decision material are confidential.

## License

[MIT](LICENSE)
