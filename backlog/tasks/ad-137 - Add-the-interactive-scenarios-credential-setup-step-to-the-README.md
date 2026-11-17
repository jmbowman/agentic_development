---
id: AD-137
title: Add the interactive scenarios' credential setup step to the README
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-5
dependencies: []
references:
  - docs/intent/interactive-evals/interactive-evals-design.md:94
  - README.md#What's in this repo
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
external_blockers:
- pytest-claude-code-evals/decide-the-credentials-form-for-the-plugin-s-isolated-sessio
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once pytest-claude-code-evals settles how its isolated config logs in, add the setup step to this repo's `README.md` (Developing this repo section), and update the `scripts/` row, which still calls the interactive scenarios 'still to come', once scenarios exist. Done when a new contributor can run a scenario from the README alone.

**Why it matters:** Removes a setup blocker for running scenarios.

**Why an agent:** a docs edit once the decision exists
<!-- SECTION:DESCRIPTION:END -->
