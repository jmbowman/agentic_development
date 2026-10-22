# Session wrap-up: prior-art search for a retrospective skill, run in a cloud session (2026-10-22)

This is an approximation of the planned end-of-session retrospective skill, run by hand on the session that produced it. It follows the shape the [prior-art note](../prior-art/2026-10-22-session-retrospective-skill.md) recommends:
- **Collect** lessons from what actually happened.
- **Filter** them, keeping a lesson only if it is reusable, non-obvious, stable and actionable.
- **Route** each to the narrowest home that owns it, following this repo's rules: project intent goes to the arrow, facts about the user go to memory.
- **Dedupe** against where the truth already lives.
- **Draft** each change.
- **Change nothing until approved.**

Nothing below has been applied. Each proposal carries a number for approval.

**Session scope:** a cloud session on branch `claude/vibrant-clarke-omew8x`. It ran four tasks:
- checked whether cloud sessions load skills through a symlink (they do);
- ran a full prior-art search for an end-of-session retrospective skill, twice: once under the default network policy, once after the policy was widened;
- answered questions about cloud limits, LID availability and container lifetime;
- wrote the [cloud-readiness report](2026-10-22-cloud-session-readiness.md).

No code changed.

**Evidence limits:** the whole conversation is in context; no compaction happened. No auto-memory directory exists in this session, so the check for regressions against saved feedback memories couldn't run.

## Lessons and where each should go

| # | Lesson (the moment it came from) | Destination | Proposed change |
|---|---|---|---|
| 1 | In a cloud session, GitHub search, skills.sh and Codeberg failed only after queries had been planned around them. One cheap probe of each route first would have shown which were usable (the first `search/repositories` call, and skills.sh 403) | **Skill** (prior-art-search), through LID | Add a route probe before step 5: one request per selected route, with any failure logged as unavailable plus its diagnosis (proxy refusal, session scoping, or site protection). Details in [report § 1](2026-10-22-cloud-session-readiness.md#1-prior-art-search-in-cloud-sessions) |
| 2 | Sourcegraph's stream API stands in for GitHub search, but it indexes only part of GitHub, `type:repo` matches names only, and it rejects Python's default client (three failed attempts before switching to `curl`) | **Skill** (prior-art-search `references/sources.md`), through LID | Add Sourcegraph as a fallback tactic on the two GitHub search rows, with these three caveats |
| 3 | A cloud session can't run `mise run check`: mise is absent. `uv run --frozen pytest` passes 294 tests, and 39 fail or error for lack of mise or Renovate | **Project instructions** (`AGENTS.md`), as a stopgap until a setup hook exists. Then a **hook or setup script** | Draft for `AGENTS.md` § Working rules: "**Cloud sessions:** if `mise` isn't installed, run the Python tests with `uv run --frozen pytest`, and say in the hand-back which checks didn't run (lint, typecheck, `lidc`, and the tests that need mise or Renovate)." Then a SessionStart hook or environment setup script ([report § 4](2026-10-22-cloud-session-readiness.md#4-running-the-repos-checks-in-a-cloud-session)) |
| 4 | The repo's "agents don't commit" rule and the environment's stop hook conflicted on every turn, and the container may be reclaimed with the notes uncommitted | **Project instructions** (`AGENTS.md` § Working rules, the Commits bullet), pending open question 3 of the report | Draft addition: "In a cloud session, commit and push to the session's branch before handing back, so the work survives the container. The developer reviews and squashes it before it reaches `main`." Also drafted narrower: "…commit only notes and drafts; code waits for the developer." |
| 5 | LID skills aren't available in cloud sessions; only the written rules load | **Design docs** (HLD § Skills come from two sources, and the decision on how this repo gets LID), through the LID HLD check | Proposal in [report § 2](2026-10-22-cloud-session-readiness.md#2-lid-skills-in-cloud-sessions); no text drafted until the HLD check |
| 6 | LID 1.4.0 has been out since 2026-10-10; this repo records 1.3.0 | **Project instructions** (the `## LID` block), through `/update-lid` in a local session | No hand edit: `/update-lid` rewrites the block ([report § 3](2026-10-22-cloud-session-readiness.md#3-upgrading-lid-from-130-to-140)) |
| 7 | The developer reads results in the Claude app, continues work in a local session, and wants notes committed so they can be picked up there | **Memory** (a fact about the user), to save from a local session, since this session has no memory directory | Draft memory: "Uses cloud sessions for research and drafting, then continues locally. Wants cloud work committed to the session branch for pickup, and reviews it locally before it reaches `main`." Confirm or correct before saving |
| 8 | Asked whether blocked routes were inherent or configurable, the useful answer separated a network-policy setting (fixable by the developer) from session scoping (not fixable) and a site's own bot protection, each with evidence | **Skill** (prior-art-search, the ledger's diagnosis), same change as #1 | Covered by #1 |
| 9 | The environment's stop hook asks for every untracked file to be committed and pushed, whatever the repo's own commit rules | **Feedback to Claude Code's maintainers** | Draft below |
| 10 | Cloud sessions can't run read-only GitHub-wide search, even for public repos, which forces part of a prior-art search back to a local session | **Feedback to Claude Code's maintainers** | Draft below |
| 11 | Directory symlinks in `.claude/skills/` load in cloud sessions | **Nowhere new.** The HLD's Decisions table already records the per-skill link and that cloud sessions load committed `.claude/skills/` | None. The confirmation is in this conversation and the prior-art note's first section |
| 12 | Choices made: the retrospective prior-art verdict (inconclusive, leaning to build), the blend to build, and the fallback base | **Nowhere new.** They are recorded in the prior-art note, which a future LID HLD check for the retrospective skill should read | None |
| 13 | A few status pings and harness reminders during long searches | **Nowhere.** Session-only | None |

Lessons considered and dropped:
- **The `mcpservers.org` bot challenge:** a single site, already in the prior-art note.
- **Codeberg returning nothing relevant:** a search result, not a lesson.

## Tool-maintainer feedback

Drafts to send through Claude Code's `/feedback` from a local session, if wanted. Nothing has been sent.

**A. The stop hook ignores a repo's commit policy.**
> In cloud sessions, the environment's stop hook (`stop-hook-git-check.sh`) asks after every turn for untracked or uncommitted files to be committed and pushed. Some repos deliberately have agents leave commits to the developer, so the agent has to decline on every turn. Could the hook be configurable per repo or environment, for example off, warn once, or notes only? Or could it defer to a setting the repo commits?

**B. Read-only public GitHub search in cloud sessions.**
> Cloud sessions are scoped to their configured repositories, so `search/repositories`, `search/code` and `github.com/topics` are refused, even for public data. Cloning public repos and reading raw files work. Research tasks such as surveying existing tools need GitHub-wide search, and today they have to finish in a local session. Could read-only public search be allowed, or offered as an environment option?

## Left to do

Ordered so the list can be worked top to bottom from a fresh local session.

- Fetch `claude/vibrant-clarke-omew8x` locally. It is pushed; the first push failed until the Claude GitHub App was given write access to the repository.
- `Review:` approve, edit or reject proposals 1-10 above.
- `Review:` answer the report's [open questions](2026-10-22-cloud-session-readiness.md#open-questions), especially #3 on cloud commits and #2 on LID delivery.
- `Review:` save memory #7 from a local session, after confirming its wording.
- Re-run GitHub repository, code and topic search for the retrospective skill from a local session with `gh` authenticated. The queries are in the prior-art note's coverage ledger, and the verdict can move from inconclusive to build only after this. The skills most likely to be found are those not indexed by Sourcegraph.
- `Implement:` upgrade LID to 1.4.0 with `/update-lid` in a local session where the plugin is installed. Then check `lidc` 0.3.0 against 1.4.0.
- `Implement:` the LID HLD check for delivering LID skills to cloud sessions (report § 2), then the cascade.
- `Implement:` the prior-art-search cloud changes (lessons 1 and 2, report § 1) through the LID cascade: design doc, `PRIOR-SRCH-*` specs, an offline eval, then `references/sources.md`.
- `Implement:` cloud setup for the repo's checks: a SessionStart hook or an environment setup script that installs mise (report § 4).
- `Implement:` start the retrospective skill: run the LID HLD check with the prior-art note as input. This wrap-up is a worked example of the target output.
- `Report:` send feedback A and B, if wanted.

## Not carried over

- **Scratch clones** of about 50 candidate repos in this session's scratchpad. They are reproducible from the commits cited in the prior-art note, and nothing in them is needed.
- **The environment's network allowlist change** (skills.sh, Codeberg, mcpservers.org) lives in the cloud environment's settings, not the repo, and persists for future sessions in that environment.
