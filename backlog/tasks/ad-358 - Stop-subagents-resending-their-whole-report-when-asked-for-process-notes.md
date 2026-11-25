---
id: AD-358
title: Stop subagents resending their whole report when asked for process notes
status: To Do
assignee: []
created_date: '2026-11-25T03:57:00Z'
labels:
  - loose-end
milestone: m-4
dependencies: []
references:
  - skills/session-wrap-up/hooks/subagent_notes.py
priority: low
type: bug
ordinal: 48000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 7491ae04-e559-4545-95a8-b20f528642de
    role: created
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Asked the hooks' fixed question ("Reply with only your process notes…"), some subagents send their whole findings report again and add the notes at the end, or leave them out. In one session, three of five notes files held a full report (17 KB, 12 KB and 9 KB), and one of those had no process notes at all. The wrap-up then reads a long report to find a few bullets, and a report's findings can pass as process notes.

**Why it matters:** notes files stay short and hold only what the wrap-up collects.

**Why an agent:** a hook and skill-text change with tests, through LID.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A notes file holds only the subagent's reply to the question, not a resent report.
- [ ] #2 A reply that restates the report is detected and handled as the design decides (asked again, trimmed or flagged), and a test covers that case.
<!-- AC:END -->
