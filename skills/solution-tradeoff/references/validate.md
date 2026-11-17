# Step 7: Validate

Check the responses and the ratings with the scripts, then eliminate the candidates that fail a Must requirement. Start after the Rate step ([rate.md](rate.md)).

## Rule

Every check is a script; report what the scripts print, never your own count or total. Never fix numbers by hand: a file that fails a check goes back to the step that produced it, and that step writes it again. If the host cannot run scripts, say so and stop.

## Sequence

Commands run from the skill folder; `run/` stands for the run's working folder. Run them in this order, and run all of them again after any file is regenerated.

1. **Response format.**

   ```bash
   python scripts/validate_response.py run/responses
   ```

2. **Point budget.** Every response spends exactly the budget for the in-scope requirements.

   ```bash
   python scripts/check_budget.py run/responses --requirements run/filtered.json
   ```

3. **Ratings.** The rating file has the right format, uses the configured scale, and rates every candidate on every in-scope requirement.

   ```bash
   python scripts/validate_rating.py run/ratings.yaml --requirements run/filtered.json
   ```

4. **Elimination.** A candidate rated below the threshold on a Must requirement is eliminated when that rating has `basis: source`; when it rests on judgment or an unread source, the candidate is at risk instead (decision 14).

   ```bash
   python scripts/elimination.py run/ratings.yaml --requirements run/filtered.json > run/elimination.json
   ```

**When a check fails** (exit code 1), show the errors it prints and send the file back:

- a response that fails step 1 or 2 goes back to step 5 ([prioritize.md](prioritize.md)), for that perspective only, with its four inputs and nothing else;
- the rating file goes back to step 6 ([rate.md](rate.md)), which rates again from its own inputs.

Do not edit the points or the ratings yourself, and do not ask the user to. A rating the user corrected in step 6 stays as corrected.

**Report the result** from `run/elimination.json`: the threshold, each eliminated candidate with the Must requirements that eliminated it (identifier and description, from `run/filtered.json`) and, for each, the rating's `source` from `run/ratings.yaml`, and the remaining candidates.

**Let the user decide on the at-risk candidates.** If `at_risk` lists any candidate, show them in one block: per candidate, each failing Must requirement with its identifier, description, rating and basis, its `source` when the rating has one, and the rationale. Ask the user, for each candidate, whether to keep it or eliminate it. Record each answer in the run record:

```yaml
validate:
  at_risk:
    - candidate: B
      decision: keep               # or eliminate
      confirmed_by: <the user's name>
      confirmed_at: 2026-11-16     # a date without quotes
```

A kept candidate continues to the Compile step marked at risk; an eliminated one is reported as eliminated by the user, not by the script.

If every candidate is eliminated, by the script or by the user, say so and return to the Frame step as a question for the user: the candidates, the Must requirements or the threshold may be wrong.

## Output

- Every check passing, on the current files.
- `run/elimination.json`: the threshold, the eliminated and the at-risk candidates with their Must requirements and bases, and the remaining candidates. The Compile step reads it.
- `validate.at_risk` in the run record: the user's decision on each at-risk candidate.

Send the run record to the user as soon as it is written, with the at-risk decisions (see "Delivering files" in `SKILL.md`).
