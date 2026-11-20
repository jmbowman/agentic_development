---
id: AD-332
title: Confirm whether Backlog.md rewrites config.yml when a key it checks is missing
status: To Do
assignee: []
created_date: '2026-11-20T13:01:00Z'
labels: []
milestone: m-1
dependencies: []
references:
  - docs/tool-feedback/backlog-md.md
  - docs/intent/task-tracker/task-tracker-design.md
priority: medium
type: spike
ordinal: 19000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 8265c29b-8e38-4a63-a066-a078049699cd
    role: created
    date: '2026-11-20'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task-tracker design (Consumer wiring) has templates render every key Backlog.md checks for before each command, with no comments, because a source reading found that when one of them is missing (such as default_port or auto_open_browser), Backlog.md writes config.yml again with its own set of keys, dropping comments and keys it doesn't know (src/cli.ts:1033-1060, src/core/config-migration.ts, src/file-system/operations.ts:2341 at v1.55.3). That was read in source, not confirmed by running. In a scratch git repo, write a config.yml that has a comment and an unknown key and lacks default_port, run one read-only command with the pinned backlog CLI, and compare the file before and after. Record the result in docs/tool-feedback/backlog-md.md (the entry 'A missing config key rewrites config.yml') and, if it doesn't happen, correct the consumer-wiring paragraph in docs/intent/task-tracker/task-tracker-design.md. Done before slice 1 of AD-5's code writes the consumer wiring.
<!-- SECTION:DESCRIPTION:END -->
