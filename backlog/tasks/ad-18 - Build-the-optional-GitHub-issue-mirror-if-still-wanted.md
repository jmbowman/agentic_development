---
id: AD-18
title: Build the optional GitHub issue mirror if still wanted
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-14
  - AD-271
  - AD-298
references:
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md#Verdict
priority: low
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: human
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Step 4: if the mirror is still wanted after the maintainer answers, build it on meta-fetch's design (watermark moves only on a complete run, resumable sync, rate-limit budget, generated indexes by label, milestone and state, deterministic output), plus jira-local's overlap window and truncated-comment detection, conditional requests with a body-hash fallback, and a periodic full reconcile because deleted or transferred issues never appear in a `since` listing.

This is a pull mirror of issues into local files; tasks are not pushed to GitHub (task-tracker LLD, decided 2026-11-19). The developer keeps it on record, low in the queue, for spotting new issues and comments, and for inspecting other repos' issue data offline. If built, it may answer the task tool's GitHub lookup for the repos it mirrors.

**Why it matters:** Gives agents an indexed local view of GitHub issues.

**Why an agent:** build through LID
<!-- SECTION:DESCRIPTION:END -->
