---
id: AD-310
title: File the smaller paper-search-mcp proposals upstream
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies:
  - AD-309
references:
  - docs/tool-feedback/paper-search-mcp.md:3
  - https://github.com/jmbowman/agentic_development/issues/168
  - docs/tool-feedback/paper-search-mcp.md
  - >-
    docs/prior-art/2026-11-07-search-harvest-pipeline.md#Limitations checked in
    source
priority: medium
type: upstream
performer: human
effort: M
external_blockers:
- paper-search-mcp/build-a-configurable-crossref-mailto-proposal-branch
- paper-search-mcp/build-a-proposal-branch-removing-insecure-tls-retries
- paper-search-mcp/build-the-retry-after-parser-proposal-branch-in-the-fork
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the shared-http-layer PR is filed, open the smaller proposals beside it, as `docs/tool-feedback/paper-search-mcp.md` plans: Retry-After parsing, arXiv canonical PDF URL, SSRN dead helpers, Crossref mailto, TLS retries, null authors, network-test markers, MCP extra, `.env` loading and IEEE key (whichever branches exist). Approve each PR text inline first, then update each entry's 'Raised upstream' line. Done when each ready branch has a PR or a recorded reason to hold it.

**Why it matters:** Moves fixes upstream so the fork can shrink.

**Why the developer:** outward-facing PRs in the developer's name
<!-- SECTION:DESCRIPTION:END -->
