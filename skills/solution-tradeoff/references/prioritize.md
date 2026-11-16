# Step 5: Prioritize

Each verified perspective decides what matters, by spending the point budget over the in-scope requirements (decision 6). Start only after the Gather summary is confirmed and the scope is frozen ([gather.md](gather.md)).

## Rule

Each perspective works from exactly four inputs, and nothing else:

1. the shared context block, `run/shared-context.md`;
2. its own perspective file, the one listed for its `id` in `run/gate.json`;
3. the point budget, from `run/budget.json`;
4. the response format, `assets/tradeoff-output.schema.json`.

A perspective never sees another perspective's response, preferred option or points. Ask the user nothing during this step: the perspectives speak for themselves, and the user reviews the result in one summary at the end.

## Sequence

`run/` stands for the run's working folder; the run record is `run/run.yaml`.

1. **Choose how to run the perspectives.**
   - If the host can start independent subagents, start one per perspective and give each only the four inputs. Record `independence: {prioritize: full}` in the run record.
   - Otherwise, run the perspectives in turn in this conversation. For each one, work from the four inputs only, as if nothing else had been said; write its response to `run/responses/<id>.yaml` before starting the next, and do not look back at earlier responses. Record `independence: {prioritize: limited}` in the run record, so the Compile and Challenge steps know the perspectives were not fully independent.

2. **Write one response per perspective**, as `run/responses/<id>.yaml`, in the format of the response schema:

   ```yaml
   perspective_id: security
   concerns:                      # up to 5, most important first
     - concern: <what worries this stakeholder>
       risk: <what happens if it is ignored>
       best_candidate: B          # or null
   point_allocations:             # in-scope requirement identifiers only
     - criterion_id: REQ001
       points: 6
       rationale: <why this requirement matters to this stakeholder>
   must_challenges:               # optional
     - req_id: REQ004
       action: challenge          # challenge a Must, or add a missing one
       description: <why>
   preferred_option: B
   preferred_rationale: <one paragraph>
   ```

   The points must add up to exactly the budget; the Validate step checks this, so do not add them up in prose. Always fill in `preferred_rationale`, although the schema allows leaving it out. Points go only to requirements in the shared context.

3. **Summarize once, at the end.** For each perspective, show its top concerns and its preferred option, one or two lines each. Then list every Must challenge, with the perspective that raised it, and say that the Challenge step will weigh them. Do not show the point allocations in the summary.

4. **Record Must challenges for the Challenge step only.** The scope is frozen (decision 13). Never change the scope in this step, and do not ask the user to accept or reject a Must challenge here. The challenges stay in the response files, where the Challenge step reads them. Continue to step 6.

## Output

- `run/responses/<id>.yaml`: one response per selected perspective.
- `independence.prioritize` in the run record: `full` or `limited`.
- The summary shown to the user. The Must challenges stay in the responses, for the Challenge step.
