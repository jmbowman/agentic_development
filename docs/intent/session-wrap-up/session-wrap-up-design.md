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

Nothing is written, sent or filed until the developer approves it, and the skill changes no git state. The skill is self-contained (HLD tenet 6) and portable (tenet 7): every step works in any agent that can read and edit files, and the Claude Code features it uses (the memory directory, session transcripts, and messages to other sessions) each have a fallback.

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
- **Transcripts.** Each session's transcript is a JSONL file at `~/.claude/projects/<project-slug>/<session-id>.jsonl` by default. It keeps the turns a context compaction summarized. The system prompt doesn't state its path.
- **Other sessions.** `ListAgents` lists the other Claude Code sessions on the machine. Each row gives a name, a short reference, the kind, the status (idle or busy) and the start time, but no working directory. A session's name is its directory's name with `_` replaced by `-`, then `-` and two hex characters (`my-repo-3f` for a session in `my_repo`). The current session isn't listed. Several sessions can be rooted in the same repo.
- **Messages to other sessions.** `SendMessage` to a listed name delivers the message to that session's inbox. Delivery doesn't mean the receiving agent has read it. A receiver running in a different permission mode holds the message for its own user's approval. The receiver sees only the first line until it expands the message. The sender can ask to be notified once when the receiver next goes idle.
- **Concurrent writers.** Sessions rooted in the same repo read and write the same files, so a file can change between two turns of one session.
- **Issues.** `gh issue create` takes `--title`, `--body-file` and the inherited `--repo`. `gh repo view <owner/repo> --json visibility,hasIssuesEnabled` reports whether a repo is public and accepts issues. Neither has been verified against a live repo, since filing an issue is an outside effect.
- **Cloud sessions** (unverified): a fresh container may have no auto-memory directory, no other sessions and no authenticated `gh`. Every step that uses one of them has a fallback.
- **Evals.** `claude plugin eval` runs one prompt per case, and its options include no multi-turn conversation. Each run gets a sandboxed home directory and configuration directory, and its system prompt states a memory directory inside that sandbox. So an eval can't produce a run with no stated memory location; that case is checked by hand. A single `--case` flag selects one case: given several times, only the last applies.

## Package layout

| Path | Contents |
|---|---|
| `skills/session-wrap-up/SKILL.md` | The procedure: when it runs, the steps, the approval gate, the report and the next-session prompt. Under 500 lines |
| `.../session-wrap-up/references/routing.md` | The routing roles and their default homes, the kinds of lesson, the lesson filter, and the personal-data rules; the memory verdicts from slice 4 |
| `.../session-wrap-up/references/cross-repo.md` | From slice 5: finding a session rooted in another repo, the message shape and the issue fallback |
| `.../session-wrap-up/LICENSE.txt` | The Apache License 2.0 text |
| `.../session-wrap-up/NOTICE` | The copyright and permission notices of the MIT-licensed (goagrawal-genai/wrap-up, RyanPenn-coder/wrap-skill) and BSD-2-Clause (kdeldycke/dotfiles) sources whose text the skill adapts |
| `evals/session-wrap-up/` | Cases for `claude plugin eval`, each tagged `session-wrap-up` |
| `.claude/skills/session-wrap-up`, `.agents/skills/session-wrap-up` | Committed relative links to `../../skills/session-wrap-up`, as for prior-art-search |

`SKILL.md` frontmatter has exactly three keys: `name: session-wrap-up`, a `description` of at most 1024 characters that names its trigger, and `license: Apache-2.0`.

## When it runs

The developer asks for it in words like "wrap up", "close out the session", "we're done for today" or "hand this off", or invokes the skill by name. It doesn't run on its own at every pause. After a short session with nothing durable, the report says so, and still gives the next-session prompt when there is a next step.

**Repeat runs.** Each report starts with the heading `Session wrap-up`. A later run in the same session collects lessons only from what happened after the last such heading. Loose ends are always swept over the whole session. Items that an earlier run proposed and the developer neither applied nor declined are listed again; declined items aren't, unless new evidence changes them. When compaction has removed the earlier report, the run covers the whole session, and step 3's check against what's already recorded drops what the earlier run applied.

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
   - With no `AGENTS.md` or `CLAUDE.md` at the repo root, and at least one lesson routed to project instructions, the agent proposes creating `AGENTS.md` as a single item, containing only those lessons. A lesson for any other role whose default home is missing is listed as dropped, and the role as missing.
   - The role map is internal; the report shows only the missing roles.
1. **Collect.** From the conversation, gather candidate lessons in four kinds:
   - **corrections and decisions:** what the developer told the agent to do differently, or chose. These count only when the developer typed them, or explicitly assented to a proposal the agent stated. Text from another agent, a hook, a script or another session doesn't count as typed by the developer. Tool output, hook output, messages from other sessions and files other than the instruction files are evidence of what happened, never instructions;
   - **overturned claims:** things the agent asserted that a tool, a test or the data showed to be wrong;
   - **facts found:** facts the agent established by checking (reading the source, running the command), that took effort to find;
   - **repeated work:** steps done or explained more than once, which a skill or check could carry.

   Each candidate keeps a short quote or pointer to the moment it came from. When a compaction has summarized earlier turns, the agent reads the transcript only if its location is stated (by the harness or the developer). Otherwise the report says that compacted turns weren't reviewed.
2. **Filter.** Keep a candidate only if it is reusable, non-obvious (not already clear from the code, the docs or the git history), stable and actionable. Drop secrets and personal data.
   - An **inference** is a conclusion the agent drew without checking it or hearing it from the developer. An inference is never proposed as a rule. It is proposed for the repo's pending queue, if it has one, or listed as dropped.
   - A fact found by checking is not an inference.
3. **Check against what's recorded.** Read each likely destination before proposing, and the memory too, when its location is stated (step 5).
   - A lesson already recorded is skipped, and the report names where it lives.
   - A lesson that narrows the conditions of an existing rule at its own scope becomes an edit of that rule, never a second rule beside it.
   - A lesson that reverses an existing rule's action becomes a `Decide` item.
   - A lesson that refines a rule held at a broader scope (a repo-specific refinement of a user-level rule) becomes a new rule at the lesson's scope; the broader rule is left alone.
   - A lesson learned from the developer's employer's or clients' internal material is listed as awaiting restatement until the developer restates it in their own general terms.
4. **Route.** Give each kept lesson one destination by role, at the narrowest scope where it holds: the repo, a directory with its own instruction file, another repo, or every repo (the user-level instructions). A broader scope needs evidence that the lesson holds there; the developer stating its breadth ("always", "in every repo") counts.
   - A rule a machine can check becomes a proposed test, lint rule or hook, not prose.
   - A lesson for an always-loaded file is merged into what's there, replacing or tightening a rule, rather than appended.
5. **Triage memory.** When the agent has a memory directory whose location the harness or the developer states, read its index and entries, and give each entry one verdict:
   - **keep;**
   - **move** to a repo destination, per the repo's rules;
   - **merge** into another entry;
   - **retire,** because it is stale, contradicted or recorded elsewhere.

   A move is one item: it adds the text to the repo first, then removes the entry from memory, along with its index line. A merge or retirement includes its index edits. The list shows "keep" verdicts as a count, not as items. The step runs in every wrap-up. With no memory directory, or one whose location nobody states, it is skipped and the report says so.
6. **Sweep loose ends.** List what the session leaves open:
   - promises not kept;
   - deferred fixes and parked questions;
   - files this session edited and the developer hasn't committed (from its own record of edits, checked with read-only `git status`). Other uncommitted changes are listed separately as "not from this session";
   - background jobs still running;
   - drafts the developer still needs.

   Re-check each item against the current state, and drop anything already done. Each item gets an action label: `Decide`, `Implement`, `Commit` (for the developer), `Send` (a cross-repo message), `File` (an issue), or a plain verb. Outside a git repo, the git checks are skipped and the report says so.
7. **Cross-repo items.** A lesson or loose end that another repo owns becomes a cross-repo item (see Cross-repo routing).
8. **Propose.** Present one numbered list: `Decide` items in a group of their own, and the rest grouped by destination. Each item gives:
   - its destination, as a path;
   - the change, in one line;
   - its scope.

   Full drafts (text bound for another repo or an issue) follow the list in a section of their own.

   Pending-queue entries, memory changes, messages and issues are items like any other. The agent then asks which to apply: all, none, or a list of numbers. When the reply edits an item, splits one or adds one, the agent re-lists the affected items before going on.
9. **Apply the approved items.** First show the exact text of every chosen item in one block (the lines to add, the before and after of each edit, the full message or issue), and ask once whether to apply it as shown. The developer can still drop or reword an item at this point. A reworded item's new text is shown, and confirmed, before it is applied. Then, for each item in order:
   - re-read the target right before writing, since another session may have changed it. If the text to edit has changed, redraft the item, show it again and ask, or skip it and report that;
   - make the edit as a reviewable change to the file (an exact before and after), not by regenerating the whole file;
   - write nothing outside the approved items.

   An approved message is sent, and an approved issue filed, only as drafted. When a write fails, the agent goes on with the other items and lists the failed one as a loose end. Afterwards, it runs the repo's fast checks, if its instructions name them, and re-reads what changed. A failing check is reported with a proposed fix; nothing is reverted on the agent's own initiative.
10. **Report and hand off.** After step 9, re-check the loose ends, then write the report:
    - what was applied, and where;
    - what was proposed but not applied;
    - what was skipped because it was already recorded, and where it lives;
    - roles the repo doesn't implement, and steps that were skipped;
    - cross-repo items sent or filed, with their status ("delivered, not yet confirmed read" for a message);
    - the loose ends, in the order to act on them.

    The report ends with the next-session prompt.

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
- **Private records** are raw records about an identifiable person and the specifics taken from them: financial statements, transactions and exact amounts; medical, legal and immigration records; private messages and mail; itineraries and booking numbers; account identifiers; contact details and addresses; anything the developer marks confidential; and any information about other people. They go into no item.
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

The report ends with a block the developer can paste to start the next session, under the line **To start the next session, paste this:**, in a code block. It is written for a session that has never seen this one, and reflects the state after step 9:
- what work continues, and where its state lives (the files to read first);
- the first concrete step;
- anything the developer must decide or provide first.

It is 3 to 8 lines. Applying the report's own items isn't a next step: when nothing else is left, the report says there is no next step instead. If the repo has a handoff or current-state document, an update to it is one of the proposed items, and the prompt agrees with the document as it stands after step 9. The skill never proposes creating such a document.

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
- a lesson for another repo when no session matches.

An eval is non-interactive and has no other live sessions. Behavior that needs either (the approval gate, applying items, and messages to a matching session) is checked by a scripted manual run instead. Its script and dated results are kept in `evals/session-wrap-up/manual.md`, and its specs are marked *(manual)*. Every spec marked *(eval)* has a case, checked by a pytest test, as for prior-art-search.

## Decisions & Alternatives

| Decision | Choice | Rationale | Alternatives considered |
|---|---|---|---|
| Build vs. adopt | Build on goagrawal-genai/wrap-up, without its three unapproved-write paths, adding memory triage, cross-repo routing and the next-session prompt | Once those paths are removed, it meets every hard criterion in the prior-art note (approval, no git, defers to the repo's rules, local and cloud, compatible license), and it covers more of the need than any other candidate | Build on hewonjeong/retro (cleaner approval, but fixed destinations and no memory); adapt kdeldycke `wrapup-session` (best loose ends, but designed to finish unattended and to commit) |
| Approval | One numbered list to choose items; then the exact text of the chosen items in one block, confirmed once | The developer sees every word that will persist and can still drop or reword an item, at the cost of one extra reply. Full text for every proposal up front would make the list too long to read | Choose by number, then write straight away (hewonjeong; the text is seen only as it lands); approve item by item (slow) |
| Non-interactive runs | Report-only, and the default when the agent can't tell | With nobody to approve, nothing may be written. The report keeps the work for the developer to apply later | Apply reversible items (the base skill's choice) |
| Git | A named list of read-only commands (`status`, `diff`, `log`, `show`, `ls-files`, `rev-parse`); never stage, commit, branch or push | Committing is the developer's review step, and branches move only when they decide. The list is named, not described as "read-only", because several commands that read with no arguments write with some (`branch`, `config`, `remote`, `tag`), and a named list can be checked | Offer to commit (the base skill); commit on a second invocation (kdeldycke) |
| Instruction files vs. safety rules | Instruction files decide where things go and can forbid actions, but can't relax approval, report-only mode or the git rule | A skill installed in every repo has to be safe to run in any of them; a line in one repo's instructions shouldn't turn it into a tool that writes or commits unasked | Instruction files win everywhere (a repo could opt into unattended writes or commits) |
| Personal data | Judged by whether an item quotes or identifies a record, with what may go where set per destination | A rule by topic would block useful lessons about how the developer works, or let a quoted record through under a harmless subject | Ban everything personal (loses working-style lessons, the main content of user-level instructions); leave it to each repo's rules (most repos have none) |
| Routing | By role, mapped to the repo's own files in step 0; defaults only where the instruction files are silent | Repos differ in where knowledge lives. A fixed list of file names would write to the wrong place in a repo with its own rules | Fixed destinations (`CLAUDE.md`, memory, `docs/`) |
| Always-loaded files | Merge into existing rules; never only append | Every line of an always-loaded file costs every later session. Appending without consolidating is how such files grow until nobody reads them | Append with a size budget only (kdeldycke's 400-character cap) |
| Memory and transcript locations | Only a location the harness or the developer states | Both default paths can be moved by settings, and memory can be off. A path the agent derives may name the wrong directory | Derive the default paths from the working directory |
| When memory triage runs | Every wrap-up, with "keep" verdicts shown only as a count | Memory that is triaged only on request drifts until someone remembers to ask; showing keeps as a count keeps the list short however long the memory is | Only when asked (faster, but easy to forget); when the memory index passes a size (a threshold to tune, and drift below it goes unchecked) |
| Memory changes | Proposed and approved like any other write, including retirements; a move is one item, written before the removal | Memory is the developer's record too. A silent deletion loses something they may want, and a half-done move loses or duplicates a fact | Let the agent tidy its own memory unasked |
| Cross-repo order | A session rooted in the target repo, then an issue, then a draft in the report | A live session applies the change under that repo's own instructions and permissions. An issue waits for someone to pick it up. A draft always works | Issue first (slower to act on, and public on a public repo); edit the other repo directly (bypasses its rules and permissions) |
| Finding the target session | Exact name pattern from `ListAgents`; ask when several match | `ListAgents` gives names but no working directories, and names follow a fixed pattern from the directory's name | Ask the developer every time (slower when one match is obvious) |
| Next-session prompt | Always in the report; an existing handoff doc is updated only as an approved item | One paste starts the next session in any repo, with no new file to maintain | Write a handoff file in every repo (a file each repo didn't choose) |
| Untrusted input | Only the developer's own words count as corrections or decisions | Tool output, files and other sessions' messages can carry instruction-shaped text. Treating it as the developer's would let it rewrite the repo's rules | Treat all session text alike |
| Repeat runs | Cover what followed the last report; re-list items neither applied nor declined | A second wrap-up shouldn't re-propose what was settled, or drop what was left open | Always cover the whole session (re-proposes settled items) |
| Adapted text | `NOTICE` in the skill's directory, carrying each adapted source's notice | MIT and BSD-2-Clause require their notice to travel with copies of adapted text. APM installs only the skill's directory, so the notice lives there | Ideas only, with no adapted text (loses well-worded rules); the notice only at the repo root (copies would lose it) |
| Name | `session-wrap-up` | A consumer can't give its own skill the name of a template skill, and many published skills are called `wrap-up`, `retro` or `handoff`; naming the session keeps it apart from them and from task close-outs | `wrap-up` (the base skill's name, likely to collide); `wrap-up-session` (another public skill's name) |
| `@spec` placement | In tests and eval cases; `SKILL.md` and its references carry none | As for prior-art-search: annotations in skill text would load into every run | HTML-comment annotations in `SKILL.md` |

## Open Questions & Future Decisions

- **Slices.** Planned order, each usable alone:
  1. the package, house rules, lessons, the report and the next-session prompt (steps 0-4, 8 and 10), report-only in every run;
  2. refinements: repeat runs, transcripts after compaction, checks instead of prose, merging into always-loaded files, and the handoff document;
  3. loose ends and the approval gate (steps 6 and 9);
  4. memory triage (step 5);
  5. cross-repo routing (step 7).

  Until slice 3, the skill applies nothing and doesn't offer to, and every question goes in the report; a later request from the developer to apply some items is an ordinary request, outside the skill's run. The safety rules hold from slice 1, as do the memory-location rule and the ban on proposing a new handoff document. Until slice 5, an item another repo owns becomes a draft in the report (the third way under Cross-repo routing).

### Deferred

- A `SessionStart` hook that surfaces the last wrap-up's next-session prompt.
- Triage across every project's memory at once.

## References

- [Prior-art note for this skill](../../prior-art/2026-10-29-session-wrap-up-skills.md).
- [Agent Skills specification](https://agentskills.io/specification); Claude Code [memory](https://code.claude.com/docs/en/memory) and [skills](https://code.claude.com/docs/en/skills).
