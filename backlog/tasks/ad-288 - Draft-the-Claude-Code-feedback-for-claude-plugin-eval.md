---
id: AD-288
title: Draft the Claude Code feedback for claude plugin eval
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/claude-plugin-eval.md
priority: medium
type: upstream
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft feedback for Claude Code's `claude plugin eval` (channel: the /feedback command, per the entry) from docs/tool-feedback/claude-plugin-eval.md: gitignored files count toward the 20,000-entry cap; a judge sees only the first 100,000 characters of a trace; results go inside the plugin directory (wants --results-dir); and the sandboxed shell can't write when the run temp dir is under /tmp (//tmp is in denyWrite; TMPDIR workaround). Done when drafts are shown inline for approval.

**Why it matters:** Would let evals run from the repo root without a copy and with trustworthy judges.

**Why an agent:** text from recorded evidence
<!-- SECTION:DESCRIPTION:END -->
