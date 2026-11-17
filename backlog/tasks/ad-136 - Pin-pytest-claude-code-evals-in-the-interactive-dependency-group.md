---
id: AD-136
title: Pin pytest-claude-code-evals in the interactive dependency group
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-5
dependencies:
  - AD-132
references:
  - docs/intent/interactive-evals/interactive-evals-specs.md:25-28
  - IEVAL-DEP-001
  - IEVAL-DEP-002
  - docs/intent/interactive-evals/interactive-evals-specs.md:27-28
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add pytest-claude-code-evals to `pyproject.toml` under `[dependency-groups]` in exactly one group, `interactive`, pinned to one exact release or git commit and not under `[project]` (IEVAL-DEP-001), and make the `check` task's dependency install include that group (IEVAL-DEP-002). Add or extend structure tests for both specs. Done when `mise run check` installs the plugin and passes, and both specs are marked `[x]`.

**Why it matters:** Prerequisite for writing and type-checking any scenario.

**Why an agent:** a config and test change once the pin form is chosen

**Also waits on (not tracked as a task):** pytest-claude-code-evals first slice usable
<!-- SECTION:DESCRIPTION:END -->
