---
id: AD-111
title: Trim the subagent-notes replies to the notes only
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T05:41:00Z'
labels:
  - issue
  - partly-done
milestone: m-4
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/160
  - skills/session-wrap-up/hooks/subagent_notes.py
  - skills/session-wrap-up/references/subagent-notes-hooks.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comment on issue #160: in 4 of 8 notes files the reply to the fixed question repeated the whole subagent report despite Do not restate your report, so each notes file grew to the report's size. Check whether the resumed turn hands back through SubagentHandback with the report, and whether the question or the hook (skills/session-wrap-up/hooks/subagent_notes.py, references/subagent-notes-hooks.md) should keep only text after a Process notes heading. The main #160 request (wrap-up collects subagent notes via hooks) is done by commits fdc28f7, cfe5924, e5d1dda and aa801e1. Done means the hook or question change with a test, or a documented finding.

**Why it matters:** Keeps notes files small so wrap-up reads less.

**Why an agent:** hook and test changes with the evidence given

**Status when filed (partly-done):** hooks and wrap-up collection landed (fdc28f7, cfe5924); the reply-size observation is the remaining follow-up
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: 5129029a-6c2e-4c0b-bd91-f3da2e301b01
created: 2026-11-24T05:41:00Z

---

Happened again on 2026-11-23: one notes file of one, for a review subagent. The reply to the fixed question came back through SubagentHandback as the whole report again, with the notes appended under a "## Process notes (requested by the coordinator)" heading, so the notes file held about 80 lines of report before 5 lines of notes. A heading of that kind is what a keep-only-the-notes rule in the hook would cut at, but its wording was the subagent's own, not fixed.

---
<!-- COMMENTS:END -->
