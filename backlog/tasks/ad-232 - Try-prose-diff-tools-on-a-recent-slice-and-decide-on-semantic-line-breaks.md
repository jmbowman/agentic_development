---
id: AD-232
title: Try prose-diff tools on a recent slice and decide on semantic line breaks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-7
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/91
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #91 prose part: try GitHub's rich diff for PRs, md-diff (markdown-diff-viewer, working tree or index) and git pandiff locally, and `sem diff -v --no-cosmetics` on a few slices; then decide whether design docs adopt semantic line breaks. Judging which reads best is the developer's call, but trying the tools and reporting can be prepared by an agent. Done means a recorded choice on prose diffs and on semantic line breaks.

**Why it matters:** Settles how prose changes get reviewed.

**Why the developer:** preference decision on how docs are written and read
<!-- SECTION:DESCRIPTION:END -->
