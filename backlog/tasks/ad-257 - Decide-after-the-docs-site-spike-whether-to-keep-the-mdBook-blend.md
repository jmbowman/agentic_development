---
id: AD-257
title: Decide after the docs-site spike whether to keep the mdBook blend
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-252
references:
  - >-
    docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md#Candidates
    and matrix
  - >-
    docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md#Refresh
    trigger
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Read the spike result and choose between the verdict (mdBook + Pagefind + a small custom preprocessor for backlinks, graph and hover previews) and the runner-up (ProperDocs + MaterialX + plugins). The note says the verdict drops below the Python stack if the custom code grows past a small preprocessor and a few hundred lines of JavaScript. Also check the refresh triggers (Zensical module API, MkDocs 2.0, Material for MkDocs end of life, scraps live reload). Done when the choice is recorded in the docs-site design or issue #54.

**Why it matters:** Gates the preprocessor build and the template rollout.

**Why the developer:** Chooses between two ranked designs on cost judgment
<!-- SECTION:DESCRIPTION:END -->
