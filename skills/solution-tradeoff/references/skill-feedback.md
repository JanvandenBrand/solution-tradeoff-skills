# Skill feedback

GitHub issues are public: anyone can read an issue once it is posted. Never include sensitive information, and never post an issue until the user has seen the exact title and body and approved it.

Use this when the user reports that the `solution-tradeoff` skill gave incorrect or outdated guidance, is missing information, or could be improved. This is about the skill (the instructions and scripts), not about the decision being analyzed.

## What not to include

The issue is drafted from the conversation, so remove the following before drafting and describe the problem in general terms instead:

- Decision material: problem statements, candidate names, requirements, principles, scores and background knowledge
- Names of organizations, vendors, projects and people
- Credentials, tokens, secrets and passwords
- Personal data, such as names, email addresses and network addresses
- Internal hostnames and links
- Private code, configuration and logs

## Steps

1. **Ask permission**: ask the user if they would like to submit feedback to the skill maintainers. If they decline, move on.

2. **Draft the issue**: fill in the table below from the conversation and use it as the issue body. Always identify which specific file and section caused the problem. Leave out everything listed in [What not to include](#what-not-to-include).

3. **Review with the user**: show the user the exact title and body, then ask a yes or no question, such as "Post this as a public issue on JanvandenBrand/solution-tradeoff-skills?" Submit only after the user answers yes. If they ask for changes, apply them and ask again. If they answer no, do not post. Agreeing to send feedback in step 1 is not approval of the text.

4. **Submit**: if the host can run the GitHub command-line tool, create the issue on the `JanvandenBrand/solution-tradeoff-skills` repository with the approved draft as the body, for example with `gh issue create --repo JanvandenBrand/solution-tradeoff-skills`. The title must follow this format: `skill-feedback: solution-tradeoff: <summary of the problem>`.

5. **Share the result**: share the issue link with the user after submission. If the host cannot submit issues, or submission fails, give the user the approved title and body, and this link to create the issue manually: <https://github.com/JanvandenBrand/solution-tradeoff-skills/issues/new>

## Issue body

| Field | Value |
|-------|-------|
| Type | `bug` (incorrect guidance), `outdated`, `missing`, or `improvement` |
| Skill | `solution-tradeoff` |
| Source | File and section, for example `SKILL.md` > "Section name" or `references/<file>.md` > "Section name" |
| Agent | The agent and model in use, if known |
| Task | What the user was trying to do, for example "verify a perspective" |
| Expected | What should have happened |
| Actual | What the skill said or what happened |
| Impact | The effect on the user, for example "Time spent correcting the point budget" |
| Suggested fix | How the skill should change; leave blank if unsure |
