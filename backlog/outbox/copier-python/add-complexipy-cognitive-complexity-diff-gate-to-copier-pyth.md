---
title: Add complexipy cognitive-complexity diff gate to copier-python
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Limitations checked in source
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add complexipy's git-diff gate to the copier-python template so only functions that are new or have got worse fail (default maximum 15). The gate fails only regressions above the maximum, so a regression below it passes; say so in the template docs. Done when a rendered project fails CI on a new over-limit function. Evidence ties cognitive complexity to comprehension time, not defects, so treat it as a guardrail.

**Why it matters:** Cheap guardrail that keeps agent-written functions small enough to review.

**Why an agent:** Add a pinned tool and a check task

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
