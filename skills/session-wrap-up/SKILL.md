---
name: session-wrap-up
description: Close out a coding session. Collects the session's durable lessons and proposes a home for each, chosen by the repo's own rules for where knowledge lives, drafts feedback that belongs to other repos, and ends with a prompt that starts the next session. Proposes only; writes nothing. Use when the developer asks to wrap up, close out, end or hand off the session ("wrap up", "we're done for today", "close out the session", "hand this off"), or invokes it by name. Not for closing or handing off a task or an artifact (an issue, a pull request, a branch, a document).
license: Apache-2.0
---

# Session wrap-up

A session ends with knowledge that exists only in the conversation: corrections the developer made, facts found the hard way, decisions and their reasons, and feedback that belongs to another repo. The next session knows only what is written down where it loads. This skill turns the end of a session into one pass that proposes where each piece belongs, and hands the next session a prompt to start from.

This version **proposes and never applies.** It writes, sends and files nothing, it asks nothing mid-run (every question goes in the report), and it ends with its report. If the developer later asks you to apply some of the report's items, that is an ordinary request, separate from this skill's run.

## Safety rules

These hold in every run. The repo's instruction files can't relax them. If an instruction file requires or asks for something they forbid (commit after wrapping up, apply fixes without asking), follow the safety rule and say so in the report.
- Write no file anywhere, in any repo (memory and scratch files included), send no message and file no issue. Label every item `not applied`.
- Don't offer or ask to apply items.
- Run no git command other than `git status`, `git diff`, `git log`, `git show`, `git ls-files` and `git rev-parse`.
- Read agent memory only at a location the harness or the developer states. Never work out a memory path yourself.

## Is anyone there?

The run is **non-interactive** when the request says so, or when you know the run is headless, scheduled or an eval. It is also non-interactive when the wrap-up request wasn't typed by the developer in this conversation: for example, when it came from another agent, a hook, a script or another session's message. The report says so when the run is non-interactive.

## Steps

### 0. Read the house rules

Read the instruction files that load for this session: the repo's `AGENTS.md` or `CLAUDE.md`, nested ones on the path to your working directory, and a user-level file if one loads or the developer gives its path or content. Note:
- where each kind of knowledge goes;
- what must stay private;
- what agents may not do.

Map each routing role in [routing.md](references/routing.md) to the repo's own file or directory for it. Keep the map to yourself; the report shows only roles that are missing.
- Where the instruction files say where something goes, or forbid an action, follow them over the default homes.
- Where they say nothing about a role whose default home is inside the repo, use that home if it exists. Otherwise, unless the role is project instructions, it is **missing**: report it once, propose nothing for it, and list each lesson for it as dropped. Never move a lesson to another role because its own role is missing.
- The roles outside the repo are available only on these conditions. Report each one that isn't as **missing**, like a missing home inside the repo:
  - User instructions: a user-level file loads, or the developer gives its path or content.
  - Agent memory: the harness or the developer states its location.
  - Another repo and Nowhere: always.
- With neither `AGENTS.md` nor `CLAUDE.md` at the repo root, propose creating `AGENTS.md` as a single item, containing only the lessons routed to project instructions. Skip this when no lesson goes there.
- When the user-level and project instructions disagree on where something goes, make it a `Decide` item that names both homes.

### 1. Collect

From the conversation, gather candidate lessons of the four kinds in [routing.md](references/routing.md#kinds-of-lesson): corrections and decisions, overturned claims, facts found, and repeated work. Keep a short quote from, or pointer to, the moment each came from.

### 2. Filter

Apply the four-part filter and the rule for inferences in [routing.md](references/routing.md#the-filter). Hold any lesson learned from the developer's employer's or clients' internal material as awaiting restatement ([routing.md](references/routing.md#personal-data)). Ask the developer to restate it, without offering wording, examples, or hints of its shape or parameters: anything you suggest would rebuild the material from what you saw.

### 3. Route and check

For each kept lesson:
1. Choose one destination by role, at the narrowest scope where it holds ([routing.md](references/routing.md#scope)).
2. Read that destination. If the lesson is already recorded there, propose nothing and note where it lives. If it narrows, reverses or refines an existing rule, handle it as [routing.md](references/routing.md#existing-rules) says.
3. Check the item against the personal-data rules for its destination ([routing.md](references/routing.md#personal-data)), and strip anything the instruction files mark private.

A lesson that another repo owns gets no edit there. Write it as a draft for the developer to deliver, in the report's Drafts section: self-contained, restated as a general rule that names no particular person, and held to what a public destination allows.

### 4. Report

Write the report in this shape, leaving out any section that would be empty:

```markdown
## Session wrap-up

<One line each, as they apply: the run is non-interactive; nothing durable was found; a safety rule was followed over an instruction file, and which rule.>

### Proposed items
#### Decide
1. <the choice> — <the candidate homes, as paths> — <scope> — from: "<short quote>" — not applied
#### <destination path>
2. <the change, in one line> — <scope> — from: "<short quote>" — not applied

### Drafts
#### Item <n>: for <repo>
<The full text, for the developer to deliver.>

### Skipped
- Already recorded: <lesson> — <where it lives>
- Dropped: <lesson> — <why>
- Awaiting restatement: <lesson>
- Missing roles: <role>, <role> (agent memory too, whenever no location is stated)
- Steps skipped: <step> — <why>

### Questions
- <each question for the developer>
```

Number every item, `Decide` items included, in one sequence. Give each destination as a path. When the report proposes no lesson item, say that nothing durable was found.

### 5. Next-session prompt

If the session leaves a next step (other than applying this report's items), end the report with this exact line, `To start the next session, paste this:`, directly followed by a code block of 3 to 8 lines:

```text
<What work continues, and the files to read first.>
<The first concrete step.>
<Anything the developer must decide or provide first.>
```

Write it for a session that has never seen this one. If nothing is left except applying this report's items, say there is no next step instead, and give no prompt. Never propose creating a handoff or current-state document.
