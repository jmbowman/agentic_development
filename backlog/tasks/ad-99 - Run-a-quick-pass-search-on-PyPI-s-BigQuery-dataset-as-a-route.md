---
id: AD-99
title: Run a quick-pass search on PyPI's BigQuery dataset as a route
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-3
dependencies:
  - AD-98
references:
  - skills/prior-art-search/references/sources.md
priority: low
type: search
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: f4b2080f-847f-4a0d-a503-34339722eeb7
    role: created
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the prior-art-search quick pass: check the columns, size and query cost (summary and keywords) of bigquery-public-data.pypi.distribution_metadata (docs.pypi.org/api/bigquery), search for tools that wrap it, and check whether BigQuery's public datasets cover other useful software catalogs. Record the result in a dated note and, if adopted, propose a sources.md change through LID.

**Why it matters:** May give the skill a far better PyPI search route than the web index.

**Why an agent:** search work the skill defines
<!-- SECTION:DESCRIPTION:END -->
