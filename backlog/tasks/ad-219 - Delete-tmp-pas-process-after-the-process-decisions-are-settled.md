---
id: AD-219
title: Delete tmp/pas-process after the process decisions are settled
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-6
dependencies:
  - AD-140
references:
  - session:4c452121 2026-11-11
priority: low
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
tmp/pas-process/ (about 1 GB of source clones and records from the #98 search) is kept so source reads can be reused while the nine synthesis decisions are worked through. Delete it, keeping nothing the notes need, once those decisions are settled. Also check tmp/ for other stale scratch (prior-art-157, pas-km, pas-rc).

**Why it matters:** Frees about 1 GB of disk.

**Why an agent:** a gitignored cleanup once the decision is made
<!-- SECTION:DESCRIPTION:END -->
