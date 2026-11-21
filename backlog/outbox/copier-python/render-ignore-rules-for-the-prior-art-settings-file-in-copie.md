---
title: Render ignore rules for the prior-art settings file in copier-python
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- issue
references:
- https://github.com/jmbowman/copier-python/issues/69
- copier-python:docs/intent/baseline-files/baseline-files-design.md:213
- docs/intent/prior-art-search/prior-art-search-design.md:533
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
external_blockers:
- copier-python/decide-how-rendered-repos-ignore-the-prior-art-settings-file
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the choice from the #69 decision: add `.config/prior-art-sources.toml` (and `inbox/` if adopted) to the ignore rules the template renders, each with a short comment, with EARS specs and a rendering test that `git check-ignore` matches the paths in a fresh copy and after an update. This is the first of the 'skill supporting baseline files' that baseline-files deferred item 6 anticipates. Done when the template tests pass and README mentions it if user-visible.

**Why it matters:** Closes the prior-art-search design's deferred template follow-up.

**Why an agent:** a small template change once the location is decided

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
