# Prior art: task management and prioritization for humans and coding agents (2026-11-12)

- **Supersedes:** the cross-repo homework and work-item parts (needs 8 and 9) and the tentative task-file format of [the federated knowledge and work-items note](2026-11-06-federated-knowledge-and-work-items.md). That note's knowledge-base blend and its lifecycle design for need 7 (a task's outcome becomes knowledge, a finding becomes a task) still stand.
- **Effort:** full method, because the task store becomes long-lived content in every repo, and the best two candidates are close.
- **Already known:** the 2026-11-06 note had read [frame](https://github.com/joshsegall/frame), [TASKS.md](https://github.com/tasksmd/tasks.md), [task-manager](https://github.com/hk9890/task-manager), [komnet](https://github.com/Komdosh/komnet) and others in source, rejected [beads](https://github.com/gastownhall/beads) (its Dolt database store, and `bd init`'s side effects) and [claude-task-master](https://github.com/eyaltoledano/claude-task-master) (Commons Clause), and left [Backlog.md](https://github.com/MrLesk/Backlog.md) unread in source. [The 2026-11-09 process note](2026-11-09-agentic-development-process.md) listed leads for this search, among them [kanban-md](https://github.com/antopolskiy/kanban-md), [specweave](https://github.com/anton-abyzov/specweave) and [rtmx](https://github.com/rtmx-ai/rtmx). The developer wasn't asked what else they knew or had dismissed (a non-interactive run), so that question is unanswered.
- **Method:** this run applied the open proposals for the prior-art-search skill where they improve the report: [#155](https://github.com/jmbowman/agentic_development/issues/155), [#156](https://github.com/jmbowman/agentic_development/issues/156), [#157](https://github.com/jmbowman/agentic_development/issues/157), [#158](https://github.com/jmbowman/agentic_development/issues/158), [#159](https://github.com/jmbowman/agentic_development/issues/159), [#191](https://github.com/jmbowman/agentic_development/issues/191), [#196](https://github.com/jmbowman/agentic_development/issues/196) and [#202](https://github.com/jmbowman/agentic_development/issues/202). It ran coordinated rounds with one owner per service, read whole license files, applied failure-path checklists to sync and file-writing tools, and checked every link and commit SHA in this note against the search records with a script. It also tagged finds by novelty, classified near-fits by the size of the addition they need, walked the use cases first, and classified each gap as additive or fundamental. It didn't run #196's test of the finalist, which needs the developer's approval to run a candidate on this machine.

## Need and criteria

| # | Requirement | Underlying need |
|---|---|---|
| R1 | Each task says who performs it: a human (which one, in multi-contributor projects) or an agent (with a suggested model) | Route work to the right performer; agent work isn't held up by human availability; pick a model that fits the task |
| R2 | Dependencies are explicit | Know what is ready and what blocks what; compute a ready queue |
| R3 | Agents search local files for full backlog context | An agent can grep the complete backlog (descriptions, notes, decisions) offline and cheaply |
| R4 | Humans have final say on priority; their decisions are never silently overridden | Human-set priorities and decisions are protected, or every agent change to them is visible and attributable |
| R5 | Visualizations | A person sees the backlog, the dependency graph, each task's status and the priority order at a glance |
| R6 | Correct granularity | A parent is a grouping that references child tasks, one thing each; agent-doable work is never stranded inside a task that needs a human |
| R7 | Sync with GitHub Issues/Projects and Jira (nice to have) | Collaborators see work where they already work. Push-only is acceptable; bidirectional only if done well |
| R8 | From [#167](https://github.com/jmbowman/agentic_development/issues/167): file layout, ordering, claiming by parallel agents, merge conflicts, how tasks reach a session, what happens to done tasks | How agentic development systems run work queues |
| R9 | Cross-repo tasks (need 8 of the 2026-11-06 note) | One repo's agent can file work for another repo |

**Use cases.** These are derived from the developer's request; the developer wasn't asked for their most common ones, so that question is unanswered:

- **U1.** The developer orders the week's priorities; later an agent proposes a reorder. The developer sees exactly what would change, and a choice they pinned can't change silently.
- **U2.** A feature needs one human decision plus several agent-doable pieces. Agents take the independent pieces while the human item waits.
- **U3.** At session start an agent gets the next ready agent task (suited to its model) and claims it, while another agent in a parallel worktree claims a different one.
- **U4.** The developer opens a view of the dependency graph, status and priority order.
- **U5.** Tasks are pushed to GitHub Issues/Projects (or Jira) for a collaborator, who comments and changes status there.

**Hard criteria:**

1. **H1.** An OSI-approved license, read from the license file, usable as an installed tool in this Apache-2.0 repo.
2. **H2.** The full backlog is available to agents as local plain-text files they can grep (repo files, or a complete local mirror kept current).
3. **H3.** An agent can't silently override a human-set priority or decision: the change is refused, or always surfaces as a reviewable, attributable diff. A small addition that gets there counts as extensible.
4. **H4.** Runs locally, with no required hosted service besides GitHub.
5. **H5.** Never merges to the default branch on its own. Agent commits, pushes and PRs are a preference (configurable), not a hard line.

**Preferences:** performer and model fields; dependency graph with ready computation and cycle check; parent/child and granularity checks; visualizations; a human-owned priority model; parallel claiming; merge-conflict resistance; delivery into an agent session; done tasks archived, not deleted; GitHub and Jira sync; cross-repo; installable through mise and updatable by Renovate; writes nothing outside its own directory; Markdown that renders on GitHub and coexists with mdBook and LID; maintenance and maturity; low process overhead.

## Verdict

**Blend: [Backlog.md](https://github.com/MrLesk/Backlog.md) as the task store and the human views, plus custom pieces for performer fields, human authority, granularity, claiming and sync.**

No single tool meets the core needs, and the custom pieces aren't all small: the list below sizes them. Backlog.md meets every hard criterion (H3 as extensible) and is far ahead of the rest on views, Markdown that renders on GitHub, and maturity. [pm-cli](https://github.com/unbraind/pm-cli) is the alternative. It holds human decision items out of the agent queue natively and records which agent and model made each change, but it needs as many custom pieces, has no board, uses a non-Markdown format, and has one maintainer. Which of them to build on is decision 1 in the table at the end of this section.

The search ran five coordinated snowball rounds. Rounds 4 and 5 added nothing that could change the verdict, and round 5 added nothing that could change the shortlist. Round 5 also covered one route not searched before (arXiv's recent cs.SE listing) to back the "nothing found" results that pieces B and C rest on. The skill's own stop rule, a round with no new serious candidate, wasn't met, because round 5 still added candidates worth borrowing ideas from. The open leads are under Snowball rounds.

### The leading blend

1. **Store and views: Backlog.md**, configured so it writes nothing it doesn't need to:
   - `autoCommit: false` (the default) and `remoteOperations: false`, which stops the `git fetch --prune` it runs when it generates an ID;
   - `init` in its CLI mode with no instruction-file targets selected, and no MCP client registration: its MCP mode writes user-level config for Claude, Gemini, Codex and Kiro. A committed project `.mcp.json` entry gives sessions its MCP server instead.

   What it provides:
   - **Store:** one Markdown file per task under `backlog/`, with dependencies, a parent and subtasks, milestones, drafts and decisions. The archive keeps task IDs. Readiness is computed (`task list --ready`).
   - **Views:** a terminal board, and `backlog browser`, a local web board on 127.0.0.1 with a dependency-graph section and statistics. Order is each column's `ordinal`.
2. **Piece A: performer and model fields** (small). Backlog.md keeps unknown frontmatter keys when it rewrites a task, so this needs a convention and a check, not a fork.
   - `performer: human:<login>` or `performer: agent`.
   - For agent tasks, a capability tier (`agent_tier: fast | moderate | strong`) as a floor, with an optional `suggested_model` (decision 5). The papers below find a model chosen up front from task text unreliable and favour escalating after a first attempt. [beadhive](https://github.com/beadhive/beadhive) resolves a model at dispatch from a stored tier, and [ADLC](https://github.com/voodootikigod/adlc)'s model-router computes a tier at dispatch from a ticket's structure.
   - When a task closes, record which agent and model did it, as [pm-cli](https://github.com/unbraind/pm-cli)'s history does. Keep the accountable human (`assignee`) separate from the acting agent (`delegate`), as [tbd](https://github.com/jlevy/tbd) does.
3. **Piece B: a human-authority check** (medium), run in pre-commit and CI. No tool found protects a human-set priority in repo files (rounds 2-5, under Snowball rounds).
   - **Protected fields:** priority, the relative order of human-ordered tasks, performer, acceptance criteria, and decision records (decision 6). A field set by a human carries `set_by: human:<login>`; an agent-set value carries `set_by: agent` and a reason. These field names come from [ravenseat](https://github.com/vegardjorg/ravenseat)'s `priority_set_by` and [mem](https://github.com/nicsuzor/mem)'s linted `set_by`.
   - **The rule:** the check compares each commit with its base. A change to a protected value, or a write of `set_by: human`, by a commit carrying the agent trailer fails. The agent writes its proposal to `backlog/proposals.md` instead, as ravenseat starts agent-added tasks as proposed until the owner approves them (docs only). It protects relative order among human-ordered tasks, not raw `ordinal` values, because Backlog.md rewrites neighbouring ordinals on a reorder.
   - **What it is today:** while the developer makes every commit, B is a review aid that points at protected changes in the diff. It becomes enforcement once agents commit with a trailer (decision 2). Identity is self-declared in every tool read, so git review remains the backstop.
   - **Showing proposals:** the SessionStart brief and the generated `proposals.md` show pending proposals, rather than a change to Backlog.md's board (decision 3). [doctrine](https://github.com/davidlee/doctrine) can grade agent-only judgements as "AgentProposed" behind an opt-in setting that is off by default.
4. **Piece C: a granularity and readiness lint** (medium). Nothing found statically flags a task that mixes human and agent work, or a parent with unsplit work (rounds 3-5).
   - Only leaf tasks are actionable, as in pm-cli's `pm next`.
   - A parent can't close while a child is open, as in [treadling](https://github.com/Abhijeet34/treadling).
   - Each task type has required fields before it is ready, treadling's definition-of-ready gate.
   - A human task may hold no checklist item marked `[agent]` (decision 7: a per-item performer marker makes this a deterministic check).
   - Readiness criteria come from [What Makes a GitHub Issue Ready for Copilot?](https://arxiv.org/abs/2512.21426). Its author reports that issues scoped to one automated change merged 16.4% more often (paper-reported). [agent-preflight](https://github.com/jawnty/agent-preflight)'s deterministic scoring (hard gates, a regex scope check that suggests splitting) is a source of rules.
   - Reject any task file carrying Backlog.md's `onStatusChange` key. Backlog.md runs that key as `sh -c` when the task's status changes, so a task file from a pull request could carry a command. A reviewer who checks out the branch and changes a status runs it before CI does, so this rule also belongs in the pre-commit hook. Whether Backlog.md can disable the key in its config wasn't found; [the tool-feedback page](../tool-feedback/backlog-md.md) proposes that.
   - At run time, park a task whose agent part is done and whose remaining acceptance needs a person, as [bmad-loop](https://github.com/bmad-code-org/bmad-loop)'s `awaiting-operator` does, rather than blocking it.
5. **Piece D: claiming** (small to medium). Backlog.md's claim is a convention (status plus assignee), not atomic, so two agents in parallel worktrees can claim one task.
   - Propose an atomic `task claim` upstream (decision 4). It would check status and assignee and write them under the create lock Backlog.md already keeps in the git common directory, which every worktree shares.
   - Fallback: a small claim file under that lock, kept by the wrapper the hook uses.
6. **Piece E: SessionStart hook and agent queue** (small), carried over from the 2026-11-06 note. It prints in-progress work first, then the top ready tasks with `performer: agent` and their tier, then items waiting on a human, then pending proposals. A small wrapper gives agents the same filtered queue, since Backlog.md's `--ready` has no performer filter. Claude Code caps hook output at 10,000 characters (docs only).
7. **Piece F: push-only sync to GitHub, built last** (large). No tool found does bidirectional sync well (answer below).
   - Map parents to native sub-issues, dependencies to native blocked-by, and priority to the Priority issue field. `gh` gained flags for these in 2.94; the installed `gh` is 2.46, so pin a newer one through mise.
   - **Remote edits:** before each push, compare the issue with the state recorded at the last push. A field a collaborator changed is reported and not overwritten (decision 8). Status changes come back as a proposal in `proposals.md`. Comments stay on GitHub and are linked from the task.
   - Borrow [ADLC](https://github.com/voodootikigod/adlc) ticket-sync's failure design: an idempotent create key, refusing a listing that may be truncated, writing the stored base only after a successful store write, and refusing a conflict rather than guessing.
   - Borrow [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync)'s random temporary IDs and native relationship mapping, but not its replacement of the whole remote link set.
   - Avoid the failure paths read in source (Limitations):
     - errors read as deletions ([gitpm](https://github.com/yevheniidehtiar/gitpm));
     - failed edits recorded as synced (gh-issue-sync);
     - creates whose issue number isn't written back ([pm-github](https://github.com/unbraind/pm-github), [pm-jira](https://github.com/unbraind/pm-jira)).
   - Jira only when a project needs it, push-only on the same design.

**Upstream changes to propose to Backlog.md** (small each): reject dependency cycles on write, reusing its existing `findCycleThroughRoot`; the atomic claim; per-task `onStatusChange` callbacks off unless the project config allows them. Its receptiveness to outside PRs is low (table below), so each piece must also work without them.

### The alternative: build on pm-cli

pm-cli's store covers what this blend's pieces A, C and D add:
- an `execution_role` per item type, with Decision human, Milestone a gate and other types agent;
- `pm next`, which holds human items, gates and parents with open children out of the agent queue;
- atomic claim within one working tree;
- a history of each change with author, harness and model.

Its policies don't protect human decisions on their own. Field-writer and approval policies default to advise rather than refuse, and any actor can change or remove them, an action that is only logged. Identity is self-declared.

The same pieces, sized for pm-cli:
- A: a model tier field (small, through its custom fields) and a performer field naming the human (small);
- B: still needed (medium), with refuse mode set and policy changes added to the check;
- C: the mixed-work rule and the `onStatusChange`-style hygiene don't apply, but the parent and definition-of-ready rules remain (small to medium);
- D: cross-worktree claims rely on its merge driver, which wasn't read (unknown);
- E: the hook (small);
- F: fixing pm-github's issue write-back and conflict checks upstream, or building F as above (large). Its optional sync workflow arms auto-merge to the default branch, so leave that out.
- Views: pm-graph's Mermaid or DOT output rendered in mdBook or a board (medium).

It also stores items as TOON (a compact, YAML-like text format), which doesn't render as Markdown on GitHub. It fits better if attributable agent provenance matters more than the board, the format and maturity.

### Bidirectional sync, answered

Nothing read does it well:
- **ADLC ticket-sync** is the most careful design. It checks its structured fields three ways and fails closed, but title and body are remote-wins, comments aren't pulled, and it covers Issues only.
- **gh-issue-sync** merges per field on push. But a failed edit is recorded as synced, the pull cursor can skip changes, and a push replaces the remote link set, removing links a collaborator added.
- **Projects v2 field values:** no tool read in source syncs them. [issync](https://github.com/jasonmadigan/issync) claims to, at README depth, and its repository has no license file.
- **Jira:** no tool documents deletions and comments in both directions. Jira's dynamic webhooks are for Connect and OAuth apps only and expire after 30 days, so a local tool must poll and can't see deletions (docs only).
- **GitHub deletions:** the REST API returns 404 for an issue transferred to, or deleted from, a repo the caller can't read, so a polling sync can't tell deleted from moved (docs only).
- **Literature:** a 12-month arXiv search for bidirectional issue-tracker sync returned nothing.

### Open decisions for the developer

| # | Decision | Recommendation | Alternative |
|---|---|---|---|
| 1 | Which store to build on | Backlog.md: views, Markdown, maturity; custom pieces carry the governance | pm-cli: native human/agent queue split and per-change model provenance; no board, TOON files, one maintainer |
| 2 | Piece B's role while the developer makes every commit | A review aid now, enforcement once agents commit with a trailer | Enforce from the start with signed human commits or a human-only command for protected edits |
| 3 | Where agent proposals show | The SessionStart brief and a generated `proposals.md` | A change to Backlog.md's web board (upstream or a fork) |
| 4 | Claiming across worktrees | An upstream `task claim` under the shared lock, with a local claim file as fallback | Accept convention-only claims and rely on one agent per task by assignment |
| 5 | Model hint on agent tasks | A capability tier as a floor plus an optional `suggested_model` | A tier only, choosing the model at dispatch |
| 6 | Which human decisions piece B protects | Priority, relative order, performer, acceptance criteria and decision records | Priority and order only |
| 7 | How piece C spots agent work inside a human task | A per-checklist-item `[agent]` / `[human]` marker and a deterministic lint | An agent or reviewer judgement at triage, with no marker |
| 8 | Collaborator edits on GitHub (U5) | Piece F detects edits since the last push, reports them, and never overwrites them | Treat GitHub as read-only for collaborators; the next push wins |

**Suggested order:**
1. Settle decision 1.
2. Run the chosen tool's pinned release in a throwaway directory to confirm its side effects (the run test #196 proposes).
3. Trial it in two repos with pieces A, C (including the `onStatusChange` rule) and E.
4. Add piece B, then D.
5. Build piece F only when a collaborator needs it.

Each piece goes through LID.

## Candidates and matrix

Ranked shortlist for the store:

1. **[Backlog.md](https://github.com/MrLesk/Backlog.md):** meets every hard criterion (H3 as extensible), with the best views and maturity (237 npm versions, about 93,000 npm downloads a month, in Homebrew core). It would drop if `onStatusChange` couldn't be fenced off, or if the custom pieces grew past their sizes.
2. **[pm-cli](https://github.com/unbraind/pm-cli):** the closest fit for R1, R6 and R8, read in source. It would rank first if it gained a board and a second maintainer, or if the developer weighted per-change provenance above views.
3. **[treadling](https://github.com/Abhijeet34/treadling):** the best readiness and override design (overrides that need a named guard and a reason, a definition-of-ready gate, stale writes refused), but no views, no sync and no adoption yet. A source of rules for piece C.
4. **[doctrine](https://github.com/davidlee/doctrine):** the most developed priority model, with human pins outranking agent claims on value. But its order is computed rather than set by a person, an agent row can retire a human one, and `install` brings in a whole governance process that would compete with LID. A source of ideas for piece B.
5. **[tbd](https://github.com/jlevy/tbd):** the assignee/delegate split, a claim that checks for another agent's live claim, and agent files generated per model tier. Its backlog lives on a sync branch under `.git` that a plain grep misses, and setup writes hooks into `.claude/settings.json`.

For sync, [ADLC](https://github.com/voodootikigod/adlc) ticket-sync has the best failure design and [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync) the best mapping to GitHub's relationships; neither is adoptable as is.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | build on | MIT (`LICENSE:1-21` at 52b4ea3) | Store, board, dependency view, MCP; no performer kind, no priority protection, no sync |
| [pm-cli](https://github.com/unbraind/pm-cli) | build on (alternative) | MIT (`LICENSE:1-21` at e67c5e4) | Human/agent queue split, per-change provenance, atomic claim; advisory policies any actor can change; no board; one maintainer |
| [pm-graph](https://github.com/unbraind/pm-graph) | borrow ideas | MIT (`LICENSE:1-3` at 5e74925, read at snippet depth) | Mermaid and DOT export of the pm graph; consent per cross-workspace edge |
| [pm-github](https://github.com/unbraind/pm-github) | reject | MIT (`LICENSE:1-21` at 6ccb293) | Export doesn't write the issue reference back, so a re-export duplicates issues; import overwrites local edits |
| [pm-jira](https://github.com/unbraind/pm-jira) | reject | MIT (`LICENSE:1-21` at e599200) | Re-push duplicates Jira issues; closures and comments never come back |
| [treadling](https://github.com/Abhijeet34/treadling) | borrow ideas | Apache-2.0 (`LICENSE:1-202` at ad4eee1) | Reasoned overrides, definition-of-ready gate, stale-write refusal |
| [doctrine](https://github.com/davidlee/doctrine) | borrow ideas | GPL-3.0-only for the binary (`Cargo.toml:7`, `LICENSE-GPL-3.0:1-674` at d3c19d7); MIT for plugins and install files | Human and agent judgements tiered, pins outrank agent claims; computed order; `install` writes harness config in and outside the repo |
| [tbd](https://github.com/jlevy/tbd) | borrow ideas | MIT (`LICENSE:1-21` at f356208) | Assignee/delegate split, agent files per model tier; backlog under `.git` |
| [beadhive](https://github.com/beadhive/beadhive) | borrow ideas | MIT (`LICENSE:1-21` at e264f72) | Capability tier per task, model chosen at dispatch; built on a Dolt database (fails H2); its merge command lands work on main by default |
| [ADLC](https://github.com/voodootikigod/adlc) | borrow ideas | MIT (`LICENSE:1-21` at 0da571c) | Fail-closed ticket sync, deterministic model-tier rules, readiness gate; no priority or performer field; an `--authorize` flag any agent can pass |
| [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at 955fe4c) | Native relationships, per-field three-way push; failed edits recorded as synced; drops unknown keys |
| [gitpm](https://github.com/yevheniidehtiar/gitpm) | reject | MIT (`LICENSE:1-21` at 00f6d1c) | Hash-format mismatch overwrites local fields on every sync; any API error cancels local tasks |
| [git-task](https://github.com/jhspetersson/git-task) | reject | GPL-3.0-or-later (`LICENSE:1-674` at 41844a7) | Tasks live in a git ref (fails H2); last writer wins on sync |
| [planr](https://github.com/instructa/planr) | borrow ideas | MIT (`LICENSE:1-21` at e27e913) | "Waiting on you" view, static HTML board; its CLI enforces no human-only rule, and only its optional board plugin checks approvals; `init` writes git hooks |
| [kanban-md](https://github.com/antopolskiy/kanban-md) | reject | MIT (`LICENSE:1-21` at e3816f2) | Its skill merges to main on its own; claims not atomic; silent ID renumbering breaks links |
| [beans](https://github.com/hmans/beans) | reject | Apache-2.0 (`LICENSE:1-201` at 99260bf) | Drops unknown frontmatter keys; its web UI starts Claude with `--dangerously-skip-permissions` |
| [ravenseat](https://github.com/vegardjorg/ravenseat) | borrow ideas | MIT (pointer only) | `priority: owner`, `priority_set_by`, a required reason; agent-added tasks start proposed and a track worktree can't approve them (docs only); store is gitignored JSON (fails H2) |
| [mem](https://github.com/nicsuzor/mem) | borrow ideas | GPL-3.0 (pointer only) | `set_by` on every edge, linted; single-user |
| [bmad-loop](https://github.com/bmad-code-org/bmad-loop) | borrow ideas | MIT (`LICENSE` opening lines; a contributor-attribution note not read) | `awaiting-operator` parks tasks whose remaining work is human; policy files committed in about 15 other repos |
| [agent-preflight](https://github.com/jawnty/agent-preflight) | borrow ideas | MIT (`LICENSE` read at dbb39ae) | Deterministic readiness scoring with hard gates and a split suggestion; no mixed-work or parent rule |
| [lattice](https://github.com/salahmyn/lattice) | borrow ideas | MIT (pointer only) | A suitability field per task (agent autonomous, agent pair, human only); agents never approve requirements |
| [microsoft/hve-core](https://github.com/microsoft/hve-core) | borrow ideas | MIT (pointer only) | Read-only triage writes recommendations; executor halts on unchecked human-review boxes; tracker is the store (fails H2) |
| [software-factory](https://github.com/musicofhel/software-factory) | borrow ideas | MIT (pointer only) | Ticket store written only from main, by a post-merge job or a human's PR |
| [Linear](https://linear.app/docs/assigning-issues.md), hosted | borrow ideas | hosted | An agent delegate separate from the human assignee, who stays owner |
| [GitHub Copilot approvals](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automation-rationale-and-approvals), hosted | borrow ideas | hosted | Agent changes below a confidence threshold held as suggestions with a rationale |
| [beads](https://github.com/gastownhall/beads) | reject | MIT (2026-11-06 note) | Dolt database store; an upgrade that forced Dolt broke one user's setup (docs only) |
| [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | reject | MIT plus Commons Clause (2026-11-06 note) | License |
| [imdone-cli](https://www.npmjs.com/package/imdone-cli), [AgiFlow po](https://github.com/AgiFlow/po), [agent-kanban](https://github.com/saltbo/agent-kanban) | reject | Proprietary, BUSL-1.1, FSL-1.1 (registry or badge pointers) | License |

About 245 further candidate records were judged variants or not serious; one of them is a bulk entry for about 110 orchestrators from one awesome list. Most are Markdown or SQLite agent trackers with mechanisms already listed, beads viewers and wrappers, MCP wrappers around hosted trackers, and per-prompt model routers that store nothing on a task. Round-1 shortlist entries dropped on closer reading:
- [orbit](https://github.com/rcmendes/orbit): tasks on an orphan branch, pre-alpha;
- [knots](https://github.com/acartine/knots): an event log plus a SQLite cache;
- [tkt](https://github.com/smileynet/tkt): every write is a commit, and a push is the claim;
- [crosslink](https://github.com/forecast-bio/crosslink), [kyosei](https://github.com/jbmv/kyosei) and [markplane](https://github.com/zerowand01/markplane): their mechanisms are covered by the finalists.

**Matrix, stores.** Symbols: ✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified. H marks hard criteria. Cells rest on the source readings under Limitations, and "(snippet)" marks a reading at snippet depth.

| Criterion | Backlog.md | pm-cli | treadling | doctrine | tbd | kanban-md | beans | planr |
|---|---|---|---|---|---|---|---|---|
| H1 license | ✓ MIT | ✓ MIT | ✓ Apache-2.0 | ✓ GPL-3.0-only | ✓ MIT | ✓ MIT | ✓ Apache-2.0 | ✓ MIT |
| H2 greppable files | ✓ `backlog/*.md`; tasks on other branches show on the board but aren't greppable | ✓ `.agents/pm/*.toon` | ✓ `.work/` month shards | ✓ `.doctrine/` TOML and Markdown | ◐ under `.git/tbd/` | ✓ `kanban/tasks/` | ✓ `.beans/` | ✓ `tasks/*.md` |
| H3 human authority | ⊕ unknown keys survive; a check is needed | ◐ policies advise by default; any actor can change them; self-declared identity | ◐ reasons logged; any actor may change priority | ◐ human tier outranks agents on value claims; self-declared rater; agent rows can retire human rows | ⊕ | ⊕ | ✗ unknown keys dropped | ✗ CLI has no human-only rule |
| H4 local | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H5 no auto-merge | ✓ `autoCommit` off by default | ✓ | ✓ runs no git | ◐ `land` merges into the current branch, and its skills may run it (snippet) | ✓ commits on `tbd sync`, plus setup's first commit and push of its branch | ✗ its skill merges to main | ◐ web UI merges on a click | ◐ board plugin pushes on a click |
| R1 performer, model | ◐ free-text assignees | ◐ role per item type; no per-task performer or model | ◐ free-text assignee | ✗ no assignee field | ◐ assignee/delegate; no tier field | ⊕ custom properties | ✗ | ◐ free-text owner |
| R2 ready, cycles | ✓ ready; cycles only reported | ✓ ready (snippet); cycles only reported | ✓ cycles refused | ✓ cycles diagnosed (snippet) | ✓ cycle detection in the clone; no record | ✓ cycles refused | ✓ (snippet) | ✓ cycle check |
| R5 views | ✓ web board, dependency graph | ◐ Mermaid via pm-graph | ✗ no renderer in the clone; no record | ✓ graph render, local map server (snippet) | ? `tbd web` not read | ◐ TUI | ◐ web board, TUI (snippet) | ✓ static HTML board |
| R6 granularity | ◐ parent and subtasks | ◐ only leaves actionable | ✓ definition-of-ready, epic close gate | ? | ◐ | ◐ parent links (snippet) | ◐ type hierarchy (snippet) | ◐ goal scopes |
| R7 sync | ✗ | ◐ separate packages, faulty | ✗ | ✗ | ◐ Linear only (snippet) | ✗ | ✗ | ✗ |
| R8 claim | ◐ convention | ✓ atomic within one tree | ◐ per-record version check in one tree; no claim verb (snippet) | ◐ append-only records merge in any order; no claim verb found | ✓ refuses another agent's live claim | ✗ not atomic | ◐ in-process only | ◐ convention |
| Side effects | ◐ fetch `--prune` by default; `onStatusChange` runs shell | ◐ `init` adds merge-driver lines to `.gitattributes` and git config by default | ✓ writes only `.work/` | ✗ `install` writes CLAUDE.md, AGENTS.md, `.claude/settings.json`, `.mcp.json`, `~/.codex/config.toml` (snippet) | ◐ hooks in `.claude/settings.json` | ◐ `init` gitignores the board on Enter | ◐ `.beans.yml` at the root; web UI writes `~/.beans/worktrees` | ◐ writes git hooks |
| Maturity | ✓ | ◐ 100+ releases, one maintainer | ✗ 0 stars | ◐ | ◐ | ◐ | ◐ idle since 2026-04 | ◐ |

R9 (cross-repo) is unsupported in all eight beyond reading another directory; the verdict keeps the 2026-11-06 note's design (a PR into the receiving repo's backlog). Installability: Backlog.md, pm-cli, planr and tbd are on npm, kanban-md and beans are Go modules, doctrine is a crate, and treadling is on npm, so mise can install and Renovate can update each one.

**Matrix, sync (U5):**

| Criterion | [ADLC](https://github.com/voodootikigod/adlc) ticket-sync | [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync) | [gitpm](https://github.com/yevheniidehtiar/gitpm) | [pm-github](https://github.com/unbraind/pm-github) | [pm-jira](https://github.com/unbraind/pm-jira) | [git-task](https://github.com/jhspetersson/git-task) |
|---|---|---|---|---|---|---|
| Direction | both (Issues) | both (GitHub) | both (5 trackers) | both: import updates title, body and assignee; `sync` pushes status only | Jira to pm create-only; push | both, last writer wins |
| Conflict detection | ◐ three-way on structured fields; title and body remote-wins | ◐ per field on push; pull skips edited files | ✗ whole entity; `ask` discards the answers | ✗ | ✗ | ✗ |
| Base advanced only on success | ✓ | ✗ failed edits recorded as synced | ◐ checkpoint file | n/a (no watermark) | n/a (no watermark) | n/a (no watermark) |
| Errors vs deletions | ✓ refuses truncated listings | ✗ no 301/404/410 handling | ✗ any error cancels the task | ? | ✗ | ✗ |
| Comments | ✗ | ◐ create-only, queued | ✗ | ◐ | ✗ | ◐ remote replaces the local list |
| Native sub-issues and blocked-by | ✗ | ◐ push replaces the remote link set | ✗ | ✗ | ✗ | ◐ sub-issues |
| Projects v2 fields | ✗ | ✗ membership only | ✗ stubs | ◐ status only | n/a | ✗ |
| Rate limits | ✗ | ✗ | ◐ only when a successful response shows zero remaining | ✓ | ✗ | ✗ |

**Blends considered:**

- **Backlog.md plus custom pieces:** the verdict.
- **pm-cli plus custom pieces:** the alternative above.
- **Backlog.md for views over pm-cli's store:** two tools owning one backlog in different formats; rejected.
- **GitHub Issues as the store, with a local mirror:** GitHub's native relationships and Priority field are good (docs only). But no mirror read keeps descriptions current and sees deletions (sync matrix), work in progress isn't in the repo, and Projects has no dependency-graph view (docs only). Kept as a push target.
- **Claude Code's task tools as the store:** they store lists under `~/.claude/tasks/`, outside the repo (fails H2), and have no owner field (docs only). Useful only inside a session.
- **The 2026-11-06 custom format** (one file per task plus a hand-ordered `TASKS.md`): Backlog.md is that design with a board, readiness, MCP and an archive already built. Its order lives in `ordinal` rather than in an index file.

**Scenario walk.** The finalists are the Backlog.md blend and the pm-cli blend. The developer's use cases come first, then generic scenarios:

1. **U1: an agent proposes a reorder.**
   - Backlog.md: nothing in the tool stops an MCP or CLI edit of `ordinal` or `priority`. Piece B flags a change to the relative order of human-ordered tasks: it fails an agent-trailer commit, or marks the diff for review while the developer makes every commit. The agent's intended order goes to `proposals.md`, which the brief shows.
   - pm-cli: a refuse-mode field-writer policy rejects the agent's edit and logs it with the agent's name and model. But enforcement defaults to advise, and an agent can switch it back, so piece B is still needed.
2. **U2: a human decision plus agent pieces.**
   - Backlog.md: a parent with subtasks. The human subtask has `performer: human:<login>`, and the brief's ready list shows only agent tasks. Piece C fails a human task holding a checklist item marked `[agent]`.
   - pm-cli: a Decision item is held out of `pm next` natively, and agent tasks are leaves.
3. **U3: two agents in parallel worktrees.**
   - Backlog.md: unique IDs through the shared lock. Claims are a convention until piece D adds an atomic claim under the same lock.
   - pm-cli: atomic within one tree; across worktrees its merge driver settles the files afterwards (not read).
4. **U4: the developer's view.**
   - Backlog.md: `backlog browser` gives the board, the dependency graph and statistics. Pending proposals are in `proposals.md`.
   - pm-cli: Mermaid text to render elsewhere.
5. **U5: push to GitHub.**
   - Both: piece F pushes parents, blocked-by and priority to GitHub's native fields. A collaborator's status change is reported at the next push and comes back as a proposal, never overwritten. Comments stay on GitHub, linked from the task.
6. **A fresh CI clone.**
   - Backlog.md installs from npm at a pinned version through mise, and pieces B and C run in CI as they do in pre-commit.
   - pm-cli installs from npm the same way.
7. **A task file from another repo's PR (R9).**
   - Piece C's pre-commit and CI rule rejects an `onStatusChange` key, and the receiving developer reviews the file like any other.

**Upstream receptiveness** (the last 50 closed PRs, outside authors only):

| Candidate | Outside PRs merged | Median days to merge (outside) | Open PRs | Policy on AI-assisted contributions |
|---|---|---|---|---|
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | 2 of the 6 outside PRs among 50 closed | 3.0 | 21 | `CONTRIBUTING.md:19` points contributors and AI agents to `AGENTS.md` |
| [pm-cli](https://github.com/unbraind/pm-cli) | 0 (9 of the 50 from bots) | n/a | 1 | None stated; `CONTRIBUTING.md:211-213` says automated reviews don't replace human approval |
| [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync) | 0 of 3 outside among 5 closed | n/a | 1 | None found |

**Gaps in the leading candidate** (classified additive or fundamental, as #202 proposes):

| Gap in Backlog.md | Class | Extension point | Size | Route |
|---|---|---|---|---|
| Performer and tier fields | additive | Unknown frontmatter keys survive rewrites (`src/markdown/frontmatter.ts:61-91`) | small | Piece A, no fork |
| Human authority over decisions | additive | The same keys; enforcement in a separate check | medium | Piece B, outside the tool |
| Cycle rejection on write | additive | `findCycleThroughRoot` (`src/utils/dependency-graph.ts:219`) | small | Upstream PR |
| Atomic claim | additive | The per-task lock lasts only for one edit | small to medium | Upstream PR, or piece D |
| Granularity lint | additive | Readiness and parent data exist | medium | Piece C, outside the tool |
| GitHub/Jira sync | additive | No integration layer | large | Piece F, outside the tool |
| Cross-repo filing | fundamental | One backlog per project root by design | n/a | A PR into the other repo's backlog |

## Limitations checked in source

Readings are from shallow clones at the commits named; nothing was installed, built or run. Every license marked with a file and line range was read in full and grepped for riders, restrictions and Commons Clause, except [pm-graph](https://github.com/unbraind/pm-graph)'s (lines 1-3) and [bmad-loop](https://github.com/bmad-code-org/bmad-loop)'s (opening lines). None had a rider.

**[Backlog.md](https://github.com/MrLesk/Backlog.md)** (at 52b4ea3):
- One Markdown file per task with YAML frontmatter; plan, notes, comments, acceptance criteria and summary are body sections. Tasks on other branches are read through `git ls-tree` and `git show`, not from the working tree. *Verified in source* (`src/constants/index.ts:4-39`, `src/markdown/serializer.ts:53-127`, `src/core/cross-branch-tasks.ts:28-80`).
- No lock, pin, approval state or provenance on priority or order. MCP `task_edit`, the CLI's `--ordinal` and board drag all set `ordinal`, and a reorder can rewrite other tasks' ordinals. *Verified in source* (`src/types/index.ts:46-88`, `src/core/reorder.ts:17-143`, `src/core/backlog.ts:3459-3560`).
- No push, merge, checkout or rebase in non-test source. `autoCommit` defaults to false; when on, it commits to the current branch, which can be main. *Verified in source* (`src/core/backlog.ts:1746-1757`, `src/git/operations.ts:142-293`) and by listing (a grep over non-test `src/`).
- With the default `remoteOperations: true`, ID generation runs `git fetch origin --prune`. *Verified in source* (`src/git/operations.ts:605-634`, `src/utils/id-generators.ts:45-60`).
- `onStatusChange` in a task's frontmatter runs as `sh -c` on a status change. *Verified in source* (`src/core/backlog.ts:3347-3372`, `src/utils/status-callback.ts:26-60`).
- `init` in MCP mode runs `claude mcp add -s user` and the equivalents for Gemini, Codex and Kiro; in CLI mode it appends a block to the instruction files selected. *Verified in source* (`src/utils/mcp-client-setup.ts:18-44`, `src/core/init.ts:252-300`).
- Cycles are reported by `backlog doctor`, not rejected on write. *Verified in source* (`src/utils/readiness.ts:1-121`, `src/cli.ts:5920-5921`).
- Claiming is status plus assignee by convention. The create lock lives in the git common directory, which worktrees share. *Verified in source* (`src/file-system/operations.ts:700-760`).
- No GitHub, Jira or other sync. *Verified by listing*: a grep for GitHub API, Octokit, Jira, Atlassian, Linear and GitLab over non-test `src/` gave 22 hits, all ID-prefix examples or comments.

**[pm-cli](https://github.com/unbraind/pm-cli)** (at e67c5e4):
- `execution_role` is set per item type: Decision is human, Milestone a gate, and other types agent unless a custom type sets it. `pm next` leaves human and gate items, items assigned to someone else, and containers with unfinished children out of the ready set unless asked. *Verified in source* (`src/core/item/type-registry.ts:24`, `src/core/item/actionability.ts:24-27,300-332`, `src/sdk/query/next.ts:376-418`).
- Field-writer and approval policies refuse inside the locked write, with no `--force` bypass, once the registry's enforcement is set to refuse; the default is advise. Actor names are unverified by design, taken from `--author`, `PM_AUTHOR`, a settings default or the detected harness. *Verified in source* (`src/core/policy/workflow-policy.ts:1-7,307-347`, `src/core/policy/workflow-policy-store.ts:116-197`, `src/core/shared/author.ts:1719-1750`).
- `policy-put`, `policy-remove` and `policy-mode` have no author restriction and are only logged. *Read at snippet depth* (verification records).
- Claim is a test-and-set under a per-item file lock with a TTL, within one working tree. *Verified in source* (`src/sdk/lifecycle/claim.ts:192-300`).
- Priority is a 0-4 bucket with no rank. *Verified in source* (`src/core/item/priority.ts:1-83`).
- `init` installs a merge driver by default: a `.gitattributes` block and clone-local `git config merge.<driver>.*` entries; `--no-merge-fence` turns it off. *Verified in source* (`src/sdk/merge/install.ts:945-1010`, `src/sdk/init.ts:1300-1453`).

**[pm-github](https://github.com/unbraind/pm-github)** (at 6ccb293):
- `export --apply` creates issues without writing the issue reference back, so a re-export duplicates them. *Verified in source* (`index.ts:4314-4347`).
- It patches title, body, labels and state without checking for remote edits, and re-import overwrites local title, description and assignee. *Verified in source* (`index.ts:3795-3845,4421-4480`).
- An optional reusable workflow opens a PR and arms auto-merge to the default branch. *Verified in source* (`.github/workflows/pm-github-sync.yml:654-760`).

**[pm-jira](https://github.com/unbraind/pm-jira)** (at e599200):
- The create response is discarded and no key is written back, so each `export --push` re-creates pm-originated issues. *Verified in source* (`index.ts:2437-2516,2907-2930`).
- Existing items are never updated on import, so Jira closures and edits never return. *Verified in source* (`index.ts:2108-2145`).

**[ADLC](https://github.com/voodootikigod/adlc)** (at 0da571c):
- `--authorize` is a plain CLI flag with no binding to a person. It is required only for a few sensitive edits (narrowing which paths a ticket may not change, widening its scope, completion, archive, restore, reassign and remote reconcile). Edges between tickets, the only input to order, need none. *Verified in source* (`packages/tickets/bin/adlc-tickets.mjs:34,196-210`, `packages/tickets/lib/service.mjs:204-226`).
- There is no priority field and no assignee field. *Verified by listing* (grep: 0 hits) and in source (`packages/tickets/lib/help.mjs:93-99,135-154`).
- model-router's rules:
  - contract, spec or architecture work, or a ticket with few protected paths, gets the frontier tier, run directly;
  - work on the critical path gets mid, unless the ledger has history;
  - work with float runs as a ladder that starts cheap when at least half its scope is protected, else mid.

  *Verified in source* (`packages/model-router/lib/assign.mjs:1-154`, `packages/model-router/lib/router.mjs:26-86`).
- ticket-sync's pull writes its base only after the store write succeeds, under a lock. A full page is treated as possibly truncated and refused, and a missing base is a conflict. Title and body are remote-wins, comments aren't pulled, and there is no rate-limit handling. *Verified in source* (`packages/ticket-sync/lib/pull.mjs:1-225`, `packages/ticket-sync/lib/reconcile.mjs:1-34`, `packages/ticket-sync/lib/providers/github.mjs:61-67`).
- `adlc init` writes `.adlc/`, edits `.gitignore` and, by default, writes `.codex/agents/*.toml` if missing. *Verified in source* (`packages/init/lib/scaffold.mjs:555-611`).

**[gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync)** (at 955fe4c):
- Push records a failed per-issue edit as synced, writing the local file and its original, so the edit is never retried and a later pull overwrites it. *Verified in source* (`internal/app/push.go:562-622`).
- The pull cursor is set from the local clock after the loop, so changes between the listing and that moment are missed until `--full`. *Verified in source* (`internal/app/pull.go:98-103,160-184,258-263`).
- Relationship sync makes GitHub's link set equal the local set, removing links that exist only on GitHub. *Verified in source* (`internal/ghcli/graphql.go:520-611`).
- Unknown frontmatter keys are dropped on rewrite. *Verified in source* (`internal/issue/issue.go:52-65,134-165`).
- No rate-limit or retry handling. *Verified by listing* (a grep over `internal/ghcli/client.go` and `graphql.go`: 0 hits).

**[gitpm](https://github.com/yevheniidehtiar/gitpm)** (at 00f6d1c):
- Push and import store the remote hash in the local hash format, which sync compares with a differently computed remote hash. Every pushed or imported issue therefore reads as changed remotely and overwrites local fields. *Verified in source* (`packages/sync-github/src/sync.ts:34-38,363-386`, `state.ts:160-231`).
- `getIssue` returns null on any error, which sync treats as a deletion, cancelling the local task. *Verified in source* (`client.ts:165-199`, `sync.ts:310-331`).
- Projects v2 support is stubs only. *Verified in source* (`client.ts:120-132`).

**[git-task](https://github.com/jhspetersson/git-task)** (at 41844a7): each task is a JSON blob in a commit tree on `refs/tasks/tasks`, not in the working tree. Pull is remote-wins and push local-wins, with no stored base. *Verified in source* (`src/lib.rs:442-469,547-616`, `src/operations.rs:683-741,1013-1042`).

**[treadling](https://github.com/Abhijeet34/treadling)** (at ad4eee1): only three guards can be overridden (blocked, work-in-progress limit, blocks others), and an override must name the guard and give a reason. The actor's kind is self-declared through an environment variable and only logged. *Verified in source* (`src/domain/state-machine.ts:37-110,353-402`, `src/cli/main.ts:103-107`).

**[planr](https://github.com/instructa/planr)** (at e27e913): the CLI's `set` and `goal` accept any status or state from any current one, with no identity check. The rules exist as skill text; only the optional board plugin checks approvals, when its host supplies an identity. *Verified in source* (`skills/planr/scripts/planr.mjs:269-274,333-363`, `skills/planr/scripts/lib/graph.mjs:321-352`, `bb-plugin/identity.ts:18-31`).

**[tbd](https://github.com/jlevy/tbd)** (at f356208): issues live on an orphan `tbd-sync` branch in a hidden worktree under the git common directory, shared by linked worktrees. `tbd sync` commits and pushes that branch, as does setup's first commit of a new branch. There is no tier or model field on an issue. *Verified in source* (`packages/tbd/src/lib/paths.ts:4-32`, `packages/tbd/src/file/git.ts:2309-2390`, `packages/tbd/src/cli/commands/start.ts:105-165`).

**[beadhive](https://github.com/beadhive/beadhive)** (at e264f72): capability tiers are labels in the beads database, classified from task text when missing. The model is resolved at dispatch from a routing table with a floor and ceiling per model. *Verified in source* (`src/beadhive/complexity.py:21-130,496-607`, `src/beadhive/model_routing.py:183-412`). The backlog is beads' Dolt store, with JSONL only as an optional export: *docs only* (`docs/BEAD-BACKENDS.md:19-56`).

**[kanban-md](https://github.com/antopolskiy/kanban-md)** (at e3816f2):
- Its bundled skill tells agents to `git switch main` and merge the task branch. *Verified in source* (`internal/skill/skills/kanban-based-development/SKILL.md:48-50,160-208`).
- `PickAndClaim` isn't serialized. *Verified in source* (`internal/board/mutate.go:636-706`).

**[beans](https://github.com/hmans/beans)** (at 99260bf):
- Fixed structs drop unknown frontmatter keys on rewrite. *Verified in source* (`pkg/bean/bean.go:169-260`).
- The web UI's default mode launches `claude -p --dangerously-skip-permissions`. *Verified in source* (`internal/agent/claude.go:807-845`).

**[doctrine](https://github.com/davidlee/doctrine)** (at d3c19d7):
- The rater of a judgement is a self-declared field that defaults to `agent`. `value pin` always writes a human-tier row, with a free-text `--by`. *Verified in source* (`src/commands/compare.rs:100-102`, `src/comparison/wire.rs:108-118`, `src/commands/facet.rs:405-420`).
- Absolute value claims rank a pin over a human over an agent, and lower tiers contribute nothing. *Verified in source* (`src/comparison/claims.rs:93-114,346-360`).
- Supersession and withdrawal ignore the rater, so an agent row can retire a human one; the only trace is a new file in the diff. *Verified in source* (`src/commands/compare.rs:285-302,637-680`, `src/comparison/resolve.rs:144-202,334-366`).
- Demoting agent evidence in pairwise comparisons is off by default. When it is on, agent rows still move bounds, placement and the question queue. *Verified in source* (`src/priority/config.rs:185-204,286`, `src/priority/surface.rs:730-846`).
- `install` writes `.gitignore`, CLAUDE.md, AGENTS.md, `.claude/` skills, SessionStart hooks in `.claude/settings.json`, `.mcp.json`, and Codex and pi config. After asking, it registers an MCP server in `~/.codex/config.toml`. *Read at snippet depth* (`src/install.rs:520-523,2955-2966,7947-7962`, `src/codex_mcp.rs:1-17`).

**Native features** (docs only):
- **Claude Code:** task tools store lists under `~/.claude/tasks/`, support dependencies and have no owner field. SessionStart hook output is capped at 10,000 characters. A subagent's model can be set per invocation.
- **GitHub:** sub-issues (100 per parent, 8 levels), blocked-by dependencies, issue types and typed issue fields, including Priority. `gh` gained flags for these in 2.94.0. Projects v2 has no dependency-graph view.
- **Jira:** links are generic link types, and each issue's changelog is readable. Dynamic webhooks are limited to apps.

Verified:
- the source claims above, at the commits named;
- every license in the candidates table marked with a file and line range, read in full except pm-graph's and bmad-loop's.

Could not verify:
- the run test #196 proposes: the chosen tool's pinned release run in a throwaway directory, to confirm `autoCommit` off, the fetch behavior and `init`'s writes. It needs the developer's approval to run a candidate on this machine;
- pm-cli's cross-worktree merge driver and its policy-change commands (snippet depth);
- `tbd web`, doctrine's granularity rules and `install` writes (snippet depth);
- licenses marked "pointer only" ([ravenseat](https://github.com/vegardjorg/ravenseat), [mem](https://github.com/nicsuzor/mem), [lattice](https://github.com/salahmyn/lattice), [hve-core](https://github.com/microsoft/hve-core), [software-factory](https://github.com/musicofhel/software-factory)) and bmad-loop's attribution note;
- [issync](https://github.com/jasonmadigan/issync)'s Projects v2 sync and [gh-md](https://github.com/jackchuka/gh-md)'s comment sync (README depth);
- Codeberg (unavailable: HTTP 429 in rounds 1, 2 and 5);
- [A Framework for Governance Policies in Human-Agent Software Development](https://doi.org/10.1145/3844953): its author-hosted open-access copy failed TLS certificate verification, which wasn't bypassed, so it stays abstract only.

## Papers

Claims are paper-reported. "Setting" says whether the paper's situation matches a repo-file backlog read by coding agents and people.

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag); setting |
|---|---|---|---|---|---|
| [What Makes a GitHub Issue Ready for Copilot?](https://arxiv.org/abs/2512.21426) | read in full | observational study | preprint | borrow ideas | The author reports issues scoped to one automated change merged 16.4% more often, and self-contained issues 16.7% more often (paper-reported). Setting matches: issue text read by an agent |
| [Effective Strategies for Asynchronous Software Engineering Agents (CAID)](https://arxiv.org/html/2603.21489) | read in part (§2, §4) | experiment | preprint | borrow ideas | Delegating only from the ready set, with a worktree per agent, beat instruction-only isolation, 63.3% to 55.5% (paper-reported). Partial match: an orchestrator's in-memory plan |
| [Before the Pull Request (grite)](https://arxiv.org/html/2606.19616) | read in full | weak experiment | preprint | borrow ideas | Leases plus shared done-state cut duplicate work from 78% to 0% in simulation; a last-writer-wins file baseline silently dropped edits (paper-reported). Partial match: synthetic agents, state in git refs |
| [Closed-Loop Autonomous Software Development via Jira-Integrated Backlog Orchestration](https://arxiv.org/html/2604.05000) | read in part (§3.1, §3.10-3.12, §5.4) | qualitative study | preprint | borrow ideas | A local backlog is authoritative and Jira is the status surface; claims are an atomic transition; an outbox replays writes; uncertain states go to human review (paper-reported). Setting matches |
| [Claim Plane](https://arxiv.org/abs/2607.21909) | read in full | untested proposal, with a 6-pair feasibility check | preprint | borrow ideas | "The model may propose; the control plane decides": change intents admitted atomically, with leases and fencing tokens (paper-reported). Partial match: a lock layer, not a backlog |
| [ParallelPilot](https://arxiv.org/html/2609.33113) | read in part (§4, §5.1, §7.2) | experiment | preprint | borrow ideas | Separating output dependencies from shared-file conflicts, scheduled in waves, raised participants' dependency understanding from 3.44 to 5.50 of 7 (paper-reported). Partial match: the plan lives in the tool |
| [A Gated Spec-Driven Workflow](https://arxiv.org/html/2611.05094) | read in part (§3, §5.3, §6) | qualitative study | preprint | borrow ideas | The orchestrator ran past its stop rule and once tried to rewrite a logged stop as a pass (paper-reported): prompt-only controls fail. Setting matches |
| [Getting a Grip](https://arxiv.org/abs/2611.00689) | read in part (§3, §4.2.4-6, §7.3-4, §8) | experiment | unreviewed report | borrow ideas | Changing which messages start work cut coordination failure from 42% to 13% (adjusted p=.057); roles given only as instructions did not reliably act; advice to "state who may choose the order of work" (paper-reported). Partial match: a message relay, not repo files; its code is noncommercial-licensed per the paper |
| [SWE-Router](https://arxiv.org/abs/2607.00053) | read in part | experiment | preprint | borrow ideas | Routing on task text alone has an error floor; routing on a cheap model's first turns does better (paper-reported). Mismatch: benchmark routing, but it weakens a fixed per-task model |
| [Scrouting](https://arxiv.org/abs/2608.04804) | read in part | experiment | preprint | borrow ideas | Always using the cheapest model with the scout's handoff tied the router, so the handoff carried the gain (paper-reported). Mismatch: benchmark routing |
| [Task-to-Model Optimization (T2MO)](https://arxiv.org/abs/2608.08528) | read in part | untested proposal | preprint | borrow ideas | The authors say difficulty judged up front is unreliable, prefer escalation chains where checks are cheap, and let developers pin a model per repo (paper-reported). Partial match: maps to a model-hint field |
| [Triage](https://arxiv.org/html/2604.07494) | read in full | untested proposal | preprint | borrow ideas | Pick a light, standard or heavy tier from the code health of the worst file a task touches (paper-reported). Setting matches |
| [Humanize](https://arxiv.org/abs/2610.08900) | read in part (§3) | observational study | preprint | borrow ideas | A human approves a plan contract that assigns each task to Claude or Codex; hooks write-block the goal and plan (paper-reported). Partial match: plan files in the repo |
| [SPOQ](https://arxiv.org/abs/2606.03115) | read in part | weak experiment | preprint | borrow ideas | YAML task files move from active to complete, a roadmap registry, wave dispatch, and a human who approves epics (paper-reported). Setting matches |
| [Developer Task Delegation to LLMs and the Trust Factor](https://arxiv.org/abs/2610.34317) | read in full | observational study | preprint | borrow ideas | Partial delegation dominates, and trust is the only significant predictor of delegating more (paper-reported). Mismatch: individual chat use |
| [When Parallelism Pays Off (Co-Coder)](https://arxiv.org/abs/2606.00953) | read in part (all but appendices) | experiment | preprint | borrow ideas | Partitioning by dependency cohesion raised pass rate from 56.8% to 68.1% at 28% lower cost (paper-reported). Mismatch: in-memory list, greenfield builds |
| [Mise en Place for Agentic Coding](https://arxiv.org/abs/2605.05400) | read in full | qualitative study | preprint (workshop paper) | borrow ideas | 64 dependency-aware task records were written before coding; four parallel subagents closed 43 (paper-reported). Setting matches; n=1 |
| [Autonomous Research Project Management as an Agent Skill](https://arxiv.org/abs/2609.31683) | read in part | qualitative study | preprint (workshop paper) | borrow ideas | State lives only in epic, issue and comment Markdown files, which only one agent may change (paper-reported). Setting matches |
| [An Exploratory Study of Agent Plans](https://arxiv.org/abs/2608.04661) | read in part (§4-6) | observational study | peer-reviewed | borrow ideas | 85 plan files in 10 of 36,710 repos; most were committed once and never revised (paper-reported). Partial match: plan files in repos |
| [The Agent Board](https://arxiv.org/html/2611.04100) | read in part (§3, §6, §7) | qualitative study | preprint | borrow ideas | The board guarantees attribution and delivery but not exclusive claims or protection from lost updates, which are left to prompts (paper-reported). Mismatch: hosted |
| [AgenticFlict](https://doi.org/10.1145/3805760.3814923) | abstract only | observational study | peer-reviewed | borrow ideas | The abstract reports textual merge conflicts in 27.67% of agent PRs. Partial match |
| [A Framework for Governance Policies in Human-Agent Software Development](https://doi.org/10.1145/3844953) | abstract only | untested proposal | peer-reviewed | borrow ideas | The abstract describes a language for roles, votes, deadlines and rationales, with GitHub bindings. Partial match: bears on piece B |

About 45 further papers were seen and not tabled: parallel-agent coordination benchmarks, model routers, delegation studies and issue-tracker tooling. They point the same way as the rows above:
- route by a tier and escalate, rather than fix a model up front;
- enforce rules rather than instruct them;
- keep the ready set and the claim explicit.

No paper found studies an LLM prioritizing a backlog under human authority.

## Worth retrieving manually

[A Framework for Governance Policies in Human-Agent Software Development](https://doi.org/10.1145/3844953) (DOI 10.1145/3844953). It bears on piece B's design for who may change what. OpenAlex reports a green open-access copy in the University of Luxembourg's repository, which failed TLS verification from this machine. Legal ways to get it: that repository's copy from a browser, ACM's page for the DOI, or an author request.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | `mise.toml`; `gh` 2.46.0 help; Claude Code's task tools, agent teams, hooks and subagent model docs; GitHub sub-issues, dependencies, issue fields, Projects v2 and webhook docs; Jira Cloud's OpenAPI file |
| Earlier notes and decisions | searched | The 2026-11-06 and 2026-11-09 notes; issues #166, #167, #155-#159, #191, #196, #202 |
| GitHub repository search | searched | About 165 queries over five rounds through a paced harvester, most with and without a star floor, e.g. "agent task tracker stars:>10", "git-native issue tracker", "jira markdown two-way sync", "decision queue agents", "ticket linter" |
| GitHub topics | searched | topic:task-management, kanban, issue-tracker, task-tracker, git-native, beads, ai-agents, claude-code, mcp-server, combined with task terms |
| GitHub code search | searched | About 100 queries. Field names found the best mechanisms, e.g. `"priority_set_by"`, `"performer: human"`, `"agent_proposed"`, `"complexity:REASONING"`, `"human_only" task status depends_on`, `"priority_locked"` (0 hits) |
| GitLab search | searched | 7 queries, e.g. "issue tracker agents", "markdown backlog"; mostly mirrors |
| Codeberg search | unavailable | Rate limit: HTTP 429 with no Retry-After in rounds 1, 2 and 5, after a retry each time |
| npm | searched | About 25 searches and 45 package documents, e.g. "task tracker agents", "backlog markdown", "jira sync", "agent task claim" |
| PyPI | searched | Through libraries.io (the search page returns a JavaScript challenge), plus 15 package lookups |
| crates.io | searched | About 15 keyword and crate lookups, e.g. "issue tracker", "jira sync", "task dependency graph agent" |
| Language registries | searched | Go: pkg.go.dev searches and module-proxy version lists for 9 modules. RubyGems: 7 queries, e.g. "issue tracker", "kanban", "backlog" |
| libraries.io | searched | About 35 searches across PyPI, npm, Cargo and Go, sorted by latest release, e.g. "humans agents tasks", "two-way sync issues", "definition of ready"; its dependents endpoint is disabled |
| Homebrew formulae | searched | The formula list grepped for task, todo, kanban, backlog, issue, ticket, jira and tracker |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | Alternatives pages for [Backlog.md](https://github.com/MrLesk/Backlog.md), [beads](https://github.com/gastownhall/beads), [git-bug](https://github.com/git-bug/git-bug) and [kanban-md](https://github.com/antopolskiy/kanban-md) |
| AUR | searched | 7 phrase searches, e.g. "issue tracker", "kanban", "jira-sync" |
| ecosyste.ms | searched | Keywords (agent-tasks, task-tracker, issue-tracker, jira-sync, two-way-sync, definition-of-ready) and dependents of finalists (0 for every CLI) |
| Cross-language equivalents | searched | "Alternatives to" searches for [Backlog.md](https://github.com/MrLesk/Backlog.md), [beads](https://github.com/gastownhall/beads), [claude-task-master](https://github.com/eyaltoledano/claude-task-master), [Linear](https://linear.app/docs/assigning-issues.md), [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync), [kanban-md](https://github.com/antopolskiy/kanban-md) and [pm-cli](https://github.com/unbraind/pm-cli); every registry above searched in its own language |
| Awesome lists | searched | awesome-cli-coding-agents, awesome-claude-code, awesome-software-factories (about 110 orchestrators), awesome-mcp-servers (empty response) |
| alternativeto.net | unavailable | It answers automated clients with a Cloudflare challenge; "alternatives to" web searches substituted |
| General web search | searched | About 75 queries, e.g. "two-way sync markdown files GitHub issues conflict", "Show HN git-based issue tracker for AI coding agents", "task tracker suggests which LLM model per task" |
| Hosted services | searched | Linear, Jira with Rovo, GitHub Copilot assignment and approvals, Plane, Unito, ONES (vendor docs; limitations docs only) |
| Skill directories | searched | skills.sh: 26 searches and 59 detail pages, e.g. "backlog", "ready queue", "claim task" |
| Claude Code plugin marketplaces | searched | The official marketplace file (317 plugins) grepped; only hosted-tracker connectors matched |
| MCP Registry | searched | 21 one-word queries, e.g. tasks, kanban, planner, orchestrator, claim |
| PulseMCP | searched | Its sitemap (allowed by robots.txt) grepped for about 140 task slugs, mapped to repos on GitHub; the search pages are disallowed by its robots.txt's restrictive group |
| Anthropic's skills repo | searched | Listing of 19 skills at 2c5958e; none for tasks |
| Awesome lists for agent skills | searched | Through GitHub code search and web search |
| GitHub topics for agent skills | searched | topic:agent-skills, claude-skills, mcp-server with task and backlog terms |
| aitoolnet.com | searched | Sitemap (48,212 URLs) grepped for task, backlog, kanban, issue, ticket, jira and sprint; 7 pages read |
| arXiv | searched | About 45 searches, 13 ID batches and 21 full texts, e.g. `all:"task decomposition" AND all:"coding agent"`, model routing, task readiness, human approval, issue-tracker sync (0 hits) |
| OpenAlex | searched | About 40 searches, DOI and open-access lookups, and `cites:` for CAID (23 citing works), ParallelPilot and Agent Plans |
| OpenAIRE | searched | 4 queries, e.g. "coding agents backlog prioritization"; found the "hive, not swarm" report |
| Semantic Scholar | searched | About 24 requests, e.g. "human-AI" "software engineering" task allocation. About half got HTTP 429 even with a key, so forward citations of four papers came from OpenAlex. This note uses data from Semantic Scholar |
| papers.cool | excluded | It indexes arXiv only, which was searched directly; one probe returned nothing new |
| Hugging Face papers | searched | 8 queries, e.g. "parallel coding agents task claiming", "git backed task tracker for coding agents" |
| Zenodo | excluded | Its robots.txt disallows search; only record pages linked from papers were read |
| Crossref | searched | 4 queries, e.g. "issue tracker synchronization", "work breakdown structure granularity"; low yield |
| Europe PMC | excluded | No life-sciences angle |
| Venue program pages | searched | arXiv's recent cs.SE listing (220 titles) scanned for task, backlog, priority and human-agent titles; three abstracts read; nothing relevant |

## Snowball rounds

1. **Round 1** (five subagents, one per group of services): 182 unique candidates after merging by owner/repo. Serious ones included [Backlog.md](https://github.com/MrLesk/Backlog.md), [pm-cli](https://github.com/unbraind/pm-cli), [gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync), [gitpm](https://github.com/yevheniidehtiar/gitpm), [kanban-md](https://github.com/antopolskiy/kanban-md), [beans](https://github.com/hmans/beans), [planr](https://github.com/instructa/planr), [orbit](https://github.com/rcmendes/orbit), [knots](https://github.com/acartine/knots) and [tkt](https://github.com/smileynet/tkt), plus eight papers read in full or in part.
2. **Round 2** (seeded from round 1's serious candidates; a find counted only with a new mechanism and evidence of design depth): added [ADLC](https://github.com/voodootikigod/adlc), [tbd](https://github.com/jlevy/tbd), [treadling](https://github.com/Abhijeet34/treadling) and [ravenseat](https://github.com/vegardjorg/ravenseat), the audit of GitHub's and Jira's native features, and the model-routing papers.
3. **Round 3** (seeded from round 2's novel finds only): added [beadhive](https://github.com/beadhive/beadhive), [hve-core](https://github.com/microsoft/hve-core)'s backlog skills and [software-factory](https://github.com/musicofhel/software-factory). It found nothing for a human-owned priority stored in repo files, or for a granularity check.
4. **Round 4** (seeded from round 3's novel finds): added [doctrine](https://github.com/davidlee/doctrine) (shortlist; read in source afterwards), [mem](https://github.com/nicsuzor/mem) and [bmad-loop](https://github.com/bmad-code-org/bmad-loop).
5. **Round 5** (seeded from round 4's finds, plus one route not searched before): added [agent-preflight](https://github.com/jawnty/agent-preflight) and [lattice](https://github.com/salahmyn/lattice) as sources of ideas. It confirmed that nothing found protects a human-set priority in repo files, or statically flags mixed human and agent work.

The search stopped after round 5, short of the 10-round cap. Round 5 added no candidate that could change the shortlist, but it still added candidates worth borrowing ideas from, so the skill's own stop rule (a round with no new serious candidate) wasn't met. This stop follows the rule proposed in #159 instead. Open leads:
- [issync](https://github.com/jasonmadigan/issync) (claims Projects v2 field sync with conflict detection; no license file) and [gh-md](https://github.com/jackchuka/gh-md) (pushes edited comments, won't push over a newer remote), at README depth;
- [taskmd](https://github.com/driangle/taskmd)'s Mermaid graph output with priority and status filters, for a static view;
- [park](https://github.com/picosam/park) and [agent-ready](https://github.com/agentlane/agent-ready), readiness validators at README depth;
- the 2026-11-06 note's open leads [markdown-ticket](https://github.com/andkirby/markdown-ticket) and [tissue](https://github.com/smeans/tissue).

## Refresh trigger

- Before the task-store LLD is finalized, if more than three months have passed (after 2027-02-12).
- When [Backlog.md](https://github.com/MrLesk/Backlog.md) adds sync, an atomic claim or field protection, or [pm-cli](https://github.com/unbraind/pm-cli) gains a board or a second maintainer.
- When a tool appears that protects a human-set priority in repo files, or flags mixed human and agent tasks.
- After the chosen store has run in two repos for a few weeks.
