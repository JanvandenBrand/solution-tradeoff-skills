# 18. Perspectives come from three sources

## Context

[Decision 4](0004-perspectives-as-markdown-in-a-library-outside-the-skill.md) keeps the user's verified perspectives in one library outside the skill, searched before the shipped defaults. In the fifth test run, the only library the skill knew of was in a folder the host could not use as a library (in WSL) and in the old YAML format, so every perspective fell back to an unverified default. A user also had no way to ship verified perspectives inside the skill they upload.

## Decision

This decision amends [decision 4](0004-perspectives-as-markdown-in-a-library-outside-the-skill.md).

Perspectives come from three sources, in this order of precedence, and then from the shipped defaults:

1. perspective files attached to the chat or in the project's files;
2. a folder the host can read, named by the user or set in `config.yaml` (`perspectives.library`);
3. `skills/solution-tradeoff/library/`, packaged with the skill.

On a matching `id`, the higher source wins. The verification gate judges a perspective by its header (`verified`, `verified_by`, `verified_at`) and by the run's confirmation, not by where it lives.

Reason: a verified perspective must be usable wherever the user can put it, and where it lives says nothing about whether a person verified it.

## Status

Accepted

## Consequences

- `library/` is git-ignored except its README, so a user's perspectives are never committed; `make package` includes the perspective files in it.
- `verification_gate.py` searches the given folders, then `perspectives.library`, then `library/`, then the shipped defaults.
- The Propose perspectives step names the source of each perspective, and never takes a library path from memory or from earlier chats ([decision 15](0015-a-run-resumes-only-from-its-own-record.md)).
