---
id: AD-4
title: Decide where cross-repo and personal tasks live
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-1
dependencies: []
references:
  - docs/task-tracking-pilot.md
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This repo is public, so tasks for private repos, the cross-repo ranking and personal to-dos can't live here. Options: a private coordination repo holding a `backlog/` in the same format plus the list of repo backlogs to read (the cross-repo note's decision 5 recommendation); or per-repo backlogs only, with personal tasks in a private repo's own `backlog/`. The pilot keeps private drafts in the gitignored `backlog/private/`. Done when the location is chosen and noted in this task; the task tracker's design records it when LID's arrow is walked (AD-5).

**Why it matters:** Unblocks the portfolio view, the personal-task trial and delivery of private drafts.
<!-- SECTION:DESCRIPTION:END -->
