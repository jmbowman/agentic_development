---
id: AD-248
title: Evaluate hunk and lazydiff for showing agent-edit annotations
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-7
dependencies: []
references:
  - docs/prior-art/2026-10-30-change-presentation.md#Verdict
  - docs/prior-art/2026-10-30-change-presentation.md#Scope of existing projects
priority: low
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The intent layer would emit annotations that an existing viewer shows. hunk (MIT) and lazydiff (MIT, alpha) both display agent annotations; the note says which fits is not yet evaluated. Run each read-only against a sample slice and compare annotation support, Markdown handling, staging and accessibility (ANSI palette). Done when a short comparison names the viewer to target, or none.

**Why it matters:** Chooses the display target before the intent layer is designed.

**Why an agent:** Read and try two small tools
<!-- SECTION:DESCRIPTION:END -->
