---
title: Ship .gitattributes for generated files in the copier-python template
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Have the copier-python template render a `.gitattributes` marking lock files and sidecars `linguist-generated`, so every generated project hides generated noise in review. PortaBase needs the same file separately. Done when a rendered project contains it and a test pins it.

**Why it matters:** Reduces review noise across all generated repos.

**Why an agent:** Template change

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
