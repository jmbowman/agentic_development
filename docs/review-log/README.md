# Review log

The yield and cost of each review wave, eval run and run of interactive scenarios, so that the point of diminishing returns can be judged from data, and the review loop's escalation thresholds revisited ([the review-wave decision](../decisions/review-wave-stopping.md)). The agent that ran one adds its row once the findings are triaged, to the file for that day and component. Separate files mean sessions working in parallel, in separate worktrees on different components, never edit the same file. Waves up to 2026-11-22 are rows of [history-to-2026-11-22.md](history-to-2026-11-22.md), which isn't added to.

**Naming.** `<date>-<component>.md`, in lower case with hyphens: the date the wave was triaged, and the component's segment or skill name. A later wave of the same component on the same day adds a row to that file; one on another day starts a new file. Sorting the names sorts the files by date.

**Content.** The table header, then one row per wave in the order they ran, so each file renders alone:

```markdown
| Date | Component | Phase | Wave | Lenses | Found | Accepted | Deferred | Rejected | Forks | Fix-caused | Wrong | Tokens | Time |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-27 | example (AD-1) | Code | 2 | what the reviewers looked at; what was accepted, deferred (with task IDs), rejected and put to the developer | 10 | 3 | 1 | 6 | 1 | 1 | 2 | 120k | 2.5 min |
```

**Columns.**
- *Wave* is the wave's number since the loop began. After an escalation, the developer's ruling to patch or rework restarts the count toward the wave limit: from then on the cell also gives the restart's number and the wave's number since it, as in `7 (restart 1, wave 2)`. A wave that escalated says so in *Lenses*, with the trigger (wave limit or fix-caused) and the developer's ruling (patch, rework or stop).
- *Found* counts findings after removing duplicates. Each one is counted once in exactly one of *Accepted*, *Deferred* and *Rejected*, so those three add up to *Found*.
- *Accepted*, *Deferred* and *Rejected* are triage's rulings: fix now, record as a backlog task, or not worth it in this project. A fork counts under the ruling the developer gives it, which is *Accepted* when they rule fix now, so a wave's row is written once its forks are ruled.
- A finding fixed by an edit the change itself makes, a new or edited task included, is *Accepted*, since the next wave reviews that edit. One whose fix is left to a backlog task, new or existing, done after this change, is *Deferred*.
- A finding triage splits into a fix and a fork is still one finding: it is *Accepted* if any part of it is fixed now, and it counts under *Forks* too.
- *Forks* counts findings put to the developer as a choice between readings.
- *Fix-caused* counts the accepted findings that the previous wave's fixes caused, as the decision doc defines them.
- *Wrong* counts findings that failed verification against the text or its sources; they are among the *Rejected* ones.
- *Tokens* and *Time* are the reviewing and triage subagents' totals; parallel reviewers' times are not added. For eval rows, the cost column is the runner's reported dollars instead of tokens.
- Eval and scenarios rows fill the triage columns only where their results were triaged that way, and put `–` elsewhere. A scenarios row has phase *Interactive*, and records a scenario as passing only when it passed in three runs of the same skill text; otherwise it gives how many runs failed.

Older files, and the history file, use an earlier header: *Applied* in place of *Accepted*, *Deferred* and *Rejected*, and no *Fix-caused* column. To read the whole log as one table, take that file's table, then the rows of the others: `tail -qn +3 docs/review-log/2*.md`; check each file's header before reading the counts across files.
