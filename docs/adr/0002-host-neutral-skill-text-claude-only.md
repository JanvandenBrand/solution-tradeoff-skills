# 2. Host-neutral skill text, Claude only for now

## Context

Agent Skills can run in several assistants. Supporting each one costs manifests, install instructions and tests. Only Claude is needed now, but other assistants may follow.

## Decision

SKILL.md and the reference files describe capabilities as conditions ("if the host can start independent subagents…"), never Claude-specific tool names. Only Claude is supported: claude.ai first, Claude Code second. Other assistants (Codex, Copilot, Mistral) are placeholder rows in the README, with no manifests and no tests.

Reason: keep the option to extend later without paying for it now.

## Status

Accepted

## Consequences

- Skill text must be reviewed for host-specific tool names before each commit.
- Only the Claude Code plugin manifest exists; the marketplace is a stub.
- Adding another assistant later means adding its manifest and tests, not rewriting the skill text.
