---
id: AD-252
title: Spike mdBook with Pagefind and frontmatter rendering on sample pages
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-8
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/54
  - docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md#Verdict
  - >-
    docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md#Limitations
    checked in source
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #54 task 2: on a sample of IWE/OKF pages, try mdBook with a Pagefind theme override (built-in search disabled via [output.html.search] enable = false) and mdbook-frontmatter-render. Check how Pagefind's index refresh fits the mdbook serve loop. Report findings in a note. Agents search the Markdown directly, not Pagefind, per the 2026-10-25 comment.

**Why it matters:** Validates the verdict before wiring it into the template.

**Why an agent:** hands-on spike with a clear check list
<!-- SECTION:DESCRIPTION:END -->
