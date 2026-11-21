---
title: Build a proposal branch marking live-network tests
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#Live-network probes mixed into unit test files
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
14 upstream test files mix offline tests with live probes that run at import or setUpClass, so CI skips the whole files. Cut a branch from upstream/main that marks live tests `@pytest.mark.network` (skipped unless asked, via a conftest option or env var), moves probes into session fixtures, and lets CI run every file offline, matching upstream's CONTRIBUTING. Done when the offline suite runs all 14 files with no network access.

**Why it matters:** Gives the fork's own offline test rule an upstream basis.

**Why an agent:** mechanical test refactor

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
