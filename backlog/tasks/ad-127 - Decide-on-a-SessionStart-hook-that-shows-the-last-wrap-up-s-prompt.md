---
id: AD-127
title: Decide on a SessionStart hook that shows the last wrap-up's prompt
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/session-wrap-up/session-wrap-up-design.md:332-333
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The session-wrap-up design defers a `SessionStart` hook that surfaces the last wrap-up's next-session prompt, and triage across every project's memory at once. Decide whether to take either up. Done when each is moved into a slice plan or kept deferred with a reason.

**Why it matters:** Would close the loop between a wrap-up and the next session start.

**Why the developer:** scope decision
<!-- SECTION:DESCRIPTION:END -->
