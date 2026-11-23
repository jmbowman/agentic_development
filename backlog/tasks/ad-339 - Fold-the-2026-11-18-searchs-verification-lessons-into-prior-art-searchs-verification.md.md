---
id: AD-339
title: >-
  Fold the 2026-11-18 search's verification lessons into prior-art-search's
  verification.md
status: To Do
assignee: []
created_date: '2026-11-22T00:15:00Z'
updated_date: '2026-11-23T00:03:00Z'
labels:
  - loose-end
milestone: m-3
dependencies: []
references:
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
priority: medium
type: chore
ordinal: 30000
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d7b6ac42-ae0a-43d4-910b-471bd3b28ac7
    role: created
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The parallel-session search (docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md) found gaps in skills/prior-art-search/references/verification.md. Walk the change through LID like any skill change.
- Unreachable originals: stablyai/orca returned 404 from the GitHub API, github.com, git ls-remote and jsDelivr on 2026-11-18, and loaded again on 2026-11-19, after the search had rejected it for having no reachable original. A 404 for a repo that registries, packagers or search results still list as live may be temporary, so retry on a later day before classifying it. Comparing LICENSE blob IDs (git ls-remote, then a blobless shallow fetch) told mirrors from the upstream cheaply. A matching package.json version didn't show that a copy was current.
- Renames: `gh api repos/<owner>/<repo>` follows renames without saying so. Compare the returned `full_name` with the path you asked for before counting two names as separate candidates or lookalikes.
- License added terms: the keyword grep flags standard Apache-2.0 and AGPL wording ("additional terms", "Notwithstanding") in every file. Comparing each file with the canonical text (`gh api licenses/<spdx-id>`) and reading only the mismatches by eye found the real added terms.
- Claims that a tool never does something: the decisive evidence that workmux can merge with no per-merge command was in a bundled skill's text, not its code. Clash's "writes nothing" claim turned on a dependency (gix `merge_trees` writes loose objects). Listings for such claims need to cover bundled skills and prompts, and the dependency calls on the claim's path.
- grep can be ugrep: a listing whose pattern starts with `-` needs `-e`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 verification.md covers retrying a forge 404 before classifying, checking renames, comparing a license with its canonical text, and what an absence-of-action listing must cover
- [ ] #2 mise run check passes
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: a83d57b3-ccde-4032-8a68-b0d049aa9a66
created: 2026-11-23T00:03:00Z

---

The generated-views search (docs/prior-art/2026-11-19-generated-views-over-markdown.md) made two absence claims that its review overturned. mdsmith "has no command that prints a view" rested on a listing of `docs/reference/cli/` whose scope covered `export.md`, which does exactly that. "mq queries can run commands" missed the default sandbox described further down the same CLI help. Both surfaced only when a reviewer read the tool's whole command and flag reference. For acceptance criterion #1: an absence listing is read in full, not only searched for the expected names.

---
<!-- COMMENTS:END -->
