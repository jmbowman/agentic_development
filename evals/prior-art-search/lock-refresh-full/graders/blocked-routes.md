---
type: llm
focus: trace
---

Codeberg search is selected for every software need, and the skill's `references/sources.md` says it blocks scripted clients and names General web search (`site:codeberg.org <terms>`) as the way to reach its projects. Judge from the report's and the note's coverage ledger, and from the tool calls you can see.

PASS if all hold:
- Codeberg (and any other route the ledger says blocks scripted clients) is excluded with the reason "blocks scripted clients", and no search request was sent to it;
- the alternative it names was searched for it (for Codeberg, `site:codeberg.org` web searches), and the ledger records that search, either as its own route or in the existing row of a route already selected (an alternative that ended unavailable counts like any unavailable route).
FAIL if either is broken, including a blocked route recorded as unavailable or searched.
