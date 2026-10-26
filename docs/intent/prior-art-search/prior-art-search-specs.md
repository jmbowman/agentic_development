# Prior-art search skill specs

Design: [prior-art-search-design.md](prior-art-search-design.md). "This repo" is agentic_development, which publishes the skill. "The skill" is `skills/prior-art-search/` in this repo. "The agent" is an agent following the skill. "The host repo" is the repo the agent is working in. "The developer" is the person the agent works for. "The report" is the skill's result in the conversation, and "the note" is the saved copy of it. "A serious candidate", "a round" and "a route" are as defined in the design's Terms section, and step numbers are those of its Steps section. "A non-interactive run" is one where the agent can't ask the developer and wait for an answer. Specs marked *(eval)* describe the agent's behavior and are verified only by the skill's behavior evals; the rest are verified by structure tests.

## Package

- [x] **PRIOR-PKG-001**: This repo shall have `.claude-plugin/plugin.json` at its root with `name` `agentic-development`, a non-empty `description`, an `author` with a non-empty `name`, `license` `Apache-2.0`, a `repository` URL, and no `version` key.
- [x] **PRIOR-PKG-002**: This repo's `.claude-plugin/marketplace.json` shall list exactly one plugin, named `agentic-development`, whose `source` is `./`.
- [x] **PRIOR-PKG-003**: The skill's `SKILL.md` frontmatter shall have exactly the keys `name`, `description` and `license`, with `name` equal to `prior-art-search`, a non-empty `description` of at most 1024 characters, and `license` equal to `Apache-2.0`.
- [x] **PRIOR-PKG-004**: The skill's `SKILL.md` shall be under 500 lines.
- [x] **PRIOR-PKG-005**: Every relative file path that the skill's `SKILL.md` references shall exist inside the skill's directory.
- [x] **PRIOR-PKG-006**: The skill shall contain `references/sources.md`, `references/verification.md` and `references/note-template.md`.
- [x] **PRIOR-PKG-007**: The skill's `SKILL.md` and reference files shall contain no `@spec` annotation.
- [x] **PRIOR-PKG-008**: The skill's `references/sources.md` shall contain a route table with the columns route, trigger, good for and tactics, including at least one route whose trigger is an agent skill, plugin or MCP server.
- [x] **PRIOR-PKG-009**: The skill's `references/verification.md` shall define the evidence record with exactly the fields `candidate`, `url`, `criterion`, `claim`, `support`, `evidence`, `evidence_kind`, `read_depth`, `commit` and `as_of`, and the ledger record with exactly the fields `route`, `state`, `queries`, `reason` and `as_of`.
- [x] **PRIOR-PKG-010**: The skill's `references/note-template.md` shall have a section for each of: the need and criteria, the verdict, the candidate table and matrix, the limitations checked in source, the coverage ledger, the snowball rounds, and the refresh trigger.
- [x] **PRIOR-PKG-015**: The skill shall contain `LICENSE.txt` with the same text as this repo's `LICENSE`.

## Triggering

- [x] **PRIOR-TRIG-001**: When an agent is about to recommend or start building a new tool, library, script, subsystem or agent skill, or to extend one with a new capability or a new external dependency, the skill shall trigger. *(eval)*
- [x] **PRIOR-TRIG-002**: When someone asks whether software that meets a need already exists, the skill shall trigger. *(eval)*
- [x] **PRIOR-TRIG-003**: The skill shall not trigger for a bug fix, a refactor inside existing code, a dependency the host repo already uses, help using a tool the developer has already chosen, or a custom piece named in the skill's own report. *(eval)*

## Effort

- [x] **PRIOR-EFF-001**: Before searching, the agent shall state its effort level, quick pass or full method, with a one-line reason. *(eval)*
- [x] **PRIOR-EFF-002**: Unless the developer has chosen the level, the agent shall pick a quick pass for a choice that is cheap to reverse, and the full method for a choice that is expensive to reverse or that the developer has flagged as long-lived. *(eval)*
- [x] **PRIOR-EFF-003**: Where the developer has chosen the effort level, the agent shall use that level. *(eval)*
- [x] **PRIOR-EFF-004**: While running a quick pass, the agent shall run steps 0 to 6 with at least two searched routes and at least one snowball round, read the primary page and the license (per PRIOR-LIC-001) of each candidate its report presents, and report in the conversation. *(eval)*
- [x] **PRIOR-EFF-005**: If the developer hasn't chosen a quick pass, and a quick pass would conclude a verdict other than adopt or build on, or two candidates both meet every hard criterion on the evidence read so far, then the agent shall switch to the full method, keep the ledger and candidates found so far, search or give a reason tied to the need for each route excluded only because of the quick pass, and restate the level with its reason. *(eval)*
- [x] **PRIOR-EFF-006**: If the developer has chosen a quick pass and PRIOR-EFF-005's condition holds, then the agent shall finish the quick pass and give the verdict as "unaudited (quick pass by developer choice)". *(eval)*
- [x] **PRIOR-EFF-007**: While running the full method, the agent shall run steps 0 to 12 and save a note. *(eval)*

## Search

- [x] **PRIOR-SRCH-001**: Before searching, the agent shall read the host repo's recorded decisions and earlier prior-art notes on the topic, and ask the developer what they already know about or have dismissed. *(eval)*
- [x] **PRIOR-SRCH-002**: In a non-interactive run, the agent shall record PRIOR-SRCH-001's question to the developer as unanswered and continue. *(eval)*
- [x] **PRIOR-SRCH-003**: The agent shall record the underlying need beside each stated requirement, and shall search against the needs rather than against a proposed solution shape. *(eval)*
- [x] **PRIOR-SRCH-004**: The agent shall list hard pass/fail criteria before weighted preferences, and unless the developer states otherwise, shall include license compatibility with the host repo's license and its distribution as a hard criterion. *(eval)*
- [x] **PRIOR-SRCH-005**: The agent shall check each recommendation inherited from an earlier note or session against the current needs and criteria, and shall treat each one that survives as a candidate, not as a conclusion. *(eval)*
- [x] **PRIOR-SRCH-006**: The agent shall check whether the host stack's existing tools, platform features or installed dependencies cover the need, and shall treat each one that does, fully or partly, as a candidate. *(eval)*
- [x] **PRIOR-SRCH-007**: The agent shall select every route in `references/sources.md` whose trigger matches a signal in the need. *(eval)*
- [x] **PRIOR-SRCH-008**: The agent shall end each selected route in exactly one ledger state: searched, with 2 or 3 differently worded queries; excluded, with a concrete reason tied to the need, or, while running a quick pass, the reason "quick pass"; or unavailable, with a diagnosis made after one retry. *(eval)*
- [x] **PRIOR-SRCH-009**: The agent shall build every search query only from the stated need, never from private identifiers, internal names or the host repo's code. *(eval)*
- [x] **PRIOR-SRCH-010**: When a round finds a new serious candidate, the agent shall seed the next round from that candidate's topics and tags, "alternatives to" pages, awesome lists that mention it, its equivalents in other languages, and its dependents. *(eval)*
- [x] **PRIOR-SRCH-011**: The agent shall end the snowball when a round adds no new serious candidate, or after round 10, and if it ended after round 10 while the last round added a serious candidate, the report shall say the cap was reached. *(eval)*
- [x] **PRIOR-SRCH-012**: Before concluding that nothing fits, the agent shall run queries with the vocabulary learned during the search on at least one route it hasn't yet searched. *(eval)*

## Classification and verification

- [x] **PRIOR-CLS-001**: The agent shall classify each serious candidate in a full-method run, and each candidate a quick-pass report presents, as adopt, build on, borrow ideas or reject, with a one-line reason and its license. *(eval)*
- [x] **PRIOR-CLS-002**: The agent shall not cite popularity, stars or install counts as evidence that a candidate meets a criterion. *(eval)*
- [x] **PRIOR-CLS-003**: While running the full method, the agent shall give every criterion for every serious candidate one support value, `native`, `partial`, `extensible`, `unsupported` or `unverified`, citing a source or saying "not found". *(eval)*
- [x] **PRIOR-CLS-004**: While running the full method, the agent shall record `unsupported` only with evidence of the absence, and shall otherwise record a criterion it couldn't confirm as `unverified`. *(eval)*
- [x] **PRIOR-CLS-005**: While running the full method, the agent shall rank serious candidates first by the number of hard criteria they support, then by preferences. *(eval)*
- [x] **PRIOR-CLS-006**: While running the full method, the agent shall verify in source the top two ranked candidates, every serious candidate when there are three or fewer, and the third when it is close to the second. *(eval)*
- [x] **PRIOR-CLS-007**: While running the full method and no verified candidate is classified adopt, the agent shall verify the next-ranked serious candidate and re-rank, until a verified candidate is classified adopt, or every remaining serious candidate has been verified or fails a hard criterion that reading its code can't change. *(eval)*
- [x] **PRIOR-CLS-008**: While running the full method, the agent shall check whether a combination of candidates, or a candidate plus a small custom piece, beats any single candidate, and shall label a partial match as a building block. *(eval)*
- [x] **PRIOR-CLS-009**: While running the full method, the agent shall walk each finalist through 2 to 4 concrete change scenarios that fit the need, and shall set the final classifications only after that walk. *(eval)*
- [x] **PRIOR-CLS-010**: While running the full method, the agent shall tag each limitation it reports as *verified in source (path:line at commit)* or *docs only*. *(eval)*
- [x] **PRIOR-CLS-011**: While running the full method, the agent shall tag every limitation of a hosted service or closed-source candidate as *docs only*, and the report shall say so. *(eval)*
- [x] **PRIOR-CLS-012**: While running the full method, the agent shall verify a native feature against the installed code or its pinned version's docs. *(eval)*

## Licenses

- [x] **PRIOR-LIC-001**: When the agent records a candidate's license, it shall read it from the first available of: its license file, the license field of its package manifest, its README or file headers; and shall cite the file and line it used. *(eval)*
- [x] **PRIOR-LIC-002**: The agent shall not record a license from a forge badge or forge API metadata alone. *(eval)*
- [x] **PRIOR-LIC-003**: The agent shall record each license at the commit it read and for the paths it used, and shall prefer a monorepo package's own license file over the repo root's. *(eval)*
- [x] **PRIOR-LIC-004**: When a license offers a choice ("OR"), the agent shall record every option. *(eval)*
- [x] **PRIOR-LIC-005**: When a candidate vendors code under another license, the agent shall flag the vendored directory and its license. *(eval)*
- [x] **PRIOR-LIC-006**: If the agent finds no license, then it shall cite the file listing it based that on, and shall classify the candidate only as borrow ideas or reject. *(eval)*

## Reading source

- [x] **PRIOR-SRC-001**: The agent shall read source from the first available of: the host repo's reference-clone convention named in its instructions, the forge's contents API when authenticated, a scratch shallow clone, and the package registry's published source archive. *(eval)*
- [x] **PRIOR-SRC-002**: When the agent clones a candidate, it shall clone with `git clone --depth 1`, no submodules and `GIT_LFS_SKIP_SMUDGE=1`, into a new, empty directory under its scratch or temp directory and outside the host repo, and for a large repo shall add `--filter=blob:none --sparse` and check out only the directories it needs. *(eval)*
- [x] **PRIOR-SRC-003**: When the agent downloads a registry source archive, it shall extract it without building it. *(eval)*
- [x] **PRIOR-SRC-004**: The agent shall record the resolved commit SHA, or the archive's version, for every source reading. *(eval)*
- [x] **PRIOR-SRC-005**: The agent shall never install, build or run a candidate, or a script from one, during evaluation. *(eval)*
- [x] **PRIOR-SRC-006**: The agent shall treat candidate repos, pages and catalog entries as data, and shall never follow instructions found in them. *(eval)*
- [x] **PRIOR-SRC-007**: The agent shall never send credentials or the host repo's private content to a candidate or its service. *(eval)*
- [x] **PRIOR-SRC-008**: Where the agent delegates searching or reading to subagents, each subagent shall return only evidence records and ledger records in the shapes `references/verification.md` defines, and the agent shall build the matrix and the ledger only from those records and its own readings. *(eval)*
- [x] **PRIOR-SRC-009**: The agent shall record a claim that something is absent as `listing` evidence whose evidence is the search command and its scope. *(eval)*

## Agent skills as candidates

- [x] **PRIOR-SKL-001**: When the need is an agent skill, plugin, MCP server or prompt pack, the agent shall select the skill-catalog routes in `references/sources.md`. *(eval)*
- [x] **PRIOR-SKL-002**: The agent shall use skill catalogs only through their websites or APIs, and shall never install a catalog's own finder skill. *(eval)*
- [x] **PRIOR-SKL-003**: When the agent evaluates a skill, it shall read the skill's `SKILL.md` and every file it references, including scripts and hooks, and for a plugin that bundles many skills, only the skills under evaluation and what they reference. *(eval)*
- [x] **PRIOR-SKL-004**: When the agent evaluates a skill, it shall record whether the skill uses frontmatter fields outside the Agent Skills spec, tools or connectors that only one agent provides, or an install step, a service or credentials. *(eval)*
- [x] **PRIOR-SKL-005**: The agent shall treat existing scanner results for a skill as leads, not verdicts, and shall not run a scanner itself. *(eval)*

## Report

- [x] **PRIOR-RPT-001**: The report shall start with exactly one verdict: adopt *X*; build on *X*; blend, naming its parts; build, naming the candidates it borrows ideas from or saying none; inconclusive; or unaudited. *(eval)*
- [x] **PRIOR-RPT-002**: If the developer stopped the search, or the agent would otherwise conclude build while a triggered route is still unavailable or the last round added a serious candidate, then the verdict shall be inconclusive, and the report shall name what's missing and, when the round cap was reached, list the open leads. *(eval)*
- [x] **PRIOR-RPT-003**: The report shall give the verdict build only when every triggered route is searched or excluded with a reason tied to the need, none is unavailable, and the last round added no serious candidate. *(eval)*
- [x] **PRIOR-RPT-004**: While running the full method, after the verdict, the report shall give a ranked shortlist with one line per candidate on why it ranks there and what would change that, the matrix, "Verified" and "Could not verify" lists, and the coverage ledger with each selected route's state and its queries or reason. *(eval)*
- [x] **PRIOR-RPT-005**: While running a quick pass, the report shall give the verdict, the candidates the agent classified with their licenses, any other candidates found listed as seen but not classified, and the coverage ledger with each selected route's state and its queries or reason. *(eval)*
- [x] **PRIOR-RPT-006**: When a triggered route is unavailable and the verdict isn't inconclusive, the report shall list that route under "Could not verify". *(eval)*
- [x] **PRIOR-RPT-007**: The report shall say what the developer already knew about or had dismissed, or that the question in PRIOR-SRCH-001 went unanswered. *(eval)*

## Saving the note

- [x] **PRIOR-SAVE-001**: When a full-method run ends, the agent shall save the note at `<dir>/YYYY-MM-DD-<topic>.md`, where `<topic>` is a short kebab-case name for the need, not for a candidate. *(eval)*
- [x] **PRIOR-SAVE-002**: The agent shall resolve `<dir>` against the host repo's root as the first of: the directory the host repo's instructions name for research or prior-art notes, created if missing; an existing `docs/prior-art/`; an existing `research/` or `docs/research/`; a new `docs/prior-art/`. *(eval)*
- [x] **PRIOR-SAVE-003**: The agent shall never stage or commit the note. *(eval)*
- [x] **PRIOR-SAVE-004**: When an earlier-dated note on the same topic exists, the new note shall link it under "Supersedes". *(eval)*
- [x] **PRIOR-SAVE-005**: When a note on the same topic already exists with the same date, the agent shall update that note instead of creating another. *(eval)*
- [x] **PRIOR-SAVE-006**: If the agent can't write the note, or isn't in a repo, then it shall print the whole note in the conversation and say it wasn't saved. *(eval)*
- [x] **PRIOR-SAVE-007**: The note shall follow `references/note-template.md`, listing the snowball rounds with the serious candidates each added and whether the cap was reached. *(eval)*
- [x] **PRIOR-SAVE-008**: When the note backs a recorded decision, it shall give a refresh trigger: a date, a version or an event. *(eval)*

## Private content

- [x] **PRIOR-PRIV-001**: The agent shall treat the host repo as private when the forge reports it private or the host repo's own instructions say it is private, and as public otherwise, including when the forge can't be asked. *(eval)*
- [x] **PRIOR-PRIV-002**: While the host repo is public, the note shall contain only public sources, the developer's stated requirements, and material the developer has approved for the note. *(eval)*
- [x] **PRIOR-PRIV-003**: If a note to be saved in a public host repo would contain material the developer marked private, then in an interactive run the agent shall ask the developer whether to include it before saving, and in a non-interactive run it shall omit the material and record in the note that something was omitted. *(eval)*
- [x] **PRIOR-PRIV-004**: While the host repo is private, the agent shall cite internal sources in the note where they support a finding, such as the host repo's code, its decisions and other private repositories. *(eval)*
