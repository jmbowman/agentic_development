---
id: AD-350
title: >-
  Search for projects that ship fast with high quality, and profile what makes
  them work
status: To Do
assignee: []
created_date: '2026-11-23T11:17:00Z'
labels: []
milestone: m-6
dependencies: []
priority: medium
type: search
ordinal: 41000
references:
  - docs/wiki/success-stories/README.md
  - docs/wiki/success-stories/orca.md
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 27e13044-1d02-40c4-90d7-0134d1214b1d
    role: created
    date: '2026-11-23'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The developer wants to learn from projects that develop quickly without losing quality, especially with small teams or one developer, by profiling each in docs/wiki/success-stories/ and then finding the practices several share, to decide what to adopt first here and in the projects that use this repo's tooling. Orca is profiled (docs/wiki/success-stories/orca.md); mise ("moving fast and not breaking things") and, to a lesser extent, Backlog.md are named candidates. Run a focused search for more, using the prior-art-search skill's auditable method where it fits (sources logged, candidates classified, claims verified in each repository), then write a profile per selected project in the format docs/wiki/success-stories/README.md sets, and fill its Common threads section once there are three or more. Each practice that fits gets a task or an outbox draft, linked from the profile's Fit here table; the Orca profile's untaken rows are inputs too.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/wiki/success-stories/ holds a profile for mise, Backlog.md and each project the search selects, each claim tagged by what it rests on and each number dated
- [ ] #2 The README's Common threads section names the practices three or more profiled projects share, and which to adopt first
- [ ] #3 Each practice judged to fit has a task or outbox draft linked from its profile
<!-- AC:END -->
