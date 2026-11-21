---
title: Build the plugin's first slice of interactive session driving
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- spec
references:
- docs/intent/interactive-evals/interactive-evals-design.md#What the scenarios need from the plugin
- docs/intent/interactive-evals/interactive-evals-design.md:93
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
external_blockers:
- pytest-claude-code-evals/decide-the-credentials-form-for-the-plugin-s-isolated-sessio
- pytest-claude-code-evals/write-pytest-claude-code-evals-hld-and-llds
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the first slice of pytest-claude-code-evals as its design specifies: enough to run one session-wrap-up manual script as a pytest test (several typed turns, scripted question-dialog answers, tool gating and an ordered tool log, repo state at each stop, a judge, caps), and inert for tests that don't use it. Tests first, per LID. Done when a sample scenario passes against a real Claude Code session.

**Why it matters:** Turns unrun manual scripts into repeatable tests.

**Why an agent:** implementation against a reviewed design

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
