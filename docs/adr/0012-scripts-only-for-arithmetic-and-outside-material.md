# 12. Scripts only for arithmetic and for checking material the assistant did not write

## Context

Decision 3 puts judgment in the instructions and arithmetic in scripts. It did not say when a check deserves a script. The first frame validator checked text the assistant had written itself: the assistant wrote the section, then ran a script to judge its own wording. That added code without adding independence.

## Decision

This decision amends [decision 3](0003-judgment-in-instructions-arithmetic-in-scripts.md).

A script is justified only for arithmetic that must be identical every run, or for checking material the assistant did not write itself. Anything the assistant writes and then checks gets an instruction, not a validator.

## Status

Accepted

## Consequences

- The frame checks are a self-check in `references/frame.md`; `validate_run_record.py` checks only the format, the dates and the gather section against the script outputs.
- A new script needs arithmetic or outside material as its reason.
