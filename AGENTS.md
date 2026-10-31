# agentic_development

Shared tooling for an agentic development process: the pieces each project **references by version** (reusable CI workflows, Renovate presets, and later skills and hooks). This repo also holds the system-level design that its sibling repos (such as `../copier-python`) point back to.

## Working rules

- **Commits:** agents don't commit. They draft `commit-message.md` (gitignored), and the developer they work for commits with `git commit -F commit-message.md`. One commit per slice that has cleared tests and the review wave. Several sessions can work in this repo at once, so re-read `commit-message.md` right before writing it, and don't replace a draft that hasn't been committed yet (compare its summary line with `git log -1`).
- **LID stop cadence (project policy):** the developer reviews the HLD, LLD, EARS and edge-audit stops. For the **tests stop and the Phase 6 completion sign-off**, the review wave is the named inspector. Warn once, then continue to the review wave rather than waiting.
- **Spec-review findings:** apply fixes that don't change meaning (clarity, coverage gaps, scope wording), loop, and list every applied fix in the stop summary. Anything that chooses between two readings of intent goes to the developer as a numbered fork.
- **Review log:** after triaging a review wave or an eval run, append its row to `docs/review-log.md`, in the order the waves ran.
- **README:** `README.md` is for people deciding whether and how to use this repo, and LID's coherence checks don't cover it. Before handing back a change, re-read it against the change. Correct anything the change made false (paths, commands, setup steps, status, what the repo contains), and add a mention of anything a user now needs to know (a new component, command, requirement or limitation). Internal details stay in `docs/`. The review wave checks this too.
- **Public content only:** this repo is public. Don't reference private repositories or files in them, and don't name or assume a particular user. Cite public sources, or restate what's needed here.
- **Subagents** for LID probes and review waves are authorized. Never use the built-in Explore or Plan agents for implementation or review work, because they don't load project rules.

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
