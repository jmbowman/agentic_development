---
id: AD-330
title: >-
  Add design-input steps to LID walks: use-case walk, related-work scan,
  adopted-tool surface audit
status: To Do
assignee: []
created_date: '2026-11-19T13:46:00Z'
labels: []
milestone: m-6
dependencies: []
references:
  - docs/intent/task-tracker/task-tracker-design.md
  - backlog/tasks/ad-214 - Design-a-spec-review-loop-around-LID-s-design-phases.md
  - backlog/tasks/ad-179 - Use-the-BMAD-edge-case-lens-as-the-prompt-for-LID-s-LLD-probe.md
  - backlog/tasks/ad-48 - Make-prior-art-search-ask-for-real-use-cases-and-walk-them-first.md
priority: medium
type: feature
ordinal: 17000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In AD-5's walk of the task tracker, the developer found most of the design's later improvements, not the agent or its edge-case probe: milestones as workstream records, a search task type, session records on tasks, one list of links, rendering the backlog in the docs site, task IDs for teams, and the meaning of Backlog.md's archive, drafts, docs and decisions. They came from three places that LID's phases don't send an agent: the developer's own uses of the thing being designed (at home and at work), other planned work in the backlog and notes, and the parts of an adopted tool that the design hadn't ruled on. LID's Phase 2 probe is limited to the LLD's own text, and an edge-case lens (AD-179) looks for branches and boundaries, so neither covers them. Design three steps for this repo's LID walks, run before the LLD stop: a use-case walk (ask the developer for the two or three main uses, including in other settings, and walk the draft through each); a related-work scan (open tasks and notes in the walk's milestone and its neighbours, and the HLD's planned components, reported as what the design should leave room for); and, when the design adopts a tool, a surface audit (every key, folder, config setting and command of the tool gets a use, ignore, override or lint verdict). AD-5's walk ran the last two as subagent probes on 2026-11-19; their results are the first evidence. Done when the steps are designed through LID (likely as part of the spec-review loop, AD-214) and used in a walk.
<!-- SECTION:DESCRIPTION:END -->
