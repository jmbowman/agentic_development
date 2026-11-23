---
id: AD-44
title: Confirm the harvester satisfies PRIOR-ACC-012 and add a test
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - maybe-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:122
  - docs/review-log/history-to-2026-11-22.md:61
  - skills/prior-art-search/scripts/harvest.py
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PRIOR-ACC-012 (a rejected API key, 401 or 403 without a rate-limit response, records the route unavailable as 'authentication: <setting> rejected' and sends no further requests) is still marked [ ] in docs/intent/prior-art-search/prior-art-search-specs.md, and the 2026-11-09 review-log row says 'PRIOR-ACC-012 stays open' because the shim would enforce it in code. skills/prior-art-search/scripts/harvest.py now has authentication outcomes (around lines 1270, 1356). Check the code against the spec, add or point at tests carrying `@spec PRIOR-ACC-012`, and flip the marker if met. Done when tests cover it and the spec status matches.

**Why it matters:** Stops a rejected key from being retried against its service.

**Why an agent:** checking code against a spec and writing tests

**Status when filed (maybe-done):** harvest.py has authentication handling added after the review-log note
<!-- SECTION:DESCRIPTION:END -->
