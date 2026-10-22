# Cloud-session readiness: suggested improvements (2026-10-22)

What a Claude Code cloud session can and can't do in this repo today, and suggested changes so it works as well there as locally. Everything below was observed in one cloud session (Claude Code 2.1.307, Anthropic-hosted environment) unless marked otherwise. Items that change design intent are proposals for the LID workflow, not decisions.

## Summary

| Area | Works in the cloud today | Gap | Suggested change |
|---|---|---|---|
| Committed skills | Yes, through the `.claude/skills/prior-art-search` symlink | None | None |
| LID skills | No | Not committed; plugins don't reach cloud sessions | Pin LID in an `apm.yml` and commit the deployed skills, at 1.4.0 |
| `mise run check` | Not out of the box; passes once mise is installed | mise isn't in a new container; 39 tests fail or error without it | A SessionStart hook ([drafted and validated](2026-10-22-cloud-setup-hook-proposal.md)) or a setup script that installs mise and the pinned tools |
| prior-art-search routes | Partly | GitHub search is blocked; some catalogs need the network allowlist | Cloud notes in the routes table, with a Sourcegraph fallback |
| Commits | Conflicting | "Agents don't commit" vs. a container that is reclaimed when idle and a stop hook that asks for a push | A cloud-session commit rule |
| GitHub access | Clone, raw reads, this repo's API, and push once the Claude GitHub App has write access | No search, no topics, no other repos' API, even with the app installed | Run GitHub-wide search from local sessions |

## 1. prior-art-search in cloud sessions

**Observed.**
- **GitHub search:** `gh search` and the API's `search/*` endpoints fail. The session's GitHub proxy answers "This GitHub API path is not available: sessions are bound to their configured repositories". `github.com/search` and `github.com/topics/...` are refused the same way. `GH_TOKEN` is set but rejected (`gh auth status`: "The token in GH_TOKEN is invalid").
- **Reading public GitHub:** works. `git clone` (shallow, blobless, sparse) and `raw.githubusercontent.com` are both fine.
- **Catalogs and forges:** skills.sh and Codeberg are refused by the egress proxy under the default network policy. Both worked once their domains were added to the environment's allowed domains. mcpservers.org serves a Cloudflare bot challenge even when allowed.
- **Sourcegraph's public search** (`https://sourcegraph.com/.api/search/stream`) is reachable and searches public GitHub, with three caveats:
  - it indexes only part of GitHub (`netresearch/retro-skill` and `Wavez/debrief-skill` weren't indexed);
  - `type:repo` matches repository names only;
  - it rejects Python's default `urllib` client with 403, so use `curl`.
- **grep.app:** reachable but rate-limited (429).
- **Reference clones:** no reference-clone convention exists in this repo yet, so verification used scratch clones, as `references/verification.md` allows.
- **Note from this session:** the run produced [the retrospective prior-art note](../prior-art/2026-10-22-session-retrospective-skill.md). Its verdict stayed **inconclusive** only because GitHub's own search routes were unavailable.

**Suggested changes.** These touch the prior-art-search segment, so they go through LID: the design doc's routes and verification sections, `PRIOR-SRCH-*` specs and the offline evals.
1. **Cloud tactics in the routes table** (`skills/prior-art-search/references/sources.md`):
   - for GitHub repository and code search, name Sourcegraph's stream API as a fallback, and say that its index is partial;
   - for skill directories, name the domains an environment must allow (`skills.sh`, `codeberg.org`).
2. **Partial routes in the ledger.** Decide whether a route covered by a partial substitute counts as searched, unavailable, or a new state such as "partly searched". Today the substitute can't lift **inconclusive**, which seems right but should be explicit (open question 1).
3. **Diagnoses for the ledger.** Distinguish a proxy refusal (the network policy can fix it) from session scoping (it can't) from a site's bot protection. Each needs a different remedy, and the skill already requires a diagnosis.
4. **Running GitHub search locally** — a "finish locally" handoff in the report when GitHub's own search is unavailable: the exact queries to re-run from a local session with `gh` authenticated. This session did this by hand.
5. **An eval for the cloud case:** an offline case where `gh search` fails with the scoping message, checking that the run logs the route as unavailable with that diagnosis and doesn't conclude **build**.

## 2. LID skills in cloud sessions

**Observed.** No LID skill is available in a cloud session. `.claude/skills/` holds only `prior-art-search`, and the repo has no `apm.yml`. A local LID install, if there is one, is a user-level plugin, and cloud sessions don't install plugins (as the HLD already says). The written LID rules in `AGENTS.md` and `CLAUDE.md` still load, but `/update-lid`, `/lid-coach` and the skill's procedure don't.

**Suggested change.** Treat LID as a *repo-specific skill* in the HLD's sense: pin `jszmajda/lid` in this repo's `apm.yml`, run `apm install`, and commit the deployed `.claude/skills/linked-intent-dev/`, `update-lid/` and `lid-coach/` (and `arrow-maintenance/` if wanted). This matches how the HLD already delivers skills, and Renovate's apm manager plus the preset's existing "hold LID bumps" rule then cover this repo too.

Things to settle in the HLD check:
- **Which plugins:** `linked-intent-dev` only, or also `arrow-maintenance` and `lid-experimental`.
- **APM layout:** whether APM's deployed layout coexists with the per-skill symlink used for this repo's own skills. APM refuses a link as a skill destination, but the LID skills would be real directories beside the links, which the HLD's Decisions table already allows.
- **Licensing:** LID is MIT (`LICENSE` at v1.4.0), compatible with committing its files here.

**Alternative, from LID 1.4.0.** LID now ships a vendored workflow doc (`docs/lid/workflow.md`) for harnesses without a plugin system, and the instruction file's workflow section points to it. That would give cloud sessions the full workflow text without committing skills, but not the `/update-lid` or `/lid-coach` procedures.

## 3. Upgrading LID from 1.3.0 to 1.4.0

Not specific to the cloud. LID 1.4.0 was released on 2026-10-10 (`CHANGELOG.md` at tag v1.4.0); this repo records 1.3.0 in the `## LID` block. Relevant changes:
- **Inspection instruments.** A phase stop may be inspected by the user or by an inspector the user names, such as a delegated reviewer, and an inspector's findings are never applied silently. This formalizes this repo's "user override, with warning" for the tests stop and Phase 6, where the review wave inspects.
- **The `review-depth` experiment:** a declared review depth with a fork log. It overlaps the same override, so it's worth evaluating against it.
- **Delegation discipline:** a subagent dispatch must carry the phase's obligations: EARS IDs in scope, tests first, `@spec`. This bears on review waves and LID probes run by subagents.
- **A misplaced-EARS guard** in the audit, **decision docs offered rather than written by default**, and **terms defined at the lowest dominating node**.
- **The vendored workflow doc** (above), and **migration:** run `/update-lid` to refresh the instruction file's workflow section.

**Suggested path.** Upgrade in a local session where the LID plugin is installed: run the `/update-lid` walk, update the `- Version:` bullet, and re-check `lidc` 0.3.0 against 1.4.0 conventions. Upgrading first means committed skills (section 2) start at 1.4.0. Whether `lidc` 0.3.0 supports everything 1.4.0 introduces wasn't checked.

## 4. Running the repo's checks in a cloud session

**Observed.**
- **mise isn't installed** in a new cloud container, so `mise run check` (lint, typecheck, test, `lidc`, conflicts) can't run out of the box.
- **The system's uv is 0.11.32**, while `mise.toml` pins 0.13.1.
- **Without mise, `uv run --frozen pytest`** gives 294 passed, 26 failed and 13 errored. The failures are in `tests/test_check_workflow_steps.py`, which runs mise; the errors are in `tests/test_renovate_preset.py`, which needs the pinned `npm:renovate`.
- **mise installs cleanly.** With the environment's widened network policy, downloading mise 2026.10.14 (CI's version) from its GitHub release, checking it against the release's checksum file, and running `mise install` installed all eight pinned tools in about 14 seconds. `mise run check` then passed in full: lint, typecheck, all 333 tests, `lidc` with no findings, and conflicts.

**Suggested change.** Install mise and the pinned tools at session start:
- **An environment setup script** is cached when it finishes in about five minutes, but it lives in the cloud environment's settings, outside the repo.
- **A SessionStart hook in `.claude/settings.json`** is committed and versioned with the repo, but runs on every session start. A fresh install takes about 30 seconds and a warm one about 1 second.

A validated draft of the hook route is in [the setup hook proposal](2026-10-22-cloud-setup-hook-proposal.md). Either way, the network policy must allow the hosts that mise and its tools download from: GitHub releases, `nodejs.org`, npm and PyPI. Open question 4.

## 5. Commit practices in cloud sessions

**Observed.**
- **The rule:** this repo's instructions say agents don't commit; they draft `commit-message.md` and the developer commits.
- **The container is reclaimed after a period of inactivity.** The docs give no duration. Reopening restores only the conversation, so uncommitted files are presumably lost.
- **A stop hook pushes the other way.** The environment's stop hook (`~/.claude/stop-hook-git-check.sh`, supplied by the environment, not the repo) asks after every turn for untracked or uncommitted files to be committed and pushed. Following the repo's rule means ignoring the hook every turn.
- **The session's own instructions name a branch to push to** (`claude/vibrant-clarke-omew8x`), so pushing there doesn't touch `main`.

**Suggested change.** Add a cloud-session clause to the commit rule, for example: "In a cloud session, commit and push work in progress to the session's branch before handing back, so it survives the container. The developer reviews, squashes or rewrites it before it reaches `main`." Keep "agents don't commit" for local sessions. A narrower alternative is to commit only notes and drafts, never code, which keeps the slice-per-commit rule intact. Open question 3.

## 6. Status of GitHub access

| Operation | Status | Detail |
|---|---|---|
| Clone public repos | Works | Through the session's git proxy |
| Read raw files | Works | `raw.githubusercontent.com` |
| Read this repo through the API (branches, contents) | Works | GitHub tools and repo-scoped endpoints |
| Push to this repo | Works once the Claude GitHub App is installed on the repository with write access | Before that, `git push` returned 403 "Claude doesn't have GitHub access to jmbowman/agentic_development for your organization", and creating a branch through the GitHub tools returned 403 "Resource not accessible by integration" |
| Other repos' API | Blocked | Sessions are bound to their configured repositories; `add_repo` can attach more |
| Repository, code and topic search | Blocked | Same scoping rule. Not a network setting, and installing the Claude GitHub App doesn't lift it; no documented switch |
| `gh` CLI | Broken | `GH_TOKEN` is set but invalid; the proxy authenticates git operations instead |
| Search through the session's GitHub tools | Barred by session instructions | They may reach outside the configured repositories |

GitHub-wide search therefore belongs in local sessions for now. If read-only public search in cloud sessions would help, that is feedback for Claude Code's maintainers (draft in the [wrap-up](2026-10-22-session-wrap-up.md#tool-maintainer-feedback)).

## 7. Other observations

- **Memory:** cloud sessions here have no auto-memory directory (`~/.claude/projects/<slug>/memory` doesn't exist), so a lesson about the user can't be saved to memory in the cloud.
- **Transcript:** the session's transcript exists at `~/.claude/projects/<slug>/<session-id>.jsonl` while the container lives. A transcript-based tool would work in the cloud, but only before the container is reclaimed.
- **README:** it doesn't yet say what works in cloud sessions. Once sections 2, 4 and 5 are decided, a short "Using this repo from Claude Code cloud sessions" note (allowed domains, setup, commit practice) would help people deciding whether to use the repo.

## Open questions

1. **Partial routes.** Should prior-art-search treat a partial substitute (Sourcegraph for GitHub search) as "searched", "unavailable", or a new state? And should cloud runs hand GitHub search to a local session as a standard step?
2. **LID delivery.** Commit the LID skills via `apm.yml`, rely on 1.4.0's vendored workflow doc, or both? Which LID plugins?
3. **Cloud commits.** Commit and push work in progress to the session branch in cloud sessions? If so, for everything or only for notes and drafts? And should the clause name the stop hook so it stops looking like a conflict?
4. **Cloud setup.** An environment setup script (outside the repo, cached) or a committed SessionStart hook (in the repo, every start) to install mise and the pinned tools? Which network domains should the environment allow as standard?
5. **LID 1.4.0 and the stop-cadence override.** Does the project's "user override, with warning" for the tests stop and Phase 6 become a named inspector under 1.4.0, or adopt the `review-depth` experiment?
6. **Where reports and handoffs live.** This report and the wrap-up are in `docs/reports/`, a new folder chosen for this session. Keep them there, move them, or delete them once acted on?
