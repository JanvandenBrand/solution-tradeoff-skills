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
   - **The decision authority and the domain:** name `frame.decision_authority` as the one who decides, and `frame.domain`, in the context.
   - **The hypothesis label:** if `frame.problem.label` is `hypothesis`, say so in the context: until the problem is confirmed, the decision rests on an unconfirmed problem.
   - **Open actions,** in the consequences. Take them from the frame first: each gap in `frame.gaps` and each open point in `frame.validation.notes` becomes an open action. Only if the frame has none, propose open actions yourself, such as the evidence that would confirm a hypothesis, and label each one "(proposed)", so the reader can tell them from what the user recorded.
   - **Drafted requirements:** every requirement in `gather.drafted_requirements`, with its identifier and text, for the user to add to the source spreadsheet (decision 11). Also list the requirements an accepted scope-review challenge dropped from the scope (`settled: accepted` in `run/scope-review/`), so the spreadsheet owner can review them; the spreadsheet itself was not changed (decision 13).
   - **At-risk decisions:** each entry in `validate.at_risk`, with the candidate, the decision and who made it.
   - **The deviations:** what departed from the full method in this run:
     - every rating the user disputed in the Rate step;
     - every challenge finding the user rejected (`settled: rejected` in `run/challenge.md`).

3. **Ask once for the hands-on time.** Ask: "How many minutes of hands-on time did this run take you?" Store the whole number in the run record, and do not ask again:

   ```yaml
   measurement:
     hands_on_minutes: 85
   ```

   If the user does not know, leave the section out and say that the run is not measured.

4. **Check that the user has the latest version of every file.** Send the decision record and the updated run record now. Then confirm that the user has the latest `run/analysis.md`, `run/challenge.md` and `run/run.yaml`, which earlier steps sent as soon as they were written; send any that changed since. A later run can be resumed from these files (decision 15).

## Output

- The decision record, with status Proposed: from the host's decision-record skill, or `run/decision-record.md`.
- `measurement.hands_on_minutes` in the run record.
- The decision record, the analysis, the challenge and the run record, all with the user in their latest version.

Send the decision record and the run record to the user, each as soon as it is written (see "Delivering files" in `SKILL.md`).
