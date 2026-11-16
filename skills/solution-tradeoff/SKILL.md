---
name: solution-tradeoff
description: Compare candidate solutions in a multi-stakeholder trade-off analysis against prioritized requirements. Use when weighing options or preparing a trade-off for an architecture decision.
---

# Solution trade-off analysis

Nothing is scored until a person has verified every selected perspective.

## 1. Frame

Establish the decision and validate the problem, one question at a time, then ask the user to confirm the frame summary. Nothing else starts before that confirmation. Follow [references/frame.md](references/frame.md); its output is the `frame` section of the run record. Any later step that finds the problem, the outcome or the criteria wrong returns here as a question for the user.

## 2. Propose perspectives

Propose 4 to 7 stakeholder perspectives from the frame as one block, each with a one-line reason, and list the ones left out. Read the user's perspective folder before the shipped defaults; on a matching id the user's copy wins. Draft a missing stakeholder, unverified. Follow [references/propose-perspectives.md](references/propose-perspectives.md); its output is the confirmed list of perspectives for step 3.

## 3. Verify perspectives

Confirm the already-verified perspectives together with one question, and review each unverified one in full, one at a time, before a person accepts it. Then run the verification gate; if it blocks, stop and say which perspective is blocked. Gather starts only after the gate passes. Follow [references/verify-perspectives.md](references/verify-perspectives.md); its outputs are `perspective_confirmations` in the run record and the verified copies for the user's library.

## 4. Gather

Establish what the candidates are judged against: check the spreadsheet prerequisites, load and filter the requirements, agree the scope, calculate the point budget, and confirm the principles and background. Every count, filter and budget comes from the scripts, never from prose. Follow [references/gather.md](references/gather.md); its outputs are the `gather` section of the run record and the shared context block, the only input to the Prioritize and Rate steps.

## 5. Prioritize

Each verified perspective spends exactly the point budget over the in-scope requirements, working only from the shared context, its own perspective file, the budget and the response schema. Use independent subagents if the host can start them; otherwise run the perspectives in turn and record limited independence. Ask nothing during the step and summarize at the end. The scope is frozen: Must challenges raised here are recorded for the Challenge step only. Follow [references/prioritize.md](references/prioritize.md); its output is one response file per perspective in `run/responses/`.

## 6. Rate

Rate every candidate on every in-scope requirement in a separate pass that sees only the shared context, never the perspectives' responses, preferred options or points. Every rating sets its basis (a source read in this run, the rater's judgment, or an unread source); end with one question about disputed ratings. Follow [references/rate.md](references/rate.md); its output is `run/ratings.yaml`.

## 7. Validate

Run the response, budget and rating checks, then elimination on the Must ratings. A failed check sends the file back to the step that produced it; never fix numbers by hand. Report the eliminated candidates and the Must requirements that eliminated them. Follow [references/validate.md](references/validate.md); its output is `run/elimination.json`.

## 8. Compile

TODO: combine priorities and ratings into one trade-off analysis, flagging conclusions that rest mainly on draft requirements. See [references/compile.md](references/compile.md).

## 9. Challenge

TODO: test the compiled analysis for blind spots, divergence and weak conclusions. See [references/challenge.md](references/challenge.md).

## 10. Record

TODO: if the host has a decision-record skill, hand it the compiled and challenged analysis; otherwise produce a decision record from `assets/decision-record-template.md`. See [references/record.md](references/record.md).

## Feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
