---
id: AD-116
title: Probe the subagent-notes cases the platform probe skipped
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-4
dependencies: []
references:
  - docs/prior-art/2026-11-11-subagent-process-notes.md#Probe of the platform
  - >-
    docs/prior-art/2026-11-11-subagent-process-notes.md#Limitations checked in
    source
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Not probed in the 2026-11-11 note: subagents started by Workflow scripts or by other subagents, and resuming a finished subagent after the prompt cache has expired. Also confirm deep-plan's license and commit, which could not be cloned. Run each probe with a throwaway plugin on the current Claude Code and record the result in the subagent-notes LLD, adding specs if a case changes hook behavior.

**Why it matters:** Finds cases where the hooks silently miss a subagent.

**Why an agent:** short local probes
<!-- SECTION:DESCRIPTION:END -->
