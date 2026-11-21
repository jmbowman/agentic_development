---
title: Build template follow-up task files for copier-python releases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-11-16-cross-repo-task-coordination.md:106-111
- docs/prior-art/2026-11-16-cross-repo-task-coordination.md:119-125
- docs/high-level-design.md:113
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
external_blockers:
- github.com/jmbowman/agentic_development#AD-5.2
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-16 cross-repo task coordination note proposes 'Piece K': a template release adds a follow-up task file that `_exclude` leaves out of fresh copies, so it arrives only in each consumer's Renovate update PR, plus a status report of which consumers have done it. It depends on the note's open decisions 2 (naming), 6 (delivery) and 8 (turning off automerge for copier updates, which would contradict HLD tenet 6). Implement in copier-python once those are answered. Done when a template release can ship a follow-up and the status report lists each consumer's state.

**Why it matters:** Gives every template consumer tracked follow-ups for releases that need hand work.

**Why an agent:** build once the decisions are made

**Also waits on (not tracked as a task):** Developer answers decisions 2, 6 and 8 in docs/prior-art/2026-11-16-cross-repo-task-coordination.md

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
