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

4. **Elimination.** A candidate rated below the threshold on any Must requirement is eliminated.

   ```bash
   python scripts/elimination.py run/ratings.yaml --requirements run/filtered.json > run/elimination.json
   ```

**When a check fails** (exit code 1), show the errors it prints and send the file back:

- a response that fails step 1 or 2 goes back to step 5 ([prioritize.md](prioritize.md)), for that perspective only, with its four inputs and nothing else;
- the rating file goes back to step 6 ([rate.md](rate.md)), which rates again from its own inputs.

Do not edit the points or the ratings yourself, and do not ask the user to. A rating the user corrected in step 6 stays as corrected.

**Report the result** from `run/elimination.json`: the threshold, each eliminated candidate with the Must requirements that eliminated it (identifier and description, from `run/filtered.json`), and the remaining candidates. If every candidate is eliminated, say so and return to the Frame step as a question for the user: the candidates, the Must requirements or the threshold may be wrong.

## Output

- Every check passing, on the current files.
- `run/elimination.json`: the threshold, the eliminated candidates with their Must requirements, and the remaining candidates. The Compile step reads it.
