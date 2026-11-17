---
id: AD-305
title: Draft the upstream issues for vendir feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/vendir.md
  - docs/prior-art/2026-11-06-agent-reference-clones.md
priority: medium
type: upstream
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft issues for carvel-dev/vendir from docs/tool-feedback/vendir.md (0.46.3): 1. a locked or pinned SHA that isn't a tip can't be fetched at shallow depth (`git.go:186-197,236-241`); 2. every tag is fetched even for a branch ref (`git.go:181`; the 63 s vs 8.4 s qtbase measurement); 3. no default-branch ref (`origin/HEAD` fails); 4. kept .git/config points at a deleted credentials file. Include the tested GIT_CONFIG workaround. Done when drafts are shown inline.

**Why it matters:** The chosen reference-clone manager needs shallow, locked restores to work.

**Why an agent:** text from recorded evidence
<!-- SECTION:DESCRIPTION:END -->
