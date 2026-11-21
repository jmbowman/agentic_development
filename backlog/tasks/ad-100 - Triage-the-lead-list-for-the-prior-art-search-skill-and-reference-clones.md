---
id: AD-100
title: Triage the lead list for the prior-art-search skill and reference clones
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
    docs/prior-art/2026-11-05-leads-from-source-calibration.md#Additions to
    earlier notes
priority: low
type: search
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Unverified leads from the calibration note: papers RepoReuse (arXiv 2609.35357), Package Hallucination via Rule Files (2610.09264), We Have a Package for You (2406.10279), Do AI Coding Assistants Check Before They Install (2609.07754), LLM Agents Can See Code Repositories (2606.14061), For Coding Agents the Repository Matters (2606.28235), The Code of Theseus (2610.20068); and repos rianczerwinski/prior-art-skill, the `patent` crate, all-repos, git-get, ham, gitopolis, ripvcs. Read abstracts, classify each (borrow ideas / reject), and feed anything that affects the skill's verification rules into issue #156 or #159. Done when each lead has a one-line verdict. Reference clones were since re-searched in the 2026-11-06 note, so check it first.

**Why it matters:** Evidence for the search-before-build and verification steps.

**Why an agent:** Reading abstracts and repos read-only

**Status when filed (partly-done):** 2026-11-05 leads note names RepoReuse etc.; grep finds RepoReuse only in the leads note and the 11-04 note, so unread; the reference-clones leads may be consumed by the 2026-11-06 note (outside my sources).
<!-- SECTION:DESCRIPTION:END -->
