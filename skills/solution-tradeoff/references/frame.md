# Step 1: Frame

## Purpose

Establish the decision and validate the problem. Nothing else starts until the decision is framed and the user has confirmed the frame summary.

## Conversation rules

- Ask one question at a time. Wait for the answer before asking the next one.
- Offer multiple choice where you can: propose likely answers drawn from what the user has said, plus an option to answer in their own words.
- Do not fill in an answer the user has not given. If something is unknown, record it as unknown and say so in the summary.
- When every field is collected, summarize the frame back to the user and ask for confirmation.

## What to collect

1. **Decision identifier**, for example `AD-012`. Required: the Gather step uses it to choose which draft requirements belong to this decision. If the decision has no identifier yet, ask the user to assign one.
2. **Decision question**: the question the decision answers, in one sentence.
3. **Problem statement**, in three parts:
   - the **outcome** the problem affects;
   - the **causal claim**: how the problem leads to that outcome;
   - the **evidence**: what was observed, what was measured, or what someone who feels the pain has stated. For each piece, note its kind (observed, measured or stated), its source, and a one-line summary.
4. **Candidates**: at least two, genuinely different from each other. Give each an identifier (`A`, `B`, `C` and so on), a short name and a one-line description. Ask explicitly whether the status quo should be one of the candidates, and record that you asked. If two candidates differ only in detail, say so and ask whether to merge them or find a real alternative.
5. **Planning horizon** (how far ahead the decision must hold) and **plateau** (the architecture plateau, a whole number, that the decision targets). The Gather step uses the plateau as the default highest plateau of the requirements in scope.
6. **Governing architecture decisions**: earlier decisions this one must respect, by identifier.
7. **Known constraints**: limits on the solution, such as budget, deadlines, regulation or contracts.

## Problem validation

If the host has a problem-validation skill, hand it the problem statement and use its result. Record the method as `host-skill`.

Otherwise, apply these checks and record the method as `built-in-checks`:

1. **Is the problem stated without naming a solution?** "We have no data platform" names a solution; "Monthly reports arrive four days late" does not. If the statement names a solution, help the user restate it, then check again.
2. **Is the outcome named?** If not, ask which outcome the problem affects.
3. **Is there evidence?** If there is none, label the problem a **hypothesis** and let the user choose:
   - proceed with the problem labeled a hypothesis, so every later step and the final record carry the label; or
   - stop, gather evidence, and return to this step.

Record the result of each check.

## Exit

Show the frame summary: decision identifier and question, problem statement with outcome, causal claim, evidence and label, candidates (marking the status quo), planning horizon and plateau, governing decisions, constraints, and the validation result. Ask: "Is this frame correct?" Continue to the Gather step only after the user confirms. If the user corrects anything, update it and ask again.

## Return rule

Any later step that finds the problem, the outcome or the criteria wrong returns here as a question for the user. A later step never changes the frame itself. Once the user has answered, update the frame, ask for confirmation again, and repeat the steps that depend on what changed.

## Output

The `frame` section of the run record (`run.yaml` in the run's working folder), in the format of `assets/run-record.schema.json`:

```yaml
frame:
  decision_id: AD-012
  decision_question: <one sentence>
  problem:
    statement: <the problem, without a solution>
    outcome: <the outcome affected>
    causal_claim: <how the problem leads to the outcome>
    evidence:
      - kind: measured            # observed, measured or stated
        source: <where it comes from>
        summary: <one line>
    label: evidenced              # hypothesis when there is no evidence
  candidates:
    - id: A
      name: <short name>
      description: <one line>
      status_quo: true
    - id: B
      name: <short name>
      description: <one line>
      status_quo: false
  status_quo_asked: true
  planning_horizon: <for example, three years>
  plateau: 2
  governing_decisions: [AD-004]
  constraints:
    - <constraint>
  validation:
    method: built-in-checks       # or host-skill
    solution_free: true
    outcome_named: true
    evidence_present: true
    notes: <optional>
  confirmed_by: <the user's name>
  confirmed_at: 2026-11-12
```

If the host can run scripts, check the section before moving on and fix every error it reports:

```bash
python scripts/validate_run_record.py run.yaml --section frame
```

If the host cannot run scripts, check the same rules by hand and tell the user the check was not run by the script.
