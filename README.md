# Solution Trade-off Skills

An [Agent Skill](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) that runs a structured, multi-stakeholder trade-off analysis through conversation. It compares two or more candidate solutions against prioritized requirements and architecture principles, from the point of view of stakeholder perspectives that a person has verified first.

This skill replaces the command-line tool `solution-tradeoff-tool`.

**Goal:** a comparable analysis, from problem definition to a published architecture decision record, takes under 1.5 hours of hands-on time, against 3 to 4 hours with the old tool ([decision 9](docs/adr/0009-success-target-under-ninety-minutes-hands-on.md)).

> **Status:** early. All ten steps of the skill instructions are written, and the scripts and the shipped perspectives are ready. No real run has been made with the complete skill yet.

## Installing

| Host | How to install | Status |
|------|----------------|--------|
| Claude Code | Copy `skills/solution-tradeoff/` to `~/.claude/skills/` | Supported |
| Claude Code (plugin marketplace) | `/plugin marketplace add JanvandenBrand/solution-tradeoff-skills`, then `/plugin install solution-tradeoff@solution-tradeoff-skills` | Stub: untested until the repository is published |
| Claude (claude.ai) | Run `make package`, then upload `dist/solution-tradeoff.zip` under **Settings > Capabilities > Skills**. Code execution must be enabled for the scripts. | Supported |
| OpenAI Codex | | Planned |
| GitHub Copilot | | Planned |
| Mistral | | Planned |

## Skills

| Skill | Useful for |
|-------|------------|
| solution-tradeoff | Comparing candidate solutions and preparing a trade-off analysis for an architecture decision |

## Before your first analysis

The skill reads your requirements from a spreadsheet and your verified perspectives from your own library. Prepare both once:

1. **Requirements spreadsheet (.xlsx)** with a requirements sheet and a principles sheet. The sheet names and column headers are set under `spreadsheet` in `skills/solution-tradeoff/assets/config.yaml`; the defaults match `tests/fixtures/requirements_sample.xlsx`.
2. **Status values.** Set `filter.excluded_statuses` and `filter.draft_statuses` to the values your spreadsheet uses. The defaults exclude "Removed" and treat "Draft" as a draft.
3. **Decision-reference column.** Draft requirements count only when tagged with the current decision in the `AD Ref` column (several references may be separated by commas or semicolons). Without that column the skill cannot scope drafts; it reports this and offers to list the drafts for you to choose from; your choices are passed to `moscow_filter.py` with `--include-draft`. Check with:

   ```bash
   python skills/solution-tradeoff/scripts/check_prerequisites.py requirements.xlsx --decision AD-012
   ```

4. **Perspective library.** The shipped perspectives are unverified defaults. Keep your own verified copies outside the skill: as claude.ai project files, or in a folder of your Claude Code workspace. Your copy wins over a shipped default with the same `id`. Each file follows `references/perspective-format.md`.

To use settings other than the defaults, copy `config.yaml`, change it, and pass `--config <file>` to the scripts.

## What is in the skill

```
skills/solution-tradeoff/
├── SKILL.md                  # the steps the assistant follows
├── references/
│   ├── challenge.md          # step 9: argue the opposing side
│   ├── compile.md            # step 8: rank the candidates and write the analysis
│   ├── frame.md              # step 1: frame the decision and validate the problem
│   ├── gather.md             # step 4: what the candidates are judged against
│   ├── perspective-format.md # format of a perspective file
│   ├── perspectives/         # shipped default perspectives (unverified)
│   ├── prioritize.md         # step 5: each perspective spends the point budget
│   ├── propose-perspectives.md # step 2: choose the perspectives
│   ├── rate.md               # step 6: separate rating pass
│   ├── record.md             # step 10: the decision record, status Proposed
│   ├── validate.md           # step 7: checks and elimination
│   ├── verify-perspectives.md  # step 3: verify, confirm and pass the gate
│   └── skill-feedback.md     # how to report a problem with the skill
├── scripts/                  # deterministic steps, run by the host
└── assets/
    ├── config.yaml           # thresholds, budget and spreadsheet column names
    ├── decision-record-template.md
    ├── rating.schema.json
    ├── run-record.schema.json
    ├── shared-context-template.md # the only input to the Prioritize and Rate steps
    └── tradeoff-output.schema.json
```

### Scripts

Every script prints JSON or a short summary, writes errors to standard error, exits with 1 on failure, and accepts `--help`. Settings come from `assets/config.yaml`; pass `--config <file>` to use another copy.

| Script | Purpose |
|--------|---------|
| `check_prerequisites.py <file.xlsx> --decision <reference>` | Check that the spreadsheet has the decision-reference column; list the drafts when it does not |
| `load_requirements.py <file.xlsx>` | Read requirements and principles from the requirements spreadsheet, with counts per domain, MoSCoW level, plateau and status |
| `moscow_filter.py <rows.json> --decision <reference> [--include-draft <id> ...]` | Keep Must and Should requirements, filtered by status, domain or requirement identifier, and plateau; keep drafts tagged with the current decision or chosen by the user, and report the rest; list the principles linked from in-scope requirements; warn when the scope exceeds `scope.max_requirements` |
| `budget.py --count <n>` | Point budget each perspective distributes |
| `check_budget.py <file or directory> --requirements <filtered.json>` | Check that every perspective response spends exactly the point budget |
| `elimination.py <ratings.yaml> --requirements <filtered.json>` | Candidates eliminated by a below-threshold Must rating from a source that was read, and candidates at risk from one based on judgment or an unread source |
| `rank.py <responses> --ratings <ratings.yaml> --elimination <elimination.json> --run-record <run.yaml> --requirements <filtered.json>` | Rank the candidates kept after elimination: per perspective, points × rating over the budget, and the mean across perspectives; the share from drafted requirements, the gap between the first two candidates, whether it is a close call (`compile.close_call`), and the requirements that decide the lead |
| `validate_rating.py <ratings.yaml> --requirements <filtered.json>` | Check that every candidate is rated once on every in-scope requirement, on the configured scale, each with its basis |
| `validate_response.py <file or directory>` | Check perspective responses against the output schema |
| `validate_perspective.py <file or directory>` | Check perspective files against the perspective format |
| `validate_run_record.py <run.yaml> [--section gather] [--requirements <filtered.json>]` | Check the run record format (alone, when resuming a run), and with `--section gather` the gather counts, chosen drafts and budget against the script outputs |
| `verification_gate.py --perspective <id> --library <folder> --run-record <run.yaml>` | Block prioritization unless every selected perspective is verified and confirmed for this run |

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
