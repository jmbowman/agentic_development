---
title: Trial RapidCheck properties for PortaBase ROW-DB specs under QTest
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use RapidCheck (BSD-2-Clause) inside QTest through `QVERIFY(rc::check(...))` (it has no QTest integration; `rc::check` returns bool). First candidates are PortaBase ROW-DB-002, -011 and -012: one property or one stateful model of add, delete and compress against a list of IDs would replace three hand-built `_data` rows. Done when one property replaces those rows and builds under qmake.

**Why it matters:** Fewer, stronger tests to review in the C++ app.

**Why an agent:** Code spike in a repo with its own session

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
