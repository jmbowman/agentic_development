# Prior art: a prior-art search skill (2026-10-17)

Written before the skill's note template existed, so it has no matrix and cites licenses without a line or commit.

## Need

An agent skill that, before an agent recommends building or substantially extending a tool, library, script or subsystem, runs an auditable search for existing software, classifies candidates (adopt / build on / borrow ideas / reject), verifies claimed limitations in source for the top 2-3, and persists a dated note with the query log. It must be reusable from any repo and work in Claude Code cloud sessions.

## Verdict

**Build, borrowing ideas.** Twelve skills do some version of "search before you build". None verifies limitations in source with file:line tags, persists an auditable query log in the host repo, and reads the license file rather than API metadata. Their ideas cut the design work.

## Candidates

All candidates' licenses were read from the `LICENSE` file at the repo root (via `gh api` or a read-only clone).

| Candidate | License | Class | Reason |
|---|---|---|---|
| [user-w-ui/search-before-build](https://github.com/user-w-ui/search-before-build) (`assess`, `quick-search`), 131★, pushed 2026-10-17 | MIT | borrow ideas | Closest method. It has a source coverage ledger with route triggers and a route audit before stopping, support enums with `unverified` kept distinct from `unsupported`, and "nothing close in N routes" wording. But it targets non-expert product ideas (necessity gates, an HTML viewer, Chinese/English defaults) and never writes to the project. |
| [ghspain/github-build-or-reuse](https://github.com/ghspain/github-build-or-reuse), pushed 2026-09-17 | MIT | borrow ideas | Treats repo content as untrusted, has license triage with PASS/UNKNOWN, hard gates that override scores, and behavioural evals (Waza) separate from static validation. It is GitHub-first, takes license from `gh` metadata, and has no source-reading or persistence step. |
| [kwonzweig/there-is-a-tool-for-that](https://github.com/kwonzweig/there-is-a-tool-for-that) (`find-tools`) | MIT | borrow ideas | Short and well judged. "Before saying nothing fits, try the new terms and one more search route." It also says that popularity tells you where to look, not whether a tool works. No structure for classification, logging or persistence. |
| [fahrellgiovanny/nothing-new-under-the-sun](https://github.com/fahrellgiovanny/nothing-new-under-the-sun) | MIT | borrow ideas | One-way vs. two-way doors to set the confidence bar, a re-evaluation trigger, a "missing information" section and compound recommendations. Business-value framing (TCO, strategic value) doesn't fit tooling choices. |
| [Emanuelel/dont-reinvent](https://github.com/Emanuelel/dont-reinvent), 39★ | MIT | borrow ideas | Treats a repo with no license as reference-only rather than discarding it, has a "Verified / Could not verify" footer, and says to diagnose a failing tool before calling a source unavailable. It requires two MCP connectors. |
| [LpcPaul/tool-scout-skill](https://github.com/LpcPaul/tool-scout-skill) | MIT | borrow ideas | Audits native features before external search, and uses query families (user, developer, capability and product-type wording). It needs a bundled Python script. |
| [shimo4228/search-first](https://github.com/shimo4228/search-first) | MIT | borrow ideas | Per-question-type "where to look / what counts as evidence / stop when" table; report the search range when nothing turns up; mark full-text vs. snippet reads. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) `search-first` | MIT | reject | Generic; adds nothing beyond the above. |
| [vadim-a-yegorov/principle-adopt-fork-build](https://github.com/vadim-a-yegorov/principle-adopt-fork-build) | MIT | reject | GitHub-first with stop-and-confirm phases; its one idea, reading 1-3 implementation files, is already in the method. |
| [meetziggy/repohunter](https://github.com/meetziggy/repohunter) | MIT | reject | MCP heuristic scoring over GitHub stats; a scorer, not a method. |
| [gaupoit/programming-advisor](https://github.com/gaupoit/programming-advisor) | MIT | reject | Web-search query templates and token-burn estimates; shallow. |
| [ShanedevPro/dont-reinvent-the-wheel-skill](https://github.com/ShanedevPro/dont-reinvent-the-wheel-skill) | MIT | reject | Prompts only; covered by the above. |

Skills for writing and testing skills, not candidates for the method itself: Anthropic's `deep-research` (subagent fan-out for narrative reports) and `skill-creator` (eval loop); Claude Code's `claude plugin eval` (cases plus graders, with a no-plugin baseline arm).

## Limitations checked in source

- search-before-build takes the license from GitHub's API metadata: *verified in source* (`references/github-retrieval.md:80-84`, "usually SPDX license metadata"). It has no clone or file:line step: *verified in source* (no `git clone` in `references/`). It never writes to the project: *verified in source* (`skills/assess/SKILL.md`, workflow step 9). It has no untrusted-content rule: *verified in source* (no match in `references/` or `skills/`).
- github-build-or-reuse takes the license from `gh` metadata: *verified in source* (`references/github-evidence.md:13,24`), although `references/licensing.md:3` says to verify the license text. It has an untrusted-content rule: *verified in source* (`references/github-evidence.md:48`). It has no persistence step: *verified in source* (no save, ADR or record instruction in `SKILL.md` or `references/`).
- there-is-a-tool-for-that is a single 41-line `SKILL.md` with no references: *verified in source* (repo file listing).

## Sources and queries

- GitHub repository search (descriptions and names, `pushed:>2026-01-01`), with these phrasings: "prior art skill", "build vs buy skill", "existing solutions before coding", "reinventing the wheel claude", "library selection skill", "dependency evaluation agent skill", "find existing library agent", "alternatives research skill", "search before build agent", "adopt build on borrow reject", "tool scouting agent skill", "dont reinvent", "reuse before rewrite", "existing tool search coding agent", "research-first", "spike research skill". Round 3: "evaluate open source alternatives skill", "existing solution vetting skill", "reuse-first". Round 3 added no serious candidate, so the search stopped.
- GitHub code search for READMEs that mention the top candidates (awesome-list snowball): found only catalogs (svg153/skills, LucioLiu/agent-modpack) and nothing new.
- npm `/-/v1/search`: "prior art skill", "dont reinvent wheel agent", "build vs buy". Nothing relevant; one MCP server for SaaS build-vs-buy pricing (clonetime-mcp-server).
- Web search: Claude Code prior-art and build-vs-buy skills, tech-selection skills, and awesome-claude-skills research and build-vs-buy entries. Found skills.sh, claudskills.com and skillselion listings: aakash-dhar build-vs-buy (a PM-oriented 700-line decision record), ECC skill-scout (finds skills before you write one), wpank decision-frameworks (OpenClaw).
- Not searched: PyPI and crates.io, because skills don't ship there. alternativeto.net has no category for agent skills.

## Ideas to carry into the design

1. A coverage ledger: routes triggered by the need's signals (language, MCP, agent skill), and each one either queried or excluded with a concrete reason. That makes the query log a checklist, not prose.
2. A support value per criterion: `native / partial / extensible / unsupported / unverified`. `unverified` never becomes `unsupported`.
3. One-way vs. two-way doors to choose between the quick pass and the full method, plus a refresh trigger on every recorded decision.
4. Audit native features of the existing stack before searching outside it.
5. A repo with no license is reference-only. Diagnose a failing route before you call it unavailable. End with "Verified / Could not verify".
6. Evals: static validation in CI; model-backed behaviour runs kept out of PR CI.

## Refresh trigger

2027-04-17, or sooner if Anthropic or a major skill catalog publishes a prior-art or build-vs-buy skill.
