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
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Step 4: if the mirror is still wanted after the maintainer answers, build it on meta-fetch's design (watermark moves only on a complete run, resumable sync, rate-limit budget, generated indexes by label, milestone and state, deterministic output), plus jira-local's overlap window and truncated-comment detection, conditional requests with a body-hash fallback, and a periodic full reconcile because deleted or transferred issues never appear in a `since` listing.

**Why it matters:** Gives agents an indexed local view of GitHub issues.

**Why an agent:** build through LID
<!-- SECTION:DESCRIPTION:END -->
