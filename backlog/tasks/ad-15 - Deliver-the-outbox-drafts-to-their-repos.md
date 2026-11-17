---
id: AD-15
title: Deliver the outbox drafts to their repos
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies:
  - AD-4
references:
  - backlog/outbox/
  - backlog/README.md
priority: medium
type: chore
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`backlog/outbox/<repo>/` holds task drafts for other repos (and the gitignored `backlog/private/outbox/` those for private ones). For each repo, start a Claude Code session there and hand it the drafts, or open the pull request that adds them to its backlog; the receiving repo assigns IDs and priority. Upstream projects' drafts are issue texts to file. Done when each draft is delivered or dropped and removed from the outbox.

**Why it matters:** Work found here reaches the repos that own it.
<!-- SECTION:DESCRIPTION:END -->
