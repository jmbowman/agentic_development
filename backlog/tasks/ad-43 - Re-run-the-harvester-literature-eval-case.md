---
id: AD-43
title: Re-run the harvester-literature eval case
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-25T14:37:22Z'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies:
  - AD-41
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:225-237
  - docs/review-log/history-to-2026-11-22.md:88-90
  - evals/prior-art-search/latest-results.md
  - PRIOR-SCR-100
  - PRIOR-SCR-110
  - PRIOR-SCR-120
  - PRIOR-SCR-121
  - docs/review-log/history-to-2026-11-22.md:61
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

## Comments

<!-- COMMENTS:BEGIN -->
author: claude-code:7491ae04
created: 2026-11-24T06:12:00Z

---

From AD-92 (2026-11-24): the case and its graders now also cover PRIOR-SCR-134 and the wider PRIOR-SCR-100 (every arXiv, OpenAlex and Semantic Scholar API request through the harvester; only full text from arxiv.org) and the PRIOR-SCR-106 exception for OpenAlex get and related. The next run is the first evidence for those.

---

author: claude-code:6becb69f
created: 2026-11-25T14:00:49Z

---

From AD-41 (2026-11-25): no skill text changed. The wave-3 failure was the grader, which then asked for the run directory in every subagent prompt; it now asks only for literature subagents. In the wave-3 trace the literature subagents sent 7 requests of their own to OpenAlex and Semantic Scholar (lookups allowed then); since AD-92 those go through the harvester, so check for them when triaging this run.

---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-run on 2026-11-25 (Claude Code 2.1.332, Sonnet 5.5 agent and judge, one run, no baseline arm, `TMPDIR` outside `/tmp`): score 0.60, $5.12 plus $0.96 for the judges, 26 min. Results are in `evals/prior-art-search/results/2026-11-25T14-05-29-122Z` (local) and the kept run is `claude-eval-4wKiMj`. The judges saw only the first 100,024 characters of a 1.9 MB trace, which end before any subagent starts, so the two FAILs need checking against the full trace: that triage is AD-82.
<!-- SECTION:FINAL_SUMMARY:END -->
