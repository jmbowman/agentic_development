---
id: AD-166
title: Build the reviewer eval corpus from this repo's escapes and seeded defects
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-163
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#15.
    Evaluating the process itself
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 3: mine this repo's history for defects that review missed and evals or the developer later found (escapes), add settled clean changes for false-alarm scoring, have the developer confirm each case, and add seeded defects while history is thin. Method from layered-code-review (revert-mined cases, finding classes fixed/wrong/intentional/not important) and craftsman's seeded suite. Done when a scorer reports recall and clean false-alarm rate per lens.

Seed escapes from AD-5's walk of the task-tracker LLD (2026-11-17 to 2026-11-19): design gaps the developer raised after the agent's draft and its edge-case probe had passed them. Each is a case where a reviewer of the draft LLD should have flagged the gap: milestones carrying no workstream description, importance or relations; no task type for prior-art searches, which hid inside `spike`; no record of the sessions that worked on a task; Backlog.md's `documentation` key overlapping `references`; Backlog.md's `docs/` and `decisions/` folders ignored without a recorded reason; no way to render the backlog in the docs site; task IDs colliding across developers and machines; and the draft's archive rule contradicting Backlog.md's (archived meant dropped, where Backlog.md archives finished tasks too). Only some intermediate drafts were committed, so the gaps are listed here; a case can be rebuilt by removing the fix from the LLD in docs/intent/task-tracker/task-tracker-design.md. Several came from the developer's uses and from other planned work rather than from the text, which is what AD-330's design-input steps target.

**Why it matters:** Every later reviewer change is judged against it.

**Why an agent:** corpus building and scorer code; the developer only confirms cases
<!-- SECTION:DESCRIPTION:END -->
