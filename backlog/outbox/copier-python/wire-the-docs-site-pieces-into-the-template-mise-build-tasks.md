---
title: Wire the docs-site pieces into the template (mise, build tasks, auto-rebuild)
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- issue
references:
- https://github.com/jmbowman/agentic_development/issues/54
- docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: L
external_blockers:
- agentic_development#AD-251
- agentic_development#AD-252
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #54 task 4: pin tools for Renovate (mdBook via aqua; Pagefind via github: or pipx:), add a mise build/serve task, GitHub Pages publishing, an automatic rebuild after agent batches that change content, plus mdbook-mermaid and a CI merman lint. This is template work, so it belongs in copier-python. Done means a generated project builds the site with one command.

**Why it matters:** Every generated project gets the same browsable docs.

**Why an agent:** template and CI wiring after the design

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
