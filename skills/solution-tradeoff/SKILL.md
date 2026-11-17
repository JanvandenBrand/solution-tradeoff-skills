---
name: solution-tradeoff
description: Compare candidate solutions in a multi-stakeholder trade-off analysis against prioritized requirements. Use when weighing options or preparing a trade-off for an architecture decision.
---

# Solution trade-off analysis

Nothing is scored until a person has verified every selected perspective.

## Before you start

Check that the host can run the scripts, from the skill folder:

```bash
python scripts/validate_rating.py --help
```

It needs Python with `pyyaml` and `jsonschema`, as every script does. If the host cannot run commands, or the command fails, say so and stop. Do not run any step by hand: the counts, budget, elimination and ranking must come from the scripts (decision 3).

## 1. Frame

Establish the decision and validate the problem, one question at a time, then ask the user to confirm the frame summary. Nothing else starts before that confirmation. The Frame step covers verifying intent: its intake, its one-question-at-a-time conversation and the confirmed summary establish what the user wants decided, so the skill does not call a separate intent-verification skill. Follow [references/frame.md](references/frame.md); its output is the `frame` section of the run record. Any later step that finds the problem, the outcome or the criteria wrong returns here as a question for the user.

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

Run the response, budget and rating checks, then elimination on the Must ratings. A failed check sends the file back to the step that produced it; never fix numbers by hand. Report the eliminated candidates and the Must requirements that eliminated them, and let the user decide, in one block, on the candidates marked at risk by judgment-based ratings. Follow [references/validate.md](references/validate.md); its output is `run/elimination.json`.

## 8. Compile

Rank the candidates with `rank.py`: per perspective, points times rating over the budget, and the mean across perspectives. Write the analysis with headings that state the point: the result (a recommendation, or a shortlist when the gap is a close call), the ranking with each perspective's preferred option, the eliminated and at-risk candidates, and the flags (hypothesis, drafted requirements, limited independence, decisive ratings on unread sources, Must challenges after the freeze). Ask nothing during the step. Follow [references/compile.md](references/compile.md); its output is `run/analysis.md`.

## 9. Challenge

Argue the opposing side in an independent subagent if the host can start one; otherwise in this conversation, and record limited independence. Make the strongest case against the leading candidate, and test drafted requirements, the hypothesis label, at-risk decisions, Must challenges after the freeze, a close call, decisive ratings on unread sources or judgment, and conflicts with governing decisions or principles. Classify each finding as execution or premise, and let the user settle all of them in one block: an accepted execution finding reruns Compile, and an accepted premise finding returns to Frame. Follow [references/challenge.md](references/challenge.md); its output is `run/challenge.md`.

## 10. Record

If the host has a decision-record skill, hand it the analysis, the challenge and the run record; otherwise fill in `assets/decision-record-template.md`. The status is Proposed, never Accepted. The record carries the hypothesis label and open actions, the drafted requirements for the source spreadsheet, the at-risk decisions and the deviations. Ask once for the user's hands-on minutes, then deliver the decision record, the analysis, the challenge and the run record. Follow [references/record.md](references/record.md).

## Resuming a run

A run resumes only from its own record (decision 15): the run record `run/run.yaml`, the shared context `run/shared-context.md` and the working copy of the spreadsheet. Ask the user for them, then check the record:

```bash
python scripts/validate_run_record.py run/run.yaml
```

Add `--section gather --requirements run/filtered.json` when the record has a gather section. Fix nothing by hand: if a check fails, show the errors and ask the user how to proceed. Then resume at the first unfinished step: the first step whose run record section or output file is missing, or whose confirmation is null.

You never write a confirmation taken from a transcript or from memory, or from a summary of either; only the user's answer in this conversation is a confirmation. If you rebuild any part of the state from anything other than those three files, set every `confirmed_by` and `confirmed_at` in the run record to null, show the sections in one block, and ask the user to confirm each one again before you continue.

## Feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
