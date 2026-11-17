# 17. Independent subagents are a precondition

## Context

The scope review, the Prioritize and Rate passes and the Challenge step each depend on not seeing what the others produced. Until now, a host without subagents could run them in turn in one conversation, recorded as limited independence. In the fourth test run, the user set the rule: always deploy independent subagents, and do not proceed without them. A pass run in the same conversation has seen everything said before it, however carefully it is told to ignore it.

## Decision

This decision amends [decision 6](0006-separate-rating-pass-ten-steps.md) and [decision 13](0013-perspectives-before-gather-scope-frozen-before-prioritize.md).

Before the run starts, the skill asks the user once for consent to deploy independent subagents for the whole run: the scope review, Prioritize, Rate and Challenge. If the user declines, or the host cannot start independent subagents, the skill says so and stops. There is no fallback that runs these passes in one conversation.

Reason: the separation these passes exist for cannot be achieved by instruction alone.

## Status

Accepted

## Consequences

- The "limited independence" fallbacks are removed from the references; Compile and Record no longer report it.
- The run record keeps the `independence` field, and its values allow only `full`.
- A host without subagents cannot run the skill.
