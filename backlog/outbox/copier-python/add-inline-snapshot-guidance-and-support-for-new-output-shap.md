---
title: Add inline-snapshot guidance and support for new output-shaped tests
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- issue
references:
- https://github.com/jmbowman/copier-python/issues/48
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Limitations checked in source
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
external_blockers:
- copier-python/decide-how-the-template-brings-inline-snapshot-and-its-test
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the #48 decision: make inline-snapshot available to consumers as decided, and write the test-authoring guidance (use `sorted(...)` where the spec promises no order; don't rewrite existing tests) where the decision puts it. Follow LID in whichever repo holds it. Done when a rendered consumer's agent would find the guidance and the dependency route is documented in the README.

**Why it matters:** Makes snapshot tests the cheap default for agents.

**Why an agent:** build once the location is decided

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
