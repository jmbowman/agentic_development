---
id: AD-134
title: Write interactive scenarios for the subagent notes hooks (NOTES-LIVE)
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-5
dependencies:
  - AD-136
references:
  - docs/intent/subagent-notes/subagent-notes-specs.md:93-97
  - docs/intent/interactive-evals/interactive-evals-specs.md:36-49
  - >-
    evals/session-wrap-up/manual.md#Subagent notes in a live session
    (NOTES-LIVE-001)
  - NOTES-LIVE-001
  - NOTES-LIVE-002
  - NOTES-LIVE-003
  - IEVAL-RUN-001
  - IEVAL-RUN-002
  - IEVAL-RUN-003
  - IEVAL-MARK-006
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write the first interactive scenarios in `evals/session-wrap-up/interactive/` against pytest-claude-code-evals, checking NOTES-LIVE-001 (report unchanged and notes file written in an attended session), NOTES-LIVE-002 (`-p` result is the main agent's own last message) and NOTES-LIVE-003 (hooks registered by plugin and in `.claude/settings.json` ask only once). Each scenario starts sessions with `--plugin-dir` set to this repo's working tree, seeds working, home and config directories outside the repo, and the NOTES-LIVE-003 one seeds `.claude/settings.json` from this repo's hook entries with absolute script paths (IEVAL-RUN-001, IEVAL-RUN-002, IEVAL-RUN-003). Add a `replaces` marker only where a scenario checks every step of its manual script (IEVAL-MARK-006), deleting the replaced script and moving its results to the review log. Done when `mise run check` collects and type-checks the scenarios.

**Why it matters:** Gives the first automated check of the hooks in a real session and proves the scenario setup the other skills will reuse.

**Why an agent:** scenario code against a pinned plugin is agent work
<!-- SECTION:DESCRIPTION:END -->
