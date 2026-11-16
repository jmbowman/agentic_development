# Prior art: cross-repo task coordination and prioritization (2026-11-16)

- **Supersedes:** the cross-repo parts of [the task-management note](2026-11-12-task-management-for-humans-and-agents.md) (its R9) and the delivery design for cross-repo "homework" in [the federated knowledge and work-items note](2026-11-06-federated-knowledge-and-work-items.md) (its need 8). Both notes' other findings stand, including the task note's verdict and its open decisions.
- **Effort:** full method, because the result shapes how every repo generated from copier-python (this system's Copier project template) coordinates work, which is costly to change later.
- **Already known:** the developer had nothing to add to the list carried over from the earlier notes and the task-management search's records. Their classes in those notes stand; none was re-read unless a round found something new about it.
  - Cross-repo mechanisms: GitHub's sub-issues, issue dependencies and Projects; [TASKS.md](https://github.com/tasksmd/tasks.md) (`repo#id` blockers); [tisket](https://github.com/cjohnhanson/tisket); [pm-graph](https://github.com/unbraind/pm-graph); [komnet](https://github.com/Komdosh/komnet) (rejected earlier); [relay](https://github.com/jcast90/relay); [orbit](https://github.com/rcmendes/orbit); [docflow](https://github.com/EvolveHQ/docflow); [momentum](https://github.com/LiminaLabsAI/momentum); [repomoot](https://github.com/dev-bude/repomoot); [p-backlog](https://github.com/expatriate/p-backlog); [khughitt/tasks](https://github.com/khughitt/tasks); [kata](https://github.com/kenn-io/kata).
  - Prioritization: [doctrine](https://github.com/davidlee/doctrine), [treadling](https://github.com/Abhijeet34/treadling), [ADLC](https://github.com/voodootikigod/adlc), [issue-graph](https://github.com/vercel-labs/issue-graph), [ravenseat](https://github.com/vegardjorg/ravenseat), [pm-cli](https://github.com/unbraind/pm-cli).
- **Supplied papers:** the developer supplied seven papers that the search could reach only as abstracts; all seven were read (Papers).

## Need and criteria

| # | Requirement | Goal or means? Underlying need |
|---|---|---|
| N1 | An agent or person in repo A files work for repo B, and B's agents find it when choosing what to do next | Means. Work discovered anywhere reaches the repo that owns it and enters that repo's normal "what next" selection, without a person relaying it |
| N2 | A task in A can be blocked by a task in B, and shows blocked until B's task closes | Means. Nobody starts work whose prerequisite elsewhere is still open, and it becomes ready when the prerequisite closes, without manual re-checking |
| N3 | The developer sees and ranks work across several repos (for example weekly), the ranking reaches each repo's agents, and human decisions on priority are never silently overridden | Goal plus means. The developer's priorities steer which repo's agents work on what, and an agent can't quietly change them |
| N4 | A template or shared-config change can create follow-up tasks in every consumer repo | Means. A change in a shared source reliably produces tracked follow-up in every consumer, and the developer can see which consumers have done it |
| N5 | An agent proposes an ordering (from the dependency graph, value and effort, pairwise comparison or an LLM judgment), a person confirms, and each pick is explained | Means. Good, justified ordering decisions for the short, medium and long term, with less of the developer's time spent ranking, under their authority, with explanations they can check. Also an approach question for the literature |
| N5a | Each task is categorized on attributes, then rules and "this over that" heuristics produce a justified ordering. The developer's own attributes: deadline; flexibility (hard deadline or someday); obligation (who would be upset, and how much the developer values that); effort; usefulness to the developer or others; how much other work it unblocks | Methods designed for people (cost of delay, multi-criteria decision analysis, requirements prioritization, personal task management) are in scope as the basis of N5, with agents helping to categorize, apply the rules and explain |

**Common uses** (from the developer's handoff; walked first under Scenario walk):

- **C1.** An agent in repo A finds a bug that belongs to repo B.
- **C2.** A task in A waits on a task in B.
- **C3.** The developer ranks the week's work across five repos.
- **C4.** A copier-python release needs a follow-up in every consumer repo.
- **C5.** A session in repo B starts and sees new incoming work.

**Hard criteria** (H1-H5 are the task note's):

1. **H1.** An OSI-approved license, read whole from the license file, usable as an installed tool in this Apache-2.0 repo.
2. **H2.** The backlog stays greppable as local plain-text files (repo files, or a complete local mirror kept current).
3. **H3.** An agent can't silently override a human-set priority or decision: the change is refused, or always surfaces as a reviewable, attributable proposal.
4. **H4.** No required hosted service besides GitHub.
5. **H5.** Never merges to the default branch on its own.
6. **H6.** Works with a Backlog.md backlog per repo, or says exactly what it would replace.

**Preferences:** delivery into an agent session; an explanation for each ranking pick; cross-repo readiness computed rather than read by eye; a cross-repo view for the developer; installable through mise and updatable by Renovate; writes nothing outside its own directory; Markdown that renders on GitHub; maintenance and maturity; low process overhead.

## Verdict

**Blend: [Backlog.md](https://github.com/MrLesk/Backlog.md) in each repo (already chosen) and [Renovate](https://github.com/renovatebot/renovate)'s Copier manager (already in the stack), plus five custom pieces, G to K, with [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas) as an optional part of the cross-repo view.**

No tool found computes readiness across per-repo file backlogs. The nearest, [onetaskgraph](https://github.com/nickderobertis/onetaskgraph), reads several task sources (Markdown folders among them) without a central store, routes writes to another source and records cross-source dependencies, but never follows those dependencies to decide what is ready, and doesn't read Backlog.md's layout. Every other tool with a real cross-repo mechanism replaces the per-repo backlog with one central store (a ledger, a hub database, GitHub Issues, a Dolt database) or carries messages rather than tasks.

The developer stopped the search after round 7, before the skill's stop rule (a round adding no new serious candidate) was met: each of rounds 2 to 7 added ideas worth borrowing. None after round 1 changed the verdict, and the shortlist stopped changing after round 5. Snowball rounds lists the open leads.

The task note's pieces, referred to below: **A** performer and model fields; **B** the human-authority check (protected fields, run in pre-commit and CI; a review aid until agents commit with a trailer); **C** the granularity and readiness lint (including rejecting `onStatusChange` keys); **D** claiming; **E** the SessionStart hook and the agent queue wrapper; **F** push-only sync to GitHub.

### What the stack already does

Each item is verified in source unless tagged.

- **Backlog.md keeps custom frontmatter.** When it rewrites a task it copies every key it doesn't own back as source text, and a test covers nested custom maps written through its CLI, MCP and web paths (`src/markdown/frontmatter.ts:57-194`, `src/markdown/serializer.ts:53-129` at 52b4ea3). Cross-repo blockers, priority records and the N5a attributes can live in task files as custom keys.
- **Backlog.md's IDs are local:**
  - its CLI and MCP refuse a dependency that doesn't resolve in the local backlog (`src/utils/task-builders.ts:67-104`), and a foreign ID written by hand fails closed: the task shows "Unknown dependency" and is never ready (`src/utils/readiness.ts:74-105`);
  - promoting a draft gives it a new ID from the task sequence (`src/core/backlog.ts:3181-3225`), so a reference to a draft's ID breaks when it's accepted;
  - its `project` field names a component of a monorepo, not another repo (`src/types/index.ts:78-79`).
- **Backlog.md shows tasks from other branches.** With `checkActiveBranches` (on by default), tasks on other local branches, and on `origin/*` branches unless `remoteOperations` is off, appear read-only on the board (`src/core/task-loader.ts:440-470`). The task note's configuration turns remote operations off.
- **Renovate delivers template releases, and auto-merges them:**
  - its Copier manager is on by default (`dist/modules/manager/copier/index.js:21-24`); it runs `copier update` against the new template tag and puts every changed file into the update pull request (`artifacts.js:11-30, 47-83` in Renovate 44.238.1), passing `--trust` (which lets Copier's tasks run) only when the self-hosted global `allowScripts` is set;
  - this repo's preset removes the release-age delay for Copier updates and sets `automerge: true` for all updates except LID minor and major bumps (`renovate/default.json:5-7, 24-35`), so a template release's pull request merges once checks pass, with no person involved (decision 8).
- **[Copier](https://github.com/copier-org/copier) can treat updates differently from fresh copies** (Copier 9.18.2, `copier/_main.py`):
  - `_exclude` patterns are rendered with `_copier_operation` set to `copy` or `update` (`:771-787`), so a template can leave a follow-up file out of fresh copies;
  - on update, a file the consumer moved or deleted isn't regenerated (`:1437-1477`);
  - a file a later template version drops is removed from consumers that still have it at its original path (the diff step read in outline only).
- **GitHub's issue dependencies cross repositories** (docs only):
  - `gh issue view` shows "Blocked by: octo-org/octo-repo#200", and the REST API takes an issue ID from any repo ([creating issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies));
  - the dependency endpoints filter their results by the token's scope, so a narrow token sees fewer blockers ([changelog, 2026-08-20](https://github.blog/changelog/2026-08-20-pin-projects-views-and-milestones-to-the-repository-sidebar/));
  - no page read says whether "Blocked" clears when a blocker closes, or whether links across owners work; a [community thread](https://github.com/orgs/community/discussions/148714) from early 2025, before dependencies shipped (snippet), reports cross-organization sub-issues refused and cross-organization blocked-by "on our roadmap";
  - sub-issues added through the REST API must share the parent's owner; issue fields such as Priority span one owner's repos; Copilot's changes to issue fields carry a rationale and confidence and can wait for a person to accept them.
- **Claude Code's cross-session messages** reach live sessions only and aren't stored as tasks (docs only).

### The custom pieces

Sizes are rough; each piece goes through LID.

1. **Piece G: incoming work (N1, C1, C5)** (small to medium). The sending side proposes a task file for the receiving repo as a pull request; nothing lands until a person in the receiving repo merges it.
   - **Reads:** the sending session's evidence. **Writes:** one task file in the receiving repo's backlog, by pull request. **Runs when:** an agent finds work that belongs elsewhere, or the developer files it.
   - **Today:** agents don't commit or open pull requests in this system, so the agent drafts the file and the pull request text and the developer opens it (decision 9). Following the 2026-11-06 note, any automated version works in a separate writable checkout or through the GitHub API, never in a reference clone (a read-only clone an agent keeps for reading another repo).
   - **What the file may carry:** provenance (requesting repo, who asked, the agent that filed it, a link to the evidence) and the request itself. The receiving repo sets priority, performer and any protected field. Piece C rejects an `onStatusChange` key; piece B flags a pin (piece J) or a `set_by: human` marker (piece B's record that a person set a field), and refuses them once agents commit with a trailer.
   - **Identity:** the file can't take an ID from the receiving repo's sequence without colliding, so how it is named and when it gets its ID is decision 2.
   - **Triage:** whether merging is the acceptance or the task waits in a triage state after merge is decision 1. Precedents: the CALO assistant checks a request against current commitments before accepting it and proposes fixes ([Myers et al. 2007](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/view/2039), paper-reported); Saffar's tool ([Saffar 2019](https://publications.polymtl.ca/3897/)) classifies an unexpected request and accepts it only if it serves the current objective.
   - **Session start:** the hook (piece E) adds a section for incoming work: open pull requests carrying the incoming label and accepted tasks not yet started. [td-fly](https://github.com/mergodon/td-fly)'s SessionStart hook prints a count of incoming issues from other repos (verified in source; no license, so only the idea is borrowed), and [hub](https://github.com/sawady/hub)'s hook prints open pull requests across repos. The hook's `gh` calls need a timeout.
   - **Automated sending, later:** [gh-aw](https://github.com/github/gh-aw)'s safe outputs are a model (verified in source at 8df5ea6): each cross-repo write runs in a separate job with an allowlist of target repos, a per-run maximum and a staged preview; pull requests default to draft, and auto-merge is off unless configured. Adopting gh-aw itself needs an AI engine for its workflows, which wasn't checked against H4.
   - **Between live sessions:** [crosstalk](https://github.com/davepoon/buildwithclaude) (its `plugins/crosstalk` skills, read in full at 3c9a725) treats a peer session's request as not the user's approval and replies DONE, BLOCKED or PROPOSAL with the files touched.
   - **The reverse direction:** feedback from a consumer to its template follows [cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) (verified in source at 6d92658): a Stop hook nudges only when the session shows friction with template-owned files, the issue is filed only after the developer confirms its exact text, and triage declines against a list of settled decisions. In this public repo, an issue from a private consumer must not name it.
2. **Piece H: blockers in other repos (N2, C2)** (medium). A custom key lists blockers outside the repo, each a task in another repo's backlog or a GitHub issue or pull request. Foreign IDs never go into Backlog.md's own `dependencies`.
   - **Reads:** each blocker's state from the other repo's default branch (its task file in `tasks/`, `completed/` or `archive/`, from a sibling checkout after a fetch or through the GitHub contents API), or a GitHub issue or pull request. **Writes:** nothing; it caches results with an age limit. **Runs when:** piece E's queue wrapper builds the ready list, including at session start. CI doesn't compute readiness.
   - **Fail closed:** an unreadable blocker, a stale cache past its limit, or an empty result from a token that may not see the other repo all count as open, as in [relevo](https://github.com/elalfner/relevo) (`Depends-on: owner/repo#N` with an allowlist) and [claude-zamu](https://github.com/dhh1128/claude-zamu), where a check that couldn't run never counts as done (verified in source at 6450e6f). gh-aw's work-queue specification states the same rule (a draft specification, docs only).
   - **Ideas to borrow:** claude-zamu's dependencies name a read-only check (an "oracle", such as a pull request in another repo or a command), and its external items record who is awaited and a date after which to chase them; [beads](https://github.com/gastownhall/beads) lets a blocker name a capability another repo provides (`external:<project>:<capability>`, satisfied by a closed issue labelled `provides:<capability>`; design document read in full), so the blocked task needn't know the other repo's task ID.
   - **A reverse index:** piece J's "how much does this unblock" needs the other direction (which tasks elsewhere name this one), so the resolver also scans the other repos' external-blocker keys, under the same read rules.
   - **Archived blockers:** like Backlog.md, which satisfies a dependency only in its final status wherever the file lives (`src/utils/readiness.ts:41`), the resolver counts a blocker as closed only when it is Done; an archived, unfinished blocker stays open and is flagged.
   - Piece F can mirror these as native blocked-by links (decision 7); readiness is computed from each blocker's own state, as [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit) does (`skills/work-plan/lib/github_state.py:268-276` at 39a6c7d), so whether GitHub's mark clears doesn't matter.
3. **Piece I: the cross-repo view (N3, C3)** (small to medium).
   - **Reads:** each repo's Backlog.md files, from a list of repos the developer keeps. **Writes:** a generated, read-only Markdown summary of each repo's ready, blocked and incoming tasks with the published ranking, kept locally. **Runs when:** on demand and before the weekly ranking session.
   - **Backlog Atlas** (optional; decision 3) is a desktop app (Tauri) with swimlanes across repos. It publishes Linux, macOS and Windows builds and runs its end-to-end tests on Ubuntu (`README.md:18, 64-65`, `.github/workflows/ci.yml:112-127` at 4264332). It reads the files directly and writes through the Backlog.md CLI with an allowlist of options, except milestone descriptions (written directly) and edits made in an external editor. A status change made in Atlas runs the target repo's `onStatusChange` callback, from the task or from that repo's config, through `sh -c` with no confirmation (Backlog.md `src/core/backlog.ts:2414-2443`, `src/utils/status-callback.ts:26-69`). Using it therefore needs piece C's rule extended to repo config: no `onStatusChange` anywhere.
   - [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub) also reads the files directly, but isn't read-only: its `/workspaces` route forwards any request, writes included, to each repo's `backlog browser`, with no switch to turn that off (`scripts/backlog-hub-server.js:1443-1459`). Its installer is macOS-only (launchd), and its worktree mode calls a `backlog workspace status` command that released Backlog.md doesn't have.
4. **Piece J: attributes, rules and a confirmed ranking (N3, N5, N5a)** (medium). The developer's six attributes become data, and the agent's role is defined.
   - **Reads:** the attributes in task frontmatter across repos (through piece I's list), piece H's reverse index, and a rules-and-weights file. **Writes:** proposed attribute values (agent-set, under piece B), a ranking, and the developer's pins and decisions. **Runs when:** a weekly session, and on demand. Where the rules, pins and ranking live is decision 5; how the ranking relates to Backlog.md's own `priority` and column order is decision 11.
   - **Attributes as custom keys**, one per N5a attribute: deadline; flexibility, as a deadline kind (hard, soft or target, after [htm](https://github.com/MilesCranmer/htm), whose hard, soft and none codes cap the planned hours per day differently; no license, so only the idea is borrowed); obligation (who is waiting and how much that matters); effort, as a coarse bucket rather than hours, from the durations of similar closed tasks where they exist; usefulness (value). How much a task unblocks, the sixth, is computed, not entered. One addition beyond N5a: a link to the current goal, which the Saffar thesis ranks against.
   - **Rules before a score** (decision 4): lexicographic tiers first (the developer's pins, then overdue or imminent hard deadlines), then a weighted score within a tier, as [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit)'s presets and [mouc](https://github.com/rnortman/mouc)'s strategies order work. Every score prints its terms, as [Taskwarrior](https://github.com/GothenburgBitFactory/taskwarrior)'s `task <id> information` prints attribute, value, coefficient and result per term (`src/commands/CmdInfo.cpp:405-470` at 401228f). Weights start from Taskwarrior's defaults (`src/Context.cpp:185-203`) and are the developer's to change. [launch-control](https://github.com/peter3605/launch-control)'s slack (time left after external lead times, arithmetic shown) is a candidate rule for deadline-driven items.
   - **Who does what:** agents propose attribute values and the ranking and explain each pick; the developer confirms the attributes that matter (which ones is decision 12), pins a short list and records each decision. [ai-cortex](https://github.com/nesnilnehc/ai-cortex)'s prioritize-backlog skill records a decision as final value, previous value, rationale and who decided; it doesn't protect a human decision (`skills/prioritize-backlog/SKILL.md:61-77` at 4bf7269), so piece B must cover these fields (decision 10). [lodestar](https://github.com/AustinGailey/lodestar)'s `next` offers only items a person has selected.
   - **Cadence:** the weekly session ends with the developer pinning the few tasks that matter most; in the "'Stick to' Three" study, a cap of three daily tasks raised completion slightly ([Meyer et al. 2025](https://doi.org/10.1145/3715336.3735792), paper-reported).
   - **What to avoid:** an LLM ranking a whole list directly. LLM pairwise judgments are non-transitive and sensitive to order ([Investigating Non-Transitivity in LLM-as-a-Judge](https://arxiv.org/abs/2502.14074), paper-reported), and no paper found evaluates LLM backlog ranking under human authority. Approval of agent output rose while reviewers' inline comments fell in one study ([Habituation at the Gate](https://arxiv.org/abs/2606.22721), paper-reported), consistent with declining scrutiny, so confirmation steps should be few and specific.
5. **Piece K: template and shared-config follow-ups (N4, C4)** (small to medium).
   - **Reads:** the template release, and each consumer's Copier answers file (`.copier-answers.<template>.yml`, holding the template commit) and follow-up task state, from a list of consumers kept privately (some consumers may be private, and this repo is public) or GitHub code search for answers files naming the template. **Writes:** a follow-up task file in each consumer, through Copier; a read-only status report. **Runs when:** a template release; the report on demand and in the weekly session.
   - **Delivery** (decision 6): the template adds the follow-up as a task file that `_exclude` leaves out of fresh copies, so it arrives only in each consumer's Renovate update pull request. A consumer that moves the file once the work is done won't get it back; the template must keep the file until every consumer has moved it (done) or recorded it as diverged, since dropping it removes it from any consumer that still has it at its original path. Whether these pull requests auto-merge is decision 8.
   - **Identity:** a template-delivered task file can't take an ID from each consumer's sequence either, so decision 2 covers it too. Releases of this repo's Renovate presets and reusable workflows arrive as version bumps with no Copier step, so they need the fallback: a release step that opens one pull request per consumer adding the task file, on the gh-aw safe-output model.
   - **Richer update pull requests:** [markdown-vault-mcp](https://github.com/pvliesdonk/markdown-vault-mcp) and its template, [fastmcp-server-template](https://github.com/pvliesdonk/fastmcp-server-template), put the template's upgrade notes and generated drift reports in the update pull request; a skill (verified in source at fe71d07) works through them, giving each drifted file either a conformed outcome or a tracked issue. The template's workflow that builds the pull request was seen only as a snippet.
   - **Status report:** borrows [ziku](https://github.com/tktcorporation/ziku)'s template-side inventory (it reads consumers' lock files and writes nothing) and the per-consumer ledger in [osdu-spi](https://github.com/Azure/osdu-spi)'s fleet rollout, without its merge step, which breaks H5. Each consumer's state includes "diverged on purpose" beside "not yet done" ([Ajibode et al. 2026](https://arxiv.org/abs/2508.10157), paper-reported).
   - **Shared files copied between repos:** [basecradle-harness](https://github.com/basecradle/basecradle-harness)'s conventions file one re-sync handoff per repo that carries a copy, in the same change, and a scheduled check compares the copies and files a drift issue when they differ.

### Open decisions for the developer

| # | Decision | Recommendation | Alternative |
|---|---|---|---|
| 1 | Whether merging an incoming task is its acceptance | Merging is acceptance: the receiving side triages on the pull request and declines by closing it, so there is one human gate | Merge into a triage state, then accept or decline separately (two gates) |
| 2 | How an incoming, template-delivered or blocking task is named across repos | The sender names the file by a slug; the receiving repo assigns its own ID on merge, and external blockers refer to the task by repo and slug or by a capability | A namespaced ID prefix per sending repo, allocated by the sender |
| 3 | The cross-repo view | A generated read-only summary first; [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas) on trial once no repo has an `onStatusChange` key | [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub) patched to drop its write proxy (macOS service only) |
| 4 | How the ranking is computed | Tiers, then a weighted score with a per-term breakdown, over attributes agents propose | Agent-proposed pairwise or LLM ranking with the developer confirming |
| 5 | Where rules, pins and the weekly ranking live | A private coordination repo (some repos and tasks may be private, and this repo is public) whose files every repo's hook reads from a current local checkout, so H2 holds | A ranking file in each repo by pull request each week (five pull requests a week) |
| 6 | How a template release creates follow-ups | A task file in the template, excluded from fresh copies, carried by each consumer's update pull request | A release job that opens a separate pull request per consumer |
| 7 | Whether to use GitHub's native [blocked-by](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies) and issue fields | Mirror them in the push-only sync (piece F), but compute readiness from files | Use them as the source of truth for cross-repo state |
| 8 | Whether Copier update pull requests auto-merge | Turn auto-merge off for the Copier manager, so a person merges each template update and its follow-ups | Keep auto-merge and rely on CI, including a test that custom task keys survive Backlog.md |
| 9 | How cross-repo pull requests are opened while the developer makes every commit | The agent drafts the task file and pull request text; the developer opens it | An agent opens it through the GitHub API, under an allowlist, once agents may commit |
| 10 | Which of piece J's fields piece B protects | Pins, the developer's decisions and the rules-and-weights file | Also every attribute the developer confirmed |
| 11 | How the ranking relates to Backlog.md's `priority` and column order | The ranking is a separate order the queue wrapper uses; it never writes Backlog.md's fields | Write the ranking back into `priority` and order |
| 12 | Which agent-proposed attributes need the developer's confirmation | Deadline kind and obligation; effort and value rank unconfirmed, marked agent-set | Confirm every attribute before it counts |

## Candidates and matrix

**Ranked shortlist** (building blocks for the blend; no candidate is a whole answer):

1. [Backlog.md](https://github.com/MrLesk/Backlog.md) (already chosen) and [Renovate](https://github.com/renovatebot/renovate)'s Copier manager (already in the stack): they cover storage, custom keys and template delivery. Would change if Backlog.md stopped preserving unknown keys.
2. [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas): the only cross-repo view that reads per-repo Backlog.md files and writes almost only through its CLI. Would drop if the callback risk can't be contained.
3. [gh-aw](https://github.com/github/gh-aw): the most careful cross-repo write design found. Would move up if its engine requirement fits H4.
4. [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit): computes cross-repo blockers from each blocker's state and ranks by lexicographic presets with a human override; fails H6.
5. [onetaskgraph](https://github.com/nickderobertis/onetaskgraph): federates task sources without a central store; would move up if it gained readiness and a Backlog.md reader.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | adopt (already chosen) | MIT (`LICENSE:1-21` at 52b4ea3) | Per-repo store; keeps custom keys; local IDs |
| [Renovate](https://github.com/renovatebot/renovate) Copier manager | adopt (already in the stack) | AGPL-3.0-only (`license:1-661` in 44.238.1; used as an installed tool) | Delivers template releases as consumer pull requests; the preset auto-merges them |
| [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas) | build on (optional, on trial) | MIT (`LICENSE:1-21` at 4264332) | Cross-repo view over Backlog.md files; status edits fire callbacks |
| [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub) | borrow ideas | MIT (`LICENSE:1-21` at ee35410) | Cross-repo view; forwards writes; macOS-only installer |
| [gh-aw](https://github.com/github/gh-aw) | borrow ideas | MIT (`LICENSE:1-21` at 8df5ea6) | Safe cross-repo writes; work queue is a draft specification; engine requirement unchecked |
| [onetaskgraph](https://github.com/nickderobertis/onetaskgraph) | borrow ideas | MIT (`LICENSE:1-21` at de029a4) | Federated sources and cross-source edges; no readiness; own Markdown keys |
| [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit) | borrow ideas | MIT (`LICENSE:1-21` at 39a6c7d) | Cross-repo blockers from blocker state; lexicographic presets; GitHub Issues as source |
| [relevo](https://github.com/elalfner/relevo) | borrow ideas | MIT (`LICENSE:1-21` at af19d1d; its brand files are excluded from the grant) | `Depends-on: owner/repo#N`, fail closed; GitHub Issues as backlog |
| [claude-zamu](https://github.com/dhh1128/claude-zamu) | borrow ideas | Apache-2.0 (read whole at 6450e6f) | Readiness from read-only checks across repos; state in the home directory |
| [beads](https://github.com/gastownhall/beads) | borrow ideas | MIT (`LICENSE:1-21` at 8cdfa79) | Capability-based external dependencies; Dolt store fails H2 |
| [work-ledger](https://github.com/NelsonBrandao/work-ledger) | borrow ideas | Apache-2.0 (`LICENSE:1-202` at c2d605f) | Cross-repo `blocked_by` in one Markdown ledger outside the repos |
| [gbd](https://github.com/aigency/gbd) | borrow ideas | MIT (`LICENSE:1-21` at 84d8f48) | Readiness from GitHub's open-blocker count; clearing on close untested |
| [hubd](https://github.com/bzdOS/hubd) | borrow ideas | MIT (read whole at 0d6fd71) | Hub-wide dependencies; one pick with a reason; separate store |
| [hub](https://github.com/sawady/hub) | borrow ideas | unverified (MIT by API pointer only) | SessionStart hook listing open pull requests and blocked items across repos |
| [crosstalk](https://github.com/davepoon/buildwithclaude) (in buildwithclaude) | borrow ideas | unverified (MIT by API pointer only) | Peer-session requests need the user's approval; DONE, BLOCKED or PROPOSAL replies |
| [td-fly](https://github.com/mergodon/td-fly) | borrow ideas (no license) | none (tree listing at a0f70b1) | Incoming issues with a provenance marker; session-start count |
| [cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) | borrow ideas | Apache-2.0 (`LICENSE`, 201 lines, head and tail read, at 6d92658) | Consumer-to-template feedback on evidence, confirmed text, settled-decision list |
| [zps-pareto](https://github.com/zebrapuma/zps-pareto-github-issues) | borrow ideas | MIT (read whole at 3a24aef) | One threshold across repos; score as an attributable comment after confirmation |
| [backlog-sync](https://github.com/djensenius/backlog-sync) | borrow ideas | Apache-2.0 (read whole at 9940a88) | Push-only Backlog.md mirror to Issues and a Project, routed to several repos; input for piece F |
| [ziku](https://github.com/tktcorporation/ziku) | borrow ideas | MIT (`LICENSE:1-21` at bff3e13) | Template-side, read-only inventory of consumer drift |
| [markdown-vault-mcp](https://github.com/pvliesdonk/markdown-vault-mcp) | borrow ideas | MIT (read whole at fe71d07) | Upgrade notes and drift reports in the update pull request; a tracked issue per drifted file |
| [osdu-spi](https://github.com/Azure/osdu-spi) fleet rollout | borrow ideas | Apache-2.0 (`LICENSE:1-200` at d3ddff5) | Per-consumer sync record and rollout ledger; merge step breaks H5 |
| [basecradle-harness](https://github.com/basecradle/basecradle-harness) | borrow ideas | MIT (read whole at f007264) | Re-sync handoff per copy of a shared file; drift checks (services not in the repo) |
| [copierz](https://pypi.org/project/copierz/) | borrow ideas | Apache-2.0 (sdist `LICENSE`, read whole, 0.1.0) | Lists Copier consumers behind their template; no tasks |
| [rollout-cli](https://pypi.org/project/rollout-cli/) | borrow ideas | Apache-2.0 (sdist `LICENSE`, read whole, 0.9.1; source repository gone) | One pull request per repo, classified clean, done or needs attention; never merges |
| [multi-gitter](https://github.com/lindell/multi-gitter) | borrow ideas | Apache-2.0 (read whole at 05a37f6) | Fan-out pull requests for piece K's fallback |
| [Taskwarrior](https://github.com/GothenburgBitFactory/taskwarrior) | borrow ideas | MIT (`LICENSE:1-23` at 401228f) | Linear urgency with a per-term breakdown; SQLite store |
| [taskpeasant](https://github.com/alexgc96/taskpeasant) | borrow ideas | GPL-3.0-or-later (sdist `LICENSE`, read whole, 0.5.0) | Taskwarrior's urgency formula in plain YAML |
| [markdown-task-butler](https://github.com/dobachi/task-butler) | borrow ideas | unverified (MIT in package metadata only) | Markdown tasks; weighted deadline, dependency and effort score with a reason per pick |
| [ai-cortex](https://github.com/nesnilnehc/ai-cortex) prioritize-backlog | borrow ideas | MIT (`LICENSE:1-21` at 4bf7269) | Decision record per task; no lock on human decisions |
| [lodestar](https://github.com/AustinGailey/lodestar) | borrow ideas | MIT (read whole at 1cac359) | Per-score rationale; `next` offers only human-selected items; own schema |
| [mouc](https://github.com/rnortman/mouc) | borrow ideas | MIT (`LICENSE:1-9` at f8d8fb8) | Backward deadline pass and scheduling strategies; no hard/soft distinction |
| [bones](https://github.com/bobisme/bones) triage | borrow ideas | MIT (read whole at 86de2f8) | Unblocking value from the graph; an Urgent or Punt flag bypasses the score, but any actor can set it |
| [launch-control](https://github.com/peter3605/launch-control) | borrow ideas | MIT (read whole at 5420519) | Slack from external lead times, arithmetic shown; board in Notion (H2, H4) |
| [lark-cowork-plugins](https://github.com/larkcowork/lark-cowork-plugins) task-prioritizer | borrow ideas | unverified (Apache-2.0 text plus 29 words at `LICENSE:201-212` that grant and restrict nothing but aren't standard, at 7140574) | Hard deadlines weighted double, assigner tier, people waiting, a reason per pick; needs Lark |
| [pma](https://github.com/shakfu/pma) | borrow ideas | MIT (read whole at 5df1d10) | Human tiers across repos; "waits on you"; state in SQLite |
| [wellmanifest/priority](https://github.com/wellmanifest/priority) | borrow ideas | Apache-2.0 (read whole at aeaaea2) | Propose-only priorities with receipts and a drift check |
| [Cora](https://github.com/pivy-off/cora) | borrow ideas (no license) | all rights reserved (`README.md:172-174` at 5632a06) | Soft target and hard deadline, stakes, relational weight, a focus pin (design document not read whole) |
| [htm](https://github.com/MilesCranmer/htm) | borrow ideas (no license) | none (b692a69) | Deadline hardness codes that cap planned hours per day |
| [llmsort](https://github.com/XyraSinclair/llmsort) | reject | MIT (read whole at 43928fe) | Pairwise LLM ranking needs a hosted model service (H4; docs) |
| [mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail) | reject | MIT plus a rider granting no rights to Anthropic, OpenAI or their agents (read whole at 9138f34) | Fails H1 |
| [chant](https://github.com/lex00/chant) | reject | unverified (repository and crate removed) | Cross-repo `depends_on` seen only in snippets; no longer published |

No candidate flagged as a possible copy remains: the one copy found was rejected in favour of its original.

**Hosted and self-hosted trackers** (docs only): [Linear](https://linear.app/docs/triage-intelligence) (triage suggestions with reasons; hosted, H4), [Jira Plans](https://www.atlassian.com/software/jira/guides/advanced-roadmaps/overview) (cross-project ranking; hosted, H4), [GitLab](https://docs.gitlab.com/user/project/issues/related_issues/) (cross-project blocking links that clear when the blocker closes; another forge), [Forgejo](https://forgejo.org/docs/latest/admin/config-cheat-sheet/) (cross-repository dependencies on by default; would replace GitHub), [Zenhub](https://support.zenhub.com/article/how-do-i-create-issue-dependencies) (cross-repo dependencies within a workspace that update when a blocker closes; hosted, H4), [Sourcegraph Batch Changes](https://sourcegraph.com/docs/batch-changes/tracking-existing-changesets.md) (per-repository change tracking; needs an instance, H4), and the [Copier Update](https://updates.python-templates.dev/) app (a hosted GitHub App, H4; duplicates Renovate). Each was rejected on the criterion named; GitLab's and Zenhub's clearing on close is the behaviour piece H computes itself.

**Matrix** (values: native, partial, extensible, unsupported, unverified; "unverified" also covers a need for which the files read showed no mechanism and no listing was made; sources are path:line at the commits above, or "docs"):

| Criterion | [Backlog.md](https://github.com/MrLesk/Backlog.md) + [Renovate](https://github.com/renovatebot/renovate) | [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas) | [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub) | [gh-aw](https://github.com/github/gh-aw) | [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit) | [onetaskgraph](https://github.com/nickderobertis/onetaskgraph) | [relevo](https://github.com/elalfner/relevo) |
|---|---|---|---|---|---|---|---|
| H1 license | native (MIT; AGPL-3.0 for Renovate as a tool) | native | native | native | native | native | native |
| H2 files | native (`frontmatter.ts:57-194`) | native (reads the files directly; its decision record 2) | native (`backlog-hub-server.js:766-788`) | partial (queue on a branch, docs) | partial (tracks outside the repo; issues on GitHub, `README.md:21,127`) | native (no cache, `README.md:22-34`) | unsupported (GitHub Issues as backlog, docs) |
| H3 human authority | extensible (piece B) | partial (CLI allowlist; callbacks fire) | partial (proxy forwards writes, `:1443-1459`) | partial (draft pull requests, staged previews) | partial (`--set-next`; confirm token) | partial (version guards the caller must pass) | unverified |
| H4 hosted | native | native | native | unverified (AI engine) | native | native | native |
| H5 merge | partial (preset auto-merges, `default.json:5-7`) | native (git read-only) | native (`rev-parse` only) | native (auto-merge opt-in) | native (no auto-push, `README.md:149,167`) | native (its Markdown source starts no subprocess, `crates/onetaskgraph-local-md/src/lib.rs`) | native (docs) |
| H6 Backlog.md | native | native | native (worktree mode partial) | extensible (can deliver task files) | unsupported (replaces) | extensible (key aliases or a plugin source) | unsupported (replaces) |
| N1 filing | extensible (piece G) | unverified | unverified | native (`create_issue.cjs:510-570`) | unverified | native (`routes`, `README.md:2784-2872`) | unverified |
| N2 blockers | partial (fails closed on foreign IDs, `readiness.ts:74-105`) | unsupported (`detail.ts:93-111`) | unsupported (no `dependencies` key, `:28`) | partial (draft specification, docs) | native (`github_state.py:268-276`) | partial (edges recorded, never followed) | native (fail closed, docs) |
| N3 view and ranking | unverified | partial (view only) | partial (view only) | unverified | native (presets, `next_up.py:119-187`) | unverified | unverified |
| N4 follow-ups | partial (delivers files; no status) | unverified | unverified | partial (example fan-out workflows, docs) | unverified | unverified | unverified |
| N5/N5a ranking | unverified (custom piece J) | unverified | unverified | unverified | partial (no explanations, no deadline kinds) | unverified | unverified |

**Blends considered.** Backlog.md plus a central ledger such as work-ledger was rejected: it would split each task's state between the repo and the home directory. Backlog.md plus GitHub Issues as the cross-repo layer (gbd, relevo, work-plan) was rejected as the source of truth because it leaves cross-repo state outside the files agents read (H2); it stays as the push target (piece F, decision 7). Backlog.md plus onetaskgraph as the federation layer would need a Backlog.md reader and a readiness verb, both additions to a single-maintainer Rust tool; it stays an option if piece H grows. The chosen blend keeps every task in its own repo and adds only resolvers, a hook section, a view and a ranking that read those files.

### Scenario walk

Common uses first, through the blend (pending the open decisions):

- **C1, a bug in A that belongs to B.** A's agent drafts a task file with provenance keys; the pull request into B is opened by the developer today (decision 9). B's next session lists it under incoming work. Merging it is the acceptance (decision 1); closing it declines. B assigns its own ID on merge (decision 2); piece C rejects a callback in the file, and piece B flags any protected field.
- **C2, A waits on B.** A's task lists B's task (by repo and slug) in its external-blocker key. When A's queue wrapper builds the ready list, the resolver reads B's default branch and leaves A's task out, naming the blocker. When B's task reaches Done (wherever its file lives), the next read lists A's task as ready; an archived, unfinished task stays a blocker. If B can't be read, or the cache is too old, A's task stays blocked.
- **C3, the weekly ranking across five repos.** The developer opens the generated summary (piece I). The agent proposes an order across the five repos from the attributes and rules, showing each pick's terms, and asks the developer to confirm deadline kinds and obligations it proposed (decision 12). The developer pins a few tasks; the pins and the ranking are written where decision 5 puts them, and piece B protects them (decision 10). Each repo's hook shows the pins first.
- **C4, a copier-python release needing follow-up everywhere.** The release adds a task file that fresh copies exclude. Each consumer's Renovate update pull request carries it with the upgrade notes; with auto-merge off for Copier (decision 8), a person merges it. The status report lists each consumer's template version and whether the follow-up is done, not done or diverged on purpose.
- **C5, a session in B starts.** The hook prints in-progress work, then B's pinned tasks, then open incoming pull requests and accepted incoming tasks, then the rest of the ready queue in the published order, within its time budget.

Change scenarios:

- **A new attribute** (say "affects a collaborator"): add a custom key and a rule or weight; Backlog.md keeps the key, and the breakdown shows its term.
- **A one-off override:** the developer pins a task; piece B flags an agent change to the pin today and refuses it once agents commit with a trailer.
- **A fresh CI clone:** sibling checkouts are absent and CI doesn't compute readiness, so nothing reports a task ready by mistake.
- **An automated upgrade pull request for Backlog.md itself:** custom keys survive as long as Backlog.md keeps preserving unknown frontmatter. Since the preset auto-merges updates, a CI test that a task with nested custom keys round-trips through Backlog.md's CLI belongs in every repo that uses pieces G, H or J.

## Limitations checked in source

Verified (full reads at the commits named):

- [Backlog.md](https://github.com/MrLesk/Backlog.md): unknown-key preservation, foreign-dependency rejection, fail-closed readiness, new IDs on draft promotion, the `project` field, cross-branch loading, the `onStatusChange` path; MIT.
- [Renovate](https://github.com/renovatebot/renovate) 44.238.1: the Copier manager's command, `--trust` condition and pull request contents; AGPL-3.0-only. This repo's preset: auto-merge and the Copier rule.
- [Copier](https://github.com/copier-org/copier) 9.18.2: `_copier_operation` in `_exclude` rendering; moved or deleted files not regenerated on update (the deletion of dropped files read in outline).
- [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub), [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas), [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit), [ai-cortex](https://github.com/nesnilnehc/ai-cortex), [Taskwarrior](https://github.com/GothenburgBitFactory/taskwarrior), [mouc](https://github.com/rnortman/mouc), [onetaskgraph](https://github.com/nickderobertis/onetaskgraph), [claude-zamu](https://github.com/dhh1128/claude-zamu), [gbd](https://github.com/aigency/gbd), [ziku](https://github.com/tktcorporation/ziku), [work-ledger](https://github.com/NelsonBrandao/work-ledger), [htm](https://github.com/MilesCranmer/htm), [osdu-spi](https://github.com/Azure/osdu-spi), [lodestar](https://github.com/AustinGailey/lodestar), [pma](https://github.com/shakfu/pma), [cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template), [markdown-vault-mcp](https://github.com/pvliesdonk/markdown-vault-mcp), the lark-cowork task-prioritizer and [gh-aw](https://github.com/github/gh-aw)'s safe outputs: the mechanisms named in the pieces and table.
- Licenses read whole for every candidate in the table, except where the table says otherwise.

Docs only: [relevo](https://github.com/elalfner/relevo)'s fail-closed rule (an archived design change), [beads](https://github.com/gastownhall/beads)' external dependencies (a design document), gh-aw's work queue (a draft specification), [llmsort](https://github.com/XyraSinclair/llmsort)'s hosted model requirement, and every GitHub, GitLab, Forgejo, Zenhub, Linear and Sourcegraph behaviour named.

Could not verify:

- Whether GitHub clears an issue's "Blocked" mark when a blocker in another repo closes, and whether blocked-by links work across owners (docs silent; a community thread reports cross-organization links refused). One skill's instructions ([claude-plugins](https://github.com/laurigates/claude-plugins)' git-issue-hierarchy) say dependency links must stay within one repo, which conflicts with GitHub's own example; nothing was tested. Readiness computed from each blocker's state avoids depending on either.
- Which AI engine gh-aw's workflows need, and so its H4 status.
- The lark-cowork license's added text, and markdown-task-butler's license (no license file in its package).
- Cora's full design document; chant's mechanism (the project is gone).
- Codeberg: it blocks scripted clients, and the web search tool ignored both `site:codeberg.org` and "codeberg" as a word, so its projects were barely reached.

## Papers

Claims are paper-reported. "Setting" says how close the paper's situation is to a developer ranking work for coding agents across repos. This note uses data from Semantic Scholar.

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag); setting |
|---|---|---|---|---|---|
| [What a To-Do](https://doi.org/10.1145/985692.985785) (Bellotti et al. 2004) | read in full (supplied) | qualitative study | peer-reviewed | borrow ideas | Tasks got done more when someone expected them (77% vs 53%), others were involved, or they were non-discretionary; having a deadline wasn't significant; time estimates were unreliable; users wouldn't enter metadata (paper-reported). Partial: individuals, not agents |
| [Towards Intelligent Assistance for To-Do Lists](https://doi.org/10.1145/1378773.1378822) (Gil and Ratnakar 2008) | read in full (supplied) | observational study | peer-reviewed | borrow ideas | In a 300-entry sample of 1,200 to-do entries, 86% were reminders, and no actionable entry could be interpreted without the user's context (paper-reported). Partial: agents inferring attributes need context |
| [An Intelligent Personal Assistant for Task and Time Management](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/view/2039) (Myers et al. 2007) | read in full (supplied) | untested proposal | peer-reviewed | borrow ideas | Delegation within the user's advice ("consult me when…"), explanations with provenance, feasibility checks before accepting a request, stated preferences before learned ones (paper-reported). Partial |
| [Understanding, Defining and Managing of Operational Personal Priorities](https://publications.polymtl.ca/3897/) (Saffar 2019) | read in part (abstract, §2.2, §3.1.2-3.4, ch. 4; supplied) | weak experiment | thesis | borrow ideas | Prioritization criteria include social and requirement factors; unexpected requests are classified and accepted only if they serve the current objective (paper-reported). Weak setting |
| [Designing for Advanced Personalization in Personal Task Management](https://doi.org/10.1145/2901790.2901805) (Haraty and McGrenere 2016) | read in full (supplied) | weak experiment | peer-reviewed | borrow ideas | Users built their own task rules from building blocks in 142 of 144 trials, but a third of the rules weren't the intended ones (paper-reported). Supports rules the developer owns, previewed before use |
| ['Stick to' Three](https://doi.org/10.1145/3715336.3735792) (Meyer et al. 2025) | read in full (supplied) | weak experiment | peer-reviewed | borrow ideas | Committing to at most three tasks a day, always visible, raised completion from 1.17 to 1.49 a day (small effect) (paper-reported). Partial: supports a small pinned focus set |
| [Bridging the Gap Between Time Management Research and Task Management App Design](https://doi.org/10.1145/3663384.3663404) (Ahmetoglu et al. 2024) | read in full (supplied) | untested proposal | peer-reviewed | borrow ideas | Durations of similar past tasks, breakdown that surfaces hidden steps, and neutral wording reduce underestimates; no reviewed app supported the durations of similar tasks or neutral wording, while 77% offered subtasks (paper-reported). Partial: effort attribute |
| [Factors affecting individual task prioritisation in a workplace setting](https://pmc.ncbi.nlm.nih.gov/articles/PMC6502562/) (2018) | read in full | observational study | peer-reviewed | borrow ideas | A review of 20 papers: length, urgency, importance, reward and the task's source drive prioritization, which is personal (paper-reported). Partial |
| [AI-Powered Reminders for Collaborative Tasks](https://arxiv.org/abs/2403.01365) (CSCW 2024) | read in part (abstract, §1-2, results, discussion) | qualitative study | peer-reviewed | borrow ideas | Commitments and requests to others as the extracted signal; reminders of forgotten low-importance tasks valued (paper-reported). Partial: obligation |
| [Tools of Task Management: SLR and Online Survey](https://ojs.lib.unideb.hu/IJEMS/article/download/17379/15356) (2026) | read in part (abstract, §1-2, survey results, discussion) | observational study | peer-reviewed | borrow ideas | Users want prioritization support but keep control of selection (paper-reported). Partial |
| [Improved Management of Issue Dependencies in Issue Trackers](https://arxiv.org/abs/2102.08485) | read in part (abstract, Table 3, consistency checks, evaluation) | weak experiment | peer-reviewed | borrow ideas | Proposes missing dependencies and flags priority conflicts with dependencies; 4,383 cross-project dependency endpoints in one Jira (paper-reported). Partial: N2 |
| [Choosing a Suitable Requirement Prioritization Method](https://arxiv.org/abs/2402.13149) | read in part (abstract, §1-3, §5.2, tables) | observational study | preprint | borrow ideas | The analytic hierarchy process (AHP, pairwise comparison) is the most reliable and costliest, n(n-1)/2 comparisons; grouping methods are fast but unordered (paper-reported). Partial |
| [Not all requirements prioritization criteria are equal at all times](https://arxiv.org/abs/2104.06033) | read in part (abstract, §1-3) | observational study | preprint | borrow ideas | In 32,139 decisions, the criteria that drove priority changed by stage (paper-reported). Partial |
| [Integrating AHP with LLMs for Transparent MCDM](https://arxiv.org/abs/2609.16779) | read in part (abstract, §1-2, §5-7) | weak experiment | preprint | borrow ideas | LLM agents generate criteria and weights with auditable steps (paper-reported). Partial |
| [A Multi-agent LLM System for Requirements Analysis](https://trepo.tuni.fi/handle/10024/240325) | read in full | weak experiment | peer-reviewed | borrow ideas | Role agents score with justifications; run-to-run rank distance 0.25-0.67 (paper-reported). Partial: LLM ranking is unstable |
| [Investigating Non-Transitivity in LLM-as-a-Judge](https://arxiv.org/abs/2502.14074) | read in part (non-transitivity sections, §5) | experiment | preprint | borrow ideas | LLM pairwise judgments are non-transitive; round-robin plus Bradley-Terry ranks more reliably (paper-reported). Method only |
| [Habituation at the Gate](https://arxiv.org/abs/2606.22721) | read in part (abstract, limitations) | observational study | preprint | borrow ideas | Approval of agent code rose and inline comments fell 22%; rational trust can't be ruled out (paper-reported). Risk for any confirmation step |
| [Collaborative Human-Agent Protocol (CHAP)](https://arxiv.org/abs/2606.09751) | read in part (§1-2, §6.3, §7.4, §10.1, App. D.1) | untested proposal | preprint | borrow ideas | An override records the base, the diff, the rationale and whether intent was preserved (paper-reported). Partial: H3 |
| [Loop Engineering](https://zenodo.org/records/21504929) | read in part (abstract, §1-3.5) | qualitative study | unreviewed report | borrow ideas | An approval is bound to an exact commit and lapses when the head changes (paper-reported). Partial: H3 |
| [Closed-Loop Autonomous Software Development via Jira-Integrated Backlog Orchestration](https://arxiv.org/abs/2604.05000) | read in part (abstract, §3.1, human gate, limitations) | qualitative study | preprint | borrow ideas | Local canonical backlog, priority-scored fix queue, human approval below a confidence threshold; cross-repo federation named as future work (paper-reported). One repo |
| [HULA](https://arxiv.org/abs/2411.12924) | read in part (abstract, research questions, stages) | observational study | peer-reviewed | borrow ideas | People approved 82% of agent plans; 59% of resulting pull requests merged (paper-reported). Partial: plan gate |
| [GitHub Template Repositories](https://arxiv.org/abs/2606.14616) | read in part (abstract, §VI) | observational study | peer-reviewed | borrow ideas | Repos created from templates aren't synchronized, so later fixes don't propagate (paper-reported). Problem evidence for N4 |
| [File-Level Copying Is an Implicit Dependency](https://arxiv.org/abs/2607.02059) | read in part (abstract, §I, §III start) | observational study | preprint | borrow ideas | Copied scaffolding and configuration lose update signals (paper-reported). Problem evidence for N4 |
| [On the synchronization between Hugging Face pre-trained language models and their upstream GitHub repository](https://arxiv.org/abs/2508.10157) (Ajibode et al., Empirical Software Engineering 2026) | read in part (abstract, §5.2) | observational study | peer-reviewed | borrow ideas | Separates intended divergence from neglected drift; critical upstream commits were never propagated (paper-reported). Partial: piece K's status states |
| [WideSWE](https://arxiv.org/abs/2609.33382) and [CrossSWE](https://arxiv.org/abs/2611.01484) | read in part (abstracts, joint vs independent execution, results headings) | experiment | preprint | borrow ideas | Agents fail many cross-repo tasks (WideSWE success 11-43%; CrossSWE best 58%); cross-repo inconsistency is 44% of CrossSWE's failures (paper-reported). Favours one task per repo with an explicit contract |

About 85 further papers were seen and not tabled: requirements-prioritization surveys and tools, LLM decision-support position papers, agent coordination benchmarks, issue-link prediction and oversight studies. They point the same way: people prioritize on personal, changing criteria; LLM rankings are unstable; a confirmation step needs protection against rubber-stamping. **No paper found studies an LLM or agent ranking a backlog under human authority, and none studies assigning tasks across repositories.**

## Worth retrieving manually

- [What Did I Ask You to Do, by When, and for Whom?](https://doi.org/10.1145/2998181.2998251) (DOI 10.1145/2998181.2998251). The abstract treats requests to and from others, with accountability, as part of a task's priority: the closest study of the obligation attribute, which bears on decision 12. Closed access; try an author's page or an author request first, then the ACM page or a library.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Backlog.md source at 52b4ea3; Renovate 44.238.1's Copier manager and license; `renovate/default.json`; Copier 9.18.2's update code; GitHub's docs and changelog on sub-issues, issue dependencies, issue fields, Projects, Copilot approvals and `repository_dispatch`; Claude Code's cross-session messaging and agent-teams docs |
| Earlier notes and decisions | searched | The 2026-11-06, 2026-11-12 and 2026-11-13 notes and the search handoff; the task-management search's candidates used as a known list |
| GitHub repository search | searched | About 400 searches (about 250 distinct wordings) over seven rounds, mostly two-word, both sorts in round 1, for the N5a vocabulary and for new topics, e.g. "cross-repo tasks", "copier update", "pairwise prioritization", "task prioritization" |
| GitHub topics | searched | About 40 topic lookups and 80 topic searches, e.g. topic:cross-repository, topic:multi-repo-orchestration, topic:task-prioritization, topic:backlog-prioritization, topic:gtd-workflow |
| GitHub code search | searched | About 145 queries on field names, `SKILL.md` descriptions and `marketplace.json` files, e.g. `"blocked_by:" "owner/repo#"`, `deadline_type: hard`, `.template-sync-commit`, `template-feedback`; two failed with HTTP 503 and one with 422 |
| GitLab search | searched | About 50 project searches; mostly mirrors and test fixtures |
| Codeberg search | excluded | Blocks scripted clients; General web search substituted with `site:codeberg.org` and "codeberg" as a word (13 queries), but the search tool ignored both, so few Codeberg projects surfaced (forj, tsk, taskfinder) |
| npm | searched | About 90 searches, mostly with the `keywords:` qualifier, plus package documents and tarballs |
| PyPI | searched | Through libraries.io and about 60 JSON lookups of known names; the search page was never requested |
| crates.io | searched | About 45 keyword searches plus crate downloads (onetaskgraph, llmsorting, pma, cohors, gbd, bones-triage, dstack); chant-cli is gone (404) |
| Language registries | searched | pkg.go.dev (about 30 searches; module zips through the Go proxy) and RubyGems (about 15 searches, nothing relevant) |
| libraries.io | searched | About 170 requests across PyPI, npm, Cargo and Go, sorted by latest release; two 502s not retried |
| Homebrew formulae | searched | The formula list grepped in each round for task, backlog, multi-repo, prioritization and Taskwarrior terms |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | Alternatives pages for Backlog.md, beads, multi-gitter, microplane and Taskwarrior; no pages exist for claude-zamu, ziku or Backlog Atlas, and lodestar's name belongs to another project |
| AUR | searched | About 25 phrase searches; only known tools |
| ecosyste.ms | searched | About 70 exact-keyword lookups (cross-repo, multi-repo, template-sync, prioritization) and dependents of copier |
| Cross-language equivalents | searched | Taskwarrior urgency ports; "alternatives to" lodestar, work-plan, ziku, hubd, gbd, claude-zamu and Backlog Atlas |
| Awesome lists | searched | Agent-orchestrator, Claude Code, productivity, plain-text and Taskwarrior lists, on GitHub and the web |
| alternativeto.net | excluded | Cloudflare challenge; "alternatives to" web searches substituted |
| General web search | searched | About 110 queries (about 75 recorded with their wording), e.g. "coordinate coding agents across multiple repositories", "hard deadline soft deadline personal task manager", "Backstage scorecard track migration adoption" |
| Hosted services | searched | The trackers and services listed under "Hosted and self-hosted trackers", plus Todoist, Things, OmniFocus, TickTick, Motion, Reclaim, Amplenote, Microsoft Viva commitments and Cortex initiatives (vendor docs; limitations docs only; Linear's pages couldn't be read verbatim) |
| Skill directories | searched | skills.sh, about 70 searches over seven rounds; its results carry no descriptions or repository paths, so hits were resolved through repository trees from round 6 |
| Claude Code plugin marketplaces | searched | Anthropic's marketplace file (317 plugins) grepped each round; community `marketplace.json` files found through code search (21 read) and Anthropic's knowledge-work-plugins listed |
| MCP Registry | searched | About 55 one-word queries; name matching only, mostly noise |
| PulseMCP | searched | Its sitemap (allowed by its robots.txt) grepped; a few allowed server pages read |
| Anthropic's skills repo | searched | Listing of `skills/`; nothing relevant |
| Awesome lists for agent skills | searched | Through GitHub code search and web search |
| GitHub topics for agent skills | searched | topic:agent-skills, claude-skills, claude-code-plugin and mcp-server with cross-repo and prioritization terms |
| aitoolnet.com | searched | Sitemap grepped for prioritization, backlog, rollout and triage slugs; only hosted products |
| arXiv | searched | About 80 queries through the harvester (about 60 recorded with their wording); queries of three or more terms mostly returned nothing |
| OpenAlex | searched | About 120 searches and citation lookups through the harvester (citers of Bellotti 2004, HULA, the Qt dependency paper, CSCW 2017, "'Stick to' Three" and Ahmetoglu 2024 among them), plus legal-copy lookups; 8 lookups in round 5 were sent without the configured key |
| OpenAIRE | searched | About 15 queries |
| Semantic Scholar | searched | Recommendations from WideSWE (2609.33382), LLM-RankFusion (2406.00231), Closed-Loop (2604.05000), CHAP (2606.09751), 2104.06033, 2609.16779, 2402.13149, Bellotti 2004, AI-Powered Reminders (2403.01365), File-Level Copying (2607.02059), CSCW 2017 (10.1145/2998181.2998251) and CrossSWE (2611.01484); the grooming paper (2507.10753) wasn't found; exact-title lookups of six papers |
| papers.cool | searched | 4 queries |
| Hugging Face papers | searched | 6 queries; mostly LLM-serving noise |
| Zenodo | searched | Record pages only (its robots.txt disallows `/api` and `/search`); Loop Engineering read from its record |
| Crossref | searched | About 8 queries on classic prioritization topics |
| Europe PMC | excluded | No life-sciences angle |
| Venue program pages | excluded | No known venue and year to scan; OpenAlex covered recent venues |

## Snowball rounds

1. **Round 1** (five agents, one per group of services): about 130 candidates. Serious: [td-fly](https://github.com/mergodon/td-fly), [relevo](https://github.com/elalfner/relevo), [backlog.md-hub](https://github.com/u-ichi/backlog.md-hub), [backlog-sync](https://github.com/djensenius/backlog-sync), [wellmanifest/priority](https://github.com/wellmanifest/priority), [pma](https://github.com/shakfu/pma), [beads](https://github.com/gastownhall/beads)' external dependencies, [copierz](https://pypi.org/project/copierz/), [rollout-cli](https://pypi.org/project/rollout-cli/) and [multi-gitter](https://github.com/lindell/multi-gitter); the audit of Backlog.md, Renovate and GitHub.
2. **Round 2** (seeded from round 1's novel finds; catalogs excluded): added [onetaskgraph](https://github.com/nickderobertis/onetaskgraph), [llmsort](https://github.com/XyraSinclair/llmsort), [Backlog Atlas](https://github.com/serendipitynz/backlog-atlas) (listing), GitHub's agent approvals for issue fields, and ideas from [gentle-teams](https://github.com/alferio94/gentle-teams) and [RELAI-TEAM](https://github.com/ECG-Rudy-Glt/RELAI-TEAM).
3. **Round 3** (adds N5a, human prioritization methods, at the developer's request): added [ai-cortex](https://github.com/nesnilnehc/ai-cortex), [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit), [lodestar](https://github.com/AustinGailey/lodestar), [bones](https://github.com/bobisme/bones), [markdown-task-butler](https://github.com/dobachi/task-butler), [taskpeasant](https://github.com/alexgc96/taskpeasant) and Taskwarrior's urgency (read in source); the requirements-prioritization literature.
4. **Round 4**: added [zps-pareto](https://github.com/zebrapuma/zps-pareto-github-issues), [hubd](https://github.com/bzdOS/hubd), [work-ledger](https://github.com/NelsonBrandao/work-ledger), [gbd](https://github.com/aigency/gbd), [ziku](https://github.com/tktcorporation/ziku), the [osdu-spi](https://github.com/Azure/osdu-spi) fleet rollout, [Cora](https://github.com/pivy-off/cora)'s design and [htm](https://github.com/MilesCranmer/htm) (listing); Backlog Atlas and backlog.md-hub read in source.
5. **Round 5**: added [gh-aw](https://github.com/github/gh-aw), [mouc](https://github.com/rnortman/mouc), the [lark-cowork](https://github.com/larkcowork/lark-cowork-plugins) task-prioritizer, htm read in source, and ideas for piece K from git-watcher (npm package `@openacp/git-watcher`; no link found, its repository returned 404 in round 7), [ripplemap](https://github.com/Zintrivious/ripplemap) and [simili-bot](https://github.com/similigh/simili-bot) (404 in round 7).
6. **Round 6** (agent skills: `SKILL.md` descriptions and community `marketplace.json` files through code search, and skills.sh hits resolved through repository trees; about 40 skills read): added [claude-zamu](https://github.com/dhh1128/claude-zamu), [basecradle-harness](https://github.com/basecradle/basecradle-harness)'s handoff conventions and [launch-control](https://github.com/peter3605/launch-control).
7. **Round 7** (a full round, under a stricter rule: a find counted only if it would change one of pieces G-K): added [cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) (consumer-to-template feedback), [markdown-vault-mcp](https://github.com/pvliesdonk/markdown-vault-mcp) (upgrade notes and drift reports in update pull requests) and the [Ajibode et al.](https://arxiv.org/abs/2508.10157) paper; the web and registry routes found nothing serious, and the literature route found nothing else that bore on the design.

Each of rounds 2 to 7 added sources of ideas, and none after round 1 changed the verdict; the shortlist stopped changing after round 5. After round 7 the developer stopped the search, short of the 10-round cap and with the stop rule unmet. Open leads:

- whether GitHub clears a cross-repo "Blocked" mark on close and allows links across owners (a test in two throwaway repos would settle both);
- gh-aw's engine requirement (H4);
- Cora's full design document (all rights reserved; ideas only);
- the paper under "Worth retrieving manually";
- simili-bot, git-watcher and issue-kit-mcp, whose repositories returned 404 in round 7;
- fastmcp-server-template's upgrade-notes documents, and whether Renovate's Copier pull requests can carry them;
- about 15 skill and marketplace hits from rounds 6-7 not yet read.

## Refresh trigger

- Before the cross-repo LLD is finalized, if more than three months have passed (after 2027-02-16).
- When Backlog.md adds a workspace or multi-project mode (its issue #1069 asks for one), or stops preserving unknown frontmatter keys.
- When GitHub documents how cross-repo blocked-by clears or whether it works across owners.
- When a tool appears that computes readiness across per-repo file backlogs, or a paper evaluates agent-assisted backlog ranking under human authority.
