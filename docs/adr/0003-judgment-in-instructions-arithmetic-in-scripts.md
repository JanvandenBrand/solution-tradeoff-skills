# 3. Judgment in instructions, arithmetic in scripts

## Context

A trade-off analysis mixes judgment (framing the problem, inhabiting a perspective, challenging conclusions) with arithmetic (budgets, filters, thresholds, totals). An assistant is good at the first and unreliable at the second.

## Decision

The conversation, the framing and the perspective work live in the skill's instructions. The points budget, the filters, elimination, budget totals and schema validation live in scripts driven by `assets/config.yaml`.

A script is justified only for arithmetic that must be identical every run, or for checking material the assistant did not write itself. Anything the assistant writes and then checks gets an instruction, not a validator.

Reason: the arithmetic must give identical results every run; the judgment needs a conversation.

## Status

Accepted

## Consequences

- Every deterministic rule has a script with unit tests, and its settings live in `assets/config.yaml`, not in code or prose.
- The host must be able to run Python with the documented dependencies.
- Instructions call scripts rather than restating their rules, so the rules have one source.
