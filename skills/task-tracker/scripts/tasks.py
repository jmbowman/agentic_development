#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Task tool: lint, rank and view a backlog kept as Backlog.md-format Markdown files.

Reads `backlog/tasks/` (this repo's tasks), `backlog/outbox/<repo>/` (tasks drafted for other
repos) and `backlog/focus.yml` (the developer's pins and weights), and never writes a task file.
Run it as `uv run --script tasks.py <command>`; `help` lists the commands. The task-tracker
skill's `references/task-format.md` describes the files it reads.

It needs only the standard library and the YAML parser vendored beside it in `_vendor/`, so it
also runs as `python3 tasks.py <command>` on Python 3.11 or later.
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from types import ModuleType

# The vendored parser's source directory; vendir.yml at this repo's root keeps it in sync.
VENDORED_PARSER = Path(__file__).resolve().parent / "_vendor" / "oneyaml-python" / "src"

DONE = "Done"
ACTIVE = "In Progress"
PERFORMERS = ("human", "agent")
TIERS = ("fast", "moderate", "strong")
EFFORTS = ("S", "M", "L")
DEADLINE_KINDS = ("hard", "soft", "target")
# Starting weights are Taskwarrior's urgency coefficients; `weights:` in focus.yml overrides them.
WEIGHTS: dict[str, float] = {
    "priority_high": 6.0,
    "priority_medium": 3.9,
    "priority_low": 1.8,
    "unblocks": 8.0,
    "due": 12.0,
    "active": 4.0,
    "effort_S": 2.0,
    "effort_M": 1.0,
    "waiting": 3.0,
    "age": 2.0,
}
DEADLINE_FACTOR = {"hard": 1.0, "soft": 0.6, "target": 0.3}
UNBLOCKS_CAP = 16  # the unblocks term grows with the square root of the count, up to this many
IMMINENT_DAYS = 7
DUE_HORIZON_DAYS = 14
GH_REF = re.compile(r"^gh:([\w.-]+/[\w.-]+)#(\d+)$")
# A task in a named repo: `<repo>#<ID>`, or forge-qualified, `<host>/<owner>/<repo>#<ID>`.
TASK_REF = re.compile(r"^(?:[\w.-]+/[\w.-]+/)?([\w.-]+)#([A-Za-z]+-[\d.]+)$")
DRAFT_REF = re.compile(r"^([\w.-]+)/([\w.-]+)$")
AGENT_ITEM = re.compile(r"^\s*- \[[ x]\].*\[agent\]", re.MULTILINE)
CACHE_SECONDS = 6 * 3600


@dataclass
class Task:
    """One task file: Backlog.md's own keys plus this pilot's custom ones."""

    id: str
    path: Path
    meta: dict[str, Any]
    body: str
    repo: str
    draft: bool = False
    blockers: list[str] = field(default_factory=list)  # open blockers, as display text
    unblocks: set[str] = field(default_factory=set)  # open tasks that transitively wait on this
    children: list[str] = field(default_factory=list)

    def get(self, key: str, default: str = "") -> str:
        """Return a frontmatter value as text."""
        value = self.meta.get(key)
        return default if value is None else str(value)

    def items(self, key: str) -> list[str]:
        """Return a frontmatter list as a list of strings."""
        value = self.meta.get(key) or []
        return [str(v) for v in value] if isinstance(value, list) else [str(value)]

    @property
    def open(self) -> bool:
        """Whether the task still needs work."""
        return self.get("status") != DONE

    @property
    def performer(self) -> str:
        """Who does the task: `human` or `agent`."""
        return self.get("performer").split(":")[0]


@dataclass
class Backlog:
    """Every loaded task, the developer's focus file, and the lint findings."""

    home: str
    tasks: dict[str, Task]
    pins: list[str]
    weights: dict[str, float]
    problems: list[str]
    today: dt.date
    statuses: list[str]
    types: list[str]  # the allowed `type` values from config.yml; empty when it sets none


def as_date(value: object) -> dt.date | None:
    """Return the date a frontmatter value starts with, or None when it isn't an ISO date."""
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


class SetupError(Exception):
    """The tool can't run here: the interpreter is too old, or the parser won't import."""


class YAMLRejectedError(Exception):
    """A YAML document the vendored parser rejected, for its syntax or for exceeding a limit."""


# @spec TASK-YAML-004, TASK-YAML-005, TASK-YAML-007
@functools.cache
def yaml_parser() -> ModuleType:
    """Import the vendored YAML parser, ahead of any other copy, with its pure-Python backend.

    Called only once a command needs YAML, so `help` works without the parser.

    Raises:
        SetupError: Python is older than 3.11, or the parser can't be imported.
    """
    # Ruff reads the project's 3.12 target, but `python3 tasks.py` may run on any interpreter.
    if sys.version_info < (3, 11):  # noqa: UP036
        message = f"tasks.py needs Python 3.11 or later; this is {platform.python_version()}"
        raise SetupError(message)
    # The library's only public switch; an invalid or `native` value found here would stop the
    # import, since only the pure backend is vendored.
    os.environ["ONEYAML_BACKEND"] = "pure"
    sys.path.insert(0, str(VENDORED_PARSER))
    # Imported here, after the path and backend are set, and only when a command needs it. Any
    # failure is a setup problem, such as a vendored copy using syntax this Python lacks.
    try:
        import oneyaml  # noqa: PLC0415
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        message = f"can't import the vendored YAML parser oneyaml from {VENDORED_PARSER} ({reason})"
        raise SetupError(" ".join(message.split())) from error
    return oneyaml


# @spec TASK-YAML-001, TASK-YAML-002, TASK-YAML-003
def parse_yaml(text: str) -> Any:  # noqa: ANN401 - a document's value has any shape; callers check
    """Parse one YAML document as YAML 1.2 under the core schema, with the untrusted limits.

    Raises:
        YAMLRejectedError: The parser rejected the document. Any other exception propagates.
    """
    oneyaml = yaml_parser()
    try:
        return oneyaml.loads(text, limits=oneyaml.Limits.untrusted())
    except oneyaml.YAMLError as error:
        raise YAMLRejectedError(str(error)) from error


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a Markdown file into its YAML frontmatter and its body.

    Raises:
        YAMLRejectedError: The frontmatter isn't valid YAML.
    """
    if not text.startswith("---\n"):
        return {}, text
    head, sep, body = text[4:].partition("\n---\n")
    if not sep:
        return {}, text
    meta = parse_yaml(head)
    return (meta if isinstance(meta, dict) else {}), body


def read_task(backlog: Backlog, path: Path) -> tuple[dict[str, Any], str] | None:
    """Read one task file, recording unreadable frontmatter as a problem."""
    try:
        return split_frontmatter(path.read_text(encoding="utf-8"))
    except YAMLRejectedError as error:
        reason = str(error).splitlines()[0]
        backlog.problems.append(f"{path.name}: frontmatter isn't valid YAML ({reason})")
        return None


def read_focus(root: Path, problems: list[str]) -> tuple[list[str], dict[str, float]]:
    """Read the developer's pins and weight overrides from focus.yml."""
    focus_file = root / "focus.yml"
    focus = parse_yaml(focus_file.read_text(encoding="utf-8")) if focus_file.exists() else {}
    if not isinstance(focus or {}, dict):
        problems.append("focus.yml: must be a mapping with `pins` and `weights`")
        return [], {}
    focus = focus or {}
    pins = focus.get("pins") or []
    pins = pins if isinstance(pins, list) else [pins]
    # Task IDs are upper case, as in dependencies; an outbox draft is named repo/slug as written.
    names = [str(p) if "/" in str(p) else str(p).upper() for p in pins]
    try:
        weights = {str(k): float(v) for k, v in dict(focus.get("weights") or {}).items()}
    except (TypeError, ValueError):
        problems.append("focus.yml: `weights` must map term names to numbers")
        weights = {}
    return names, weights


def load(root: Path, today: dt.date | None = None, *, private: bool = False) -> Backlog:
    """Load the backlog under `root` (a `backlog/` directory).

    Args:
        root: The `backlog/` directory.
        today: The date readiness and deadlines are judged against; defaults to now.
        private: Also load the gitignored drafts under `private/outbox/`.
    """
    config = parse_yaml((root / "config.yml").read_text(encoding="utf-8")) or {}
    home = str(config.get("project_name", root.resolve().parent.name))
    problems: list[str] = []
    pins, weights = read_focus(root, problems)
    backlog = Backlog(
        home=home,
        tasks={},
        pins=pins,
        weights={**WEIGHTS, **weights},
        problems=problems,
        # The local date: Backlog.md writes local dates, and a deferral ends on the developer's day.
        today=today or dt.datetime.now().astimezone().date(),
        statuses=[str(s) for s in config.get("statuses") or ["To Do", ACTIVE, DONE]],
        types=[str(t) for t in config.get("types") or []],
    )
    if "onStatusChange" in config or "on_status_change" in config:
        backlog.problems.append("config.yml: status-change callbacks aren't allowed")
    for folder in ("tasks", "completed"):
        for path in sorted((root / folder).glob("*.md")):
            parts = read_task(backlog, path)
            if parts:
                task_id = str(parts[0].get("id") or "").upper()
                add(backlog, Task(task_id, path, parts[0], parts[1], home))
    drafts = sorted(root.glob("outbox/*/*.md"))
    if private:
        drafts += sorted(root.glob("private/outbox/*/*.md"))
    for path in drafts:
        parts = read_task(backlog, path)
        if parts:
            repo = path.parent.name
            add(backlog, Task(f"{repo}/{path.stem}", path, parts[0], parts[1], repo, draft=True))
    return backlog


def add(backlog: Backlog, task: Task) -> None:
    """Add a task, recording a missing or repeated ID as a problem."""
    if not task.id:
        backlog.problems.append(f"{task.path.name}: no id")
    elif task.id in backlog.tasks:
        backlog.problems.append(f"{task.path.name}: id {task.id} is already used")
    else:
        backlog.tasks[task.id] = task


def github_state(ref: str, cache_file: Path) -> bool | None:
    """Return whether the GitHub issue or pull request `gh:owner/repo#N` is closed.

    A pull request closed without merging counts as closed. Answers are cached for six hours, so
    a reopened issue can read as closed for that long. None means the state couldn't be read.
    """
    cache: dict[str, Any] = {}
    try:
        loaded = json.loads(cache_file.read_text(encoding="utf-8"))
        cache = loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError):
        cache = {}  # a missing or damaged cache is an empty one
    hit = cache.get(ref)
    if isinstance(hit, dict) and time.time() - float(hit.get("at", 0)) < CACHE_SECONDS:
        return bool(hit.get("closed"))
    match = GH_REF.match(ref)
    if not match:
        return None
    command = ["gh", "api", f"repos/{match[1]}/issues/{match[2]}", "--jq", ".state"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or result.stdout.strip() not in {"open", "closed"}:
        return None
    cache[ref] = {"closed": result.stdout.strip() == "closed", "at": time.time()}
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    # Written whole and then renamed, so a second run never reads half a file.
    partial = cache_file.with_suffix(f".{os.getpid()}.tmp")
    partial.write_text(json.dumps(cache), encoding="utf-8")
    partial.replace(cache_file)
    return bool(cache[ref]["closed"])


def external_blocker(backlog: Backlog, ref: str, github: Callable[[str], bool | None]) -> str:
    """Return why an external blocker still blocks, or an empty string when it's closed.

    A blocker that can't be read counts as open.
    """
    if GH_REF.match(ref):
        closed = github(ref)
        if closed is True:
            return ""
        return f"{ref} ({'unreadable' if closed is None else 'open'})"
    task = backlog.tasks.get(local_id(backlog, ref))
    if task is None:
        return f"{ref} (unreadable)"
    return f"{ref}: {task.get('title')}" if task.open else ""


def local_id(backlog: Backlog, ref: str) -> str:
    """Return the loaded-task ID an external reference names, or the reference itself."""
    match = TASK_REF.match(ref)
    return str(match[2]).upper() if match and match[1] == backlog.home else ref


def blockers(backlog: Backlog, task: Task, github: Callable[[str], bool | None]) -> set[str]:
    """Record a task's open blockers on it; return the loaded tasks it waits on.

    A finished task has no blockers, so its external ones are never looked up.
    """
    waits_on: set[str] = set()
    if not task.open:
        return waits_on
    for dep in (d.upper() for d in task.items("dependencies")):
        other = backlog.tasks.get(dep)
        if other is None:
            task.blockers.append(f"{dep} (unknown)")
        elif other.open:
            task.blockers.append(f"{dep}: {other.get('title')}")
            waits_on.add(dep)
    for ref in task.items("external_blockers"):
        reason = external_blocker(backlog, ref, github)
        if reason:
            task.blockers.append(reason)
            if local_id(backlog, ref) in backlog.tasks:
                waits_on.add(local_id(backlog, ref))
    defer = task.get("defer_until")
    until = as_date(defer)
    # A date that can't be read defers the task: lint reports it, and nothing starts by mistake.
    if defer and (until is None or until > backlog.today):
        task.blockers.append(f"deferred until {defer}")
    return waits_on


def resolve(backlog: Backlog, github: Callable[[str], bool | None]) -> None:
    """Compute each task's open blockers, children and the tasks it unblocks.

    A parent waits on its open subtasks, so finishing a subtask counts towards what it unblocks,
    and a subtask that depends on its own parent shows up as a cycle.
    """
    waits_on: dict[str, set[str]] = {}
    for task in backlog.tasks.values():
        parent = task.get("parent_task_id").upper()
        if parent in backlog.tasks:
            backlog.tasks[parent].children.append(task.id)
        waits_on[task.id] = blockers(backlog, task, github)
    for task in backlog.tasks.values():
        if task.open:
            waits_on[task.id] |= {c for c in task.children if is_open(backlog, c)}
    for tid, task in backlog.tasks.items():
        if task.open:
            for blocker in transitive(tid, waits_on):
                backlog.tasks[blocker].unblocks.add(tid)


def transitive(start: str, edges: dict[str, set[str]]) -> set[str]:
    """Return every node reachable from `start`, without `start` itself unless it's in a cycle."""
    seen: set[str] = set()
    stack = list(edges.get(start, ()))
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(edges.get(node, ()))
    return seen


def check(backlog: Backlog) -> list[str]:
    """Return every lint finding: schema, links, cycles, granularity and callbacks."""
    problems = list(backlog.problems)
    for task in backlog.tasks.values():
        problems.extend(f"{task.id}: {p}" for p in task_problems(backlog, task))
    problems.extend(
        f"focus.yml: pin {p} isn't an open task" for p in backlog.pins if not is_open(backlog, p)
    )
    return problems


def is_open(backlog: Backlog, task_id: str) -> bool:
    """Whether `task_id` names a loaded task that still needs work."""
    task = backlog.tasks.get(task_id)
    return task is not None and task.open


def task_problems(backlog: Backlog, task: Task) -> Iterable[str]:
    """Yield the lint findings for one task."""
    kind = task.get("deadline_kind")
    named = task.draft or task.path.name.lower().startswith(task.id.lower() + " - ")
    bad_dates = [
        key
        for key in ("created_date", "due_date", "defer_until")
        if task.meta.get(key) is not None and as_date(task.meta[key]) is None
    ]
    rules = {
        f"status must be one of {backlog.statuses}": task.get("status") not in backlog.statuses,
        f"type must be one of {backlog.types}": (
            bool(backlog.types) and task.get("type") not in backlog.types
        ),
        "priority_set_by must be agent or human": (
            task.get("priority_set_by", "agent") not in PERFORMERS
        ),
        f"not a date (YYYY-MM-DD): {', '.join(bad_dates)}": bool(bad_dates),
        "a task file may not carry onStatusChange (it runs as a shell command)": (
            "onStatusChange" in task.meta
        ),
        f"file name {task.path.name!r} doesn't start with the id": not named,
        "no title": not task.get("title"),
        f"performer must be one of {PERFORMERS}": task.performer not in PERFORMERS,
        f"an agent task needs agent_tier, one of {TIERS}": (
            task.performer == "agent" and task.get("agent_tier") not in TIERS
        ),
        "a decision is the developer's: performer must be human": (
            task.get("type") == "decision" and task.performer != "human"
        ),
        f"effort must be one of {EFFORTS}": task.get("effort") not in EFFORTS,
        "priority must be high, medium or low": (
            task.get("priority") not in {"high", "medium", "low"}
        ),
        f"deadline_kind must be one of {DEADLINE_KINDS}": bool(kind) and kind not in DEADLINE_KINDS,
        "deadline_kind without due_date": bool(kind) and not task.get("due_date"),
        "an outbox draft has no id or dependencies; the receiving repo assigns them": (
            task.draft and bool(task.meta.get("id") or task.items("dependencies"))
        ),
        "a human task holds a checklist item marked [agent]; split it out": (
            task.performer == "human" and bool(AGENT_ITEM.search(task.body))
        ),
        "closed while a subtask is open": (
            not task.open and any(is_open(backlog, c) for c in task.children)
        ),
        "is in a dependency cycle": task.id in task.unblocks,
    }
    yield from (message for message, broken in rules.items() if broken)
    for ref in task.items("external_blockers"):
        if not (GH_REF.match(ref) or TASK_REF.match(ref) or DRAFT_REF.match(ref)):
            yield f"external blocker {ref!r} isn't gh:owner/repo#N, repo#ID or repo/slug"
    # An unreadable external blocker isn't a finding: it may be in a repo this run can't see.
    yield from (b for b in task.blockers if b.endswith("(unknown)"))


def ready(backlog: Backlog, task: Task) -> bool:
    """Whether a task can be started now: open, unblocked, and not a parent of open subtasks."""
    return task.open and not task.blockers and not any(is_open(backlog, c) for c in task.children)


def score(backlog: Backlog, task: Task) -> tuple[int, float, list[str]]:
    """Return a task's tier (lower first), its score, and the terms that made the score."""
    weights = backlog.weights
    terms: list[tuple[str, float]] = []
    priority = task.get("priority", "low")
    terms.append((f"priority {priority}", weights.get(f"priority_{priority}", 0.0)))
    waiting = task.unblocks
    if waiting:
        agents = sum(1 for t in waiting if backlog.tasks[t].performer == "agent")
        share = min(1.0, math.sqrt(len(waiting) / UNBLOCKS_CAP))
        terms.append(
            (f"unblocks {len(waiting)} ({agents} for agents)", weights["unblocks"] * share)
        )
    days_left: int | None = None
    due = as_date(task.meta.get("due_date"))
    if due:
        days_left = (due - backlog.today).days
        kind = task.get("deadline_kind", "soft")
        kind = kind if kind in DEADLINE_FACTOR else "soft"
        nearness = min(
            1.0,
            max(0.2, 1.0 - 0.8 * (days_left + IMMINENT_DAYS) / (DUE_HORIZON_DAYS + IMMINENT_DAYS)),
        )
        terms.append(
            (f"{kind} deadline in {days_left}d", weights["due"] * nearness * DEADLINE_FACTOR[kind])
        )
    if task.get("status") == ACTIVE:
        terms.append(("in progress", weights["active"]))
    if task.get("effort") in {"S", "M"}:
        terms.append((f"effort {task.get('effort')}", weights[f"effort_{task.get('effort')}"]))
    if task.get("waiting"):
        terms.append((f"{task.get('waiting')} is waiting", weights["waiting"]))
    created = as_date(task.meta.get("created_date"))
    if created:
        age = (backlog.today - created).days
        terms.append((f"age {age}d", weights["age"] * min(age / 365, 1.0)))
    tier = 2
    if task.id in backlog.pins:
        tier = 0
    elif (
        days_left is not None and days_left <= IMMINENT_DAYS and task.get("deadline_kind") == "hard"
    ):
        tier = 1
    total = sum(value for _, value in terms)
    shown = [f"{label} {value:.1f}" for label, value in terms if value]
    if tier == 0:
        shown.insert(0, f"pinned #{backlog.pins.index(task.id) + 1}")
    return tier, total, shown


def ranked(backlog: Backlog, tasks: Iterable[Task]) -> list[tuple[Task, float, list[str]]]:
    """Order tasks: pins in pin order, then imminent hard deadlines, then by score."""

    def key(task: Task) -> tuple[int, float, float, str]:
        tier, total, _ = score(backlog, task)
        pin = backlog.pins.index(task.id) if tier == 0 else 0
        return tier, pin, -total, task.id

    return [(t, score(backlog, t)[1], score(backlog, t)[2]) for t in sorted(tasks, key=key)]


def queue(backlog: Backlog, performer: str, repo: str = "") -> list[tuple[Task, float, list[str]]]:
    """Return the ranked ready tasks for one performer (`human`, `agent` or `all`)."""
    picked = (
        t
        for t in backlog.tasks.values()
        if ready(backlog, t) and performer in {"all", t.performer} and repo in {"", t.repo}
    )
    return ranked(backlog, picked)


def waits_for(backlog: Backlog, task: Task) -> str:
    """Return what keeps an open task from being ready, briefly, or an empty string."""
    reasons = [b.split(": ")[0] for b in task.blockers]
    if any(is_open(backlog, c) for c in task.children):
        reasons.append("its open subtasks")
    return "; ".join(reasons)


def cell(text: str) -> str:
    """Escape text for a Markdown table cell."""
    return text.replace("|", "\\|")


def link(task: Task, base: Path) -> str:
    """Return a Markdown link to a task file, relative to `base`."""
    target = quote(task.path.resolve().relative_to(base.resolve(), walk_up=True).as_posix())
    return f"[{task.id}]({target})"


def table(
    backlog: Backlog, rows: list[tuple[Task, float, list[str]]], base: Path, limit: int
) -> list[str]:
    """Render ranked tasks as a Markdown table, marking any that aren't ready."""
    lines = [
        "| # | Task | Title | Type | Effort | Tier | Why this rank |",
        "|---|---|---|---|---|---|---|",
    ]
    for number, (task, total, terms) in enumerate(rows[:limit], 1):
        cells = [
            str(number),
            link(task, base),
            cell(task.get("title")) + ("" if ready(backlog, task) else " (blocked)"),
            task.get("type"),
        ]
        cells += [
            task.get("effort"),
            task.get("agent_tier", "-"),
            f"**{total:.1f}** = " + " + ".join(terms),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    if len(rows) > limit:
        more = "`mise run tasks -- next --for human -n 0` (or `--for agent`)"
        lines.append(f"\n…and {len(rows) - limit} more: {more}.")
    return lines


def waiting_sections(
    backlog: Backlog, tasks: list[Task], home: list[Task], base: Path
) -> list[str]:
    """Render the board's Bottlenecks table and its list of blocked tasks."""
    out = ["", "## Bottlenecks", "", "Open tasks that the most other tasks wait on.", ""]
    out += ["| Task | Title | For | Ready? | Waiting on it |", "|---|---|---|---|---|"]
    for task in sorted(tasks, key=lambda t: (-len(t.unblocks), t.id))[:15]:
        if task.unblocks:
            state = "yes" if ready(backlog, task) else "no: " + cell(waits_for(backlog, task))
            cells = [link(task, base), cell(task.get("title")), task.performer, state]
            out.append("| " + " | ".join(cells) + f" | {len(task.unblocks)} |")
    out += ["", "## Blocked", ""]
    for task in sorted((t for t in home if not ready(backlog, t)), key=lambda t: t.id):
        reasons = list(task.blockers)
        if any(is_open(backlog, c) for c in task.children):
            reasons.append("its open subtasks")
        out.append(
            f"- {link(task, base)} ({task.performer}) {task.get('title')}: waits on "
            + "; ".join(reasons)
        )
    return out


# @spec TASK-CMD-017
def board(backlog: Backlog, root: Path, base: Path | None = None) -> str:
    """Render the whole backlog as one Markdown page.

    Args:
        backlog: The loaded, resolved backlog.
        root: The `backlog/` directory.
        base: The directory the page's links are relative to: where the tool was started.
    """
    base = base or root
    tasks = [t for t in backlog.tasks.values() if t.open]
    home = [t for t in tasks if not t.draft]
    out = [
        "# Task board",
        "",
        "Generated by `mise run tasks -- board`; don't edit. How to use it: backlog/README.md.",
        "",
    ]
    out += ["| | Ready | Blocked | Total open |", "|---|---|---|---|"]
    for who in PERFORMERS:
        mine = [t for t in home if t.performer == who]
        can = sum(1 for t in mine if ready(backlog, t))
        label = "developer" if who == "human" else "agents"
        out.append(f"| For the {label} | {can} | {len(mine) - can} | {len(mine)} |")
    out += [f"| For other repos (outbox) | | | {len(tasks) - len(home)} |", ""]
    pinned = [backlog.tasks[p] for p in backlog.pins if is_open(backlog, p)]
    out += [
        "## Focus",
        "",
        "The developer's pins, from backlog/focus.yml, in their order.",
        "",
    ]
    out += (
        table(backlog, ranked(backlog, pinned), base, 99)
        if pinned
        else ["Nothing pinned: the queues below are computed."]
    )
    sections = [
        (
            "For the developer: ready now",
            "Decisions and other work only a person can do, ranked by how much each unblocks.",
            "human",
            25,
        ),
        (
            "For agents: ready now",
            "Work a coding agent can finish; the tier is the weakest model class suited to it.",
            "agent",
            30,
        ),
    ]
    for heading, intro, who, limit in sections:
        out += ["", f"## {heading}", "", intro, ""]
        out += table(backlog, queue(backlog, who, backlog.home), base, limit)
    out += waiting_sections(backlog, tasks, home, base)
    for repo in sorted({t.repo for t in tasks if t.draft}):
        out += [
            "",
            f"## For {repo}",
            "",
            "Drafts to deliver to that repo, which assigns its own IDs and priority.",
            "",
        ]
        out += table(backlog, ranked(backlog, (t for t in tasks if t.repo == repo)), base, 99)
    out += ["", "## Everything open, by milestone", ""]
    titles = {}
    for path in root.glob("milestones/*.md"):
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        titles[str(meta.get("id"))] = str(meta.get("title"))
    for milestone in sorted({t.get("milestone", "none") for t in home}):
        out += [f"### {titles.get(milestone, milestone)}", ""]
        for task, _, _ in ranked(
            backlog, (t for t in home if t.get("milestone", "none") == milestone)
        ):
            mark = "" if ready(backlog, task) else " (blocked)"
            tags = f"`{task.performer}` `{task.get('priority')}`"
            out.append(f"- {link(task, base)} {tags} {task.get('title')}{mark}")
        out.append("")
    return "\n".join(out) + "\n"


def brief(backlog: Backlog) -> str:
    """Render the short text a session-start hook would show an agent."""
    lines = [
        f"Backlog ({backlog.home}): `mise run tasks -- next` lists more; `why <ID>` explains one."
    ]
    active = [t for t in backlog.tasks.values() if t.get("status") == ACTIVE]
    lines += [f"In progress: {t.id} {t.get('title')} ({t.performer})" for t in active]
    for label, who, count in (
        ("Ready for agents", "agent", 5),
        ("Waiting on the developer", "human", 3),
    ):
        rows = queue(backlog, who, backlog.home)
        lines.append(f"{label} ({len(rows)}):")
        lines += [
            f"  {t.id} [{t.get('agent_tier') or t.get('type')}, {t.get('effort')}] {t.get('title')}"
            for t, _, _ in rows[:count]
        ]
    return "\n".join(lines) + "\n"


def why(backlog: Backlog, task_id: str) -> str:
    """Explain one task's rank, blockers and what waits on it."""
    task = backlog.tasks.get(task_id) or backlog.tasks.get(task_id.upper())
    if task is None:
        return f"no task {task_id}\n"
    tier, total, terms = score(backlog, task)
    lines = [
        f"{task.id} {task.get('title')}",
        f"  for: {task.performer}  status: {task.get('status')}  repo: {task.repo}",
    ]
    lines.append(f"  rank tier {tier}, score {total:.1f} = " + " + ".join(terms))
    lines += [f"  waits on: {b}" for b in task.blockers]
    lines += [f"  unblocks: {t} {backlog.tasks[t].get('title')}" for t in sorted(task.unblocks)]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run the command line; returns the exit status."""
    parser = argparse.ArgumentParser(prog="tasks", description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("backlog"))
    parser.add_argument(
        "--offline", action="store_true", help="don't ask GitHub; gh: blockers count as open"
    )
    parser.add_argument(
        "--private", action="store_true", help="also load the gitignored drafts in private/outbox/"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="lint the backlog")
    listing = commands.add_parser("next", help="ranked ready tasks")
    listing.add_argument("--for", dest="performer", choices=[*PERFORMERS, "all"], default="all")
    listing.add_argument("-n", type=int, default=10, help="how many to show; 0 for all")
    listing.add_argument("--repo", default="", help="an outbox repo, or `all`; default this repo")
    commands.add_parser("why", help="explain one task's rank").add_argument("id")
    commands.add_parser("board", help="print the whole backlog as one Markdown page")
    commands.add_parser("brief", help="the session-start summary")
    commands.add_parser("help", help="show this help")
    args = parser.parse_args(argv)
    if args.command == "help":
        parser.print_help()
        return 0
    try:
        yaml_parser()
    except SetupError as error:
        sys.stderr.write(f"tasks: {error}\n")
        return 2

    backlog = load(args.root, private=args.private)
    cache = args.root / ".cache" / "github.json"
    resolve(
        backlog, (lambda _ref: None) if args.offline else (lambda ref: github_state(ref, cache))
    )
    problems = check(backlog)
    output = ""
    if args.command == "check":
        output = "".join(f"{p}\n" for p in problems) or f"{len(backlog.tasks)} tasks, no problems\n"
    elif args.command == "next":
        repo = "" if args.repo == "all" else args.repo or backlog.home
        for task, total, terms in queue(backlog, args.performer, repo)[: args.n or None]:
            who = task.get("agent_tier") if task.performer == "agent" else "human"
            output += (
                f"{task.id:<8} {total:5.1f}  [{who}, {task.get('effort')}] {task.get('title')}\n"
            )
            output += f"{'':16}{' + '.join(terms)}\n"
    elif args.command == "why":
        output = why(backlog, args.id)
    elif args.command == "board":
        output = board(backlog, args.root, Path.cwd())
    else:
        output = brief(backlog)
    sys.stdout.write(output)
    if problems and args.command != "check":
        sys.stderr.write(f"{len(problems)} problems: run `check`\n")
    return 1 if problems and args.command == "check" else 0


if __name__ == "__main__":
    sys.exit(main())
