---
id: AD-269
title: Adopt mdbook-llms with a committed llms.txt and freshness check
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-268
references:
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build `llms.txt` from SUMMARY.md with mdbook-llms (one-line descriptions from an optional `description:` key that #54's frontmatter renderer keeps off the page), commit it, keep it current with an index-freshness check (nothing may run inside another repo's clone), and link it directly from AGENTS.md/CLAUDE.md as the single index level. Optionally card-catalog's INDEX.md for record folders.

**Why it matters:** One cheap index entry point for humans and agents across repos.

**Why an agent:** tool adoption and check
<!-- SECTION:DESCRIPTION:END -->
