---
title: Render copier-python into pytest-claude-code-evals
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- surfaced
references:
- copier-python:README.md:23-60
priority: medium
type: chore
performer: agent
agent_tier: moderate
effort: M
external_blockers:
- pytest-claude-code-evals/decide-on-onboarding-pytest-claude-code-evals-as-a-template
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow copier-python's README onboarding steps 1-7 in pytest-claude-code-evals: `copier copy --vcs-ref <latest tag>`, `mise trust`, `mise run setup`, `/update-lid` to bootstrap LID, `mise run fix`, an optional `mise lock`, and `mise run check` until green, then draft `commit-message.md`. Record any friction as copier-python feedback. Done when `mise run check` passes; the developer commits and does the GitHub settings steps.

**Why it matters:** First-run-green evidence for the template, and a strict baseline for the plugin.

**Why an agent:** scripted onboarding steps

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
