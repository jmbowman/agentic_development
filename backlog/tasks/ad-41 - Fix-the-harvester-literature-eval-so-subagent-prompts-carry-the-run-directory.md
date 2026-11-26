---
id: AD-41
title: Fix the harvester-literature eval so subagent prompts carry the run directory
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-25T14:00:48Z'
labels:
  - process
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/review-log/history-to-2026-11-22.md:90
  - evals/prior-art-search/latest-results.md
  - evals/prior-art-search/harvester-literature
priority: high
type: feature
performer: agent
agent_tier: strong
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: worked
    date: '2026-11-25'
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: finished
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review-log 2026-11-15 Evals wave 3: with TMPDIR outside /tmp the harvester ran 13 times, but `harvester-used` failed because the software subagents' prompts lacked the run directory; one fork was put to the developer. latest-results.md shows harvester-literature at 1 run, 1 failed. Fix the skill text (skills/prior-art-search/SKILL.md or references) so subagent briefs include the run directory, then update tests and the case if needed. Done when the text and tests are updated, ready for a re-run.

**Why it matters:** Proves the harvester is used when subagents search.

**Why an agent:** a skill-text fix against a traced failure

**Status when filed (partly-done):** later commits (aec8b25, 2d835c7) touched the skill; the case was not re-run after wave 3
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
No skill, spec or test change was needed: the wave-3 failure traced to the grader. At that run, `harvester-used` required the run directory in every subagent prompt (the grader text saved with that run's local results says so); the grader as first committed, in 49b1ff9, asks it only of subagents that searched the literature routes, which is what PRIOR-SCR-101, the LLD, `SKILL.md` and `references/harvester.md` say. Verified against the wave-3 trace (run `claude-eval-JGSmlT`, local to the machine that ran it): all 12 subagent prompts carried the rules block; the 5 literature subagents each got the harvester command and the run directory; the 7 software subagents sent nothing to arXiv, OpenAlex or Semantic Scholar. The `latest-results.md` row stays as it is until the AD-43 re-run replaces it. Risk: the rules block still tells a software-only subagent about a harvester command it is not given; the trace shows no harm from that.
<!-- SECTION:FINAL_SUMMARY:END -->
