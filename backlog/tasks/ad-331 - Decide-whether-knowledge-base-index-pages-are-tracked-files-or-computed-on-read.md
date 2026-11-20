---
id: AD-331
title: >-
  Decide whether knowledge-base index pages are tracked files or computed on
  read
status: To Do
assignee: []
created_date: '2026-11-20T03:11:00Z'
labels: []
milestone: m-8
dependencies: []
priority: low
type: decision
ordinal: 18000
references:
  - docs/prior-art/2026-11-19-generated-views-over-markdown.md
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The generated-views prior-art search (docs/prior-art/2026-11-19-generated-views-over-markdown.md, Verdict) recommends insitu for knowledge-base index pages such as the decision-doc index: SQL over frontmatter written between markers, with insitu check failing CI when an index is stale. HLD tenet 10 favours computing derived views on read, as the task tracker does for its board and AD-264 plans for decisions with a SessionStart hook. The note recommends tracked indexes only for pages that agents and GitHub readers navigate by, and computing on read (docs-site build or hook) for everything else. Done when the developer has ruled, and the ruling is recorded in the HLD or the knowledge-base design, with the tenet 10 wording adjusted if tracked indexes are allowed.
<!-- SECTION:DESCRIPTION:END -->
