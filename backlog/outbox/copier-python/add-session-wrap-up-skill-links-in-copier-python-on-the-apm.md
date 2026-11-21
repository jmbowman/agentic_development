---
title: Add session-wrap-up skill links in copier-python on the apm bump PR
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- surfaced
references:
- docs/high-level-design.md#Key Design Decisions (Template skills are pinned by the template)
- copier-python:docs/high-level-design.md:87
- copier-python:docs/intent/baseline-files/baseline-files-design.md:213
- copier-python:template/.claude/skills/
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
external_blockers:
- github.com/jmbowman/agentic_development#AD-22
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A skills package release that adds a skill needs a hand edit to the template's links on Renovate's apm bump PR (HLD: 'APM doesn't create the links'). Add `template/.claude/skills/session-wrap-up` and `template/.agents/skills/session-wrap-up`, each a link to `../../.config/copier-python/.claude/skills/session-wrap-up`, beside the existing prior-art-search and LID links, and update whatever the template tests expect. Check whether the release's subagent-notes hooks or the harvester need baseline support (baseline-files deferred item 6). Done when the bump PR's CI passes and it merges.

**Why it matters:** Consumers get the session wrap-up skill without installing the plugin by hand.

**Why an agent:** a mechanical link and test update on an existing PR branch

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
