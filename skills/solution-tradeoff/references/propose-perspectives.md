# Step 3: Propose perspectives

Choose the stakeholder perspectives whose priorities drive the analysis. Start only after the user has confirmed the gather summary ([gather.md](gather.md)).

## Rule

Choosing the perspectives is a judgment, so it happens in the conversation, not in a script. Propose the whole set at once as one block for the user to confirm or edit; do not ask about each perspective separately. Nothing is verified in this step: verification is step 4 ([verify-perspectives.md](verify-perspectives.md)).

## Sequence

1. **Read the user's perspective folder first.** Ask where the user keeps their perspectives: project files, or a folder in their workspace. Read every perspective file there. Then read the shipped defaults in `references/perspectives/`. When both have a file with the same `id`, the user's copy wins: use it and ignore the default. If the user has no folder yet, say so and continue with the defaults.

2. **Propose 4 to 7 perspectives from the frame.** Use the decision question, the problem, the candidates and the constraints in the `frame` section of the run record. Pick the stakeholders whose concerns the candidates would trade off against each other. Show the proposal as one block, one line per perspective:

   ```text
   security        Security Perspective      your copy, verified   Candidate B moves credentials to a new host.
   financial       Financial Perspective     default, unverified   The candidates differ mainly in license and run cost.
   clinical_ops    Clinical Operations       new draft, unverified No perspective covers the ward staff who use the system.
   ```

   Each line gives the `id`, the `label`, which copy is used and whether it is verified, and a one-line reason tied to the frame. Below the block, list the perspectives left out, from the user's folder and from the defaults, by `id` and `label`, so the user can add one back.

3. **Draft a missing stakeholder.** If the decision affects a stakeholder that no available perspective covers, draft one in the format of [perspective-format.md](perspective-format.md) and offer it in the block as "new draft, unverified". The header has `verified: false`, `verified_by: null` and `verified_at: null`; only a person verifies it, in step 4. Before you offer the draft, check it against the format yourself (decision 12): the `id` uses lowercase letters, digits and underscores; the body has Role, Primary concern, Failure mode and Evaluation lens, in that order, each with text; the Role is in the second person; the Evaluation lens has at least one bulleted question.

4. **Ask the user to confirm or edit the block.** The user may add, drop or replace perspectives. Repeat the block after each change until the user confirms it. If fewer than 4 remain, say that the trade-off may miss a stakeholder, and continue if the user confirms.

## Output

- The confirmed list of perspective ids. For each one, note which file is used (the user's copy, a default, or a new draft) and whether it is verified. Step 4 reads this list.
- Each new draft, kept in full in the conversation so step 4 can show it.

The run record gets no new section here: the selection is recorded by the confirmations in step 4 and by the ids passed to the verification gate.
