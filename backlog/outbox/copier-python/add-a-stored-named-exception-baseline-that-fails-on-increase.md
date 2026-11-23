---
title: Add a stored named-exception baseline that fails on increases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/strict-profile/strict-profile-design.md:75
- docs/high-level-design.md:241
- https://github.com/jmbowman/agentic_development/blob/main/docs/wiki/success-stories/orca.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's HLD success metric 'Shrinking divergence' says each repo's named-exception count never rises without a recorded reason; copier-python's strict-profile LLD defers a stored per-repo baseline, with `check` failing when the count rises, until two repos are onboarded. Build it then, on top of the existing `mise run exceptions` task. Done when a rendered consumer's check fails on an unexplained increase.

**Prior art:** Orca (stablyai/orca) runs this pattern at scale as "ratchets": 34 baseline files in its `config/`, one per rule (file length, synchronous file access, typecheck errors in end-to-end tests, flaky-test patterns and more), each listing today's violations, with a count that may only go down and a `--prune` option that removes fixed entries; its change-scoped check runs the ratchets the changed paths select. Beyond named exceptions, the same shape would let a consumer adopt a new strict rule straight away, baselining the existing violations instead of fixing them first. See the Orca profile in agentic_development's docs/wiki/success-stories/.

**Why it matters:** Makes a system-level success metric enforceable.

**Why an agent:** a design-then-build slice with a clear trigger

**Also waits on (not tracked as a task):** Two repos onboarded to copier-python

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
