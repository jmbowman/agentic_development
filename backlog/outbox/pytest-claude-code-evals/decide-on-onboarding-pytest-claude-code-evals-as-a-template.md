---
title: Decide on onboarding pytest-claude-code-evals as a template consumer
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- surfaced
references:
- copier-python:README.md#Onboarding an existing repo
- docs/high-level-design.md:237-242
- pytest-claude-code-evals:pyproject.toml
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
No repo has been onboarded to copier-python yet, so the HLD's success metrics (zero hand edits per release, first-run green) and several deferred items gated on 'two repos onboarded' can't be measured. pytest-claude-code-evals is a fresh, public, uncommitted `uv init` Python project that agentic_development will depend on: a natural first consumer. Decide whether to onboard it now (it needs LID, a test, the GitHub settings in README steps 8-9, and Renovate installed). Done when the developer says yes or names another first consumer.

**Why it matters:** Gives the template its first real consumer, exercising the update path end to end.

**Why the developer:** chooses a repo's tooling and needs GitHub settings and app installs

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
