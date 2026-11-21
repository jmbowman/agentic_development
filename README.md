# agentic_development

Shared tooling for repos where coding agents write most of the code: CI workflows and a Renovate
preset that every repo references by version, agent skills that reach repos through the template,
plus the design of the system they belong to.

## Why

Agents write code faster than anyone can review it line by line, so quality has to come from
guardrails that run on every change: strict lint and type checks, tests, and design docs the code
is checked against. Those guardrails only help if every repo has them, and copying setup files
from repo to repo fails in predictable ways:

- **Copies drift.** A repo set up from last month's files misses this month's fixes.
- **Changes need hand edits everywhere,** so most repos never get them.
- **Guardrails erode.** An agent under pressure relaxes a check instead of fixing the code.

The broader aim is to assemble the best existing methods and research for each part of the
lifecycle into one system a single developer can drive, and to build only what's missing.

## What you get

- **One baseline, kept current automatically.** A [copier](https://copier.readthedocs.io)
  template renders the baseline into each repo. When the template, workflow or preset changes,
  [Renovate](https://docs.renovatebot.com) opens an update pull request, which merges by itself
  once CI passes. Raising the bar means changing one repo, not every repo. The exception is a
  new LID minor or major version: its update fails `check` until someone runs LID's
  `/update-lid` on the update's branch, because the design docs need walking to the new
  version. A LID patch release asks nothing of a project, so it merges like any other update.
- **Strict by default, with exceptions you can count.** Checks start as strict as each tool
  allows (for Python, every ruff rule and every ty rule as an error). Each relaxation is a named
  exception that a task lists, so a repo's divergence is visible and can be paid down.
- **CI a repo can't quietly hollow out.** The shared workflow runs every check, even after one
  fails, and fails if a repo has redefined the template's `check` task or any task it depends on.
- **Design that stays connected to code.** Repos follow
  [Linked-Intent Development](https://github.com/jszmajda/lid) (LID): design docs, specs, tests
  and code that cite each other, with a CI gate that fails when the links break.
- **Built from mature open-source parts:** copier, Renovate, mise, GitHub Actions. Nothing is
  tied to one person or organization.

## What's in this repo

| Path | What it is |
|---|---|
| `.github/workflows/check.yml` | The reusable CI workflow. A repo's CI is a stub that calls it with no inputs; it installs the repo's pinned tools with [mise](https://mise.jdx.dev) and runs the repo's `check` task. |
| `.github/workflows/lock-refresh.yml` | A reusable workflow for repos that commit `mise.lock`. On Renovate's template-update PRs it reruns `mise lock` and pushes the result with a GitHub App token, so those PRs pass CI's locked install and still merge automatically. |
| `renovate/default.json` | The Renovate preset: update pull requests merge automatically once CI passes, most new releases wait 3 days first, and template-owned files are left to the template. |
| `skills/prior-art-search/` | An agent skill that searches for existing software, and for published research on approaches, before an agent recommends building something: sources chosen by the need, candidates classified with licenses read from their license files, limitations verified in source, papers tagged by how much was read and linked by name, and a dated note saved for costly choices. Free keys for some sources (OpenAlex, libraries.io and others) are optional; an OpenAlex key raises the daily budget that its default literature searches spend: copy `skills/prior-art-search/references/settings.example.toml` to `.config/prior-art-sources.toml` in your repo, fill in what you want, and make sure git ignores it (reading it needs Python 3.11 or later). A value you set is sent with every request to its source, and a source that rejects it is skipped for the rest of the run. Its literature searches on arXiv and OpenAlex, and its Semantic Scholar recommendations and title lookups, go through a bundled script, `scripts/harvest.py`, which paces requests across every search on your machine, retries Semantic Scholar's frequent refusals, and keeps raw results out of the agent's context. It needs [uv](https://docs.astral.sh/uv/), which installs a pinned fork of [paper-search-mcp](https://github.com/jmbowman/paper-search-mcp) on first use, and Linux or macOS. It keeps its shared pacing in `~/.cache/prior-art-search/` (under `$XDG_CACHE_HOME` when set). Without uv, the agent sends those requests itself. It follows the [Agent Skills](https://agentskills.io) format, so it works in Claude Code and other agents. |
| `skills/session-wrap-up/` | An agent skill that closes out a session: it proposes a home for each durable lesson, following the repo's own rules for where knowledge lives, lists the session's loose ends after checking them against the current state, proposes recording the ones that name work as tasks in the repo's backlog, drafts feedback for other repos as outbox drafts in that backlog for the developer to deliver, and ends with a prompt that starts the next session. It writes nothing until the developer has chosen items and confirmed their exact text, and a non-interactive run only reports. After a context compaction it searches the session transcript, but only at a location the harness or the developer states; without one, it says which turns it didn't review. It triages the process notes the hooks below collect from subagents, which it reads from the session's notes directory beside the transcript, outside the repo (Claude Code may ask permission for that read), and says when subagents ran without the hooks. Recording tasks needs a `backlog/` in Backlog.md's format, its `backlog` CLI on `PATH`, and backlog settings with `remote_operations: false` and `auto_commit` off, since otherwise the CLI fetches or commits; without them, loose ends stay a list in the report. Work that a repo can't hold publicly goes to a private outbox, which can be the one write outside the repo (to a private repo named in `~/.config/task-tracker/config.yml`), and Claude Code may ask permission for it. |
| `hooks/hooks.json`, `skills/session-wrap-up/hooks/` | Claude Code hooks, shipped with the plugin and registered in this repo's `.claude/settings.json`, that ask each finished subagent one fixed question about the friction it met and save the reply as a notes file beside the session transcript, without changing the subagent's report. Each subagent costs a short housekeeping turn and, outside auto mode, a permission prompt; they ask only in interactive sessions, and `SUBAGENT_NOTES=off` turns them off. They need `python3` 3.11 or later. A repo that installs the skills with APM, and a cloud session, which doesn't install plugins, doesn't get them: [the skill's reference](skills/session-wrap-up/references/subagent-notes-hooks.md) gives the settings to add by hand. |
| `.claude-plugin/` | Packages this repo as a Claude Code plugin (the repo root is the plugin), with a one-plugin marketplace, so Claude Code can install it straight from this repo. |
| `apm.yml`, `apm.lock.yaml`, `.claude/hooks/` | [LID](https://github.com/jszmajda/lid)'s skills pinned with [APM](https://github.com/microsoft/apm). The pin serves this repo and, as the skills package's dependency, every repo that installs the package. Also this repo's hook that installs the tools and skills in Claude Code cloud sessions. |
| `evals/` | Behavior evals for each skill, in `evals/<skill>/`, run by hand with `mise run eval`, which runs `claude plugin eval` in a clean copy of the plugin; each skill's `latest-results.md` gives every case's most recent triaged result. See its README. |
| `scripts/` | The workflow's helper script, fetched at the workflow's own commit; `run_evals.py`, which the `eval` task runs; and `collect_scenarios.py`, with which `check` imports the interactive scenarios (still to come) without running them. |
| `skills/task-tracker/` | An agent skill for a repo's task backlog: outstanding work as one Markdown file per task in [Backlog.md](https://github.com/MrLesk/Backlog.md)'s format with a few extra keys, a read-only tool (`scripts/tasks.py`) that lints the files and ranks what is ready, separately for the developer and for agents, and the rules agents follow to record, pick up and finish tasks and to draft work for other repos. It assumes the repo already has a backlog: a `backlog/config.yml` with the statuses and task types the skill's format reference lists. The tool needs [uv](https://docs.astral.sh/uv/) and Python 3.12 or later, and uv installs its one dependency (PyYAML) on first use. Agents create tasks with Backlog.md's `backlog` CLI, and blockers on GitHub are looked up with the `gh` CLI. Still in progress: its lint and ranking are being rebuilt to their specs, and the template doesn't deliver it yet. |
| `backlog/` | This repo's own backlog, tracked with the skill above; see [its README](backlog/README.md). |
| `docs/` | The system's high-level design, each component's design and specs, prior-art notes, a log of each review wave's yield and cost, and lessons about the development process. |

## Using it

Most repos get everything through a template rather than from this repo directly. The first is
[copier-python](https://github.com/jmbowman/copier-python), a strict Python baseline. Its README
covers onboarding a new or existing repo.

To use the skills before the template delivers them, install this repo as a Claude Code plugin:

```
/plugin marketplace add jmbowman/agentic_development
/plugin install agentic-development@agentic-development
```

This tracks the default branch, not a release tag. In other agents, copy or link
each skill's directory in `skills/` into the agent's skills directory (commonly `.agents/skills/`).

In this repo itself, each skill in `skills/` is linked from `.claude/skills/` (for Claude Code)
and from `.agents/skills/` (for other agents).

## Status

Early: one template (Python), GitHub only, Linux runners. Two shared agent skills are built:
prior-art search, and session wrap-up, whose capture of items in an issue and memory triage are still to come. It reads the process notes that its hooks collect from subagents, and records loose ends as tasks.
The template delivers skills to a repo, installed from a lock file (copier-python v0.3.0 and
later). Session wrap-up and the other changes made here since v0.3.1 aren't in a release yet, so
they don't reach template repos. A third skill, the task tracker, is in progress: its rules and
tool are usable in this repo, whose backlog it tracks. Process guardrails (commit gates, review loops) are designed in
outline only.

## Developing this repo

Install [mise](https://mise.jdx.dev), then run `mise trust` and `mise run setup`. Setup also
installs the LID skills that `apm.lock.yaml` pins (they're gitignored, so a fresh clone has none
until then); run `mise run skills` again after a LID update. `mise run check` runs everything CI
runs, and needs network access to GitHub the first time it installs the skills. Start with
[`docs/high-level-design.md`](docs/high-level-design.md) for the design.

In a Claude Code cloud session, a SessionStart hook installs mise, the pinned tools and the
skills before the first prompt. The environment's network policy must allow GitHub (releases
and git), `nodejs.org`, npm and PyPI. Threads in a claude.ai Project don't run the hook or load
the repo's skills.

## License

[Apache License 2.0](LICENSE).
