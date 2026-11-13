# Step 4: Verify perspectives

Make sure a person has fully verified every selected perspective once, and has confirmed it for this run (decision 5). Start with the list of perspectives confirmed in step 3 ([propose-perspectives.md](propose-perspectives.md)).

## Rule

Nothing is scored with a perspective until a person has verified it and confirmed it for this run. You never set a perspective to verified on your own judgment: only the user's answer does. Already-verified perspectives are confirmed together, with one question. Unverified ones are reviewed one at a time, in full. The verification gate decides whether step 5 may start; if it blocks, stop.

## Sequence

`run/` stands for the run's working folder; the run record is `run/run.yaml`.

1. **Confirm the already-verified perspectives together.** Show one line each: `id`, `label`, `verified_by` and `verified_at`. Ask one question: "Are these still correct?" On yes, add one entry per perspective to `perspective_confirmations` in the run record:

   ```yaml
   perspective_confirmations:
     - id: security
       confirmed_by: <the user's name>
       confirmed_at: 2026-11-13     # a date without quotes
   ```

   If the user says a perspective is no longer correct, ask what changed, apply the change to a copy, and treat that copy as unverified (step 2).

2. **Review the unverified perspectives one at a time.** These are the shipped defaults, the new drafts from step 3, and any copy changed in step 1. Show the first one in full: the header and all four sections. Ask the user to accept it, edit it or drop it, and wait for the answer before showing the next one. Never ask about several at once.
   - **Edit:** apply the changes, show the whole perspective again, and ask again.
   - **Drop:** remove it from the selection and say which stakeholder is no longer represented.
   - **Accept:** in a copy of the file, set `verified: true`, `verified_by` to the user's name and `verified_at` to today's date, without quotes. Add its entry to `perspective_confirmations`. Save the copy as `run/perspectives/<id>.md` so the gate uses it in this run. Then hand it to the user's library:
     - if the host can write files in the user's folder (as in Claude Code), save it there as `<id>.md`;
     - otherwise (as in claude.ai), give it to the user as a file named `<id>.md` to add to the project files, so the next run finds it verified.

   Never change the files in `references/perspectives/`: the shipped defaults stay unverified.

3. **Run the verification gate** before step 5, with every selected id. List `run/perspectives` first, then the user's folder:

   ```bash
   python scripts/verification_gate.py --perspective <id> [--perspective <id> ...] \
       --library run/perspectives --library <user's folder> --run-record run/run.yaml > run/gate.json
   ```

   If it exits with 1, stop. Name each blocked perspective and the reason the gate gives on standard error (not found, not valid, not verified, or not confirmed for this run). Resolve it with the user, by reviewing it (step 2), confirming it (step 1) or dropping it, and run the gate again. Do not start step 5 until the gate passes.

## Output

- `perspective_confirmations` in the run record: one entry per selected perspective, with `confirmed_by` and `confirmed_at`.
- `run/perspectives/`: the copies verified in this run, each also handed to the user's library.
- The gate output, kept as `run/gate.json`, listing the file used for each perspective. Step 5 uses exactly those files.
