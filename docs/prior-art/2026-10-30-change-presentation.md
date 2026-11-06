# Prior art: presenting changes to code and prose for fast, accurate review (2026-10-30)

- **Effort:** full method. The aim is a medium-term fix that may mean building or extending a tool, and the choice shapes how every slice is reviewed.
- **Already known:** the candidates and configuration in [the review-burden note](2026-10-27-review-and-comprehension-burden.md) and in issue #91: delta, difftastic, git word diff, lazygit, markdown-diff-viewer, rich-markdown-diff, pandiff, sem, drift, diffr and diffnav. The developer uses delta and `git wd` (git's own word diff), and reported that `git wd` works well for targeted Markdown changes.

## Need and criteria

The reviewer should see quickly and correctly what changed in code, Markdown and config.

| Property | Underlying need |
|---|---|
| P1 Location | Each change shows where it sits: enclosing function or class, or heading breadcrumb |
| P2 Precision | Show what changed in structure, not reformatting, re-indentation or moved blocks |
| P3 Once per line | A changed line appears once, with removed and added words inline |
| P4 Changed parts only | Changes with a little context, never the whole document |
| P5 Accessible | Terminal (ANSI) palette, plus brightness and shape cues; configurable |
| P6 Coverage | C++, Python, Markdown, TOML/YAML |
| P7 Rendered prose | An optional rendered view of Markdown changes |
| P8 Git workflow | Working tree, index and commits; ideally staging |
| P9 Agent-safe | Plain `git diff` output is unchanged |
| P10 Extensible | A library or API, so spec-ID grouping (#89) can be added |

**Hard criteria:** an OSI-approved license; runs locally; P9.
**Preferences:** evidence-backed presentation choices; no lock-in to another version-control system; maintained.

## Verdict

**Blend:** a new Rust tool with a neutral change model. Its first producer parses `git diff` patch output, and its own inline step shows each changed line once. It borrows line pairing from delta, a fallback threshold from jj, and uses tree-sitter for location. Difftastic's output is a later input where code precision matters. Behind it, a medium-term layer records each agent edit and its stated intent, and checks the claim against the diff.

**No single tool has P1, P2 and P3 together** (see the scorecard below):
- jj's built-in `color-words` format comes closest, with P1 partial and P3, P4 and P5 native. But jj can't serve as the viewer for a git checkout under review. A colocated workspace records the working copy as commits and resets git's HEAD. A workspace on an external git repo leaves HEAD alone but has its own working-copy files, so it can't see the checkout's uncommitted changes. Neither mode has a view of git's index.
- difftastic is the only mature structural differ, but it has no location (P1) and no inline merged lines (P3).
- delta has location but no merged lines.

**The custom pieces, in stages:**
1. **Patch-based renderer (medium).**
   - Input: plain `git diff` patch output, so git owns attributes, drivers, function names and renames. A lazygit `stdinFilter` receives a plain patch anyway, and OSC 1717 staging needs each line's old and new numbers, which `--word-diff=porcelain` output loses.
   - It pairs changed lines (delta's `infer_edits` approach), diffs tokens with `similar`, and renders each changed line once (P3), falling back to separate lines when a pair alternates too much (jj's `max-inline-alternation`).
   - It uses ANSI colour plus strike and underline (P5).
   - It adds a full breadcrumb (P1) from tree-sitter, with git's hunk section as the fallback.
   - It works on the working tree, index and commits (P8), as an alias or a lazygit filter, so plain `git diff` is untouched (P9).
2. **Code precision (medium).** For code files, take difftastic's JSON (changed spans per line) as a second producer. Difftastic's JSON is marked unstable (`DFT_UNSTABLE`, `src/options.rs:813` at 4618021), so pin the version. Word-diff porcelain stays an optional display-only mode for reflowed prose.
3. **Intent layer (medium; the better foundation).**
   - Capture each agent edit (old and new text, file and slice) at edit time, for example from a Claude Code `PostToolUse` hook on Edit and Write.
   - Group the edits by purpose and by EARS ID (#89).
   - Let the agent declare mechanical changes (rename, move, reflow) as rules, replay them, and show the reviewer the unexplained residue next to the full diff.
   - Present stated intent as a claim to check, after the diff, never in place of it.

**Upstream contributions that would shrink the custom part:**
- difftastic location (P1): [Wilfred/difftastic#304](https://github.com/Wilfred/difftastic/issues/304). Small as a regex lookback, medium with tree-sitter scopes.
- delta merged-line mode (P3): [dandavison/delta#152](https://github.com/dandavison/delta/issues/152). Medium.
- jj breadcrumb and TOML mapping (P1, P6). Small.

## Research evidence: what helps reviewers see what changed

Strength tags: [exp] a controlled experiment with a significant result; [exp-weak] an experiment without significance; [obs] large-scale mining; [qual] interviews or observation; [vendor] a vendor claim; [untested] no study. Most sources were read as abstracts.

**Supported by evidence:**
- **Grouping by structure or meaning helps most on complex or systematic changes; plain text diffs suffice on small ones.**
  - Critics (Zhang et al., ICSE 2015, n=12, split across 2 patches): the tool's users scored 33/36 on questions matched to it, against 16/36 or 20/36 with Eclipse diff (the paper's prose and its Table IV disagree), and were faster on the larger patch. It reports no significance tests, and its authors chose tasks that suit the tool. [exp-weak]
  - Zhao et al., CHI 2021 (n=107 end users): outcome-level "semantic diffs" beat syntax diffs on correctness for complex programs (χ²(4)=30.6, p<.001), with no advantage on short programs and no difference in time. An empty result was sometimes read as "no difference". [exp]
  - CG-Diff (arXiv 2609.32057, 2026, n=7): the call graph helped orientation, but the median pull request connects only 30% of its changed functions, so it needs a fallback. [qual]
- **Separating refactorings and moves cuts what must be read.** RAID (ICPC 2021, 8 developers over 3 months): median lines shown fell from 14.5 to 2 for moves and from 113 to 55 for extractions. That's a computed proxy with no control group, and its detector had 13.2% false positives on these types. 46% of refactored entities are also edited in the same commit (Negara, via Alikhanifard & Tsantalis), so edits inside a move must stay visible. [obs]
- **The alignment algorithm changes what reviewers see.**
  - Histogram gave the better result than Myers in 62.6% vs 16.9% of code files where they differ, by two authors' ratings. On non-code files they were level (Nugroho et al., EMSE 2020). [obs]
  - Rule-based "programmer-centric" diffs were rated significantly more understandable and readable than all comparators, mostly with small effects, and GumTree's minimal tree edits were rated significantly worse than GitHub's line diff (srcDiff; Decker et al., JSEP; 69 students, 5 of them experts, 14 changes). These are ratings, not comprehension scores. Accuracy tied with GumTree overall. [exp-weak]
  - AST mappings still mis-match often, and test code is a weak spot (Alikhanifard & Tsantalis, TOSEM 2024). [obs]
  - Correcting an alignment takes about 2 actions in simulation, but the target was Histogram's output, not a reviewer's intent (Yagi & Hayashi, SCAM 2024). [untested]
- **Marks show what changed; animation keeps your place.** In Diffamation (Chevalier et al., CHI 2010, n=16), animation plus highlight was fastest for spotting whether a sentence changed (1.6 s vs 2.2 s for a highlighted slideshow, p<.0001), with no benefit when nothing moved. Animation alone had the most errors. It measured detection of a marked sentence, not understanding. [exp]
- **Never show two versions with no marks.** A bare dual view took 65.5 s against 18–23 s for any marked technique (Zaman et al., GI 2011, diagrams). In its second study the difference layer alone was the slowest and lowest-ranked. [exp]
- **Background tint as a region marker** improved comprehension for some tasks (Feigenspan et al., EMSE 2013, 3 experiments). [exp]
- **Generated summaries and explanations affect review, and what they omit matters most.**
  - Comments that silently left out a constraint lowered accuracy against exact comments (OR 0.58, p=.037) and raised confidence against no comment (p=.005). Accurate comments gave no overall benefit. Over-specified and wrong comments showed no such effect (Kaufman et al., arXiv 2607.08885, n=86, judging assertions). [exp]
  - A complete-looking AI review neither raised detection of injected issues nor saved time, and it added reading. Narrowing to flagged locations is descriptive only, and the nulls may be underpowered (Tufano et al., ICSE 2025, n=29). [exp-weak]
  - One precise, correct comment on a neglected bug type raised detection of a second such bug from 11% to 62%, with wide intervals (Spadini et al., ICSE 2020, n=85). So a targeted pointer can widen review. [exp]
  - Inline-linked explanations raised trust, but the AI was never wrong in that study, so it says nothing about catching flawed output (Gao et al., arXiv 2607.24601, n=34). [exp]
  - A provenance label added fixation time; defect detection wasn't measured (Khojah et al., arXiv 2606.26505, n=32). [exp]
  - Summaries are preferred for large or unfamiliar pull requests (ESEM 2025, n=10). That's preference only. [qual]
- **Graded de-emphasis** improved comprehension and speed on GRE prose by fading less essential words while keeping them visible, but a poor selector was worse than plain text (GP-TSM, Gu et al., CHI 2024, n=18). It hasn't been tested on changed text. [exp]
- **Confidence, trust and preference don't track accuracy** across Kaufman, Zhao, Tufano and Gao, so they can't be the measure of this tool.

**No study found (folklore or open):**
- whether explanations should come before or after a diff. No study tests the order; "after" is a recommendation in Tufano et al., not a tested condition. This is the largest open question for the intent layer. [untested]
- split vs unified layout: the one eye-tracking study, n=12, found no significant difference (Alcocer et al., IEEE Access 2023; abstract only). [exp-weak]
- word-level or intra-line highlighting, context size, and folding of unchanged regions;
- colour-blind diff palettes. Practice converges on blue/orange or blue/brown, a luminance difference, and redundant glyphs or shapes (Wikimedia, Review Board, Phabricator discussions). [qual] Strike and underline appear in Neuwirth's and srcDiff's figures, but no paper tests them. Decker et al. only checked that removing colour-blind participants didn't change their conclusions.
- track changes and legal redlining comprehension. Neuwirth et al. 1992, "Flexible diff-ing", is a system description with no controlled evaluation. It separates what is reported from how precisely it's pinpointed, with reader-set grain size and author explanations on changes. Its authors say the best settings are unknown. [untested]

**Gaps a small study could close,** scoring detection of seeded defects rather than confidence:
1. Explanation before the diff, after a first pass, or on demand, including flawed explanations.
2. Complete vs constraint-omitting summaries on real diffs.
3. One targeted pointer vs a complete-looking review.
4. Stated intent used as a checklist vs a generated summary.
5. Coverage of unmentioned lines under a reordered view.

## Foundations beyond before/after text

| Foundation | Reviewer gains | Limits | Code or prose | Best implementation |
|---|---|---|---|---|
| Tree/AST differencing: Chawathe 1996; GumTree, ASE 2014; truediff, PLDI 2021; hdiff, ICFP 2019; difftastic | No noise from reformatting; changes aligned to syntax; moves (GumTree family) | Heuristic matches can be unintuitive. Difftastic has no move kind (`src/diff/changes.rs:7-20`), no Markdown parser, and falls back to a line diff above 1 MB or 3M graph vertices (`src/options.rs:17,21`) | Code | difftastic (MIT) for display; GumTree (LGPL-3.0, metadata only) for edit scripts |
| Structured-document differencing: Cobena et al., ICDE 2002 (XyDiff/BULD) | Block-aware prose diffs, immune to rewrapping | lowdown shows a move as a delete and an add (`src/diff/diff.c:999` at 6205433); no Pandoc-AST differ exists | Prose | lowdown-diff (ISC-style, `LICENSE.md:1-8`) |
| Semantic and refactoring-aware differencing: Jackson & Ladd 1994; RefactoringMiner; RAID; Coccinelle; comby | A rename or extraction collapses into one claim plus a residue | Per language; fixed set of refactorings | Code | RefactoringMiner (Java-centred) |
| Operation capture with intent: Robbes & Lanza 2006; Epicea; Peritext, CSCW 2022; Ink & Switch Patchwork "Edit Groups"; Darcs and Pijul patch theory | True operations instead of inferred alignment; edits grouped by purpose, with rationale | Needs control of the editing channel; raw operation logs need grouping; stated intent is a claim, not proof | Both | None for review. An agent's own Edit tool calls are such a log already, at no capture cost |
| Revision-intent classification for prose: Yang et al., EMNLP 2017; IteraTeR, ACL 2022; arXivEdits, EMNLP 2022 | Sentence alignment plus "meaning changed" vs "wording only" labels | Classifiers imperfect; taxonomies built for encyclopaedia and paper prose | Prose | datasets and models only |

**Why the agent-authored setting changes the calculus.** Line, tree and document diffs all reconstruct a change from before and after text. An agent knows its operations and intent when it edits, so capture is free. The research above says to use that knowledge only as checkable claims:
- declared mechanical changes are replayed, and the reviewer sees the residue. Review then shifts to the rule, which must itself be read. No tool built this way was found in three searches; LSDiff infers rules rather than taking them as declared. [untested]
- grouped edits are shown alongside the independently computed diff, never in place of it. Inferred grouping is only a suggestion: LLM untangling still misassigns about 30–40% of changed statements (Atomizer; ColaUntangle). Agent-declared groups avoid inference, but they're claims. [exp-weak]
- any summary is labelled as generated, states what it doesn't cover, and points to the hunks it describes.

**For prose,** the evidence supports only coarse labels: mechanical, wording, meaning changed, and unsure (treated as meaning changed). Small meaning changes are the hard case: arXivEdits' "More Accurate" class scores F1 58.6, and IteraTeR's meaning-changed precision is .44. So labels may order and highlight changes in specs but never hide them. For EARS, changes to modal verbs, numbers, triggers or negation could be flagged by rule (proposed, untested).

**Findings on capture and structure:**
- Capture and display should stay separate, with display chosen at read time (Upwelling). Reviewed content must equal merged content, and review state must survive acceptance. [qual]
- Grouping must be retroactive, many-to-many and non-contiguous, and a group isn't necessarily a revert unit (Patchwork Edit Groups, team's own use). [qual]
- The lowdown approach should carry over to mdast, because it needs only node types, hashable attributes and a stable order. Nobody has tried it. Heading slugs and EARS IDs are natural explicit IDs, which XyDiff shows beat inference. [untested]
- Move can be a derived view of detach plus attach of one node (truediff). [obs]
- Marks need provenance and confidence, because tree mappings are heuristic and GumTree is direction-unstable. [exp-weak]

## Proposed change model and Rust stack

**Invariant:** every item records whether it is *observed* (a log), *computed* (a differ), *claimed* (an agent) or *verified* (replay or tests). What the reviewer sees of the target must always be derivable from computed primitives, so a false claim can't hide text.

**Core concepts:**
- an exact base and target revision;
- an artifact, with a renderer-defined pointer into it (hunk, scope path, sentence or token span);
- a hunk as the always-available fallback, with old and new line identity for every line;
- structural scope path, token span, and sentence alignment (one-to-one, split, merge, reorder);
- stable node IDs, using explicit IDs where they exist;
- primitive operations (insert, delete, update), with move derived;
- a rule operation with a replay status: clean, with residue, or unverifiable;
- an edit group;
- a claim with a coarse intent label;
- provenance, confidence, and verification status;
- review state that is independent of acceptance;
- a coverage indicator, so a reordered view shows nothing is missing.

**Left out at first:** keystroke-level streams, merge and commutation semantics, revertable-group guarantees, fine intent taxonomies, automatic untangling, CRDT anchoring, and non-text artifacts.

**Stage 1 stack (read in source; nothing was built or run):**

| Need | Choice | License | Reason |
|---|---|---|---|
| Diff source | `git` subprocess | GPL-2.0, as a separate program | Owns attributes, function names, renames and whitespace behaviour |
| Token diff | `similar` 3.2 (`from_slices`) | Apache-2.0 (`LICENSE:1` at bf4c758) | Takes custom tokens, standalone |
| Line pairing | delta's `infer_edits` approach | MIT | The crates above don't pair lines for custom tokens |
| Location | `tree-sitter` plus grammars for C++, Python, Markdown, TOML, YAML | MIT | Git's section heading is the fallback; it gives one level, and nothing for TOML or YAML |
| Styles | `anstyle` | MIT OR Apache-2.0 | Palette-defined ANSI colours; `anstyle-git` parses git colour syntax |
| Staging | OSC 1717 | spec CC0; delta's module MIT | lazygit hosts it from 0.66.0 |

**Safe invocation.** `git diff` can rewrite the index when it refreshes stat information (`builtin/diff.c:237-250`), and `--no-optional-locks` doesn't prevent that. Use `git -c diff.autoRefreshIndex=false diff --no-ext-diff --no-color --src-prefix=a/ --dst-prefix=b/`, and turn off any `diff.<driver>.cachetextconv`. Read from source, not run.

**gitoxide (MIT OR Apache-2.0; `gix-imara-diff` is Apache-2.0 only).** It can produce all three diffs, and its read paths don't write the index unless asked. It has no function-name patterns, `wordRegex`, whitespace-ignore modes or `diff.context` config, and it doesn't run external drivers (listing and source at 9dd78c8). Its crates are major-zero with roughly monthly releases, and rename tracking deviates from git. Use it later for object, index and attribute reads, behind the same model. Git's userdiff patterns are GPL-2.0, so a permissively licensed tool shouldn't copy them.

**jj-core's `ContentDiff`** takes byte-range tokenizers, which suits tree-sitter. Its core file has few dependencies, so vendoring it under Apache-2.0 is an option if `similar` falls short.

**sem-core 0.29 (MIT OR Apache-2.0).** Usable as a library: `extract_entities` needs no git, and has no telemetry in this crate. It's heavy without a minimal feature on main, its TOML and YAML entities are flat, Markdown support is ATX-only, and it had 59 releases in about 7.5 months. lazydiff depends on a `lang-minimal` branch at 0.5.3, which suggests a shared need for a small extraction crate. Nested TOML and YAML scopes would be a natural contribution.

**srcDiff** (C++, GPL-3.0, `COPYING.txt` at 5d890d2) is usable as an external git diff driver for C, C++ and Java. Its code can't go into a permissively licensed tool, but its published rules for how programmers edit can inform one.

## Candidates and scorecard

n native, p partial, e extensible, u unsupported, ? unverified.

| Candidate | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | License |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jj `color-words` (0.46) | p | p | n | n | n | p | u | p | n | p | Apache-2.0 (LICENSE) |
| git `--word-diff` + funcname drivers | p | p (`-w`) | n | n | p | n | u | n | n | p (porcelain) | GPL-2.0 (tool use only) |
| delta 0.20.1 | n | u | u | n | n | n | u | n | n | u | MIT (LICENSE) |
| difftastic 0.71 | u | n | u | n | p | p | u | p | n | p | MIT (LICENSE) |
| diffsitter | p | n | u | n | p | p | u | p | n | n | MIT (LICENSE) |
| sem | p | p | u | n | ? | ? | u | p | n | n | MIT OR Apache-2.0 |
| GumTree | e | n | u | p | ? | p | u | u | n | n | LGPL-3.0 (LICENSE) |
| VS Code diff editor | p | p | p | n | p | n | u | n | n | e | MIT (`LICENSE.txt:1`; the shipped build is under a separate product license) |
| GitHub web | n | u | u | n | u | n | n | p | n | u | commercial |
| perspica (beta) | p | n | ? | n | ? | p | u | p | n | p | MIT (`LICENSE:1` @2b2935b) |
| hunk | ? | u | ? | n | p | ? | p | n | n | e | MIT (`LICENSE:1` @503efd5) |
| lazydiff (alpha) | p (through sem-core) | p | ? | n | ? | ? | u | p | n | ? | MIT (`LICENSE:1` @bf8d6e6) |

Also scored, with nothing that changes the ranking:
- **u on P1–P3 and P7:** dwdiff, wdiff, gitwdiff, latexdiff, diff-so-fancy, riff, ydiff, icdiff, git-split-diffs, diff2html.
- **Side-by-side or one-sided:** diffview.nvim, difftastic.nvim, diffbandit.nvim.
- **Commercial GUIs:** SemanticDiff, Beyond Compare, Kaleidoscope, JetBrains.
- **No diff command:** Mergiraf.

**Ranking:**
1. A patch-based renderer over `git diff`: covers P1 (with the breadcrumb added), P3–P6, P8 and P9; P2 limited to whitespace options until a structural producer is added.
2. jj `color-words`: closest as shipped. It would rank first if it could render a git checkout's working tree and index.
3. difftastic: the only practical P2. Its location (P1) and merged lines (P3) are upstream work.
4. delta: keeps P1 and staging through lazygit OSC 1717. Merged lines (P3) are upstream work.

**Combination paths, best first:**
1. Plain patch plus renderer.
2. Difftastic JSON as a second producer for the same renderer.
3. sem entity ranges joined onto patch hunks.
4. GumTree edit scripts (large; Java; no Markdown).

Word-diff porcelain as the main input was rejected: a lazygit filter gets a plain patch anyway, line identity for OSC 1717 is lost, and whitespace-only changes don't appear as word changes.

## Limitations checked in source

Verified:
- **jj source-symbol context.**
  - The language mapping covers C-like, Python, Markdown and INI files, with no TOML or YAML (`cli/src/source_symbol.rs:58-93` at 0b00193).
  - Indented C++ class methods are deliberately excluded (`:337-339`).
  - The 0.46.0 changelog lists symbol context in hunk headers (`CHANGELOG.md:211`).
- **Extension points** found by the scorecard researcher:
  - **jj breadcrumb:** one `rfind` symbol per hunk (`cli/src/diff_util.rs:1170-1192`). Its word tokenizer is pluggable (`core/src/diff.rs:620`), but the diff is computed line by line first (`diff_util.rs:1052`).
  - **difftastic headers** are built from path and hunk number only (`src/display/style.rs:539-579`). The tree-sitter node kind is dropped at `src/parse/syntax.rs:116-131`.
  - **delta** paints the minus block, then the plus block (`src/paint.rs:671-700` at 3c2269c). The line pairing a merged mode needs already exists (`src/edits.rs:24,174`).
  - **diffsitter** has `get_scope` (`src/ast_navigation.rs:264` at a5a6681) but doesn't use it in hunk titles (`src/render/unified.rs:256-280`).
- **difftastic's limits:** no move kind, no Markdown parser, a size fallback, and unstable JSON (`src/diff/changes.rs:7-20`, `src/options.rs:17,21,813` at 4618021).

- **jj's attachment to git** (at 2906ef2):
  - **Modes:** `jj git init` has `--no-colocate` and an external `--git-repo` mode (`cli/src/commands/git/init.rs:89-144`).
  - **Colocated:** jj imports and exports on every command (`docs/git-compatibility.md:133-137`) and usually leaves git on a detached HEAD (`:145-149`). `reset_head` rewrites HEAD when the working-copy parent changes (`lib/src/git.rs:2074-2110`).
  - **External repo:** the workspace has its own working-copy files, and refs reach the git repo only through explicit `jj git import` and `export` (`docs/git-compatibility.md:101-117`). jj still protects its commits with `refs/jj/keep/` refs in the git store it uses (`git-backend/src/git_backend.rs:95`).
  - **No index:** jj has no staging area (`docs/git-comparison.md:19-23`).
- **Reuse of jj's code:** the symbol and word-diff rendering lives in `cli/src/source_symbol.rs` and `cli/src/diff_util.rs`, inside the `jj-cli` crate, so a separate tool would copy it under Apache-2.0 rather than depend on it. The tokenizer-based diff is in the `jj-core` crate.
- **jj's contribution policy** (`AI_POLICY.md:1-50`): AI-assisted code is welcome if the contributor understands it and adds an `Assisted-by` trailer, but agents may not open pull requests, reply to issues or post in discussions.

Could not verify:
- Read in full or nearly so: Diffamation, Critics, Neuwirth, Zaman, the srcDiff tool paper, Kaufman, Gao, Khojah, Aðalsteinsson, RAID, CG-Diff, D-Diff, Spadini, most of Tufano, Zhao and GP-TSM, and the Patchwork notebook. Decker et al. (JSEP) was read for its design, results and threats. Targeted sections only: Nugroho, Yagi, Alikhanifard, Peritext, truediff, hdiff, XyDiff, GumTree, IteraTeR, arXivEdits, Yang, Atomizer, ColaUntangle, Coccinelle and comby.
- Still abstract or summary only: Alcocer et al. (IEEE blocked the download), Feigenspan, LSDiff, SemaDiff, ReviewFactor, RefactoringMiner's PurityChecker and the TU Delft theses. Robbes & Lanza 2006 was unavailable, so their FASE 2007 paper stands in.
- Several 2026 preprints (CG-Diff, D-Diff, Kaufman et al., arXiv 2607.24601) are unreviewed. Critics' prose and tables disagree, and the percentages it headlines don't compare like with like.
- The pinned jj line citations in "Extension points" are at 0b00193 and weren't rechecked at 2906ef2.
- Rust crate build time and binary size are unmeasured. Rust unified-diff parser crates haven't been searched, so run a prior-art pass before writing a patch parser.
- lazygit's source comment says git speaks OSC 1717 for word-diff formats. Git's source at ebdc087 has no such code.

## Licensing of a tool built on git

A renderer that runs `git` as a separate program and parses its output is not a derived work of git, on the Free Software Foundation's own reading: pipes and command-line arguments normally connect separate programs, and a program's output isn't covered by its license unless it copies part of the program. That FAQ was restated from memory because gnu.org was rate-limiting requests, and this isn't legal advice. The limits are:
- linking git's code, or copying from it, would bring in GPL-2.0 (`libgit2`, under GPL-2.0 with a linking exception, and `gitoxide`, under MIT or Apache-2.0, are the library alternatives);
- code copied from jj carries Apache-2.0 terms: keep its license text and notices, and mark the files changed.

## Scope of existing projects

No project found covers change comprehension for both code and prose. That rests on these searches, whose queries targeted tools rather than project scope, so treat it as probable, not proven. The nearest efforts each cover part of it:

| Project | Covers | Doesn't cover |
|---|---|---|
| [Ataraxy Labs](https://ataraxy-labs.com) (sem, [inspect](https://github.com/Ataraxy-Labs/inspect), [lazydiff](https://github.com/Ataraxy-Labs/lazydiff)) | Entity-level diffs, risk triage and a terminal review UI for code | Prose beyond heading sections, merged lines, reviewer experiments |
| [hunk](https://github.com/modem-dev/hunk) | Terminal review UI with inline agent notes | Structural diffs, by its own comparison table |
| [semantic-review](https://github.com/mikker/semantic-review) | LLM narrative of a diff | Independent checking of the narrative |
| [Ink & Switch Patchwork](https://www.inkandswitch.com/patchwork/notebook/) | Version control and review for prose and other media | Code; it's research, not a tool to adopt |
| [marginalia](https://github.com/gruesomeparty/marginalia) | Comments on rendered Markdown, returned to agents | Change presentation |

The gap is the combination: code and prose together, claims checked against independently computed diffs, and evaluation with reviewers.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Installed delta 0.20.1, difftastic 0.71.0, git 2.53; tests in the 2026-10-28/29 work on #91 |
| Earlier notes | searched | [2026-10-27 review-burden note](2026-10-27-review-and-comprehension-burden.md); issue #91 comments |
| Research literature | searched | Web search, OpenAlex (keyword and citing-works snowballs from Neuwirth 1992, Chevalier 2010, Nugroho 2020, Alcocer 2023, srcDiff 2019 and Zhao 2021), and arXiv; queries on diff layout, word highlighting, AST diffs with users, track changes, animation, colour-blind palettes, summaries and anchoring, tree differencing, operation capture, revision intent |
| Semantic Scholar API | unavailable | HTTP 429 on retry |
| Ink & Switch essays | searched | Patchwork notebook and Peritext, from search summaries |
| GitHub repository search | searched | "structural diff", "word diff", "semantic diff", "inline diff", "diff viewer", "tree diff", "ast diff", "markdown diff", "intent diff", "refactoring aware diff", "diff visualization", "colorblind diff", "moved code detection diff", "pijul", "peritext" |
| GitHub topics | searched | `hunk-extension`, `tree-diff`, `structural-diff` |
| crates.io | searched | "word diff", "structural diff", "diff pager", "semantic diff", "tree diff", "markdown diff" |
| npm | searched | "word diff", "inline diff terminal", "structural diff", "git diff pager", "markdown diff" |
| PyPI | searched (R2, by name); excluded (R3) | gumtree, graphtage, xmldiff, tree-sitter-diff; R3 excluded it because PyPI has no search API and other routes covered the space |
| alternativeto.net | searched | Alternatives to difftastic (search snippet; GUI two-pane tools only) |
| General web search | searched | Vendor features (SemanticDiff, VS Code, JetBrains, GitHub/GitLab rich diffs, dwdiff, Mergiraf), legal redlining, Wikipedia diffs; "open source project improving human comprehension of code and documentation changes" (2026-11-02) |
| GitHub search for project scope | searched (2026-11-02) | "code review comprehension", "review agent diffs", "understand code changes", "human review ai code", "review tool agents" |
| aitoolnet.com | excluded | The need is a diff viewer, not an AI tool. The AI review layers that exist (semantic-review, perspica, CodeRabbit) were found through GitHub and web search |

## Snowball rounds

- **Round 1:** named tools and papers, plus the route queries. Added hunk, perspica, diffle, diffbandit, gitwdiff, lowdown, truediff and the Patchwork notebook.
- **Round 2:** citing works, and registry follow-ups. Added srcDiff, Critics, ClDiff, Diffamation, Zhao et al., CG-Diff, D-Diff, Feigenspan, IteraTeR and arXivEdits.
- **Round 3:** source reading and agent provenance (git-ai, Memento). This found jj 0.46's symbol context, the one significant new fit.
- **Round 4 (2026-11-02):** full reads and Rust building blocks. Added Spadini 2020, GP-TSM's findings, Upwelling, gitoxide, `similar`, `anstyle`, lazydiff and srcDiff's open-source release. No new candidate has P3 together with P1 or P2.

The search stopped because no later round produced a candidate with P3 together with P1 or P2.

## Refresh trigger

Recheck when any of these happens:
- difftastic#304 or delta#152 lands;
- jj can render a git checkout's working tree and index without moving HEAD;
- a controlled study of word-level highlighting or colour-blind diff palettes appears;
- before starting stage 3 of the verdict.
