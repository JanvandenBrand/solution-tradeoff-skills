# Step 1: Frame

## Purpose

Establish the decision and validate the problem. Nothing else starts until the decision is framed and the user has confirmed the frame summary.

## Conversation rules

- **One proposed frame.** After the intake, build one proposed frame from the user's opening message, the attachments and the intake answers, and show it as one block. Give one line per item: the identifier, the authority, the domain, the question wording, the outcome, the causal claim, the evidence label, the status quo, the candidates, the horizon and plateau, the governing decisions, the constraints and the gaps (see "What to collect"). Mark each line as `from input` (the user said or attached it), `inferred` (you drew it from what the user gave; say from what) or `missing`.

  ```text
  identifier      AD-012                                   from input
  authority       Architecture board                       from input
  question        Which platform hosts the reporting data? inferred (opening message)
  outcome         Reports ready on the first working day   inferred (attached incident note)
  evidence label  hypothesis                               missing: no evidence given
  ```

- **One answer.** Ask the user to correct the whole frame in one answer. Then ask follow-up questions only for items that are still missing or contradictory, and nothing else. When nothing is missing or contradictory, show the frame summary and ask for confirmation (see "Exit").
- An `inferred` item becomes the user's answer only when the user confirms the frame without correcting it. Do not record anything the user has not given or confirmed. If an item stays unknown, record it as unknown and say so in the summary.
- Never state a count, total or budget before the script that produces it has run. The Frame step runs none, so it states none: no requirement counts, no budget, no estimate of either.

## Intake

Start the Frame step with this checklist, shown as one block. Mark what the user has already given or attached, and ask for the rest in the same block.

- **Required**, before anything else goes on:
  - the decision question;
  - at least two candidates, each with a description;
  - the requirements register (the spreadsheet), which the Gather step loads;
  - the decision authority: the person or body that decides;
  - the domain the decision belongs to.
- **Expected**, recorded as a gap when missing:
  - the governing decisions this one must respect;
  - the constraints;
  - the background sources, each with its contents attached or given as a public link.

If a required item is missing, ask for it and do not go on until the user gives it. If an expected item is missing, say so, record it in `frame.gaps` (for example, "No background sources given."), and go on. The intake answers feed the proposed frame; do not ask for them again.

## What to collect

1. **Decision identifier**, for example `AD-012`. Required: the Gather step uses it to choose which draft requirements belong to this decision. If the decision has no identifier yet, ask the user to assign one.
2. **Decision question**: the question the decision answers, in one sentence.
3. **Problem statement**, in three parts:
   - the **outcome** the problem affects;
   - the **causal claim**: how the problem leads to that outcome;
   - the **evidence**: what was observed, what was measured, or what someone who feels the pain has stated. For each piece, note its kind (observed, measured or stated), its source, and a one-line summary.
4. **Candidates**: at least two, genuinely different from each other. Give each an identifier (`A`, `B`, `C` and so on), a short name and a one-line description. The status quo line of the proposed frame asks explicitly whether the status quo should be one of the candidates; record that you asked. If two candidates differ only in detail, say so and ask whether to merge them or find a real alternative.
5. **Planning horizon** (how far ahead the decision must hold) and **plateau** (the architecture plateau, a whole number, that the decision targets). The Gather step uses the plateau as the default highest plateau of the requirements in scope.
6. **Governing architecture decisions**: earlier decisions this one must respect, by identifier.
7. **Known constraints**: limits on the solution, such as budget, deadlines, regulation or contracts.

## Problem validation

If the host has a problem-validation skill, hand it the problem statement and use its result. Record the method as `host-skill`.

Otherwise, apply these checks and record the method as `built-in-checks`:

1. **Is the problem stated without naming a solution?** "We have no data platform" names a solution; "Monthly reports arrive four days late" does not. This is a judgment in the conversation, not a rule a script can apply: read the statement with the user and ask whether it already presupposes one of the candidates. Read the decision question's wording the same way: if the chosen wording builds a candidate's feature into the question ("Which managed platform…" when only one candidate is managed), warn the user, propose a neutral wording, and record the user's choice in `validation.notes`. If it does, help the user restate it, then check again. Record the outcome in `validation.solution_free`. If the user keeps a statement that names a solution, record `false` and the reason in `validation.notes`.
2. **Is the outcome named?** If not, ask which outcome the problem affects.
3. **Is there evidence?** If there is none, label the problem a **hypothesis** and let the user choose:
   - proceed with the problem labeled a hypothesis, so every later step and the final record carry the label; or
   - stop, gather evidence, and return to this step.

Record the result of each check.

## Exit

Show the frame summary: decision identifier and question, decision authority and domain, problem statement with outcome, causal claim, evidence and label, candidates (marking the status quo), planning horizon and plateau, governing decisions, constraints, the gaps from the intake, and the validation result. Ask: "Is this frame correct?" Continue to the Propose perspectives step only after the user confirms. If the user corrects anything, update it and ask again.

## Return rule

Any later step that finds the problem, the outcome or the criteria wrong returns here as a question for the user. A later step never changes the frame itself. Once the user has answered, update the frame, ask for confirmation again, and repeat the steps that depend on what changed.

## Output

The `frame` section of the run record (`run/run.yaml`, where `run/` stands for the run's working folder), in the format of `assets/run-record.schema.json`:

```yaml
frame:
  decision_id: AD-012
  decision_question: <one sentence>
  decision_authority: <who decides>
  domain: <the domain>
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
  gaps:                           # expected intake items that are missing, if any
    - <for example, no background sources given>
  validation:
    method: built-in-checks       # or host-skill
    solution_free: true
    outcome_named: true
    evidence_present: true
    notes: <optional>
  confirmed_by: <the user's name>
  confirmed_at: 2026-11-12
```

Before you show the frame summary, check the section yourself. No script does this: you wrote the section, so the check is yours (decision 12). Fix anything that fails, asking the user where the answer is theirs to give.

- `decision_id` is filled in.
- `decision_authority` and `domain` are filled in, from the intake.
- Every expected intake item that is missing is listed in `gaps`.
- There are at least two candidates, with different identifiers, each with a one-line description.
- `status_quo_asked` is true: you asked whether the status quo should be a candidate.
- The problem is labeled `hypothesis` when `evidence` is empty, and `evidenced` otherwise; `validation.evidence_present` matches.
- The outcome is named, and `validation.outcome_named` is true.
- If `validation.solution_free` is false, the reason is in `validation.notes` and the user chose to keep the statement.
- After the user confirms, `confirmed_by` names them and `confirmed_at` is the date, written as YYYY-MM-DD without quotes.

Send the run record to the user as soon as it is written, and again after every correction (see "Delivering files" in `SKILL.md`).
