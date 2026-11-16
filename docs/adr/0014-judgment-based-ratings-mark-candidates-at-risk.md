# 14. Judgment-based ratings mark candidates at risk; they don't eliminate

## Context

Between rounds with near-identical inputs, the rater moved nine ratings by up to 2 points, and one eliminated candidate rested on a single judgment rating. A rating that rests on judgment is not stable enough to remove a candidate on its own.

## Decision

This decision amends [decision 6](0006-separate-rating-pass-ten-steps.md).

A Must rating below the threshold eliminates a candidate only when it rests on a source that was read. If it rests on the rater's judgment or on an unread source, the candidate is marked at risk and the user decides.

Reason: elimination is final, so it needs a basis that gives the same rating every run.

## Status

Accepted

## Consequences

- Every rating carries a basis: `source`, `judgment` or `unread_source` (`assets/rating.schema.json`).
- `elimination.py` lists eliminated and at-risk candidates separately, each with the requirement and the basis.
- The Validate step shows the at-risk candidates to the user in one block; the user's decision on each is recorded in the run record.
