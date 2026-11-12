# 8. Removed requirements excluded

## Context

The old tool excluded requirements with status "deprecated" or "rejected". Those values do not occur in the real spreadsheet, which uses "Removed".

## Decision

Requirements with status "Removed" are excluded by the status filter. The spreadsheet's own status values are used, configured in `assets/config.yaml`.

Reason: the old tool's excluded statuses do not occur in the real spreadsheet, so nothing was excluded.

## Status

Accepted

## Consequences

- `filter.excluded_statuses` in `assets/config.yaml` lists `removed`; matching ignores case.
- A spreadsheet with other status values needs its own settings file, passed with `--config`.
