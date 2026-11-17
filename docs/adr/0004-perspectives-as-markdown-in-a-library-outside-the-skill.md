# 4. Perspectives as Markdown with a YAML header, in a library outside the skill

## Context

Perspectives describe the stakeholders whose views drive prioritization. Users need to add, adapt and reuse their own perspectives across analyses. Installed skills are read-only in claude.ai, so a user cannot store verified perspectives inside the skill.

## Decision

A perspective is a Markdown file with a YAML header. The header holds `id`, `label`, `verified`, `verified_by` and `verified_at`; the body holds Role, Primary concern, Failure mode and Evaluation lens. The skill ships unverified defaults. The user's verified perspectives live outside the skill: in claude.ai project files, or in a workspace folder in Claude Code. On a matching `id`, the user's copy wins.

Reason: users must be able to extend and reuse perspectives, and installed skills are read-only in claude.ai.

## Status

Accepted; amended by [decision 18](0018-perspectives-come-from-three-sources.md)

## Consequences

- `references/perspective-format.md` defines the format and `validate_perspective.py` enforces it.
- Shipped defaults are never verified; a user verifies their own copy.
- Perspective lookup searches the user's library first, then the shipped defaults.
