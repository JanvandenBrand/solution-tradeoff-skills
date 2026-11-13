# Step 2: Gather

Establish what the candidates are judged against. Start only after the user has confirmed the frame ([frame.md](frame.md)).

## Rule

Every count, filter and budget comes from running the scripts, never from calculating in prose. Never state a count, total or budget before the script that produces it has run, not even as an estimate. Keep each script's output as a file in the run's working folder, next to the run record, and quote numbers from those files. Follow the conversation rules of the Frame step. Here the judgment calls, asked one at a time, are the scope (step 4) and each drafted requirement. The inferable facts, the principles (step 8) and the background summaries (step 9), are shown as one block for the user to confirm or edit.

If the host cannot run scripts, say so and stop: this step cannot be done reliably by hand.

## Sequence

Commands run from the skill folder; `<decision>` is `frame.decision_id` from the run record, and `run/` stands for the run's working folder.

1. **Obtain the requirements spreadsheet.** Ask the user for the file. Record only its file name, never its location.

2. **Check the prerequisites.**

   ```bash
   python scripts/check_prerequisites.py <requirements.xlsx> --decision <decision> > run/prerequisites.json
   ```

   If the decision-reference column is missing, the script exits with 1. Show the user the prerequisite flag from the report: without the column, draft requirements cannot be scoped to a decision (decision 7). List the drafts from `drafts_to_choose_from` with their identifiers and descriptions, and ask which belong to this decision. Record the choices; step 5 passes each one with `--include-draft`. Suggest adding the column before the next analysis.

3. **Load the requirements** and show the counts per domain, MoSCoW level and plateau from the `counts` object of the output.

   ```bash
   python scripts/load_requirements.py <requirements.xlsx> > run/requirements.json
   ```

4. **Propose a scope** derived from the frame, and let the user confirm or edit it:
   - **domains**: the domains the decision touches, by the names in the counts (an empty list keeps every domain);
   - **requirement identifiers**: when the domains do not fit the decision, name the requirements by identifier instead, or in addition (a requirement is kept when its domain or its identifier is listed);
   - **highest plateau**: by default `frame.plateau`;
   - **MoSCoW levels**: by default Must and Should.

   Never change categories in the spreadsheet or in a copy of it to make a scope fit. A working copy may only gain new draft rows.

   **Drafted requirements (decision 11).** If the spreadsheet does not cover something the decision needs, you may draft a requirement as a new draft row in a working copy, with the decision identifier in its decision-reference column. For each one you draft:
   - present it on its own, with its MoSCoW level, and state which candidates it may favor;
   - ask the user to approve it, change it or drop it, and wait for the answer before presenting the next; never ask for approval of several at once;
   - record it in `gather.drafted_requirements` with `origin: assistant`.

   Reload the working copy (step 3) after adding rows.

5. **Filter the requirements.**

   ```bash
   python scripts/moscow_filter.py run/requirements.json --decision <decision> \
       [--domain <name> ...] [--requirement <id> ...] [--plateau <n>] [--moscow <level> ...] \
       [--include-draft <id> ...] > run/filtered.json
   ```

   Report the in-scope counts from `scope` (Must, Should, total) and the number of excluded drafts from `excluded_drafts`. If the script reports an unknown domain or requirement identifier, show what it lists and return to step 4.

6. **Check the scope size.** If `scope.exceeds` is true, the in-scope count is above `scope.max_requirements` in the settings (60 by default) and the script printed a warning. Tell the user, propose a narrower scope (fewer domains, a lower plateau, or Must only), and repeat steps 4 to 6 until the user accepts a scope.

7. **Calculate the point budget** from the in-scope total in `scope.count`.

   ```bash
   python scripts/budget.py --count <scope.count> > run/budget.json
   ```

8. **Propose the principles** linked from the in-scope requirements: `principles.linked` in `run/filtered.json`, each with its description. If `principles.unknown` lists references not found in the principles sheet, tell the user. Ask whether to add other principles. Show them in one block with the background summaries from step 9, and ask the user to confirm or edit the block.

9. **Collect background.** Ask for governing documents or other context the perspectives and the rater should know. Summarize each one in a few lines, with its title, and add the summaries to the block from step 8. Do not copy documents into the run record or the shared context.

10. **Summarize and confirm.** Show the scope, the in-scope counts, the excluded drafts (and the drafts the user chose, if any), the budget, the principles and the background summaries. Ask: "Is this what the candidates should be judged against?" Continue only after the user confirms. If the summary shows that the problem, the outcome or the criteria are wrong, return to the Frame step as a question for the user.

## Output

1. The `gather` section of the run record, in the format of `assets/run-record.schema.json`:

   ```yaml
   gather:
     spreadsheet: <file name only>
     included_drafts: []          # drafts chosen with --include-draft
     drafted_requirements:        # requirements drafted in this run, if any
       - id: <identifier>
         origin: assistant        # or user
     scope:
       domains: []                # empty keeps every domain
       plateau: 2
       moscow: [Must, Should]
     outputs:
       requirements: requirements.json
       filtered: filtered.json
       budget: budget.json
     counts:
       must: 0                    # from scope.must in filtered.json
       should: 0                  # from scope.should
       excluded_drafts: 0         # from excluded_drafts.count
     budget: 15                   # from budget.json
     principles: [P01]
     background:
       - title: <document title>
         summary: <a few lines>
     confirmed_by: <the user's name>
     confirmed_at: 2026-11-12
   ```

   Check it against the script outputs and fix every error it reports:

   ```bash
   python scripts/validate_run_record.py run/run.yaml --section gather --requirements run/filtered.json
   ```

2. The **shared context block**, `run/shared-context.md`, filled in from `assets/shared-context-template.md`: the frame summary, the in-scope requirements, the principles and the background. This block is the only input the Prioritize and Rate steps receive. It never contains perspective preferences or points.
