# Prior art: a federated, human-paced knowledge base and work-item system for project repos (2026-11-06)

- **Supersedes:** [the progressive-disclosure knowledge base note](2026-10-23-progressive-disclosure-knowledge-base.md). Its knowledge-base blend carries forward with the corrections listed under the verdict; this note adds federation, work items and cross-repo task handoff.
- **Effort:** full method, because the result would be delivered to every repo, and its page and task formats become long-lived content that is costly to migrate.
- **Already known:** everything listed in the superseded note (OpenKnowledge dropped after a trial; the LLM-Wiki family; LEANN; [Commonplace](https://github.com/zby/commonplace) as a source of ideas; IWE, the OKF tools, lat.md, hyalo and others evaluated). After that note, the developer judged [IWE](https://github.com/iwe-org/iwe) overkill, since its retrieval engine and inclusion links exceed what a lint-first blend needs, and [seiso](https://github.com/scarletkc/seiso) promising. [beads](https://github.com/gastownhall/beads) had good ideas but a large, fast-changing implementation. [Issue #54](https://github.com/jmbowman/agentic_development/issues/54) holds the docs-site plan (mdBook, Pagefind, a frontmatter renderer, a backlinks preprocessor). The public [PortaBase](https://github.com/jmbowman/portabase) repo mirrors its GitHub issues to local Markdown with [gh2md](https://github.com/mattduck/gh2md), which re-exports everything on every run and builds no index. Reference clones of other repos follow [the reference-clones note](2026-10-19-agent-reference-clones.md); refreshing that note is a separate search.
- **Omitted:** one code-search hit in a repository not known to be public was left out.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| 1. Progressive disclosure | A reader, human or agent, loads a one-screen overview, then a summary, then detail, and nothing more than the task needs |
| 2. Human-paced, human-gated | Agents propose; a person reviews the diff in git before anything durable lands. No autonomous ingestion, self-committing or branch moves |
| 3. Reorganize without broken links | Move, split and merge pages in small reviewable diffs |
| 4. Documentation quality | Typed pages and style rules that linters enforce |
| 5. Plain Markdown in the repo | Renders on GitHub and in mdBook; `SUMMARY.md` stays the only navigation hierarchy; LID's design tree keeps its own conventions and checker |
| 6. Federation | Agents in one repo find and read related repos' knowledge bases cheaply, starting from an index |
| 7. Lifecycle spectrum | Background knowledge, possible tasks, work in progress, and done work and decisions live in one system; a task's outcome becomes knowledge and a finding becomes a task, without duplication or rot |
| 8. Cross-repo "homework" | Humans and agents in one repo can record a task for another repo where that repo's agents will find and prioritize it when choosing what to do next |
| 9. Work items | GitHub Issues is good for capture but has no index, and its information fragments across the description and comments. A local mirror needs incremental sync and an index, or an in-repo tracker replaces it |
| 10. Scale of use | Many research notes, goals and strategies stay organized well enough for agents to plan parallel work and pick what to do next |

**Hard criteria:**

1. An OSI-approved license, compatible with use as an installed tool.
2. Human-gated: nothing commits, pushes, merges, stages, or rewrites content without review by default.
3. Repo files are the source of truth for knowledge and work items (a GitHub mirror may derive from GitHub).
4. Runs locally, with no required hosted service besides GitHub.
5. Coexists with mdBook and LID: no second navigation hierarchy, and no formatter that rewrites whole documents.

**Preferences:** standard relative Markdown links over wikilinks; no required frontmatter; low process overhead; checks that run in pre-commit and CI; installable and pinnable through mise and updatable by Renovate; maintenance and maturity.

## Verdict

**Inconclusive.** The search stopped after five snowball rounds, short of the prior-art-search skill's stop condition (a round that adds no new serious candidate) and its 10-round cap, with the open leads listed under Snowball rounds. The last two rounds added building blocks and design details for the pieces below, but nothing that would change the overall shape. On that evidence, the leading option is a blend: existing linters, indexers and checkers, held together by a small amount of custom glue. No candidate covers needs 7-9 on its own, and several that look close fail the human gate or the source-of-truth criterion when read in source.

**The leading blend:**

1. **Knowledge base (needs 1-5).**
   - mdBook with `SUMMARY.md` as the only hierarchy.
   - [seiso](https://github.com/scarletkc/seiso), with kinds mapped from paths in `seiso.toml` (no frontmatter needed) and each wanted preview rule enabled explicitly, because only 5 stable rules run by default.
   - rumdl (MD057) and [mdbook-lint](https://github.com/joshrotenberg/mdbook-lint) (MDBOOK005), as already used in the stack, plus [lychee](https://github.com/lycheeverse/lychee) for anchors and external links. mdbook-lint's decision-record rules (ADR001-017, on by default) treat any `decisions/` folder as MADR-style records requiring a status and a date, so they must be listed by ID under `disabled-rules` in `.mdbook-lint.toml` (at least ADR002-ADR005, which fail every LID decision doc; wildcards aren't supported).
   - The authoring rules file from the superseded note.

   Moves and splits are ordinary edits whose missed links the linters catch. No tool found does safe moves inside an mdBook tree (see [docanchor](https://github.com/E0min/docanchor) under Limitations).
2. **Agent index (need 1).**
   - [mdbook-llms](https://github.com/ttdonovan/mdbook-llms) builds `llms.txt` from `SUMMARY.md`, one heading per part. One-line descriptions come from an optional `description:` key, which issue #54's frontmatter renderer keeps off the page. `llms.txt` is **committed** and kept current by an index-freshness check, because nothing may run inside another repo's reference clone.
   - Agents get **one index level**: `AGENTS.md`/`CLAUDE.md` link `llms.txt` directly. A second routing level didn't help agents in [Is Progressive Disclosure All You Need?](https://arxiv.org/abs/2607.17598).
   - [card-catalog](https://github.com/someotherdustin/card-catalog)'s generated one-line-per-record `INDEX.md` suits record folders. It is a page listed in `SUMMARY.md` like any other, run from its CLI or a check rather than its auto-writing hook.
3. **Work items and homework (needs 7-9).**
   - **Task file.** Each repo keeps plain Markdown task files with an inbox. The format is a design choice, not settled here. Frame's files and the TASKS.md format can each be used without their tools, and a custom format can borrow from both; the trade-offs read in source are under Limitations.
   - **Leading candidate, tentative:** one Markdown file per task, plus a hand-ordered index (`TASKS.md`) holding one line per task (link and state), ordered by priority, like `SUMMARY.md` for pages.
     - **Why it leads:**
       - per-task files avoid the merge conflicts that single-file tools had to engineer around (frame's merge driver, TASKS.md's separate claims ref);
       - they leave room for detail;
       - ordering in the index keeps priority without a frontmatter field;
       - a checker can fail when a task file is missing from the index;
       - the session-start hook reads only the index.
     - It is pending a prior-art search on how current agentic development systems handle task files and work queues.
   - **Delivery of homework.** It arrives as a pull request against the receiving repo's task file. The sending agent makes the change in a separate writable checkout of the receiving repo, or creates the branch and PR through the GitHub API with `gh`, never in a reference clone, which stays read-only. Each affected repo gets its own item, as in [docflow](https://github.com/EvolveHQ/docflow)'s one plan item per affected repo. An item lands only when a person in the receiving repo merges it.
   - **GitHub Issues and the task file.** Issues hold contributor-facing work, and the task file carries only a `gh#n` reference to such an issue, never a copy. The issue mirror (item 5) is optional and built last.
   - **Task states.** offered (inbox), ready, in progress, needs-a-human, done. Done items leave the agent's brief and are archived as non-authoritative, linking to the knowledge page that records their outcome. A finding becomes a task through an inbox entry that links its page.
   - **SessionStart hook.** It prints in-progress work first, then the top ready items, then new inbox items awaiting triage, then anything needing a human, all labelled as data and with blockers verbatim. It prints one line when nothing needs action, and delivers through stdout or context, not a prompt waiting on a terminal.
   - **Ideas to borrow:**
     - [frame](https://github.com/joshsegall/frame): untriaged inbox items, position as priority, edits that touch only the changed item;
     - [task-manager](https://github.com/hk9890/task-manager): random IDs so PRs from several repos never collide, and "ready" as open with no open blockers, sorted by priority then age;
     - [TASKS.md](https://github.com/tasksmd/tasks.md): cross-repo `repo#id` blockers;
     - [komnet](https://github.com/Komdosh/komnet): agenda order (stalled, then in progress, then offered);
     - [momentum](https://github.com/LiminaLabsAI/momentum): a handoff block with summary, decisions, files touched, verification commands and open questions;
     - [repomoot](https://github.com/dev-bude/repomoot): the requester verifies the delivery;
     - [issue-graph](https://github.com/vercel-labs/issue-graph): withhold the single "next" pick, with reasons, when coverage is incomplete;
     - [md-issues](https://www.npmjs.com/package/md-issues): a generated index that a check fails when stale, and writes held until validation passes.
4. **Lifecycle and drift (need 7).**
   - **Closeout rule.** A task with a configured label can't be marked done until a knowledge page or lesson exists and the evidence that it works is recorded. [taskset](https://github.com/FalseFoundation/taskset) gates on a related lesson document; this widens it to a knowledge page and adds the evidence requirement from [Soei](https://arxiv.org/abs/2610.39468).
   - **Drift check, adopted.** [extant](https://github.com/scooter-sensei/extant) checks the commit SHAs, branches, paths and links that docs cite, with no markup, in the documents listed in its `.extant.toml`, so each knowledge-base page must be listed there. [blockwatch](https://github.com/mennanov/blockwatch) enforces explicit anchors (an HTML-comment block whose `affects` target must change with it) where one is wanted. [kontext](https://github.com/patkusch/kontext) is an optional time-based staleness check once it is published.
   - **Decision records.** LID's decision docs stay as they are; [the decision-records note](2026-11-06-decision-records-and-lid.md) covers supplements and suggested LID improvements. For any separate decision-record folder, adopt [adrkit](https://github.com/mbeacom/adrkit) only if that folder takes its strict frontmatter. Otherwise borrow its `affects` globs, its in-code `@adr` markers and its warning for markers that cite a superseded record.
5. **GitHub issue mirror (need 9), optional, custom, built last.** None of the mirrors read in source is adoptable as is, and no equivalent of meta-fetch's engine was found in Python, Go or TypeScript.
   - Borrow [github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch)'s design: the watermark moves only when a run completes, sync resumes after an interruption, rate limits are budgeted, linked indexes are generated by label, milestone and state, and output is deterministic.
   - Add [jira-local](https://github.com/jollytoad/jira-local)'s overlap window and truncated-comment detection, [flow-agents](https://github.com/kontourai/flow-agents)' conditional requests with a body-hash fallback, and a periodic full reconcile, because deleted or transferred issues never appear in a `since` listing.
   - A change feed like [github-export](https://github.com/mevdschee/github-export)'s.
   - If meta-fetch publishes releases, adopting it replaces this piece.
6. **Federation (need 6).**
   - Reference clones as in the reference-clones note. Each repo commits its `SUMMARY.md` and `llms.txt` index, and readers follow [OpenSpec](https://github.com/Fission-AI/OpenSpec)'s Stores pattern: one line per entry plus the exact command to fetch the full text.
   - Another repo's index is read **as links to follow, never as prose instructions**. An adversarial manifest read as prose steered 21 of 24 answers, and reading only its links stopped that ([Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361)). Loading two same-job skills together cut rule-following from 93-99% to 61-62% ([SkillClash](https://arxiv.org/abs/2610.25064)), and two repos' overlapping guidance is the same situation. One candidate repo's own `CLAUDE.md` carried an injection-shaped instruction.
   - Each repo owns its own pages, and other repos refer to them by a lightweight entry (a title, a one-line summary and a path) rather than copying them, the "proxy element" practice of [Towards Federated Architecture Knowledge Management](https://doi.org/10.1109/icsa-c68850.2026.00013).
   - Borrow [filedist](https://github.com/flaviostutz/filedist)'s lock file (resolved SHA plus per-file checksums) for the reference-clone manifest.
7. **Capture skill.** As in the superseded note: [IWE](https://github.com/iwe-org/iwe)'s distill flow, with one question first, quoted evidence, and rejections remembered. It also writes drift anchors, enforces the closeout rule, and queues proposals for triage before they're admitted, as in [Memory as Infrastructure (SIx Harness)](https://arxiv.org/html/2609.05510) (59 of 154 decisions kept).

**Need 10, scale and parallel work, is not covered** by any candidate or paper. The partial ideas are goals and strategy pages under `SUMMARY.md` that tasks link to, a claim marker on in-progress items, and komnet's agenda order. [CooperBench](https://arxiv.org/abs/2601.13295) found that planning in the first turn predicted success; agent messaging cut merge conflicts but not failures. Need 10 stays an open design question.

**Corrections to the superseded verdict:**

- seiso runs only 5 stable rules unless preview rules are enabled.
- seiso ships no standalone binaries (crates.io, PyPI wheels, npm).
- One-line descriptions need an optional `description:` key.
- The OKF `verified` and `stale_after` fields give way to extant and blockwatch.
- Unchanged: the authoring-rules sources (developer-docs-framework's rules, seiso's convention, LID's "current intent, read cold" rule, a page-size budget), LID's paths excluded from seiso, Vale where style rules are wanted, and schematter for any frontmatter fields kept.

**Custom glue:**

1. the task-file format, unless an existing one is adopted, plus its checker;
2. the SessionStart hook;
3. the capture skill's extensions;
4. the optional issue mirror, unless meta-fetch publishes releases and is adopted instead.

**Design rules from the papers** (all paper-reported):

- Deliver, don't store: agents made no voluntary memory reads, while delivery by the harness worked ([Delivery, Not Storage](https://arxiv.org/abs/2607.20972)).
- Keep blockers verbatim in handoffs; compression deactivated 97% of them ([When "Must" Becomes "Maybe"](https://arxiv.org/abs/2608.24569)).
- Prefer executable checks to prose rules ([ContextCov](https://arxiv.org/abs/2603.00822); [Lessons Outlive Their Failures](https://arxiv.org/abs/2610.32578)).
- Add one sentence to the user-level instructions giving existing code precedence over a conflicting instruction file ([Stale Instruction Files Override the Code](https://arxiv.org/abs/2610.30571)).
- Hand-written context beats context an agent generates for itself ([Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988)), while context written by a stronger model helps a weaker one ([Context Inheritance](https://github.com/getmetatron/context-md/blob/main/experiment/paper/camera-ready-agenticdev2026/context-inheritance-agenticdev-2026-camera-ready.pdf)). The hook's brief therefore quotes hand-written task text rather than summarizing it.
- Keep old change records out of the agent's working context ([Spec-Driven Development as Prescribed and Practiced](https://arxiv.org/abs/2608.25202)).
- Separate a task's status from its evidence ([Take It From Here](https://arxiv.org/abs/2611.07307)).

**Failure modes the custom pieces must avoid** (verified in source; see Limitations):

- a watermark saved after a failed or rate-limited run (github-grep, github-export);
- an open-only sync that never sees closures (ghfs);
- a generated `CLAUDE.md` that loads as instructions (meta-fetch);
- sequential IDs that collide across repos (md-issues);
- `init` editing git config or `.gitattributes`, and automatic archiving (frame);
- hooks or commands that stage files (repo-librarian, docanchor);
- agent-recorded "human" decisions (komnet);
- a check that fails ordinary pages (skymavis decision-records);
- a sync that rewrites body text (opys);
- done tasks deleted outright (TASKS.md);
- a hook prompt that waits on a terminal (momentum).

**Suggested order:**

1. Adopt the knowledge-base linters, mdbook-llms, extant and blockwatch, and link the index from `AGENTS.md`/`CLAUDE.md`.
2. Design and build the task file, its checker and the hook, and trial them in two repos.
3. Extend the capture skill.
4. If still wanted, build the issue mirror, after asking meta-fetch's maintainer about releases.

Each piece goes through LID.

## Candidates and matrix

Ranked shortlist, per component:

1. **The blend above.** It passes every hard criterion. A single tool that passes the human gate and keeps work items in repo Markdown while delivering them into the session would displace the custom task file and hook.
2. **[frame](https://github.com/joshsegall/frame) as the task store.** Its format is the closest fit for needs 7 and 8. Its `init` edits `.gitattributes` and `.git/config`, its interactive mode archives tasks on its own, some states render as literal text on GitHub, and adoption is very low. It would be adopted if those side effects became opt-in and a release stabilized.
3. **[TASKS.md](https://github.com/tasksmd/tasks.md) as the task store.** It passes every hard criterion except a partial human gate: its file-backend CLI runs no git, but its git-native backend pushes and its next-task skill commits, pushes, opens a PR and, in ship-it mode, merges. Agents can only pull, ranking is P0-P3 then alphabetical (`priorityWeight` is never read), and done tasks are deleted. It would move up if done tasks were archived and ranking used blockers.
4. **[github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch) as the issue mirror.** It has the most correct engine and the best indexes. Against it: no releases, a SQLite cache outside the repo, deletions handled only by an explicit `--full`, and a generated `CLAUDE.md`. It would be adopted with tagged releases.
5. **[komnet](https://github.com/Komdosh/komnet) for homework.** It delivers into the session best and has the best agenda. But tasks live in a separate transport repo plus `~/.komnet`, and its daemon promotes decisions to that repo's `main` and pushes them with an agent recorded as the decider. It would move up if promotion became human-only and tasks could live in the receiving repo.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [seiso](https://github.com/scarletkc/seiso) | adopt | MIT (`LICENSE:1-21` at 5bae44f) | Convention linter; path-mapped kinds; no reformatting |
| [mdbook-llms](https://github.com/ttdonovan/mdbook-llms) | adopt | MIT (`LICENSE:1-21` at d81c009) | `llms.txt` from `SUMMARY.md` parts; mdBook 0.5; crates.io |
| [card-catalog](https://github.com/someotherdustin/card-catalog) | adopt | MIT (`LICENSE:1-21` at ca509be) | Generated record index; npm `@someotherdustin/card-catalog`; use the CLI, not the hook |
| [extant](https://github.com/scooter-sensei/extant) | adopt | MIT (`LICENSE:1-21` at 7999ce2) | Citation drift check; no markup; PyPI; writes nothing by default |
| [blockwatch](https://github.com/mennanov/blockwatch) | adopt | MIT (`LICENSE:1-21` at caa3776) | Explicit anchors checked against the staged diff; pipx, uv, cargo, brew |
| [lychee](https://github.com/lycheeverse/lychee) | adopt | MIT or Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE` at 06f90b0) | Anchors and external links |
| [kontext](https://github.com/patkusch/kontext) | adopt (once published) | MIT (`LICENSE:1-21` at 0f34cf0) | Read-only staleness from git history; npm package not published |
| [adrkit](https://github.com/mbeacom/adrkit) | borrow ideas (adopt where a folder takes its frontmatter) | Apache-2.0 (`LICENSE:1-201` at 9513165) | Scoped decision-record linter; strict frontmatter; no cycle check |
| [github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch) | borrow ideas | MIT (`LICENSE:1-21` at 83df59c) | Best sync engine and indexes; build on it once it has releases |
| [github-export](https://github.com/mevdschee/github-export) | borrow ideas | MIT (`LICENSE:1-21` at bbd4f42) | `events/` change feed; errors still advance the watermark |
| [jira-local](https://github.com/jollytoad/jira-local) | borrow ideas | not read (MIT per its JSR and repository pages) | Watermark overlap, advanced only after a clean run, truncated-comment detection; mirrors Jira, not GitHub (docs only) |
| [flow-agents](https://github.com/kontourai/flow-agents) | borrow ideas | Apache-2.0 (`LICENSE`, opening lines, at 1f59f7d) | Conditional requests with a body-hash fallback; retire records only with a link to what implemented or superseded them; a heavy engine |
| [ghfs](https://github.com/antfu/ghfs) | borrow ideas | MIT (`LICENSE.md:1-21` at 6dce9c1) | Linked open/closed index; default sync misses closures |
| [github-grep](https://github.com/atinux/github-grep) | reject | MIT (`LICENSE:1-21` at ab41493) | Saves its watermark after a rate-limited run; index has no links |
| [gh2md](https://github.com/mattduck/gh2md) | reject | MIT (`LICENSE`, opening lines, at 15602ca) | Full refetch every run, no index |
| [frame](https://github.com/joshsegall/frame) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at 2f5740d) | Inbox, position as priority, archive; install side effects |
| [task-manager](https://github.com/hk9890/task-manager) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at c78059c) | Random IDs, readiness rule, signed releases; required frontmatter |
| [md-issues](https://www.npmjs.com/package/md-issues) (npm; no repository) | borrow ideas | MIT (`package/LICENSE:1-21` in the 0.3.0 tarball) | Checked index, validated writes, link-safe issue moves; no ranking |
| [issue-graph](https://github.com/vercel-labs/issue-graph) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at 2080cf8) | Next-action scoring with a withhold rule; GitHub only |
| [TASKS.md](https://github.com/tasksmd/tasks.md) | borrow ideas | MIT (`LICENSE:1-21` at bce0bba) | Cross-repo blockers; pull only |
| [komnet](https://github.com/Komdosh/komnet) | borrow ideas | MIT (`LICENSE:1-21` at 364c613) | SessionStart inbox, agenda; agent-promoted decisions |
| [repomoot](https://github.com/dev-bude/repomoot) | borrow ideas | Apache-2.0 (`LICENSE:1-202` at 613f783) | Request lifecycle; SQLite daemon |
| [momentum](https://github.com/LiminaLabsAI/momentum) | borrow ideas | MIT (`LICENSE:1-21` at 3942983) | Handoff into the receiving repo's inbox; branches, commits and pushes on its own |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | borrow ideas | MIT (`LICENSE:1-21` at 3e4d5f0) | Stores' index of another repo's specs; imposes an `openspec/` tree |
| [kanbento](https://www.npmjs.com/package/kanbento) | borrow ideas | FSL-1.1-Apache-2.0, not OSI-approved (`LICENSE`, opening lines, at 6ae92a7) | A request into another board's inbox, decided by its owner |
| [docflow](https://github.com/EvolveHQ/docflow) | borrow ideas | MIT (`LICENSE`, opening lines, at 612384b) | Writes never cross repos; one plan item per affected repo |
| [filedist](https://github.com/flaviostutz/filedist) | borrow ideas | MIT (`LICENSE:1-21` at e478722) | Lock file with SHA and checksums; copies files into the consumer |
| [docanchor](https://github.com/E0min/docanchor) | reject | Apache-2.0 (`LICENSE:1-202` at f94497a) | No `SUMMARY.md` awareness; `--apply` stages files; unpublished |
| [loredown](https://github.com/Fenriuz/loredown) | borrow ideas | MIT (`LICENSE:1-21` at b824fd1) | Drift anchors and budgets; required frontmatter and wikilinks |
| [taskset](https://github.com/FalseFoundation/taskset) | borrow ideas | MIT (`LICENSE:1-21` at ca2a771) | Closeout gate; separate `.taskset/` tree |
| [opys](https://github.com/BohdanTkachenko/opys) | reject | Apache-2.0 (`LICENSE`, full standard text, at d0bf442) | Sync rewrites body text and moves files |
| [skymavis decision-records](https://github.com/skymavis/skills) | borrow ideas | MIT (`LICENSE:1-21` at c1ebc6f) | Relinks only decision records; its check fails ordinary pages |
| [repo-librarian](https://github.com/CCROWN2246/repo-librarian) | reject | MIT (`LICENSE:1-21` at 422d404) | `init` commits by default; pre-commit hook stages files |
| [briefd](https://github.com/ismailperim/briefd) | borrow ideas | Apache-2.0 (`LICENSE`, opening lines, at 0b289c7) | Agent writes go only to proposal branches; needs a local server |
| [toy-crane/skills](https://github.com/toy-crane/skills) | borrow ideas | MIT (`LICENSE`, opening lines, at 8d62612) | Spec in the repo is the source of truth and the issue derives from it |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | borrow ideas | MIT (`LICENSE`, opening lines, at 3a296c0) | Tasks, docs and decisions in one tool; not read in source |
| [beads](https://github.com/gastownhall/beads) | reject | MIT (`LICENSE`, opening lines, at 8c3eb30) | Dolt storage; `bd init` edits `AGENTS.md` and installs hooks (docs) |
| [git-bug](https://github.com/git-bug/git-bug) | borrow ideas | GPL-3.0-or-later (`LICENSE`, opening lines, at 4ea4534) | Incremental bridge import; issues are git objects, not Markdown |
| [mcp_agent_mail_rust](https://github.com/Dicklesworthstone/mcp_agent_mail_rust), [beads_rust](https://github.com/Dicklesworthstone/beads_rust) | reject | MIT with an OpenAI/Anthropic rider, not OSI-approved (`LICENSE:1-14` at ae38477, and `LICENSE` at 29774be, respectively) | License |
| [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | reject | MIT plus Commons Clause, not OSI-approved (`LICENSE:1-12` at c0c98d3) | License |
| [IWE](https://github.com/iwe-org/iwe) | borrow ideas | Apache-2.0 (`LICENSE-APACHE`; `Cargo.toml:7` at 44a6742) | Distill flow borrowed; judged overkill |

About 350 further tools were seen and judged not serious. Most are in-repo Markdown trackers, handoff files, decision-record tools and memory stores that are variants of the rows above, or that fail the source-of-truth criterion (SQLite, a home-directory store, a server) or the license criterion.

Backlog.md was not read in source; its row rests on its README and the skills catalog record.

**Matrix A, work items and homework** (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified; H marks hard criteria). Cells rest on the source readings under Limitations; "?" means no reading or listing covers it.

| Criterion | Blend | frame | TASKS.md | komnet | meta-fetch | md-issues |
|---|---|---|---|---|---|---|
| License (H) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Human-gated (H) | ✓ edits reviewed in git | ◐ `init` edits git config; auto-archive (`git_setup.rs`, `tui/app.rs`) | ◐ file CLI runs no git; git-native backend pushes; skill commits and merges | ✗ daemon promotes and pushes (`daemon.ts:478-504`) | ✓ no git writes | ✓ writes after validation only (`workspace.js`) |
| Repo files as source (H) | ✓ | ✓ `frame/` | ✓ file backend | ✗ transport repo plus `~/.komnet` | ◐ SQLite cache; Markdown derived | ✓ |
| Local only (H) | ✓ | ✓ | ✓ | ✓ | ✓ GitHub API only | ✓ |
| Coexistence (H) | ✓ | ◐ own directory; literal states on GitHub (docs only: GFM spec) | ✓ | ✓ touches no code repo | ◐ own output directory; generated `CLAUDE.md` | ◐ frontmatter in the issues folder (and `docs/specs/` if present) |
| Progressive disclosure | ◐ `SUMMARY.md`, `llms.txt`, record indexes | ? | ? | ◐ inbox brief | ✓ linked indexes (`render/mod.rs:99-209`) | ✓ generated index (`render.js`) |
| Delivered into the session (need 8) | ⊕ custom hook | ? | ✗ (grep for hooks: 0 hits at bce0bba) | ✓ SessionStart hook (`hooks.json:1-17`) | ? | ? |
| Cross-repo tasks (need 8) | ⊕ PR into the receiving inbox | ◐ inbox, one repo | ◐ `repo#id` blockers (`workspaces.ts`) | ✓ rooms across repos | ? | ✗ sequential IDs collide (`issues.js:128-137`) |
| Incremental issue sync (need 9) | ⊕ custom sync | ? | ? | ? | ✓ watermark, resumable (`sync/issues.rs:605-707`) | ? |
| Lifecycle (need 7) | ⊕ closeout rule, drift checks | ◐ archive (`format.md:233-265`) | ✗ done tasks deleted (spec) | ◐ agenda, derived staleness | ? | ◐ done/wontfix folders |
| Install via mise | ✓ crates, npm, PyPI | ✓ crate, release binaries | ✓ npm | ✓ npm | ? cargo from a git rev may work; no releases | ✓ npm |
| Maturity | ◐ seiso and blockwatch young; rest established | ✗ few users; unreleased breaking changes | ◐ | ✗ early | ✗ 0 stars, no releases | ✗ 4 weeks, no public repo |

Sources for Matrix A, beyond the Limitations entries:
- frame: `CHANGELOG.md:5-13`, `release.yml:20-41` at 2f5740d.
- TASKS.md: `packages/cli/src/backend/git-native.ts:244-285` and `next-task/SKILL.md:18-23` at bce0bba.
- komnet: rooms and derived staleness, `spec:274-345` and `agenda.ts:84-195` at 364c613; install, `packages/cli/package.json:2-3`.
- meta-fetch: no git writes, by listing (grep for git commands in `src/` at 83df59c).
- md-issues: `config.js:95-112`, `checks/specs.js:60-130` in the 0.3.0 tarball.
- Install and maturity cells: registry pages and repository metadata read on 2026-11-06 (docs only).

**Matrix B, knowledge-base building blocks:**

| Criterion | seiso | mdbook-llms | card-catalog | extant | blockwatch | kontext | adrkit |
|---|---|---|---|---|---|---|---|
| License (H) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Human-gated (H) | ✓ fix mode opt-in, only removes suppressions | ✓ build output only | ◐ plugin hook rewrites index; CLI doesn't | ✓ writes only with opt-in flags | ✓ writes nothing | ✓ `init --yes` only | ✓ writes only on explicit commands |
| Local only (H) | ✓ | ✓ | ✓ | ✓ git only | ◐ optional `check-ai` calls a remote API when a key is set; disable it | ✓ | ✓ |
| Coexistence (H) | ✓ path-mapped kinds | ✓ reads `SUMMARY.md` | ✓ page in `SUMMARY.md` | ✓ | ✓ invisible comment tags | ✓ scans existing tree | ◐ strict frontmatter in its folder |
| No required frontmatter | ✓ | ◐ `description:` for summaries | ✓ | ✓ | ✓ | ◐ `describes:` to get a signal | ✗ YAML schema, unknown keys rejected |
| Pre-commit and CI | ✓ | ✗ a build step, no check | ✓ `validate` | ✓ exit 1 on findings | ✓ staged diff in pre-commit | ✓ `--fail-on` | ✓ exit 0/1/2 |
| Install via mise | ✓ cargo, pipx, npm | ✓ crate | ✓ npm | ✓ pipx | ✓ pipx, cargo | ✗ npm 404 | ✓ npm |

Sources for Matrix B, beyond the Limitations entries:
- seiso: `rules/fixes.rs:1-183` at 5bae44f.
- mdbook-llms: `lib.rs:90-208` at d81c009.
- card-catalog: `hooks/hooks.json` and `scripts/on-write.ts` at ca509be.
- extant: `extant/cli.py:179-231,640-713` at 7999ce2.
- blockwatch: `src/cli.rs:41-160`, `src/validators/check_ai.rs:1-40` at caa3776.
- kontext: `init.ts:479-516`, `check.ts:415-467` at 0f34cf0.
- adrkit: `packages/core/src/validate/index.ts:99-142` at 9513165.
- Install cells: registry pages read on 2026-11-06 (docs only).

**Blends considered:**

- **The leading blend** (above).
- **An existing task format, unmodified, plus the custom hook and checker.**
  - With frame's files: no format design, and frame's tool stays optional (its `init` edits git config), but its literal states don't render on GitHub.
  - With the TASKS.md format: its spec deletes done tasks, which loses need 7's record unless the archive rule is added.

  Either is a fair starting point for the task-file design, which is why the format is left open.
- **komnet for homework:** best delivery and agenda, but tasks would live outside the receiving repo and decisions would be agent-promoted. It fails hard criterion 3 and need 2.
- **GitHub Issues as the only task store, with a mirror plus issue-graph:** capture stays on GitHub, but issue text still fragments across comments, ranking works only for GitHub, and work in progress isn't in the repo. Kept instead as the store for contributor-facing work.
- **OpenSpec as the lifecycle core:** it imposes its own tree beside `SUMMARY.md` and LID's specs. Rejected on coexistence.
- **filedist for federation:** it copies another repo's docs into the consumer, duplicating content in git, and its `check` validates the lock file rather than the config. Pinned reference clones stay.

**Scenario walk.** The finalists are the blend with a custom task file, the blend with frame's files, and the blend with the TASKS.md format. komnet is included where it differs.

1. **Repo A's agent finds work for repo B.**
   - All three blends: the agent opens a PR that adds the item to B's inbox, without touching its reference clone of B, and can mark A's own item as blocked by `B#id`. A person merges it, and B's next session starts with the item among the new inbox items in the hook's brief.
   - komnet: B's session sees the item immediately, but nothing lands in B's repo.
2. **A task finishes.** In all three blends, the closeout rule blocks "done" until a knowledge page or lesson and the evidence exist, and the capture skill drafts them with drift anchors for one reviewed diff. With the TASKS.md format, the archive rule must be added, because its spec deletes done tasks.
3. **A page is split.** Ordinary edits in all three. MD057 and lychee catch missed links, mdbook-lint catches a page missing from `SUMMARY.md`, and extant (for pages listed in its config) and blockwatch flag anchors that no longer resolve.
4. **The issue mirror syncs while hitting the rate limit.**
   - The custom sync: the watermark doesn't move until a run completes, and the next run resumes.
   - meta-fetch as is: the same resume behavior, with deletions only on `--full`.
   - github-grep and github-export, by contrast, would silently skip what they missed.
5. **A fresh CI clone.** mise installs seiso, mdbook-llms, extant, blockwatch, lychee and the existing linters at pinned versions. The task-file checker and the index-freshness check fail the build exactly as they fail pre-commit.

## Limitations checked in source

Readings are from shallow clones or registry archives at the commits named. The exception is gh2md, which was read from the copy already installed as part of the stack. Nothing was installed or run for this search.

**Issue mirrors:**

- **[gh2md](https://github.com/mattduck/gh2md)** 2.5.1 has no option to fetch only updated items, orders by creation date and refetches every issue. *Verified in source* (installed copy, `gh2md/gh2md.py:102-173,205-261`).
- **[github-grep](https://github.com/atinux/github-grep)** saves its `fetchedAt` watermark when it writes the index at the end of a run, including after a rate-limit stop, so the next run skips unfetched issues. *Verified in source* (`cli.ts:100-155`, `writer.ts:294-336` at ab41493). It never removes deleted or transferred issues. *Verified by listing* (grep over `src/` at ab41493; `writer.ts:132-155`).
- **[github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch)** moves its watermark only when a run completes and resumes after every page. It removes deleted items only on `--full` or the first sync, and its README says the same. *Verified in source* (`sync/issues.rs:605-707`, `store/sync_state.rs:107-154`, `sync/mod.rs:154-165,242-249` at 83df59c).
- **[github-export](https://github.com/mevdschee/github-export)** logs fetch errors as warnings and still advances `synced_at`. *Verified in source* (`main.go:113-168`, `issues.go:35-85,400-406` at bbd4f42). It has no index. *Verified by listing* (grep over all `.go` files at bbd4f42).
- **[ghfs](https://github.com/antfu/ghfs)** syncs only open items by default and drops items that are no longer open only on a full sync. Sync appends `.ghfs` to `.gitignore`. *Verified in source* (`sync-repository.ts:85-186`, `config/load.ts:65`, `gitignore.ts:7-48` at 6dce9c1).

**Knowledge-base tools:**

- **[seiso](https://github.com/scarletkc/seiso)** works without frontmatter (kinds come from path globs), never reformats, and by default runs only 5 stable rules (KND001, KND002, LNK001, SUP001, SUP002). *Verified in source* (`src/rules/kind.rs:160-179`, `config/mod.rs:62-67,316-323,406-441`, `rules/mod.rs:243-265` at 5bae44f). It has no `SUMMARY.md` check. *Verified in source* (`commands.rs:796-875` at 5bae44f). Its release workflow publishes to crates.io, PyPI and npm only, with no standalone binaries. *Verified in source* (`publish.yml` at 5bae44f).
- **[mdbook-lint](https://github.com/joshrotenberg/mdbook-lint)** treats any path segment named `decisions`, `adr`, `adrs` or `architecture-decisions` as a decision-record folder, and its ADR rules (on by default) then require a status, a date and MADR section headings, so ADR002-ADR005 fail every LID decision doc. They are disabled only by listing each ID under `disabled-rules`; the documented `"ADR*" = true` wildcard has no effect. *Verified in source* (`format.rs:63-83,107-147`, `registry.rs:156-211`, core `config.rs:26-32` at a1c27e5).
- **[mdbook-llms](https://github.com/ttdonovan/mdbook-llms)** builds `llms.txt` from mdBook's parsed `SUMMARY.md`, and takes one-line descriptions only from a frontmatter `description:` key. *Verified in source* (`src/render.rs:1-82`, `frontmatter.rs:1-41` at d81c009).
- **[card-catalog](https://github.com/someotherdustin/card-catalog)** builds `INDEX.md` by full rebuild with no frontmatter needed, and its plugin's PostToolUse hook rewrites the index in the working tree. *Verified in source* (`core/index-build.ts:1-429`, `core/record.ts:57-190`, `hooks/hooks.json` at ca509be).
- **[loredown](https://github.com/Fenriuz/loredown)** requires frontmatter and checks only wikilinks, and can't lint an existing `docs/` tree. Its drift check compares source anchors with `git log sha..HEAD`. *Verified in source* (`load.ts:395-651`, `lint.ts:181-190`, `drift.ts:1-140` at b824fd1).
- **[opys](https://github.com/BohdanTkachenko/opys)**'s sync rewrites frontmatter, turns IDs in body text into links, and moves files. *Verified in source* (`commands/sync.rs:1-60`, `links.rs:1-23` at d0bf442).
- **[taskset](https://github.com/FalseFoundation/taskset)** blocks `done` while child tasks or related concerns are open, and for configured labels until a related lesson document exists. *Verified in source* (`core/src/tasks/closeout.ts:24-92` at ca2a771).
- **[kontext](https://github.com/patkusch/kontext)** is read-only, treats docs without `describes:` as "unverified" (never failing CI by default), and scans an existing tree including `SUMMARY.md`. *Verified in source* (`freshness.ts:62-72,369-636`, `scan.ts:49-131` at 0f34cf0). Its npm package returns 404. *Docs only* (registry lookup, 2026-11-06).
- **[skymavis decision-records](https://github.com/skymavis/skills)** relinks only links to records under `docs/decisions/`. Its `check` lints every doc under `docs/` and fails ordinary pages on broken links or on a 4-digit inline-code number. Human sign-off is a convention, not code. *Verified in source* (`decisions.py:403-465,468-510,1187-1282` at c1ebc6f).
- **[repo-librarian](https://github.com/CCROWN2246/repo-librarian)**'s `init` runs `git add -A` and `git commit` by default when the tree is clean (`--no-commit` opts out), and its pre-commit hook stages `_index/` files. *Verified in source* (`cli.py:341-387`, `githooks/pre-commit:13-16` at 422d404).

**Work items and homework:**

- **[komnet](https://github.com/Komdosh/komnet)**'s SessionStart hook prints the inbox brief, with work in progress first. Its daemon promotes decisions to the transport repo's `main`, commits and pushes them, and sets `decided_by` to the sending agent. Its needs-a-human items can't be drained, only answered through a human relay whose attribution is by convention, not authenticated. *Verified in source* (`plugins/claude/hooks/hooks.json:1-17`, `daemon.ts:478-504`, `sealer.ts:885-938`, `inbox.ts:48-61` at 364c613).
- **[repomoot](https://github.com/dev-bude/repomoot)** keeps state in SQLite behind a local daemon. Only the requester, or an observer, can accept or reject a delivery. *Verified in source* (`db.py:11-59`, `lifecycle.py:1-109` at 613f783).
- **[TASKS.md](https://github.com/tasksmd/tasks.md)**'s file-backend CLI runs no git, its git-native backend commits and pushes a claims ref, and its next-task skill commits, pushes, opens a PR and, in ship-it mode, merges. *Verified in source* (`packages/cli/src/backend/tasks-md.ts:1-208`, `backend/git-native.ts:244-285`, `next-task/SKILL.md:18-23` at bce0bba). Its documented `priorityWeight` and `exclude` are never read. *Verified in source* (`workspaces.ts:16,137-173` at bce0bba). Nothing pushes tasks into a session. *Verified by listing* (grep for hook or SessionStart, 0 hits at bce0bba). Done tasks are deleted. *Docs only* (its spec).
- **[OpenSpec](https://github.com/Fission-AI/OpenSpec)** Stores never clone, pull or push, and `openspec instructions` adds an index of a referenced store's stable specs only. *Verified in source* (`git.ts:55-171`, `references.ts:170-224,374-522` at 3e4d5f0).
- **[frame](https://github.com/joshsegall/frame)**'s `init` and `git setup` append merge-driver lines to `.gitattributes` and run `git config`, and its interactive mode auto-runs `clean`, which archives tasks. *Verified in source* (`git_setup.rs:367-400,416-560`, `tui/app.rs:5969-6000` at 2f5740d).
- **[task-manager](https://github.com/hk9890/task-manager)** defines "ready" as open with no open blockers, sorted by priority then age. *Verified in source* (`sdk/tasks/ready.go:36-89` at c78059c). It requires YAML frontmatter and keeps no index by design. *Docs only* (`docs/specs/TASK-STORAGE-SPEC.md:1-260` at c78059c).
- **[md-issues](https://www.npmjs.com/package/md-issues)** rewrites links when it moves an issue, writes nothing unless every check passes, and uses sequential IDs. *Verified in source* (`sync.js:36-165`, `workspace.js:1-69`, `issues.js:128-137` in the 0.3.0 tarball).
- **[issue-graph](https://github.com/vercel-labs/issue-graph)** is read-only toward GitHub and can rank only GitHub items. *Verified in source* (`transports/shell.ts:84-126`, `types.ts:58-90`, `plan.ts:82-381` at 2080cf8).
- **[momentum](https://github.com/LiminaLabsAI/momentum)** writes handoffs straight into the receiving repo's working tree, prompts for a key only when stdin is a terminal, and branches, commits and pushes on its own. *Verified in source* (`core/orchestration/handoff.js:53-130`, `scripts/sessionstart-handoff.sh:1-203`, `bin/ecosystem.js:270-285`, `core/lanes/lib/cleanup.js:160-252` at 3942983). The auto-branching rule is *docs only* (`AGENTS.md:231-271`).

**Drift, decision-record and federation building blocks:**

- **[docanchor](https://github.com/E0min/docanchor)**'s `move --apply` runs `git add` on the moved files. It has no `SUMMARY.md` or mdBook awareness, and split doesn't register the new page. It is not published on npm. *Verified in source* (`scripts/tools.mjs:366-492,540` at f94497a; npm "Not found").
- **[adrkit](https://github.com/mbeacom/adrkit)**'s `adr lint` checks schema, unique IDs and dangling references, but not supersession cycles, despite its README. Markers are scanned only by `adr check` and `adr explain`, where one that cites a superseded record only warns. Records need strict YAML frontmatter. *Verified in source* (`packages/core/src/validate/index.ts:99-142`, `validate/corpus-invariants.ts:189-250`, `markers/resolve.ts:347-485`, `adr.schema.ts:236-314` at 9513165).
- **[filedist](https://github.com/flaviostutz/filedist)** pins any git ref and records a 12-character SHA and per-file checksums in `.filedist.lock`. Its `check` works from the lock, not the config. *Verified in source* (`lib/src/package/source.ts:346-402`, `lib/src/package/lockfile.ts:10-131`, `lib/src/package/action-check.ts:54-218` at e478722).
- **[extant](https://github.com/scooter-sensei/extant)** checks 13 kinds of citation, skips fenced code, fails with exit 1 on findings, and writes only with opt-in flags. It checks only the documents listed in `.extant.toml` (default `NEXT_SESSION.md`). *Verified in source* (`extant/gate.py:438-500`, `extant/cli.py:179-231,640-713`, `extant/config.py:102-104` at 7999ce2).
- **[blockwatch](https://github.com/mennanov/blockwatch)** fails when a block's lines change in the staged diff but its `affects` target doesn't, and writes nothing. *Verified in source* (`src/validators/affects.rs:17-75,197-244`, `src/cli.rs:41-160`, `.pre-commit-hooks.yaml:1-22` at caa3776).

**Safety:** komnet's own `CLAUDE.md` ends with an unrelated instruction to import other agents' configurations into Claude Code. *Verified in source* (repository root at 364c613).

Verified:

- The licenses of every candidate under Limitations except gh2md: each read in full and grepped for riders, restrictions, the Commons Clause and additional terms.
- The other licenses, read from the named file's opening lines at the named commit; lychee and IWE carry forward from the superseded note.
- The source claims above.

Could not verify:

- kontext's behavior once published, and frame's unreleased HEAD;
- Backlog.md's storage and git behavior (not read in source);
- how seiso's preview rules behave on a real wiki;
- whether Renovate can update filedist-style pins, and whether mise's cargo backend installs meta-fetch from a git revision;
- the library-dependents route, the PyPI search page, Semantic Scholar in rounds 3-5 (one call succeeded in round 4), and the ACM PDF (all unavailable; see the ledger);
- citation snowballing for 2026 arXiv preprints, which OpenAlex doesn't cover yet.

## Papers

Every claim below is paper-reported; claims from preprints are the authors' and not established. Some citation data came from Semantic Scholar.

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Progressive Disclosure for LLM-Maintained Wiki KBs](https://arxiv.org/abs/2607.04576) | read in part (§1-6, 9-10) | experiment | preprint | borrow ideas | A capable agent never loaded the large index; one-line page summaries plus keyword search cut cost 30-58% with pooled quality non-inferior, but aggregation questions lost correctness (paper-reported) |
| [Is Progressive Disclosure All You Need?](https://arxiv.org/abs/2607.17598) | read in part (§3.2-3.3, 5.1-5.2) | experiment | peer-reviewed | borrow ideas | One index level matched or beat raw navigation on two of three harnesses (not Codex, which greps on its own); a second level never helped and sometimes hurt (paper-reported) |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) | read in part (§4.2-4.4) | experiment | preprint | borrow ideas | Generated context files slightly hurt and cost 20-23% more; developer-written ones gave a non-significant gain (paper-reported) |
| [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) | read in part (§3.3, 5, 6) | weak experiment | peer-reviewed | borrow ideas | No correctness difference, but an on-demand wiki cut wasted work (paper-reported) |
| [Delivery, Not Storage](https://arxiv.org/abs/2607.20972) | read in part (abstract, §5.2) | weak experiment | preprint | borrow ideas | Zero voluntary memory reads in 114 turns; delivery triggered by the harness always worked (paper-reported) |
| [Stale Instruction Files Override the Code](https://arxiv.org/abs/2610.30571) | read in full | experiment | preprint | borrow ideas | Agents followed a stale instruction file in 90.1% of choices; one sentence giving existing code precedence raised code-following from 4.2% to 91.4% (paper-reported) |
| [ContextCov](https://arxiv.org/abs/2603.00822) | abstract only | experiment | preprint | borrow ideas | The abstract reports 88% compliance with executable checks vs 67% prompt-only (paper-reported) |
| [Lessons Outlive Their Failures](https://arxiv.org/abs/2610.32578) | read in part (§3, 5.1-5.2, 6) | observational study | preprint | borrow ideas | Drift caused 40.7% of failures, and only pre-commit checks held (paper-reported) |
| [One Skill Takes Over (SkillClash)](https://arxiv.org/abs/2610.25064) | read in part (§4, 5, 7) | experiment | preprint | borrow ideas | A second same-job skill cut rule-following to 61-62%; a priority note didn't help; one merged file ending in a worked example restored 96-99% (paper-reported) |
| [Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361) | read in full | weak experiment | peer-reviewed (IEEE FLLM 2026) | borrow ideas | Agents rarely fetched `llms.txt` unprompted; an adversarial manifest read as prose steered 21/24 answers, and reading only same-origin links gave 0/24 at equal utility (paper-reported) |
| [Context Inheritance](https://github.com/getmetatron/context-md/blob/main/experiment/paper/camera-ready-agenticdev2026/context-inheritance-agenticdev-2026-camera-ready.pdf) (DOI [10.1145/3843282.3844425](https://doi.org/10.1145/3843282.3844425)) | read in full (author-hosted CC BY 4.0 copy) | experiment | peer-reviewed | borrow ideas | Context written by a frontier model raised a small model's localization by 26.1 points, its own lessons by 0; an index plus shards used about a third of the tokens of one file (exploratory, small reader only; a frontier reader paid about 50% more); the review gate and merge behavior were not measured (paper-reported) |
| [Handoff Debt](https://arxiv.org/abs/2606.02875) | read in part (§3, 5) | experiment | peer-reviewed | borrow ideas | Structured handoff notes cut tokens 42-63%; solve-rate effects small (paper-reported) |
| [When "Must" Becomes "Maybe"](https://arxiv.org/abs/2608.24569) | abstract only | experiment | preprint | borrow ideas | The abstract reports that compressing handoffs deactivates 97% of blockers (paper-reported) |
| [Take It From Here](https://arxiv.org/abs/2611.07307) | read in part (§1-3, 5, App. A.1) | experiment | preprint | borrow ideas | 4.95% complete delivery with full history; a "requirement atom" separates status from evidence (paper-reported) |
| [A Gated Spec-Driven Workflow](https://arxiv.org/abs/2611.05094) | read in part (§3, 5.4) | qualitative study | preprint | borrow ideas | Memory entries proposed at archive time go to a human one by one; 3 of 8 approved and later cited (paper-reported) |
| [Agent Plans in OSS](https://arxiv.org/html/2608.04661) | read in full | observational study | peer-reviewed | borrow ideas | Plan files are rare and mostly committed once, never referenced (paper-reported) |
| [Acquiring and Verifying Repository Norms](https://arxiv.org/abs/2610.07757) | read in part (§1, 3.5) | experiment | preprint | borrow ideas | A read-only Markdown norm package with a `START.md` entry and pages filed by repository path; the abstract reports 7-11% higher norm compliance overall and 31-45% on contribution norms (paper-reported) |
| [Memory as Infrastructure (SIx Harness)](https://arxiv.org/html/2609.05510) | read in part (§3.2-3.5, 5) | observational study | preprint | borrow ideas | Captured decisions were triaged before admission (59 of 154 kept); an inventory doc plus a do-not-rebuild note stopped re-proposals of existing subsystems (paper-reported) |
| [Superintelligent Software Engineering (OSTEON)](https://arxiv.org/html/2610.31306) | read in part (abstract, §VI, X) | untested proposal | preprint | borrow ideas | A session-start check of recorded source digests stays silent when healthy; the abstract reports that in the median context file that names paths, 9.5-22% of them don't resolve (paper-reported) |
| [Lore](https://arxiv.org/html/2603.15566) | read in full | untested proposal | preprint | borrow ideas | Decision records carried as git commit trailers (Constraint, Rejected, Directive), read by agents before editing a path; no evaluation (paper-reported) |
| [Soei](https://arxiv.org/abs/2610.39468) | abstract only | observational study | preprint | borrow ideas | The abstract reports that 57.8% of to-dos an agent marked complete had no proof in between (paper-reported) |
| [VibeMemBench](https://arxiv.org/abs/2609.23570) | abstract only | experiment | preprint | borrow ideas | The abstract reports that, across four memory systems, 11 of 12 solver-system pairs fail to beat no memory (paper-reported) |
| [Stratum](https://arxiv.org/abs/2610.36153) | read in part (III-B, V-B) | weak experiment | preprint | borrow ideas | Inherited notes found the root cause in 21/24 trials vs 6/24 (paper-reported) |
| [CooperBench](https://arxiv.org/abs/2601.13295) | read in part (§4, 5) | experiment | preprint | borrow ideas | Messaging cut merge conflicts, not failures; first-turn planning predicted success (paper-reported) |
| [Temporal Validity on Real Software Histories](https://arxiv.org/abs/2608.20685) | abstract only | experiment | preprint | borrow ideas | The abstract reports that retrieval returns superseded values 36-38% of the time, deterministic supersession almost never (paper-reported) |
| [Towards Federated Architecture Knowledge Management](https://doi.org/10.1109/icsa-c68850.2026.00013) | read in full (a two-page talk proposal, from a copy the developer supplied) | qualitative study (experience report, no evaluation) | peer-reviewed | borrow ideas | In an organization of over fifty architects, a monolithic model repository became outdated, with unclear ownership. Splitting it into a core repository of reusable abstract elements and domain repositories that own their implementations worked better. Lightweight "proxy" elements carry minimal metadata and keep identity across repositories, and one publication layer shows only approved elements, without readers needing to know which repository each came from (paper-reported) |
| [Organizes Before It Retrieves](https://arxiv.org/html/2610.32851) | read in full | observational study | preprint | borrow ideas | A self-describing artifact catalog separates fields known at creation from fields accrued in use; the authors scope it to machine-generated corpora (paper-reported) |
| [PROJECTMEM](https://arxiv.org/abs/2606.12329) | read in part (§2, 3, 5) | untested proposal | preprint | borrow ideas | A typed event log projected into `summary.md` (paper-reported) |
| [Spec-Driven Development as Prescribed and Practiced](https://arxiv.org/abs/2608.25202) | read in part (V-B to V-D) | qualitative study | preprint | borrow ideas | Old change records in the working tree feed agents outdated intent; spec updates should be drafted from diffs for human confirmation (paper-reported) |

About 110 further papers were seen and not tabled. Nearly all would be borrow ideas: context-file studies, staleness detection, repository memory and multi-agent handoff. No paper addresses cross-repo task assignment or backlog prioritization by agents: searches on arXiv, OpenAlex, Semantic Scholar and Crossref for those returned nothing.

## Worth retrieving manually

None.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | gh2md 2.5.1 (installed copy); mdBook, rumdl, mdbook-lint and lidc as in the superseded note; Claude Code hooks (SessionStart) and cross-session messaging; GitHub sub-issues, issue types and blocked-by dependencies (gh 2.94) |
| Earlier notes and decisions | searched | The superseded note, the reference-clones and docs-site notes, the calibration leads note, issue #54, PortaBase's wiki pages and its issue-export task |
| GitHub repository search | searched | 142 phrasings in rounds 1 and 3-5, most run with and without a star floor, e.g. "git issue tracker", "markdown task tracker stars:>10", "handoff coding agents markdown repo", "message bus git repository coding agents", "stable ids markdown rename links docs" |
| GitLab and Codeberg search | searched | 30 GitLab and 40 Codeberg queries, e.g. "git issue tracker", "agent backlog", "handoff", "markdown task tracker". Codeberg matches single keywords only, and GitLab results are dominated by mirrors |
| GitHub topics | searched | 44 topic queries, e.g. `topic:git-issue`, `topic:agent-handoff-protocol`, `topic:llms-txt`, `topic:decision-records pushed:>2026-10-01` |
| GitHub code search | searched | 25 queries, including 3 repo-scoped checks of sync claims, e.g. `repomoot filename:README.md`, `path:docs/follow-ups`, `filename:INBOX.md agents tasks` |
| npm | searched | About 55 searches plus 24 package-document reads, e.g. "markdown task tracker git", "git issue tracker cli", "github issues incremental markdown" |
| PyPI | searched | 8 site searches and 21 JSON lookups, e.g. "github issues export markdown incremental sync", "markdown knowledge base cli index agents llms.txt". PyPI's own search page is in its own row |
| PyPI search page | unavailable | A bot-check page after one retry; PyPI keyword queries went through libraries.io instead |
| crates.io | searched | 12 keyword queries, e.g. "issue tracker git", "markdown tasks", "kanban markdown", plus exact-name lookups at 1 request a second |
| Language registries | searched | Go: 17 pkg.go.dev searches and module-proxy lookups, e.g. "github issues markdown sync", "issues filesystem". RubyGems: 7 queries, e.g. "issue tracker", "kanban", "backlog" |
| libraries.io | searched | 29 searches, e.g. "git issue tracker markdown", "github issues local files agents", "issues mirror incremental" |
| libraries.io dependents | unavailable | The API answered "Disabled for performance reasons", after a retry |
| Homebrew formulae | searched | Alternations over the formula list, e.g. `issue track\|bug track\|todo\|task (track\|manag)\|kanban` and `handoff\|backlog\|ticket\|decision` |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | 19 `/r/<owner>/<repo>` pages, e.g. git-bug, Backlog.md, OpenSpec, beans |
| AUR | searched | 20 name searches, e.g. "issue tracker", "kanban", "handoff", "ready queue" |
| ecosyste.ms | searched | 31 keyword tags, e.g. issue-tracker, kanban, handoff, decision-records, documentation-drift, stale-docs |
| aitoolnet.com | searched | Sitemap grep over 48k slugs for backlog, kanban, issue, task, knowledge, memory and docs; hits were hosted or known tools |
| Cross-language equivalents | searched | "alternatives to" and Rust, Python and Go equivalents of ghfs, tasks.md, gh2md, beads, git-bug and github-repo-meta-fetch |
| Awesome lists | searched | awesome-claude-code, awesome-agent-skills, awesome-mcp-servers, awesome-claude-skills, awesome-spec-driven-development, Awesome-Context-Engineering, awesome-agent-orchestrators, awesome-harness-engineering. No list exists for git-based issue trackers or `llms.txt` |
| alternativeto.net | excluded | It challenges automated clients; covered by "alternatives to" web searches |
| General web search | searched | About 120 phrasings, e.g. "git-native issue tracker for AI coding agents", "cross-repo task coordination AI coding agents inbox", "SessionStart hook inbox for coding agents", "documentation staleness check last verified commit", plus Hacker News threads through mirrors |
| Hosted services | searched | GitHub Projects and issue features, Linear, Jira Rovo, Notion, DeepWiki, Cursor and Windsurf memories, Factory, Augment, Sourcegraph, Plane, Huly. All but GitHub fail the local criterion |
| Skill directories | searched | skills.sh: 106 queries, e.g. "knowledge base", "backlog", "ready queue", "decision records", "stale docs" |
| Claude Code plugin marketplaces | searched | The official marketplace file grepped in full in four rounds, e.g. for knowledge, backlog, decision, adr, stale |
| MCP Registry | searched | 38 queries (31 keyword, 7 named leads), e.g. backlog, handoff, inbox, decisions, staledocs |
| PulseMCP | excluded | robots.txt disallows ClaudeBot (re-read 2026-11-06) |
| Anthropic's skills repo | searched | Skill list read in rounds 1, 3 and 5; nothing in scope |
| Awesome lists for agent skills | searched | As in the awesome-lists row |
| GitHub topics for agent skills | searched | agent-skills, claude-skills, mcp-server and claude-code-plugin combined with backlog, task, knowledge and handoff |
| arXiv | searched | 99 queries plus HTML full texts, e.g. `all:"progressive disclosure" AND all:agent`, `all:"AGENTS.md"`, `abs:"decision records" AND (agent\|agents\|LLM)` |
| OpenAlex | searched | 35 searches plus DOI and citing-work lookups, e.g. "context files coding agents", `cites:` for 2602.11988. It has no reference lists for arXiv-only preprints |
| OpenAIRE | searched | 10 queries, e.g. `"progressive disclosure" coding agents`, `"context rot"` |
| Semantic Scholar | searched | 13 calls: 10 in round 1 and 3 in round 4 (1 succeeded), e.g. bulk `"AGENTS.md" \| "CLAUDE.md" \| "context files"`. Unavailable in rounds 3 and 5 (rate limit, no key set); OpenAlex, its substitute, was searched |
| papers.cool | searched | 7 queries, not cached, e.g. "progressive disclosure agent", "agent handoff coding" |
| Hugging Face papers | searched | 19 queries, e.g. "coding agent memory repository", "cross-repository task handoff coding agents" |
| Zenodo | excluded | robots.txt disallows `/api` and `/search` (re-read 2026-11-06); abstracts came through OpenAlex |
| Crossref | searched | 12 queries in the polite pool, e.g. "design rationale capture issue tracking systems", "architecture decision records large language model" |
| ACM Digital Library | unavailable | A bot challenge on the PDF of a paper reported open access, after a retry; an author-hosted copy was read instead |
| Europe PMC | excluded | No life-sciences angle in the need |
| Venue program pages | excluded | ICSA 2026 surfaced from a DOI in round 3; its companion-track paper was reached through OpenAlex and Crossref, and no other venue and year came up |

## Snowball rounds

1. **Round 1:** 154 unique candidates across all routes. Serious ones included [Backlog.md](https://github.com/MrLesk/Backlog.md), [TASKS.md](https://github.com/tasksmd/tasks.md), [ghfs](https://github.com/antfu/ghfs), [github-export](https://github.com/mevdschee/github-export), [github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch), [git-bug](https://github.com/git-bug/git-bug), [repomoot](https://github.com/dev-bude/repomoot), [opys](https://github.com/BohdanTkachenko/opys) and [md-issues](https://www.npmjs.com/package/md-issues).
2. **Round 2** (a partial round):
   - added [agent-handoff](https://github.com/zzyyfff/agent-handoff), [mdbook-combiner](https://github.com/jscarrott/mdbook-combiner) and [metagit-cli](https://github.com/metagit-ai/metagit-cli)'s skills;
   - read the key sections of [Acquiring and Verifying Repository Norms](https://arxiv.org/abs/2610.07757) and [Delivery, Not Storage](https://arxiv.org/abs/2607.20972).
3. **Round 3** (264 unique candidates after merging):
   - added [komnet](https://github.com/Komdosh/komnet), [briefd](https://github.com/ismailperim/briefd), [github-grep](https://github.com/atinux/github-grep), [mdbook-llms](https://github.com/ttdonovan/mdbook-llms), [loredown](https://github.com/Fenriuz/loredown), [taskset](https://github.com/FalseFoundation/taskset) and [card-catalog](https://github.com/someotherdustin/card-catalog);
   - added the papers [Take It From Here](https://arxiv.org/abs/2611.07307) and [SkillClash](https://arxiv.org/abs/2610.25064).
4. **Round 4:**
   - added [frame](https://github.com/joshsegall/frame), [task-manager](https://github.com/hk9890/task-manager), [issue-graph](https://github.com/vercel-labs/issue-graph), [skymavis decision-records](https://github.com/skymavis/skills), [kontext](https://github.com/patkusch/kontext), [repo-librarian](https://github.com/CCROWN2246/repo-librarian) and [kanbento](https://www.npmjs.com/package/kanbento);
   - reading these in source reduced each to borrowed ideas, an optional role or a rejection.
5. **Round 5:**
   - added [extant](https://github.com/scooter-sensei/extant) and [blockwatch](https://github.com/mennanov/blockwatch) (adopted as drift checks), [adrkit](https://github.com/mbeacom/adrkit), [docanchor](https://github.com/E0min/docanchor), [filedist](https://github.com/flaviostutz/filedist), [momentum](https://github.com/LiminaLabsAI/momentum), [docflow](https://github.com/EvolveHQ/docflow), [jira-local](https://github.com/jollytoad/jira-local) and [flow-agents](https://github.com/kontourai/flow-agents);
   - added the papers [Memory as Infrastructure (SIx Harness)](https://arxiv.org/html/2609.05510), [Superintelligent Software Engineering (OSTEON)](https://arxiv.org/html/2610.31306) and [Soei](https://arxiv.org/abs/2610.39468), and full reads of [Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361), [Context Inheritance](https://github.com/getmetatron/context-md/blob/main/experiment/paper/camera-ready-agenticdev2026/context-inheritance-agenticdev-2026-camera-ready.pdf) and [Lore](https://arxiv.org/html/2603.15566);
   - nothing in it could change the shape of the leading option.

A sixth round, narrowed to decision records, is reported in [the decision-records note](2026-11-06-decision-records-and-lid.md).

The general search stopped after round 5 by the developer's decision, short of the 10-round cap, with rounds still adding candidates. Open leads:

- [claude-bible](https://github.com/tonydzi/claude-bible): one rule per file, a declined-decisions journal;
- [zenrei](https://github.com/pikonori/zenrei): a decision index across repos with pending-only agent writes;
- [mason](https://github.com/adrianczuczka/mason) and [commitlore](https://github.com/MongLong0214/commitlore): decisions delivered per file;
- [dossier-scribe](https://github.com/kd-011/dossier-scribe): claims citing source files;
- [lore-protocol](https://github.com/Ian-stetsenko/lore-protocol), the implementation of [Lore](https://arxiv.org/html/2603.15566)'s git trailers;
- [markdown-ticket](https://github.com/andkirby/markdown-ticket) and [tissue](https://github.com/smeans/tissue);
- forward citations of [Progressive Disclosure for LLM-Maintained Wiki KBs](https://arxiv.org/abs/2607.04576) and [Take It From Here](https://arxiv.org/abs/2611.07307).

## Refresh trigger

- When frame cuts a release with opt-in git setup, or kontext is published.
- When github-repo-meta-fetch publishes releases.
- When seiso adds an explanation or concept kind, or reaches 1.0.
- When komnet makes decision promotion human-only.
- When mdBook gains a way to import another book's `SUMMARY.md` ([rust-lang/mdBook#1347](https://github.com/rust-lang/mdBook/issues/1347)).
- Before the task-file design (Suggested order step 2) starts: check the open leads under Snowball rounds.
- After the task file and session-start hook have run in two repos for a few weeks.
- On 2027-05-06, whichever comes first.
