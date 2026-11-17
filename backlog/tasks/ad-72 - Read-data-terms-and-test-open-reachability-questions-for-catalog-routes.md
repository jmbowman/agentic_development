---
id: AD-72
title: Read data terms and test open reachability questions for catalog routes
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
  - partly-done
milestone: m-3
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-04-agent-readable-catalogs-and-paper-sources.md#Limitations
    checked in source
  - skills/prior-art-search/references/sources.md
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The catalogs note could not verify: data terms of Homebrew and nixpkgs index files, LibHunt, PulseMCP and Glama's attribution requirement (read before bulk caching or quoting); Crossref's `type` filter; PulseMCP's robots rules under a strict reading of its second `*` group; arXiv's one-request-per-3-seconds rule (recalled, not re-read); OpenAIRE's exact endpoint and recipe. Read or test each and update skills/prior-art-search/references/sources.md. Done when each is verified or marked unverifiable in sources.md.

**Why it matters:** Keeps the skill's route list inside each service's terms.

**Why an agent:** Reading terms and running curl tests

**Status when filed (partly-done):** sources.md already carries the verdict's routes (OpenAIRE, Crossref, Homebrew etc., commit 02137cf); which could-not-verify items were closed is unchecked. Issue #158 (open) covers other route guidance but not these.
<!-- SECTION:DESCRIPTION:END -->
