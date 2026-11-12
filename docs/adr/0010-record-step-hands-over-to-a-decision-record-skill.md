# 10. Record step hands over to a decision-record skill

## Context

The baseline in decision 9 ends at a published architecture decision record. Hosts may already have a skill that writes decision records; rebuilding one here would duplicate it.

## Decision

The Record step hands the compiled and challenged analysis to a decision-record skill when the host has one. Otherwise it produces a decision record from a template in the Cognitect format: title, context, decision, status, consequences.

Reason: the baseline ends at a published decision record, so the skill must too, and rebuilding an existing skill would duplicate it.

## Status

Accepted

## Consequences

- The skill ships `assets/decision-record-template.md` as the fallback.
- The handover depends on what the host offers, described as a condition in the skill text.
