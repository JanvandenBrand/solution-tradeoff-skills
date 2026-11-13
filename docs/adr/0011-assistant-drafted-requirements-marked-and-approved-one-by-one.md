# 11. Assistant-drafted requirements are marked and approved one by one

## Context

When the spreadsheet does not cover the decision, the assistant drafts requirements during the Gather step. In the first prototype run, the assistant drafted half of the in-scope requirements, the conclusion rested mainly on two of them, and all of them were approved in one answer. Perspectives must be verified by a person (decision 5); the criteria they are scored against had no such rule.

## Decision

The assistant records `origin: assistant` for each requirement it drafts, asks for approval of each one separately, and states which candidates it may favor. The Challenge step tests whether the conclusion rests on assistant-drafted requirements. The Record step lists them for the user to add to the source spreadsheet.

There is no validator for the approval: a script cannot tell whether a person approved.

## Status

Accepted

## Consequences

- The Gather step asks more questions, but the criteria the outcome rests on are approved by a person, one at a time.
- The run record marks drafted requirements with their origin (`gather.drafted_requirements`).
- The approval rule lives in the instructions (`references/gather.md`), not in a script (decision 3).
