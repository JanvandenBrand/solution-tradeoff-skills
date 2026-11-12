---
name: solution-tradeoff
description: Compare candidate solutions in a multi-stakeholder trade-off analysis against prioritized requirements. Use when weighing options or preparing a trade-off for an architecture decision.
---

# Solution trade-off analysis

Nothing is scored until a person has verified every selected perspective.

## 1. Frame

Establish the decision and validate the problem, one question at a time, then ask the user to confirm the frame summary. Nothing else starts before that confirmation. Follow [references/frame.md](references/frame.md); its output is the `frame` section of the run record. Any later step that finds the problem, the outcome or the criteria wrong returns here as a question for the user.

## 2. Gather

TODO: load and filter the requirements and principles, and collect background knowledge. See [references/gather.md](references/gather.md).

## 3. Propose perspectives

TODO: propose the stakeholder perspectives that fit the decision. See [references/propose-perspectives.md](references/propose-perspectives.md).

## 4. Verify perspectives

TODO: make sure every selected perspective was fully verified once by a person and is confirmed for this run, then pass the verification gate. See [references/verify-perspectives.md](references/verify-perspectives.md).

## 5. Prioritize

TODO: produce one point distribution per verified perspective, spending exactly the point budget. See [references/prioritize.md](references/prioritize.md).

## 6. Rate

TODO: rate every candidate on every in-scope requirement in a separate pass that sees only the candidates and the requirements, never the perspectives' preferences or points. See [references/rate.md](references/rate.md).

## 7. Validate

TODO: check the responses, the budget totals and the ratings, then apply the elimination threshold to the Must ratings. See [references/validate.md](references/validate.md).

## 8. Compile

TODO: combine priorities and ratings into one trade-off analysis, flagging conclusions that rest mainly on draft requirements. See [references/compile.md](references/compile.md).

## 9. Challenge

TODO: test the compiled analysis for blind spots, divergence and weak conclusions. See [references/challenge.md](references/challenge.md).

## 10. Record

TODO: if the host has a decision-record skill, hand it the compiled and challenged analysis; otherwise produce a decision record from `assets/decision-record-template.md`. See [references/record.md](references/record.md).

## Feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
