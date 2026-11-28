---
id: AD-215
title: Design the process hooks component
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-27T21:44:07Z'
labels:
  - open-question
milestone: m-6
dependencies:
  - AD-140
  - AD-142
  - AD-372
references:
  - docs/high-level-design.md:167
  - README.md#What's in this repo
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HLD components table lists 'Process hooks' (commit gates and other hooks, and how Claude Code hooks reach consumer repos) as planned and not yet designed. Write its LLD through LID; it overlaps the review-wave commit gate and the subagent notes hooks' delivery to APM-installed consumers (which today must add settings by hand). Done when an LLD exists and the components table links it.

**Why it matters:** Gets hooks to consumers that install skills with APM, who currently get none.

**Why an agent:** agent drafts under LID; developer reviews at the stops
<!-- SECTION:DESCRIPTION:END -->
