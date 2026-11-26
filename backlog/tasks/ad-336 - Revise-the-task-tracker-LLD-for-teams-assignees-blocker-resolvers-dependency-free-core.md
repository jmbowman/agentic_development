---
id: AD-336
title: >-
  Revise the task-tracker LLD for teams: assignees, blocker resolvers,
  dependency-free core
status: In Progress
assignee: []
created_date: '2026-11-21T00:45:00Z'
updated_date: '2026-11-26T13:02:34Z'
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
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: worked
    date: '2026-11-23'
  - agent: claude-code
    id: a20b213e-9cc5-4bd1-8407-62658bae5e42
    role: worked
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A review of the task-tracker specs for use by a team of several developers raised needs the LLD (docs/intent/task-tracker/task-tracker-design.md) does not meet. Settle them through LID (LLD, EARS, edge audit) before AD-5.2 builds the data layer and lint, so that slice is not rebuilt. (1) Several human assignees: the proposal is Backlog.md assignee on human tasks, next --assignee and --mine with the current person set in the per-machine settings, agent tasks never assigned, focus.yml staying one set of rulings for the repo. (2) Blockers in other trackers such as Jira, with no support built in: the proposal is <scheme>:<ref> blockers with gh: built in, and other schemes resolved by a command declared in a repo file that reads references on standard input and prints each state as JSON, under the same cache and fail-closed rules. (3) Adoption without dependencies: the proposal is that the tool parses the restricted YAML the format reference allows using only the standard library, after a quick search for vendorable pure-Python parsers, keeps the per-file rules in code, and needs jsonschema only for a repo schema.json, which also settles AD-26. (4) A Decisions row on why outbox drafts, not issues filed on the receiving repo, are the record of work for another repo (reviewed before leaving the repo, written offline, keeps the task keys, readable by readiness, room for private work, no particular forge; the cost is delivery latency). The developer rules on each proposal at the LLD stop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The LLD and specs cover assignees, blocker resolvers and the dependency policy, approved at their LID stops
- [x] #2 The LLD Decisions table has a row comparing outbox drafts with filing issues on the receiving repo
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Proposal (3), the dependency-free core, is ruled and through its LID stops (LLD, EARS, edge audit, review wave): the tool vendors oneyaml (kept current by vendir and Renovate lock-file maintenance), declares no dependencies and has no lock file; every lint rule is in code; repo schema.json support is dropped (AD-353 parks custom per-repo rules). See the task-tracker LLD: Lint (Rules in code), Reading YAML, Commands and the Decisions rows. AD-354 implements it; AD-26 closed. Proposals (1) assignees, (2) blocker resolvers and (4) the outbox Decisions row remain.

Proposals (1) assignees and (4) the outbox Decisions row: LLD drafted, probed and ruled on 2026-11-25 (ten forks; review log 2026-11-25-task-tracker.md), with one HLD sentence; EARS drafted and awaiting review. Proposal (2) blocker resolvers: not designed; the developer chose a full prior-art search first, to start after planned improvements to the prior-art-search skill.

2026-11-25, later: assignees were widened to agent tasks (the supervising developer) and session records gained a supervisor, by the developer's ruling at the EARS stop. Edge audit run and its nine forks ruled; review wave run (review log 2026-11-25-task-tracker.md has all three rows; the LLD probe ruled nine forks plus one HLD sentence). Follow-ups: AD-364 (skill text), AD-365 (session wrap-up), notes on AD-5.2 and AD-5.3. Still open here: proposal (2), and two small forks from the review wave.

The two review-wave forks are ruled and applied (an agent asks before taking an assigned task from an unnarrowed queue; the user command needs no backlog). Proposal (2) remains.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: a20b213e-9cc5-4bd1-8407-62658bae5e42
created: 2026-11-26T13:02:34Z

---

Proposal (2), blocker resolvers: options sketched on 2026-11-25, before any search. (A) A `<scheme>:<ref>` blocker such as `jira:PROJ-123` is resolved by a command the repo declares, which reads references on standard input and prints each state as JSON, under the `gh:` cache and fail-closed rules. Open point: where the repo declares it; `focus.yml` is already the file agents never edit, which matters because the tool would run the command. (B) The same protocol, with the command declared in the per-machine settings: no tracked file names a command to run, but every developer configures it and CI sees those blockers as unreadable. (C) Nothing built: a blocker in another tracker is a human task or a `defer_until` date. The developer chose a full prior-art search first. The search still needs two inputs from the developer: what they already know of or have dismissed, and the two or three most common uses (assumed so far: a task waiting on a Jira ticket, one waiting on another team's tracker, and CI running `check` with no credentials). Open Question 15 in the LLD (delivery by issue on a forge other than GitHub) waits on the same design.

---
<!-- COMMENTS:END -->
