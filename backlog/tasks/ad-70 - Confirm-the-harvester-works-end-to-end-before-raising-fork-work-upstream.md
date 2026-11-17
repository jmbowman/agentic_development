---
id: AD-70
title: Confirm the harvester works end to end before raising fork work upstream
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
milestone: m-3
dependencies: []
references:
  - docs/tool-feedback/paper-search-mcp.md:3
  - docs/review-log.md:88-90
  - https://github.com/jmbowman/agentic_development/issues/157
priority: medium
type: review
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's tool-feedback note says the shared-http-layer PR is filed 'once the harvester works end to end', matching the developer's rule to hold upstream issues until local use works. The harvester landed (#244), but the 2026-11-15 eval rows for harvester-literature record sandbox problems, and issue #157 is still open. Judge whether local use is proven. Done when the developer records a go or names what's missing.

**Why it matters:** Gates every upstream proposal from the fork.

**Why the developer:** a readiness judgment and gate on outward action
<!-- SECTION:DESCRIPTION:END -->
