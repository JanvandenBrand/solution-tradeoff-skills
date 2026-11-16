# Step 10: Record

Turn the compiled and challenged analysis into a decision record, and deliver the run (decision 10). Start after the Challenge step ([challenge.md](challenge.md)), when every finding is settled.

## Rule

The decision record is a proposal for people to decide on: set its status to Proposed. The skill never sets the status to Accepted; only the people who own the decision do that, outside this run. Everything in the record comes from `run/analysis.md`, `run/challenge.md` and the run record; add no conclusion that is not in them.

## Sequence

`run/` stands for the run's working folder; the run record is `run/run.yaml`.

1. **Write the decision record.**
   - If the host has a decision-record skill, hand it `run/analysis.md`, `run/challenge.md` and `run/run.yaml`, with the items in step 2 and the instruction to set the status to Proposed.
   - Otherwise, fill in `assets/decision-record-template.md`: title, context, decision, status and consequences. Save it as `run/decision-record.md`.

2. **Make sure the record carries these items**, in the consequences unless the template has a better place:
   - **The hypothesis label:** if `frame.problem.label` is `hypothesis`, say so in the context. List the open actions in the consequences: what to observe or measure to confirm the problem, drawn from `frame.problem.outcome` and `frame.problem.causal_claim`, and who should do it, if the user names someone. Until that is done, the decision rests on an unconfirmed problem.
   - **Drafted requirements:** every requirement in `gather.drafted_requirements`, with its identifier and text, for the user to add to the source spreadsheet (decision 11). Also list the requirements an accepted scope-review challenge dropped from the scope (`settled: accepted` in `run/scope-review/`), so the spreadsheet owner can review them; the spreadsheet itself was not changed (decision 13).
   - **At-risk decisions:** each entry in `validate.at_risk`, with the candidate, the decision and who made it.
   - **The deviations:** what departed from the full method in this run:
     - every `independence` value that is `limited`;
     - every rating the user disputed in the Rate step;
     - every challenge finding the user rejected (`settled: rejected` in `run/challenge.md`).

3. **Ask once for the hands-on time.** Ask: "How many minutes of hands-on time did this run take you?" Store the whole number in the run record, and do not ask again:

   ```yaml
   measurement:
     hands_on_minutes: 85
   ```

   If the user does not know, leave the section out and say that the run is not measured.

4. **Deliver the run.** Hand over four files: the decision record, `run/analysis.md`, `run/challenge.md` and `run/run.yaml`. A later run can be resumed from these files (decision 15).
   - If the host can write files in the user's folder, save them there.
   - Otherwise, give them to the user as files to keep.

## Output

- The decision record, with status Proposed: from the host's decision-record skill, or `run/decision-record.md`.
- `measurement.hands_on_minutes` in the run record.
- The four files, delivered to the user.
