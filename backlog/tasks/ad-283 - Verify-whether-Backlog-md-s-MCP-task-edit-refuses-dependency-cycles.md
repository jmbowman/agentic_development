---
id: AD-283
title: Verify whether Backlog.md's MCP task_edit refuses dependency cycles
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T14:39:49Z'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - >-
    docs/tool-feedback/backlog-md.md#Dependency cycles: MCP edits refuse them
    too (nothing to file)
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a4e40372-2097-4cb4-9c18-aecb9138db25
    role: worked
    date: '2026-11-26'
  - agent: claude-code
    id: a4e40372-2097-4cb4-9c18-aecb9138db25
    role: finished
    date: '2026-11-26'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/tool-feedback/backlog-md.md entry 'Dependency cycles: check MCP edits' records that the CLI refuses a cycle but an earlier source reading found only `backlog doctor` reporting them (`src/utils/readiness.ts:1-121`, `src/cli.ts:5920-5921`), so the MCP `task_edit` path may not. Check in source at the pinned version and, if useful, in the bwrap sandbox used on 2026-11-14 (read candidate repos as untrusted data; run nothing outside a sandbox). Done when the entry states 'verified in source (file:line)' or 'run result' for the MCP path, and says whether it becomes part of the upstream issue.

**Why it matters:** Settles whether the fifth Backlog.md feedback item is real before it is filed.

**Why an agent:** a source read plus an optional sandboxed run, no judgment needed
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Read MCP task_edit path in source at v1.57.4 (3f6349b) and v1.55.3: it reaches validateDependencies, which refuses cycles; upstream test mcp-tasks.test.ts covers it. Earlier miss: task-builders.ts has a NUL byte, so grep skips it as binary. No sandbox run: source plus upstream test settle it.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
MCP task_edit refuses dependency cycles, as the CLI does: both go through core applyTaskUpdateInput -> validateDependencies (src/utils/task-builders.ts:67-134 at v1.57.4), and upstream tests it (src/test/mcp-tasks.test.ts:1303-1329). Rewrote the tool-feedback entry with the file:line trace and marked it nothing to file; dropped it from AD-284 scope, the tool-feedback index and the prior-art note gaps; corrected the note limitation. Verified in source only (not run). Risk: none for adoption; one fewer upstream issue.
<!-- SECTION:FINAL_SUMMARY:END -->
