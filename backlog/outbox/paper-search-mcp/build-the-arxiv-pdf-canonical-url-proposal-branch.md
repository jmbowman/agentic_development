---
title: Build the arxiv-pdf-canonical-url proposal branch
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- paper-search-mcp:fork-notes/shared-http-layer.md#Moved out of scope (separate PRs)
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Requesting `https://arxiv.org/pdf/<id>.pdf` gets a 301 to the bare form, so each download uses two of arXiv's one-per-3-seconds slots. Cut `arxiv-pdf-canonical-url` from upstream/main to request the bare form, updating the download URL that #147's tests assert, with offline tests and a fork-notes record. Done when the branch passes offline tests.

**Why it matters:** Halves arXiv slot use per PDF download.

**Why an agent:** a small, specified code change

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
