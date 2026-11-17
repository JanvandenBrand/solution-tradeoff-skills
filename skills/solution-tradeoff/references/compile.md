# Step 8: Compile

Combine the perspectives' points and the separate ratings into one trade-off analysis, `run/analysis.md`. Start after the Validate step ([validate.md](validate.md)), when every check passes and the user has decided on each at-risk candidate.

## Rule

Every number comes from `rank.py`; never compute, round or adjust a score yourself. Ask the user nothing during this step: the Challenge step tests the analysis, and the user settles its findings there. Report what the files say, including what weakens the result.

## Sequence

Commands run from the skill folder; `run/` stands for the run's working folder, and the run record is `run/run.yaml`.

1. **Rank the candidates.**

   ```bash
   python scripts/rank.py run/responses --ratings run/ratings.yaml --elimination run/elimination.json \
       --run-record run/run.yaml --requirements run/filtered.json > run/ranking.json
   ```

   If it exits with 1, show the errors. An at-risk candidate without a decision goes back to the Validate step; any other error goes back to the step that wrote the file.

2. **Write `run/analysis.md`.** Every heading states its point as a sentence, such as "B leads, mainly on deployment from code", not "Results". Write these sections, in this order:

   1. **The result.**
      - If `close_call` is false, recommend the first candidate, with the gap.
      - If `close_call` is true, present a shortlist of the candidates within `compile.close_call` of the first, not a winner, and say that the call is close.
      - If only one candidate is ranked, say so: there is nothing to trade off.
   2. **The ranking.** One table, with candidates as rows in the ranking order: the overall score, one column per perspective with its score, and the drafted share. In each perspective's column, mark the cell of its preferred option (`preferred_option` in `run/responses/<id>.yaml`), so each perspective's score stands next to its preferred option. Below the table, name every perspective whose preferred option is not the candidate it scores highest.
   3. **The eliminated and at-risk candidates.**
      - Each eliminated candidate comes from `run/elimination.json`: the Must requirements, each with its rating, basis and `source` from `run/ratings.yaml`.
      - Each at-risk candidate is listed with the same details and the user's decision from `validate.at_risk`.
   4. **The flags.** List each flag that applies, with the numbers behind it, or say that none applies:
      - **Hypothesis:** `frame.problem.label` is `hypothesis`. The result answers a problem that has no evidence yet.
      - **Drafted requirements:** the drafted share of a ranked candidate, highest first. Name the drafted requirements in `gather.drafted_requirements` (decision 11).
      - **Decisive ratings on unread sources:** every `decisive` entry in `run/ranking.json` where either candidate's rating has basis `unread_source`, with that source.
      - **Must challenges after the freeze:** every `must_challenges` entry in `run/responses/`, with the perspective that raised it. They did not change the scope (decision 13); the Challenge step weighs them.

3. **Show the analysis** to the user in full, and continue to the Challenge step.

## Output

- `run/ranking.json`: the output of `rank.py`.
- `run/analysis.md`: the result, the ranking, the eliminated and at-risk candidates, and the flags. The Challenge and Record steps read it.
