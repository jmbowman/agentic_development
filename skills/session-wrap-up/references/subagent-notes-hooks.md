# Subagent notes hooks

A subagent's friction, workarounds and surprises usually stay in its own context; only its report comes back. These Claude Code hooks collect them without changing the report:

1. When the main conversation launches a subagent with the `Agent` tool, a hook records it and adds one line of context: `[subagent-notes] agent <ID>, notes in <directory>`.
2. At the end of each turn of an interactive session, a hook asks the main agent to send each finished subagent the fixed question below with `SendMessage`. Each subagent is asked once.
3. Hooks save each subagent's reply to `<ID>.md` in the session's notes directory, beside the session's transcript.

The session wrap-up reads the notes as candidate lessons. When subagents ran and no hook added that line, it reports that the hooks aren't active.

**What they cost.** For each subagent: one short housekeeping turn of the main agent at the end of the turn it finished in, and one short resumed turn of the subagent. Outside auto mode, each `SendMessage` also brings a permission prompt; deny it and that subagent isn't asked again. They ask only in interactive sessions, so a `claude -p` run's result is never replaced. Setting `SUBAGENT_NOTES=off` in the environment turns them off.

**What they need.** `python3` 3.11 or later. They change nothing outside the notes directory, and a missing or failing script never blocks Claude Code.

## The fixed question

```text
Reply with only your process notes for the task you just finished: at most 5 bullet points, each a non-obvious piece of friction, a workaround or a surprise (a tool that failed or was blocked, an instruction or claim that misled you, query wording that returned noise). Don't restate your report. If there is nothing worth noting, reply with exactly `none`.
```

## Installing them

**As a plugin.** The hooks come with the `agentic-development` plugin. In Claude Code, run:

```
/plugin marketplace add jmbowman/agentic_development
/plugin install agentic-development@agentic-development
```

**By hand.** Where the skill is installed without the plugin (for example by APM, or copied into a repo), add these entries to the repo's `.claude/settings.json`, merged with any hooks it already has. Replace `<skill path>` with the skill's directory relative to the repo root, such as `.claude/skills/session-wrap-up`. For a skill installed in your user directory, use its absolute path in place of `$CLAUDE_PROJECT_DIR/<skill path>`, in `~/.claude/settings.json`.

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "SendMessage", "hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]}
    ],
    "PostToolUse": [
      {"matcher": "Agent", "hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]},
      {"matcher": "SendMessage", "hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]},
      {"matcher": "SubagentHandback", "hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]}
    ],
    "Stop": [{"hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]}],
    "SubagentStart": [{"hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]}],
    "SubagentStop": [{"hooks": [{"type": "command", "command": "python3 -I \"$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes.py\" || true"}]}]
  }
}
```

The `|| true` keeps a missing script from blocking: a hook command that exits with status 2 blocks Claude Code, and `python3` exits 2 when its script isn't there. Registering the hooks both ways is safe: each step happens once, however many copies run.

**When they don't run.**
- Settings that disable hooks (`disableAllHooks`, or a managed policy that allows only managed hooks) keep them from running, whichever way they are installed.
- Claude Code cloud sessions don't install plugins declared in settings, so there only the by-hand entries work.
- A project's hooks run only after you accept the workspace trust dialog for its folder.
