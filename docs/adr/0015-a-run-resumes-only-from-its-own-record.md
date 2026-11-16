# 15. A run resumes only from its own record

## Context

A run spans several conversations. When a run is resumed, the confirmations it rests on (the frame, the scope, the perspectives) must be ones a person gave in that run. Rebuilding them from a transcript, a summary or memory would record confirmations nobody gave.

## Decision

Given `run.yaml`, the shared context and the working copy of the spreadsheet, the skill validates them and resumes at the first unfinished step.

The skill never writes confirmations taken from a transcript or from memory. If it rebuilds state from anything else, every confirmation is set to null and the user confirms each section again, in one block.

Reason: every confirmation in the record must be one a person gave, and a resumed run must not cost a full rerun.

## Status

Accepted

## Consequences

- The run record allows a null `confirmed_by` and `confirmed_at`; a null confirmation means the section is not confirmed, and the verification gate blocks on it.
- `validate_run_record.py` can check the format of the whole record without a section, for resuming.
- `SKILL.md` describes how to resume a run.
