---
id: AD-370
title: >-
  Revisit the review-wave escalation thresholds once the review log can judge
  them
status: To Do
assignee: []
created_date: '2026-11-26T14:38:29Z'
labels: []
milestone: m-6
dependencies:
  - AD-199
references:
  - docs/decisions/review-wave-stopping.md
priority: low
type: decision
ordinal: 57000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: created
    date: '2026-11-26'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/decisions/review-wave-stopping.md escalates a review loop to the developer instead of a sixth wave, or when at least two and over 30% of a wave's accepted findings were caused by the previous wave's fixes. Both thresholds are unmeasured guesses (the 30% is borrowed from deep-review-loop, unmeasured there too), and the decision obligates revisiting them. Trigger: about ten waves logged with the per-wave counts AD-199 adds, or the first escalation under them. Review the counts and confirm or retune both thresholds in the decision doc. Also weigh an incentive seen in the first loop run under the rule: once one accepted fix forces another wave (or, in the last wave before the count limit, an escalation), accepting more looks free, so triage must hold each finding to the worth-a-wave bar on its own. And decide whether a defect introduced by an earlier wave's fix, but first found after the next wave, counts as fix-caused: the trigger now counts only the previous wave's fixes.

**Why it matters:** Keeps the escalation triggers from silently over- or under-firing.

**Why the developer:** the thresholds decide when the loop hands off to the developer
<!-- SECTION:DESCRIPTION:END -->
