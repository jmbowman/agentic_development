---
id: AD-135
title: Run the subagent notes interactive scenarios three times
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-5
dependencies:
  - AD-134
references:
  - docs/intent/subagent-notes/subagent-notes-specs.md:95-97
  - docs/intent/interactive-evals/interactive-evals-design.md:82
  - docs/intent/interactive-evals/interactive-evals-design.md:89
  - NOTES-LIVE-001
  - NOTES-LIVE-002
  - NOTES-LIVE-003
priority: medium
type: eval
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the NOTES-LIVE-001 to -003 scenarios by hand (paid model runs) three times each on the same skill text, as the review-log rule requires for an Interactive row, and paste the output for triage. Done when the review log has an Interactive row and `evals/session-wrap-up/latest-results.md` has a row per scenario.

**Why it matters:** Confirms the hooks don't break attended sessions or `-p` results for everyone who installs the plugin.

**Why the developer:** the developer runs paid evals
<!-- SECTION:DESCRIPTION:END -->
