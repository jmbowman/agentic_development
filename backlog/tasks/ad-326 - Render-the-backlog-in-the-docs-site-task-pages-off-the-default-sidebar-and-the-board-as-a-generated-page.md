---
id: AD-326
title: >-
  Render the backlog in the docs site: task pages off the default sidebar, and
  the board as a generated page
status: To Do
assignee: []
created_date: '2026-11-18T12:55:00Z'
updated_date: '2026-11-23T00:03:00Z'
labels: []
milestone: m-8
dependencies:
  - AD-252
references:
  - docs/intent/task-tracker/task-tracker-design.md
  - docs/prior-art/2026-10-23-docs-site-search-and-graph-features.md
  - docs/prior-art/2026-11-19-generated-views-over-markdown.md#Verdict
priority: medium
type: spike
ordinal: 13000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task tracker computes its views on read (HLD tenet 10), so a board generated when the docs site is built needs no tracked or gitignored file, and custom views over the backlog can sit in the site's normal navigation. Backlog.md can keep the backlog under docs/ through backlog_directory in a root backlog.config.yml, and the task tool follows the same setting (docs/intent/task-tracker/task-tracker-design.md, Layout). In the mdBook spikes, check: task pages rendered (frontmatter shown or hidden as for notes) without hundreds of entries in the sidebar (a folded Backlog chapter, CSS, or a preprocessor that leaves them out of the navigation); the board as a preprocessor-generated page; how seiso and the link checkers treat task pages; and whether outbox drafts belong on the public site. The developer plans a preprocessor that generates useful views of task data for the site, the board among them, once the docs site is set up; the spike should find what it needs from the task tool, such as links relative to the site and a machine-readable output, rather than a second reader of the format. The generated-views search (docs/prior-art/2026-11-19-generated-views-over-markdown.md, Verdict) shapes that preprocessor as a small view tool: it uses mdBook 0.5's preprocessor protocol, replaces `<!-- view: <name> -->` markers with the output of named commands from an allowlist in its configuration (the task tool's views, and mq queries run with `--allow-read` limited to their folders and never `--allow-run`), never runs a command written in a page, and fails the build when a command exits non-zero or a page names a view that isn't in the allowlist. If AD-331 rules for tracked index pages, the same tool also needs `sync` and `check` modes that write the views into committed pages and fail prek and CI when one is stale. Done when the spike's results say which of these work, and the docs-site and task-tracker designs are updated to match.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: a83d57b3-ccde-4032-8a68-b0d049aa9a66
created: 2026-11-23T00:03:00Z

---

The task-tracker design's open item 13 (docs/intent/task-tracker/task-tracker-design.md:411) still says the generated-views note recommends a preprocessor "borrowing mdbook-cmdrun's marker". The note now recommends a small view tool that runs only an allowlist of views, with its own `<!-- view: <name> -->` marker, and never runs a command written in a page. Updating that design is part of this task's done criteria.

---
<!-- COMMENTS:END -->
