---
id: AD-270
title: Adopt extant and blockwatch for knowledge-base drift checks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-268
references:
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md#Verdict
  - docs/tool-feedback/extant.md
  - docs/tool-feedback/kontext.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adopt extant (checks commit SHAs, branches, paths and links that docs cite, over documents listed in .extant.toml, so each knowledge page must be listed) and blockwatch (explicit anchors whose affects target must change with them), with kontext as an optional time-based staleness check once published. Check whether extant's glob support (docs/tool-feedback/extant.md) removes the one-by-one listing. Doctrine's staleness-as-commits-since-SHA idea can be tried beside them.

**Why it matters:** Catches knowledge pages that cite things which no longer exist.

**Why an agent:** tool adoption
<!-- SECTION:DESCRIPTION:END -->
