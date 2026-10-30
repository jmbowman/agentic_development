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

## What you get

- **One baseline, kept current automatically.** A [copier](https://copier.readthedocs.io)
  template renders the baseline into each repo. When the template, workflow or preset changes,
  [Renovate](https://docs.renovatebot.com) opens an update pull request, which merges by itself
  once CI passes. Raising the bar means changing one repo, not every repo. The exception is a
  new LID version: its update fails `check` until someone runs LID's `/update-lid` on the
  update's branch, because the design docs need walking to the new version.
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
| `skills/prior-art-search/` | An agent skill that searches for existing software before an agent recommends building something: sources chosen by the need, candidates classified with licenses read from their license files, limitations verified in source, and a dated note saved for costly choices. It follows the [Agent Skills](https://agentskills.io) format, so it works in Claude Code and other agents. |
| `skills/session-wrap-up/` | An agent skill that closes out a session: it proposes a home for each durable lesson, following the repo's own rules for where knowledge lives, drafts feedback for other repos, and ends with a prompt that starts the next session. This first version only proposes; the developer applies what they choose. |
| `.claude-plugin/` | Packages this repo as a Claude Code plugin (the repo root is the plugin), with a one-plugin marketplace, so Claude Code can install it straight from this repo. |
| `apm.yml`, `apm.lock.yaml`, `.claude/hooks/` | [LID](https://github.com/jszmajda/lid)'s skills pinned with [APM](https://github.com/microsoft/apm). The pin serves this repo and, as the skills package's dependency, every repo that installs the package. Also this repo's hook that installs the tools and skills in Claude Code cloud sessions. |
| `evals/` | Behavior evals for each skill, in `evals/<skill>/`, run by hand with `claude plugin eval`; see its README. |
| `scripts/` | The workflow's helper script, fetched at the workflow's own commit. |
| `docs/` | The system's high-level design, each component's design and specs, prior-art notes, and a log of each review wave's yield and cost. |

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
prior-art search, and the first slice of session wrap-up, which proposes but doesn't yet apply.
Delivering skills through the template, installed from a lock file, is designed and not yet
released. Process guardrails (commit gates, review loops) are designed in
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
