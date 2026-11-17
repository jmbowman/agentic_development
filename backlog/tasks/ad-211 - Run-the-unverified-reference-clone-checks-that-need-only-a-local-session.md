---
id: AD-211
title: Run the unverified reference-clone checks that need only a local session
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-204
references:
  - >-
    docs/prior-art/2026-11-06-agent-reference-clones.md#Limitations checked in
    source
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Test locally: that the Edit deny rule blocks Edit and Write, that `claudeMdExcludes` on `**/.reference-repos/**` works, that a committed project settings `env` reaches agent Bash (only a --settings file was tested), that Glob with no path skips a gitignored directory, the three-config vendir layout (`-f <config> --lock-file <lock> -d` creating a missing lock; no-tags override under `-f`), and whether non-Claude agents act on the AGENTS.md listing. Record results in the reference-clones note or its LLD.

**Why it matters:** Confirms the design's assumptions before it ships to every repo.

**Why an agent:** local probes
<!-- SECTION:DESCRIPTION:END -->
