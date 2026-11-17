# Step 9: Challenge

Argue the opposing side: make the strongest case against the leading candidate, and test whether the analysis holds. Start after the Compile step ([compile.md](compile.md)).

## Rule

The reviewer works from exactly these inputs, and nothing else:

1. the analysis, `run/analysis.md`;
2. the run record, `run/run.yaml`;
3. the ratings, `run/ratings.yaml`;
4. the responses, `run/responses/`.

The reviewer argues against the result, not for it, and never changes a score, a rating or the scope. Every finding is settled by the user, in one block.

## Sequence

`run/` stands for the run's working folder.

1. **Start one independent subagent for the reviewer** (decision 17), and give it only the four inputs. Record `independence: {challenge: full}` in the run record, next to the other passes.

2. **Make the strongest case against the leading candidate.** If the result is a shortlist, argue against each candidate on it. Then test each of these points, and write a finding for each one that weakens the result:
   - **Drafted requirements:** does the result rest mainly on drafted requirements, those with `origin: assistant` in `gather.drafted_requirements`? Use the drafted share in the analysis (decision 11).
   - **Hypothesis:** if `frame.problem.label` is `hypothesis`, what would the result be worth if the problem turned out not to exist?
   - **At-risk decisions:** would the result change if an at-risk candidate the user kept had been eliminated, or one the user eliminated had been kept (`validate.at_risk`)?
   - **Must challenges after the freeze:** would an accepted `must_challenges` entry in `run/responses/` change the scope enough to change the result?
   - **A close call:** if the analysis reports a close call, could one rating change reverse the order?
   - **Decisive ratings:** does a decisive rating, one the analysis names as carrying the lead, rest on `basis: unread_source` or `basis: judgment`?
   - **Governing decisions and principles:** does the leading candidate conflict with a principle in the shared context, or with a decision the frame names as governing this one?

3. **Write `run/challenge.md`.** Start with the case against the leading candidate, in one paragraph. Then list the findings, numbered:

   ```markdown
   ### 1. The lead rests on one judgment rating
   - point: decisive ratings
   - finding: B leads by 0.8 only through REQ005, rated 9 on judgment.
   - class: execution
   - settled:
   ```

   Classify each finding:
   - `class: execution`: the analysis is built wrong, but the frame holds. Examples: a flag missing from the analysis, a number misreported, or a decisive rating that rests on judgment.
   - `class: premise`: the frame itself may be wrong. Examples: the problem is a hypothesis that does not hold, a missing candidate, or a Must requirement that should not be one.

   If no finding weakens the result, say so, and list the points that were tested.

4. **Let the user settle every finding at once.** Show the case and all findings in one block, and ask the user to accept or reject each one. Write each answer into the finding as `settled: accepted` or `settled: rejected`.
   - **Accepted execution findings:** rerun the Compile step on the current files, then show the findings again, with each one marked as resolved or still open. A finding that needs a different rating goes back to the Rate step through its dispute question; Compile never changes a rating.
   - **Accepted premise findings:** stop, and return to the Frame step as a question for the user. Name the finding and the part of the frame it questions.
   - **Rejected findings:** keep them in `run/challenge.md`. The Record step lists them as deviations.

   Continue to the Record step only when every finding is settled and no accepted finding is still open.

## Output

- `run/challenge.md`: the case against the leading candidate, and every finding with its point, class and settlement.
- `independence.challenge: full` in the run record.

Send `run/challenge.md` and the run record to the user, each as soon as it is written, and again after the findings are settled (see "Delivering files" in `SKILL.md`).
