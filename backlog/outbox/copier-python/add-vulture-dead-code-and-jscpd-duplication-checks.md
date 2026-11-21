---
title: Add vulture dead-code and jscpd duplication checks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
- https://github.com/jmbowman/copier-python/issues/47
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
external_blockers:
- copier-python/check-jscpd-s-license-and-mise-renovate-support-for-the-base
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add vulture at confidence 80 or higher with a whitelist (its default of 60 is noisy), and optionally jscpd for duplicated blocks, to the copier-python template and this repo's checks. Code size and vocabulary predict comprehension load, and agent-written code skews to copy-paste. Done when `mise run check` reports unused code and duplicates and the whitelist workflow is documented.

**Why it matters:** Reduces the lines a reviewer must read.

**Why an agent:** Tool addition with documented settings

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
