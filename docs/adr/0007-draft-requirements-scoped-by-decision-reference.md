# 7. Draft requirements included, scoped by decision reference

## Context

A new design brings new requirements that are still drafts. Ignoring them scores against yesterday's problem. Including every draft lets other decisions' drafts leak into this analysis.

## Decision

Draft requirements take part in the analysis. Only drafts tagged with the current decision in the `AD Ref` column are included; excluded drafts are counted and reported. If the column is missing, the skill flags it as a missing prerequisite and offers to list the drafts for the user to choose from. The compiled analysis flags conclusions that rest mainly on drafts.

Reason: score against the current problem, without letting other decisions' drafts leak in.

## Status

Accepted

## Consequences

- The requirements spreadsheet needs a decision-reference column: an external prerequisite that lowers usability. The README documents it under "Before your first analysis".
- `check_prerequisites.py` checks for the column and lists the drafts when it is missing.
- `moscow_filter.py` takes the current decision reference and reports excluded drafts.
- Kept drafts keep their status, so the Compile step can flag conclusions that rest on them.
