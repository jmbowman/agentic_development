---
title: Check whether Claude Code reads .agents/skills so template links can shrink
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:214
- https://github.com/anthropics/claude-code/issues/31005
- docs/high-level-design.md:207-213
priority: medium
type: spike
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python defers dropping its `.claude/skills/` links if Claude Code starts reading `.agents/skills/` (anthropics/claude-code#31005); agentic_development's HLD uses the same two-directory layout. Check the issue's state and current Claude Code docs. If it now reads `.agents/skills/`, open a design change in both repos; otherwise record the date checked. Done when the deferred item carries a current status.

**Why it matters:** Could halve the links every skill release must hand-edit.

**Why an agent:** a read-only check of an external issue and docs

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
