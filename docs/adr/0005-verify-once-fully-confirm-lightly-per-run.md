# 5. Verify once fully; confirm lightly per run

## Context

The rule is that a person verifies every perspective before it influences an analysis. Full verification on every run would force the user to re-read and re-upload perspective files each time, which defeats the time target.

## Decision

A person fully verifies a perspective once, which is recorded in its header. In each run, the user confirms it with "Is this still correct?" That confirmation is recorded in the run record, not in the perspective file. The verification gate checks both before any prioritization.

Reason: keep the rule that a person verifies every perspective, without forcing a re-upload of perspective files every run.

## Status

Accepted

## Consequences

- `verification_gate.py` blocks prioritization unless every selected perspective is verified and confirmed for this run.
- The run record carries a confirmation (who, when) per selected perspective.
- Perspective files change only when a person verifies or edits them.
