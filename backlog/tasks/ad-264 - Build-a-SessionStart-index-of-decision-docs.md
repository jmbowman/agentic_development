---
id: AD-264
title: Build a SessionStart index of decision docs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-331
references:
  - docs/prior-art/2026-11-06-decision-records-and-lid.md#Verdict
  - docs/tool-feedback/lid.md#4. Deliver decisions to the agent
  - docs/prior-art/2026-11-19-generated-views-over-markdown.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A SessionStart hook of about 20 lines listing both decision folders (project-level and per-segment under docs/intent/) with each doc's H1 title, so agents know decisions exist without opening each. It ports pi-adr's idea and needs no LID change; the title names the topic, not the outcome. Where the hook gets its titles waits on AD-331: if index pages are computed on read, it runs the same allowlisted mq view the docs site uses (docs/prior-art/2026-11-19-generated-views-over-markdown.md, Verdict); if they are tracked, it prints the committed index page's region. Done through LID with fixtures that the hook prints nothing when there are none and does not echo untrusted text as instructions.

**Why it matters:** Agents rarely read stored context on their own; delivery by the harness works.

**Why an agent:** small hook with tests
<!-- SECTION:DESCRIPTION:END -->
