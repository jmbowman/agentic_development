# Orca

[Orca](https://github.com/stablyai/orca) is a desktop app for running many coding agents at once, each in its own git worktree. This repo trials it as a session manager; [the Orca guide](../orca.md) covers using it. This page is about how it's built. Observed on 2026-11-23, reading the repository at v1.4.269 and GitHub's API.

## Who

- **Stably AI,** a San Francisco startup from Y Combinator's Winter 2022 batch. YC lists Jinjing Liang as co-founder and CEO, and Neil Parker as a founder ([YC](https://www.ycombinator.com/companies/stably-ai-orca)).
- **About five core developers.** Five GitHub accounts hold about 18,000 of the commits (nwparker 8,173, brennanb2025 3,552, Jinwoo-H 2,544, AmethystLiang 2,537, AmoabaKelvin 1,394). About 25 outside contributors have 10 or more.
- **Paid for by another product.** Orca is free and MIT-licensed, and runs on the user's own agent subscriptions. Stably sells an enterprise version, but its revenue comes mainly from its AI testing platform, sold by subscription and usage credits (third-party reports: [everydev.ai](https://www.everydev.ai/developers/stablyai), [Extruct](https://www.extruct.ai/hub/stably-ai/)). Funding beyond YC's seed is reported inconsistently, as anything from \$0.5M to \$7.7M, and wasn't confirmed from a primary source.

## Pace and quality

- **Created 2026-03-17;** by 2026-11-23 it had 133k stars, 8.5k forks, about 47,000 pull requests and 9,000 open issues.
- **About 20 commits an hour** on the morning observed: 100 commits between 00:07 and 04:52 UTC.
- **Releases about daily,** with hourly and daily macOS builds, and 78 CI workflows.
- **Solid in use:** the trial here found its settings, hook installation and terminal daemon behaving as their source describes.

## Practices

Read in the repository unless marked otherwise.

1. **A short root `AGENTS.md` (60 lines)** that points to detail in `docs/agents-md-refs/`, read only when a task touches that area ("If changing code around `git` … read git-workflow.md"). Directories with their own traps keep their own `AGENTS.md`, such as the terminal daemon's, which records 23 defects from seven review rounds and the rules that came out of them.
2. **One gate, scoped to the change.** `pnpm check:changed` runs format, lint, typecheck, the tests that import the changed files, and the ratchets the paths select, and prints only failures. Agents are told a pass is cached, not to re-run it, and not to run the full suite, which is CI's job.
3. **Ratchets.** 34 baseline files in `config/` (file length, synchronous file access in the main process, typecheck errors in end-to-end tests, flaky-test patterns and more) list today's violations of a rule; a count may only go down, and `--prune` removes fixed ones. A strict rule applies to new code at once, without first fixing the old.
4. **Strict rules for tests** (`docs/agents-md-refs/test-antipatterns.md`). A test stays only if it fails when the change is reverted, its expected values are hardcoded rather than computed by production code, and it runs at the one layer that owns the behavior. A long list of anti-patterns is banned: asserting only mock calls, copying inventories, pinning constants, testing third-party libraries, timing. Only `*.performance.test.*` files may count work, and each names the incident it guards and fails when that fix is reverted.
5. **AI review on every pull request:** CodeRabbit reviews each one, and the pull-request template asks for a summary from the author's coding agent covering cross-platform behavior, remote use, agent compatibility, performance, UI quality and security.
6. **"First-class citizens":** every change is weighed against macOS, Linux and Windows, remote hosts, mobile, and workspaces that aren't git worktrees.
7. **Main is always releasable,** with dark-build switches (`config/dark-build-switches.cjs`) for unfinished work, and a broken CI fixed before anything else.

## Fit here

| Practice | Fit | Where it's taken up |
|---|---|---|
| Test criteria: fails on revert, hardcoded expectations, one layer | Good. Its default of adding no tests conflicts with LID's tests-first rule, so borrow the criteria, not the default | AD-141 |
| Ratchets | Good for copier-python consumers adopting the strict profile | The copier-python outbox draft on a stored named-exception baseline |
| A short `AGENTS.md` with references read on demand | Likely good: this repo's `AGENTS.md` keeps growing | Not yet taken up |
| One cached, change-scoped gate for agents | Worth weighing against `mise run check`, which runs everything | Not yet taken up |
| An agent-written risk summary in each pull request | Cheap; fits copier-python's template | Not yet taken up |
| AI review on every pull request | Overlaps this repo's review waves, which run before commit | Not yet taken up |
