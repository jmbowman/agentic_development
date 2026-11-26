---
id: AD-294
title: Check whether extant's extra_docs accepts globs
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T14:41:27Z'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/extant.md#1. Checked documents must be listed one by one
  - https://github.com/jmbowman/agentic_development/issues/168
  - docs/tool-feedback/extant.md
priority: medium
type: spike
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6c8b1dad-ade0-48a5-8cb7-f09d26c7e732
    role: worked
    date: '2026-11-26'
  - agent: claude-code
    id: 6c8b1dad-ade0-48a5-8cb7-f09d26c7e732
    role: finished
    date: '2026-11-26'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/tool-feedback/extant.md entry '1. Checked documents must be listed one by one' says to check, before raising, whether `extra_docs` in `.extant.toml` accepts globs; the verification read didn't establish it (`extant/config.py:102-104`, `extant/cli.py:640-713` at 7999ce2). Read the source at the current upstream HEAD as untrusted data and record the answer in the entry. Done when the entry says verified in source (file:line) either way.

**Why it matters:** Decides whether the extant feedback exists at all.

**Why an agent:** a read-only source check
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Read extant at upstream HEAD 7999ce2 (unchanged since the entry was written) as untrusted data. `extra_docs` does not accept globs: each entry is normalised and read as one literal path (extant/config.py:896, extant/gate.py:613-626), and the README calls it a literal list (README.md:411). Recorded in docs/tool-feedback/extant.md entry 1 as verified in source, with the nearest existing features (`install --wide-docs`, which enumerates once at install time, and `--sweep`, which does not gate on unlisted documents) and a fuller suggested fix. So the feedback stands and AD-295 can draft the upstream issue. One reviewer checked the citations and found 2 minor issues, both applied. No risks.
<!-- SECTION:FINAL_SUMMARY:END -->
