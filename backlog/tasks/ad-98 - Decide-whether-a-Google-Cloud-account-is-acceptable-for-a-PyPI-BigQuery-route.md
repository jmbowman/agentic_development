---
id: AD-98
title: Decide whether a Google Cloud account is acceptable for a PyPI BigQuery route
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-3
dependencies: []
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: f4b2080f-847f-4a0d-a503-34339722eeb7
    role: created
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A queued quick-pass search would evaluate bigquery-public-data.pypi.distribution_metadata as a searchable PyPI route in the prior-art skill. It needs a Google Cloud account (and probably billing). The developer must say whether that is acceptable before the search runs.

**Why it matters:** Gates a possible new search route for PyPI packages.

**Why the developer:** needs the developer's accounts and credentials
<!-- SECTION:DESCRIPTION:END -->
