---
id: AD-331
title: >-
  Decide whether knowledge-base index pages are tracked files or computed on
  read
status: To Do
assignee: []
created_date: '2026-11-20T03:11:00Z'
labels: []
milestone: m-8
dependencies: []
priority: low
type: decision
ordinal: 18000
references:
  - docs/prior-art/2026-11-19-generated-views-over-markdown.md
  - docs/high-level-design.md
  - AD-264
  - AD-326
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Knowledge-base index pages, such as a page listing every decision doc by its H1 title, can be kept two ways (docs/prior-art/2026-11-19-generated-views-over-markdown.md, Verdict). Both use the same allowlisted mq view, run by the custom view tool that AD-326 plans, so mq is pinned either way.

- **Computed on read:** the view tool, as an mdBook preprocessor, runs the view when the site is built, and nothing is committed. This follows HLD tenet 10 as written. But the index exists only on the built site, not when the repo is read on GitHub or in an editor, and there is no index page at all until AD-326's docs site and view tool exist.
- **Tracked:** the view tool's `sync` mode writes the view between markers in a committed page, and its `check` mode in prek and CI fails when the page is stale. The index then reads the same on GitHub, in an editor and on the site. But every new or retitled decision doc also changes the index page, tenet 10 ("computed when read, not written into files") needs an exception for it, and the view tool needs those two modes and a place in prek and CI.

AD-264's SessionStart hook is needed either way: it puts decision titles into the agent's context at session start, which a page doesn't do. What it depends on is where it gets the titles. Computed on read, it runs the mq view itself, so mq runs at every session start. Tracked, it can print the committed page's region and needs no mq at session start.

Done when the developer has ruled, and the ruling is recorded in the HLD (tenet 10's wording, if tracked index pages are allowed).

Done when the developer has ruled, and the ruling is recorded in the HLD (tenet 10's wording, if tracked index pages are allowed).
<!-- SECTION:DESCRIPTION:END -->
