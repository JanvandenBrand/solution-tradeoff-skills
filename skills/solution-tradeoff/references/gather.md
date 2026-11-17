# Step 4: Gather

Establish what the candidates are judged against. Start only after the frame is confirmed ([frame.md](frame.md)) and the verification gate has passed ([verify-perspectives.md](verify-perspectives.md)).

## Rule

Every count, filter and budget comes from running the scripts, never from calculating in prose. Never state a count, total or budget before the script that produces it has run, not even as an estimate. Keep each script's output as a file in the run's working folder, next to the run record, and quote numbers from those files. Follow the conversation rules of the Frame step. Here the judgment calls, asked one at a time, are the scope (step 4) and each drafted requirement. The inferable facts, the principles (step 10) and the background summaries (step 11), are shown as one block for the user to confirm or edit.

The perspectives review the scope once, before the budget is set (step 7), and the user settles their challenges once (step 8). When the user confirms the summary (step 12), the scope is frozen (decision 13). No later step adds or changes requirements.

If the host cannot run scripts, say so and stop: this step cannot be done reliably by hand.

## Sequence

Commands run from the skill folder; `<decision>` is `frame.decision_id` from the run record, and `run/` stands for the run's working folder.

1. **Obtain the requirements spreadsheet.** Use the requirements register the user gave in the Frame intake; ask for the file only if it is not available. Record only its file name, never its location.

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

7. **Review the scope with the perspectives.** Each verified perspective, using the file listed for it in `run/gate.json`, reviews the proposed scope and returns only Must challenges. It receives the frame summary, the in-scope requirements from `run/filtered.json` (identifier, description and MoSCoW level) and its own perspective file, and nothing else. If the host can start independent subagents, give each perspective its own; otherwise review them in turn, each from those inputs only. Record `independence: {scope_review: full}` or `independence: {scope_review: limited}` in the run record, so the Challenge step knows whether the review was independent. Each one writes `run/scope-review/<id>.yaml` with a `must_challenges` list in the format of `assets/tradeoff-output.schema.json`: `req_id`, `action` (`challenge` a Must, or `add` a missing one) and `description`. An empty list is a valid answer.

8. **Settle the challenges once.** Show every challenge in one block, grouped by requirement, with the perspectives that raised it. The user settles them once, accepting or rejecting each; mark each entry in its review file with `settled: accepted` or `settled: rejected`.
   - An accepted `challenge` drops the requirement from the scope. Never change its category in the spreadsheet or a copy: list every requirement that stays in `scope.requirements`, clear `scope.domains`, and run step 5 again with `--requirement` for each. The Record step lists the accepted challenges as changes for the spreadsheet owner.
   - An accepted `add` is a drafted requirement under decision 11: present it on its own, with the candidates it may favor, and wait for approval before the next one (step 4).

   Run steps 5 and 6 again if the scope changed. Do not review the scope with the perspectives a second time.

9. **Calculate the point budget** from the in-scope total in `scope.count`.

   ```bash
   python scripts/budget.py --count <scope.count> > run/budget.json
   ```

10. **Propose the principles** linked from the in-scope requirements: `principles.linked` in `run/filtered.json`, each with its description. If `principles.unknown` lists references not found in the principles sheet, tell the user. Ask whether to add other principles. Show them in one block with the background summaries from step 11, and ask the user to confirm or edit the block.

11. **Collect background.** Start from the background sources listed in the Frame intake, and ask whether there are other governing documents or context the perspectives and the rater should know. Then, for each source (decision 16):
    - **Public**, such as a public repository or published documentation: if the host can fetch web content, read it yourself, as far as the decision needs. If it cannot, ask the user to attach it.
    - **Private or unpublished**: Never fetch private or unpublished material, even when you have its address; ask the user to attach it.
    - Never send user material to an external service: fetch only public addresses, and put nothing from the run into a request.

    Summarize each source in a few lines, with its title, and record what you read and how far: `depth: full` (read in full), `depth: partial` (only the parts named in `read`) or `depth: title_only` (not read; known only by its title or a claim about it). A rating that rests on a `title_only` source has basis `unread_source`. Add the summaries to the block from step 10, with the depth of each. Do not copy documents into the run record or the shared context.

12. **Summarize, confirm and freeze.** Show the scope, the in-scope counts, the excluded drafts (and the drafts the user chose, if any), the settled challenges, the budget, the principles and the background summaries. Ask: "Is this what the candidates should be judged against?" Continue only after the user confirms. With that confirmation the scope is frozen: no later step adds or changes requirements, and Must challenges raised in the Prioritize step are recorded for the Challenge step only. If the summary shows that the problem, the outcome or the criteria are wrong, return to the Frame step as a question for the user.

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
       requirements: []           # identifiers passed with --requirement
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
         link: <public address>   # leave out for attached material
         read: <what was read>
         depth: full              # full, partial or title_only
     confirmed_by: <the user's name>
     confirmed_at: 2026-11-12
   ```

   Check it against the script outputs and fix every error it reports:

   ```bash
   python scripts/validate_run_record.py run/run.yaml --section gather --requirements run/filtered.json
   ```

2. `independence.scope_review` in the run record: `full` or `limited`.

3. The **shared context block**, `run/shared-context.md`, filled in from `assets/shared-context-template.md`: the frame summary, the in-scope requirements, the principles and the background. This block is the only input the Prioritize and Rate steps receive. It never contains perspective preferences or points.
