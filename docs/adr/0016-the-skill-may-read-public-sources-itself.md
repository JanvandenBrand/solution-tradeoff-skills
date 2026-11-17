# 16. The skill may read public sources itself

## Context

Many background sources are public, such as open-source repositories, vendor documentation and published standards. Until now, the skill knew them only by the title or the claim the user gave. A rating that rests on a source nobody read gets basis `unread_source`, and such a rating cannot eliminate a candidate ([decision 14](0014-judgment-based-ratings-mark-candidates-at-risk.md)). Asking the user to copy public material into the conversation adds hands-on time ([decision 9](0009-success-target-under-ninety-minutes-hands-on.md)).

## Decision

If the host can fetch web content, the Gather step reads the public sources listed in the Frame intake, for example public repositories. For each source, it records what was read and to what depth.

Private or unpublished material is never fetched; the skill asks the user to attach it. No user material is sent to external services: the skill only reads public addresses.

Reason: a source the skill has read can support a rating, and reading a public source costs the user nothing.

## Status

Accepted

## Consequences

- Fewer ratings rest on unread sources (decision 14), so more Must ratings can eliminate a candidate when they fall below the threshold.
- Each background entry in the run record states its link, what was read, and its depth (`full`, `partial` or `title_only`).
- On a host that cannot fetch web content, public sources are attached by the user or stay unread.
