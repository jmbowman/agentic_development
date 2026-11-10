# LID feedback

Suggestions for [LID](https://github.com/jszmajda/lid) (in use at v1.4.0), mostly about decision docs. The evidence is in [the decision-records note](../prior-art/2026-11-06-decision-records-and-lid.md). Related open upstream threads:
- [#39](https://github.com/jszmajda/lid/issues/39): tenets in the instruction file.
- [#79](https://github.com/jszmajda/lid/issues/79): an eval for offering decision docs.
- [#90](https://github.com/jszmajda/lid/issues/90): a table of pending decisions at each stop.
- [#105](https://github.com/jszmajda/lid/issues/105): rulings recorded as paraphrases drift.
- [Discussion #33](https://github.com/jszmajda/lid/discussions/33): the weight of the `@spec` token.

None of the items below has been raised upstream.

**Suggested order:**
1. Build items 1 and 4 locally first.
2. Open one discussion pairing item 1 with #33 and #105.
3. Raise items 2 and 3 after the maintainer responds.
4. Hold item 5.

## Open items

### 1. Decision citations from code, checked like `@spec`

- **Where:** `lidc` checks EARS IDs and `@spec` annotations; nothing checks references to decision docs.
- **What:** code and docs that rely on a decision have no checkable way to cite it, so a deleted or renamed decision leaves stale citations silently wrong.
- **Evidence:**
  - In one project, nine line-number citations silently pointed at the wrong text after an edit, one of them in a tool description agents read. The project now resolves every citation by heading in a test (observational, one case).
  - ConDec used `@decision` code tags with human-validated proposals (Kleebaum et al. 2021).
  - A survey of decision tooling calls linking decisions to code essential, and notes most tools keep only one-way, unchecked links (Mehrpour and LaToza 2023).
  - About 21% of decision-record files moved or vanished within three years (Su et al. 2026), so links to decisions rot too.
- **Limits:**
  - A replacement written into the same file under the same headings passes the check, while the citation may no longer hold.
  - A heading rename forces edits wherever it's cited.
- **Suggested fix:** a citation form by file and heading (`<name>.md § <heading>`, never a line number) that `lidc` resolves, failing on a missing file or heading. Discussion #33's question applies: define what a citation means (implements vs. mentions).

### 2. Tie decisions to the EARS requirements that carry them out

- **Where:** the decision-doc template, which says a decision doc "carries no spec IDs".
- **What:** nothing links a decision to the specs that carry it out, so a spec rename or deletion can orphan a decision without notice.
- **Evidence:** spec-driven-docs checks across the repo that every rule its records name still exists. MADR has an optional Confirmation section for how compliance is checked. In Su et al. 2026, about a quarter of models' misjudged violations involved principle-style decisions with no operational criteria.
- **Two directions to offer:**
  - **(a) The decision cites specs:** an "Enforced by" line listing EARS IDs, which `lidc` checks still exist. This changes the "carries no spec IDs" rule.
  - **(b) Specs cite the decision:** an EARS spec, or the owning design doc's Decisions & Alternatives row, cites the decision doc, and `lidc` checks each decision doc is cited by at least one live spec or row. This keeps the rule and the arrow's direction.

### 3. A structure check for decision docs

- **Where:** no check exists; the template's rules are prose.
- **What:** these are all checkable but unchecked:
  - required sections present and not empty;
  - each option's analysis leads with a verdict word;
  - criteria (not gates) carry an importance from the template's or a project's vocabulary;
  - `node:` names a real segment;
  - the owning design doc links the decision doc.

  The template implies, but doesn't state, at least two options.
- **Evidence:** options are the part people leave out (36% of surveyed practitioners never record discarded options, Tang et al. 2006; a preprint finds Considered Options the weakest section in mined records, Miccio Palermo et al. 2026). There is no evidence that a linter improves outcomes, and rigid checks on rare, judgment-heavy docs risk failing legitimate ones.
- **Suggested fix:** a `lidc` check covering the items above, tolerant of project vocabularies.

### 4. Deliver decisions to the agent

- **Where:** decision docs are found only when an agent goes looking.
- **What:** agents rarely read stored context on their own initiative.
- **Evidence:** one preprint reports zero voluntary memory reads in 114 turns, against reliable delivery by the harness ("Delivery, Not Storage", weak experiment). Two 2026 preprints report better results when past decisions are supplied at coding or review time (abstracts only).
- **Suggested fix:**
  - Start with a SessionStart hook that lists both decision folders with each doc's title, building on #39's generated instruction-file block. Titles name the topic, not the outcome, so agents still open the doc.
  - Later, an optional `scope:` glob list beside `node:` would let a hook print the decisions governing a file before an edit. That adds a second frontmatter field.

### 5. Reopening conditions for rejected or deferred options

- **Where:** the decision-doc template's Options in the Domain section.
- **What:** a rejected or deferred option doesn't name what would bring it back. This overlaps Decision Elements, which already let a reader re-run the judgment; the gain is naming the trigger.
- **Evidence:** practitioner guidance only. Weak.
- **Suggested fix:** an optional "revisit if …" clause per option. Lowest priority.

### 6. Evidence for #79's premise

- **Where:** #79 (does the workflow offer a decision doc when warranted?) is blocked on a multi-turn harness.
- **What:** a single-turn test of a related question can run now: does a recorded decision change agent behavior?
- **Evidence:** keep-the-why's experiment asked sessions to "simplify" a retry wrapper whose rejected alternative was or wasn't recorded. With the record, 0 of 10 offered to drop the behavior the rejected option would lose, against 7 of 10 without (p ≈ 0.003). It is a weak experiment: one task, one model, graded by its author, and the rationale was also in a commit message.
- **Suggested fix:** borrow that design.

### 7. The setup docs overstate what the plugins enforce

- **Where:** `docs/setup.md:59` (at [LID](https://github.com/jszmajda/lid) `727ed80`) says the plugins "automate phase gates".
- **What:** the plugins ship no hooks. The only script is an optional reference `coherence-check.mjs` that always exits 0. The phase gates are skill instructions the agent follows, not mechanical checks. A reader choosing LID for enforcement would be misled.
- **Evidence:** a listing of the plugins at that commit, from [the process prior-art note](../prior-art/2026-11-09-agentic-development-process.md).
- **Suggested fix:** reword to say the skills guide the agent through the phase stops, and point to where mechanical checks can be added (`lidc` in hooks and CI).

## What the evidence says about LID's existing choices

- **Rationale in decision docs, checkable rules in specs:** matches the rationale-versus-rules distinction in the tool-support literature (Mehrpour and LaToza 2023).
- **No status field:** status labels drift (20 inconsistent labels across 109 repos), about half of decision records are never edited after the first commit, and readers rated status as needed only about a quarter of the time.
- **Two weights of record and the cold-reader test:** independent tools arrived at the same split and bar. Caveat: one small study found a minimal template easier to understand than MADR, and LID's full template is heavier still.
- **Mandatory options:** items 3 and 6.
- **Delete and replace:**
  - Practitioners report that agents follow stale records more rigidly than people do (web summaries).
  - Counter-evidence: most practice keeps superseded records with a status, which gives history without git archaeology and keeps supersession links checkable; items 1 and 2 partly recover that.
  - A middle path, an archive folder kept out of agent context, wasn't evaluated.
