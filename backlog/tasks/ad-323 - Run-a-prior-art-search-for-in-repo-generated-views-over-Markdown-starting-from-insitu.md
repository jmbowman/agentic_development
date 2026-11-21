---
id: AD-323
title: >-
  Run a prior-art search for in-repo generated views over Markdown, starting
  from insitu
status: Done
assignee: []
created_date: '2026-11-18T05:17:00Z'
labels: []
milestone: m-8
dependencies: []
references:
  - https://github.com/marcusinthesky/insitu
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md
  - docs/intent/task-tracker/task-tracker-design.md
priority: low
type: spike
ordinal: 10000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
insitu (https://github.com/marcusinthesky/insitu, MIT, alpha) indexes Markdown and frontmatter into SQLite, runs SQL models over it, and writes the results back into Markdown files between comment markers, with a check that fails CI when a view is stale. Its own repo gates Markdown with rumdl, lychee, schematter and codespell, close to the knowledge-base blend in docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md. Run the prior-art-search skill for tools that keep generated views (indexes, tables, dashboards) of Markdown and frontmatter inside the repo, or query frontmatter with SQL, with insitu as the first candidate. Judge them for the knowledge base's generated indexes (such as the decision-doc index, AD-264) and as a query layer over task and note frontmatter. The task tracker computes its views on read and never writes task files (HLD tenet 10), so a tool that writes views into task files fits only as a reader there. Done when a docs/prior-art/ note classifies the candidates with licenses read from files, and the knowledge-base note's refresh triggers name the result.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-19: full-method search saved as docs/prior-art/2026-11-19-generated-views-over-markdown.md. The knowledge-base note's refresh triggers name the result.

2026-11-20: after the review wave, the verdict is a blend of mq as the query layer for all three uses and a small custom view tool that runs only an allowlist of view commands: as an mdBook preprocessor at site build (AD-326), and with `sync` and `check` modes if index pages are tracked. insitu is held until it matures; cmdsync and mdsh were dropped because they run commands written in pages. Whether knowledge-base index pages are tracked or computed on read is the developer's call (AD-331), and AD-264's SessionStart hook waits on that ruling.
<!-- SECTION:NOTES:END -->
