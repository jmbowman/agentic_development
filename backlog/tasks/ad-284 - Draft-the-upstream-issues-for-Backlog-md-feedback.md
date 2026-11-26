---
id: AD-284
title: Draft the upstream issues for Backlog.md feedback
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-25T18:54:15Z'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies:
  - AD-1
  - AD-283
references:
  - docs/tool-feedback/backlog-md.md
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
priority: medium
type: upstream
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft issue text for MrLesk/Backlog.md covering the five entries of docs/tool-feedback/backlog-md.md: 'A task file can run a shell command' (onStatusChange runs as sh -c; the most serious, consider a private security report first), 'Claiming a task isn't atomic', 'ID generation fetches and prunes by default', '`init --defaults` writes an always-run instruction into AGENTS.md', and 'Dependency cycles: check MCP edits' (include only if the verification item confirms it). Use the source lines and the 1.55.3 sandbox evidence already in the entries. Done when drafts are shown inline for approval.

**Why it matters:** Backlog.md is the leading task store candidate; the callback issue affects any repo that accepts task files by pull request.

**Why an agent:** text from recorded evidence; filing is separate
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-25: one more entry to draft, added by AD-336: the assignee filter treats alex and @alex as different people.
<!-- SECTION:NOTES:END -->
