---
title: Revisit template-provided AGENTS.md fragments at the second consumer
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:209
- copier-python:docs/high-level-design.md:38
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python renders no instruction file (LID's `/update-lid` owns it) and defers template-owned `AGENTS.md` fragments until a second consumer exists. Several agentic_development working rules (commit-message drafting, README re-read, public-content rule) are repeated by hand in each tooling repo's AGENTS.md. Decide whether to provide fragments when the trigger fires. Done when the deferred item is decided.

**Why it matters:** Would stop working rules drifting between repos.

**Why the developer:** a design direction choice

**Also waits on (not tracked as a task):** A second template consumer exists

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
