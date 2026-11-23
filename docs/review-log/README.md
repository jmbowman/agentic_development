# Review log

The yield and cost of each review wave, eval run and run of interactive scenarios, so that the point of diminishing returns can be judged from data. The agent that ran one adds its row once the findings are triaged, to the file for that day and component. Separate files mean sessions working in parallel, in separate worktrees on different components, never edit the same file. Waves up to 2026-11-22 are rows of [history-to-2026-11-22.md](history-to-2026-11-22.md), which isn't added to.

**Naming.** `<date>-<component>.md`, in lower case with hyphens: the date the wave was triaged, and the component's segment or skill name. A later wave of the same component on the same day adds a row to that file; one on another day starts a new file. Sorting the names sorts the files by date.

**Content.** The table header, then one row per wave in the order they ran, so each file renders alone:

```markdown
| Date | Component | Phase | Wave | Lenses | Found | Applied | Forks | Wrong | Tokens | Time |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | example (AD-1) | Code | 1 | what the reviewers looked at; what was applied, skipped and put to the developer | 10 | 8 | 1 | 1 | 120k | 2.5 min |
```

**Columns.** *Found* counts findings after removing duplicates. *Applied* counts those acted on. *Forks* counts those put to the developer as a choice between readings. *Wrong* counts findings that failed verification against the text or its sources. Tokens and time are the reviewing subagents' totals; parallel reviewers' times are not added. For eval rows, the cost column is the runner's reported dollars instead of tokens. A scenarios row has phase *Interactive*, and records a scenario as passing only when it passed in three runs of the same skill text; otherwise it gives how many runs failed.

To read the whole log as one table, take that file's table, then the rows of the others: `tail -qn +3 docs/review-log/2*.md`.
