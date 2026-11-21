---
id: AD-73
title: Re-run prior-art refreshes at their trigger dates
status: To Do
assignee: []
created_date: '2026-11-16'
due_date: '2027-04-17'
labels:
  - prior-art
milestone: m-3
dependencies: []
references:
  - docs/prior-art/2026-10-17-prior-art-search-skill.md#Refresh trigger
  - >-
    docs/prior-art/2026-11-04-agent-readable-catalogs-and-paper-sources.md#Refresh
    trigger
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Refresh trigger
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md#Refresh trigger
priority: medium
type: search
deadline_kind: target
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Several notes set dated refresh triggers: the prior-art skill note on 2027-04-17 (or sooner if a major catalog publishes a prior-art skill), the catalogs and paper routes on 2027-05-04 (or when OpenAlex's anonymous budget or Semantic Scholar's relevance search changes), musthold and kalku by 2027-04 (sooner if musthold adds C++ or @spec-style citations), the review-burden note when a custom piece is designed, and the in-repo architecture-maps note on 2027-05-17 (or sooner when groma.md reaches 1.0 or settles its plan to detach from the filesystem), starting from the further leads it lists as not pursued under "Leads read after the cap". Run the prior-art-search skill's refresh for each when due and record results. Done when each due refresh has a dated note or log row.

**Why it matters:** Keeps verdicts current as tools change.

**Why an agent:** Runs an existing skill on a schedule

**Deadline:** Earliest dated refresh trigger among the notes
<!-- SECTION:DESCRIPTION:END -->
