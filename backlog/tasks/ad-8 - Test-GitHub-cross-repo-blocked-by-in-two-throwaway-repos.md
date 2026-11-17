---
id: AD-8
title: Test GitHub cross-repo blocked-by in two throwaway repos
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-1
dependencies: []
references:
  - session:26c85309 2026-11-16
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
priority: medium
type: chore
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The cross-repo coordination note says GitHub's blocked-by links and sub-issues work across repos, but only from docs. Create two throwaway repositories in the developer's account, link an issue in one as blocked by an issue in the other, and record whether the relationship and the API behave as documented. Done when the result is added to the note or its design follow-up.

**Why it matters:** Verifies a claim the cross-repo layer design would rest on.

**Why the developer:** needs repos created in the developer's account
<!-- SECTION:DESCRIPTION:END -->
