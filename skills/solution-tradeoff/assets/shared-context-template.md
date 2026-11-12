<!--
Shared context block for one run of the solution trade-off analysis.
Filled in at the end of the Gather step from the run record and run/filtered.json.
This is the only input the Prioritize and Rate steps receive. Never add
perspective preferences, points or ratings to it.
-->

# Shared context: <decision identifier>

## Decision

<decision question>

Governing decisions: <identifiers, or "none">

## Problem

<problem statement>

- Outcome affected: <outcome>
- Causal claim: <how the problem leads to the outcome>
- Evidence: <one line per piece, with its kind and source>
- Label: <evidenced or hypothesis>

## Candidates

| Identifier | Name | Description |
|------------|------|-------------|
| A | <name> | <one line; mark the status quo> |
| B | <name> | <one line> |

## Planning horizon and plateau

<planning horizon>; plateau <n>

## Constraints

- <constraint>

## In-scope requirements

| Identifier | MoSCoW | Domain | Status | Requirement |
|------------|--------|--------|--------|-------------|
| <req_id> | <Must or Should> | <domain> | <status; drafts stay marked as drafts> | <description> |

## Principles

| Identifier | Principle |
|------------|-----------|
| <principle_id> | <description> |

## Background

- **<title>**: <summary>
