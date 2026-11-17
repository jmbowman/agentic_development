---
id: AD-43
title: Re-run the harvester-literature eval case
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies:
  - AD-41
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:225-237
  - docs/review-log.md:88-90
  - evals/prior-art-search/latest-results.md
  - PRIOR-SCR-100
  - PRIOR-SCR-110
  - PRIOR-SCR-120
  - PRIOR-SCR-121
  - docs/review-log.md:61
priority: high
type: eval
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Re-run `harvester-literature` with `mise run eval` (with `TMPDIR` outside `/tmp`, as wave 3 needed). Its last run (2026-11-15, wave 3) failed only the harvester-used grader because the software subagents' prompts lacked the run directory, and the harvester then changed (OpenAlex default, Semantic Scholar lookups, commit aec8b25). It covers PRIOR-SCR-100 to PRIOR-SCR-110, PRIOR-SCR-120 and PRIOR-SCR-121. Paste the output for triage.

**Why it matters:** Verifies the harvester is actually used, which gates removing the agents' own-request fallback.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** latest-results: 1 run, 1 failed (2026-11-15); SKILL.md now tells the agent to pass the run directory to every subagent
<!-- SECTION:DESCRIPTION:END -->
