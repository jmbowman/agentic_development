---
id: AD-283
title: Verify whether Backlog.md's MCP task_edit refuses dependency cycles
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - 'docs/tool-feedback/backlog-md.md#Dependency cycles: check MCP edits'
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/tool-feedback/backlog-md.md entry 'Dependency cycles: check MCP edits' records that the CLI refuses a cycle but an earlier source reading found only `backlog doctor` reporting them (`src/utils/readiness.ts:1-121`, `src/cli.ts:5920-5921`), so the MCP `task_edit` path may not. Check in source at the pinned version and, if useful, in the bwrap sandbox used on 2026-11-14 (read candidate repos as untrusted data; run nothing outside a sandbox). Done when the entry states 'verified in source (file:line)' or 'run result' for the MCP path, and says whether it becomes part of the upstream issue.

**Why it matters:** Settles whether the fifth Backlog.md feedback item is real before it is filed.

**Why an agent:** a source read plus an optional sandboxed run, no judgment needed
<!-- SECTION:DESCRIPTION:END -->
