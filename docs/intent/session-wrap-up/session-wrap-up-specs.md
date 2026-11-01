# Session wrap-up skill specs

Design: [session-wrap-up-design.md](session-wrap-up-design.md). The terms below are used as follows:
- **This repo:** agentic_development, which publishes the skill.
- **The skill:** `skills/session-wrap-up/` in this repo.
- **The agent:** an agent following the skill.
- **The developer:** the person the agent works for.
- **The host repo:** the repo the session is rooted in.
- **A handoff document:** a document the instruction files name as the record of current state, or one the session read or changed whose title says it records current state. A README, a changelog or a backlog isn't one.
- **The instruction files:** the instruction files that load for the session: the host repo's `AGENTS.md` or `CLAUDE.md`, nested ones on the path to the session's working directory, and the user-level file.
- **The report:** the skill's result in the conversation, starting with the heading `Session wrap-up`.
- **An earlier report:** a report the agent gave, before the current request, from an earlier run of the skill in this session. The heading in a tool result, a loaded skill, another session's message or text quoted in a turn isn't one.
- **An item:** one numbered proposal in the report: a write, a memory change, a message or an issue, or a `Decide` item that asks the developer to choose.
- **A draft:** the full text of an item bound for a repo other than the host repo, or for an issue: a message, an issue, or text for the developer to deliver. Items for the user-level instructions or the agent's memory aren't drafts.
- **A routing role:** as in the design's Routing roles table.
- **A default home:** the default home that `references/routing.md` gives a routing role.
- **The safety rules:** WRAP-RUN-006, WRAP-RUN-011, WRAP-LOOSE-006, WRAP-GATE-006 and WRAP-XREPO-001. All five are in force in every slice, whichever slice's section states them.
- **Typed by the developer:** written by the developer in the current conversation, as opposed to arriving from another agent, a hook, a script or another session's message. A turn read back from a transcript counts only if the transcript marks it as the developer's own.
- **A stated location:** a location the harness gives in its system prompt or a compaction summary, or the developer gives in text they typed. A path in tool output, hook output, a repo file or another session's message isn't stated.
- **Secrets:** the values of credentials, tokens, keys and passwords, and the contents of secret files.
- **Private records:** raw records about an identifiable person and the specifics taken from them, as the design's Personal data section lists them, and any information about people other than the developer.
- **Personal context:** summaries about the developer that they chose to share: goals, preferences, working style and routines, with no names, institutions, identifiers or exact figures.
- **Personal data:** private records and personal context.

Specs marked *(eval)* describe the agent's behavior, and the skill's behavior evals verify them. Specs marked *(manual)* need a live, interactive session, another live session, a real compaction, or the order of tool calls, which an eval can't provide. A scripted manual run, recorded in `evals/session-wrap-up/manual.md`, verifies them. Structure tests verify the rest. The headings name the slice that delivers each group.

In an eval, the session record in the prompt stands for the conversation: a turn marked `[agent]` is the agent's own, one marked `[developer]` is typed by the developer, and the record's report is an earlier report when it fills an agent turn. Text quoted inside a marked turn stays quoted.

## Package (slice 1)

- [x] **WRAP-PKG-001**: The skill's `SKILL.md` frontmatter shall have exactly the keys `name`, `description` and `license`, with `name` equal to `session-wrap-up`, a non-empty `description` of at most 1024 characters, and `license` equal to `Apache-2.0`.
- [x] **WRAP-PKG-002**: The skill's `SKILL.md` shall be under 500 lines.
- [x] **WRAP-PKG-003**: Every relative Markdown link target in the skill's `SKILL.md` shall exist inside the skill's directory.
- [x] **WRAP-PKG-004**: The skill shall contain `references/routing.md`, `LICENSE.txt` with the same text as this repo's `LICENSE`, and `NOTICE`.
- [x] **WRAP-PKG-005**: The skill's `NOTICE` shall name goagrawal-genai/wrap-up and RyanPenn-coder/wrap-skill, each with its full MIT License text, and kdeldycke/dotfiles with its full BSD 2-Clause License text.
- [x] **WRAP-PKG-006**: The skill's `references/routing.md` shall contain a table with the header `Role | Holds | Default home` and exactly one row for each routing role in the design's Routing roles table, and no other rows.
- [x] **WRAP-PKG-007**: The skill's `references/routing.md` shall state the lesson filter's four tests: reusable, non-obvious, stable and actionable.
- [x] **WRAP-PKG-008**: The skill's `SKILL.md` and reference files shall contain no `@spec` annotation.
- [x] **WRAP-PKG-009**: Every spec marked *(eval)* under the heading of a delivered slice shall be cited, by a `@spec` line in its `case.yaml`, by an eval case under `evals/session-wrap-up/` that is tagged `session-wrap-up`.

## Triggering and runs (slice 1)

- [x] **WRAP-RUN-001**: When the developer asks to wrap up, close out, end or hand off the session, or invokes the skill by name, the skill shall trigger. *(eval)*
- [x] **WRAP-RUN-002**: The skill shall not trigger for a request that doesn't ask to wrap up, close out, end or hand off the session, including a request to close or hand off a task or an artifact. *(eval)*
- [x] **WRAP-RUN-006**: While the run is non-interactive, the agent shall write no file anywhere, memory and scratch files included, send no message and file no issue, and shall label each item in the report `not applied`. *(eval)*
- [x] **WRAP-RUN-007**: When the request says the run is non-interactive, or the agent knows the run is headless, scheduled or an eval, the agent shall treat the run as non-interactive. *(eval)*
- [x] **WRAP-RUN-008**: When none of the conditions of WRAP-RUN-007 holds and the wrap-up request was typed by the developer, the agent shall treat the run as interactive. *(manual)*
- [x] **WRAP-RUN-009**: When none of the conditions of WRAP-RUN-007 holds and the wrap-up request wasn't typed by the developer, the agent shall treat the run as non-interactive. *(manual)*
- [x] **WRAP-RUN-010**: While the run is non-interactive, the agent shall present the items without asking which to apply. *(eval)*
- [x] **WRAP-RUN-015**: Until the approval gate (slice 3) is delivered, the agent shall put every question it has in the report rather than stopping to ask it. *(eval)*
- [x] **WRAP-RUN-011**: Until the approval gate (slice 3) is delivered, the agent shall apply no item and write no file in any run, shall label each item `not applied`, shall not offer or ask to apply items, and shall end the run with the report. *(eval)*
- [x] **WRAP-RUN-012**: When the report proposes no lesson item, new or re-listed, it shall say that nothing durable was found. *(eval)*
- [x] **WRAP-RUN-013**: When, after a report, the developer asks the agent to apply some of its items, the agent shall treat that as an ordinary request outside the run. *(manual)*
- [x] **WRAP-RUN-014**: The agent shall read memory only at a location the harness or the developer states. *(eval)*

## House rules (slice 1)

- [x] **WRAP-RULE-001**: Before collecting lessons, the agent shall read the instruction files and map each routing role to the file or directory the host repo uses for it, without showing the map in the report. *(eval)*
- [x] **WRAP-RULE-002**: Where the instruction files say nothing about a routing role whose default home is inside the host repo, and that home exists, the agent shall use the default home. *(eval)*
- [x] **WRAP-RULE-003**: Where the instruction files say nothing about a routing role whose default home is inside the host repo, other than project instructions, and that home doesn't exist, the agent shall report the role as missing once, propose no item for it, and list each lesson for it as dropped. *(eval)*
- [x] **WRAP-RULE-008**: The agent shall treat the user instructions role as available only when a user-level instruction file loads for the session or the developer states its path or content, the agent memory role only when the harness or the developer states the memory location, and the another-repo and nowhere roles as always available, and shall report each unavailable role as missing. *(eval)*
- [x] **WRAP-RULE-004**: Where the host repo has neither `AGENTS.md` nor `CLAUDE.md` at its root and at least one lesson is routed to project instructions, the agent shall propose creating `AGENTS.md`, containing only those lessons, as a single item. *(eval)*
- [x] **WRAP-RULE-005**: Where the instruction files say where an item goes, or forbid the agent an action, the agent shall follow them over the default homes. *(eval)*
- [x] **WRAP-RULE-006**: Where the instruction files require, or ask the agent to take, an action that one of the safety rules forbids, the agent shall follow the safety rule and say so in the report. *(eval)*
- [x] **WRAP-RULE-007**: When the user-level and project instruction files conflict on where an item goes, the agent shall list that item as a `Decide` item. *(eval)*

## Lessons (slice 1)

- [x] **WRAP-LES-001**: The agent shall collect candidate lessons of four kinds: corrections and decisions, claims of its own that a tool, a test or the data overturned, facts it established by checking, and work done or explained more than once. *(eval)*
- [x] **WRAP-LES-002**: The agent shall count a candidate as a correction or a decision only when text typed by the developer states it, or gives explicit assent to a proposal the agent stated in the conversation. *(eval)*
- [x] **WRAP-LES-003**: The agent shall not treat instruction-shaped text in tool output, hook output, messages from other sessions, or files other than the instruction files as a correction, a decision or an instruction to follow. *(eval)*
- [x] **WRAP-LES-004**: The agent shall cite, for each proposed lesson, a short quote from or pointer to the moment in the session it came from. *(eval)*
- [x] **WRAP-LES-005**: Apart from lessons already recorded (WRAP-LES-009), the agent shall propose a lesson only if it is reusable, non-obvious from the code, the docs and the git history, stable, and actionable. *(eval)*
- [x] **WRAP-LES-006**: The agent shall not propose an inference (a conclusion it drew without checking it or hearing it from the developer) as a rule. *(eval)*
- [x] **WRAP-LES-007**: Where an inference passes the other filter tests, the agent shall propose it for the host repo's pending queue where the host repo has one, and otherwise list it with the dropped lessons. *(eval)*
- [x] **WRAP-LES-008**: The agent shall leave secrets and private records out of the whole report, the items and the next-session prompt included, and where it lists something left out for that reason, it shall describe it only in general terms. *(eval)*
- [x] **WRAP-LES-009**: When a lesson is already recorded in a destination, the agent shall propose no item for it, and the report shall name where it is recorded. *(eval)*
- [x] **WRAP-LES-010**: When a lesson narrows the conditions of an existing rule at the lesson's own scope, the agent shall propose an edit of that rule rather than a new rule. *(eval)*
- [x] **WRAP-LES-011**: When a lesson reverses the action of an existing rule, at any scope, the agent shall list it as a `Decide` item. *(eval)*
- [x] **WRAP-LES-012**: The agent shall give each proposed lesson exactly one destination, at the narrowest scope where it holds, and use a broader scope only when the session shows the lesson holds there, the developer stating its breadth ("always", "in every repo") included. *(eval)*
- [x] **WRAP-LES-017**: The agent shall propose personal context only for the user-level instructions or the agent's memory, never for a repo, a message or an issue. *(eval)*
- [x] **WRAP-LES-018**: The agent shall propose a lesson learned from the developer's employer's or clients' internal material only once the developer has restated it in their own general terms, and shall list such a lesson as awaiting restatement until then. *(eval)*
- [x] **WRAP-LES-019**: When the agent can't tell whether an item's content is allowed at its destination, the agent shall strip it to what a public destination allows if a usable lesson remains, and otherwise leave the item out and ask about it in the report. *(eval)*
- [x] **WRAP-LES-020**: When a lesson refines a rule held at a broader scope than the lesson's own, without reversing its action, the agent shall propose a new rule at the lesson's scope rather than an edit of the broader rule. *(eval)*

## Report and next-session prompt (slice 1)

- [x] **WRAP-RPT-001**: The report shall present the items as one numbered list, with `Decide` items in a group of their own and the rest grouped by destination, each item giving its destination as a path, its change in one line, and its scope. *(eval)*
- [x] **WRAP-RPT-002**: The report shall list the lessons skipped as already recorded and where each is recorded, the lessons dropped, the routing roles reported missing, and the steps the procedure skipped in this run with the reason for each, leaving out any empty category. *(eval)*
- [x] **WRAP-RPT-003**: When an item belongs to a repo other than the host repo, and cross-repo routing (slice 5) isn't delivered, the agent shall put a draft of the item in a section of the report after the numbered list, for the developer to deliver, and edit nothing in that repo. *(eval)*
- [x] **WRAP-RPT-004**: Before putting a draft in the report, the agent shall remove from it any content that the instruction files mark private, and any secrets or personal data, and shall restate each lesson in it as a general rule that names no particular user. *(eval)*
- [x] **WRAP-RPT-005**: When the session leaves a next step other than applying the report's own items, the report shall end with the line `To start the next session, paste this:` directly followed by a code block of 3 to 8 lines inside its fences. *(eval)*
- [x] **WRAP-RPT-006**: The next-session prompt shall name the work that continues, the files to read first, the first step, and anything the developer must decide or provide first. *(eval)*
- [x] **WRAP-RPT-007**: When the session leaves no next step other than applying the report's own items, the report shall say so instead of giving a next-session prompt. *(eval)*
- [x] **WRAP-RPT-009**: The agent shall never propose creating a handoff or current-state document. *(eval)*

## Refinements (slice 2)

### Repeat runs

- [x] **WRAP-RUN-003**: When the conversation contains an earlier report, the agent shall collect lessons only from the turns after the latest one. *(eval)*
- [x] **WRAP-RUN-004**: When an earlier run in the conversation proposed items that the developer neither applied nor declined, the agent shall list those items again. *(eval)*
- [x] **WRAP-RUN-005**: When the developer declined an item from an earlier run in the conversation, the agent shall not propose it again unless evidence after that run changes it. *(eval)*
- [x] **WRAP-RUN-018**: The agent shall count an item as declined only when text typed by the developer refuses it, by number, by description or with "none"; an item left out of a choice isn't declined. *(eval)*
- [x] **WRAP-RUN-019**: The agent shall count an item as applied when its substance is in its destination, whoever put it there. *(eval)*
- [x] **WRAP-RUN-020**: Before listing an item again, the agent shall check it against the current state, and update it or drop it when that state has changed it. *(eval)*
- [x] **WRAP-RUN-021**: The report shall number re-listed items in its one sequence, repeat in full the draft of each one that has a draft, and cite the earlier report as each one's source. *(eval)*
- [x] **WRAP-RUN-022**: When the latest earlier report holds lessons awaiting restatement or questions the developer hasn't answered, the report shall list them again where it lists such lessons and questions. *(eval)*
- [x] **WRAP-RUN-023**: The agent shall not list again a lesson that an earlier report dropped. *(eval)*
- [x] **WRAP-RUN-024**: The agent shall not collect a reply that settles an item or a question from an earlier report as a lesson of its own. *(eval)*
- [x] **WRAP-RUN-025**: When the developer answers a `Decide` item or a question from an earlier report in words, and nothing has applied the answer, the agent shall replace it with the item that follows from the answer, which counts as re-listed. *(eval)*
- [x] **WRAP-RUN-027**: When the developer's answer to a `Decide` item or a question from an earlier report leads to no change, the agent shall remove it from the items and name it under Skipped. *(eval)*
- [x] **WRAP-RUN-028**: The report shall name under Skipped each earlier item it doesn't list again because the item was applied or the current state dropped it. *(eval)*
- [x] **WRAP-RUN-029**: When the developer amends an item from an earlier report in words, and the amendment hasn't been applied, the agent shall list the item again as amended. *(eval)*
- [x] **WRAP-RUN-026**: When the report's only lesson items are re-listed, it shall say that no new lesson was found. *(eval)*
- [x] **WRAP-RPT-010**: The report shall name under Skipped each item it left out because the developer declined it. *(eval)*

### Checks and one-line rules

- [x] **WRAP-LES-013**: When a lesson bound for the host repo is a rule that a tool the host repo already runs can check, and the instruction files have no rule on its subject, the agent shall propose a test, lint rule or hook for it, as the lesson's one item, rather than prose. *(eval)*
- [x] **WRAP-LES-028**: When a rule that a tool the host repo already runs can check holds across many repos, and the host repo comes from a shared template, the agent shall make the check an item for the template's repo rather than for the host repo. *(eval)*
- [x] **WRAP-LES-029**: The agent shall treat the host repo as coming from a shared template only when the instruction files name the template or the repo root holds a template tool's answers file. *(eval)*
- [x] **WRAP-LES-032**: When a rule that holds across many repos has no shared template to go to, the agent shall route it as a prose rule for the user-level instructions. *(eval)*
- [x] **WRAP-LES-030**: The agent shall not count a rule about how an agent invokes a tool as a rule a tool can check. *(eval)*
- [x] **WRAP-LES-026**: When a lesson is a rule that no tool the host repo already runs can check, the agent shall route it as a prose rule, not to the check role, and shall not drop it for want of a check. *(eval)*
- [x] **WRAP-LES-014**: When a lesson's destination is one of the instruction files, and that file has a rule on the lesson's subject that the lesson doesn't reverse, the agent shall propose replacing or tightening that rule, named in the item, rather than adding a line. *(eval)*
- [x] **WRAP-LES-023**: When a lesson's destination is one of the instruction files, and that file has no rule on the lesson's subject, the agent shall propose adding one line in the section it fits. *(eval)*

### After compaction

- [x] **WRAP-RUN-016**: When compaction has summarized earlier turns and the transcript, at a stated location, marks the developer's turns and holds an earlier report, the agent shall apply WRAP-RUN-003, WRAP-RUN-004 and WRAP-RUN-005 to the latest such report as if it were in the conversation. *(eval)*
- [x] **WRAP-RUN-017**: When compaction has summarized earlier turns, the agent can't review them, and the conversation shows signs of an earlier run of the skill, the report shall warn that items declined in that run may be proposed again. *(eval)*
- [x] **WRAP-LES-015**: When compaction has summarized turns that WRAP-RUN-003 leaves in scope and the harness or the developer states the transcript's location, the agent shall collect from those turns in the transcript. *(eval)*
- [x] **WRAP-LES-016**: When compaction has summarized turns that WRAP-RUN-003 leaves in scope and neither the harness nor the developer states the transcript's location, the report shall say that those turns weren't reviewed. *(eval)*
- [x] **WRAP-LES-021**: The agent shall read a session transcript only at a location the harness or the developer states. *(eval)*
- [x] **WRAP-LES-022**: If the transcript can't be read at the stated location, then the report shall say that the summarized turns weren't reviewed. *(eval)*
- [x] **WRAP-LES-031**: If the transcript doesn't mark which turns are the developer's, then the report shall say that the summarized turns weren't reviewed. *(eval)*
- [x] **WRAP-LES-024**: While the agent can't review summarized turns, it shall take no lesson from the compaction summary, and shall put any candidate the summary suggests in the report as a question. *(eval)*
- [x] **WRAP-LES-025**: While collecting from a transcript, the agent shall carry nothing from a tool result into the report except what a specific candidate needs. *(eval)*
- [x] **WRAP-LES-027**: While collecting from a transcript, the agent shall search the developer's turns and its own first, and shall open a tool result only to check a specific candidate. *(manual)*

### Handoff document

- [x] **WRAP-RPT-008**: Where the host repo has a handoff document and the session changed what it records, the agent shall propose an update covering only that change as an item. *(eval)*
- [x] **WRAP-RPT-011**: An update to a handoff document shall state project state and shall name no person. *(eval)*
- [x] **WRAP-RPT-012**: Where the update to a handoff document isn't applied and the next-session prompt lists the document among the files to read, the prompt shall flag the document as out of date. *(eval)*
- [x] **WRAP-RPT-013**: Where the instruction files name a handoff document that doesn't exist, the agent shall ask about it in the report rather than propose creating it. *(eval)*

## Loose ends (slice 3)

- [ ] **WRAP-LOOSE-001**: The agent shall list as loose ends, from the whole session, the promises not kept, deferred fixes, parked questions, background jobs still running, and drafts the developer still needs. *(eval)*
- [ ] **WRAP-LOOSE-002**: Where the host repo is a git repo, the agent shall list the uncommitted files that the session edited separately from other uncommitted changes, which it shall label "not from this session". *(eval)*
- [ ] **WRAP-LOOSE-003**: Where the host repo isn't a git repo, the agent shall skip the git checks and say so in the report. *(eval)*
- [ ] **WRAP-LOOSE-004**: Before listing a loose end, the agent shall check it against the current state, and drop it when it is already done. *(eval)*
- [ ] **WRAP-LOOSE-005**: The agent shall begin each loose end with one of the labels `Decide`, `Implement`, `Commit`, `Send` or `File`, or with a plain verb. *(eval)*
- [ ] **WRAP-LOOSE-006**: The agent shall run no git command other than `git status`, `git diff`, `git log`, `git show`, `git ls-files` and `git rev-parse`. *(eval)*
- [ ] **WRAP-LOOSE-007**: The report shall list the loose ends in the order to act on them. *(eval)*

## Approval (slice 3)

- [ ] **WRAP-GATE-001**: While the run is interactive, after presenting the items the agent shall ask which to apply: all, none, or a list of numbers. *(manual)*
- [ ] **WRAP-GATE-002**: When the developer's choice edits, splits or adds an item, the agent shall list the affected items again before applying any item. *(manual)*
- [ ] **WRAP-GATE-003**: After the developer chooses items, and before applying any, the agent shall show in one block the exact text of every chosen item: the lines to add, the before and after of each edit, and the full text of each draft. *(manual)*
- [ ] **WRAP-GATE-004**: After showing the exact text, the agent shall ask once for confirmation, and shall drop any item the developer drops at that point. *(manual)*
- [ ] **WRAP-GATE-005**: When the developer rewords an item at the confirmation, the agent shall show the reworded text and get confirmation before applying it. *(manual)*
- [ ] **WRAP-GATE-006**: The agent shall write, send or file nothing that isn't in a confirmed item. *(manual)*
- [ ] **WRAP-GATE-007**: Immediately before applying an item that edits a file, the agent shall re-read the file. *(manual)*
- [ ] **WRAP-GATE-008**: If the text an item edits has changed since the proposal, then the agent shall redraft the item and ask again, or skip the item and say so in the report. *(manual)*
- [ ] **WRAP-GATE-009**: The agent shall apply each edit as a change to the existing text, not by rewriting the whole file. *(manual)*
- [ ] **WRAP-GATE-010**: If applying an item fails, then the agent shall go on with the remaining items and list the failed item as a loose end. *(manual)*
- [ ] **WRAP-GATE-011**: Where the instruction files name fast checks, the agent shall run them after applying items. *(manual)*
- [ ] **WRAP-GATE-012**: If a fast check fails after applying items, then the agent shall report the failure with a proposed fix, and revert nothing. *(manual)*
- [ ] **WRAP-GATE-013**: After applying items, the agent shall compose the loose ends and the next-session prompt from the state the applied items leave. *(manual)*
- [ ] **WRAP-GATE-014**: The report shall list each applied item and where it was applied, and each proposed item that wasn't applied. *(manual)*

## Memory (slice 4)

- [ ] **WRAP-MEM-001**: Where the harness or the developer states the location of the agent's memory directory, the agent shall give each memory entry one verdict: keep, move, merge or retire. *(eval)*
- [ ] **WRAP-MEM-002**: The report shall show "keep" verdicts only as a count. *(eval)*
- [ ] **WRAP-MEM-003**: The agent shall propose a move as one item that adds the entry's text to its repo destination, chosen by the instruction files, and then removes the entry and its index line from memory. *(eval)*
- [ ] **WRAP-MEM-004**: If adding a move's text to the repo fails, then the agent shall leave the memory entry in place and list the move as a loose end. *(manual)*
- [ ] **WRAP-MEM-005**: The agent shall include the index edits in each merge or retire item. *(eval)*
- [ ] **WRAP-MEM-006**: Where neither the harness nor the developer states the location of a memory directory, the agent shall read no memory, and the report shall say that memory triage was skipped. *(eval)*
- [ ] **WRAP-MEM-007**: The skill's `references/routing.md` shall define the four memory verdicts: keep, move, merge and retire.

## Cross-repo routing (slice 5)

- [ ] **WRAP-XREPO-001**: The agent shall edit no file in a repo other than the host repo. *(eval)*
- [ ] **WRAP-XREPO-002**: When an item belongs to another repo and the agent can list other sessions, the agent shall treat as matching those sessions whose name is that repo's directory name, with `_` replaced by `-`, followed by `-` and two hex characters. *(manual)*
- [ ] **WRAP-XREPO-003**: When exactly one session matches, the agent shall draft the item as a message to that session. *(manual)*
- [ ] **WRAP-XREPO-004**: When several sessions match, the agent shall ask the developer which one to message, or, in a non-interactive run, name them all in the report. *(manual)*
- [ ] **WRAP-XREPO-005**: When no session matches, or the agent can't list other sessions, and `gh repo view` reports that the repo accepts issues, the agent shall draft the item as an issue on that repo. *(eval)*
- [ ] **WRAP-XREPO-006**: When neither a matching session nor an issue is available, the agent shall put the draft in the report for the developer to deliver. *(eval)*
- [ ] **WRAP-XREPO-007**: The agent shall make each message or issue self-contained, with a first line that states its subject, what to change and why, the sources to read, and what to report back. *(eval)*
- [ ] **WRAP-XREPO-008**: The agent shall not draft a message or issue asking its receiver to do something this session was denied permission to do. *(eval)*
- [ ] **WRAP-XREPO-009**: Before showing a message or issue for confirmation, the agent shall remove from it any content that the instruction files mark private, and any secrets or personal data, and shall restate each lesson in it as a general rule that names no particular user. *(eval)*
- [ ] **WRAP-XREPO-010**: After sending a message, the report shall give its status as delivered but not yet confirmed read, and list checking for a reply as a loose end. *(manual)*
- [ ] **WRAP-XREPO-011**: After filing an issue, the report shall give the issue's URL. *(manual)*
- [ ] **WRAP-XREPO-012**: The skill shall contain `references/cross-repo.md`, which states the session-name pattern and the parts of a self-contained message: subject line, change and reason, sources, and what to report back.
