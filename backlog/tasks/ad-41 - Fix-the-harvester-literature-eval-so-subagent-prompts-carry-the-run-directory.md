---
id: AD-41
title: Fix the harvester-literature eval so subagent prompts carry the run directory
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - process
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/review-log.md:90
  - evals/prior-art-search/latest-results.md
  - evals/prior-art-search/harvester-literature
priority: high
type: feature
performer: agent
agent_tier: strong
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review-log 2026-11-15 Evals wave 3: with TMPDIR outside /tmp the harvester ran 13 times, but `harvester-used` failed because the software subagents' prompts lacked the run directory; one fork was put to the developer. latest-results.md shows harvester-literature at 1 run, 1 failed. Fix the skill text (skills/prior-art-search/SKILL.md or references) so subagent briefs include the run directory, then update tests and the case if needed. Done when the text and tests are updated, ready for a re-run.

**Why it matters:** Proves the harvester is used when subagents search.

**Why an agent:** a skill-text fix against a traced failure

**Status when filed (partly-done):** later commits (aec8b25, 2d835c7) touched the skill; the case was not re-run after wave 3
<!-- SECTION:DESCRIPTION:END -->
