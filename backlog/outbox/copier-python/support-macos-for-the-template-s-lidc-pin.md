---
title: Support macOS for the template's lidc pin
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/local-checks/local-checks-design.md:105
- copier-python:docs/intent/local-checks/local-checks-specs.md:8
- README.md:48
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python pins `lidc` with an `asset_pattern` that selects only the Linux x86_64 binary (CHECKS-TOOL-002), and defers a per-platform pattern until a macOS user needs it. agentic_development's README says the prior-art harvester supports Linux or macOS, so a macOS consumer would have the skill but no `lid` check. Done when the fragment selects the right binary per platform, with a spec and test, or the item is closed.

**Why it matters:** Removes a Linux-only assumption the system README doesn't state for consumers.

**Why an agent:** config plus a test

**Also waits on (not tracked as a task):** A macOS consumer needs it

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
