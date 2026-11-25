---
id: AD-332
title: Confirm whether Backlog.md rewrites config.yml when a key it checks is missing
status: Done
assignee: []
created_date: '2026-11-20T13:01:00Z'
updated_date: '2026-11-25T13:31:00Z'
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
  - agent: claude-code
    id: 60abb818-6bc1-47ae-8fe7-f2357c94e058
    role: worked
    date: '2026-11-24'
  - agent: claude-code
    id: 60abb818-6bc1-47ae-8fe7-f2357c94e058
    role: finished
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task-tracker design (Consumer wiring) has templates render every key Backlog.md checks for before each command, with no comments, because a source reading found that when one of them is missing (such as default_port or auto_open_browser), Backlog.md writes config.yml again with its own set of keys, dropping comments and keys it doesn't know (src/cli.ts:1033-1060, src/core/config-migration.ts, src/file-system/operations.ts:2341 at v1.55.3). That was read in source, not confirmed by running. In a scratch git repo, write a config.yml that has a comment and an unknown key and lacks default_port, run one read-only command with the pinned backlog CLI, and compare the file before and after. Record the result in docs/tool-feedback/backlog-md.md (the entry 'A missing config key rewrites config.yml') and, if it doesn't happen, correct the consumer-wiring paragraph in docs/intent/task-tracker/task-tracker-design.md. Done before AD-5.2 (slice 2 of AD-5) updates the copier-python draft that carries the consumer wiring.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ran the pinned CLI (1.55.3) in scratch repos: the rewrite happens, and the key list in the design was incomplete. task_prefix and a milestones line with a value also trigger it; project_name and statuses do not. Recorded in docs/tool-feedback/backlog-md.md. Review wave 1: 9 findings, tool-feedback fixes applied. The design paragraph correction is held: Clash reports a conflict with the ad-336-dependency-free worktree on task-tracker-design.md.

After rebasing on main, applied the reviewed correction to the consumer-wiring paragraph of task-tracker-design.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Confirmed by running Backlog.md 1.55.3 in scratch repos: before each command, even a read-only one, it rewrites config.yml (dropping comments and unknown keys) when default_port, auto_open_browser, remote_operations, auto_commit or task_prefix is missing, or a milestones line lists a value. A missing project_name or statuses does not trigger it, because the parser fills them in. Recorded in docs/tool-feedback/backlog-md.md (entry renamed "Config migration rewrites config.yml before each command"), and corrected the consumer-wiring paragraph in docs/intent/task-tracker/task-tracker-design.md, which had listed project_name and statuses but not task_prefix or milestones. One review wave re-ran every case; its fixes are applied. Risk: none for consumers, whose template already renders task_prefix; a later Backlog.md release may add checked keys, so AD-5.2 should re-run the comparison on upgrade.
<!-- SECTION:FINAL_SUMMARY:END -->
