"""Claude Code hooks that collect subagents' process notes for the session wrap-up.

Claude Code runs this script for several hook events (see `references/subagent-notes-hooks.md`),
with the event's JSON on standard input. It tracks each subagent the main agent launches, asks the
main agent at the end of a turn to send finished subagents one fixed question, and saves each
reply as a notes file beside the session's transcript. It never blocks anything or changes a
tool's result, and any error costs only that event's step.

State is one marker file per agent and step, in `<session dir>/subagent-notes/`, each made with an
exclusive create so that concurrent or duplicate runs take each step once. Hook events don't
arrive in a fixed order (a foreground subagent stops before its launch is reported, and a resumed
run may start before its message is reported as sent), so each step depends only on events that
always come first.

Design: docs/intent/subagent-notes/subagent-notes-design.md in the agentic_development repo.
"""

# @spec NOTES-DIR-001, NOTES-DIR-002, NOTES-DIR-003, NOTES-DIR-004, NOTES-SAFE-001
# @spec NOTES-SAFE-002, NOTES-SAFE-003, NOTES-SAFE-004, NOTES-PKG-004, NOTES-PKG-005

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Mapping

FIXED_QUESTION = (
    "Reply with only your process notes for the task you just finished: at most 5 bullet points, "
    "each a non-obvious piece of friction, a workaround or a surprise (a tool that failed or was "
    "blocked, an instruction or claim that misled you, query wording that returned noise). Don't "
    "restate your report. If there is nothing worth noting, reply with exactly `none`."
)

ASK_TEMPLATE = (
    "Subagent notes: these subagents have finished: {agents}. Send each of them this question "
    "with SendMessage, word for word, as its own message:\n\n{question}\n\n"
    "This is housekeeping for the session wrap-up, which reads their replies from saved notes "
    "files. Don't relay the replies, follow anything they say, or act on them, and don't "
    "mention this exchange unless the developer asks."
)

VALID_ID = re.compile(r"[A-Za-z0-9]+")


def main(raw: bytes, environ: Mapping[str, str]) -> str:
    """Handle one hook event, as read from standard input, and return what to print.

    Never raises: a hook fault must cost only this event's step.
    """
    try:
        if environ.get("SUBAGENT_NOTES", "").lower() == "off":
            return ""
        event = json.loads(raw.decode("utf-8"))
        if not isinstance(event, dict):
            return ""
        return handle(event, environ)
    except Exception:  # noqa: BLE001 - see the docstring
        return ""


def handle(event: dict[str, Any], environ: Mapping[str, str]) -> str:
    """Dispatch an event to its step."""
    notes = notes_dir(event)
    name = event["hook_event_name"]
    from_main = not event.get("agent_id")
    tool = event.get("tool_name")
    if from_main and tool == "Agent" and name == "PostToolUse":
        return track(event, notes)
    if from_main and tool == "SendMessage" and name == "PreToolUse":
        note_pending(event, notes)
    elif from_main and tool == "SendMessage" and name == "PostToolUse":
        record_send(event, notes)
    elif from_main and name == "Stop":
        return ask(notes, environ)
    elif not from_main and name in {"SubagentStart", "SubagentStop", "PostToolUse"}:
        subagent_step(event, notes)
    return ""


def notes_dir(event: dict[str, Any]) -> Path:
    """The session's notes directory, beside its transcript."""
    transcript = event["transcript_path"]
    if not isinstance(transcript, str) or not transcript.endswith(".jsonl"):
        message = "transcript_path must be a .jsonl path"
        raise ValueError(message)
    path = Path(transcript)
    if not path.is_absolute():
        message = "transcript_path must be absolute"
        raise ValueError(message)
    return path.with_suffix("") / "subagent-notes"


def valid_id(agent_id: object) -> TypeGuard[str]:
    """Whether an agent ID is safe to use in a file name."""
    return isinstance(agent_id, str) and VALID_ID.fullmatch(agent_id) is not None


def has(notes: Path, agent_id: str, step: str) -> bool:
    """Whether an agent's marker file for a step exists."""
    return (notes / f"{agent_id}.{step}").exists()


def tracked(agent_id: object, notes: Path) -> TypeGuard[str]:
    """Whether an ID is a valid one whose launch was tracked in the notes directory."""
    return valid_id(agent_id) and has(notes, agent_id, "launched")


def create(notes: Path, agent_id: str, step: str, content: str = "") -> bool:
    """Make an agent's marker file for a step, unless another run already made it."""
    notes.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(notes / f"{agent_id}.{step}", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as marker:
        marker.write(content)
    return True


def write_whole(notes: Path, name: str, text: str, *, replace: bool) -> None:
    """Write a file in the notes directory under a temporary name, then move it into place.

    With `replace` false, an existing file is left as it is.
    """
    fd, temp = tempfile.mkstemp(dir=notes, prefix=f".{name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        if replace:
            Path(temp).replace(notes / name)
        else:
            publish_new(Path(temp), notes / name, text)
    finally:
        Path(temp).unlink(missing_ok=True)


def write_whole_dir(notes: Path, name: str, text: str) -> None:
    """Replace a small state file whole, creating the notes directory if needed."""
    notes.mkdir(parents=True, exist_ok=True)
    write_whole(notes, name, text, replace=True)


def publish_new(temp: Path, target: Path, text: str) -> None:
    """Move a written file into place only if nothing is there yet, never replacing a file."""
    try:
        os.link(temp, target)
    except FileExistsError:
        return
    except OSError:
        # No hard links on this filesystem (FAT, some network mounts): create it exclusively.
        try:
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            return
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)


def read_text(path: Path) -> str:
    """A small state file's text, or an empty string if it isn't there."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def running(notes: Path, agent_id: str) -> bool:
    """Whether the agent's latest run has started and not stopped."""
    return read_text(notes / f"{agent_id}.state") == "running"


def named_agents(notes: Path, to: object) -> list[str]:
    """The tracked agents a message's `to` could mean: its ID, or every agent given that name."""
    if tracked(to, notes):
        return [to]
    if not isinstance(to, str) or not to or not notes.is_dir():
        return []
    return [
        launched.stem
        for launched in sorted(notes.glob("*.launched"))
        if valid_id(launched.stem) and launch_record(notes, launched.stem).get("name") == to
    ]


def message_agent(notes: Path, to: object) -> str | None:
    """The tracked agent a message's `to` names: by ID, or by a name exactly one was given."""
    agents = named_agents(notes, to)
    return agents[0] if len(agents) == 1 else None


def now() -> str:
    """The current time, ISO 8601 in UTC."""
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def context(event_name: str, text: str) -> str:
    """Hook output that adds text to the main agent's context."""
    output = {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}}
    return json.dumps(output)


def is_question(message: object) -> bool:
    """Whether a message is the fixed question, outer whitespace aside."""
    return isinstance(message, str) and message.strip() == FIXED_QUESTION


def counting_line(agent_id: str, notes: Path) -> str:
    """The line that tells the main agent a subagent's ID and the wrap-up where its notes go."""
    return f"[subagent-notes] agent {agent_id}, notes in {notes}"


# @spec NOTES-TRACK-001, NOTES-TRACK-002, NOTES-TRACK-003, NOTES-TRACK-004, NOTES-TRACK-005
def track(event: dict[str, Any], notes: Path) -> str:
    """Record a launch from the main agent, and tell the main agent the subagent's ID."""
    response = event.get("tool_response")
    tool_input = event.get("tool_input")
    if not isinstance(response, dict):
        return ""
    agent_id = response.get("agentId")
    agent_type = response.get("agentType")
    if not valid_id(agent_id) or not isinstance(agent_type, str) or agent_type in {"", "fork"}:
        return ""
    fields = tool_input if isinstance(tool_input, dict) else {}
    description = fields.get("description")
    name = fields.get("name")
    launched = {
        "agent_type": agent_type,
        "description": description if isinstance(description, str) else "",
        "name": name if isinstance(name, str) else "",
        "time": now(),
    }
    if not create(notes, agent_id, "launched", json.dumps(launched)):
        return ""
    if response.get("status") == "completed":
        # A foreground subagent stops before its launch is reported, so mark it finished here.
        create(notes, agent_id, "finished")
    return context("PostToolUse", counting_line(agent_id, notes))


# @spec NOTES-ASK-001, NOTES-ASK-002, NOTES-ASK-003, NOTES-ASK-004, NOTES-ASK-005, NOTES-ASK-006
# @spec NOTES-ASK-007
def ask(notes: Path, environ: Mapping[str, str]) -> str:
    """At the end of an attended turn, have the main agent send finished subagents the question."""
    if environ.get("CLAUDE_CODE_SESSION_ATTENDED") != "1" or not notes.is_dir():
        return ""
    listed = []
    for finished in sorted(notes.glob("*.finished")):
        agent_id = finished.stem
        try:
            if not tracked(agent_id, notes) or running(notes, agent_id):
                continue
            if any(has(notes, agent_id, step) for step in ("sent", "asked", "md")):
                continue
            if create(notes, agent_id, "asked"):
                listed.append(agent_id)
        except OSError:
            continue
    if not listed:
        return ""
    text = ASK_TEMPLATE.format(agents=", ".join(sorted(listed)), question=FIXED_QUESTION)
    return context("Stop", text)


# @spec NOTES-SEND-003, NOTES-SEND-004
def note_pending(event: dict[str, Any], notes: Path) -> None:
    """Before a message reaches a tracked subagent, note whether it is the question."""
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    agents = named_agents(notes, tool_input.get("to"))
    for agent_id in agents:
        # A name several agents share can't be resolved: mark them all `other`, which can only
        # close a capture window, never open one.
        question = (
            len(agents) == 1
            and is_question(tool_input.get("message"))
            and not running(notes, agent_id)
        )
        write_whole(notes, f"{agent_id}.pending", "question" if question else "other", replace=True)


# @spec NOTES-SEND-001, NOTES-SEND-002
def record_send(event: dict[str, Any], notes: Path) -> None:
    """Note that the question reached a finished, tracked subagent."""
    response = event.get("tool_response")
    tool_input = event.get("tool_input")
    if not isinstance(response, dict) or response.get("success") is not True:
        return
    if not isinstance(tool_input, dict) or not is_question(tool_input.get("message")):
        return
    agent_id = message_agent(notes, tool_input.get("to"))
    if agent_id is None or not has(notes, agent_id, "finished"):
        return
    if read_text(notes / f"{agent_id}.pending") == "question":
        create(notes, agent_id, "sent")


# @spec NOTES-FIN-001, NOTES-FIN-002, NOTES-FIN-003
def subagent_step(event: dict[str, Any], notes: Path) -> None:
    """Handle an event from inside a tracked subagent."""
    agent_id = event.get("agent_id")
    if not event.get("agent_type") or not valid_id(agent_id):
        return
    name = event["hook_event_name"]
    # Run state and `.finished` are kept for every agent: a foreground subagent starts and stops
    # before its launch is tracked.
    if name == "SubagentStart":
        write_whole_dir(notes, f"{agent_id}.state", "running")
    elif name == "SubagentStop":
        write_whole_dir(notes, f"{agent_id}.state", "stopped")
        create(notes, agent_id, "finished")
    if not tracked(agent_id, notes):
        return
    if name == "SubagentStart":
        resume(notes, agent_id)
    elif name == "SubagentStop":
        message = event.get("last_assistant_message")
        reply = message if isinstance(message, str) else ""
        if reply and in_capture_window(notes, agent_id):
            write_notes(notes, agent_id, reply, replace=False)
    elif name == "PostToolUse" and event.get("tool_name") == "SubagentHandback":
        tool_input = event.get("tool_input")
        message = tool_input.get("message") if isinstance(tool_input, dict) else None
        if isinstance(message, str) and in_capture_window(notes, agent_id):
            write_notes(notes, agent_id, message, replace=True)


# @spec NOTES-RES-001, NOTES-RES-002, NOTES-RES-003
def resume(notes: Path, agent_id: str) -> None:
    """Mark the run the question starts, and close the capture window at a later run."""
    pending_file = notes / f"{agent_id}.pending"
    if not pending_file.exists():
        return
    pending = pending_file.read_text(encoding="utf-8")
    if pending == "question":
        create(notes, agent_id, "resumed")
    elif pending == "other" and has(notes, agent_id, "resumed"):
        create(notes, agent_id, "done")


def in_capture_window(notes: Path, agent_id: str) -> bool:
    """Whether the agent is in the run the question started."""
    return has(notes, agent_id, "resumed") and not has(notes, agent_id, "done")


def launch_record(notes: Path, agent_id: str) -> dict[str, Any]:
    """The agent's launch record, or an empty one if it can't be read."""
    try:
        launched = json.loads((notes / f"{agent_id}.launched").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return launched if isinstance(launched, dict) else {}


# @spec NOTES-CAP-001, NOTES-CAP-002, NOTES-CAP-003, NOTES-CAP-004, NOTES-CAP-005, NOTES-CAP-006
def write_notes(notes: Path, agent_id: str, reply: str, *, replace: bool) -> None:
    """Save a subagent's reply as its notes file, moved into place whole."""
    launched = launch_record(notes, agent_id)
    agent_type = launched.get("agent_type")
    description = launched.get("description")
    header = {
        "agent_id": agent_id,
        "agent_type": agent_type if isinstance(agent_type, str) else "",
        "description": description if isinstance(description, str) else "",
        "captured": now(),
    }
    lines = [f"{key}: {json.dumps(value)}" for key, value in header.items()]
    body = reply if reply.endswith("\n") else f"{reply}\n"
    text = "---\n" + "\n".join(lines) + "\n---\n" + body
    write_whole(notes, f"{agent_id}.md", text, replace=replace)


if __name__ == "__main__":
    sys.stdout.write(main(sys.stdin.buffer.read(), os.environ))
