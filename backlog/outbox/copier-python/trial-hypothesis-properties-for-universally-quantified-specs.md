---
title: Trial Hypothesis properties for universally quantified specs in copier-python
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
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use Hypothesis (MPL-2.0) where a spec says 'for any ...', replacing hand-picked example tables with one property or stateful model. Every copier-python test uses function-scoped fixtures, which trip Hypothesis's health check (`_hypothesis_pytestplugin.py:256,290`), so the spike must settle how to scope fixtures. Done when one spec is covered by a property and the approach is judged.

**Why it matters:** Shrinks test text for universally quantified specs.

**Why an agent:** Small code spike

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
