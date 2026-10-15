# agentic_development

Shared tooling for repos where coding agents write most of the code: one CI workflow and one
Renovate preset that every repo references by version, plus the design of the system they belong
to.

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
  once CI passes. Raising the bar means changing one repo, not every repo.
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
| `scripts/` | The workflow's helper script, fetched at the workflow's own commit. |
| `docs/` | The system's high-level design and each component's design and specs. |

## Using it

Most repos get everything through a template rather than from this repo directly. The first is
[copier-python](https://github.com/jmbowman/copier-python), a strict Python baseline. Its README
covers onboarding a new or existing repo.

## Status

Early: one template (Python), GitHub only, Linux runners. Shared agent skills and process
guardrails (commit gates, review loops) are designed in outline but not built yet.

## Developing this repo

Install [mise](https://mise.jdx.dev), then run `mise trust` and `mise run setup`.
`mise run check` runs everything CI runs. Start with
[`docs/high-level-design.md`](docs/high-level-design.md) for the design.

## License

[Apache License 2.0](LICENSE).
