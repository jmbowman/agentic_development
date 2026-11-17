---
title: Tighten PortaBase clang-tidy cognitive-complexity check
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
priority: low
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PortaBase's `.clang-tidy` enables `readability-*` (line 6) so the cognitive-complexity check runs at its default threshold of 25 with `WarningsAsErrors: ''` (line 16). Lower the threshold and make the check an error. Done when a function over the new threshold fails the lint run.

**Why it matters:** Applies the complexity ratchet to the C++ codebase.

**Why an agent:** One config change in a repo with its own session

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
