---
title: Draft the shared-http-layer upstream PR description
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- paper-search-mcp:fork-notes/shared-http-layer.md#Known limits, to mention in the PR
- paper-search-mcp:fork-notes/shared-http-layer.md#Decisions, with the alternatives rejected
- docs/tool-feedback/paper-search-mcp.md#Pacing and retries live in each connector
- docs/tool-feedback/paper-search-mcp.md#Semantic Scholar has no keyed pacing
- ../paper-search-mcp:fork-notes/shared-http-layer.md
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
target: github.com/jmbowman/paper-search-mcp
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft the pull request text for the fork's `shared-http-layer` branch (a3a9f62) against openags/paper-search-mcp, in the maintainer's style (prose, matching their recent PRs). Use `fork-notes/shared-http-layer.md`: the problem, the pace-but-never-retry design, the stdlib SQLite limiter instead of PyrateLimiter, the opt-in shared directory, the 10 s cap, the per-host table (including Semantic Scholar's keyed 1/s limit), and the 'Known limits, to mention in the PR' section, plus an offer of the `.netrc` follow-up. Confirm the branch still sits on upstream main (cab1b5c, unchanged as of 2026-11-16). Show the draft inline for review. Done when the developer approves the text.

**Why it matters:** Readies the fork's main proposal so the fork can shrink to upstream.

**Why an agent:** drafting from a complete decision record

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
