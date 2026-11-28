---
id: AD-164
title: Build the review-wave stop and escalation check over the ledger
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T14:03:47Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-163
  - AD-140
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#10.
    Convergence and stopping
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
  - docs/decisions/review-wave-stopping.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A pure function over the ledger returning continue, stop or escalate-to-developer for the loop in docs/decisions/review-wave-stopping.md: stop when the last recorded wave's triage ruling accepted nothing to fix now (a stored ruling, not computed; a wave with no recorded ruling is still in triage and doesn't stop the loop) and no fork awaits the developer's ruling, where a fork ruled fix-now counts as an accepted finding; escalate instead of starting a sixth wave, or when at least two of a wave's accepted findings, and more than 30% of them, were fix-caused (thresholds configurable), counting waves from the start of the loop or from the developer's last ruling to patch or rework after an escalation; a converged result is void when the content hash changes. Doctrine's escalate rule (serious findings not falling across two waves) is not part of the ruling; if ledger data supports it, propose it to the developer rather than adding it. Fixtures per principle 4.

**Why it matters:** Makes the escalation triggers and the stop check mechanical, so a gate can re-check them.

**Why an agent:** pure code with fixtures
<!-- SECTION:DESCRIPTION:END -->
