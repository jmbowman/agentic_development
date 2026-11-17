---
id: AD-28
title: Correct the README status line on template skill delivery
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-17T20:36:00Z'
labels:
  - surfaced
milestone: m-2
dependencies: []
references:
  - README.md:78-82
  - copier-python commit eab605c (in v0.3.0)
  - copier-python:README.md#Skills
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's README Status says 'Delivering skills through the template, installed from a lock file, is designed and not yet released.' copier-python v0.3.0 (2026-10-28, commit eab605c) released exactly that, and copier-python's README documents it. Update the Status paragraph to say the template delivers the skills (and which ones, as of its current pin). Done when the README matches copier-python's released state.

**Why it matters:** Readers deciding whether to adopt get an accurate status.

**Why an agent:** a factual doc correction
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-17: checked against copier-python's v0.3.0 tag (eab605c, 2026-10-28), which installs template skills from a lock file. README Status corrected; what is unreleased is this repo's work since v0.3.1 (AD-22).
<!-- SECTION:NOTES:END -->
