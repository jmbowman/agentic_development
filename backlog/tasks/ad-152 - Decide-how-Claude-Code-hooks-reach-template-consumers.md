---
id: AD-152
title: Decide how Claude Code hooks reach template consumers
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-6
dependencies: []
references:
  - docs/high-level-design.md:216-218
  - docs/high-level-design.md:167
  - README.md:50
  - copier-python:docs/high-level-design.md:106
priority: medium
type: decision
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's HLD says consumers that install the skills package with APM don't get the subagent-notes hooks (APM merges hooks into `.config/<template>/.claude/settings.json`, where Claude Code doesn't look) and that the process-hooks design will settle delivery for both skill hooks and commit gates. Until then consumers add the hook entries by hand from `skills/session-wrap-up/references/subagent-notes-hooks.md`. Decide the delivery route (template-rendered entries in the repo-owned `.claude/settings.json`, APM hook integration, or another), since copier-python's work depends on it. Done when the process-hooks design records it.

**Why it matters:** Unblocks the template delivering subagent-notes hooks and later commit gates.

**Why the developer:** a design decision with rejected alternatives already listed
<!-- SECTION:DESCRIPTION:END -->
