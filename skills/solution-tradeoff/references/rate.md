# Step 6: Rate

Rate how well every candidate meets every in-scope requirement, in a pass separate from the perspectives (decision 6). Start after the Prioritize step ([prioritize.md](prioritize.md)).

## Rule

The rater works from exactly these inputs, and nothing else:

1. the shared context block, `run/shared-context.md`: the candidates, the in-scope requirements, the principles and the background;
2. the rating format, `assets/rating.schema.json`;
3. the rating scale, `rating.minimum` to `rating.maximum` in `assets/config.yaml`.

The rater never sees the perspectives' responses, preferred options or point allocations. Ratings that know which candidate a perspective prefers anchor on that preference; this step exists to prevent that.

## Sequence

`run/` stands for the run's working folder; the run record is `run/run.yaml`.

1. **Start one independent subagent for the rater** (decision 17), and give it only the three inputs. Record `independence: {rate: full}` in the run record, next to `prioritize`.

2. **Rate every candidate on every in-scope requirement**, as a whole number on the scale. Write `run/ratings.yaml` in the format of the rating schema:

   ```yaml
   candidates: [A, B]             # the candidate identifiers from the frame
   ratings:
     - candidate: A
       requirement_id: REQ001
       rating: 7
       basis: source
       source: <background title>
       rationale: "<why this rating>"
     - candidate: B
       requirement_id: REQ001
       rating: 4
       basis: judgment
       rationale: "<why this rating>"
     - candidate: B
       requirement_id: REQ002
       rating: 5
       basis: unread_source
       rationale: "<title of the source>, not read in this run: <what it is said to show>"
   ```

   Set `basis` on every rating:
   - `basis: source`: the rating rests on a background document whose content was read in this run and is summarized in the shared context. Set `source` to that background item's title.
   - `basis: unread_source`: the rating rests on a source known only by its title or by a claim about it, not read in this run. Name the source in the rationale.
   - `basis: judgment`: no source covers it; the rating is the rater's judgment.

   Rate a status quo candidate as it is today, not as it could be improved.

3. **Ask one question.** Show the ratings as a table, candidates as columns and requirements as rows, with each basis. Ask: "Do you dispute any rating?" For each dispute, change the rating to the user's correction and keep the trail in its rationale: the original rating, basis and reason, followed by `Disputed by <the user's name>: <reason>.` A corrected rating gets `basis: judgment`, unless the user points to a source that is then read in this run; then it gets `basis: source` and `source` names that background item. A correction by the user is the only way a rating changes outside this pass.

## Output

- `run/ratings.yaml`: every candidate rated on every in-scope requirement, with disputes and corrections in the rationales.
- `independence.rate: full` in the run record.

Send the run record to the user as soon as it is written (see "Delivering files" in `SKILL.md`).
