# 1. New repository, command-line tool frozen

## Context

The trade-off analysis started as a command-line tool, solution-tradeoff-tool. It is being reworked into an Agent Skill that an assistant runs through conversation. The old repository is structured around a command-line pipeline that generates prompt files. Only Claude is in scope.

## Decision

The skill is built from scratch in a new repository, solution-tradeoff-skills, cherry-picking from solution-tradeoff-tool. The old tool is frozen as a stand-alone fallback and is not rewired to the skill.

Reason: restructuring the old repository costs more than starting clean, and because only Claude is in scope, the skill never needs to hand work to the tool.

## Status

Accepted

## Consequences

- Drift between the skill and the frozen tool is accepted; fixes are not backported.
- Only files tracked by git in the old repository may be copied. Ignored decision material stays out.
- The old repository is read-only for this work.
