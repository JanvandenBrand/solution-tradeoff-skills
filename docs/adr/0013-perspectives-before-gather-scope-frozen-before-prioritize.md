# 13. Perspectives before Gather; scope frozen before Prioritize

## Context

In the second prototype run, the scope was reopened four times, the point budget changed three times, and the stakeholder weighting was lost. The perspectives first saw the scope in the Prioritize step, so every Must challenge they raised sent the run back to Gather, and every new scope meant a new budget and new point distributions.

## Decision

This decision amends [decision 6](0006-separate-rating-pass-ten-steps.md).

The step order becomes: Frame, Propose perspectives, Verify perspectives, Gather, Prioritize, Rate, Validate, Compile, Challenge, Record.

Gather ends with one scope review: each verified perspective, in its own subagent where the host has them, returns only Must challenges against the proposed scope. The user settles them once, under the approval rule of [decision 11](0011-assistant-drafted-requirements-marked-and-approved-one-by-one.md) for anything drafted. Then the scope is frozen.

After the freeze, no step adds or changes requirements. Must challenges raised in Prioritize are recorded for the Challenge step only.

Reason: the perspectives challenge the scope once, before the budget is set, so the budget and the point distributions are made once.

## Status

Accepted

## Consequences

- The perspectives are chosen and verified from the frame alone, before the requirements are loaded.
- The Gather step asks the perspectives for Must challenges before it calculates the budget.
- The Prioritize step never returns to Gather; its Must challenges become input to the Challenge step.
- A requirement dropped by an accepted challenge leaves the scope by identifier (`gather.scope.requirements`); the spreadsheet is not changed.
