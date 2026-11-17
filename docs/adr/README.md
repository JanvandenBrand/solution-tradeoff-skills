# Architecture decision records

Decisions that shape this repository, in the Cognitect format (title, context, decision, status, consequences). They are the source of intent: when code or skill text disagrees with a record, the record wins until a new record replaces it.

| Number | Decision | Status |
|--------|----------|--------|
| 1 | [New repository, command-line tool frozen](0001-new-repository-command-line-tool-frozen.md) | Accepted |
| 2 | [Host-neutral skill text, Claude only for now](0002-host-neutral-skill-text-claude-only.md) | Accepted |
| 3 | [Judgment in instructions, arithmetic in scripts](0003-judgment-in-instructions-arithmetic-in-scripts.md) | Accepted, amended by 12 |
| 4 | [Perspectives as Markdown with a YAML header, in a library outside the skill](0004-perspectives-as-markdown-in-a-library-outside-the-skill.md) | Accepted |
| 5 | [Verify once fully; confirm lightly per run](0005-verify-once-fully-confirm-lightly-per-run.md) | Accepted |
| 6 | [Separate rating pass; ten steps](0006-separate-rating-pass-ten-steps.md) | Accepted, amended by 13, 14 and 17 |
| 7 | [Draft requirements included, scoped by decision reference](0007-draft-requirements-scoped-by-decision-reference.md) | Accepted |
| 8 | [Removed requirements excluded](0008-removed-requirements-excluded.md) | Accepted |
| 9 | [Success target: under 1.5 hours of hands-on time](0009-success-target-under-ninety-minutes-hands-on.md) | Accepted |
| 10 | [Record step hands over to a decision-record skill](0010-record-step-hands-over-to-a-decision-record-skill.md) | Accepted |
| 11 | [Assistant-drafted requirements are marked and approved one by one](0011-assistant-drafted-requirements-marked-and-approved-one-by-one.md) | Accepted |
| 12 | [Scripts only for arithmetic and for checking material the assistant did not write](0012-scripts-only-for-arithmetic-and-outside-material.md) | Accepted |
| 13 | [Perspectives before Gather; scope frozen before Prioritize](0013-perspectives-before-gather-scope-frozen-before-prioritize.md) | Accepted, amended by 17 |
| 14 | [Judgment-based ratings mark candidates at risk; they don't eliminate](0014-judgment-based-ratings-mark-candidates-at-risk.md) | Accepted |
| 15 | [A run resumes only from its own record](0015-a-run-resumes-only-from-its-own-record.md) | Accepted |
| 16 | [The skill may read public sources itself](0016-the-skill-may-read-public-sources-itself.md) | Accepted |
| 17 | [Independent subagents are a precondition](0017-independent-subagents-are-a-precondition.md) | Accepted |

To change a decision, add a new record that supersedes or amends the old one and set the old record's status to "Superseded by N" or "Accepted; amended by N".
