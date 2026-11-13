"""Tests of the subagent notes hooks: the script, its registration and its reference.

These run the script as Claude Code does, on hook inputs shaped like those a probe of Claude Code
2.1.322 recorded, and replay whole flows in the event orders the probe logged. They assume a POSIX
system.
"""

from __future__ import annotations

import ast
import functools
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from tests.support import REPO_ROOT, SKILLS

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

SKILL = SKILLS / "session-wrap-up"
SCRIPT = SKILL / "hooks" / "subagent_notes.py"
REFERENCE = SKILL / "references" / "subagent-notes-hooks.md"
PLUGIN_HOOKS = REPO_ROOT / "hooks" / "hooks.json"
REPO_SETTINGS = REPO_ROOT / ".claude" / "settings.json"
SPECS = REPO_ROOT / "docs" / "intent" / "subagent-notes" / "subagent-notes-specs.md"
MANUAL = REPO_ROOT / "evals" / "session-wrap-up" / "manual.md"

SESSION = "0b6f6c2e-5d1a-4c55-9a8e-3f2d1c0b9a87"
AGENT = "a1b2c3d4e5f60718"
OTHER = "a9f8e7d6c5b40312"
THIRD = "a5a5a5a5a5a5a5a5"

# Events and matchers the script is registered for, wherever it is registered.
REGISTRATIONS = {
    ("PreToolUse", "SendMessage"),
    ("PostToolUse", "Agent"),
    ("PostToolUse", "SendMessage"),
    ("PostToolUse", "SubagentHandback"),
    ("Stop", None),
    ("SubagentStart", None),
    ("SubagentStop", None),
}
PLUGIN_COMMAND = (
    'python3 -I "${CLAUDE_PLUGIN_ROOT}/skills/session-wrap-up/hooks/subagent_notes.py" || true'
)
REPO_COMMAND = (
    'python3 -I "$CLAUDE_PROJECT_DIR/skills/session-wrap-up/hooks/subagent_notes.py" || true'
)
REFERENCE_COMMAND = (
    r'python3 -I "\$CLAUDE_PROJECT_DIR/<skill path>/hooks/subagent_notes\.py" \|\| true'
)

FORBIDDEN_OUTPUT_KEYS = {"decision", "permissionDecision", "updatedInput", "updatedToolOutput"}
ISO_UTC = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|\+00:00)"
ATTENDED = {"CLAUDE_CODE_SESSION_ATTENDED": "1"}
NOTES = "- The environment said this was a git repo, but `ls -A` showed no `.git`.\n"
REPORT = '{"entries": ["alpha.txt", "beta.txt"]}'
TIMEOUT = 10


@functools.cache
def question() -> str:
    """The fixed question, from the ```text block under the reference's heading for it."""
    text = REFERENCE.read_text()
    assert "## The fixed question" in text, "the reference has a section for the fixed question"
    section = text.split("## The fixed question", 1)[1]
    block = re.search(r"```text\n(.*?)\n```", section, re.DOTALL)
    assert block, "the reference gives the fixed question in a ```text block"
    return str(block.group(1))


def load_script() -> ModuleType:
    """Import the script as a module, for the tests that reach its documented internals."""
    spec = importlib.util.spec_from_file_location("subagent_notes", SCRIPT)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class Session:
    """A fake Claude Code project directory holding one session's transcript path."""

    project: Path

    @property
    def transcript(self) -> Path:
        """The main transcript's path, as hooks receive it."""
        return self.project / f"{SESSION}.jsonl"

    @property
    def notes(self) -> Path:
        """The notes directory the script derives from the transcript path."""
        return self.project / SESSION / "subagent-notes"

    def marker(self, agent: str, step: str) -> Path:
        """One agent's marker file for one step."""
        return self.notes / f"{agent}.{step}"

    def mark(self, agent: str, *steps: str) -> None:
        """Make marker files directly, to set up a state; `pending=x` writes a pending file."""
        self.notes.mkdir(parents=True, exist_ok=True)
        for step in steps:
            if step == "launched":
                launched = {"agent_type": "Explore", "description": "List files", "time": "t"}
                self.marker(agent, step).write_text(json.dumps(launched))
            elif step.startswith("pending="):
                self.marker(agent, "pending").write_text(step.removeprefix("pending="))
            else:
                self.marker(agent, step).touch()

    def files(self) -> set[str]:
        """The names of the files in the notes directory."""
        return {p.name for p in self.notes.iterdir()} if self.notes.exists() else set()

    def event(self, name: str, **fields: object) -> dict[str, Any]:
        """A hook input for this session, with the common fields filled in."""
        base = {
            "session_id": SESSION,
            "transcript_path": str(self.transcript),
            "cwd": str(self.project),
            "permission_mode": "default",
            "hook_event_name": name,
        }
        return base | fields


@pytest.fixture
def session(tmp_path: Path) -> Session:
    """An empty project directory for one session."""
    project = tmp_path / "projects" / "-home-dev-repo"
    project.mkdir(parents=True)
    return Session(project)


def environment(env: dict[str, str] | None) -> dict[str, str]:
    """A minimal environment, as a hook command gets, plus the given variables."""
    return {"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8", **(env or {})}


def run(
    event: dict[str, Any] | str | bytes,
    env: dict[str, str] | None = None,
    *,
    python: str = sys.executable,
    flags: tuple[str, ...] = ("-I",),
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Run the script with the event on standard input; it must exit 0 with no error output."""
    if isinstance(event, dict):
        stdin = json.dumps(event).encode()
    elif isinstance(event, str):
        stdin = event.encode()
    else:
        stdin = event
    result = subprocess.run(  # noqa: S603
        [python, *flags, str(SCRIPT)],
        input=stdin,
        capture_output=True,
        cwd=cwd,
        env=environment(env),
        check=False,
        timeout=TIMEOUT,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == b""
    return result


def run_concurrently(
    event: dict[str, Any], env: dict[str, str] | None, count: int, tmp_path: Path
) -> list[str]:
    """Start several runs on the same event, each with its input ready, before waiting on any."""
    payload = tmp_path / "event.json"
    payload.write_text(json.dumps(event))
    procs = []
    try:
        for _ in range(count):
            with payload.open() as stdin:
                procs.append(
                    subprocess.Popen(  # noqa: S603
                        [sys.executable, "-I", str(SCRIPT)],
                        stdin=stdin,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=environment(env),
                    )
                )
        return [proc.communicate(timeout=TIMEOUT)[0] for proc in procs]
    finally:
        for proc in procs:
            proc.kill()


def output(result: subprocess.CompletedProcess[bytes], event_name: str) -> str:
    """The additionalContext printed for an event, or an empty string when nothing was printed."""
    if not result.stdout.strip():
        return ""
    printed = json.loads(result.stdout)
    specific = printed["hookSpecificOutput"]
    assert specific["hookEventName"] == event_name
    value = specific["additionalContext"]
    assert isinstance(value, str)
    return value


def launch(
    session: Session,
    agent: object = AGENT,
    launched_type: str = "Explore",
    *,
    foreground: bool = False,
    name: str | None = None,
    **extra: object,
) -> dict[str, Any]:
    """A PostToolUse input for an `Agent` launch: by default from the main agent, in background."""
    status = "completed" if foreground else "async_launched"
    tool_input = {"description": "List files", "prompt": "List.", "subagent_type": launched_type}
    if name is not None:
        tool_input["name"] = name
    return session.event(
        "PostToolUse",
        tool_name="Agent",
        tool_input=tool_input,
        tool_response={"status": status, "agentId": agent, "agentType": launched_type},
        **extra,
    )


def subagent_event(
    session: Session, name: str, agent: str = AGENT, agent_type: str = "Explore", **extra: object
) -> dict[str, Any]:
    """An input for a hook running inside a subagent."""
    return session.event(name, agent_id=agent, agent_type=agent_type, **extra)


def pre_send(
    session: Session, to: str = AGENT, message: str | None = None, **extra: object
) -> dict[str, Any]:
    """A PreToolUse input for a `SendMessage` from the main agent, by default the question."""
    return session.event(
        "PreToolUse",
        tool_name="SendMessage",
        tool_input={"to": to, "message": question() if message is None else message},
        **extra,
    )


def send(
    session: Session,
    to: str = AGENT,
    message: str | None = None,
    response: dict[str, object] | None = None,
    **extra: object,
) -> dict[str, Any]:
    """A PostToolUse input for a `SendMessage` from the main agent, by default the question."""
    return session.event(
        "PostToolUse",
        tool_name="SendMessage",
        tool_input={"to": to, "message": question() if message is None else message},
        tool_response={"success": True, "resumedAgentId": to} if response is None else response,
        **extra,
    )


def start(session: Session, agent: str = AGENT) -> dict[str, Any]:
    """A SubagentStart input."""
    return subagent_event(session, "SubagentStart", agent)


def handback(session: Session, message: str, agent: str = AGENT) -> dict[str, Any]:
    """A PostToolUse input for a subagent's delivered `SubagentHandback`, in auto mode."""
    return subagent_event(
        session,
        "PostToolUse",
        agent,
        permission_mode="auto",
        tool_name="SubagentHandback",
        tool_input={"message": message},
        tool_response={"success": True, "message": "Report delivered to your caller."},
    )


def subagent_stop(session: Session, message: str, agent: str = AGENT) -> dict[str, Any]:
    """A SubagentStop input with the subagent's last message."""
    return subagent_event(session, "SubagentStop", agent, last_assistant_message=message)


def stop(session: Session, *, active: bool = False) -> dict[str, Any]:
    """A main-agent Stop input."""
    return session.event("Stop", stop_hook_active=active, last_assistant_message="Done.")


def notes_file(session: Session, agent: str = AGENT) -> tuple[dict[str, str], str]:
    """A notes file's front matter, parsed as YAML, and its body."""
    text = (session.notes / f"{agent}.md").read_text()
    assert text.startswith("---\n")
    header, body = text[4:].split("\n---\n", 1)
    meta = yaml.safe_load(header)
    assert isinstance(meta, dict)
    for line in header.splitlines():
        assert isinstance(json.loads(line.split(": ", 1)[1]), str), line
    return {str(k): str(v) for k, v in meta.items()}, body


def registrations(hooks: dict[str, Any], cmd: re.Pattern[str]) -> set[tuple[str, str | None]]:
    """The (event, matcher) pairs under which a hooks object runs a command matching a pattern."""
    found: set[tuple[str, str | None]] = set()
    for event, groups in hooks["hooks"].items():
        for group in groups:
            if any(cmd.fullmatch(hook.get("command", "")) for hook in group["hooks"]):
                matcher = group.get("matcher")
                found.add((str(event), None if matcher is None else str(matcher)))
    return found


# Package


# @spec NOTES-PKG-001
def test_plugin_registers_the_script_for_each_event() -> None:
    """The plugin's hooks run the script for every step of the flow."""
    hooks = json.loads(PLUGIN_HOOKS.read_text())
    assert registrations(hooks, re.compile(re.escape(PLUGIN_COMMAND))) == REGISTRATIONS


# @spec NOTES-PKG-002
def test_repo_settings_register_the_script_for_each_event() -> None:
    """This repo runs the same hooks from its own checkout."""
    hooks = json.loads(REPO_SETTINGS.read_text())
    assert registrations(hooks, re.compile(re.escape(REPO_COMMAND))) == REGISTRATIONS


# @spec NOTES-PKG-003
@pytest.mark.parametrize(
    "needle",
    [
        "/plugin marketplace add jmbowman/agentic_development",
        "/plugin install agentic-development@agentic-development",
        "SUBAGENT_NOTES=off",
        "permission prompt",
        "disableAllHooks",
        "cloud sessions",
    ],
    ids=["marketplace", "install", "opt-out", "cost", "disabled-hooks", "cloud"],
)
def test_reference_says_what_users_need(needle: str) -> None:
    """The wrap-up points a developer here when the hooks are missing."""
    assert needle in REFERENCE.read_text()


# @spec NOTES-PKG-003
def test_reference_settings_register_every_event() -> None:
    """The settings to register the hooks by hand cover the whole flow."""
    block = re.search(r"```json\n(.*?)\n```", REFERENCE.read_text(), re.DOTALL)
    assert block, "the reference gives the settings entries in a ```json block"
    hooks = json.loads(block.group(1))
    assert registrations(hooks, re.compile(REFERENCE_COMMAND)) == REGISTRATIONS


# @spec NOTES-PKG-003, NOTES-PKG-004
def test_script_question_matches_the_reference() -> None:
    """The main agent copies the question the hooks give it; the hooks recognize only that text."""
    fixed = load_script().FIXED_QUESTION
    assert fixed == question()
    assert question().strip() == question()
    assert "`none`" in question()


# @spec NOTES-PKG-005
def test_script_imports_only_the_standard_library() -> None:
    """The script runs with a bare python3, outside any virtual environment."""
    modules = set()
    for node in ast.walk(ast.parse(SCRIPT.read_text())):
        if isinstance(node, ast.Import):
            modules |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            modules.add(node.module.split(".")[0])
    assert modules - {"__future__"} <= set(sys.stdlib_module_names)


# @spec NOTES-PKG-005
def test_script_runs_under_the_system_python(session: Session) -> None:
    """Hooks run `python3`, not this venv's interpreter, so check that it works there too."""
    system_python = shutil.which("python3", path="/usr/bin:/bin")
    assert system_python is not None, "a system python3 is installed"
    result = run(launch(session), python=system_python, flags=("-I", "-S"))
    assert output(result, "PostToolUse").startswith("[subagent-notes]")


# @spec NOTES-PKG-006
@pytest.mark.parametrize(
    ("command", "variable"),
    [(PLUGIN_COMMAND, "CLAUDE_PLUGIN_ROOT"), (REPO_COMMAND, "CLAUDE_PROJECT_DIR")],
    ids=["plugin", "repo"],
)
def test_a_missing_script_never_blocks(tmp_path: Path, command: str, variable: str) -> None:
    """Claude Code treats exit status 2 as a block; python3 exits 2 for a missing script."""
    result = subprocess.run(  # noqa: S603
        ["/bin/sh", "-c", command],
        input=b"{}",
        capture_output=True,
        env={"PATH": "/usr/bin:/bin", variable: str(tmp_path / "missing")},
        check=False,
        timeout=TIMEOUT,
    )
    assert result.returncode == 0
    assert result.stdout == b""


# Notes directory and markers


# @spec NOTES-DIR-001
def test_notes_directory_is_created_and_nothing_written_elsewhere(session: Session) -> None:
    """The session directory beside the transcript may not exist yet."""
    assert not (session.project / SESSION).exists()
    run(launch(session))
    written = {p.relative_to(session.project) for p in session.project.rglob("*") if p.is_file()}
    assert written == {Path(SESSION, "subagent-notes", f"{AGENT}.launched")}


# @spec NOTES-DIR-002
def test_an_existing_marker_counts_as_the_step_taken(session: Session) -> None:
    """A second registration of the hooks finds the step made and does nothing."""
    session.mark(AGENT, "launched")
    before = session.marker(AGENT, "launched").read_text()
    assert output(run(launch(session)), "PostToolUse") == ""
    assert session.marker(AGENT, "launched").read_text() == before


# @spec NOTES-DIR-002, NOTES-SAFE-004
def test_markers_are_created_exclusively(session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each marker is created with O_CREAT | O_EXCL, so only one run can make it."""
    module = load_script()
    flags: dict[str, int] = {}
    real_open = os.open

    def spy(path: str | os.PathLike[str], flag: int, *args: int) -> int:
        flags[Path(path).name] = flag
        return real_open(path, flag, *args)

    monkeypatch.setattr(module.os, "open", spy)
    events = [
        launch(session, foreground=True),
        stop(session),
        pre_send(session),
        start(session),
        send(session),
        subagent_stop(session, NOTES),
        pre_send(session, message="Now list the docs."),
        start(session),
    ]
    for event in events:
        module.main(json.dumps(event).encode(), ATTENDED)
    for step in ("launched", "finished", "asked", "sent", "resumed", "done"):
        name = f"{AGENT}.{step}"
        assert name in flags, name
        assert flags[name] & os.O_CREAT, name
        assert flags[name] & os.O_EXCL, name


# @spec NOTES-DIR-003
@pytest.mark.parametrize(
    "bad",
    ["../escape", "a/b", "", "abc def", "abc.launched", "abc\n", "é1", "١٢٣", 123],
    ids=["dotdot", "slash", "empty", "space", "dot", "newline", "accent", "arabic-digits", "int"],
)
def test_invalid_agent_ids_are_ignored(session: Session, bad: object) -> None:
    """An ID is used in a file name only when it is plain ASCII letters and digits."""
    assert output(run(launch(session, agent=bad)), "PostToolUse") == ""
    assert session.files() == set()
    assert not (session.project / "escape.launched").exists()


# @spec NOTES-DIR-004
@pytest.mark.parametrize(
    "path",
    ["relative/session.jsonl", "/abs/session.json", "/abs/session", "", 123],
    ids=["relative", "other-suffix", "no-suffix", "empty", "int"],
)
def test_odd_transcript_paths_are_ignored(session: Session, path: object) -> None:
    """The notes directory is derived only from an absolute .jsonl transcript path."""
    event = launch(session) | {"transcript_path": path}
    assert output(run(event, cwd=session.project), "PostToolUse") == ""
    assert not any(session.project.rglob("*"))


# Track


# @spec NOTES-TRACK-001
def test_launch_is_tracked(session: Session) -> None:
    """A main-agent launch records the agent's type, description, name and time."""
    run(launch(session, name="lister"))
    launched = json.loads(session.marker(AGENT, "launched").read_text())
    assert set(launched) == {"agent_type", "description", "name", "time"}
    assert launched["agent_type"] == "Explore"
    assert launched["description"] == "List files"
    assert launched["name"] == "lister"
    assert re.fullmatch(ISO_UTC, launched["time"])


# @spec NOTES-TRACK-001
def test_launch_with_no_name_records_an_empty_one(session: Session) -> None:
    """Most launches have no name."""
    run(launch(session))
    assert json.loads(session.marker(AGENT, "launched").read_text())["name"] == ""


# @spec NOTES-TRACK-001
def test_launch_with_no_description_records_an_empty_one(session: Session) -> None:
    """The description is an empty string when the launch gave none."""
    event = launch(session)
    del event["tool_input"]["description"]
    run(event)
    assert json.loads(session.marker(AGENT, "launched").read_text())["description"] == ""


# @spec NOTES-TRACK-001
@pytest.mark.parametrize("agent_id", [None, ""], ids=["null", "empty"])
def test_null_or_empty_agent_id_is_the_main_agent(session: Session, agent_id: str | None) -> None:
    """The main agent is the one whose agent_id is absent, null or empty."""
    run(launch(session, agent_id=agent_id))
    assert session.marker(AGENT, "launched").is_file()


# @spec NOTES-TRACK-001
def test_launch_with_no_agent_type_is_not_tracked(session: Session) -> None:
    """Tracking needs a non-empty agent type."""
    assert output(run(launch(session, launched_type="")), "PostToolUse") == ""
    assert session.files() == set()


# @spec NOTES-TRACK-002
def test_launch_prints_the_counting_line(session: Session) -> None:
    """The line tells the main agent the ID, and the wrap-up where the notes go."""
    expected = f"[subagent-notes] agent {AGENT}, notes in {session.notes}"
    assert not expected.endswith("/")
    assert output(run(launch(session)), "PostToolUse") == expected


# @spec NOTES-TRACK-003
def test_launch_from_inside_a_subagent_is_not_tracked(session: Session) -> None:
    """Only the main agent's launches are tracked."""
    event = launch(session, agent_id=OTHER, agent_type="general-purpose")
    assert output(run(event), "PostToolUse") == ""
    assert session.files() == set()


# @spec NOTES-TRACK-004
def test_fork_is_not_tracked(session: Session) -> None:
    """A fork shares the main conversation, so it isn't asked for notes."""
    assert output(run(launch(session, launched_type="fork")), "PostToolUse") == ""
    assert session.files() == set()


# @spec NOTES-TRACK-005
def test_foreground_launch_is_already_finished(session: Session) -> None:
    """A foreground subagent stopped before its launch could be tracked."""
    run(launch(session, foreground=True))
    assert session.files() == {f"{AGENT}.launched", f"{AGENT}.finished"}


# @spec NOTES-TRACK-005
def test_background_launch_is_not_yet_finished(session: Session) -> None:
    """A background launch returns while the subagent runs."""
    run(launch(session))
    assert session.files() == {f"{AGENT}.launched"}


# Finish


# @spec NOTES-FIN-001
def test_stop_of_a_tracked_agent_marks_it_finished(session: Session) -> None:
    """A tracked background agent's stop makes it ready to be asked."""
    session.mark(AGENT, "launched")
    run(subagent_stop(session, REPORT))
    assert session.files() == {f"{AGENT}.{s}" for s in ("launched", "finished", "state")}
    assert session.marker(AGENT, "state").read_text() == "stopped"


# @spec NOTES-FIN-001
def test_stop_before_tracking_still_marks_finished(session: Session) -> None:
    """A subagent can stop before its launch is tracked; its stop still counts."""
    run(subagent_stop(session, "done"))
    assert session.files() == {f"{AGENT}.finished", f"{AGENT}.state"}


# @spec NOTES-FIN-003
def test_start_marks_the_agent_running(session: Session) -> None:
    """A run in progress is recorded, tracked agent or not."""
    run(start(session))
    assert session.marker(AGENT, "state").read_text() == "running"
    run(subagent_stop(session, REPORT))
    assert session.marker(AGENT, "state").read_text() == "stopped"


# @spec NOTES-FIN-002
@pytest.mark.parametrize("name", ["SubagentStart", "SubagentStop"])
def test_internal_agents_are_ignored(session: Session, name: str) -> None:
    """Claude Code's own agents start and stop with an empty agent type."""
    session.mark(AGENT, "launched", "pending=question", "sent", "resumed")
    before = session.files()
    event = subagent_event(session, name, agent_type="", last_assistant_message="x")
    assert output(run(event), name) == ""
    assert session.files() == before


# Ask


# @spec NOTES-ASK-001
def test_stop_asks_each_finished_agent_once(session: Session) -> None:
    """An agent is listed at one Stop only, even if nothing was sent to it."""
    session.mark(AGENT, "launched", "finished")
    assert AGENT in output(run(stop(session), ATTENDED), "Stop")
    assert session.marker(AGENT, "asked").is_file()
    assert output(run(stop(session), ATTENDED), "Stop") == ""
    assert session.files() == {f"{AGENT}.{s}" for s in ("launched", "finished", "asked")}


# @spec NOTES-ASK-001, NOTES-ASK-003
def test_stop_skips_agents_already_asked_or_unfinished(session: Session) -> None:
    """An agent already asked, or still running, isn't listed."""
    session.mark(AGENT, "launched", "finished", "asked")
    session.mark(OTHER, "launched")
    assert output(run(stop(session), ATTENDED), "Stop") == ""
    assert not session.marker(OTHER, "asked").exists()


# @spec NOTES-ASK-001
def test_stop_waits_for_a_busy_agent(session: Session) -> None:
    """An agent running a later piece of work is asked once that run stops, not during it."""
    session.mark(AGENT, "launched", "finished")
    session.marker(AGENT, "state").write_text("running")
    assert output(run(stop(session), ATTENDED), "Stop") == ""
    assert not session.marker(AGENT, "asked").exists()
    session.marker(AGENT, "state").write_text("stopped")
    assert AGENT in output(run(stop(session), ATTENDED), "Stop")


# @spec NOTES-ASK-001
def test_stop_skips_an_agent_that_already_has_notes(session: Session) -> None:
    """Notes captured from a question the main agent sent on its own aren't asked for again."""
    session.mark(AGENT, "launched", "finished", "md")
    assert output(run(stop(session), ATTENDED), "Stop") == ""


# @spec NOTES-ASK-001
def test_stop_skips_an_agent_already_sent_the_question(session: Session) -> None:
    """An agent sent the question by someone else isn't asked again."""
    session.mark(AGENT, "launched", "finished", "sent")
    assert output(run(stop(session), ATTENDED), "Stop") == ""
    assert not session.marker(AGENT, "asked").exists()


# @spec NOTES-ASK-002
def test_ask_output_is_the_filled_template(session: Session) -> None:
    """The context names the agents just listed, sorted, with the question; no one else."""
    session.mark(OTHER, "launched", "finished")
    session.mark(AGENT, "launched", "finished")
    session.mark(THIRD, "launched", "finished", "asked", "sent")
    module = load_script()
    expected = module.ASK_TEMPLATE.format(
        agents=f"{AGENT}, {OTHER}", question=module.FIXED_QUESTION
    )
    assert output(run(stop(session), ATTENDED), "Stop") == expected


# @spec NOTES-ASK-006
@pytest.mark.parametrize(
    "needle",
    ["{agents}", "{question}", "SendMessage", "word for word", "relay", "follow", "act on"],
)
def test_ask_template_gives_the_housekeeping_rules(needle: str) -> None:
    """The template says how to send the question and to keep the replies out of the work."""
    template = load_script().ASK_TEMPLATE
    assert template.startswith("Subagent notes:")
    assert needle in template


# @spec NOTES-ASK-006
def test_ask_template_says_not_to_mention_the_exchange() -> None:
    """The exchange is housekeeping the developer doesn't need to hear about."""
    template = load_script().ASK_TEMPLATE
    assert re.search(r"(don't|do not|not to) mention", template)
    assert "unless the developer asks" in template


# @spec NOTES-ASK-003
def test_stop_with_nothing_to_ask_prints_nothing(session: Session) -> None:
    """Most turns end with nothing to ask, and add no context."""
    assert output(run(stop(session), ATTENDED), "Stop") == ""


# @spec NOTES-ASK-004
@pytest.mark.parametrize(
    "env",
    [{}, {"CLAUDE_CODE_SESSION_ATTENDED": "0"}, {"CLAUDE_CODE_SESSION_ATTENDED": "true"}],
    ids=["unset", "zero", "true"],
)
def test_unattended_stop_does_nothing(session: Session, env: dict[str, str]) -> None:
    """In a -p run the housekeeping turn would replace the run's result."""
    session.mark(AGENT, "launched", "finished")
    assert output(run(stop(session), env), "Stop") == ""
    assert not session.marker(AGENT, "asked").exists()


# @spec NOTES-ASK-005
@pytest.mark.parametrize("active", [True, False], ids=["active", "inactive"])
def test_stop_hook_active_makes_no_difference(session: Session, *, active: bool) -> None:
    """Agents that finish during the housekeeping turn are asked too."""
    session.mark(AGENT, "launched", "finished")
    assert AGENT in output(run(stop(session, active=active), ATTENDED), "Stop")


# @spec NOTES-ASK-007
def test_a_failed_ask_keeps_the_agents_already_listed(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One agent's fault doesn't cost the others their question."""
    session.mark(AGENT, "launched", "finished")
    session.mark(OTHER, "launched", "finished")
    module = load_script()
    real_open = os.open

    def failing(path: str | os.PathLike[str], flag: int, *args: int) -> int:
        if Path(path).name == f"{OTHER}.asked":
            raise OSError(28, "No space left on device")
        return real_open(path, flag, *args)

    monkeypatch.setattr(module.os, "open", failing)
    printed = json.loads(module.main(json.dumps(stop(session)).encode(), ATTENDED))
    text = printed["hookSpecificOutput"]["additionalContext"]
    assert AGENT in text
    assert OTHER not in text


# Send


# @spec NOTES-SEND-003
@pytest.mark.parametrize(
    ("message", "expected"),
    [(None, "question"), ("  {q}\n", "question"), ("Now list the docs.", "other")],
    ids=["question", "padded-question", "other"],
)
def test_presend_records_what_is_pending(
    session: Session, message: str | None, expected: str
) -> None:
    """Before the run a message starts, the hooks note whether it is the question."""
    session.mark(AGENT, "launched", "finished")
    text = None if message is None else message.replace("{q}", question())
    assert output(run(pre_send(session, message=text)), "PreToolUse") == ""
    assert session.marker(AGENT, "pending").read_text() == expected


# @spec NOTES-SEND-003
def test_presend_replaces_the_pending_message(session: Session) -> None:
    """Each message to the agent replaces what was pending, so a denied question doesn't linger."""
    session.mark(AGENT, "launched", "finished", "pending=question")
    run(pre_send(session, message="Now list the docs."))
    assert session.marker(AGENT, "pending").read_text() == "other"


# @spec NOTES-SEND-003
@pytest.mark.parametrize("change", ["untracked", "from-subagent"])
def test_presend_ignores_untracked_and_subagent_sends(session: Session, change: str) -> None:
    """Only the main agent's messages to tracked agents are noted."""
    session.mark(AGENT, "launched", "finished")
    event = (
        pre_send(session, to=OTHER)
        if change == "untracked"
        else pre_send(session, agent_id=THIRD, agent_type="general-purpose")
    )
    run(event)
    assert session.files() == {f"{AGENT}.launched", f"{AGENT}.finished"}


def launched_with_name(session: Session, agent: str, name: str) -> None:
    """Record an agent as launched with a name, as Track does."""
    session.mark(agent, "launched", "finished")
    record = {"agent_type": "Explore", "description": "List files", "name": name, "time": "t"}
    session.marker(agent, "launched").write_text(json.dumps(record))


# @spec NOTES-SEND-003
def test_presend_recognizes_an_agent_by_name(session: Session) -> None:
    """A work message sent by name replaces a pending question, so it can't be taken for one."""
    launched_with_name(session, AGENT, "lister")
    session.mark(AGENT, "pending=question")
    run(pre_send(session, to="lister", message="Now list the docs."))
    assert session.marker(AGENT, "pending").read_text() == "other"


# @spec NOTES-SEND-004
@pytest.mark.parametrize("message", [None, "Now list the docs."], ids=["question", "other"])
def test_presend_to_a_shared_name_marks_every_match_other(
    session: Session, message: str | None
) -> None:
    """A name two tracked agents share can't be resolved, so neither gets a pending question."""
    launched_with_name(session, AGENT, "lister")
    launched_with_name(session, OTHER, "lister")
    session.mark(AGENT, "pending=question")
    run(pre_send(session, to="lister", message=message))
    assert session.marker(AGENT, "pending").read_text() == "other"
    assert session.marker(OTHER, "pending").read_text() == "other"


# @spec NOTES-SEND-001
def test_sending_the_question_by_name_marks_the_agent_sent(session: Session) -> None:
    """The question counts whether it was addressed by ID or by name."""
    launched_with_name(session, AGENT, "lister")
    session.mark(AGENT, "pending=question")
    run(send(session, to="lister"))
    assert session.marker(AGENT, "sent").is_file()


# @spec NOTES-SEND-003
def test_the_question_to_a_busy_agent_is_not_pending(session: Session) -> None:
    """A question sent into a run in progress isn't a notes run, and doesn't count as sent."""
    session.mark(AGENT, "launched", "finished")
    session.marker(AGENT, "state").write_text("running")
    run(pre_send(session))
    assert session.marker(AGENT, "pending").read_text() == "other"
    run(send(session))
    assert not session.marker(AGENT, "sent").exists()


# @spec NOTES-SEND-001
@pytest.mark.parametrize("padding", ["", "  ", "\n"], ids=["exact", "spaces", "newline"])
def test_sending_the_question_marks_the_agent_sent(session: Session, padding: str) -> None:
    """A successful send of the question to a finished agent confirms it was asked."""
    session.mark(AGENT, "launched", "finished", "pending=question")
    assert (
        output(run(send(session, message=f"{padding}{question()}{padding}")), "PostToolUse") == ""
    )
    assert session.marker(AGENT, "sent").is_file()


def changed_send(session: Session, change: str) -> dict[str, Any]:
    """A send that differs from the question's in one way."""
    q = question()
    changes: dict[str, Callable[[], dict[str, Any]]] = {
        "failed": lambda: send(session, response={"success": False}),
        "no-success": lambda: send(session, response={"resumedAgentId": AGENT}),
        "success-string": lambda: send(session, response={"success": "true"}),
        "untracked-recipient": lambda: send(session, to=OTHER),
        "unfinished-recipient": lambda: send(session, to=THIRD),
        "running-recipient": lambda: send(session, to=OTHER),
        "other-message": lambda: send(session, message="Please continue with the next file."),
        "upper-case": lambda: send(session, message=q.upper()),
        "prefixed": lambda: send(session, message=f"Thanks. {q}"),
        "suffixed": lambda: send(session, message=f"{q} Thanks."),
        "inner-newline": lambda: send(session, message=q.replace(" ", "\n", 1)),
        "no-final-period": lambda: send(session, message=q.removesuffix(".")),
        "from-subagent": lambda: send(session, agent_id=THIRD, agent_type="general-purpose"),
    }
    return changes[change]()


# @spec NOTES-SEND-002
@pytest.mark.parametrize(
    "change",
    [
        "failed",
        "no-success",
        "success-string",
        "untracked-recipient",
        "unfinished-recipient",
        "running-recipient",
        "other-message",
        "upper-case",
        "prefixed",
        "suffixed",
        "inner-newline",
        "no-final-period",
        "from-subagent",
    ],
)
def test_other_sends_mark_nothing(session: Session, change: str) -> None:
    """A failed send, another recipient or message, or a subagent's send changes nothing."""
    session.mark(AGENT, "launched", "finished", "asked")
    session.mark(THIRD, "launched")
    if change == "running-recipient":
        # PreToolUse found it running, so it recorded the question as `other`.
        session.mark(OTHER, "launched", "finished", "asked", "pending=other")
        session.marker(OTHER, "state").write_text("running")
    before = session.files()
    assert output(run(changed_send(session, change)), "PostToolUse") == ""
    assert session.files() == before


# Resume


# @spec NOTES-RES-001
@pytest.mark.parametrize("sent", [False, True], ids=["before-post", "after-post"])
def test_start_after_the_question_marks_resumed(session: Session, *, sent: bool) -> None:
    """The run the question starts is the notes run, whether or not `.sent` came first."""
    session.mark(AGENT, "launched", "finished", "asked", "pending=question")
    if sent:
        session.mark(AGENT, "sent")
    run(start(session))
    assert session.marker(AGENT, "resumed").is_file()
    assert not session.marker(AGENT, "done").exists()


# @spec NOTES-RES-001, NOTES-SAFE-004
def test_a_duplicate_start_of_the_notes_run_keeps_the_window_open(session: Session) -> None:
    """A second copy of the hooks seeing the notes run's start mustn't close the window."""
    session.mark(AGENT, "launched", "finished", "pending=question")
    run(start(session))
    run(start(session))
    assert not session.marker(AGENT, "done").exists()
    run(subagent_stop(session, NOTES))
    assert notes_file(session)[1] == NOTES


# @spec NOTES-RES-002
def test_start_with_nothing_pending_marks_nothing(session: Session) -> None:
    """A run nobody messaged (a background agent's first) isn't a notes run."""
    session.mark(AGENT, "launched")
    run(start(session))
    assert session.files() == {f"{AGENT}.launched", f"{AGENT}.state"}


# @spec NOTES-RES-001, NOTES-RES-003
def test_start_with_another_message_first_is_not_the_notes_run(session: Session) -> None:
    """A resume for real work, before any question, isn't a notes run."""
    session.mark(AGENT, "launched", "finished", "asked", "pending=other")
    run(start(session))
    assert not session.marker(AGENT, "resumed").exists()
    assert not session.marker(AGENT, "done").exists()


# @spec NOTES-RES-003
@pytest.mark.parametrize("captured", [True, False], ids=["notes-saved", "nothing-saved"])
def test_a_later_message_closes_the_capture_window(session: Session, *, captured: bool) -> None:
    """A run started by another message after the notes run is real work again."""
    session.mark(AGENT, "launched", "finished", "sent", "resumed", "pending=other")
    if captured:
        session.mark(AGENT, "md")
    run(start(session))
    assert session.marker(AGENT, "done").is_file()


# Capture


@pytest.fixture
def notes_run(session: Session) -> Session:
    """A session whose agent is in its notes run."""
    session.mark(AGENT, "launched", "finished", "asked", "pending=question", "sent", "resumed")
    return session


# @spec NOTES-CAP-001
def test_handback_writes_the_notes_file(notes_run: Session) -> None:
    """In auto mode the reply comes as a hand-back."""
    run(handback(notes_run, NOTES))
    assert notes_file(notes_run)[1] == NOTES


# @spec NOTES-CAP-001
def test_handback_replaces_an_existing_notes_file(notes_run: Session) -> None:
    """In auto mode the first stop's text can be a preamble before the hand-back."""
    (notes_run.notes / f"{AGENT}.md").write_text('---\nagent_id: "x"\n---\nHanding back now.\n')
    run(handback(notes_run, NOTES))
    assert notes_file(notes_run)[1] == NOTES


# @spec NOTES-CAP-002
def test_stop_writes_the_notes_file_when_none_exists(notes_run: Session) -> None:
    """Outside auto mode the reply is the resumed run's last message."""
    run(subagent_stop(notes_run, NOTES))
    assert notes_file(notes_run)[1] == NOTES


# @spec NOTES-CAP-002
def test_stop_with_an_empty_message_writes_nothing(notes_run: Session) -> None:
    """An empty last message isn't a reply."""
    run(subagent_stop(notes_run, ""))
    assert not (notes_run.notes / f"{AGENT}.md").exists()


# @spec NOTES-CAP-002
def test_stop_does_not_replace_a_handback(notes_run: Session) -> None:
    """Text at a later stop never replaces a delivered hand-back."""
    run(handback(notes_run, NOTES))
    run(subagent_stop(notes_run, "Something else."))
    assert notes_file(notes_run)[1] == NOTES


# @spec NOTES-CAP-002
def test_stop_publishes_without_clobbering(
    notes_run: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A hand-back's notes written between a stop's check and its write survive."""
    module = load_script()
    real_link = os.link

    def racing_link(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        Path(dst).write_text('---\nagent_id: "x"\n---\nfrom the hand-back\n')
        real_link(src, dst)

    monkeypatch.setattr(module.os, "link", racing_link)
    module.main(json.dumps(subagent_stop(notes_run, "preamble")).encode(), {})
    assert notes_file(notes_run)[1] == "from the hand-back\n"
    assert not [p for p in notes_run.notes.iterdir() if p.name.endswith(".tmp")]


def no_hard_links(*_: object) -> None:
    """`os.link` on a filesystem without hard links, such as FAT."""
    raise OSError(1, "Operation not permitted")


# @spec NOTES-CAP-002
def test_stop_saves_notes_without_hard_links(
    notes_run: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without hard links, the stop's notes are still saved."""
    module = load_script()
    monkeypatch.setattr(module.os, "link", no_hard_links)
    module.main(json.dumps(subagent_stop(notes_run, NOTES)).encode(), {})
    assert notes_file(notes_run)[1] == NOTES
    assert not [p for p in notes_run.notes.iterdir() if p.name.endswith(".tmp")]


# @spec NOTES-CAP-002
def test_stop_never_clobbers_without_hard_links(
    notes_run: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fallback still leaves an existing notes file alone."""
    module = load_script()
    monkeypatch.setattr(module.os, "link", no_hard_links)
    module.main(json.dumps(handback(notes_run, NOTES)).encode(), {})
    module.main(json.dumps(subagent_stop(notes_run, "preamble")).encode(), {})
    assert notes_file(notes_run)[1] == NOTES


# @spec NOTES-CAP-003
@pytest.mark.parametrize(
    "steps",
    [
        ("launched", "finished", "pending=other"),
        ("launched", "finished", "sent", "resumed", "done"),
    ],
    ids=["no-notes-run", "after-notes-run"],
)
@pytest.mark.parametrize("via", ["handback", "stop"])
def test_no_notes_outside_the_capture_window(
    session: Session, steps: tuple[str, ...], via: str
) -> None:
    """Outside the notes run, a reply is a work report, not notes."""
    session.mark(AGENT, *steps)
    run(handback(session, REPORT) if via == "handback" else subagent_stop(session, REPORT))
    assert not (session.notes / f"{AGENT}.md").exists()


# @spec NOTES-CAP-004
def test_notes_file_format(session: Session) -> None:
    """Front matter of JSON strings survives any description; the reply follows verbatim."""
    session.mark(AGENT, "finished", "pending=question", "sent", "resumed")
    tricky = 'Say "hi": then\nleave — ünïcode'
    launched = {"agent_type": "general-purpose", "description": tricky, "time": "t"}
    session.marker(AGENT, "launched").write_text(json.dumps(launched))
    reply = "\n  - a note with trailing spaces   \n\n"
    run(handback(session, reply))
    meta, body = notes_file(session)
    assert set(meta) == {"agent_id", "agent_type", "description", "captured"}
    assert meta["agent_id"] == AGENT
    assert meta["agent_type"] == "general-purpose"
    assert meta["description"] == tricky
    assert re.fullmatch(ISO_UTC, meta["captured"])
    assert body == reply


# @spec NOTES-CAP-004
def test_reply_without_a_final_newline_gets_one(notes_run: Session) -> None:
    """The file ends with a newline whatever the reply."""
    run(handback(notes_run, "none"))
    assert notes_file(notes_run)[1] == "none\n"


# @spec NOTES-CAP-004
def test_missing_description_is_an_empty_string(session: Session) -> None:
    """A launch record with no description still gives a well-formed header."""
    session.mark(AGENT, "finished", "pending=question", "sent", "resumed")
    session.marker(AGENT, "launched").write_text(json.dumps({"agent_type": "Explore", "time": "t"}))
    run(handback(session, NOTES))
    assert notes_file(session)[0]["description"] == ""


# @spec NOTES-CAP-005
def test_handback_notes_are_renamed_into_place(
    notes_run: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A reader never sees a partial notes file."""
    module = load_script()
    renames: list[tuple[Path, Path]] = []
    real_replace = os.replace

    def spy(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        renames.append((Path(src), Path(dst)))
        real_replace(src, dst)

    monkeypatch.setattr(module.os, "replace", spy)
    module.main(json.dumps(handback(notes_run, NOTES)).encode(), {})
    target = notes_run.notes / f"{AGENT}.md"
    assert renames == [(renames[0][0], target)]
    assert renames[0][0] != target
    assert renames[0][0].parent == notes_run.notes
    assert not [p for p in notes_run.notes.iterdir() if p.name.endswith(".tmp")]


# @spec NOTES-CAP-006
@pytest.mark.parametrize("content", ["", "not json", "[1, 2]"], ids=["empty", "not-json", "array"])
def test_a_damaged_launch_record_still_saves_the_notes(session: Session, content: str) -> None:
    """A crash can leave `.launched` empty; the reply is kept anyway."""
    session.mark(AGENT, "finished", "pending=question", "sent", "resumed")
    session.marker(AGENT, "launched").write_text(content)
    run(handback(session, NOTES))
    meta, body = notes_file(session)
    assert body == NOTES
    assert meta["agent_type"] == ""
    assert meta["description"] == ""


# Flows, in the event orders the probe logged


def replay(events: list[dict[str, Any]]) -> list[str]:
    """Run each event in order, attended, and return what each printed."""
    return [run(event, ATTENDED).stdout.decode() for event in events]


# @spec NOTES-TRACK-005, NOTES-RES-001, NOTES-CAP-001
def test_foreground_flow_in_auto_mode(session: Session) -> None:
    """Foreground: the subagent stops before its launch is tracked, and hands back its reply."""
    printed = replay(
        [
            start(session),
            handback(session, REPORT),
            subagent_stop(session, ""),
            launch(session, foreground=True),
            stop(session),
            pre_send(session),
            start(session),
            send(session),
            subagent_stop(session, NOTES),
            handback(session, NOTES),
            subagent_stop(session, ""),
        ],
    )
    assert "[subagent-notes]" in printed[3]
    assert AGENT in printed[4]
    assert notes_file(session)[1] == NOTES


# @spec NOTES-TRACK-005, NOTES-RES-001, NOTES-CAP-002
def test_foreground_flow_in_manual_mode(session: Session) -> None:
    """Outside auto mode the reply is the resumed run's last message."""
    replay(
        [
            start(session),
            subagent_stop(session, REPORT),
            launch(session, foreground=True),
            stop(session),
            pre_send(session),
            start(session),
            send(session),
            subagent_stop(session, NOTES),
        ],
    )
    assert notes_file(session)[1] == NOTES
    assert session.marker(AGENT, "sent").is_file()


# @spec NOTES-FIN-001, NOTES-RES-001, NOTES-RES-003, NOTES-CAP-001
def test_background_flow_then_later_work(session: Session) -> None:
    """Background: the stop marks it finished; a later work run doesn't touch the notes."""
    printed = replay(
        [
            launch(session),
            start(session),
            handback(session, REPORT),
            subagent_stop(session, ""),
            stop(session),
            pre_send(session),
            send(session),
            start(session),
            handback(session, NOTES),
            subagent_stop(session, ""),
            pre_send(session, message="Now list the docs."),
            start(session),
            handback(session, REPORT),
            subagent_stop(session, REPORT),
        ],
    )
    assert AGENT in printed[4]
    assert notes_file(session)[1] == NOTES
    assert session.marker(AGENT, "done").is_file()


# @spec NOTES-FIN-003, NOTES-ASK-001
def test_an_agent_given_more_work_is_asked_after_it(session: Session) -> None:
    """More work in the same turn: the agent is asked only once that work has stopped."""
    printed = replay(
        [
            launch(session),
            start(session),
            subagent_stop(session, REPORT),
            pre_send(session, message="Now list the docs."),
            send(session, message="Now list the docs."),
            start(session),
            stop(session),
            subagent_stop(session, REPORT),
            stop(session),
            pre_send(session),
            start(session),
            send(session),
            subagent_stop(session, NOTES),
        ],
    )
    assert AGENT not in printed[6]
    assert AGENT in printed[8]
    assert notes_file(session)[1] == NOTES


# @spec NOTES-SEND-003, NOTES-RES-003
def test_work_sent_by_name_after_the_notes_is_not_taken_for_notes(session: Session) -> None:
    """A later message by name closes the capture window like one by ID."""
    replay(
        [
            start(session),
            subagent_stop(session, REPORT),
            launch(session, foreground=True, name="lister"),
            stop(session),
            pre_send(session),
            start(session),
            send(session),
            subagent_stop(session, NOTES),
            pre_send(session, to="lister", message="Now list the docs."),
            start(session),
            handback(session, "WORK REPORT 2"),
            subagent_stop(session, "WORK REPORT 2"),
        ],
    )
    assert notes_file(session)[1] == NOTES
    assert session.marker(AGENT, "done").is_file()


# @spec NOTES-SEND-003, NOTES-RES-001
def test_a_denied_question_then_work_takes_no_notes(session: Session) -> None:
    """A denied question leaves `question` pending until the next message replaces it."""
    replay(
        [
            launch(session, foreground=True),
            stop(session),
            pre_send(session),
            pre_send(session, message="Now list the docs."),
            start(session),
            subagent_stop(session, REPORT),
        ],
    )
    assert not session.marker(AGENT, "resumed").exists()
    assert not (session.notes / f"{AGENT}.md").exists()


# Safety


def acting_event(session: Session, name: str) -> tuple[dict[str, Any], str]:
    """For each kind of event, a state in which its step acts, and the file the step makes."""
    states: dict[str, tuple[tuple[str, ...], Callable[[], dict[str, Any]], str]] = {
        "launch": ((), lambda: launch(session), "launched"),
        "subagent-stop": (("launched",), lambda: subagent_stop(session, "{}"), "finished"),
        "stop": (("launched", "finished"), lambda: stop(session), "asked"),
        "pre-send": (("launched", "finished", "asked"), lambda: pre_send(session), "pending"),
        "send": (
            ("launched", "finished", "asked", "pending=question"),
            lambda: send(session),
            "sent",
        ),
        "start": (
            ("launched", "finished", "asked", "pending=question"),
            lambda: start(session),
            "resumed",
        ),
        "handback": (
            ("launched", "finished", "asked", "pending=question", "sent", "resumed"),
            lambda: handback(session, NOTES),
            "md",
        ),
    }
    steps, build, made = states[name]
    if steps:
        session.mark(AGENT, *steps)
    return build(), f"{AGENT}.{made}"


ACTING_EVENTS = ["launch", "subagent-stop", "stop", "pre-send", "send", "start", "handback"]


# @spec NOTES-SAFE-001
@pytest.mark.parametrize("name", ACTING_EVENTS)
def test_script_never_blocks_or_rewrites(session: Session, name: str) -> None:
    """The hooks only observe and add context; they never stop or change anything."""
    event, _ = acting_event(session, name)
    result = run(event, ATTENDED)
    if result.stdout.strip():
        printed = json.loads(result.stdout)
        assert not FORBIDDEN_OUTPUT_KEYS & set(printed)
        assert not FORBIDDEN_OUTPUT_KEYS & set(printed.get("hookSpecificOutput", {}))


# @spec NOTES-SAFE-002
@pytest.mark.parametrize(
    "stdin",
    [
        b"",
        b"not json",
        b"[1, 2]",
        b"null",
        b'{"hook_event_name": "Stop"}',
        b'{"hook_event_name": "Stop", "transcript_path": "/x/\xff.jsonl"}',
    ],
    ids=["empty", "not-json", "array", "null", "no-fields", "not-utf8"],
)
def test_malformed_input_exits_quietly(stdin: bytes) -> None:
    """Bad input costs nothing but this event."""
    assert run(stdin, ATTENDED).stdout == b""


# @spec NOTES-SAFE-002
def test_main_takes_raw_bytes_that_arent_utf8(session: Session) -> None:
    """Decoding happens inside the guard, whatever the locale the hook runs under."""
    raw = json.dumps(launch(session)).encode().replace(b"List files", b"List \xff files")
    assert load_script().main(raw, {}) == ""
    assert session.files() == set()


# @spec NOTES-SAFE-002
def test_an_error_after_a_marker_keeps_the_marker(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fault costs only the rest of that step; what was made stays."""
    module = load_script()

    def broken(*_: object) -> str:
        message = "boom"
        raise RuntimeError(message)

    monkeypatch.setattr(module, "counting_line", broken)
    assert module.main(json.dumps(launch(session)).encode(), {}) == ""
    assert session.marker(AGENT, "launched").is_file()


# @spec NOTES-SAFE-002
def test_unwritable_notes_directory_exits_quietly(session: Session) -> None:
    """A notes directory that can't be made costs only the notes."""
    (session.project / SESSION).mkdir()
    (session.project / SESSION / "subagent-notes").write_text("a file, not a directory")
    assert run(launch(session)).stdout == b""


# @spec NOTES-SAFE-003
@pytest.mark.parametrize("name", ACTING_EVENTS)
def test_each_step_acts_without_the_opt_out(session: Session, name: str) -> None:
    """The control for the opt-out test: in these states, every step makes its file."""
    event, made = acting_event(session, name)
    run(event, ATTENDED | {"SUBAGENT_NOTES": "on"})
    assert made in session.files()


# @spec NOTES-SAFE-003
@pytest.mark.parametrize("value", ["off", "OFF", "Off"])
@pytest.mark.parametrize("name", ACTING_EVENTS)
def test_opt_out_turns_every_step_off(session: Session, value: str, name: str) -> None:
    """`SUBAGENT_NOTES=off` leaves no notes and adds no context."""
    event, made = acting_event(session, name)
    before = session.files()
    assert run(event, ATTENDED | {"SUBAGENT_NOTES": value}).stdout == b""
    assert session.files() == before
    assert made not in session.files()


# @spec NOTES-SAFE-004
def test_concurrent_stops_ask_each_agent_once(session: Session, tmp_path: Path) -> None:
    """Hooks registered twice, or run in parallel, still list each agent once."""
    session.mark(AGENT, "launched", "finished")
    outputs = run_concurrently(stop(session), ATTENDED, 8, tmp_path)
    assert sum(1 for out in outputs if AGENT in out) == 1
    assert session.marker(AGENT, "asked").is_file()


# @spec NOTES-SAFE-004
def test_concurrent_launches_print_one_counting_line(session: Session, tmp_path: Path) -> None:
    """Only the run that creates `.launched` tells the main agent about it."""
    outputs = run_concurrently(launch(session), None, 8, tmp_path)
    assert sum(1 for out in outputs if "[subagent-notes]" in out) == 1


# In a live session: these specs are checked by the scripted manual runs. lidc reads `@spec`
# only in test code, so this test cites them; it checks only that the manual script covers each.


def manual_spec_ids() -> list[str]:
    """The IDs of the specs marked *(manual)*."""
    pattern = r"\*\*(NOTES-[A-Z]+-\d{3})\*\*:.*\*\(manual\)\*"
    return [str(spec) for spec in re.findall(pattern, SPECS.read_text())]


# @spec NOTES-LIVE-001, NOTES-LIVE-002, NOTES-LIVE-003
@pytest.mark.parametrize("spec", manual_spec_ids())
def test_manual_spec_is_in_the_manual_script(spec: str) -> None:
    """Each live-session spec has a step in the manual runs."""
    assert spec in MANUAL.read_text()
