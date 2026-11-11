---
parent: high-level-design
prefix: WRAP
---

# Session wrap-up skill

## Context and Design Philosophy

A coding session ends with knowledge that exists only in the conversation: corrections the developer made, facts found the hard way, decisions and their reasons, work left half done, and feedback that belongs to some other repo. A fresh session knows only what is written down where it loads. Without a fixed procedure, agents close sessions unevenly: they summarize instead of auditing, append to instruction files until nobody reads them, write to whichever file is handy, and leave the next session to rebuild the context.

This skill makes the close of a session one repeatable pass. The agent:
- collects the session's durable lessons and proposes a home for each, chosen by the repo's own rules for where knowledge lives;
- proposes moving agent memory that belongs in the repo into the repo's own docs, and retiring memory that is stale;
- lists the loose ends, each checked against the current state;
- routes feedback that belongs to another repo to a session rooted there, or to an issue on that repo;
- ends with a prompt the developer can paste to start the next session.

Nothing is written, sent or filed until the developer approves it, and the skill changes no git state. The skill is self-contained (HLD tenet 7) and portable (tenet 8): every step works in any agent that can read and edit files, and the Claude Code features it uses (the memory directory, session transcripts, and messages to other sessions) each have a fallback.

The design builds on [goagrawal-genai/wrap-up](https://github.com/goagrawal-genai/wrap-up) (MIT), per [the prior-art note](../../prior-art/2026-10-29-session-wrap-up-skills.md). The base skill routes by the role a destination plays, defers to the project's own rules, consolidates instead of appending, and refreshes the handoff. This design removes the three paths where the base skill writes without the developer seeing the text:
- applying "safe" changes when no user is present;
- skipping confirmation when the developer says "just do it";
- offering to commit.

It adds memory triage, cross-repo routing and the next-session prompt. Ideas also come from:
- hewonjeong/retro (MIT): choose items by number, and see the exact text before it lands;
- kdeldycke/dotfiles `wrapup-session` (BSD-2-Clause): loose ends re-checked against current state and labelled by action, and a lesson about a tool routed to that tool's repository;
- RyanPenn-coder/wrap-skill (MIT): the paste-ready prompt for the next session;
- benmfzen/claude-memory-triage (MIT): one verdict per memory entry (keep, move, merge, retire);
- the-c0d3r/claude-skill-memory-promotion (MIT): its categories for where a memory entry belongs;
- ozzy-labs/skills `lessons-triage` (MIT): one batch approval for the issues to file;
- sentimony/agentic-workflow `session-learnings` (MIT, `SKILL.md:42-56` at 612e661): the four-part filter for what counts as a lesson, and counting only the developer's own words as corrections.

## Platform facts

Checked against Claude Code 2.1.312 on Linux on 2026-10-29, unless marked otherwise.

- **Memory location.** Auto-memory defaults to `~/.claude/projects/<project-slug>/memory/`: a `MEMORY.md` index and one file per entry. The slug is the working directory's path with `/` and `_` replaced by `-`. The location is a setting (`autoMemoryDirectory`), and memory can be turned off (`autoMemoryEnabled: false`, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY`). When memory is on, the session's system prompt states the directory.
- **Transcripts.** Each session's transcript is a JSONL file at `~/.claude/projects/<project-slug>/<session-id>.jsonl` by default. It keeps the turns a context compaction summarized. The system prompt doesn't state its path, but each compaction summary does (checked on 2.1.314, 2026-10-30): it ends by telling the agent to read the full transcript at that path if it needs detail the summary left out. The format is internal and undocumented, so it can change between versions. The file mixes the developer's turns with the agent's, tool results (stored as `user` entries with no `origin`), attachments and bookkeeping entries. Other `user` entries can carry `origin.kind`: `human`, with a top-level `promptSource` of `typed`, marks the developer's own turn; `peer` marks messages from subagents and other sessions; `task-notification` marks harness notices. An entry with no `origin` is never a typed turn, and that includes a question-tool answer, which is stored as a tool result whose `toolUseResult` holds `answers` and `annotations`. A long session's file runs to tens of megabytes, so it is searched, not read whole.
- **Question tool.** `AskUserQuestion` takes 1 to 4 questions per dialog, each with 2 to 4 options. A single-select option can carry a preview. The developer can also answer in free text, or add a note to the option they pick. The dialog can hide the conversation above it, and a long preview is cropped.
- **Other sessions.** `ListAgents` lists the other Claude Code sessions on the machine. Each row gives a name, a short reference, the kind, the status (idle or busy) and the start time, but no working directory. A session's name is its directory's name with `_` replaced by `-`, then `-` and two hex characters (`my-repo-3f` for a session in `my_repo`). The current session isn't listed. Several sessions can be rooted in the same repo.
- **Messages to other sessions.** `SendMessage` to a listed name delivers the message to that session's inbox. Delivery doesn't mean the receiving agent has read it. A receiver running in a different permission mode holds the message for its own user's approval. The receiver sees only the first line until it expands the message. The sender can ask to be notified once when the receiver next goes idle.
- **Concurrent writers.** Sessions rooted in the same repo read and write the same files, so a file can change between two turns of one session.
- **Issues.** `gh issue create` takes `--title`, `--body-file` and the inherited `--repo`. `gh repo view --json visibility,hasIssuesEnabled` reports whether a repo is public and accepts issues (checked on a live repo, 2026-11-01). Filing has not been tried, since it is an outside effect.
- **Cloud sessions** (unverified): a fresh container may have no auto-memory directory, no other sessions and no authenticated `gh`. Every step that uses one of them has a fallback.
- **Evals.** `claude plugin eval` runs one prompt per case, and its options include no multi-turn conversation. Each run gets a sandboxed home directory and configuration directory, and its system prompt states a memory directory inside that sandbox. So an eval can't produce a run with no stated memory location; that case is checked by hand. The sandbox home is itself a git repo, so a case can't run outside git either. A single `--case` flag selects one case: given several times, only the last applies.

## Package layout

| Path | Contents |
|---|---|
| `skills/session-wrap-up/SKILL.md` | The procedure: when it runs, the steps, the approval gate, the report and the next-session prompt. Under 500 lines |
| `.../session-wrap-up/references/routing.md` | The routing roles and their default homes, the kinds of lesson, the lesson filter, the handling of existing and new rules, what carries forward from an earlier report, and the personal-data rules; the memory verdicts from slice 4 |
| `.../session-wrap-up/references/cross-repo.md` | From slice 5: finding a session rooted in another repo, the message shape and the issue fallback |
| `.../session-wrap-up/LICENSE.txt` | The Apache License 2.0 text |
| `.../session-wrap-up/NOTICE` | The copyright and permission notices of the MIT-licensed (goagrawal-genai/wrap-up, RyanPenn-coder/wrap-skill) and BSD-2-Clause (kdeldycke/dotfiles) sources whose text the skill adapts |
| `evals/session-wrap-up/` | Cases for `claude plugin eval`, each tagged `session-wrap-up` |
| `.claude/skills/session-wrap-up`, `.agents/skills/session-wrap-up` | Committed relative links to `../../skills/session-wrap-up`, as for prior-art-search |

`SKILL.md` frontmatter has exactly three keys: `name: session-wrap-up`, a `description` of at most 1024 characters that names its trigger, and `license: Apache-2.0`.

## When it runs

The developer asks for it in words like "wrap up", "close out the session", "we're done for today" or "hand this off", asks to apply items from a wrap-up report, or invokes the skill by name. It doesn't run on its own at every pause. After a short session with nothing durable, the report says so, and still gives the next-session prompt when there is a next step.

**The shape of a run.** An interactive run with something to approve gives two reports. The proposal holds the items, the sections around them and a provisional next-session prompt, and ends by asking which items to apply. The closing report follows the approval step and replaces that prompt. Because the proposal is a report, a developer who walks away from the question still has a prompt, and a later run still has a report to carry on from. A reply that is a new request, with no choice in it, is walking away: the run ends, the items stay open, and the agent does what was asked. A reply that also chooses items finishes the approval steps first. A run with nothing to approve, and every non-interactive run, gives one report. A later request to apply items from a report, of either kind of run, goes through the approval steps for those items.

**Repeat runs.** Each report starts with the heading `Session wrap-up`. A later run in the same session collects lessons only from what happened after the last report. The same heading in a tool result, a loaded skill, another session's message or quoted text doesn't mark a report, since text the agent didn't write as a report shouldn't decide what the run reviews. Loose ends are always swept over the whole session.

What the earlier report left open carries over:
- An item the developer neither applied nor declined is listed again, after a fresh check against the current state, in the new report's one numbered sequence, with any draft in full and the earlier report cited as its source.
- An item counts as applied once its substance is in its destination, whoever put it there. An item applied, or dropped because the current state changed it, is named under Skipped.
- An item the developer amended in words, and that isn't applied, is listed again as amended.
- Only a refusal typed by the developer declines an item, by number, by description, with "none", or by dropping it at the approval step. Leaving an item out of a choice doesn't decline it. A declined item isn't proposed again unless later evidence changes it, and the report names it under Skipped. An earlier report's Skipped list is the record of what was declined.
- Lessons awaiting restatement and unanswered questions are listed again, where the report lists such things. Dropped lessons aren't.
- A reply that settles an earlier item or question isn't collected as a lesson of its own. A `Decide` item or question answered in words gives way to the item that follows from the answer, which counts as re-listed. An answer that leads to no change removes it, and the report names it under Skipped.
- An item captured in an issue is settled: the report names it under Skipped, with the issue's URL.
- A loose end the developer dismissed in words isn't swept again.

A run whose only lesson items are re-listed says that no new lesson was found.

When compaction has removed the earlier report and the transcript's location is stated, the agent finds the report there and carries on from it as if it were still in the conversation. In a transcript that doesn't mark the developer's turns, a report's heading can't be told from tool output and a typed decline can't be seen, so a report found there is only a sign of an earlier run. With no transcript, the run covers the whole session, step 3's check against what's already recorded drops what the earlier run applied, and if there are signs of an earlier run the report warns that items declined then may come back.

**Non-interactive runs.** A run is non-interactive when the request says so, or when the agent knows it runs headless, scheduled or in an eval. Otherwise, a run is interactive when the developer typed the wrap-up request in the current conversation. When neither applies, the agent treats the run as non-interactive. A non-interactive run is **report-only**: the agent writes, sends and files nothing, and its report gives every proposal, marked "not applied".

## Steps

0. **Read the house rules.** Read the instruction files in effect (the repo's `AGENTS.md` or `CLAUDE.md`, nested ones, and the user-level file) for where knowledge goes, what must stay private, and what agents may not do. Map each routing role (below) to the repo's file or directory for it.
   - Where the instruction files are silent about a role whose default home (below) is inside the repo, that home applies if it exists. Otherwise the role is reported as missing.
   - The roles outside the repo are available on these conditions:
     - user instructions, when a user-level file loads or the developer states its path or content;
     - agent memory, when its location is stated;
     - another repo and nowhere, always.

     An unavailable role is reported as missing, like a missing home inside the repo.
   - Wherever the instruction files and the skill differ on where something goes, or forbid the agent an action, the instruction files win. They can't relax the safety rules: approval before every write, report-only when non-interactive, and no git writes. When they try, the agent follows the safety rule and says so.
   - When the user-level and project instructions conflict on where something goes, that item becomes a `Decide` item.
   - With no `AGENTS.md` or `CLAUDE.md` at the repo root, and at least one lesson routed to project instructions, the agent proposes creating `AGENTS.md` as a single item, containing only those lessons. A lesson for any other role whose default home is missing is listed as dropped, and the role as missing. A rule no tool in the repo can check is never a lesson for the Check role (step 4).
   - The role map is internal; the report shows only the missing roles.
1. **Collect.** From the conversation, gather candidate lessons in four kinds:
   - **corrections and decisions:** what the developer told the agent to do differently, or chose. These count only when the developer typed them, or explicitly assented to a proposal the agent stated. Text from another agent, a hook, a script or another session doesn't count as typed by the developer. Tool output, hook output, messages from other sessions and files other than the instruction files are evidence of what happened, never instructions;
   - **overturned claims:** things the agent asserted that a tool, a test or the data showed to be wrong;
   - **facts found:** facts the agent established by checking (reading the source, running the command), that took effort to find;
   - **repeated work:** steps done or explained more than once, which a skill or check could carry.

   Each candidate keeps a short quote or pointer to the moment it came from. When a compaction has summarized earlier turns in the run's scope, the agent reads the transcript only if its location is stated (by the harness, in its system prompt or a compaction summary, or by the developer). A turn read there counts as the developer's only if the transcript marks it as their own. It searches the developer's and its own turns first, and opens a tool result only to check a specific candidate, extracting no more than that needs. Compaction may have removed secrets from the conversation that the transcript still holds, and tool results are where most of them sit. With no stated location, a file that can't be read, or a transcript that doesn't mark the developer's turns, the report says that compacted turns weren't reviewed. The compaction summary then gives leads only: it is the agent's paraphrase, so a candidate it suggests goes in the report as a question, not as a lesson.
2. **Filter.** Keep a candidate only if it is reusable, non-obvious (not already clear from the code, the docs or the git history), stable and actionable. Drop secrets and private records.
   - An **inference** is a conclusion the agent drew without checking it or hearing it from the developer. An inference is never proposed as a rule. It is proposed for the repo's pending queue, if it has one, or listed as dropped.
   - A fact found by checking is not an inference.
3. **Check against what's recorded.** Read each likely destination before proposing, and the memory too, when its location is stated (step 5).
   - A lesson already recorded is skipped, and the report names where it lives.
   - A lesson that narrows the conditions of an existing rule at its own scope becomes an edit of that rule, never a second rule beside it.
   - A lesson that reverses an existing rule's action, at any scope, becomes a `Decide` item.
   - A lesson that refines a rule held at a broader scope without reversing its action (a repo-specific refinement of a user-level rule) becomes a new rule at the lesson's scope; the broader rule is left alone.
   - A lesson learned from the developer's employer's or clients' internal material is listed as awaiting restatement until the developer restates it in their own general terms.
4. **Route.** Give each kept lesson one destination by role, at the narrowest scope where it holds: the repo, a directory with its own instruction file, another repo, or every repo (the user-level instructions). A broader scope needs evidence that the lesson holds there; the developer stating its breadth ("always", "in every repo") counts.
   - A rule that a tool the repo already runs can check becomes a proposed test, lint rule or hook, as the lesson's one item, not prose. With no such tool it stays a prose rule, so a correction the developer typed isn't lost. A check is only for a lesson with no rule on its subject: a lesson already recorded as prose is skipped (step 3), and one that narrows, tightens or reverses a rule is handled as a change to that rule, whatever could check it. Personal context never becomes a check, since it goes to no repo file, and neither does a rule about how an agent invokes a tool.
   - A checkable rule that holds across many repos belongs in the shared template the host repo comes from, if it has one: the check goes to the template's repo as a cross-repo item, so every repo built from the template gets it. The host repo has a template when the instruction files name one or its root holds a template tool's answers file (such as `.copier-answers.yml`). With no template, a rule for every repo stays prose in the user instructions.
   - A lesson for an instruction file that has a rule on the same subject is merged into that rule, replacing or tightening it, and the item names the rule. A lesson on a new subject is added as one line in the section it fits.
5. **Triage memory.** When the agent has a memory directory whose location the harness or the developer states, read its index and entries, and give each entry one verdict:
   - **keep;**
   - **move** to a repo destination, per the repo's rules;
   - **merge** into another entry;
   - **retire,** because it is stale, contradicted or recorded elsewhere.

   A move is one item: it adds the text to the repo first, then removes the entry from memory, along with its index line. A merge or retirement includes its index edits. The list shows "keep" verdicts as a count, not as items. The step runs in every wrap-up. With no memory directory, or one whose location nobody states, it is skipped and the report says so.
6. **Sweep loose ends.** List what the session leaves open:
   - promises not kept;
   - deferred fixes and parked questions;
   - files this session edited and the developer hasn't committed (from its own record of edits, checked with read-only `git status`). Other uncommitted changes are listed separately as "not from this session". When compaction has taken that record and no reviewable transcript restores it, a file's origin can't be told, and it is listed as "origin unknown". Those two lists are for information: they carry no action label and aren't a next step;
   - background jobs still running;
   - drafts the developer still needs, other than the text of a numbered item.

   The sweep covers the whole session, turns before an earlier report included, and the compaction rules of step 1 apply to it: a loose end that only a compaction summary suggests goes in the report as a question. Re-check each one against the current state, and drop anything already done or abandoned. One that can't be checked stays listed. Each gets an action label: `Decide`, `Implement`, `Commit` (for the developer), `Send` (a cross-repo message), `Issue` (an issue to file), or a plain verb.

   Loose ends are a list of their own, not items: they aren't numbered and can't be chosen at the approval step, so "all" never starts new work. They run in the order to act on them: what others depend on first, then `Decide`, then the rest. Outside a git repo, the git checks are skipped and the report says so.
7. **Cross-repo items.** A lesson or loose end that another repo owns becomes a cross-repo item (see Cross-repo routing).
8. **Propose.** Present one numbered list: `Decide` items in a group of their own, and the rest grouped by destination. Each item gives:
   - its destination, as a path;
   - the change, in one line;
   - its scope.

   Full drafts (text bound for another repo or an issue) follow the list in a section of their own.

   Pending-queue entries, memory changes, messages, issues, items carried from an earlier report (see Repeat runs) and a handoff update (see Next-session prompt) are items like any other. In an interactive run with at least one selectable item, the agent then asks which to apply: all, none, or a list of numbers. An item that can't yet be delivered isn't selectable, and the report says why (see Open Questions). With no selectable item, this report is the run's last. When the reply edits an item, splits one or adds one, the agent re-lists the affected items and goes on to step 9 without asking for the choice again. A chosen `Decide` item has no text to show, so the agent first asks for its answer and re-lists the item that follows. Questions stay in the report; the developer may answer them here, and needn't.
9. **Apply the approved items.** First the developer sees the exact text of every chosen item: the lines to add, the before and after of each edit, the whole of a new file, the full message or issue. They see it even if they said to skip this.
   - **With a question tool that shows previews,** and when every chosen item's text is at most 8 displayed lines (short enough for a preview to show whole), each item gets its own question, naming its number and destination, up to the tool's limit per dialog, then the next dialog. Lines are counted over the whole text, before and after together, with each 80 characters of a line counting as one. The option that applies the text previews it. The options are to apply as shown, to leave the item for now and to decline it, and the developer can adjust the item in a note on any option or in free text.
   - **Otherwise,** the agent shows all the text in one plain-text message and asks once.

   A declined or dropped item counts as declined. An item left for now stays open, and so does each item in a dialog dismissed without an answer. An adjustment can change an item's text or its destination: the agent redrafts the item, screens it again against the privacy rules, warns if the new text breaks them, shows it, and confirms it before going on. Only the developer's own reply confirms anything; a reply that doesn't clearly confirm is asked again. An item edited, split or added at step 8 gets the same privacy check, and any changed item is checked again for whether it is selectable.

   **Apply now or capture in an issue.** Work may be in progress that the session's lessons shouldn't be committed with. So once the text is confirmed, and where the host repo accepts issues, the agent asks whether to apply the items now or capture them in one GitHub issue on the host repo, and shows the full issue before filing. The issue is self-contained: each item's destination and exact text, so a later session can apply them. It is held to what a public destination allows unless the repo is known to be private, and an item it can't hold stays an open item. Items for the user-level instructions aren't repo work, so they aren't deferred: they're applied now. Leaving the items open is always a choice too. Where the repo can't take an issue, or `gh` isn't available, the agent says so and offers to apply now or leave the items open. An adjusted issue is shown again. A refused issue returns to applying now or leaving the items open, and a failed filing leaves them open.

   To apply, for each item in order:
   - re-read the target right before writing, since another session may have changed it. If the text to edit has changed since the developer saw it, or a file to create now exists, redraft the item, show it again and ask, or skip it and report that. The run's own earlier edits don't count as a change;
   - make the edit as a reviewable change to the file (an exact before and after), not by regenerating the whole file;
   - write nothing outside the approved items.

   An approved message is sent, and an approved issue filed, only as drafted. When a write fails, the agent goes on with the other items, except those that depend on the failed one, and each stays an open item. Afterwards, if host-repo files changed and the instruction files name fast checks, it runs them and re-reads what changed. A check known to change git state is skipped, and the report says so. The report names any file a check changed. A failing check is reported with a proposed fix, as text, not as a new approval; nothing is reverted on the agent's own initiative.
10. **Report and hand off.** After step 9, re-check the loose ends, then write the closing report:
    - what was applied, and where;
    - what was captured in an issue, with its URL;
    - what was proposed but not applied, and what was declined;
    - what was skipped because it was already recorded, and where it lives;
    - roles the repo doesn't implement, and steps that were skipped;
    - cross-repo items sent or filed, with their status ("delivered, not yet confirmed read" for a message);
    - the loose ends, in the order to act on them.

    The report ends with the next-session prompt. It offers no work beyond its items and the approval question, such as a commit message: the developer asks for that when they want it.

## Routing roles

Destinations are named by the role they play, and step 0 maps each role to the repo's own file. A default home applies only where the instruction files are silent:

| Role | Holds | Default home |
|---|---|---|
| Project instructions | How agents should work in this repo | `AGENTS.md` at the repo root, or `CLAUDE.md` where that is the only one |
| User instructions | How agents should work in every repo | The user-level instruction file (`~/.claude/CLAUDE.md` under Claude Code) |
| Design and decisions | What the system should do, and why | The repo's design docs or decision records |
| Knowledge base | Reference material read on purpose | The repo's `docs/` or wiki |
| Skill | A repeatable procedure | The skill that owns it, or a new skill |
| Check | A rule a machine can enforce | A test, lint rule or hook |
| Agent memory | Facts about the user and how they like to work, which no repo owns | The harness's memory directory |
| Pending queue | Inferences to review later | The repo's backlog |
| Another repo | Anything that repo owns | A message to a session rooted there, or an issue on it |
| Nowhere | One-offs and transient detail | — |

## Personal data

The test is whether an item quotes or identifies a record, not what its subject is. "Prefers small, reviewable diffs" describes how the developer works, and may be routed. A lesson that quotes a bank statement may not, whatever it teaches.

- **Secrets** (credentials, tokens, keys, passwords, secret files) go nowhere. The agent doesn't quote them.
- **Private records** are raw records about an identifiable person and the specifics taken from them: financial statements, transactions and exact amounts; medical, legal and immigration records; private messages and mail; itineraries and booking numbers; account identifiers; contact details and addresses; anything the developer marks confidential; and any information about other people. They go nowhere in the report.
- **Personal context** is summaries about the developer that they chose to share: goals, preferences, working style, routines and patterns, with no names, institutions, identifiers or exact figures.

| Destination | May hold |
|---|---|
| The user-level instructions, or the agent's memory | Personal context about how the developer works; no private records and no names of other people |
| A private repo | What that repo's own privacy rules allow; with none, as a shared repo |
| A shared or public repo, an issue, a pull request | No personal data; each lesson restated as a general rule that names no particular user. An issue counts as public unless its repo is known to be private |
| A message to another session | What the receiver needs for its task, at the level of the strictest place it will write |

Material from the developer's employer or clients (internal tools, code and processes) is never quoted or reconstructed. A lesson learned from it becomes routable only once the developer restates it in their own general terms. When the agent can't tell whether content is allowed at a destination, it treats the destination as public, or leaves the item out and asks.

## Cross-repo routing

The skill edits no repo except the one the session is rooted in. An item that another repo owns goes there by the first of these that is available:
1. **A message to a session rooted in that repo.** The agent lists the other sessions with `ListAgents`. A session matches when its name is the target repo's directory name, with `_` replaced by `-`, followed by `-` and two hex characters. With one match, the agent drafts a message to it; with several, it asks the developer which to use (in a report-only run, it names them all).
2. **An issue on that repo.** The agent checks with `gh repo view` that the repo accepts issues, and drafts a title and body.
3. **A draft in the report,** for the developer to deliver, when neither of the others is available.

The lookups (`ListAgents`, `gh repo view`) are read-only and run before approval; sending and filing wait for it.

A message or issue body is self-contained: what to change and why, the sources to read, and what to report back. Its first line says what it is about, because that line is all the receiver sees at first. It never asks the receiver to do something this session was denied permission to do. Before any draft goes out, by any channel, the agent screens it against the instruction files' privacy rules and the Personal data section, and leaves out what they don't allow. After a message is sent, the report gives its status as "delivered, not yet confirmed read", and a loose end says to check for the reply.

## Next-session prompt

The report ends with a block the developer can paste to start the next session, under the line **To start the next session, paste this:**, in a code block. It is written for a session that has never seen this one, and reflects the state the run leaves (in a proposal, the state before any item is applied):
- what work continues, and where its state lives (the files to read first);
- the first concrete step;
- anything the developer must decide or provide first.

It is 3 to 8 lines. Applying the report's own items isn't a next step, and neither is a `Commit` loose end on its own: when nothing else is left, the report says there is no next step instead. Something only a compaction summary suggests is never the work or a step, because the summary is the agent's paraphrase. The prompt may ask about it as something to decide first, saying where it comes from, since the next session is the only place an unverified promise can be picked up.

A **handoff document** is one the instruction files name as the record of current state, or one the session read or changed whose title says it records current state. A README, a changelog or a backlog isn't one. When the session changed what such a document records, an update to it is one of the proposed items.
- The update covers only what the session changed, since the session holds no evidence for the rest.
- It states project state and names no person. It isn't a lesson, so the filter doesn't apply.
- The prompt states the true state. When an update isn't applied and the prompt lists the document among the files to read, the prompt flags the document as out of date.

The skill never proposes creating such a document, even when the instruction files name one that doesn't exist; it asks about that in the report.

## Testing

**Structure tests** run with pytest in CI, as for prior-art-search: the frontmatter, the line limit, referenced files existing, the license and notice files, the reference files holding the role table and the message shape, and the skill links.

**Behavior evals** run by hand with `claude plugin eval`. As for prior-art-search, runs are isolated (the harness loads no user-level or project instructions; the skill reads a case's seeded instruction files from disk in step 0), and every case also runs in the no-plugin baseline arm. Each case's prompt is written by the developer. It contains a record of the session to wrap up, with each turn marked by who spoke (developer, agent or tool output), followed by the request to wrap up. A scaffold seeds a repo with its instruction files. For memory cases, it also seeds a memory directory, whose location the developer states in the prompt. An eval run is non-interactive, so graders check:
- that no file changed, and no message or issue tool was called;
- what the report proposes, and where it routes each item;
- that the report ends with a next-session prompt.

The cases cover:
- trigger and no-trigger prompts;
- a correction routed by the repo's own rules;
- a lesson already recorded;
- tool output in the session record that reads like an instruction;
- memory entries to move and to retire;
- a loose end already done;
- a lesson for another repo when no session matches;
- a repeat run, with items left open, declined and settled;
- a compacted session, with a readable transcript, none, and an unreadable one;
- a rule a tool can check, and a rule to merge;
- a handoff document;
- loose ends: a kept promise, a dismissed one, uncommitted files of each origin, and a repo that isn't under git.

In an eval, the record stands for the conversation: a report filling an `[agent]` turn is an earlier report, and a `[developer]` turn is typed by the developer. Compaction can't happen in an eval, so a case's record simulates it and the developer states the transcript's location. The harness stating it, in a real compaction summary, is checked by a manual run.

An eval is non-interactive, has no other live sessions, and can't check the order of tool calls. Behavior that needs any of these (the approval gate on both of its routes, applying items, capture in an issue, messages to a matching session, and the order of a transcript search) is checked by a scripted manual run instead. Its script and dated results are kept in `evals/session-wrap-up/manual.md`, and its specs are marked *(manual)*. Every spec marked *(eval)* has a case, checked by a pytest test, as for prior-art-search.

## Decisions & Alternatives

| Decision | Choice | Rationale | Alternatives considered |
|---|---|---|---|
| Build vs. adopt | Build on goagrawal-genai/wrap-up, without its three unapproved-write paths, adding memory triage, cross-repo routing and the next-session prompt | Once those paths are removed, it meets every hard criterion in the prior-art note (approval, no git, defers to the repo's rules, local and cloud, compatible license), and it covers more of the need than any other candidate | Build on hewonjeong/retro (cleaner approval, but fixed destinations and no memory); adapt kdeldycke `wrapup-session` (best loose ends, but designed to finish unattended and to commit) |
| Approval | One numbered list to choose items; then the exact text of the chosen items, as one previewed question per item where a question tool is available and the text fits, otherwise in one plain-text message, confirmed once | The developer sees every word that will persist and can still drop or adjust an item. Full text for every proposal up front would make the list too long to read. A dialog can hide the conversation and crops long previews, so text shown above a dialog, or one long preview, can hide what is being approved. Per-item questions keep each item's text visible while batching still needs only one pass; the plain-text route keeps the step working in any agent (tenet 8) and carries items too long to preview | Choose by number, then write straight away (hewonjeong; the text is seen only as it lands); plain text only (one route, but loses the dialog's Apply and Drop and its notes); one text block in a question (cropped); approve each item in its own round, without selection (slow) |
| Apply now or capture in an issue | After the text is confirmed, offer one issue on the host repo instead of applying, where the repo accepts issues | Other work may be under way at the end of a session, and the lessons shouldn't be committed with it. An issue keeps the confirmed text for a later session and leaves the tree alone | Always apply (ties the lessons to unrelated work); leave items open for a later wrap-up (lost if no one runs one); a local file (a write the repo didn't choose, and it needs committing too); a choice per item (more questions for a choice that is usually about the whole set) |
| Interactive run shape | The proposal and the closing report are both reports, and the proposal holds a provisional next-session prompt | The developer may walk away from the question. A later run then still has a report to carry on from, and the prompt isn't lost | One report after the gate (an abandoned gate leaves nothing); the proposal isn't a report (a later run re-collects the whole session) |
| Who can confirm | Only the developer's reply, typed or through the question tool; an unclear reply is asked again | Another session's "apply all" isn't approval. A question-tool answer is the developer's own, though it is stored as a tool result. After compaction, the closing report's Skipped list is the record of what was declined, so nothing depends on the transcript's format for tool results | Typed text only (a dialog could never approve) |
| Loose ends | A list of their own, not numbered and not selectable | "All" must not start code work, and an action for the developer isn't a write the gate can apply | Number them with the items (a chosen `Implement` would be new work) |
| Answers at confirmation | Apply as shown, Not now, or Decline, and a dismissed dialog counts as Not now | Seeing the text can change the developer's mind in either direction. Declining stops an item returning; putting it off must not, and a label that doesn't say which invites the wrong one | Apply or Drop only (no way to put an item off once its text is showing) |
| A later request to apply | Goes through the approval steps, after any kind of run, and the description triggers on it | The rule that the developer sees every word before it lands holds however the request arrives, and after compaction the skill's text may no longer be loaded | An ordinary request, outside the run (skips the text); refuse after a non-interactive report (the developer has to run the whole wrap-up again) |
| A new request at the gate | Ends the run; the items stay open | The developer has moved on, and holding their request hostage to a question is worse than leaving items open, which later runs carry forward | Keep asking for a choice (blocks the work) |
| Fast checks | Only checks the instruction files name, only when host-repo files changed; one known to change git state is skipped; files a check changes are reported | The approval rule binds what the agent writes. Read as binding a check's side effects, almost no check could run, since tests write caches. The git rule stays absolute, and instruction files can't relax it | Run nothing (loses the check); run anything named (a hook runner can stash) |
| `Commit` and the next step | A `Commit` loose end alone isn't a next step | Almost every applied run leaves uncommitted edits, so every run would otherwise open the next session with "commit" | Count it as a next step |
| Non-interactive runs | Report-only, and the default when the agent can't tell | With nobody to approve, nothing may be written. The report keeps the work for the developer to apply later | Apply reversible items (the base skill's choice) |
| Git | A named list of read-only commands (`status`, `diff`, `log`, `show`, `ls-files`, `rev-parse`); never stage, commit, branch or push | Committing is the developer's review step, and branches move only when they decide. The list is named, not described as "read-only", because several commands that read with no arguments write with some (`branch`, `config`, `remote`, `tag`), and a named list can be checked | Offer to commit (the base skill); commit on a second invocation (kdeldycke) |
| Instruction files vs. safety rules | Instruction files decide where things go and can forbid actions, but can't relax approval, report-only mode or the git rule | A skill installed in every repo has to be safe to run in any of them; a line in one repo's instructions shouldn't turn it into a tool that writes or commits unasked | Instruction files win everywhere (a repo could opt into unattended writes or commits) |
| Personal data | Judged by whether an item quotes or identifies a record, with what may go where set per destination | A rule by topic would block useful lessons about how the developer works, or let a quoted record through under a harmless subject | Ban everything personal (loses working-style lessons, the main content of user-level instructions); leave it to each repo's rules (most repos have none) |
| Routing | By role, mapped to the repo's own files in step 0; defaults only where the instruction files are silent | Repos differ in where knowledge lives. A fixed list of file names would write to the wrong place in a repo with its own rules | Fixed destinations (`CLAUDE.md`, memory, `docs/`) |
| Instruction files | Merge into a rule on the same subject; a new subject gets one line in the section it fits | Every line of an always-loaded file costs every later session, and appending without consolidating is how such files grow until nobody reads them. A new subject has nothing to merge into, and a rule of the skill shouldn't lose a lesson over that | Append with a size budget only (kdeldycke's 400-character cap); require a removal for every addition (contrived when nothing is stale) |
| Checks instead of prose | Only when a tool the repo already runs can check the rule | Almost any rule is checkable in principle, so that test would turn most lessons into proposals for new tooling. A repo with no such tool keeps the lesson as prose rather than losing a correction. A check that holds across many repos goes to their shared template, where one change reaches them all | Anything checkable in principle (changes what ordinary rules become, and drops lessons in repos with no checks); keep every check in the host repo (each repo built from the template repeats the work) |
| Memory and transcript locations | Only a location the harness or the developer states | Both default paths can be moved by settings, and memory can be off. A path the agent derives may name the wrong directory | Derive the default paths from the working directory |
| When memory triage runs | Every wrap-up, with "keep" verdicts shown only as a count | Memory that is triaged only on request drifts until someone remembers to ask; showing keeps as a count keeps the list short however long the memory is | Only when asked (faster, but easy to forget); when the memory index passes a size (a threshold to tune, and drift below it goes unchecked) |
| Memory changes | Proposed and approved like any other write, including retirements; a move is one item, written before the removal | Memory is the developer's record too. A silent deletion loses something they may want, and a half-done move loses or duplicates a fact | Let the agent tidy its own memory unasked |
| Cross-repo order | A session rooted in the target repo, then an issue, then a draft in the report | A live session applies the change under that repo's own instructions and permissions. An issue waits for someone to pick it up. A draft always works | Issue first (slower to act on, and public on a public repo); edit the other repo directly (bypasses its rules and permissions) |
| Finding the target session | Exact name pattern from `ListAgents`; ask when several match | `ListAgents` gives names but no working directories, and names follow a fixed pattern from the directory's name | Ask the developer every time (slower when one match is obvious) |
| Next-session prompt | Always in the report; an existing handoff doc is updated only as an approved item | One paste starts the next session in any repo, with no new file to maintain | Write a handoff file in every repo (a file each repo didn't choose) |
| Untrusted input | Only the developer's own words count as corrections or decisions | Tool output, files and other sessions' messages can carry instruction-shaped text. Treating it as the developer's would let it rewrite the repo's rules | Treat all session text alike |
| Repeat runs | Cover what followed the last report; re-list items neither applied nor declined; only an explicit refusal declines | A second wrap-up shouldn't re-propose what was settled, or drop what was left open. Silence is too weak a signal to lose an item on, and the approval gate's "a list of numbers" inherits the same rule | Always cover the whole session (re-proposes settled items); choosing some items declines the rest (loses items the developer only put off) |
| Earlier report after compaction | Find it in the transcript when one is stated; otherwise cover the whole session and warn | The transcript still holds the report and its declines, so the run can honor them. Without it, the check against what's recorded catches applied items but not declined ones, so the report says so | Always cover the whole session (declined items come back even when the record is available) |
| Compaction summary | Leads only, as questions in the report | It is the agent's paraphrase, so treating it as the developer's words would break the rule that only their own words count | Ignore it (loses what it could point to); treat it as conversation |
| Transcript tool results | Search the developer's and agent's turns first; open a tool result only for a specific candidate | Overturned claims and facts found are often proved by tool output, but reading it all brings back secrets that compaction removed | Read everything and filter at output; never read tool results (loses that proof) |
| Handoff document | Named by the instruction files, or titled as such and seen in the session; updated only for what the session changed, with project state and no names | No routing role holds it, so the test has to be strict enough not to catch READMEs and backlogs. A session has no evidence for the rest of a stale document, and task state tends to name people, in repos that may be public | Match by filename; refresh the whole document; follow what the document already contains |
| Adapted text | `NOTICE` in the skill's directory, carrying each adapted source's notice | MIT and BSD-2-Clause require their notice to travel with copies of adapted text. APM installs only the skill's directory, so the notice lives there | Ideas only, with no adapted text (loses well-worded rules); the notice only at the repo root (copies would lose it) |
| Name | `session-wrap-up` | A consumer can't give its own skill the name of a template skill, and many published skills are called `wrap-up`, `retro` or `handoff`; naming the session keeps it apart from them and from task close-outs | `wrap-up` (the base skill's name, likely to collide); `wrap-up-session` (another public skill's name) |
| `@spec` placement | In tests and eval cases; `SKILL.md` and its references carry none | As for prior-art-search: annotations in skill text would load into every run | HTML-comment annotations in `SKILL.md` |

## Open Questions & Future Decisions

- **Slices.** Planned order, each usable alone:
  1. the package, house rules, lessons, the report and the next-session prompt (steps 0-4, 8 and 10), report-only in every run;
  2. refinements: repeat runs, transcripts after compaction, checks instead of prose, merging into always-loaded files, and the handoff document;
  3. in three parts, each committed on its own:
     - 3a: loose ends (step 6), still report-only in every run;
     - 3b: the approval gate and applying items (steps 8 to 10), where the skill starts to write;
     - 3c: capture in an issue, and fast checks;
  4. memory triage (step 5);
  5. cross-repo routing (step 7).

  Until 3c, confirmed items are applied straight away, with no offer of an issue, and no fast checks run. The safety rules hold from slice 1, as do the memory-location rule and the ban on proposing a new handoff document. Until slice 4, an item for agent memory stays proposed and isn't selectable, because no spec covers adding an entry and its index line. Until slice 5, an item another repo owns becomes a draft in the report (the third way under Cross-repo routing), and isn't selectable. An item for the user-level instructions is selectable when its path is known; if that path resolves into another repo, it is treated as an item for that repo.

### Deferred

- Issue capture and issue routing on forges other than GitHub, such as GitLab. Until then, a host repo `gh` can't reach takes the no-issue route.
- A `SessionStart` hook that surfaces the last wrap-up's next-session prompt.
- Triage across every project's memory at once.

## References

- [Prior-art note for this skill](../../prior-art/2026-10-29-session-wrap-up-skills.md).
- [Agent Skills specification](https://agentskills.io/specification); Claude Code [memory](https://code.claude.com/docs/en/memory) and [skills](https://code.claude.com/docs/en/skills).
