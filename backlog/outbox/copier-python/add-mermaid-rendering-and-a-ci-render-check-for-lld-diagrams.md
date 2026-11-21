---
title: Add Mermaid rendering and a CI render check for LLD diagrams
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Follow-up quick passes (2026-10-28)
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
external_blockers:
- copier-python/wire-the-docs-site-pieces-into-the-template-mise-build-tasks
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add mdbook-mermaid (MPL-2.0; renders only for the html renderer and does not validate syntax) to the book setup and a CI check that fails on a Mermaid block that does not parse, using merman's lint or batch mode (MIT OR Apache-2.0) or mermaid-cli. Then use state, sequence-with-alt and flowchart diagrams beside LLD prose. Done when a malformed diagram fails CI and a good one renders in mdBook and on GitHub.

**Why it matters:** Diagrams in specs cut review time for experienced readers.

**Why an agent:** Tool wiring after the book setup exists

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
