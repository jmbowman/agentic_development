# lid-tooling (`lidc`) feedback

Bugs and proposed enhancements for [lid-tooling](https://github.com/EtaCassiopeia/lid-tooling), which provides `lidc`, LID's coherence checker. This repo runs it as `mise run lid`. Everything below comes from a source read at `1f5627d` (HEAD, 2026-06-10). Paths are relative to that repo; line numbers are at that commit. The wider context is in [the process prior-art note](../prior-art/2026-11-09-agentic-development-process.md).

None of the items below has been raised upstream. The repo has had no commits since 2026-06-10.

**Suggested order:**
1. File the two coverage bugs. They're small, they make this repo's gate weaker than it looks, and filing them tests whether upstream responds.
2. Then propose (e) and (d), which are small and conflict with nothing in LID.
3. Then (a), (b) and (c), which need new inputs.
4. Hold (f).

## How `lidc check` works today

- **Checks:** thirteen are registered (`crates/lid-core/src/checks/mod.rs:46-62`). This repo runs three of them: `coverage`, `reverse-orphan` and `spec-id-format`.
- **EARS lines:** one regex per line, `- [x| |D] **ID**: text` (`parse/markdown.rs:38-41`).
- **`@spec` citations:** any line containing `@spec`, and every ID-shaped token with a digit on that line, so comma lists work (`parse/source.rs:94-112`).
- **Citation kind:** decided from the file's path (`parse/source.rs:126-169`).
- **Staleness:** none. `audited_sha` is parsed but never read.
- **Purity:** checks are pure functions over the loaded repo (`checks/mod.rs:1-10`). Anything that needs test results or a git base ref therefore needs a new input.

## Bugs

### 1. Coverage passes vacuously under a directory named `test` or `tests`

- **Where:** `parse/source.rs:137-142`, called with absolute paths from `repo.rs:91,110`.
- **What:** a citation's kind is tested on its absolute path. In a checkout under any directory named `test` or `tests`, every code citation counts as a Test citation, so `coverage` passes for every `[x]` spec.
- **Suggested fix:** classify on the path relative to the repo root.

### 2. Citations in `.sh` and other script files are invisible

- **Where:** `parse/source.rs:144-150`.
- **What:** files whose extension isn't on the code list are classed Other. Their `@spec` citations escape both `reverse-orphan` and `coverage`. In this repo that covers the SessionStart hook script and the eval `case.yaml` files.
- **Suggested fix:** add shell and other script extensions to the code list, and make the list configurable.

### 3. Malformed IDs: one aborts the run, one is silently skipped

- **Where:** `parse/markdown.rs:38-41`.
- **What:** a spec-shaped line whose ID has no digit aborts the whole run with exit 2. An ID containing lowercase letters is silently not a spec, with no finding.
- **Suggested fix:** report both as findings from `spec-id-format`, rather than as a load error or nothing.

Minor: the Cargo workspace version is 0.2.1 at HEAD while the CHANGELOG says 0.3.0, and `Cargo.toml:10` names a different repository URL.

## Proposed enhancements

Each enhancement fits `lidc`'s design, and none conflicts with LID's rule that revisions change text, not IDs.

### (a) Staleness per spec by content hash

- **What:** an `[x]` marker and a citing test say nothing about whether either changed since someone judged that the test checks the spec.
- **Evidence:**
  - [2119](https://github.com/Unsupervisedcom/2119) hashes the requirement text plus each covering test block, so any edit voids recorded verdicts (`src/hash.ts:12-28`, `src/annotations.ts:61-131` at 652891f).
  - [Habeas Codicem](https://github.com/nikomatsakis/habeas-codicem) fails with a diff when a requirement's text or its cited lines change (`src/evidence.rs:321-420` at 2e8083f).
- **Suggested fix:**
  - Hash each `[x]` spec's normalized text together with the block of each Test citation.
  - Record `{id, hash, verdict}` in a committed file.
  - Add a `lidc stamp` subcommand to write entries, and a `staleness` check that emits the existing `Category::Staleness`. No git is needed.
  - A smaller first step: segment staleness from `audited_sha`, which LID's audit checklist already specifies.
- **Size:** medium, roughly 500-800 lines.

### (b) Coverage proven by the test runner

- **What:** `coverage` checks only that a test file cites the ID. The test may be skipped, never run, or failing.
- **Evidence:**
  - [Spec Engine](https://github.com/spec-engine/spec-engine) joins `@spec` tags to JUnit results by file (`packages/engine/src/check/proven.ts:1-60` at 1f844fd).
  - [Shallnot](https://github.com/RachidChabane/shallnot) binds tests to requirements from JUnit results only.
- **Suggested fix:** a `--results <glob>` option that reads JUnit XML, and a `proven-coverage` check:
  - a failure is an Error;
  - no result is a Warning;
  - a pass proves the spec.
- **Size:** medium, roughly 400-700 lines.

### (c) Guarding against lost links

- **What:** under `--fail-on warning`, an `[x]` spec that loses its last test citation already fails `coverage`. Two gaps remain:
  - nothing requires an `[x]` spec to keep a Code citation;
  - flipping `[x]` to `[ ]`, or deleting a spec together with its citations, silences the check.
- **Evidence:** Spec Engine's guard against a base ref (`packages/engine/src/guard/losses.ts:61-154`).
- **Suggested fix:**
  - An opt-in check for `[x]` specs with no Code citation.
  - A `--base <ref>` mode reporting specs that were downgraded or removed along with their last citation. It must report Warnings only, since LID allows deleting specs that are no longer wanted.
- **Size:** small for the first part; medium for the second, which needs git.

### (d) Impact query from changed files

- **What:** a cascade has no mechanical starting list of the specs and segments a change touches.
- **Evidence:**
  - [specspan](https://github.com/nripankadas07/specspan) (`src/specspan/analyzer.py:617-654` at d0c1fe0);
  - [V-Model](https://github.com/leocamello/spec-kit-v-model) (`scripts/bash/impact-analysis.sh:194-260` at e050c7b);
  - LID's audit checklist already maps changed files to segments.
- **Suggested fix:** a `lidc impact --files` query with JSON output. It maps a changed file to the citations in it, then to spec IDs and their nodes, then to dependents through `index.yaml`. It's the inverse of the MCP spec-reference lookup, and the caller supplies the file list.
- **Size:** small to medium, roughly 200-400 lines.

### (e) EARS-quality lint

- **What:** EARS form and one obligation per spec are checked only by reviewers, in prose.
- **Evidence:** [letspecify](https://www.npmjs.com/package/letspecify) 0.34.0 has deterministic rules for one obligation, one of the five EARS forms, and no declared imprecise terms. Measured on this repo's 438 spec lines:
  - the EARS-form rule passes all of them today;
  - up to 80 lines have more than one `shall`, so a single-obligation rule needs a baseline first.
- **Suggested fix:** an `ears-lint` check at Warning or Info level, with a project-supplied list of imprecise terms. That needs a config surface, which `lidc` lacks today. It must tolerate trailing markers such as `*(eval)*`.
- **Size:** small, roughly 150-250 lines.

### (f) Report of unclaimed code, and two-way pairing

- **What:** `orphan` covers design and spec files only. `implementing-artifacts` checks that listed paths exist, but not that they cite the spec.
- **Evidence:** [srs-dd](https://github.com/crellia-s-l/srs-dd) pairs links in both directions and reports unclaimed files (`srs-dd/tools/srs_check.py:1114-1179` at 29e38cb).
- **Suggested fix:** an Info check listing files with no citation and no arrow-doc entry; and a check that each listed implementing artifact cites an ID from its spec file. Neither can be an Error, since LID annotates entry points only.
- **Size:** small to medium, roughly 150-300 lines.
