# agentic_development

Shared tooling for an agentic development process: the pieces each project **references by version** (reusable CI workflows, Renovate presets, and later skills and hooks). This repo also holds the system-level design that its sibling repos (such as `../copier-python`) point back to.

## Working rules

- **Commits:** agents don't commit. They draft `commit-message.md` (gitignored), and the developer they work for commits with `git commit -F commit-message.md`. One commit per slice that has cleared tests and the review wave. A prior-art note is a slice too: its review wave runs before its commit message is drafted. Several sessions can work in this repo at once, so re-read `commit-message.md` right before writing it, and don't replace a draft that hasn't been committed yet (compare its summary line with `git log -1`).
- **Checking the staged tree:** to check exactly what's staged, extract `git archive $(git write-tree)` into `tmp/staged-check/` and run the checks there. In that copy `test_skills_layout` and `test_own_skill_links_are_not_ignored` fail whatever the change: the APM-installed skills aren't in git, and `tmp/` is gitignored. Git commands run inside the copy resolve to the parent repo, whose `tmp/` rule ignores everything in it, so a test that reads git state there (the index, ignore rules) tests the parent: such a test skips there or builds its own repo.
- **Running the checks:** before handing back a change, run `mise run check` as CI does, with no virtualenv active. Running a tool through `uv run` activates the project venv and can pass where CI fails (a PEP 723 script's imports did).
- **LID stop cadence (project policy):** the developer reviews the HLD, LLD, EARS and edge-audit stops. For the **tests stop and the Phase 6 completion sign-off**, the review wave is the named inspector. Warn once, then continue to the review wave rather than waiting.
- **Spec-review findings:** apply fixes that don't change meaning (clarity, coverage gaps, scope wording), loop, and list every applied fix in the stop summary. Anything that chooses between two readings of intent goes to the developer as a numbered fork.
- **Specs before a prior-art search:** before searching for a tool to adopt, spec only what agents must do today. Leave behavior a candidate tool would decide (retry policy, error classification, wait caps) as open questions, so the search's criteria don't rule out a tool that made a different, equally valid choice.
- **Skill limits in briefs:** a brief or handoff for a skill run keeps the skill's own limits (round caps, stop rules, effort level) and its evidence rules (what verifies a license or a claim), neither tightened nor loosened. Ask the developer about a tighter limit for cost or time rather than writing one in.
- **Review log:** after triaging a review wave, an eval run or a run of interactive scenarios, add its row to that day's file for the component in `docs/review-log/`, creating the file if needed, as [its README](docs/review-log/README.md) says; never add rows to its frozen history file. A scenarios row has phase *Interactive*, and records a scenario as passing only when it passed in three runs of the same skill text; otherwise it gives how many runs failed. When a script leaves a skill's `manual.md`, its dated result lines move to the review log as rows in the same change. With an eval or scenarios row, update the rows of `evals/<skill>/latest-results.md` for each case or scenario that run covered.
- **Tenet citations:** LLDs and notes cite HLD tenets by number, so adding, removing or reordering a tenet means updating those citations (`grep -rni 'tenet [0-9]' docs`).
- **README:** `README.md` is for people deciding whether and how to use this repo, and LID's coherence checks don't cover it. Before handing back a change, re-read it against the change. Correct anything the change made false (paths, commands, setup steps, status, what the repo contains), and add a mention of anything a user now needs to know (a new component, command, requirement or limitation). Internal details stay in `docs/`. The review wave checks this too.
- **Tasks:** outstanding work goes in `backlog/tasks/`, one file per task, or in `backlog/outbox/<repo>/` when it belongs to another repo (`backlog/private/outbox/` when it can't be public), following the `task-tracker` skill. Don't leave it only in an issue, a note's closing section, a spec marker or a wrap-up report: link those from the task. An open or deferred spec needs a task that cites its ID. Tool feedback needs one drafting task and one filing task per tool, not one per entry. GitHub issues stay as the public way in: a task links the issue it came from, and the issue is closed when its tasks are done. After adding or changing a task, run `mise run tasks -- check`. Agents never edit `backlog/focus.yml`.
- **Which segment owns a file:** to find the design behind a file, look in this order:
  1. its `@spec` lines (`git grep -n "@spec" -- <file>`), then the folder of the spec file that defines the ID (`grep -rl <ID> docs/intent`);
  2. for a file with no `@spec` line, the "Lives in" column of the HLD's Components table (`@spec` sits only at a behavior's entry point, so skill text, workflows and helpers often have none);
  3. a search for the path in the design docs (`grep -rl "<path>" docs/intent --include='*-design.md'`).

  Then read that segment's LLD. Some LLDs name related segments, but nothing lists a segment's neighbours systematically. A file none of these finds, such as `tests/conftest.py`, is shared infrastructure: say so rather than guess an owner.
- **Knowledge base:** pages people and agents read on purpose (guides to using a tool, explanations of how something works, reference material) go in `docs/wiki/`, one page per topic. Design intent stays in the arrow (`docs/high-level-design.md`, `docs/intent/`), search results in `docs/prior-art/`, process lessons in `docs/process-lessons.md`, and tool bugs in `docs/tool-feedback/`. A wiki page links to those rather than restating them. Pages are meant for other developers' machines too: a page whose instructions depend on the operating system or architecture says which platforms they were tried on, and keeps each platform's notes apart.
- **Tool feedback:** proposed enhancements and bugs for tools this repo uses or plans to adopt go in `docs/tool-feedback/<tool>.md` (where, what, evidence, suggested fix, whether raised upstream) until they're raised upstream.
- **Supplied papers:** the developer drops lawfully obtained papers in `inbox/` (gitignored). Read them there, record the read state in the relevant note, and never stage them.
- **Public content only:** this repo is public. Don't reference private repositories or files in them, and don't name or assume a particular user. Cite public sources, or restate what's needed here. Work found while reading a private repo stays out of tracked files, whichever repo it is for: put it under `backlog/private/`. So do personal details about the developer, including ones an agent knows from memory.
- **Subagents** for LID probes and review waves are authorized. Never use the built-in Explore or Plan agents for implementation or review work, because they don't load project rules. A subagent still loads this repo's `AGENTS.md` and git status, so a blind divergence probe isn't blind to the repo: its brief asks it to list separately any reading it drew from outside the spec text. A review brief names the revision under review (a commit, the staged tree or the working tree) and how to view it, since another session may have committed the change or staged other work. For the working tree that is `git diff HEAD`: the developer stages files as they review them, and plain `git diff` leaves those out. Every brief gives absolute paths: a subagent's shell commands can start in the repo root rather than where its last command left off.
- **Script tests:** a test that runs a script as a subprocess asserts its exit status, fails on any Python traceback in its output, and runs it with `cwd` in the test's temporary directory, so a crash or a missing script can't pass a "nothing was written" test, a crash's exit status 1 can't pass for the script's own status 1, and a relative path can't write into the repo. It runs a script meant to use only the standard library on the interpreter the project venv was made from (`sys._base_executable`), since under the venv's own interpreter an import of a dev dependency would pass.
- **Scratch runs of pinned tools:** `mise -C <repo>` runs the command with `<repo>` as its working directory, so a tool started that way from a scratch copy acts on the repo. From the scratch directory, call the tool by the absolute path that `mise which <tool>` prints in the repo.
- **Clash prompts:** when [Clash](https://github.com/clash-sh/clash)'s hook flags an edit, Claude Code asks the developer to approve it without saying why, and the agent learns why only from the approved edit's result ("Conflicts on <file> with N worktree(s): …"); a rejected edit tells it nothing. When an edit's result carries that text, tell the developer which worktree has changed the file before going on, and make no further edit to that file until they say how to proceed. After an edit in a worktree is rejected, run `clash check <file>` and tell the developer what it reports. A conflict reported on `commit-message.md` against the main worktree is a known false positive ([tool feedback](docs/tool-feedback/clash.md)): the file is gitignored and each worktree has its own. Say that it came up, and carry on.

## LID
- Mode: Full
- Version: 1.4.0

## Linked-Intent Development (MANDATORY)

**Consult the `linked-intent-dev` skill for ALL code changes.** All changes flow through the arrow of intent in one direction:

```
HLD → LLDs → EARS → Tests → Code
```

- **All changes**: consult the `linked-intent-dev` skill if your harness provides it; otherwise read `docs/lid/workflow.md` before making changes, and if it is missing and `## LID` records no decline, offer the user once to add it from https://raw.githubusercontent.com/jszmajda/lid/v1.4.0/plugins/linked-intent-dev/skills/update-lid/references/workflow-doc.md (on decline, add `- Workflow doc: declined` to `## LID`). The workflow in one line: HLD check → LLD → EARS specs → edge audit → failing tests first → code — inspected at each phase.
- **Bug fixes**: walk the arrow like any other change — find where behavior diverged from intent and cascade from there. No short-circuit.

Each phase's output is inspected — by the user or an inspector they name — before the next begins; ambiguous spec readings go back to the user. **Docs carry current intent, written to be read cold** — write each doc as if authored fresh today, from current intent alone: no narration of how it changed, no meaning that needs the conversation that produced it, no rebuttals to questions only a past discussion raised. Rationale, considered alternatives, and constraints a fresh author would independently write stay; record rejected alternatives and why in the LLD's Decisions & Alternatives table, not as asides in body prose.

**Memory vs. intent.** Before saving durable project knowledge to agent or tool memory, test whether it is project *intent* — would a fresh agent, in any tool, next session, need it to build this system correctly? If yes, record it in the arrow (HLD / LLD / EARS / decision doc), which travels and cascades — not in private, per-tool memory, where intent escapes the arrow. Knowledge about the user or how they like to work stays in memory.

### Navigation

| What you need | Where to look |
|---|---|
| High-level design | `docs/high-level-design.md` |
| Design tree (sub-HLDs, LLDs, their specs) | `docs/intent/` — one folder per node |
| EARS specs | beside each design doc as `{node}-specs.md` in the node's folder under `docs/intent/` |
| Decision docs | `docs/decisions/` (project-level) and `docs/intent/<segment>/decisions/` |
| Arrow of intent overlay | `docs/arrows/index.yaml` and per-segment docs in `docs/arrows/` |

### Terminology

- **HLD**: High-Level Design — single project-level doc at `docs/high-level-design.md`.
- **LLD**: Low-Level Design — detailed component design doc in `docs/intent/`. The design layer is a recursive tree: the root is the HLD, leaf LLDs own EARS, and a component deep enough to outgrow one doc becomes a sub-HLD (HLD-shaped, owns no EARS) with children beneath it. "HLD" and "LLD" are roles by position; depth-2 (one HLD over flat leaf LLDs) is the default.
- **EARS**: Easy Approach to Requirements Syntax — structured one-line requirements beside each design doc as `{node}-specs.md` in the node's folder under `docs/intent/`. IDs are path-concatenated — the root-to-leaf path of the owning segment plus a number — so a prefix grep gathers a subtree. Markers: `[x]` implemented, `[ ]` active gap, `[D]` deferred.
- **Arrow**: the unidirectional chain from vision to code (HLD → LLDs → EARS → Tests → Code). Strictly a DAG of intent.
- **Arrow segment**: the territory owned by one leaf LLD — the LLD itself plus the specs, tests, and code that cite its EARS IDs. The boundary is the leaf prefix. Within-segment cascade is free; across-segment cascade pauses.
- **Cascade**: propagating a change downstream through the arrow so adjacent levels stay coherent.

### Code annotations

Annotate code and tests with `@spec` comments citing EARS IDs:

```
// @spec AUTH-UI-001, AUTH-UI-002
```

Place the annotation at the *entry point of the behavior's implementation graph* — the topmost function or module owning the specified behavior, not every helper. When a behavior spans multiple subsystems (UI + API + database, for example), annotate at the entry point in each subsystem. Tests follow the same rule: annotate the test that directly exercises the spec, not every inner assertion.

## LID Tooling

Declare project-local helper scripts LID-related skills should invoke instead of their in-prompt fallbacks. When present, the listed scripts are authoritative for the deterministic checks they perform. When absent or empty, skills fall back to performing the checks in-prompt.

- **Coherence check**: `mise run lid` — runs `lidc check` for the reverse-orphan, coverage and spec-ID-format checks. LID's other audit checks still run in-prompt.
