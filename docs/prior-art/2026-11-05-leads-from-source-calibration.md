# Leads from the source calibration (2026-11-05)

These are unverified leads, found while calibrating the prior-art-search skill's sources on 18 topics (see the [catalogs note](2026-11-04-agent-readable-catalogs-and-paper-sources.md)). Nobody has read any of them beyond a title, an abstract or a catalog listing line. A prior-art search should treat each one as a candidate to check, not as a finding. Repos given by owner and name without a link were recorded that way in the source listing.

## Additions to earlier notes

### [Prior-art search skill](2026-10-17-prior-art-search-skill.md)
- [RepoReuse: Do Coding Agents Reuse Existing Code or Reinvent the Wheel?](https://arxiv.org/abs/2609.35357) — measures the failure that a search-before-build skill targets.
- [Package Hallucination Attacks on Coding Agents through Rule Files](https://arxiv.org/abs/2610.09264) — the risk that a "check the package exists" step guards against.
- [We Have a Package for You](https://arxiv.org/abs/2406.10279) — an earlier study of package hallucination.
- [Do AI Coding Assistants Check Before They Install?](https://arxiv.org/abs/2609.07754) — whether agents verify a dependency before adding it.
- `rianczerwinski/prior-art-skill` (no link found) — a prior-art skill found by GitHub search.
- `patent` crate (no link found) — listed as "a prior-art search for your code ideas"; 0 votes on AUR.

### [Agent reference clones](2026-10-19-agent-reference-clones.md)
- [LLM Agents Can See Code Repositories](https://arxiv.org/abs/2606.14061) — how repository access affects agent behavior.
- [For Coding Agents, the Repository Matters](https://arxiv.org/abs/2606.28235) — the same question; a replication package is on Zenodo.
- [The Code of Theseus](https://arxiv.org/abs/2610.20068) — repository-access effects, judged from title and abstract.
- `all-repos`, `git-get`, `ham`, `gitopolis`, `ripvcs` (no link found) — multi-repo tools; the listings suggest none gives pinned read-only reference clones.

### [Docs-site search and graph features](2026-10-23-docs-site-search-and-graph-features.md)
- [RepoDoc](https://arxiv.org/abs/2604.26523) — documentation generation built on a knowledge graph.
- [CODENS](https://arxiv.org/abs/2607.18356) — living, queryable documentation updated from code changes.
- [Knowledge Activation: AI skills as institutional knowledge](https://arxiv.org/abs/2603.14805) — skills as a form of documentation.
- [A Toolkit for Generating Code Knowledge Graphs](https://arxiv.org/abs/2002.09440) — older graph-building work; no paper on site generators turned up.

### [Progressive-disclosure knowledge base](2026-10-23-progressive-disclosure-knowledge-base.md)
- [Progressive Disclosure for LLM-Maintained Wiki KBs](https://arxiv.org/abs/2607.04576) — a preregistered ablation of the note's design question.
- [Is Progressive Disclosure All You Need for Long-Context Agents?](https://arxiv.org/abs/2607.17598) — the topic's papers include counter-evidence that it may not be cheaper.
- [Report: Progressive Disclosure of Agent Skills](https://arxiv.org/abs/2609.35692) — an industry report on skills loaded in stages.
- [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) — measures what context files do; 15 citing papers, all relevant.
- [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) — the same question, studied separately.
- [Do Coding Agents Follow AGENTS.md?](https://arxiv.org/abs/2611.04367) — compliance with context files.
- [What Open-Source Projects Tell Their Coding Agents](https://arxiv.org/abs/2610.31715) — a census of AGENTS.md files.
- [Agentic Coding Manifests](https://arxiv.org/abs/2509.14744) — on Claude context manifests.
- [Acquiring and Verifying Repository Norms](https://arxiv.org/abs/2610.07757) — agents and a repo's conventions.

### [Review and comprehension burden](2026-10-27-review-and-comprehension-burden.md)
- [Breaking the Alphabet: file ordering in code review](https://arxiv.org/abs/2609.04207) — file order and reviewer attention; a replication package is on Zenodo.
- [Code Review Comprehension](https://arxiv.org/abs/2503.21455) — reviewing strategies seen through comprehension theories.
- [Software Delegation Contracts: Measuring Reviewability](https://arxiv.org/abs/2606.17099) — a reviewability measure.
- Human-AI Collaboration in Code Review: Cognitive Load (no link found) — a 2026 title on the note's core question.
- `alibaba/open-code-review` (no link found) — a deterministic pipeline plus LLM review, about 49k stars.
- `roborev`, `tuicr`, `reviewdog` (no link found) — review tools that the topic's baseline search missed.

### [Session wrap-up skills](2026-10-29-session-wrap-up-skills.md)
- [Handoff Debt](https://arxiv.org/abs/2606.02875) — the cost of resuming work after a handoff.
- [The Handoff Tax](https://arxiv.org/abs/2608.24358) — the same theme, studied separately.
- [Compact-Bench](https://arxiv.org/abs/2610.31710) — a benchmark for context compaction.
- [Compaction Laundering](https://arxiv.org/abs/2610.29869) — provenance that summaries lose.
- [PROJECTMEM](https://arxiv.org/abs/2606.12329) — local-first, event-sourced memory for coding agents.
- [LongMemEval-V2](https://arxiv.org/abs/2605.12493) and [MemoryArena](https://arxiv.org/abs/2602.16313) — memory benchmarks.
- When Does Context Compaction Pay in Long-Horizon Agents? (no link found) — a 2026 title on Crossref.
- `mimo-code`, `entire-cli`, `claude-md-management` (no link found) — cross-session memory, agent sessions captured in git, and saving session learnings.

### [Change presentation](2026-10-30-change-presentation.md)
- [ARCTIC: From Code Review to Code Critique](https://arxiv.org/abs/2607.29516) — a different framing of what review produces.
- [Runnable Commit Untangling for Coding Agents](https://arxiv.org/abs/2610.11593) — splitting agent changes into runnable commits.
- [Untangling Fine-Grained Code Changes](https://arxiv.org/abs/1502.06757) — the older untangling work.
- [Augmenting Diffs With Runtime Information](https://arxiv.org/abs/2212.11077) — diffs annotated with execution data.
- [Diff-XYZ](https://arxiv.org/abs/2510.12487) — a benchmark for diff understanding.
- [Beyond the "Diff": Agentic Entropy](https://arxiv.org/abs/2604.16323) — on agent-made changes, title only.
- ChangePrism's reference list on Semantic Scholar (no link found) — the older tool lineage: Spike, DiffViz, REdiffs, RefDistiller, graph-based visualization of merge requests.
- `diffyml`, `csvdiff`, `datadiff-cli` (no link found) — structured-data diffs.

### [Interactive skill evals](2026-11-03-interactive-skill-evals.md)
- [SWE-DIVE](https://arxiv.org/abs/2610.30047) — multi-turn evaluation of coding agents with a simulated user.
- [UserSWE](https://arxiv.org/abs/2610.29822) and [SWE-Together](https://arxiv.org/abs/2606.29957) — other 2026 benchmarks that script a user.
- [Intent-Preserving Adversarial User Simulation](https://arxiv.org/abs/2610.35426) — simulated users that keep to an intent.
- [SAGE user simulator](https://arxiv.org/abs/2510.11997) — a user simulator to borrow from.
- [PersonaForge](https://arxiv.org/abs/2608.28378) and [Lost in Simulation](https://arxiv.org/abs/2601.17087) — more user-simulation work.
- [A Framework for Evaluating Agentic Skills at Scale](https://arxiv.org/abs/2606.17819) — skill-level evaluation.
- `darkrishabh/agent-skills-eval`, `@microsoft/vally-cli`, `trajectory-judge` (no link found) — skill-eval tools, probably single-turn; not checked for answering dialogs.

## Broad software topics

### Flaky tests
- [Shaker](https://arxiv.org/abs/2609.25528) — flaky-test work with a software artifact on Zenodo.
- [Flakiness datasets](https://arxiv.org/abs/2605.21677) — data for evaluating detectors.

### Dependency and supply-chain risk
- [ConfuGuard](https://arxiv.org/abs/2502.20528) — a good snowball seed; its Semantic Scholar recommendations were mostly relevant.
- [Backstabber's Knife Collection](https://arxiv.org/abs/2005.09535) — the landmark review of package supply-chain attacks.
- `cargo-vet` (no link found) — Rust dependency auditing; no paper on release-age cooldowns turned up.

### Configuration drift across repos
- [tfdrift](https://arxiv.org/abs/2608.18173) — one of few papers here; the literature is thin, mostly industry whitepapers.

### Evaluating LLM coding agents
- [SWE-bench](https://arxiv.org/abs/2310.06770) — the landmark benchmark.
- [SWE-bench Live](https://arxiv.org/abs/2505.23419) — a later SWE-bench variant.
- [Agent-as-a-Judge](https://arxiv.org/abs/2410.10934) — agents grading agents.

### Reproducible builds and lock files
- [Reproducible builds landmark paper (2021)](https://arxiv.org/abs/2104.06020) — the standard overview.
- [The Design Space of Lockfiles](https://arxiv.org/abs/2505.04834) — lockfile designs compared.

### API evolution
- [Roseau](https://arxiv.org/abs/2507.17369) — breaking-change detection, with an artifact on Zenodo.
- [Why and How Java Developers Break APIs](https://arxiv.org/abs/1801.05198) — the landmark empirical study.

## Seeds for upcoming searches

### The agentic development process (issue #98)
- [github/spec-kit](https://github.com/github/spec-kit) — Spec Kit, MIT, about 147k stars.
- [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) — a spec-driven framework, MIT.
- [nizos/tdd-guard](https://github.com/nizos/tdd-guard) — a hook that enforces TDD, MIT.
- `sd0xdev/sd0x-harness` (no link found) — dual review enforced by hooks.
- `itsallcode/openfasttrace` (no link found) — requirements tracing, GPL-3.0.
- [Spec Kit Agents](https://arxiv.org/abs/2604.05278) — context-grounded workflows built on Spec Kit.
- [Spec-driven development as prescribed and as practiced](https://arxiv.org/abs/2608.25202) — an empirical comparison.
- [The Kitchen Loop](https://arxiv.org/abs/2603.25697) — user-spec-driven development for a self-evolving codebase.
- [OpenCodeReview](https://arxiv.org/abs/2608.09290) — determinism over non-determinism in agent code review.
- [Adversarial Review](https://arxiv.org/abs/2608.18167) — structured disagreement in agent code review.
- [A Deterministic Control Plane for LLM Coding Agents](https://arxiv.org/abs/2606.26924) — agent config managed across repos as shared components.

### Rust in agent skills
- [microsoft/wassette](https://github.com/microsoft/wassette) — Wasm components through MCP, MIT.
- [symposium](https://symposium.dev) — matches skills, hooks and MCP servers to a Rust project's dependencies.
- `agent-sh/agnix` (no link found) — a Rust linter for SKILL.md, hooks and MCP, Apache-2.0.
- `daixudk96-max/agent-skill-gate` (no link found) — a step gate written in Rust.
- [Agent Skills for Large Language Models](https://arxiv.org/abs/2602.12430) — skill architecture, acquisition and security.
- [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) — whether skills help in real software work.
- [MVVM](https://arxiv.org/abs/2410.15894) — WebAssembly-based secure deployment of agents.
- [Names Are Not Objects](https://arxiv.org/abs/2610.14488) — confinement for compromised coding agents.
- [Hidden Licensing Risks in the LLMware Ecosystem](https://arxiv.org/abs/2602.10758) — licensing risk in the agent ecosystem; no paper on shipping compiled helpers with skills turned up.

### State machines and BPMN for orchestrating LLM work
- [statelyai/agent](https://github.com/statelyai/agent) — XState-based agents, MIT.
- `justinstimatze/stull` (no link found) — Claude Code hooks as guarded state machines.
- `conductor-oss/conductor` (no link found) — a durable workflow engine, Apache-2.0.
- [Best AI coding agent orchestrators](https://openalternative.co/blog/best-ai-coding-agent-orchestrators) — a blog comparison of 13 tools.
- [Bounded Loops](https://arxiv.org/abs/2609.27871) — a harness with proved termination, compared with durable execution.
- [MCP Workflow Engine](https://arxiv.org/abs/2605.00827) — replays solved tasks without LLM tokens.
- [MetaAgent](https://arxiv.org/abs/2507.22606) — multi-agent systems built as finite state machines.
- [BPMN extension for human-agentic workflows](https://arxiv.org/abs/2412.05958) — BPMN adapted for agent and human steps.
- [AgentSPEX](https://arxiv.org/abs/2604.13346) — a specification and execution language for agents.
- [A Formal Hierarchical Architecture for Agentic Orchestration](https://arxiv.org/abs/2607.11138) — stack-based execution with lazy discovery.

### Moving a system's deterministic parts to Rust
- `smartcomputer-ai/lightspeed` (no link found) — a deterministic agent harness in Rust for Temporal, Apache-2.0.
- `VirtusLab/orca` (no link found) — deterministic AI-driven flows.
- `cordum-io/cordum` (no link found) — policy and human approval before tool calls.
- [RustMap](https://arxiv.org/abs/2503.17741) — project-scale C-to-Rust migration through program analysis plus an LLM.
- [CRUST-Bench](https://arxiv.org/abs/2504.15254) — a benchmark for C-to-safe-Rust translation.
- [Steerability via constraints](https://arxiv.org/abs/2607.02389) — enforced conventions and access control as oversight of agents.
- [Ontology-Grounded Project Memory for Coding Agents](https://arxiv.org/abs/2608.13662) — a deterministic store beside the LLM.
- [Imandra CodeLogician](https://arxiv.org/abs/2601.11840) — neuro-symbolic reasoning about software logic.
- Maat: Independent Deterministic Contract-Based Governance for Multi-Agent LLM Workflows (no link found) — governance kept outside the model.
