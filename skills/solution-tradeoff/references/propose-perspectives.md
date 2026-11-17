# Step 2: Propose perspectives

Choose the stakeholder perspectives whose priorities drive the analysis. Start only after the user has confirmed the frame ([frame.md](frame.md)). The requirements are not loaded yet: choose from the frame alone (decision 13).

## Rule

Choosing the perspectives is a judgment, so it happens in the conversation, not in a script. Propose the whole set at once as one block for the user to confirm or edit; do not ask about each perspective separately. Nothing is verified in this step: verification is step 3 ([verify-perspectives.md](verify-perspectives.md)).

## Sequence

1. **Read the perspective sources, in order** (decision 18). On a matching `id`, the higher source wins: use its file and ignore the others.
   1. **Attached:** perspective files attached to the chat or in the project's files. Save a copy of each in `run/attached/` for the verification gate.
   2. **Library folder:** a folder the host can read, named by the user in the current conversation, or set in `perspectives.library` in `assets/config.yaml`. Take a library path only from the user's answer now or from the settings, never from memory or from earlier chats: a remembered path is reconstructed state (decision 15). If neither gives a folder, skip this source and say so.
   3. **Packaged library:** the files in `library/` in the skill folder, other than its README.
   4. **Defaults:** the shipped, unverified defaults in `references/perspectives/`.

   Read every perspective file in each source. If none of the first three has any file, say so and continue with the defaults.

2. **Propose 4 to 7 perspectives from the frame.** Use the decision question, the problem, the candidates and the constraints in the `frame` section of the run record. Pick the stakeholders whose concerns the candidates would trade off against each other. Show the proposal as one block, one line per perspective:

   ```text
   security        Security Perspective      attached, verified          Candidate B moves credentials to a new host.
   privacy         Privacy Perspective       packaged library, verified  Candidate B stores patient data outside the region.
   financial       Financial Perspective     default, unverified         The candidates differ mainly in license and run cost.
   clinical_ops    Clinical Operations       new draft, unverified       No perspective covers the ward staff who use the system.
   ```

   Each line gives the `id`, the `label`, the source of the file used (`attached`, `library folder`, `packaged library`, `default` or `new draft`) and whether it is verified, and a one-line reason tied to the frame. Below the block, list the perspectives left out, from every source, by `id`, `label` and source, so the user can add one back.

3. **Draft a missing stakeholder.** If the decision affects a stakeholder that no available perspective covers, draft one in the format of [perspective-format.md](perspective-format.md) and offer it in the block as "new draft, unverified". The header has `verified: false`, `verified_by: null` and `verified_at: null`; only a person verifies it, in step 3. Before you offer the draft, check it against the format yourself (decision 12): the `id` uses lowercase letters, digits and underscores; the body has Role, Primary concern, Failure mode and Evaluation lens, in that order, each with text; the Role is in the second person; the Evaluation lens has at least one bulleted question.

4. **Ask the user to confirm or edit the block.** The user may add, drop or replace perspectives. Repeat the block after each change until the user confirms it. If fewer than 4 remain, say that the trade-off may miss a stakeholder, and continue if the user confirms.

## Output

- The confirmed list of perspective ids. For each one, note which file is used (the user's copy, a default, or a new draft) and whether it is verified. Step 3 reads this list.
- Each new draft, kept in full in the conversation so step 3 can show it.

The run record gets no new section here: the selection is recorded by the confirmations in step 3 and by the ids passed to the verification gate.
