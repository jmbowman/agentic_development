---
id: AD-336
title: >-
  Revise the task-tracker LLD for teams: assignees, blocker resolvers,
  dependency-free core
status: To Do
assignee: []
created_date: '2026-11-21T00:45:00Z'
labels: []
milestone: m-1
dependencies: []
priority: high
type: feature
ordinal: 26000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A review of the task-tracker specs for use by a team of several developers raised needs the LLD (docs/intent/task-tracker/task-tracker-design.md) does not meet. Settle them through LID (LLD, EARS, edge audit) before AD-5.2 builds the data layer and lint, so that slice is not rebuilt. (1) Several human assignees: the proposal is Backlog.md assignee on human tasks, next --assignee and --mine with the current person set in the per-machine settings, agent tasks never assigned, focus.yml staying one set of rulings for the repo. (2) Blockers in other trackers such as Jira, with no support built in: the proposal is <scheme>:<ref> blockers with gh: built in, and other schemes resolved by a command declared in a repo file that reads references on standard input and prints each state as JSON, under the same cache and fail-closed rules. (3) Adoption without dependencies: the proposal is that the tool parses the restricted YAML the format reference allows using only the standard library, after a quick search for vendorable pure-Python parsers, keeps the per-file rules in code, and needs jsonschema only for a repo schema.json, which also settles AD-26. (4) A Decisions row on why outbox drafts, not issues filed on the receiving repo, are the record of work for another repo (reviewed before leaving the repo, written offline, keeps the task keys, readable by readiness, room for private work, no particular forge; the cost is delivery latency). The developer rules on each proposal at the LLD stop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The LLD and specs cover assignees, blocker resolvers and the dependency policy, approved at their LID stops
- [ ] #2 The LLD Decisions table has a row comparing outbox drafts with filing issues on the receiving repo
<!-- AC:END -->
