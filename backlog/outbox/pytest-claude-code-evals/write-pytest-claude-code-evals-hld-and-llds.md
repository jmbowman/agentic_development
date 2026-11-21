---
title: Write pytest-claude-code-evals' HLD and LLDs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- spec
references:
- docs/intent/interactive-evals/interactive-evals-design.md#What the scenarios need from the plugin
- docs/high-level-design.md:219-221
- docs/prior-art/2026-11-03-interactive-skill-evals.md:30-55
- pytest-claude-code-evals:src/pytest_claude_code_evals/__init__.py
priority: medium
type: docs
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The plugin repo has only a `uv init` scaffold (placeholder `hello()`, empty README, pyproject description 'Add your description here', all uncommitted). agentic_development's HLD says it is its own project 'with its own design docs'. Bootstrap LID and write its HLD and LLDs covering the needs table in agentic_development's interactive-evals LLD (typed turns, dialog answers, repo state at stops, tool gating and logging, judge, caps, inertness) and the build-on choices from the 2026-11-03 prior-art note (Claude Agent SDK, tui-test). Fill in README and pyproject metadata. Done when the HLD and LLDs pass the developer's LID stops.

**Why it matters:** Everything the IEVAL specs wait on starts here.

**Why an agent:** drafting design docs; the developer reviews each LID stop

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
