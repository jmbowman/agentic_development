# Prior art: an end-of-session wrap-up skill (2026-10-29)

- **Supersedes:** `docs/prior-art/2026-10-22-session-retrospective-skill.md`, which is on the branch `claude/vibrant-clarke-omew8x` and not on `main`. It ran in a cloud session that couldn't use GitHub's repository, code or topic search, so its verdict was **inconclusive**. This note runs those routes, widens the need to the full wrap-up (handoff, memory triage, cross-repo routing), and re-reads its leading candidates at their current commits.
- **Effort:** full method, because a wrap-up skill delivered through the template reaches every consumer repo and decides where each repo's durable knowledge ends up.
- **Already known:** the developer named no candidates and dismissed none. The 2026-10-22 note's candidates were inherited and re-checked (step 3).
- **Omitted:** an internal wrap-up skill that isn't public. Nothing from it was used, and the requirements below are stated in general terms.

## Decision

**Blend: build on [goagrawal-genai/wrap-up](https://github.com/goagrawal-genai/wrap-up) (MIT), plus a custom piece.**
- **Why that base:** it's the only candidate that meets every hard criterion and covers most of the need. It routes by *role*, not by file name: instruction store, memory index, entry point, decision store, reference store, pending queue and gate. It reads the project's own rules first, and "project policy always outranks this skill". It proposes before it writes, consolidates rather than appends, and refreshes the handoff document as its main deliverable.
- **The custom piece** covers the three things no candidate does together:
  1. a **memory-triage pass** over memory that already exists. It proposes moving each entry into the repo's own durable docs, following the repo's routing rules, or retiring it.
  2. a **paste-ready prompt to start the next session**.
  3. **routing to other repos**: either a self-contained message to a session rooted in the other repo (Claude Code's `SendMessage` and `ListAgents`), or a GitHub issue on that repo, filed only after the user approves the draft.
- **Borrowed ideas,** each credited below:
  - hewonjeong/retro: its numbered select-then-show-exact-text approval;
  - kdeldycke/dotfiles `wrapup-session`: loose ends re-verified against current state, labelled by action, plus routing a tool's lesson to that tool's repository;
  - RyanPenn-coder/wrap-skill: the prompt format for the next session;
  - the-c0d3r/claude-skill-memory-promotion: its memory-promotion categories;
  - ozzy-labs/skills `lessons-triage`: batch approval of the issues to file.
- **Licenses:** all of these are MIT except kdeldycke (BSD-2-Clause). Text adapted from them keeps its notice inside this Apache-2.0 repo. Nothing is taken from netresearch/retro-skill's CC-BY-SA content.
- **Compared with the 2026-10-22 note:**
  - sentimony `session-learnings`, that note's fallback, now records notes "without asking". It also edits `.gitignore` and the root instruction file during setup, so it fails the approval criterion.
  - goagrawal-genai/wrap-up and hewonjeong/retro were invisible to the cloud session's partial code index.
  - A local GitHub search closed the routes that note couldn't reach.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Capture the session's learnings: corrections, wrong assumptions, hard-won facts, decisions | Later sessions don't repeat the mistakes or re-derive the facts |
| Find what the session learned that isn't yet in memory or the repo's docs | Nothing durable is lost when the conversation ends |
| Triage existing agent memory: move what belongs in the repo (instructions, design docs, a knowledge base) out of memory, and retire what's stale | Per-tool memory doesn't travel to other agents or collaborators. Project intent belongs in the repo, where every agent loads it, and memory keeps only what's personal to the user |
| Write a prompt for starting the next session | A fresh session picks up cold from one paste |
| List loose ends | Unfinished work, pending verifications and promised follow-ups are visible, not forgotten |
| Route feedback that belongs to another repo there: a message to a session rooted in that repo, or a GitHub issue on it | A session doesn't edit repos outside its own. The owning repo's session applies the change under that repo's own instructions and permissions |
| Route each learning to the right *kind* of home: project instructions, global instructions, a skill (new or improved), memory, a design doc or knowledge-base entry, an issue, or nowhere | A lesson is applied only if it lands where the next agent loads it, or where it's enforced |

**Hard criteria:**
1. **License:** compatible with this repo's Apache-2.0, and with shipping the skill as committed files under `skills/`.
2. **Runs in Claude Code, both locally and in cloud sessions,** with no service or runtime beyond the agent's own tools.
3. **No silent writes:** every change outside the conversation is proposed and approved first.
4. **No git operations:** no staging, committing, branching or pushing. Filing a GitHub issue is allowed after the user approves the draft.
5. **Defers to the project's own rules** for where things go. Repos differ: one may route project intent to its design docs and keep only facts about the user in memory.

**Preferences:**
- self-contained Agent Skills format;
- coverage of the seven requirements above;
- maintenance and maturity.

## Candidates and matrix

Ranked shortlist:
1. **[goagrawal-genai/wrap-up](https://github.com/goagrawal-genai/wrap-up):** meets all five hard criteria (with the qualification under criterion 3, below), and has the broadest routing. Gaps: it doesn't triage existing memory, its handoff is a file rather than a paste-ready prompt, and it has nothing for other repos. It would move to **adopt** if it gained those three.
2. **[hewonjeong/retro](https://github.com/hewonjeong/retro):** has the cleanest approval flow of the group, and offers to open GitHub issues. It refuses to write the harness's own memory, so it can't triage memory. It would move up if it read memory and deferred to project routing rules.
3. **[kdeldycke/dotfiles `wrapup-session`](https://github.com/kdeldycke/dotfiles/tree/main/dotfiles/.agents/skills/wrapup-session):** has the best loose-ends pass and routes a tool's lesson to that tool's repository. It still applies small edits without asking, and commits on a repeat call, so it fails criteria 3 and 4.
4. **[RyanPenn-coder/wrap-skill](https://github.com/RyanPenn-coder/wrap-skill):** the only candidate whose closing prompt is ready to paste. It writes session records without an approval step.
5. **[the-c0d3r/claude-skill-memory-promotion](https://github.com/the-c0d3r/claude-skill-memory-promotion):** promotes memory into instructions, with approval. Its targets are fixed (`CLAUDE.md`, skills, auto-memory), it ignores repo docs, and it does nothing else from the need.
6. **[howar31/closure](https://github.com/howar31/closure):** gives every open thread one disposition: resolve, document, memorize, hand off or drop. It delegates each one to a skill that already covers it. Ideas only, because its approval wording is loose: "carry out — or propose".
7. **[ozzy-labs/skills `lessons-triage`](https://github.com/ozzy-labs/skills):** files approved lessons about skills as GitHub issues on the skills' own repo, with one batch-approval question. It's hard-wired to that repo and to its own `SessionEnd` queue.
8. **[jachai/session-guide](https://github.com/jachai/session-guide):** relays decisions between parallel Claude Code sessions over `SendMessage`. It's an orchestrator, not a wrap-up. Its message conventions are borrowed: a self-contained first line, and sessions named by title plus id.
9. **[reallyunintented/claude-continuity-kit](https://github.com/reallyunintented/claude-continuity-kit):** a handoff with a "first action next session" section, a `SessionStart` hook that surfaces it, and a checklist before writing memory. It doesn't route learnings.
10. **Native Claude Code (2.1.312):** has building blocks, but not the job.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| goagrawal-genai/wrap-up | build on | MIT (`LICENSE:1` at c347ab3) | Meets the hard criteria; role-based routing; three gaps |
| hewonjeong/retro | borrow ideas | MIT (`LICENSE:1` at d04d068) | Approval flow and issue offer; no memory |
| kdeldycke/dotfiles `wrapup-session` | borrow ideas | BSD-2-Clause (`LICENSE.md:1` at 978f231) | Loose ends; writes without asking; commits |
| RyanPenn-coder/wrap-skill | borrow ideas | MIT (`LICENSE:1` at 0f61804) | Paste-ready next-session prompt; writes records unasked |
| the-c0d3r/claude-skill-memory-promotion | borrow ideas | MIT (`LICENSE:1` at e0276b4) | Memory-promotion categories; fixed targets |
| howar31/closure | borrow ideas | MIT (`LICENSE:1` at e6a974f) | One disposition per open thread; delegates to other skills |
| ozzy-labs/skills `lessons-triage` | borrow ideas | MIT (`LICENSE:1` at db212a4) | Approved lessons become issues on the owning repo |
| jachai/session-guide | borrow ideas | MIT (`LICENSE:1` at 72b7491) | Cross-session message conventions |
| reallyunintented/claude-continuity-kit | borrow ideas | MIT (`LICENSE:1` at 32338ff) | Handoff gating condition; surfacing hook |
| benmfzen/claude-memory-triage | borrow ideas | MIT (`LICENSE:1` at cdc3a55) | Weekly propose-only memory verdicts (keep / graduate / expire / merge); a Python script using `claude -p`, not a skill |
| sentimony/agentic-workflow `session-learnings` | reject | MIT (`LICENSE:1`, `SKILL.md:7` at 612e661) | Now writes notes and setup edits without approval; excludes memory and loose ends |
| netresearch/retro-skill | reject | MIT code (`LICENSE-MIT`) and CC-BY-SA-4.0 content (`LICENSE-CC-BY-SA-4.0`) at 0b339de | Still commits with sign-off (`skills/retro/SKILL.md:92-93`) |
| robertantolin/claude-retro-skill | reject | MIT (`LICENSE:1` at 389ab8e) | Python scripts and a data folder under `~/.claude/retro/`; an "approve-always" setting |
| disableRDP/claude-skill-after-action-review | reject | MIT (`LICENSE:1` at 863d75a) | Proposes `CLAUDE.md`/`AGENTS.md` diffs only, which the user applies by hand |
| codewithmukesh/dotnet-claude-kit `wrap-up` | reject | MIT (`LICENSE:1` at 2330089) | Writes the handoff and `MEMORY.md` without approval (`SKILL.md:43-50`); depends on its `instinct-system` |
| anthropics/launch-your-agent `wrap-up` | reject | Apache-2.0 (`LICENSE:1` at d5d0ffb) | Closes out a Managed Agents tutorial build; not a session wrap-up |
| 1273984347/mem-wrap-up | reject | Apache-2.0 (`LICENSE:1` at 008f79a) | Stages files on its own (`SKILL.md:185`) |
| mikeprasad/aria-knowledge `wrapup`, jerseycheese/agent-skills `wrap-it-up`, redhat-ai-americas/memory-hub `session-close`, falshaw/claude-wrap | reject | license files present (GitHub API pointer only, not read) | Auto modes that write memory or commit; additive edits without confirmation |
| Handoff-only skills: REMvisual/claude-handoff, zltstl888/agent-session-wrap-up, wan-huiyan/session-handoff, IlyaGorsky/memory-toolkit, Mparker25/session-recap-plugin | reject | MIT or Apache-2.0 (`LICENSE:1` at 44ed590, 55b545c, b57baab, 66908bd, 51f088c) | One slice only, or bound to plugin scripts and agents |
| kyle-chalmers/next-session-prompt, Qin-C/claude-handoff-skill, danielvazdar/wrapup-skill, amr05008/agent-skills `wrap-up` | reject | no root license file (listing at 46a44ab, f00dc77, 854cea1, 2f3a16a) | Ideas only; no text may be reused |
| Registry tools: claude-handoff, handoff-agent, claude-retro (PyPI); many-retro, handoff-mcp (crates.io); @windyroad/retrospective (npm) | reject | registry metadata only | Transcript exporters, memory stores, or retros outside the session |

Matrix (✓ native, ◐ partial, ✗ unsupported, ? unverified). Line numbers are in each skill's single `SKILL.md`, at the commit in the table above.

| Criterion | goagrawal wrap-up | hewonjeong retro | kdeldycke wrapup-session | RyanPenn wrap | memory-promotion |
|---|---|---|---|---|---|
| License (hard) | ✓ MIT | ✓ MIT | ✓ BSD-2 | ✓ MIT | ✓ MIT |
| Local and cloud (hard) | ✓ one file, no scripts (repo listing) | ✓ one file | ✓ one file | ✓ one file | ✓ `allowed-tools: Read Write Edit Glob` (l.6) |
| No silent writes (hard) | ✓ "Confirm, then apply" (l.119-123); ◐ applies safe items when no user is present (l.70-72) | ✓ numbered selection, exact text shown first (l.58-72) | ✗ "Do not ask questions" (l.9); "Apply small, safe edits directly" (l.54) | ✗ saves records with no approval step (l.26-32) | ✓ "Wait for explicit confirmation" (l.107-112) |
| No git; issues after approval (hard) | ◐ offers to commit (l.136-138) | ✓ "do not commit … unless asked"; offers issues (l.77-78) | ✗ commits on a repeat call (l.19) | ✓ commits only if asked (l.38) | ✓ no shell tool (l.6) |
| Defers to project rules (hard) | ✓ roles, not paths; "project policy always outranks" (l.18-20, 40-44) | ◐ follows existing layout (l.24-31); handoff fixed to `docs/` (l.78) | ✓ narrowest home that owns it (l.39-46) | ✓ "house rules" decide (l.10-12) | ✗ fixed targets (l.86-105) |
| 1. Capture learnings | ✓ five buckets (l.73-92) | ✓ seven categories (l.39-47) | ✓ (l.35-46) | ◐ takes stock, no routing (l.16-18) | ✗ not session-based |
| 2. What's not in memory | ◐ reads memory to update, not duplicate (l.42-43) | ✗ won't use the tool's own memory (l.24) | ◐ memory "when the harness provides one" (l.44) | ✗ not found | ◐ diffs memory against `CLAUDE.md` (l.86-91) |
| 3. Memory → repo triage | ◐ memory vs. instruction store in its routing table; stale entries fixed at source (l.149-159); no pass over existing memory | ✗ (l.24) | ✗ not found | ✗ not found | ◐ memory → `CLAUDE.md` or skills only (l.86-105) |
| 4. Next-session prompt | ◐ refreshes the entry-point file (l.124-132); no paste-ready prompt | ✗ handoff doc only (l.78) | ✗ not found | ✓ "To start the next session, paste this" (l.50-55) | ✗ |
| 5. Loose ends | ◐ open loops go to the entry point (l.154); probes for stale items (l.87-91) | ◐ "Incomplete work" and Follow-up (l.46, 77) | ✓ re-verified, action-labelled (l.23-33, 56-70) | ✓ (l.34-38) | ✗ |
| 6. Cross-repo routing | ✗ listing: `grep -ciE "other repo\|another repo\|cross-repo\|SendMessage"` → 0 | ◐ offers GitHub issues on the project's tracker (l.77) | ◐ a tool's lesson goes to its repo; `Report:` label (l.41, 68) | ✗ listing, same grep → 1 (unrelated) | ✗ |
| 7. Destination breadth | ✓ seven roles, plus skill proposals (l.22-30, 156) | ◐ five groups (l.60) | ✓ (l.39-46) | ◐ the project's record places (l.26-32) | ◐ `CLAUDE.md`, skills, auto-memory (l.91-105) |

**Native Claude Code 2.1.312,** read from strings in the installed binary:
- `/recap` ("Generate a one-line session recap now"), the away summary, `/compact`, `/resume`, `/rename` and `/insights`;
- `/memory` ("Edit CLAUDE.md files and memory settings"), auto-memory and its "Dream: Memory Consolidation" pass;
- `SessionEnd` hooks;
- the `SendMessage` and `ListAgents` tools for messaging sessions rooted in other repos.

Each covers one slice: a recap, memory upkeep, or a channel to another session. None routes learnings or produces a handoff. `SendMessage` is the transport for requirement 6.

**Blends considered:**
- **goagrawal wrap-up + custom memory triage, next-session prompt and cross-repo routing (chosen).** It keeps the base's routing, consolidation and approval. The custom steps are small and separable. Its "apply safe items when no user is present" branch must be dropped, and its commit offer replaced with the developer's own commit convention, to meet criteria 3 and 4 in full.
- **hewonjeong retro + memory triage + loose ends + prompt + routing.** Its approval flow is better, but it would need a new routing model (its five fixed groups) as well as everything else. That makes it a bigger rewrite than goagrawal.
- **kdeldycke `wrapup-session` with the direct edits and the commit step removed.** It has the best loose-ends pass. But removing "Do not ask questions" changes its whole design: it's built to finish in one unattended turn.
- **Native features + a small skill.** The skill would still be the whole job; the native features supply only the cross-session transport and the memory store.

**Scenario walk:**
1. *A repo whose instructions route project intent to design docs and keep only facts about the user in memory.* goagrawal reads those hard rules first and lets them win (l.40-44). memory-promotion would put the lesson in `CLAUDE.md`, and hewonjeong in the project's instruction file. The custom triage pass must take its targets from the repo's rules, as goagrawal's roles do.
2. *The session finds feedback for another repo's code or instructions.* No candidate messages another session. kdeldycke names the tool's repository but writes the report itself, and hewonjeong offers an issue only on the current project. The custom step: find a session rooted in that repo with `ListAgents` and draft a self-contained message for approval. If no such session exists, draft a GitHub issue for that repo and file it once it's approved.
3. *Memory holds a project fact that the repo's design docs now own, plus a stale entry.* memory-promotion and claude-memory-triage propose graduate-or-expire verdicts with approval, which is the shape to borrow. goagrawal's "edit stale entries at source" covers the stale entry, but nothing in it sweeps the rest of memory.
4. *A cloud session with no auto-memory directory and no peer sessions.* goagrawal says when a role has no implementation, instead of inventing one (l.18-20). The custom steps must do the same: skip memory triage with a note, and fall back from messaging a session to drafting an issue.

## Limitations checked in source

Verified:
- goagrawal-genai/wrap-up is a single skill file with no scripts or references: *verified in source* (repo listing at c347ab3: `skills/wrap-up/SKILL.md`, plus plugin manifests, a README, `docs/design-rationale.md` and a CI workflow).
- goagrawal applies "safe, reversible" items without confirmation when no user is available (`SKILL.md:70-72`), and offers to commit (`SKILL.md:136-138`): *verified in source* at c347ab3.
- goagrawal has nothing for other repos: *listing*. `grep -ciE "other repo|another repo|cross-repo|sibling|SendMessage|other session"` on its `SKILL.md` at c347ab3 returned 0.
- hewonjeong/retro won't write "a tool's private, auto-captured memory": *verified in source* (`skills/retro/SKILL.md:24` at d04d068).
- kdeldycke `wrapup-session` still edits without asking and commits on a repeat call: *verified in source* (`dotfiles/.agents/skills/wrapup-session/SKILL.md:9,19,54` at 978f231).
- sentimony `session-learnings` now records without approval and edits tracked setup files: *verified in source* (`plugins/aw/skills/session-learnings/SKILL.md:3,135-145,155-157` at 612e661). It also excludes memory and task state (`SKILL.md:233-235`).
- netresearch/retro-skill still commits with DCO sign-off: *verified in source* (`skills/retro/SKILL.md:92-93` at 0b339de).
- RyanPenn-coder/wrap-skill's next-session prompt: *verified in source* (`wrap/SKILL.md:50-55` at 0f61804).
- ozzy-labs `lessons-triage` runs `gh issue create` only for the lessons the user selects, against its own repo: *verified in source* (`.claude/skills/lessons-triage/SKILL.md:2,28-30` at db212a4).
- Native features: *verified against the installed binary* (Claude Code 2.1.312), for the command names and descriptions quoted above. Behaviour beyond those strings is *docs only*.
- The licenses in the candidate table are read from license files at the commits listed, except the rows marked otherwise.

Could not verify:
- Licenses of the four auto-mode wrap-ups (aria-knowledge, wrap-it-up, memory-hub, claude-wrap), and of the registry tools. They were rejected on behaviour, so their licenses weren't read.
- zolat/claude-code-retros, found by web search: seen but not read. Its listing describes a `Stop` hook that writes retros automatically, which fails criterion 3 on the docs.
- aitoolnet.com: the search returned no page from that site.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code 2.1.312 binary strings (`recap`, `insights`, `memory`, `compact`, `resume`, `rename`, `awaySummary`, `Memory Consolidation`, `SessionEnd`); this session's tool list (`SendMessage`, `ListAgents`) and skills (`fewer-permission-prompts`, `skill-creator`) |
| Earlier notes and decisions | searched | `docs/prior-art/` on `main` (none on this topic). `docs/prior-art/2026-10-22-session-retrospective-skill.md` on `claude/vibrant-clarke-omew8x` (inherited, re-checked). `docs/prior-art/2026-10-17-prior-art-search-skill.md` (its source list reused) |
| GitHub repository search | searched | "session wrap-up", "session handoff", "session retrospective", "wrapup skill", "session learnings", "claude retro", "claude reflect", "end of session", "handoff skill", "session debrief", "lessons learned claude", "continuous learning claude", "next session prompt", "starter prompt session", "memory promotion", "memory triage", "memory hygiene", "close out session", "session closeout", "loose ends", "open threads session", "cross-repo agent", "session end skill", "wrap up agent", "learnings CLAUDE.md", "retro skill", "session summary skill", "resume prompt claude", "auto-memory CLAUDE.md"; round 4: "session continuity claude", "memory drift claude", "handoff SessionStart hook", "claude continuity" |
| GitHub topics | searched | `claude-code-skill`, `agent-skills` and `claude-skills`, each × wrap-up / handoff / retrospective; `claude-code` × learnings / handoff; `session-continuity` |
| GitHub code search | searched | `"next-session prompt"`, `"wrap up" SendMessage`, `"loose ends" memory CLAUDE.md`, `"gh issue create" "lessons"`, `graduate memory CLAUDE.md`, `"handoff" "starter prompt"`, all with `filename:SKILL.md` |
| GitLab and Codeberg | searched | "session handoff", "retrospective agent", "wrap up skill" (APIs): handoff-only projects on GitLab, nothing on Codeberg |
| npm | searched | "claude wrap up session", "session handoff agent", "claude retrospective skill", "agent memory promotion" |
| PyPI | searched | Known names from web search: `claude-handoff`, `handoff-agent`, `claude-retro` (JSON API) |
| crates.io | searched | "agent retrospective", "session handoff", "agent memory curation" |
| Language registries | excluded | The need names no language; the deliverable is a `SKILL.md` |
| Cross-language equivalents | excluded | No candidate is a library with ports |
| Awesome lists | searched | Web search "awesome claude code skills session handoff retrospective memory promotion list": directory listings only, no curated list on the topic |
| alternativeto.net | excluded | Not an end-user app |
| aitoolnet.com | searched | Web search "aitoolnet session handoff retrospective agent tool Claude Code": no aitoolnet page returned |
| General web search | searched | "Claude Code end of session wrap-up skill route learnings memory CLAUDE.md next session prompt", plus the two searches above |
| Hosted services | excluded | The need is a skill run inside the session; hosted memory services are one destination, not the job |
| Skill directories | searched | skills.sh API: wrap up, wrap-up, wrapup, session end, handoff, retro, retrospective, session learnings, memory promotion, loose ends, next session, closeout |
| Claude Code plugin marketplaces | searched | Anthropic's skills via skills.sh (`anthropics/launch-your-agent`, `anthropics/claude-plugins-official`); community marketplaces found through repository search (`.claude-plugin/marketplace.json` in several candidates) |
| MCP Registry | excluded | The need is a skill, not a server. The 2026-10-22 note searched it and found memory stores only |
| Anthropic's skills repo | searched | Via skills.sh's `anthropics/*` results; the 2026-10-22 note's `git ls-tree` of `anthropics/skills` found no match, and no new Anthropic wrap-up skill for coding sessions appeared |
| Awesome lists for agent skills | searched | Same as "Awesome lists" |
| GitHub topics for agent skills | searched | Same as "GitHub topics" |

## Snowball rounds

1. **Round 1** (inherited candidates, plus GitHub repository and topic search): added goagrawal wrap-up, hewonjeong retro, RyanPenn wrap, the-c0d3r memory-promotion, howar31 closure, claude-memory-triage and jachai session-guide. It also re-read kdeldycke, sentimony and netresearch at their current commits.
2. **Round 2** (vocabulary from round 1: "next-session prompt", `SendMessage`, "graduate memory", `gh issue create` lessons, closeout; code search, skills.sh, npm): added ozzy-labs `lessons-triage`. Screened and rejected the dotnet-claude-kit, Anthropic launch-your-agent, aria-knowledge, wrap-it-up, memory-hub and rootnode wrap-ups.
3. **Round 3** (web search, awesome lists, PyPI, crates.io and aitoolnet, the routes not yet searched): added claude-continuity-kit.
4. **Round 4** (seeded by claude-continuity-kit's topics and vocabulary): added no serious candidate, only compaction helpers, memory stores and more handoff variants.

The search stopped because round 4 added no serious candidate. The cap was not reached.

## Refresh trigger

Re-search before the build starts if it begins after 2027-01-29, or sooner if any of these happens:
- goagrawal-genai/wrap-up adds memory triage or cross-repo routing;
- hewonjeong/retro starts reading the harness's memory;
- Claude Code ships a native wrap-up or handoff command (check its changelog and `/help`).
