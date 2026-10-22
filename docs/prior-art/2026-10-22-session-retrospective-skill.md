# Prior art: end-of-session retrospective that routes lessons to where they get applied (2026-10-22)

- **Effort:** full method, because a skill delivered through the template reaches every consumer repo and shapes where each repo's durable knowledge ends up. That is costly to reverse, and the developer asked for the full procedure.
- **Already known:** not asked. The request arrived as a single prompt in a cloud session, so the run was treated as non-interactive. The request named search phrasings but no known or dismissed candidates.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Runs at the end of any session, including one that changed nothing | Lessons from exploration, diagnosis and research sessions are captured too, not only from sessions that shipped code |
| Looks back over the session for corrections, wrong assumptions, hard-won facts, what worked or wasted time, friction, and decisions | Future sessions avoid repeating the same mistakes and re-deriving the same facts |
| Proposes a destination for each lesson: project instructions, global instructions, agent memory, design docs, a skill, a hook or permission, tool-maintainer feedback, or nowhere | A lesson gets *applied* only if it lands where the next agent will load it, or where it is enforced. Picking the destination is the core of the job, not an add-on |
| Drafts the changes, and the user approves them | No silent edits to instructions, memory or settings |
| Captures unfinished work (open questions, pending verifications, follow-ups in other repos) | A fresh session can pick up cold |
| Defers to the project's own instruction file for where things go | Repos differ. This one, for example, routes project intent to the design arrow and keeps only facts about the user in memory |
| No git operations | Committing is handled separately, before the retrospective runs |

**Hard criteria:**
1. A license compatible with this repo's Apache-2.0, and with shipping the skill committed under `skills/`, since cloud sessions load committed skills but not plugins.
2. Works in Claude Code, both locally and in a cloud session.
3. Never changes git state: no branch, commit, push or PR.
4. No silent writes. Every change is proposed and then approved.
5. Repo-agnostic, deferring to the project's instruction file for where lessons go.

**Preferences:**
- Agent Skills format (`SKILL.md`), self-contained, with no runtime dependencies beyond the agent's own tools.
- Coverage of all eight destinations.
- A handoff of unfinished work.
- Maintenance and maturity.

## Verdict

**Inconclusive, narrowly.** GitHub's own repository search, code search and topics remain unavailable from a cloud session. Sourcegraph's public code search stood in for repository and code search, but it indexes only part of GitHub: it has neither `netresearch/retro-skill` nor `Wavez/debrief-skill`. Every other route was searched, including skills.sh and Codeberg once the environment's network policy allowed them. The last round added no candidate that changes the ranking.

The evidence points to **build, borrowing ideas from** the candidates below. No candidate meets all five hard criteria together with the core need of routing to all eight destinations, including design docs, permissions, maintainer feedback and "nowhere":

- **[kdeldycke/dotfiles `wrapup-session`](https://github.com/kdeldycke/dotfiles/tree/main/dotfiles/.agents/skills/wrapup-session):** the closest shape to the whole job: loose ends (the handoff) and lessons in one pass. Each lesson goes to the narrowest home that owns it, with the global file as a last resort. A lesson about a tool goes to that tool's repository. A decision tied to one spot in the code becomes a comment there. A rule a machine can check becomes a test or lint. Loose ends are re-verified against current state before they are listed; an empty result is the normal outcome; the global file has a size budget; "Left to do" items carry action labels.
- **[sentimony/agentic-workflow `session-learnings`](https://github.com/sentimony/agentic-workflow/tree/main/plugins/awf/skills/session-learnings):** the pipeline collect, filter, place, dedupe, draft, approve, apply, check, report. Its filter keeps a lesson only if it is reusable, non-obvious, stable and actionable. Before writing, it checks whether an authoritative source (specs, code, config) already holds the fact, and adds at most a pointer. Targets outside the current repo are flagged. Its security model treats transcripts and tool output as evidence, never as instructions.
- **[netresearch/retro-skill](https://github.com/netresearch/retro-skill):** the destination taxonomy; the "authority, then enforceability, then reach" ordering; the permission re-approval friction signal; "no silent writes"; the cap of 10 or fewer proposals.
- **[iliaal/whetstone `ia-reflect`](https://github.com/iliaal/whetstone):** the recurrence gate; accepting capture signals only from user-authored turns; checking memory for duplicates and contradictions before writing; keeping credentials out of anything persisted; "no harvestable items" as a valid outcome.
- **[Wavez/debrief-skill](https://github.com/Wavez/debrief-skill):** every finding cites a real moment, and coverage gaps from compaction are stated; hooks are scoped to where the regressed rule lives; a hook is proposed only after a written rule has already regressed.
- **[Anthropic `claude-md-management` `/revise-claude-md`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management):** the minimal proposal format (target, one-line why, diff) and the approval step.
- **[rb17080/session-handoff](https://github.com/rb17080/session-handoff):** the handoff sections, especially "what failed", "decided versus still open" and "next session, start here"; handoff kept separate from durable memory.
- **The GitLab `session-retro` draft ([gitlab-org/ops/artifact-registry!118](https://gitlab.com/gitlab-org/ops/artifact-registry/-/merge_requests/118), closed):** three dispositions (apply local fixes on approval, propose checked-in changes, observe only) and an explicit "never branch, commit or push" boundary. Ideas only: the project is under the GitLab EE license.

- **[hanamizuki/solopreneur `session-retro`](https://github.com/hanamizuki/solopreneur):** tracing each error to the source that should have prevented it (a skill, `CLAUDE.md`, memory, tool behavior, or nothing). It sorts the cause into four kinds, each with its own remedy: the source is unclear, the source is missing, the agent drifted from a clear source, or it was a one-off slip.

If a build is rejected, the fallback is to **build on sentimony `session-learnings`** (MIT). It meets the hard criteria, with one qualification: it commits only when the user asks. Its proposal and approval pipeline is the reusable part. Its "When not to use" section deliberately excludes memory, skill feedback and handoffs. Adding those, plus design docs, permissions and maintainer feedback, is still most of the job. Wavez/debrief-skill (MIT) is the second fallback.

To close the audit fully, re-run GitHub repository, code and topic search from a local session with `gh` authenticated. The queries are listed in the ledger.

## Candidates and matrix

Ranked shortlist:
1. **kdeldycke `wrapup-session`:** the closest to the whole job, covering loose ends plus routing to instructions, skills, code comments, memory, checks, a tool's own repository, and the global file. It fails two hard criteria. Small edits are applied directly, with no approval, and the skill says "Do not ask questions". A repeat invocation commits. It would move up with an approval gate and no commit step.
2. **netresearch/retro-skill:** the richest taxonomy, with a done gate and evals. It fails three hard criteria. It opens branches, commits and PRs for skill updates; it hard-codes `AGENTS.md` as the only project rule store and never writes project memory; and it needs `uv`, `jq` and `gh`/`glab`, plus three sibling Netresearch skills for half its destinations. It would move up if a mode limited to proposals existed and routing deferred to the project's own rules.
3. **sentimony `session-learnings`:** meets the hard criteria, with commits only on request. Its pipeline and security model are the best of the group. It routes only to instruction files: project, nested, global, and other repos'. It would move up if it routed to memory, skills, design docs and settings, and added a handoff.
4. **Wavez/debrief-skill:** meets every hard criterion as a single file. Its destinations stop at memory, project and global `CLAUDE.md`, a script or skill asset, and hooks; there is no handoff. It would move up with a richer routing table.
5. **whetstone `ia-reflect`:** the strongest evidence discipline of any candidate. It is tied to Claude Code memory paths, and its routing table covers remedy kinds rather than destinations. It would move up if it shipped outside its plugin with routing to destinations.
6. **hanamizuki `session-retro`:** traces each error to its source and sorts the cause, with approval; routes to memory, skills, agent definitions and `CLAUDE.md`. No handoff, design docs or settings.
7. **Anthropic `/revise-claude-md`:** official and minimal, with approval, but it only writes `CLAUDE.md` and `.claude.local.md`, and it is a plugin command rather than a skill.
8. **BayramAnnakov/claude-reflect:** capture hooks feed a queue that `/reflect` applies to many instruction targets. It is heavy (a 1,536-line command, Python hooks on four events) and centred on `CLAUDE.md`, with no design docs or handoff.
9. **The handoff family (rb17080/session-handoff, softaworks `session-handoff`, mattpocock `handoff`, rohitg00/pro-workflow `wrap-up`):** covers only the secondary job. `wrap-up` runs git and asks whether to commit.
10. **Native Claude Code features:** cover parts of the job, each a different part. `/insights` reports across sessions; auto memory and its background consolidation ("dream") keep memory tidy; the `fewer-permission-prompts` skill turns repeated read-only prompts into an allowlist.
11. **Others** (table below): either tied to their own framework or store, or covering only reporting or capture.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [kdeldycke/dotfiles `wrapup-session`](https://github.com/kdeldycke/dotfiles) | borrow ideas | BSD-2-Clause (`LICENSE.md` at c4af098) | Closest shape; applies edits without approval and commits on a repeat call |
| [sentimony/agentic-workflow `session-learnings`](https://github.com/sentimony/agentic-workflow) | build on (fallback) | MIT (`LICENSE` at 132a003; `SKILL.md:6`) | Meets the hard criteria; instruction files only |
| [hanamizuki/solopreneur `session-retro`](https://github.com/hanamizuki/solopreneur) | borrow ideas | MIT (`LICENSE` at 7bccfe3) | Traces errors to their source and sorts the cause; partial routing |
| [netresearch/retro-skill](https://github.com/netresearch/retro-skill) | borrow ideas | MIT for code (`LICENSE-MIT`) and CC-BY-SA-4.0 for content (`LICENSE-CC-BY-SA-4.0`; `SKILL.md:2,6`) at 15241e93 | Best taxonomy; fails "no git" and "repo-agnostic". Share-alike content means ideas only, no copied text |
| [Wavez/debrief-skill](https://github.com/Wavez/debrief-skill) | build on (second fallback) | MIT (`LICENSE` at 5e53eff5) | Meets every hard criterion; covers few destinations; no handoff |
| [iliaal/whetstone `ia-reflect`](https://github.com/iliaal/whetstone) | borrow ideas | MIT (`LICENSE` at 60f598c1) | Evidence and capture discipline; plugin-bound |
| [Anthropic claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) | borrow ideas | Apache-2.0 (`plugins/claude-md-management/LICENSE` at af59ee3a) | `CLAUDE.md` only; plugin command |
| [BayramAnnakov/claude-reflect](https://github.com/BayramAnnakov/claude-reflect) | borrow ideas | MIT (`LICENSE` at b6c42326) | Correction capture by hook and a target table; heavy, `CLAUDE.md`-centred |
| [rb17080/session-handoff](https://github.com/rb17080/session-handoff) | borrow ideas | MIT (`LICENSE` at cf6ffe51) | Handoff structure; writes `.gitignore` and reads git |
| [rohitg00/pro-workflow `wrap-up`](https://github.com/rohitg00/pro-workflow) | reject | MIT (`package.json` at 86d5f277; no license file) | Release-style checklist; asks to commit |
| [Bitwarden `retrospecting`](https://github.com/bitwarden/ai-plugins/tree/main/plugins/claude-retrospective) | reject | Bitwarden License Agreement (`LICENSE.txt` at 30f420b4), not open source | Reporting from git history and log metrics; no routing to destinations |
| [AndreJorgeLopes/devflow `reflect-session`](https://github.com/AndreJorgeLopes/devflow) | reject | MIT (`LICENSE` at bd4b70c5) | Writes only to its Hindsight memory store |
| [majiayu000/claude-arsenal `codex-retrospective`](https://github.com/majiayu000/claude-arsenal) | borrow ideas | MIT (`LICENSE` at ed52af74) | Codex-oriented, multi-day; evidence inventory and a "no high-confidence change" exit |
| [mattpocock/skills `retro`](https://github.com/mattpocock/skills) | borrow ideas | MIT (`LICENSE` at 5beb35b0) | Prefer checks over prose, and pointers over always-loaded text; depends on its `writing-for-agents` skill |
| [windyroad/agent-plugins `run-retro`](https://github.com/windyroad/agent-plugins) | reject | MIT (`packages/retrospective/package.json` at e206da4; no license file) | Deletes briefing entries silently; tied to its own briefing and ticket framework |
| [florianbuetow/claude-code `retrospective`](https://github.com/florianbuetow/claude-code) | reject | MIT (`LICENSE` at 62bab87) | Analysis of usage logs across sessions; no approval and routing step |
| [blader/claudeception](https://github.com/blader/claude-code-continuous-learning-skill) | reject | MIT (`LICENSE` at 62dbb91) | Turns lessons into new skills only |
| [ECC continuous-learning v1/v2](https://github.com/affaan-m/everything-claude-code) | reject | MIT (`LICENSE` at 90606c83) | Stop hook or observer hooks writing "instincts" to its own store |
| [melodykoh/learning-loop-skill](https://github.com/melodykoh/learning-loop-skill) | reject | MIT (`LICENSE` at eb54130) | A 1,963-line skill with mandatory subagent fan-out |
| [corca-ai/claude-plugins `cwf:retro`](https://github.com/corca-ai/claude-plugins) | reject | MIT (`LICENSE` at 08983e0) | Bound to the CWF workflow's live-state scripts |
| GitLab `session-retro` draft | borrow ideas | GitLab EE License (`LICENSE` on `main`) | Repo-specific; closed draft |
| [Cursor `continual-learning`, `reflect` (pstack)](https://github.com/cursor/plugins) | reject | MIT (`continual-learning/LICENSE`, `harness/pstack/claude-code/LICENSE` at eb4db2b) | `continual-learning` updates only `AGENTS.md` through a Cursor subagent and Stop hook; `reflect` routes only to skills, with mandatory subagents. Its "move anything a check could enforce to backlog" step is worth noting |
| [Cursor `run-learning-retrospective`](https://github.com/cursor/plugins) | reject | MIT (at eb4db2b) | About learners' study plans, not agent sessions |
| [garrytan/gstack `retro`](https://github.com/garrytan/gstack) | reject | MIT (`LICENSE` at 514fbfd) | Weekly engineering retrospective from git activity |
| Skills that update only instruction files or memory: meain `retrospect`, ulpi-io `update-claude-learnings`, dyad `remember-learnings`, lgbarn `lessons-learned`, griffinhilly `retro` | reject | MIT where a license file exists (meain, lgbarn, griffinhilly, dyad's mixed `LICENSE` at 3e336e2, 0d07a8c, e5bf989, 46d861c); ulpi-io has no root license | `CLAUDE.md`/`AGENTS.md`, or feedback memory, only |
| [jwilger/agent-skills `session-reflection`](https://github.com/jwilger/agent-skills) | reject | CC0-1.0 (`LICENSE` at e2f5e19) | Bound to its own team layout (`WORKING_STATE.md`, coordinator instructions) |
| [haddock-development/claude-reflect-system](https://github.com/haddock-development/claude-reflect-system), [pskoett/self-improving-agent](https://github.com/pskoett/self-improving-agent), [minicoohei `session-retrospective`](https://github.com/minicoohei/ai-agent-camp) | reject | no license file in a root listing (41d03d0, 94fe734, 048ba4c) | Auto-commits skill edits; continuous hook logging; files GitHub issues. No license, so not even ideas can be taken verbatim |
| [gupsammy/Claudest `extract-learnings`](https://github.com/gupsammy/Claudest), [kdlbs/kandev `harness-improvement`](https://github.com/kdlbs/kandev), diegosouzapw `session-retrospective` | reject | no license file (be26c03, a6b3c300); kandev `LICENSE` at 5aa31be | Memory-layer maintenance with subagents; repo-specific; `CLAUDE.md` and skills only |
| Neolab `reflect`, 1c-ai-development-kit `session-retro` | reject | GPL-3.0 (`LICENSE` at 23e2428); AGPL-3.0 (`LICENSE` at 92d389e) | Copyleft; self-critique of output, and a 27-line note respectively |
| Handoff skills: [softaworks `session-handoff`](https://github.com/softaworks/agent-toolkit), [mattpocock `handoff`](https://github.com/mattpocock/skills), paulrberg `wrap-up`, terrylica `session-debrief` | borrow ideas (handoff only) | MIT (`LICENSE` at 3027f20, 5beb35b, f4fde3f, af438b0) | Secondary job only |
| claude-retro, ccretro, claude-doctor, openloops, chsum (npm/PyPI) | reject | MIT where listed (npm metadata, not read from license files) | Transcript miners that draft rules or digests from past logs, not end-of-session routing |
| MCP memory servers (registry search "memory") | reject | n/a | A memory store is one destination, not the routing job |
| Native: `/insights`, auto memory and consolidation, `fewer-permission-prompts` | partial (native) | Claude Code 2.1.307 | Each covers one slice; none routes lessons |

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified):

| Criterion | retro-skill | debrief | ia-reflect | revise-claude-md | claude-reflect | session-handoff |
|---|---|---|---|---|---|---|
| License (hard) | ◐ CC-BY-SA content: share-alike on adaptations | ✓ MIT | ✓ MIT | ✓ Apache-2.0 | ✓ MIT | ✓ MIT |
| Claude Code, local and cloud (hard) | ◐ needs `uv`, `jq`, `gh`/`glab` (`SKILL.md:7`) | ✓ one file, no scripts | ✓ | ◐ plugin command; cloud sessions don't install plugins | ◐ plugin hooks in Python | ✓ |
| No git changes (hard) | ✗ commits, signs off and opens PRs (`patch-workflow.md:85,173`) | ✓ | ✓ | ✓ (`allowed-tools: Read, Edit, Glob`) | ? | ✗ edits `.gitignore` (`SKILL.md` "The file is always ignored") |
| No silent writes (hard) | ✓ (`SKILL.md:25-26`) | ✓ (`SKILL.md:155-157`) | ✓ (`SKILL.md:18,40`) | ✓ (`revise-claude-md.md:52-54`) | ✓ review step, `--dry-run` | n/a (writes the handoff by design) |
| Repo-agnostic, defers to project rules (hard) | ✗ "`AGENTS.md` is the single project rule store" (`destination-taxonomy.md:58-59`); "never project-local memory" (`SKILL.md:74`) | ◐ "check each one's own conventions" (`SKILL.md:19-20`) | ◐ uses the configured memory location (`SKILL.md:76`) | ✗ `CLAUDE.md` only | ◐ discovers many targets | ◐ project voice only |
| Project and global instructions | ✓ | ✓ | ◐ | ◐ project only | ✓ | ✗ |
| Agent memory | ✗ (forbids project memory) | ✓ | ✓ | ✗ | ◐ low-confidence items only | ◐ points to `MEMORY.md` |
| Design docs | ◐ `canonical-source` (upstream owner), no design-doc row: not found by `grep -n -i "design doc\|ADR\|decision" references/destination-taxonomy.md` | ✗ not found | ✗ not found | ✗ | ◐ "referenced docs" | ✗ |
| Skill (new or improved) | ✓ PR to the source repo | ◐ "script or skill asset" | ✓ skill audit | ✗ | ◐ `commands/*.md` | ✗ |
| Hook or permission | ✓ `harness-artefact`; A18 "Same permission prompt approved ≥3×" (`friction-catalog.md:62`) | ◐ hook only, after a regression (`suggested-improvements.md:13-23`) | ◐ "deterministic check, hook, or gate" (`capture-and-routing.md:16`) | ✗ | ✗ | ✗ |
| Tool-maintainer feedback | ◐ `canonical-source` PR | ✗ | ✗ | ✗ | ✗ | ✗ |
| "Nowhere" outcome | ✓ no-action evals | ✓ (`SKILL.md:153`) | ✓ (`SKILL.md:52`) | ◐ "avoid one-off fixes" | ? | n/a |
| Handoff of unfinished work | ◐ the done gate's "Questions" row (`done-mode.md:45`); no handoff file | ✗ | ✗ | ✗ | ✗ | ✓ |
| Self-contained `SKILL.md` | ✗ 11 references, 15 scripts, 3 sibling skills | ✓ | ✓ plus one reference | ✗ command | ✗ | ✓ |

The two candidates added once skills.sh and Sourcegraph became reachable:

| Criterion | wrapup-session (c4af098) | session-learnings (132a003) |
|---|---|---|
| License (hard) | ✓ BSD-2-Clause | ✓ MIT |
| Claude Code, local and cloud (hard) | ✓ one file | ✓ one file |
| No git changes (hard) | ✗ "a repeat one does" commit (`SKILL.md:18`) | ◐ stages or commits only "when the user asks" (`SKILL.md:83-84`) |
| No silent writes (hard) | ✗ "Apply small, safe edits directly" (`SKILL.md:53`); "Do not ask questions" (`SKILL.md:9`) | ✓ "Edit nothing before the user approves" (`SKILL.md:75-76`) |
| Repo-agnostic, defers to project rules (hard) | ✓ narrowest home that owns it (`SKILL.md:38-45`) | ✓ lists the writable instruction surfaces, then narrowest scope (`SKILL.md:37-46`) |
| Project and global instructions | ✓ | ✓ |
| Agent memory | ✓ "when the harness provides one" (`SKILL.md:43`) | ✗ excluded (`SKILL.md:96-97`) |
| Design docs | ◐ code comments; existing docs count as "already recorded" (`SKILL.md:36,42`) | ◐ specs as the authoritative place to point to (`SKILL.md:52-56`) |
| Skill (new or improved) | ✓ (`SKILL.md:41`) | ✗ excluded (`SKILL.md:92-93`) |
| Hook or permission | ◐ "a test or lint" (`SKILL.md:44`); no settings | ✗ not found |
| Tool-maintainer feedback | ✓ lesson goes to the tool's repository; `Report:` label (`SKILL.md:40,66`) | ◐ other repositories' instruction files (`SKILL.md:40-41`) |
| "Nowhere" outcome | ✓ (`SKILL.md:49`) | ✓ (`SKILL.md:77`) |
| Handoff of unfinished work | ✓ verified loose ends, "Left to do" (`SKILL.md:22-32,61-69`) | ✗ "not … a pending item" (`SKILL.md:31`) |
| Self-contained `SKILL.md` | ✓ | ✓ |

**Blends considered.**
- *sentimony's pipeline and security model + kdeldycke's routing order and loose-ends section + a custom routing table:* meets the hard criteria once kdeldycke's direct edits and commits are removed. kdeldycke's text is BSD-2-Clause, so adapted text keeps its notice. This is the shape the build should take.
- *debrief + session-handoff + a custom routing table:* meets the hard criteria, but the custom table is the core of the job, so it amounts to building with debrief as a skeleton.
- *retro-skill with its git-writing destinations removed:* any adaptation of its CC-BY-SA content must stay CC-BY-SA, which mixes licenses inside an Apache-2.0 skills package, and its hard-coded store choices would need rewriting.
- *Native plus a small skill:* `/insights` and auto memory don't run in-session or route, so the skill would still be the whole job.

**Scenario walk.**
1. *A cloud session that changed nothing (exploration or diagnosis).* Its transcript exists at `~/.claude/projects/<slug>/<session-id>.jsonl`, but no auto-memory directory exists (listing: `ls ~/.claude/projects/<slug>/memory` returned "No such file or directory"). retro-skill's pre-pass needs `uv` and `gh`. debrief and the build work from the live conversation alone. A built skill must treat memory as possibly unavailable and say so.
2. *A repo whose instructions route intent to design docs and keep only facts about the user in memory, such as this one.* retro-skill would write project rules to `AGENTS.md` and refuse memory. debrief would suggest `CLAUDE.md`. Only a skill that reads the project's routing rules first handles it.
3. *The same permission prompt is approved repeatedly.* retro-skill detects it (A18). Natively, `fewer-permission-prompts` builds the allowlist. A built skill should route this lesson to that skill or to settings, not to prose.
4. *Follow-ups in another repo plus a pending verification.* kdeldycke's loose-ends pass and the handoff family capture this; rb17080's version edits `.gitignore`. A built skill should re-verify each item against current state, as kdeldycke does, then draft the handoff and let the user choose where it lives.

## Limitations checked in source

- retro-skill materializes skill updates as commits and PRs: *verified in source* (`skills/retro/references/patch-workflow.md:85,173` at 15241e93).
- retro-skill forbids project `CLAUDE.md` and project-local memory: *verified in source* (`destination-taxonomy.md:44-59`, `SKILL.md:74` at 15241e93).
- retro-skill needs external tools: *verified in source* (`SKILL.md:7,12` at 15241e93).
- retro-skill has no handoff output: *listing*. `grep -rn -i -E "handoff|next session|pending verification" skills/retro/references/*.md` at 15241e93 returned nothing.
- The retro-skill SessionEnd hook only prints a reminder: *verified in source* (`hooks/session-end.json:3,19` at 15241e93).
- debrief's destinations: *verified in source* (`references/suggested-improvements.md:7-23` at 5e53eff5). It has no permission destination: *listing*, `grep -n -i "permission\|settings" skills/debrief/SKILL.md` returned nothing.
- ia-reflect is tied to Claude Code memory paths: *verified in source* (`SKILL.md:76` at 60f598c1).
- `/revise-claude-md` writes only `CLAUDE.md` and `.claude.local.md`: *verified in source* (`commands/revise-claude-md.md:3,23-25` at af59ee3a).
- windyroad's `run-retro` deletes entries silently: *verified in source* (`packages/retrospective/skills/run-retro/SKILL.md`, "Delete handling — silent", at e206da4).
- pro-workflow's `wrap-up` asks to commit: *verified in source* (`skills/wrap-up/SKILL.md`, Guardrails, at 86d5f277).
- Native features, read from strings in the installed Claude Code 2.1.307 binary:
  - `/insights`: "Generate a report analyzing your Claude Code sessions", user-invoked only (`disableModelInvocation`);
  - `/memory`: "Edit CLAUDE.md files and memory settings";
  - an `autoDream` "Memory Consolidation" pass, gated on session count and elapsed time.
  
  These are *verified against the installed binary*. Behaviour beyond those strings is *docs only*.

Verified:
- The licenses in the candidate table, read from license files at the commits listed, except where the table says "metadata".
- retro-skill's content is CC-BY-SA-4.0 (`SKILL.md:2`, `destination-taxonomy.md:1`); the README states code is MIT and content is CC-BY-SA.

- kdeldycke `wrapup-session` edits directly without asking, and commits on a repeat invocation: *verified in source* (`dotfiles/.agents/skills/wrapup-session/SKILL.md:9,18,53` at c4af098).
- sentimony `session-learnings` excludes memory, skill feedback and pending items: *verified in source* (`plugins/awf/skills/session-learnings/SKILL.md:31,91-97` at 132a003).
- Sourcegraph's index is partial: *listing*. `repo:^github\.com/netresearch/retro-skill$ type:repo` and the same query for `Wavez/debrief-skill` returned 0 matches on 2026-10-22, though both repositories clone.

Could not verify:
- GitHub's own repository search, code search and topic pages. The API and `github.com/search` both returned "This GitHub API path is not available: sessions are bound to their configured repositories"; `github.com/topics/claude-skills` returned 403. This is a scoping rule on the cloud session's GitHub access, not a network setting.
- grep.app code search: HTTP 429 (rate limited), twice.
- mcpservers.org (the openshift `learn-session` listing): the site serves a Cloudflare bot challenge (403) even with the domain allowed.
- Skills on skills.sh whose path could not be resolved by name in their repos: eins78 `bye`, agglayer `session-retro`, gjkim42 `pre-session-end`, paulrberg `debrief`, xpepper `session-wrap-up` (all under 30 installs except `pre-session-end`).
- claude-reflect's git behaviour, and the full text of the 1,536-line `reflect.md`.
- Licenses of the npm and PyPI transcript miners, which were not read from license files.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code 2.1.307 binary strings (`insights`, `autoMemory`, `autoDream`, `SessionEnd`, `PreCompact`); this session's skill list (`fewer-permission-prompts`, `update-config`, `skill-creator`) |
| Earlier notes and decisions | searched | `docs/prior-art/` (2 notes, neither on this topic); `docs/` grep for retrospect, reflect, lesson, handoff, wrap-up, memory (only the `CLAUDE.md`/`AGENTS.md` "Memory vs. intent" rule) |
| GitHub repository search | unavailable (partly substituted) | GitHub's API and `github.com/search` are limited to the session's configured repos; retried once. Substitute: Sourcegraph `type:repo` name search for "claude retrospective", "session retrospective agent", "claude reflect", "session handoff claude", "self-improving agent skill", "claude learnings" (0 hits: repo search matches names only), then name patterns `retro-skill`, `retrospective-skill`, `session-retro`, `claude-retro`, `claude-reflect`, `session-handoff`, `learning-loop`, `self-improving-agent`. Partial index: see Limitations |
| GitLab | searched | "retrospective agent", "claude retro", "session reflection", "agent learnings" (API); the `session-retro` draft MR, found by web search, read through the API |
| Codeberg | searched | "retrospective", "claude skill", "agent learnings", "session handoff", "reflection" (API, after the network policy was widened): nothing relevant |
| GitHub topics | unavailable | `github.com/topics/...` returns 403 from the session's GitHub scoping; Sourcegraph has no topic filter. Topic-tagged skills were reached through skills.sh |
| GitHub code search | unavailable (partly substituted) | Substitute: Sourcegraph content search over `file:SKILL.md$`: skill names matching `retro\|reflect\|debrief\|lessons\|learnings\|wrap-?up` together with `CLAUDE.md`; "permission prompt\|allowlist" with retrospective; "end of" session lessons memory; handoff "open questions" "next session"; "narrowest home\|scope" lesson; global instructions + learnings + approval; design doc\|ADR + memory + hook. grep.app was rate-limited (429) |
| npm | searched | "keywords:claude-code retrospective", "claude session learnings", "agent skill reflect session", "claude-doctor" |
| PyPI | searched | Web search: `site:pypi.org claude code session retrospective learnings transcript CLAUDE.md` |
| crates.io | searched | "agent reflection", "agent retrospective", "llm reflection memory" |
| Language registries | excluded | The need names no language; the deliverable is a `SKILL.md` |
| Cross-language equivalents | excluded | No candidate is a library with ports; Codex counterparts (`codex-retrospective`) were reached through web search |
| Awesome lists | searched | "awesome claude skills retrospective reflection memory consolidation", "awesome-claude-code list retrospective learning skills hooks session lessons" |
| alternativeto.net | excluded | Not an end-user app |
| General web search | searched | 13 queries across rounds: session retrospective `CLAUDE.md`; `/reflect` corrections; self-improving agent; handoff and wrap-up; continuous-learning Stop hook; `/insights` and auto memory; routing lessons to memory vs. instructions; Codex `AGENTS.md` retrospective; friction and permission-prompt retro; candidate comparisons; Windy Road; routing to destinations (extended mode); claudeception alternatives and handoff |
| Hosted services | excluded | The need is a skill run inside the session, with no external service. Hosted memory services appear only as MCP registry hits |
| Skill directories | searched | skills.sh API (after the network policy was widened): retrospective, retro, reflect, reflection, lessons, learnings, session handoff, handoff, wrap-up, debrief, self-improving, continuous learning, postmortem; then wrapup, session-learnings, session-retro, instruction learnings, bye, end session. Listings from claudepluginhub, skills.cat, tessl, smithery, skillselion and openskillindex via web search results |
| Claude Code plugin marketplaces | searched | `anthropics/claude-plugins-official` read (`claude-md-management`); community marketplaces via web search |
| MCP Registry | searched | "retrospective", "reflect", "learnings", "memory" |
| Anthropic's skills repo | searched | `git ls-tree` of `anthropics/skills` at HEAD, grep for `retro\|reflect\|learn\|memory\|handoff\|wrap` in `SKILL.md` paths: no match |
| Awesome lists for agent skills | searched | Same two queries as "Awesome lists"; no list page surfaced, only directory entries |
| GitHub topics for agent skills | unavailable | Same as "GitHub topics" |

## Snowball rounds

1. **Round 1 (web, npm, GitLab, crates, MCP registry, plugin marketplace).** Added retro-skill, debrief, ia-reflect, claude-md-management, claude-reflect, Bitwarden `retrospecting`, devflow `reflect-session`, codex-retrospective, Pocock `retro`, ECC continuous-learning, session-handoff, pro-workflow `wrap-up`, and the npm transcript miners.
2. **Round 2 (seeded by retro-skill's and debrief's comparisons, plus npm keyword hits).** Added windyroad `run-retro`, florianbuetow `retrospective`, claudeception, claude-retro, and the GitLab `session-retro` draft.
3. **Round 3 (vocabulary: "route each learning destination", "handoff open questions cold start"; plus PyPI as a route not yet searched).** Added learning-loop, corca `cwf:retro`, openloops and chsum. None changed the ranking or met more hard criteria than debrief.

4. **Round 4 (skills.sh, Codeberg and Sourcegraph, once reachable).** Added kdeldycke `wrapup-session`, sentimony `session-learnings` and hanamizuki `session-retro` as serious candidates. Also screened, and rejected or kept for the handoff only: Cursor's `continual-learning`, `reflect` and `run-learning-retrospective`; gstack `retro`; and about 20 smaller retrospective, learnings and handoff skills (candidate table).
5. **Round 5 (vocabulary from round 4: "narrowest home", "global instructions … last resort", wrapup, session-learnings, session-retro, bye, end session).** Added Claudest `extract-learnings`, kandev `harness-improvement` and diegosouzapw `session-retrospective`. None met more hard criteria or covered more destinations than the round-4 additions.

The search stopped because round 5 added no serious candidate that changes the ranking. The cap was not reached.

## Refresh trigger

Before the build starts, or by 2027-01-22: re-run GitHub repository, code and topic search from a local session with `gh` authenticated. Also re-check whether retro-skill gains a mode that only proposes changes and routing that defers to the project, and whether Claude Code ships a native retrospective or handoff command, from its changelog and the output of `/help`.
