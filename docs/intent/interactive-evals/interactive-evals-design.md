---
parent: high-level-design
prefix: IEVAL
---

# Interactive scenarios

## Context and Design Philosophy

`claude plugin eval` runs one prompt per case, in a non-interactive session. Some of the skills' behavior happens only in a live conversation: a skill that asks the developer to choose, shows text in a question dialog and waits for a confirmation before it writes; hooks that act at the end of a turn; a real compaction. Those specs, and the parts of some *(eval)* specs that an eval can't reach, are checked by scripts a person follows by hand, in `evals/session-wrap-up/manual.md` (which also holds the scripts for the [subagent notes hooks](../subagent-notes/subagent-notes-design.md), since those hooks ship with the session wrap-up skill). Scripts are slow, and a step done slightly differently changes the result, so they have mostly gone unrun.

The interactive scenarios turn those scripts into pytest tests. Each test seeds a scratch repo, starts a real, interactive Claude Code session with this repo loaded as a plugin, types the developer's turns, answers each question dialog as the test says, and checks what happened: the files at each stop, the order and inputs of the agent's tool calls, and the text of its replies.

The machinery that drives the session belongs to [pytest-claude-code-evals](https://github.com/jmbowman/pytest-claude-code-evals), a pytest plugin with its own repository and design docs (see the HLD's decision that the harness is its own project). It runs Claude Code in a terminal emulator and uses Claude Code hooks to answer dialogs, gate and log tool calls, and mark the end of each turn. This doc covers this repo's side: where the scenarios live, how this repo depends on and runs the plugin, how a spec moves from a manual script to a test, how runs are recorded, and what the scenarios need the plugin to provide.

## Layout and running

| Path | Contents |
|---|---|
| `evals/<skill>/interactive/test_<skill>.py` or `test_<skill>_<suffix>.py` (the skill's name with `_` for `-`) | A skill's scenarios, one test per manual script it replaces, each with `@spec` annotations |
| `evals/<skill>/interactive/conftest.py` | The skill's seeds (the scratch repo's files for its scripts) and its shell allowlist; no `@spec` annotations |
| `evals/<skill>/latest-results.md` | The skill's latest-results table: each eval case's and scenario's most recent triaged run |
| `pyproject.toml` | The plugin, pinned to an exact release or git commit in a dependency group of its own, `interactive`; the `replaces` marker's registration (the repo runs pytest with `--strict-markers`) |

- **Run by hand, checked in CI.** Each scenario is a paid model run, like the evals. The repo's `pytest` run collects only `tests/` (`testpaths`), so it never runs them. A developer runs `uv run --group interactive pytest evals/<skill>/interactive`, with the model under test and the judge model given as the plugin's options. The `interactive` group is installed everywhere the other groups are, CI included, so ty can check the scenario files against the plugin's types, and `check` collects the scenarios without running them (`pytest --collect-only`), which catches a broken import, fixture or marker at no model cost.
- **The plugin is inert when unused.** Installed, pytest loads it in every run, `tests/` included, so it must change nothing for a test that uses none of its fixtures or markers.
- **Module names are unique across skills.** The scenario directories have no `__init__.py`, and pytest's default import mode imports test modules by basename, so each module's name starts with its skill's (`test_session_wrap_up_approval.py`).
- **The plugin under test** is this repo's root, loaded with `--plugin-dir`, so a scenario runs the skills and hooks as they stand in the working tree, uncommitted edits included. Every scenario runs in a seeded scratch repo, never in this repo. The check that the subagent notes hooks act once when registered twice (NOTES-LIVE-003) seeds its scratch repo's `.claude/settings.json` with the same hook entries this repo's own settings register, so the plugin and the project both register them.
- **The subagent notes scenarios** live in `evals/session-wrap-up/interactive/`, since those hooks ship with the session wrap-up skill and their scripts are in its `manual.md`; `tests/test_subagent_notes_hooks.py` holds their structure checks.
- **The pin** is updated by Renovate like any other development dependency, and automerges under the shared preset's policy (tenet 6). Because no check runs the scenarios, an update that merges has passed only the repo's structure tests; the next hand run is what exercises it.

## From manual script to test

- **One test per script, linked by name.** A test replaces one section of `manual.md`, and says which with a `replaces` pytest marker holding the section's heading. The section is deleted in the change that adds the test. The test carries the `@spec` IDs it checks, and its steps and pass conditions say what the script's did; where a check was a judgment (for example, "the report treats the run as interactive"), the test asks the plugin's judge. Every current script can become a test once the plugin meets the needs below; a step it turns out not to reproduce stays in the script, with the specs only that step checks.
- **The marker changes with the script.** A marker records how a spec is checked, not its latest result. Once no remaining script names a spec and a test cites it, the spec changes from *(manual)* to *(interactive)*; while any script still names it, it keeps *(manual)*. A spec checked partly by an eval and partly by a test is marked *(eval, interactive)*. Whether the checks currently pass is in the latest-results table (below), not in the marker.
- **The last script.** When a skill's `manual.md` has no script left, it is deleted, together with the structure tests that read it. Those tests live in the session-wrap-up and subagent-notes segments, so that change cascades there.
- **One check for every segment.** The marker rules govern every segment's specs file, so a single structure test of this segment checks them across all specs files and `manual.md` files. Each segment's own structure tests read a marker as a list, so *(eval, interactive)* counts wherever *(eval)* does; adapting them, and the intro lines of their specs files that describe the markers, is a cascade into those segments when the first scenario lands.
- **Results move with the script.** In the change that deletes a section, its dated result lines move to the review log as rows, so a recorded failure isn't lost.
- **lidc sees the tests directly.** lidc reads `@spec` annotations in `test_*.py` files under `evals/` as tests, so the scenarios count for its coverage check, and *(interactive)* specs don't need the citation block that *(eval)* and *(manual)* specs get in a skill's structure test file; a spec leaves that block when it becomes *(interactive)*.
- **A pass.** A spec counts as passing when its test passes in three runs. One run can't tell a reliable behavior from a lucky draw, and three is the most this repo's eval rows have used to measure a behavior's rate. A test that fails in some runs is diagnosed from its tool log and judge verdicts before the skill text changes, as a flaky eval case is, and the rate is recorded either way.

## Recording runs

- **Results** go to the plugin's JSON output under each skill's gitignored `evals/<skill>/interactive/results/`.
- **The review log** gets a row for each triaged run of a skill's scenarios (the review-log working rule in `AGENTS.md`), in the eval rows' form: phase *Interactive*, the cases and runs, what was found and applied, the plugin's reported cost and the time taken.
- **The latest-results table.** The review log is a history, ordered by when waves ran, so it can't answer "is this check passing now?" without a scan. Each skill's `evals/<skill>/latest-results.md` has one row per eval case and per scenario, giving its most recent triaged run: the date, Claude Code version, model, runs and failures, and the review-log row it came from (its Date, Component, Phase and Wave, which together name one row), or `never run`. A run that failed because of the grader or the case, not the skill, is left out of both counts, since the table answers whether the skill is passing. It is updated in the same change as the review-log row. A structure test keeps its rows in step with the cases and scenarios that exist; the results themselves come from triage, since raw run output stays in gitignored directories on the machine that ran it.

## What the scenarios need from the plugin

These are the `manual.md` scripts' requirements, for the plugin's design to cover. The plugin decides how it provides each.

| Need | Used by |
|---|---|
| Several typed turns in one interactive session, context kept, and several sessions in one test (a script's "new run" or "new session") | every script |
| A turn's end, for state and replies, comes after any continuation a Stop hook adds (the subagent notes hooks continue the main agent's turn) | NOTES-LIVE-001, WRAP-NOTES-019 |
| Answers to a question dialog, given per question: an option, several options, free text, a note on an option, or a dismissal; a dialog the test didn't expect, or an expected one that didn't come, fails the test | the approval scripts (WRAP-GATE-*) |
| Each dialog's questions, options and previews readable by the test, including several dialogs in one turn (the tool's limit of questions, then a second dialog) | WRAP-GATE-001, WRAP-GATE-019, WRAP-GATE-020, WRAP-GATE-044 |
| A check that a preview is shown whole on screen, not cut off | WRAP-GATE-019 |
| The repo's state (status and diff against the seed) when a turn ends and when a dialog arrives, before it's answered | every approval script |
| A step run while a dialog waits, before it's answered (editing or `chmod`-ing a file in the scratch repo) | WRAP-GATE-008, WRAP-GATE-010 |
| An ordered log of tool calls with their inputs, and helpers for read-before-write and exact edits | WRAP-GATE-001, WRAP-LES-027, WRAP-NOTES-015 |
| The context hooks add, as the agent received it (the `[subagent-notes]` line, `Subagent notes:` requests) | NOTES-LIVE-001, NOTES-LIVE-003, WRAP-NOTES-019 |
| Tool gating: `Skill` allowed; file tools inside the scenario's seeded directories, and reads of this repo's plugin files; an exact-match shell allowlist; everything else denied with a fixed reason | every script |
| A scenario can allow `Agent` and `SendMessage` | NOTES-LIVE-001, NOTES-LIVE-003, WRAP-NOTES-019, WRAP-RUN-009 |
| A scenario can pass named tools through to Claude Code's own permission prompt, and the test answers that prompt (so a run in `manual` mode exercises the prompt a developer sees) | NOTES-LIVE-001 |
| Project settings seeded in the scratch repo (`.claude/settings.json`), loaded beside the plugin | NOTES-LIVE-003 |
| Seeding beyond one repo: a second git repo, a directory outside git, and links in the session's home directory | WRAP-GATE-031, WRAP-LOOSE-003 |
| Slash commands typed as turns, `/compact` in particular | WRAP-LES-015 (its harness half), WRAP-LES-027, WRAP-NOTES-015 |
| Session options: permission mode (`default`, `manual` or `auto`), disallowed tools, extra environment variables | NOTES-LIVE-001, WRAP-GATE-020, WRAP-RULE-008 (its memory half) |
| The session's ID and transcript path, its subagents' transcripts, and its config directory's per-session files (the subagent notes directory) | NOTES-LIVE-001, NOTES-LIVE-003, WRAP-NOTES-015 |
| An isolated config directory with seeded instruction files and memory, so no real user instructions or memory load, and checks of reads under its projects directory (the harness's equivalent of `~/.claude/projects/`) | every script; WRAP-RULE-008 |
| A one-shot `claude -p` run with the plugin loaded, for the specs about non-interactive runs | NOTES-LIVE-002 |
| A judge that checks a reply against one or two plain-language criteria | most scripts |
| No effect on a test that uses none of the plugin's fixtures or markers | the repo's `tests/` run |
| Caps on turns, time and cost; a tripped cap or a driver failure is an error, distinct from a fail | every script |

## Decisions & Alternatives

| Decision | Choice | Rationale | Alternatives considered |
|---|---|---|---|
| Where scenarios live | Under each skill's eval directory, `evals/<skill>/interactive/` | They test that skill's specs, beside its eval cases and `manual.md`, and the structure tests can find them by path | One shared `evals/interactive/` tree (separates a skill's checks from each other); in the plugin's repository (it would hold this repo's skill specs) |
| Running | By hand; CI installs the plugin, type-checks the scenarios and collects them without running them | Each run is a paid model call, and running them on every push would cost far more than the occasional hand run a skill change needs; collecting and type-checking cost nothing and catch a broken scenario before a paid run does | Run them in CI (cost on every push); keep the plugin out of CI with `--no-group interactive` (ty can't resolve the scenarios' imports, so they go unchecked until a hand run) |
| Marking specs | A distinct *(interactive)* marker, given only once every manual step for the spec is covered; *(eval, interactive)* for a spec checked partly by each | A reader can tell at a glance which specs a test checks and which still need a person, and the structure tests check each kind against its own evidence | Keep *(manual)* (hides which specs are automated); reuse *(eval)* (eval cases and interactive tests are found and run differently); change the marker at the first covering test (hides the steps still left to a person); keep a split spec's *(eval)* marker alone (hides that a test checks part of it) |
| Where scenarios run | Always a seeded scratch repo; a check about this repo's own setup seeds that setup into the scratch repo | A session in this repo would load its real instructions, hooks and memory, and could write to its working tree | Run that one check from this repo's root (not isolated, and depends on the developer's checkout) |
| What retires a script | A scenario's `replaces` marker naming its heading | An explicit link makes "this script is automated" a decision the test's author records, and a structure test can check it; a spec shared by several scripts otherwise keeps every script alive until all are replaced | Retire a script once scenarios cite every spec it names (a scenario covering some of a script's steps would retire all of it) |
| When a marker changes | When the script is replaced, not when a run passes | A marker says how a spec is checked; pass and fail change run to run, and belong in the latest-results table and the review log | Change it after three passing runs (the marker would then flip back and forth with results) |
| Where latest results live | A committed `latest-results.md` per skill, a row per eval case and scenario | One place answers "what's passing now", for eval cases and scenarios alike, without scanning the review log | Only the review log (history, hard to query); generated from results directories (gitignored, and present only on the machine that ran them) |
| A replaced script | Deleted from `manual.md`, its dated results moved to the review log in the same change | The test is the procedure, and a script kept beside it drifts; the results are history the review log already keeps for evals | Keep it as a fallback (two procedures to keep in step) |
| Runs per pass | Three | One run can't show a behavior's rate; three is what this repo's eval rows use to measure one | One run (a lucky pass hides a 1-in-3 miss); five or more (cost, for a gain that triage of three already gives) |

## Open Questions & Future Decisions

- **The first pin.** Until pytest-claude-code-evals has a release, the `interactive` group can pin it to a git commit. Whether to do that, or wait for a first release before writing scenarios here, depends on how far the plugin's first slice goes.
- **Credentials.** The plugin's isolated config directory needs a login. Which form (a token from `claude setup-token`, a linked credentials file, an API key) is the plugin's decision; this repo's README gives the setup step once it's settled.

## References

- [Prior-art note](../../prior-art/2026-11-03-interactive-skill-evals.md), including its 2026-11-13 refresh.
- [Session wrap-up manual scripts](../../../evals/session-wrap-up/manual.md).
