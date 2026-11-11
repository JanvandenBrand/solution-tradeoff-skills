# Perspective format

A perspective describes one stakeholder whose point of view is used to evaluate the candidate solutions. Each perspective is one Markdown file with a YAML header. The shipped defaults live in [perspectives/](perspectives/).

Check a file against this format with `scripts/validate_perspective.py <file or directory>`.

## File name

`<id>.md`, where `<id>` is the value of the `id` field.

## Header

The file starts with a YAML header between two `---` lines. The header has exactly these fields:

| Field | Type | Rule |
|-------|------|------|
| `id` | string | Lowercase letters, digits and underscores, starting with a letter. Must match the file name. |
| `label` | string | Readable name, for example `Security Perspective`. Not empty. |
| `verified` | boolean | `true` only after a person has reviewed and accepted the perspective. |
| `verified_by` | string or null | Name of the person who verified it. `null` when `verified` is `false`; not empty when `verified` is `true`. |
| `verified_at` | date or null | Date of verification, as `YYYY-MM-DD`. `null` when `verified` is `false`; required when `verified` is `true`. |

Shipped perspectives are always unverified. Only a person sets `verified` to `true`, after reading the whole file. Nothing is scored with a perspective until it is verified.

## Body

The body has exactly four level-two headings, in this order, and no other headings:

1. `## Role`: who the stakeholder is, written in the second person ("You are…"), so it can brief whoever takes on the perspective. Be specific about job, organization type and responsibilities.
2. `## Primary concern`: what this stakeholder cares about most.
3. `## Failure mode`: what would make this stakeholder reject a solution.
4. `## Evaluation lens`: a bulleted list (`- `) of the questions this stakeholder asks of every candidate. At least one item.

Every section must contain text.

## Example

```markdown
---
id: security
label: Security Perspective
verified: false
verified_by: null
verified_at: null
---

## Role

You are the security architect for the platform.

## Primary concern

Defense in depth.

## Failure mode

Any solution that exposes credentials without a documented compensating control.

## Evaluation lens

- Is this secure by default?
- What is the blast radius if this component is compromised?
```
