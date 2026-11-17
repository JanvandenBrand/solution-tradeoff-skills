# 6. Separate rating pass; ten steps

## Context

The old tool asked each perspective both what matters and how good each candidate is. That mixes two concerns, and ratings anchor on the perspective's preferred candidate.

## Decision

Perspectives decide what matters, through a point distribution. A separate pass rates every candidate on every in-scope requirement. Elimination runs on the Must ratings. The rater sees only the candidates and the requirements, never the perspectives' preferences or point totals.

The steps are: Frame, Gather, Propose perspectives, Verify perspectives, Prioritize, Rate, Validate, Compile, Challenge, Record.

Reason: one concern per step, and protection against ratings anchoring on preferences.

## Status

Accepted; amended by [decision 13](0013-perspectives-before-gather-scope-frozen-before-prioritize.md), [decision 14](0014-judgment-based-ratings-mark-candidates-at-risk.md) and [decision 17](0017-independent-subagents-are-a-precondition.md)

## Consequences

- A rating file has its own schema (`assets/rating.schema.json`) with no fields for preferences or points.
- `validate_rating.py` checks that every candidate is rated on every in-scope requirement.
- `elimination.py` reads the Must ratings from the rating file.
- The Rate step must not pass prioritization output to the rater.
