---
id: AD-199
title: Apply the review-wave loop to this repo as an interim rule
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-28T03:18:28Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-140
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
  - docs/decisions/review-wave-stopping.md
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 7266f96f-11b4-409a-94b6-febeac87bf64
    role: worked
    date: '2026-11-27'
  - agent: claude-code
    id: 7266f96f-11b4-409a-94b6-febeac87bf64
    role: finished
    date: '2026-11-27'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Until AD-372 decides how process guidance ships to template consumers, apply the loop in docs/decisions/review-wave-stopping.md to this repo only, so sessions here (such as those improving the prior-art-search skill) run under it. Its selected option and "What it obligates" list are the source of truth: point to them from AGENTS.md rather than restating them loosely. Bring AGENTS.md's Commits, LID stop cadence, Spec-review findings, Subagents and Review log rules in line with the loop, and add what running it here showed: fresh reviewers over the whole change as it stands each wave; briefs that say reporting nothing is acceptable and not to report what costs more to fix than it is worth for the intended uses, and that carry the findings triage rejected (with reasons) and deferred (with task IDs); a triage agent separate from the reviewers and the change's author that holds each finding to the worth-a-wave bar on its own and rules on problems the change exposes in untouched text by their harm; cascade briefs that check which tasks the change makes ready (the task tool's why command) and whether what one task builds supplies what another reads; a snapshot of the reviewed tree per wave, so triage can check its fix-caused tags. Per AD-369's ruling, questions during a loop lead with the finding and only the context needed to answer it, and the final stop leads with the artifact. Extend docs/review-log/README.md to record per wave the findings raised, accepted, deferred and rejected and how many accepted ones the previous fixes caused, and settle how a finding fixed by creating or editing a task is counted. Say that the portable form waits on AD-372.

**Why it matters:** Sessions here keep running the old single-wave rule until AGENTS.md says otherwise.

**Why an agent:** AGENTS.md and README text, reviewed under the loop itself
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
created: 2026-11-28T02:33:33Z

---

Brief and triage notes from the AD-140 review loop (ten waves, 2026-11-26), for the AGENTS.md rules this task writes: (1) the backlog CLI renames a task's file when its title changes, so `git diff HEAD` shows a deletion plus an untracked file; tell reviewers to compare with `git show HEAD:<old path>`. (2) A slice's `git diff HEAD` can overflow the inline output; run `--stat` first, then read the files. (3) Triage briefs quote the decision doc's definitions word for word and say which wave made each recent edit: a paraphrase that counted rulings not carried into other files as fix-caused tripped a false escalation, and fix-caused tags depend on knowing when each edit landed. (4) Settle how a finding triage splits into a fix and a fork is counted in the log.

---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
AGENTS.md gains a Review waves rule that applies docs/decisions/review-wave-stopping.md to this repo as an interim rule, pointing to the decision doc as the source of truth for the stop, escalation and definitions; the portable form waits on AD-372. Its five steps: a per-wave snapshot in tmp/review-waves/ that also keeps findings and triage rulings; fresh full-scope reviewers whose briefs name intended uses, say nothing is a good outcome and carry rejected and deferred findings; a separate triage agent holding the worth-a-wave bar and ruling on exposed untouched text by harm; fork rulings first, then the stop, escalation and apply checks in that order (deferral tasks need no wave, per the developer); a final stop that leads with the artifact (AD-369). The Commits, LID stop cadence, Spec-review findings, Review log, README and Subagents rules now follow the loop (untracked files, renamed task paths, --stat first). docs/review-log/README.md now records Accepted, Deferred, Rejected and Fix-caused per wave, defines restarts and escalation notes, and settles how task-edit fixes and split fix-and-fork findings are counted. Verified by mise run check and tasks check passing, and by four review waves under the rule itself (docs/review-log/2026-11-27-review-waves.md): 6, 1 and 1 accepted, then none. Risk: the escalation thresholds are still guesses (AD-370).
<!-- SECTION:FINAL_SUMMARY:END -->
