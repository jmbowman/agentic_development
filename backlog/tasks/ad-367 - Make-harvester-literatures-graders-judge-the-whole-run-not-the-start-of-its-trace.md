---
id: AD-367
title: >-
  Make harvester-literature's graders judge the whole run, not the start of its
  trace
status: To Do
assignee: []
created_date: '2026-11-26T02:08:51Z'
labels:
  - loose-end
milestone: m-3
dependencies: []
references:
  - docs/tool-feedback/claude-plugin-eval.md
  - docs/review-log/2026-11-25-prior-art-search-harvester.md
  - evals/prior-art-search/harvester-literature/graders
  - evals/README.md
  - AD-288
  - AD-363
priority: medium
type: search
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: created
    date: '2026-11-25'
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `llm` graders of `harvester-literature` (`harvester-used`, `harvester-output`, `own-requests-paced`) read a trace that the runner cuts at about 100,000 characters. The 2026-11-25 run wrote 1.9 MB; the part the judges saw ended while the main agent was still reading the skill's reference files, before any subagent or harvester command, so their FAIL votes and their PASS votes both mean nothing. Each run of the case that reached the harvester has been triaged by hand against the kept `out/trace.jsonl` with ad hoc `jq` commands, and the round rules added on 2026-11-25 (PRIOR-SCR-136 to PRIOR-SCR-146) are verified only by this eval. The other online full-method cases with subagents have the same exposure.

Two directions, not exclusive, to weigh before building anything:
- a check over the kept trace that decides the mechanical conditions (which hosts got requests and whether each went through `harvest.py`; anything from `arxiv.org` other than a `/pdf/` or `/html/` page; one `--run-dir` and its presence in each literature subagent's prompt; the gaps between a harvester run and an agent's own request; harvester files read whole or filtered), leaving judgment calls (a serious candidate, a later round, a matching lookup title) to a judge or a person;
- making the trace the judges get small enough to matter: a case shaped to produce less (fewer routes or rounds, a narrower prompt), or the evidence reduced before judging (tool calls and results without the system and message noise), which the tool-feedback entry also proposes upstream.

Start with a prior-art search for trace-checking and trace-reduction tools for agent evals, and check what `claude plugin eval` already offers for grading from a script or from a reduced trace.

**Why it matters:** until this is fixed the case can pass or fail only by hand, and every re-run costs a manual triage.

**Why an agent:** a search, then a design proposal for the developer to rule on
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A prior-art note records what exists for checking or reducing an agent eval's trace, and what the runner itself offers
- [ ] #2 The developer has a proposal that names one direction or both, with what each grader condition would then be decided by
- [ ] #3 The chosen direction has its own tasks, or this one is extended to build it
<!-- AC:END -->
