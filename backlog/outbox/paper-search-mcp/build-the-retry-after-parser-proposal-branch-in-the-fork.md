---
title: Build the retry-after-parser proposal branch in the fork
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
- partly-done
references:
- paper-search-mcp:fork-notes/shared-http-layer.md#Moved out of scope (separate PRs)
- paper-search-mcp:.worktrees/retry-after-followup.patch
- docs/tool-feedback/paper-search-mcp.md:31
- docs/tool-feedback/paper-search-mcp.md#Pacing and retries live in each connector
- ../paper-search-mcp:fork-notes/shared-http-layer.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/paper-search-mcp
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The fork's decision record moved Retry-After parsing in both forms (seconds and HTTP date) for Semantic Scholar and IEEE out of scope into a separate PR, saved as `.worktrees/retry-after-followup.patch`; it notes date-form waits need a cap. Cut a branch `retry-after-parser` from upstream/main, apply and finish the patch in upstream's style with deterministic offline tests, add `fork-notes/retry-after-parser.md` on integration, and merge it into integration. Done when the branch passes the offline tests and has a decision record.

**Why it matters:** Correct backoff for Semantic Scholar's frequent refusals, which the harvester retries.

**Why an agent:** code from a saved patch with a known gap

**Status when filed (partly-done):** patch exists in .worktrees/; no branch

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
