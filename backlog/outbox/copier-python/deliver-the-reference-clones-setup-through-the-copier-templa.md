---
title: Deliver the reference-clones setup through the copier template
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-11-06-agent-reference-clones.md#Need and criteria
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
external_blockers:
- agentic_development#AD-150
- agentic_development#AD-206
- agentic_development#AD-207
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the pieces work here, add them to the copier template so every repo gets the vendir configs, task, hook, CI check, settings and gitignore entries. Pinned tool in mise, setup in the mise setup task, and CI check in the template's check task. Done when a fixture consumer repo renders and passes.

**Why it matters:** The reason the clone design was researched at full depth.

**Why an agent:** template change in another repo; sent as a request to a session rooted there

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
