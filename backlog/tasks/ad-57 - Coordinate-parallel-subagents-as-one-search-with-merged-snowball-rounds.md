---
id: AD-57
title: Coordinate parallel subagents as one search with merged snowball rounds
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/155
  - https://github.com/jmbowman/agentic_development/issues/157
  - skills/prior-art-search/SKILL.md
  - skills/prior-art-search/references/verification.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #155: change SKILL.md's Working in parallel and Snowball sections and verification.md's Subagent records so the main agent coordinates rounds: subagents run one round at a time and return snowball records (new candidates, new_vocabulary, new_tags); the main agent merges by owner/repo (never by name) and sends the next round's seeds to every service holder; stop condition and cap apply to merged rounds only; any request to a held service, including metadata lookups, goes through its holder; records are appended as found, with a per-round call cap; consider a fresh agent per round once a holder's context is large. The #157 comment notes a shared cross-process limiter would let subagents share services and simplify ownership. LID pass with specs, tests and an eval case.

**Why it matters:** Cuts duplicate work and lost seeds across parallel search agents.

**Why an agent:** skill and spec edits following a written proposal
<!-- SECTION:DESCRIPTION:END -->
