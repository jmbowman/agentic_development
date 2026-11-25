#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "paper-search-mcp @ git+https://github.com/jmbowman/paper-search-mcp@155f360e802c8b9747ad881a030b3055a1f2a4da",
# ]
# ///
"""Send a batch of literature queries for the prior-art search skill, and record what came back.

Run it as `uv run --script harvest.py <action> --service <service> --round <n> --run-dir <dir>
<query>...`; `references/harvester.md` describes the arguments, output files and exit statuses.

The connectors come from a fork of paper-search-mcp. This script installs its own transport
adapter under them, which paces, checks, retries and logs every request, and it judges each
query's outcome from what that adapter saw, never from a connector's return value.
"""

# @spec PRIOR-SCR-001, PRIOR-SCR-010, PRIOR-SCR-092

from __future__ import annotations

import argparse
import contextlib
import email.utils
import fcntl
import json
import logging
import os
import random
import re
import secrets
import subprocess
import sys
import tempfile
import time
import tomllib
import traceback
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, cast
from urllib.parse import quote, quote_plus, urljoin, urlsplit
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from types import ModuleType

    import requests
    from requests.adapters import HTTPAdapter

    Arxiv406 = Callable[[requests.Response], bool]

if sys.version_info >= (3, 12):  # noqa: UP036 - this repo's target is 3.12, the script's 3.11
    from typing import override
else:  # Python 3.11, which the header allows, has no typing.override.
    from typing import TypeVar

    F = TypeVar("F")

    def override(method: F) -> F:  # noqa: UP047 - the PEP 695 form is a syntax error in 3.11
        """Mark a method as overriding one in a base class (a no-op before Python 3.12).

        Returns:
            The method.
        """
        return method


# Clock seams, so tests can run the waits on a fake clock, and the random source of Semantic
# Scholar's backoff jitter, so tests can fix it.
_sleep = time.sleep
_monotonic = time.monotonic
_wall = time.time
_uniform = random.uniform

USER_AGENT = "prior-art-search agent skill (+https://github.com/jmbowman/agentic_development)"
MAX_WAIT_SECONDS = 60.0  # longest wait for a limiter slot, and longest Retry-After honored
RATE_LIMIT_DEFAULT_WAIT = 15.0  # before the retry of a rate-limit response without Retry-After
TITLE_WIDTH = 100
MAX_BOOLEAN_OPERATORS = 5  # OpenAlex limits searches with more of them more tightly
RELATIONS_BUDGET = 60.0  # the most time the fork's citations and references lookups allow

ARXIV, OPENALEX, S2 = "arxiv", "openalex", "semanticscholar"
HOSTS = {"export.arxiv.org": ARXIV, "api.openalex.org": OPENALEX, "api.semanticscholar.org": S2}
ROUTES = {ARXIV: "arXiv", OPENALEX: "OpenAlex", S2: "Semantic Scholar"}
KEY_SETTINGS = {OPENALEX: "openalex.api_key", S2: "semanticscholar.api_key"}
KEY_HEADERS = {OPENALEX: "Authorization", S2: "x-api-key"}
# Results to fetch per query (default, maximum), and the services each action takes.
FETCH_DEPTH = {
    "search": (50, 100),
    "get": (1, 1),
    "citations": (100, 500),
    "references": (100, 500),
    "related": (20, 100),
    "recommend": (100, 500),
    "lookup": (1, 1),
}
ACTION_SERVICES = {
    "search": (ARXIV, OPENALEX),
    "get": (ARXIV, OPENALEX),
    "citations": (OPENALEX,),
    "references": (OPENALEX,),
    "related": (OPENALEX,),
    "recommend": (S2,),
    "lookup": (S2,),
}
# Actions whose first request names a paper by ID, so that a 404 there means the ID is unknown.
NOT_FOUND_ACTIONS = {"get", "citations", "references", "related", "recommend"}
# arXiv search sort orders, as the arXiv connector's `sort_by` takes them.
SORTS = {"relevance": "relevance", "submitted": "submittedDate"}

# OpenAlex single-work requests, which the harvester builds itself for `get` and `related`. The
# fields are those the connector's work parser reads, plus the open-access ones it reads only in
# part. OpenAlex doesn't charge a single-work request to the daily budget, so these two actions
# go on after a search has spent it.
SINGLE_WORK_ACTIONS = {"get", "related"}
WORK_SELECT = (
    "id,title,authorships,abstract_inverted_index,doi,primary_location,best_oa_location,"
    "open_access,publication_date,concepts,cited_by_count,referenced_works"
)
RELATED_SELECT = "id,related_works"
OPENALEX_TIMEOUT = 30
OPENALEX_REDIRECTS = 3  # merged-work redirects followed for one single-work request
# What a single-work response must hold to parse: a work, or a `related` query's seed.
WORK, SEED = "work", "seed"
FORK_VARIABLES = [
    "OPENALEX_API_KEY",
    "OPENALEX_EMAIL",
    "SEMANTIC_SCHOLAR_API_KEY",
    "RATE_LIMIT_DIR",
]
ATOM_FEED = "{http://www.w3.org/2005/Atom}feed"
RATE_LIMIT_PHRASES = ("rate limit", "too many requests", "quota")
BUDGET_PHRASES = ("budget", "plan upgrade")
REMAINING_HEADERS = ("x-ratelimit-remaining", "x-rate-limit-remaining")

# Semantic Scholar requests, which the harvester builds itself. The fields are those the
# connector's paper parser reads; Semantic Scholar otherwise returns little more than the title.
S2_API = "https://api.semanticscholar.org"
S2_FIELDS = (
    "paperId,title,abstract,url,publicationDate,externalIds,citationCount,authors,"
    "openAccessPdf,fieldsOfStudy"
)
S2_TIMEOUT = 30
S2_NO_MATCH = "Title match not found"
# The key under which each Semantic Scholar action's response lists its papers.
S2_LISTS = {"recommend": "recommendedPapers", "lookup": "data"}
# ASCII digits only: `\d` would also accept other scripts' digits.
DOI = r"10\.[0-9]{4,9}/\S+"
DOI_SEED = re.compile(rf"(?:(?i:doi:)|(?i:https?://(?:dx\.)?doi\.org/))?({DOI})")
ARXIV_SEED = re.compile(r"(?i:arxiv:)?([0-9]{4}\.[0-9]{4,5})(?:[vV][0-9]+)?")
S2_PAPER_SEED = re.compile(r"[0-9a-fA-F]{40}")

# Attempts per distinct request within a query, and Semantic Scholar's backoff between them:
# min(cap, base x growth^retries + jitter), with the jitter drawn from 0 to S2_JITTER.
ATTEMPTS = {ARXIV: 2, OPENALEX: 2, S2: 7}
S2_BACKOFF_BASE, S2_BACKOFF_GROWTH, S2_BACKOFF_CAP, S2_JITTER = 1.5, 1.6, 15.0, 0.75

# Kinds of response or failure the adapter records for a request.
USABLE, RATE, BUDGET, AUTH, NOT_FOUND, CLIENT, SERVER, PARSE, ARXIV_406, NETWORK = (
    "usable",
    "rate limit",
    "openalex budget",
    "authentication",
    "not found",
    "client error",
    "server error",
    "unparseable",
    "unusable arxiv 406",
    "network",
)
RETRYABLE = {RATE, SERVER, PARSE, ARXIV_406, NETWORK}
DAILY_BUDGET = "daily budget"
RAN = {"ok", "empty"}
# Outcomes that fault the query rather than the service, so they don't count for its route.
QUERY_FAULTS = {"invalid input", "client error", "not found"}
SETUP_ERROR, NOT_ALL_RAN = 4, 3


class UsageError(Exception):
    """The command line is invalid."""


class SetupError(Exception):
    """The harvester can't run: its settings file or its rate-limit directory is unusable."""


# Arguments ----------------------------------------------------------------------------------


class _Parser(argparse.ArgumentParser):
    @override
    def error(self, message: str) -> NoReturn:
        raise UsageError(message)


class _Once(argparse.Action):
    """Store an option's value, refusing a second occurrence."""

    @override
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: object,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, f"_seen_{self.dest}", False):
            parser.error(f"{option_string} given more than once")
        setattr(namespace, f"_seen_{self.dest}", True)
        setattr(namespace, self.dest, values)


def build_parser() -> argparse.ArgumentParser:
    """The harvester's command-line parser.

    Returns:
        The parser.
    """
    # No abbreviated options, and no -h: a query that happens to be "-h" must not exit 0.
    parser = _Parser(
        prog="harvest.py",
        description="Send literature queries through paced, logged connectors.",
        allow_abbrev=False,
        add_help=False,
    )
    parser.add_argument("--help", action="help", help="show this help and exit")
    parser.add_argument("action", choices=sorted(FETCH_DEPTH))
    parser.add_argument("--service", action=_Once, choices=sorted(ROUTES), required=True)
    parser.add_argument("--round", action=_Once, type=int, required=True)
    parser.add_argument("--run-dir", action=_Once, required=True)
    parser.add_argument(
        "--sort", action=_Once, choices=sorted(SORTS), help="order of an arXiv search's results"
    )
    parser.add_argument("--max-results", action=_Once, type=int, help="results to fetch per query")
    parser.add_argument("--show", action=_Once, type=int, default=10, help="results to print")
    parser.add_argument("queries", nargs="+", help="queries, paper IDs, seeds or titles")
    return parser


@dataclass
class Args:
    """A validated command line."""

    action: str
    service: str
    round: int
    run_dir: Path
    max_results: int
    show: int
    queries: list[str]
    sort: str = "relevance"


# @spec PRIOR-SCR-010, PRIOR-SCR-011
def parse_args(argv: list[str]) -> Args:
    """Parse and check the command line.

    Args:
        argv: The arguments.

    Returns:
        The checked arguments.

    Raises:
        UsageError: An argument is missing, repeated, empty or out of range.
    """
    ns = build_parser().parse_args(argv)
    services = ACTION_SERVICES[ns.action]
    if ns.service not in services:
        msg = f"{ns.action} needs --service {' or '.join(services)}"
        raise UsageError(msg)
    if ns.sort is not None and (ns.action, ns.service) != ("search", ARXIV):
        msg = "--sort is only for search with --service arxiv"
        raise UsageError(msg)
    default, maximum = FETCH_DEPTH[ns.action]
    depth = default if ns.max_results is None else ns.max_results
    if not 1 <= depth <= maximum:
        msg = f"--max-results must be from 1 to {maximum} for {ns.action}"
        raise UsageError(msg)
    if ns.round < 1 or ns.show < 0 or any(not q.strip() for q in ns.queries):
        msg = "--round must be 1 or more, --show 0 or more, and every query non-empty"
        raise UsageError(msg)
    if not ns.run_dir.strip():
        msg = "--run-dir must not be empty"
        raise UsageError(msg)
    run_dir = Path(ns.run_dir)
    sort = ns.sort or "relevance"
    return Args(ns.action, ns.service, ns.round, run_dir, depth, ns.show, ns.queries, sort)


# Settings and redaction ---------------------------------------------------------------------


def _git(*args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None


# @spec PRIOR-SCR-024, PRIOR-SCR-025, PRIOR-SCR-026, PRIOR-SCR-032
def read_settings() -> dict[str, str]:
    """Every non-blank value in the host repo's settings file, when git ignores the file.

    Returns:
        Each value, stripped, by its `section.key` name; none when there's no usable file.

    Raises:
        SetupError: The file is ignored but unreadable, malformed, or holds a key that isn't a
            string. The message names the file and the problem, never a value.
    """
    path = _ignored_settings_file()
    if path is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        msg = f"{path} can't be read ({exc.strerror})"
        raise SetupError(msg) from None
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        msg = f"{path} isn't valid TOML"
        raise SetupError(msg) from None
    return _values(path, data)


def _ignored_settings_file() -> Path | None:
    """The host repo's settings file, when it exists and git ignores it."""
    top = _git("rev-parse", "--show-toplevel")
    if top is None or top.returncode != 0:
        return None
    path = Path(top.stdout.strip()) / ".config" / "prior-art-sources.toml"
    if not path.exists():
        return None
    ignored = _git("check-ignore", "-q", str(path))
    return path if ignored is not None and ignored.returncode == 0 else None


def _values(path: Path, data: dict[str, Any]) -> dict[str, str]:
    """The non-blank string values of a parsed settings file, by `section.key`.

    Raises:
        SetupError: A key the harvester uses holds something other than a string.
    """
    values: dict[str, str] = {}
    for section, table in data.items():
        if not isinstance(table, dict):
            continue
        for key, value in table.items():
            name = f"{section}.{key}"
            if not isinstance(value, str):
                if name in KEY_SETTINGS.values():
                    msg = f"{path}: {name} isn't a string"
                    raise SetupError(msg)
                continue
            if any(ord(c) < 32 or ord(c) == 127 for c in value.strip()):  # noqa: PLR2004
                # A control character would reach logs escaped, where redaction can't find it.
                msg = f"{path}: {name} holds a control character"
                raise SetupError(msg)
            if value.strip():
                values[name] = value.strip()
    return values


def _encoded_forms(value: str) -> set[str]:
    """A value as written, and as URLs, JSON and Python reprs can encode it."""
    forms = {value, json.dumps(value)[1:-1], repr(value)[1:-1]}
    for encoded in (quote(value, safe=""), quote(value, safe="/:@"), quote_plus(value)):
        forms |= {encoded, re.sub(r"%[0-9A-F]{2}", lambda m: m[0].lower(), encoded)}
    return forms


class Redactor:
    """Replaces every settings value, in each form it can be encoded in, with its name."""

    def __init__(self, values: dict[str, str]) -> None:
        """Index the values, longest first, so a value inside another is never half-replaced.

        Args:
            values: Settings values by name.
        """
        pairs: dict[str, str] = {}
        for name, value in values.items():
            for form in _encoded_forms(value):
                pairs.setdefault(form, f"[redacted:{name}]")
        self.pairs = sorted(pairs.items(), key=lambda pair: len(pair[0]), reverse=True)

    def record(self, value: object) -> object:
        """Redact every string inside a JSON-ready value, leaving its structure intact.

        Args:
            value: A string, number, list or dict.

        Returns:
            The value with every string redacted.
        """
        if isinstance(value, str):
            return self(value)
        if isinstance(value, list):
            return [self.record(item) for item in value]
        if isinstance(value, dict):
            return {self(str(k)): self.record(v) for k, v in value.items()}
        return value

    # @spec PRIOR-SCR-030
    def __call__(self, text: str) -> str:
        """Redact a text.

        Args:
            text: The text.

        Returns:
            The text with every value replaced.
        """
        for value, label in self.pairs:
            text = text.replace(value, label)
        return text


# Environment --------------------------------------------------------------------------------


def _cache_home() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME", "")
    return Path(xdg) if xdg and Path(xdg).is_absolute() else Path.home() / ".cache"


# @spec PRIOR-SCR-020, PRIOR-SCR-021, PRIOR-SCR-022
def _prepare_environment() -> Path:
    """Clear the fork's own settings from the environment, then set the harvester's.

    No key goes into the environment: the OpenAlex key goes to its connector's constructor, and
    the harvester puts the Semantic Scholar key in the requests it builds.

    Returns:
        The shared rate-limit directory.
    """
    for name in FORK_VARIABLES:
        os.environ.pop(name, None)
        os.environ.pop(f"PAPER_SEARCH_MCP_{name}", None)
    limits = (_cache_home() / "prior-art-search" / "rate-limits").absolute()
    os.environ["PAPER_SEARCH_MCP_RATE_LIMIT_DIR"] = str(limits)
    missing = Path(tempfile.gettempdir()) / f"prior-art-search-no-env-{secrets.token_hex(8)}"
    os.environ["PAPER_SEARCH_MCP_ENV_FILE"] = str(missing)
    return limits


def _writable(directory: Path) -> str | None:
    """Why a directory can't hold the limiter store, or None when it can."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / f".probe-{secrets.token_hex(4)}"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return exc.strerror or type(exc).__name__
    return None


# @spec PRIOR-SCR-023, PRIOR-SCR-094
def _choose_limits(shared: Path, run_dir: Path) -> str | None:
    """Point the fork's limiter at the shared directory, or else at the run directory.

    A sandbox that allows writes only inside the host repo blocks the shared directory.

    Returns:
        A note for the summary when the limiter is in the run directory, else None.

    Raises:
        SetupError: Neither directory can hold the store.
    """
    if _writable(shared) is None:
        return None
    local = run_dir / "rate-limits"
    reason = _writable(local)
    if reason is not None:
        msg = f"neither {shared} nor {local} can hold the rate limits ({reason})"
        raise SetupError(msg)
    os.environ["PAPER_SEARCH_MCP_RATE_LIMIT_DIR"] = str(local)
    return (
        f"note: {shared} isn't writable, so pacing is shared only within this run "
        f"({local}), not with other runs on this machine"
    )


# Run directory ------------------------------------------------------------------------------


@contextlib.contextmanager
def _locked(path: Path, mode: str, *, shared: bool = False) -> Generator[Any]:
    """Open a file holding an exclusive `flock` on it, or a shared one for reading."""
    with path.open(mode, encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        try:
            yield handle
        finally:
            handle.flush()
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class RunDir:
    """The run directory's files, written under `flock` and redacted."""

    def __init__(self, root: Path, redact: Redactor) -> None:
        """Create the directory and its `raw/` subdirectory.

        Args:
            root: The run directory.
            redact: The redactor for everything written.

        Raises:
            SetupError: The directory can't be created.
        """
        self.root = root.absolute()
        self.redact = redact
        try:
            (self.root / "raw").mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            msg = f"{root} can't be used as the run directory ({exc.strerror})"
            raise SetupError(msg) from None

    # @spec PRIOR-SCR-081
    def append(self, name: str, text: str) -> None:
        """Append to a shared file under its lock.

        Args:
            name: The file's name.
            text: The text, without a final newline.
        """
        self._write_line(name, self.redact(text))

    def _write_line(self, name: str, line: str) -> None:
        with _locked(self.root / name, "a") as handle:
            handle.write(line + "\n")

    def append_json(self, name: str, record: dict[str, object]) -> None:
        """Append one JSON object as a line, redacting its strings before it is serialized.

        Args:
            name: The file's name.
            record: The object.
        """
        self._write_line(name, dumps(self.redact.record(record)))

    def state(self) -> State:
        """What `state.json` records for the run.

        Returns:
            The state; an empty one when there's no file yet.

        Raises:
            RuntimeError: `state.json` isn't the harvester's.
        """
        path = self.root / "state.json"
        if not path.exists():
            return State()
        with _locked(path, "r", shared=True) as handle:
            text = handle.read()
        return _state(text)

    # @spec PRIOR-SCR-072
    def reject(self, service: str) -> None:
        """Record that a service's key was rejected.

        Args:
            service: The service.
        """
        self._update_state(
            lambda state: state.rejected_keys.update({service: KEY_SETTINGS[service]})
        )

    # @spec PRIOR-SCR-118, PRIOR-SCR-131
    def spend_budget(self, *, single_work: bool) -> None:
        """Record that OpenAlex reported its daily budget spent; nothing ever removes the record.

        Args:
            single_work: Whether a single-work request got the report, which ends those too.
        """

        def spend(state: State) -> None:
            state.openalex_budget_spent = True
            state.openalex_single_work_budget_spent |= single_work

        self._update_state(spend)

    def _update_state(self, change: Callable[[State], object]) -> None:
        """Rewrite `state.json` under its lock, keeping every record but the one changed."""
        with _locked(self.root / "state.json", "a+") as handle:
            handle.seek(0)
            state = _state(handle.read())
            change(state)
            handle.seek(0)
            handle.truncate()
            handle.write(json.dumps(vars(state), indent=2) + "\n")

    # @spec PRIOR-SCR-084
    def save_raw(self, stem: str, content_type: str, body: bytes) -> None:
        """Save one response body.

        Args:
            stem: The file name without its extension.
            content_type: The response's content type.
            body: The body.
        """
        kind = content_type.lower()
        extension = "json" if "json" in kind else "xml" if "xml" in kind else "txt"
        text = self.redact(body.decode("utf-8", errors="replace"))
        (self.root / "raw" / f"{stem}.{extension}").write_text(text, encoding="utf-8")


def dumps(record: object) -> str:
    """One JSON line, as every output file and the printed ledger write it.

    Args:
        record: The object.

    Returns:
        The JSON text.
    """
    return json.dumps(record, ensure_ascii=False, default=str)


@dataclass
class State:
    """The run directory's `state.json`: rejected keys, and whether OpenAlex's budget is spent.

    The budget is recorded twice: as spent, which stops searches, citations and references, and
    as spent for single-work requests too, which stops every OpenAlex request.
    """

    rejected_keys: dict[str, str] = field(default_factory=dict)
    openalex_budget_spent: bool = False
    openalex_single_work_budget_spent: bool = False


# @spec PRIOR-SCR-079
def _state(text: str) -> State:
    """The state in `state.json`'s text.

    Raises:
        RuntimeError: The text isn't a state file the harvester wrote.
    """
    try:
        data = json.loads(text or "{}")
    except ValueError:
        data = None
    rejected = data.get("rejected_keys", {}) if isinstance(data, dict) else None
    spent = data.get("openalex_budget_spent", False) if isinstance(data, dict) else None
    single = (
        data.get("openalex_single_work_budget_spent", False) if isinstance(data, dict) else None
    )
    flags_ok = isinstance(spent, bool) and isinstance(single, bool)
    if not isinstance(rejected, dict) or not flags_ok:
        msg = "state.json in the run directory isn't one the harvester wrote"
        raise RuntimeError(msg)  # a corrupt file, not a caller's type error
    keys = {str(service): str(setting) for service, setting in rejected.items()}
    return State(keys, bool(spent), bool(single))


class _LogHandler(logging.Handler):
    """Writes the connectors' log lines to `harvest.log`, redacted, and nowhere else."""

    def __init__(self, run: RunDir) -> None:
        super().__init__(logging.INFO)
        self.run = run

    @override
    def emit(self, record: logging.LogRecord) -> None:
        with contextlib.suppress(Exception):
            self.run.append(
                "harvest.log", f"{record.levelname} {record.name}: {self.format(record)}"
            )


# Transport ----------------------------------------------------------------------------------


def _retry_after(response: requests.Response) -> float | None:
    """Seconds from now that a response's Retry-After asks for, or None when absent or bad."""
    value = (response.headers.get("Retry-After") or "").strip()
    if not value:
        return None
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    return max(0.0, when.timestamp() - _wall())


# @spec PRIOR-SCR-060
def _is_rate_limit(response: requests.Response, service: str | None) -> bool:
    status = response.status_code
    if status in {429, 503}:
        return True
    body = response.content or b""
    if service == ARXIV and status == 200:  # noqa: PLR2004
        return body.lstrip().lower().startswith(b"rate exceeded")
    if status != 403:  # noqa: PLR2004
        return False
    headers = {k.lower(): v.strip() for k, v in response.headers.items()}
    if "retry-after" in headers or any(headers.get(h) == "0" for h in REMAINING_HEADERS):
        return True
    text = body.decode("utf-8", errors="replace").lower()
    return any(phrase in text for phrase in RATE_LIMIT_PHRASES)


@dataclass(frozen=True)
class Expect:
    """What one request's response must hold to be usable, beyond the rules for every request.

    Attributes:
        title_match: Whether it answers a `lookup`, whose no-match 404 is usable.
        listed: For a `recommend` or `lookup`, the key under which a 2xx body must hold its
            list of papers to parse.
        work: For a single-work request, what a 2xx body must hold to parse: `WORK` for a work
            ID, `SEED` for that and a list of related works.
        gone_ok: Whether it answers a `related` query's request for a listed work, whose 404 is
            usable: the work is left out.
    """

    title_match: bool = False
    listed: str | None = None
    work: str | None = None
    gone_ok: bool = False


def _parses(response: requests.Response, service: str | None, expect: Expect) -> bool:
    try:
        if service == ARXIV:
            return ET.fromstring(response.content).tag == ATOM_FEED  # noqa: S314
        body = json.loads(response.content)
    except (ET.ParseError, ValueError):
        return False
    if expect.work is not None:
        if not isinstance(body, dict) or not isinstance(body.get("id"), str) or not body["id"]:
            return False
        return expect.work != SEED or isinstance(body.get("related_works"), list)
    listed = expect.listed
    return listed is None or (isinstance(body, dict) and isinstance(body.get(listed), list))


def _is_budget(response: requests.Response, service: str | None) -> bool:
    """Whether a response is OpenAlex's report of a spent daily budget."""
    if service != OPENALEX or response.status_code != 429:  # noqa: PLR2004
        return False
    text = (response.content or b"").decode("utf-8", errors="replace").lower()
    return any(phrase in text for phrase in BUDGET_PHRASES)


def _is_no_title_match(response: requests.Response) -> bool:
    """Whether a 404 is Semantic Scholar's answer that no paper matches a title."""
    try:
        body = json.loads(response.content)
    except ValueError:
        return False
    return isinstance(body, dict) and bool(body.get("error") == S2_NO_MATCH)


# @spec PRIOR-SCR-060, PRIOR-SCR-061, PRIOR-SCR-062, PRIOR-SCR-117
def classify(
    response: requests.Response,
    service: str | None,
    arxiv_406: Arxiv406,
    expect: Expect,
) -> str:
    """The kind of a response, for retries and outcomes.

    Args:
        response: The response.
        service: The service it came from.
        arxiv_406: The arXiv connector's own check of a 406 feed.
        expect: What this request's response must hold to be usable.

    Returns:
        One of the response kinds.
    """
    status = response.status_code
    if _is_rate_limit(response, service):
        return BUDGET if _is_budget(response, service) else RATE
    if 200 <= status < 400:  # noqa: PLR2004
        parses = _parses(response, service, expect)
        return USABLE if status >= 300 or parses else PARSE  # noqa: PLR2004
    if service == ARXIV and status == 406:  # noqa: PLR2004
        return USABLE if arxiv_406(response) else ARXIV_406
    if status in {401, 403}:
        return AUTH
    if status == 404:  # noqa: PLR2004
        no_match = expect.title_match and _is_no_title_match(response)
        return USABLE if expect.gone_ok or no_match else NOT_FOUND
    return CLIENT if status < 500 else SERVER  # noqa: PLR2004


@dataclass
class Attempt:
    """One attempt at a request, as the query log records it."""

    time: str
    url: str
    status: int | None = None
    error: str | None = None
    wait: float = 0.0
    refused: str | None = None
    from_memory: bool = False


@dataclass
class RequestLog:
    """What the adapter has seen of one distinct request (its method and URL) in a query."""

    number: int
    service: str | None = None
    sends: int = 0
    kind: str | None = None
    retry_after: float | None = None
    failed_at: float = 0.0  # when the last failure arrived
    first_arrival: float | None = None  # when the first response or failure arrived
    delay: float = 0.0  # how long after the last failure the retry must wait
    withheld: bool = False  # a retry was withheld, so the last failure stands
    refusal: str | None = None
    limiter: bool = False
    memory: tuple[int, dict[str, str], bytes, str] | None = None

    @property
    def retry_allowed(self) -> bool:
        """Whether the last failure allows another send, before any time limit."""
        too_long = self.retry_after is not None and self.retry_after > MAX_WAIT_SECONDS
        attempts = ATTEMPTS.get(self.service or "", 1)
        return (
            1 <= self.sends < attempts
            and self.kind in RETRYABLE
            and not too_long
            and not self.withheld
        )

    @property
    def may_retry(self) -> bool:
        """Whether one more send is allowed after the last failed."""
        if not self.retry_allowed:
            return False
        if self.service == S2:
            return self.failed_at + self.delay - (self.first_arrival or 0.0) <= MAX_WAIT_SECONDS
        return True

    # @spec PRIOR-SCR-052, PRIOR-SCR-053, PRIOR-SCR-111
    def plan_retry(self) -> None:
        """Set how long after this failure the retry must wait.

        On Semantic Scholar, the backoff's jitter is drawn only for a retry the failure allows.
        """
        if self.service != S2:
            if self.retry_after is not None:
                self.delay = self.retry_after
            else:
                self.delay = RATE_LIMIT_DEFAULT_WAIT if self.kind == RATE else 0.0
            return
        if not self.retry_allowed:
            self.delay = 0.0
            return
        growth = S2_BACKOFF_GROWTH ** (self.sends - 1)
        backoff = min(S2_BACKOFF_CAP, S2_BACKOFF_BASE * growth + _uniform(0, S2_JITTER))
        self.delay = max(backoff, self.retry_after or 0.0)


@dataclass
class QueryState:
    """The requests and attempts of one query, kept across the connector calls for it."""

    qid: str
    requests: dict[tuple[str, str], RequestLog] = field(default_factory=dict)
    attempts: list[Attempt] = field(default_factory=list)

    def log(self, key: tuple[str, str]) -> RequestLog:
        """The log of one request, created on first sight.

        Args:
            key: The request's method and URL.

        Returns:
            Its log.
        """
        if key not in self.requests:
            service = HOSTS.get((urlsplit(key[1]).hostname or "").lower())
            self.requests[key] = RequestLog(len(self.requests) + 1, service)
        return self.requests[key]


class Transport:
    """The checks, pacing, retries and records around every connector request."""

    def __init__(
        self,
        fork: ModuleType,
        run: RunDir,
        keys: dict[str, str],
        arxiv_406: Arxiv406,
        *,
        action: str,
    ) -> None:
        """Remember what the adapter needs.

        Args:
            fork: The fork's `http_limits` module.
            run: The run directory.
            keys: The API key values by service.
            arxiv_406: The arXiv connector's own check of a 406 feed.
            action: The invocation's action. A `lookup`'s no-match 404 is usable, a
                `recommend` or `lookup` body parses only with its list of papers, and a `get`
                or `related` invocation's OpenAlex requests are single-work requests.
        """
        self.fork = fork
        self.run = run
        self.keys = keys
        self.arxiv_406 = arxiv_406
        self.action = action
        self.expected: Expect | None = None  # set around each single-work request
        self.title_match = action == "lookup"
        self.listed = S2_LISTS.get(action)
        self.query: QueryState | None = None
        self.sends = 0
        self.internal: tuple[Exception, str] | None = None

    # @spec PRIOR-SCR-075
    def send(
        self,
        adapter: HTTPAdapter,
        request: requests.PreparedRequest,
        kwargs: dict[str, Any],
    ) -> requests.Response:
        """Send one request, keeping the harvester's own errors from the connector.

        Connectors catch broad exceptions, so an error of the harvester's own raised in here
        would pass as a network failure. It is stored for `Harvester.run_query` to re-raise, and
        the connector sees an ordinary request failure.

        Args:
            adapter: The adapter the request came through.
            request: The request.
            kwargs: The adapter's send arguments.

        Returns:
            The response.

        Raises:
            requests.RequestException: The request failed, was refused or withheld, or the
                harvester itself failed while handling it.
        """
        import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

        try:
            return self._checked_send(adapter, request, kwargs)
        except requests.RequestException:
            raise
        except Exception as exc:
            if self.internal is None:
                self.internal = (exc, traceback.format_exc())
            msg = "the harvester failed while handling this request"
            raise requests.RequestException(msg) from exc

    def _refusal(self, request: requests.PreparedRequest, kwargs: dict[str, Any]) -> str | None:
        parts = urlsplit(request.url or "")
        service = HOSTS.get((parts.hostname or "").lower())
        if parts.scheme != "https" or parts.port is not None or service is None:
            return "host"
        if not kwargs.get("verify", True):  # requests turns verification off for any false value
            return "tls"
        state = self.run.state()
        if service in state.rejected_keys:
            return "key rejected"
        # @spec PRIOR-SCR-118, PRIOR-SCR-131
        exempt = self.action in SINGLE_WORK_ACTIONS and not state.openalex_single_work_budget_spent
        if service == OPENALEX and state.openalex_budget_spent and not exempt:
            return DAILY_BUDGET
        key = self.keys.get(service)
        if key is not None:
            expected = f"Bearer {key}" if service == OPENALEX else key
            if request.headers.get(KEY_HEADERS[service]) != expected:
                return "missing key"
        return None

    # @spec PRIOR-SCR-040, PRIOR-SCR-044, PRIOR-SCR-045, PRIOR-SCR-046, PRIOR-SCR-047
    # @spec PRIOR-SCR-048, PRIOR-SCR-049, PRIOR-SCR-050, PRIOR-SCR-051, PRIOR-SCR-052
    # @spec PRIOR-SCR-053, PRIOR-SCR-054, PRIOR-SCR-111, PRIOR-SCR-118
    def _checked_send(
        self,
        adapter: HTTPAdapter,
        request: requests.PreparedRequest,
        kwargs: dict[str, Any],
    ) -> requests.Response:
        """Check, pace, send and record one request.

        Args:
            adapter: The adapter the request came through.
            request: The request.
            kwargs: The adapter's send arguments.

        Returns:
            The response, live or from memory.

        Raises:
            requests.RequestException: The request was refused or withheld, or failed to send.
        """
        import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

        query = self.query or QueryState("none")
        host = (urlsplit(request.url or "").hostname or "").lower()
        if host != "api.openalex.org":
            request.headers.pop("Authorization", None)
        if host != "api.semanticscholar.org":
            request.headers.pop("x-api-key", None)
        request.headers["User-Agent"] = USER_AGENT
        log = query.log((request.method or "GET", request.url or ""))
        attempt = Attempt(datetime.fromtimestamp(_wall(), UTC).isoformat(), request.url or "")
        query.attempts.append(attempt)
        reason = self._refusal(request, kwargs)
        if reason is not None:
            attempt.refused = reason
            if log.sends == 0:
                log.refusal = reason
            msg = f"refused: {reason}"
            raise requests.RequestException(msg)
        if log.memory is not None:
            attempt.from_memory = True
            return _replay(request, log.memory)
        if log.sends >= 1 and not log.may_retry:
            attempt.refused = "retry not allowed"
            msg = "retry not allowed"
            raise requests.RequestException(msg)
        if log.sends >= 1:
            # The wait runs before the limiter's slot is asked for, so the two overlap.
            attempt.wait = max(0.0, log.failed_at + log.delay - _monotonic())
            _sleep(attempt.wait)
        return self._send(adapter, request, kwargs, query, log, attempt)

    # @spec PRIOR-SCR-041, PRIOR-SCR-112
    def _pace(
        self, adapter: HTTPAdapter, request: requests.PreparedRequest, log: RequestLog
    ) -> None:
        """Wait for the limiter's slot, then withhold a Semantic Scholar retry that is too late.

        Raises:
            RateLimited: The slot is further away than the adapter's `max_wait`.
            requests.RequestException: The retry would go more than 60 seconds after the
                request's first response arrived.
        """
        import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

        limit = cast("Any", adapter).limit_for(request.url or "")
        if limit is not None:
            credentialed = self.fork._carries_credential(limit, request)  # noqa: SLF001
            self.fork.acquire(limit, cast("Any", adapter).max_wait, credentialed)
        late = log.first_arrival is not None and _monotonic() - log.first_arrival > MAX_WAIT_SECONDS
        if log.service == S2 and log.sends >= 1 and late:
            log.withheld = True
            msg = "retry not allowed: more than 60 seconds after the first response"
            raise requests.RequestException(msg)

    def _send(  # noqa: PLR0913, PLR0917
        self,
        adapter: HTTPAdapter,
        request: requests.PreparedRequest,
        kwargs: dict[str, Any],
        query: QueryState,
        log: RequestLog,
        attempt: Attempt,
    ) -> requests.Response:
        import requests.adapters  # noqa: PLC0415 - imported with the fork, after the environment

        try:
            self._pace(adapter, request, log)
        except self.fork.RateLimited:
            attempt.error = "RateLimited"
            if log.sends == 0:
                log.limiter = True
            else:
                log.withheld = True  # the failed response decides the outcome
            raise
        except requests.RequestException:
            attempt.refused = "retry not allowed"
            raise
        try:
            response = requests.adapters.HTTPAdapter.send(adapter, request, **kwargs)
        except requests.RequestException as exc:
            self.sends += 1
            log.sends += 1
            log.kind, log.retry_after = NETWORK, None
            attempt.error = type(exc).__name__
            self._failed(log)
            raise
        self.sends += 1
        log.sends += 1
        body = response.content or b""
        attempt.status = response.status_code
        content_type = response.headers.get("Content-Type", "")
        self.run.save_raw(f"{query.qid}-{log.number}-{log.sends}", content_type, body)
        service = log.service
        log.kind = classify(response, service, self.arxiv_406, self._expect())
        if log.kind == USABLE:
            headers = dict(response.headers)
            log.memory = (response.status_code, headers, body, response.url or "")
        else:
            log.retry_after = _retry_after(response)
            self._failed(log)
        key_header = KEY_HEADERS.get(service or "")
        carried = key_header is not None and request.headers.get(key_header) is not None
        if log.kind == AUTH and service in self.keys and carried:
            self.run.reject(service or "")
        if log.kind == BUDGET:
            self.run.spend_budget(single_work=self.action in SINGLE_WORK_ACTIONS)
        return response

    # @spec PRIOR-SCR-062
    def _expect(self) -> Expect:
        """What the current request's response must hold to be usable.

        A single-work request's sender says so in `expected` before it sends; any other request
        is judged by the invocation's action.
        """
        if self.expected is not None:
            return self.expected
        return Expect(title_match=self.title_match, listed=self.listed)

    @staticmethod
    def _failed(log: RequestLog) -> None:
        """Note when a failure arrived, and plan the retry it allows."""
        log.failed_at = _monotonic()
        if log.first_arrival is None:
            log.first_arrival = log.failed_at
        log.plan_retry()


class _NoSleep:
    """The `time` module, as a connector sees it, with `sleep` doing nothing."""

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401 - whatever `time` holds
        return getattr(time, name)

    @staticmethod
    def sleep(_seconds: float) -> None:
        """Return at once; the adapter waits before each resend instead."""


def _replay(
    request: requests.PreparedRequest, memory: tuple[int, dict[str, str], bytes, str]
) -> requests.Response:
    import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

    status, headers, body, url = memory
    response = requests.Response()
    response.status_code = status
    response.headers.update(headers)
    response._content = body  # noqa: SLF001
    response._content_consumed = True  # noqa: SLF001
    response.url = url
    response.request = request
    response.encoding = response.encoding or "utf-8"
    return response


# Connectors and records ---------------------------------------------------------------------


@dataclass
class Connectors:
    """The fork's modules and the searchers for this invocation's service."""

    http_limits: ModuleType
    relations: ModuleType
    request_errors: tuple[type[BaseException], ...]
    s2_error: type[Exception]
    searcher: Any = None
    s2_key: str | None = None
    arxiv_id: re.Pattern[str] | None = None  # the arXiv connector's own paper-ID pattern
    feedparser: Any = None  # the feed parser the arXiv connector uses
    transport: Any = None  # the harvester's transport, told what a single-work request expects


def _year(value: object) -> int | None:
    if isinstance(value, datetime):
        return value.year
    if isinstance(value, str) and re.match(r"\d{4}", value):
        return int(value[:4])
    return None


def _arxiv_id(service: str, paper_id: str, doi: str) -> str | None:
    if service == ARXIV:
        return paper_id
    match = re.search(r"10\.48550/arxiv\.(.+)", doi or "", re.IGNORECASE)
    return str(match[1]) if match else None


def _record(service: str, paper: Any) -> dict[str, object]:  # noqa: ANN401 - a Paper or its dict
    data = paper if isinstance(paper, dict) else vars(paper)
    authors = data.get("authors") or []
    if isinstance(authors, str):
        authors = [a for a in authors.split("; ") if a]
    extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
    paper_id = str(data.get("paper_id") or "")
    doi = str(data.get("doi") or "")
    return {
        "title": data.get("title") or "",
        "authors": authors,
        "year": _year(data.get("published_date")),
        "venue": (extra or {}).get("venue") or None,
        "doi": doi or None,
        "arxiv_id": _arxiv_id(service, paper_id, doi),
        "service_id": paper_id,
        "abstract": data.get("abstract") or "",
        # arXiv reports no citation counts; the connector's 0 would read as "never cited".
        "citations": None if service == ARXIV else data.get("citations"),
        "url": data.get("url") or None,
        "pdf_url": data.get("pdf_url") or None,
    }


# @spec PRIOR-SCR-114, PRIOR-SCR-115
def s2_seed(seed: str) -> str | None:
    """A `recommend` seed as Semantic Scholar's paper ID, before percent-encoding.

    Args:
        seed: The seed as given.

    Returns:
        `DOI:<doi>`, `arXiv:<id>` or a lower-case paper ID, or None for any other form.
    """
    seed = seed.strip()
    if match := DOI_SEED.fullmatch(seed):
        # A `.` or `..` segment would be resolved away when the URL is prepared, sending the
        # request to another endpoint's path. A DOI URL's query string or fragment isn't part
        # of the DOI, and the citations lookup refuses it too.
        if {".", ".."} & set(match[1].split("/")):
            return None
        if "://" in seed and any(mark in match[1] for mark in "?#"):
            return None
        return f"DOI:{match[1]}"
    if match := ARXIV_SEED.fullmatch(seed):
        return f"arXiv:{match[1]}"
    if S2_PAPER_SEED.fullmatch(seed):
        return seed.lower()
    return None


# @spec PRIOR-SCR-028, PRIOR-SCR-113, PRIOR-SCR-114, PRIOR-SCR-116, PRIOR-SCR-122
# @spec PRIOR-SCR-083
def _s2_fetch(connectors: Connectors, args: Args, query: str) -> list[dict[str, object]]:
    """Send one `recommend` or `lookup` request, and make harvest records of its papers.

    The connector has no method for either, so the harvester sends the request through the
    connector's session, which carries its adapter, and parses each paper with the connector's
    own parser. A retry is another call, which the adapter times like a connector's resend.

    Returns:
        The records; none when the response isn't a usable 200, whose outcome the adapter's
        record decides.

    Raises:
        SemanticScholarRequestError: A usable response holds no list of papers.
    """
    searcher = connectors.searcher
    if args.action == "recommend":
        seed = quote(s2_seed(query) or "", safe=":/")
        url = f"{S2_API}/recommendations/v1/papers/forpaper/{seed}"
        params = {"from": "all-cs", "limit": str(args.max_results), "fields": S2_FIELDS}
    else:
        url = f"{S2_API}/graph/v1/paper/search/match"
        params = {"query": query.strip(), "fields": S2_FIELDS}
    listed = S2_LISTS[args.action]
    headers = {} if connectors.s2_key is None else {"x-api-key": connectors.s2_key}
    response = searcher.session.get(url, params=params, headers=headers, timeout=S2_TIMEOUT)
    if response.status_code != 200:  # noqa: PLR2004 - a lookup's no-match 404 included
        return []
    body = response.json()
    items = body.get(listed) if isinstance(body, dict) else None
    if not isinstance(items, list):
        msg = f"Semantic Scholar's response has no {listed} list"
        raise connectors.s2_error(msg)
    records = []
    for item in items[: args.max_results]:
        paper = searcher._parse_paper(item) if isinstance(item, dict) else None  # noqa: SLF001
        if paper is None:
            continue
        record = _record(S2, paper)
        if args.action == "lookup":
            record["match_score"] = item.get("matchScore")
        records.append(record)
    return records


# @spec PRIOR-SCR-123, PRIOR-SCR-124
def arxiv_get_id(connectors: Connectors, given: str) -> str | None:
    """An arXiv `get` ID as `id_list` takes it.

    Args:
        connectors: The connectors.
        given: The ID as given.

    Returns:
        The ID without surrounding whitespace or an `arXiv:` prefix, or None when the arXiv
        connector's own paper-ID pattern doesn't match it.
    """
    value = re.sub(r"^arxiv:", "", given.strip(), flags=re.IGNORECASE)
    pattern = connectors.arxiv_id
    return value if pattern is not None and pattern.fullmatch(value) else None


# @spec PRIOR-SCR-113, PRIOR-SCR-123
def _arxiv_get(connectors: Connectors, query: str) -> list[dict[str, object]]:
    """Send one arXiv `get` request, and make a harvest record of the paper it returns.

    The connector has no method for a paper by ID, so the harvester sends the request through
    the connector's own request routine and parses the entry with the connector's own parser.

    Returns:
        The paper's record; none when arXiv's feed has no entry, or the response isn't usable.

    Raises:
        requests.RequestException: The feed's entry isn't a paper the connector can parse.
    """
    import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

    searcher = connectors.searcher
    params = {"id_list": arxiv_get_id(connectors, query) or "", "max_results": 1}
    response = searcher._request_with_retries(params)  # noqa: SLF001
    if response is None or response.status_code not in {200, 406}:
        return []
    entries = connectors.feedparser.parse(response.content).entries[:1]
    try:
        return [_record(ARXIV, searcher._paper_from_entry(entry)) for entry in entries]  # noqa: SLF001
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        msg = "arXiv's feed entry isn't a paper"
        raise requests.RequestException(msg) from exc


def _open_access(work: dict[str, Any]) -> dict[str, object]:
    """The open-access fields a `get` or `related` record adds, null where OpenAlex gives none."""
    access = work.get("open_access")
    access = access if isinstance(access, dict) else {}
    best = work.get("best_oa_location")
    best = best if isinstance(best, dict) else {}
    return {
        "is_oa": access.get("is_oa"),
        "oa_status": access.get("oa_status"),
        "oa_url": access.get("oa_url"),
        "oa_license": best.get("license"),
    }


# @spec PRIOR-SCR-113, PRIOR-SCR-125
def _openalex_work(
    connectors: Connectors, identifier: str, select: str, expect: Expect
) -> tuple[int, dict[str, Any] | None]:
    """Send one single-work request through the OpenAlex connector's session.

    The session carries the harvester's adapter and, when the key is set, its `Authorization`
    header. A retry is another call, which the adapter times like a connector's resend.

    OpenAlex redirects a merged work's ID to the work that replaced it. The harvester follows
    such a redirect itself, only to another work on the same host, so that the next request
    keeps its `select` and the adapter judges it by the same expectation.

    Args:
        connectors: The connectors.
        identifier: The work's DOI or work ID.
        select: The fields to ask for.
        expect: What the adapter requires of the response, redirect hops included.

    Returns:
        The response's status, and its body when that is a work: a JSON object with an ID, as
        the adapter requires of a usable response.

    Raises:
        requests.RequestException: A redirect leads anywhere but another OpenAlex work, or
            there are too many of them.
    """
    import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

    searcher = connectors.searcher
    normalized = connectors.relations.normalize_identifier(identifier)
    url = f"{searcher.BASE_URL}/{quote(normalized, safe=':')}"
    connectors.transport.expected = expect
    try:
        for _hop in range(OPENALEX_REDIRECTS + 1):
            response = searcher.session.get(
                url, params={"select": select}, timeout=OPENALEX_TIMEOUT, allow_redirects=False
            )
            if response.status_code not in {301, 302, 307, 308}:
                break
            target = urlsplit(urljoin(url, response.headers.get("Location", "")))
            on_host = (target.scheme, target.netloc) == ("https", "api.openalex.org")
            if not on_host or not re.fullmatch(r"/works/W[0-9]+", target.path):
                msg = "OpenAlex returned a redirect to something other than a work"
                raise requests.RequestException(msg)
            url = f"https://{target.netloc}{target.path}"
        else:
            msg = "OpenAlex returned too many redirects"
            raise requests.RequestException(msg)
    finally:
        connectors.transport.expected = None
    try:
        body = response.json()
    except ValueError:
        body = None
    is_work = isinstance(body, dict) and isinstance(body.get("id"), str) and bool(body["id"])
    return response.status_code, body if is_work else None


# @spec PRIOR-SCR-132
def _work_record(connectors: Connectors, work: dict[str, Any]) -> dict[str, object] | None:
    """A harvest record of one OpenAlex work, with its open-access fields.

    Returns:
        The record, or None for a work the connector's parser returns no paper for (one
        without a title).

    Raises:
        requests.RequestException: The connector's parser can't read the work.
    """
    import requests  # noqa: PLC0415 - imported with the fork, after the environment is set

    try:
        paper = connectors.searcher._parse_work(work)  # noqa: SLF001
    except (AttributeError, KeyError, TypeError, ValueError) as exc:  # @spec PRIOR-SCR-076
        msg = "OpenAlex's work isn't a paper the connector can parse"
        raise requests.RequestException(msg) from exc
    return None if paper is None else _record(OPENALEX, paper) | _open_access(work)


def _listed_work_id(connectors: Connectors, entry: object) -> str | None:
    """The work ID of one `related_works` entry, or None when it isn't one."""
    if not isinstance(entry, str):
        return None
    try:
        work_id = str(connectors.relations.normalize_identifier(entry))
    except ValueError:
        return None
    return work_id if re.fullmatch(r"W[0-9]+", work_id) else None


# @spec PRIOR-SCR-126, PRIOR-SCR-127, PRIOR-SCR-128, PRIOR-SCR-135
def _related_fetch(
    connectors: Connectors, args: Args, query: str
) -> tuple[list[dict[str, object]], str | None]:
    """Fetch a paper's related works: its list, then each of the first listed works.

    Returns:
        The records, each with its position in OpenAlex's list as its rank, and `<M> listed`
        when the list is longer than the number to fetch. No records when a request didn't get
        a usable response, which ends the query there.
    """
    status, seed = _openalex_work(connectors, query, RELATED_SELECT, Expect(work=SEED))
    listed = seed.get("related_works") if status == 200 and seed is not None else None  # noqa: PLR2004
    if not isinstance(listed, list):
        return [], None
    truncated = f"{len(listed)} listed" if len(listed) > args.max_results else None
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for rank, entry in enumerate(listed[: args.max_results], start=1):
        work_id = _listed_work_id(connectors, entry)
        if work_id is None or work_id in seen:
            continue
        seen.add(work_id)
        listed_work = Expect(work=WORK, gone_ok=True)
        status, work = _openalex_work(connectors, work_id, WORK_SELECT, listed_work)
        if status == 404:  # noqa: PLR2004 - the listed work is gone: leave it out
            continue
        if status != 200 or work is None:  # noqa: PLR2004
            return [], None
        record = _work_record(connectors, work)
        if record is not None:
            records.append(record | {"rank": rank})
    return records, truncated


def fetch(
    connectors: Connectors, args: Args, query: str
) -> tuple[list[dict[str, object]], str | None]:
    """Call the connector for one query, or send a request the harvester builds itself.

    Args:
        connectors: The connectors.
        args: The command line.
        query: The query, paper ID, seed or title.

    Returns:
        The harvest records, without their query ID and (but for `related`) their rank, and the
        query's truncation: the stop reason when snowballing hit the connector's budget, or how
        many related works were listed when more than were fetched.
    """
    searcher = connectors.searcher
    if args.service == S2:
        return _s2_fetch(connectors, args, query), None
    if args.action == "get" and args.service == ARXIV:
        return _arxiv_get(connectors, query), None
    if args.action == "get":
        status, work = _openalex_work(connectors, query, WORK_SELECT, Expect(work=WORK))
        found = status == 200 and work is not None  # noqa: PLR2004
        record = _work_record(connectors, work) if found else None
        return ([] if record is None else [record]), None
    if args.action == "related":
        return _related_fetch(connectors, args, query)
    if args.action == "search":
        # @spec PRIOR-SCR-129
        options = {"sort_by": SORTS[args.sort]} if args.service == ARXIV else {}
        papers = searcher.search(query, max_results=args.max_results, **options)
        return [_record(args.service, p) for p in papers], None
    getter = searcher.get_citations if args.action == "citations" else searcher.get_references
    # @spec PRIOR-SCR-078
    # The connector's own time budget runs on the real clock and includes the adapter's waits,
    # so give it the most it allows; its default of 30 seconds would undo a Retry-After wait.
    result = getter(query, max_results=args.max_results, timeout_seconds=RELATIONS_BUDGET)
    stop = result.get("stop_reason")
    truncated = str(stop) if stop in {"page_budget", "request_budget"} else None
    return [_record(args.service, p) for p in result.get("papers") or []], truncated


# @spec PRIOR-SCR-057, PRIOR-SCR-058, PRIOR-SCR-115, PRIOR-SCR-124
def invalid(connectors: Connectors, args: Args, query: str) -> bool:
    """Whether a query is invalid input, which is never sent.

    Args:
        connectors: The connectors.
        args: The command line.
        query: The query, paper ID, seed or title.

    Returns:
        True when the query is invalid.
    """
    if args.action == "get" and args.service == ARXIV:
        return arxiv_get_id(connectors, query) is None
    if args.action in {"get", "citations", "references", "related"}:
        try:
            connectors.relations.normalize_identifier(query)
        except ValueError:
            return True
        return False
    if args.action == "recommend":
        return s2_seed(query) is None
    operators = re.findall(r"\b(?:AND|OR|NOT)\b", query)
    is_openalex_search = args.action == "search" and args.service == OPENALEX
    return is_openalex_search and len(operators) > MAX_BOOLEAN_OPERATORS


# Outcomes -----------------------------------------------------------------------------------

FAILURE_OUTCOMES = {
    RATE: "rate limit",
    BUDGET: "rate limit",
    AUTH: "authentication",
    CLIENT: "client error",
    SERVER: "network",
    PARSE: "network",
    ARXIV_406: "network",
    NETWORK: "network",
}


def first_failure(state: QueryState) -> RequestLog | None:
    """The query's first request that didn't get a usable response.

    Args:
        state: The query.

    Returns:
        Its log, or None when every request was usable.
    """
    for log in state.requests.values():
        if log.kind != USABLE:
            return log
    return None


# @spec PRIOR-SCR-063, PRIOR-SCR-064, PRIOR-SCR-065, PRIOR-SCR-066, PRIOR-SCR-067
# @spec PRIOR-SCR-068, PRIOR-SCR-069, PRIOR-SCR-070, PRIOR-SCR-074, PRIOR-SCR-076
# @spec PRIOR-SCR-118
def outcome(state: QueryState, *, paper_id: bool, records: int) -> tuple[str, str | None]:
    """A query's outcome, from what its adapter recorded.

    Args:
        state: The query.
        paper_id: Whether its first request looks up a paper ID (citations, references or
            recommendations), so that a 404 there means the paper isn't found.
        records: How many harvest records it produced.

    Returns:
        The outcome and its reason: a refusal's, or `daily budget` for an OpenAlex budget
        response.
    """
    log = first_failure(state)
    if log is None:
        ran = "ok" if records else "empty"
        return (ran if state.requests else "network"), None
    if log.sends == 0:
        return _unsent_outcome(log)
    if log.kind == NOT_FOUND:
        return ("not found" if paper_id and log.number == 1 else "client error"), None
    reason = DAILY_BUDGET if log.kind == BUDGET else None
    return FAILURE_OUTCOMES.get(log.kind or NETWORK, "network"), reason


def _unsent_outcome(log: RequestLog) -> tuple[str, str | None]:
    """The outcome of a request the adapter never sent."""
    if log.refusal is not None:
        return "refused", log.refusal
    if log.limiter:
        return "not sent: limiter wait", None
    return "network", None


# @spec PRIOR-SCR-087, PRIOR-SCR-088
def diagnosis(results: list[QueryResult], service: str, keys: dict[str, str]) -> str:
    """The diagnosis of a route none of whose queries ran.

    Args:
        results: The route's query results, in command-line order.
        service: The service.
        keys: The API key values by service.

    Returns:
        The diagnosis, in the skill's wording.
    """
    failed = [r for r in results if r.outcome not in RAN | QUERY_FAULTS]
    last = failed[-1]
    setting = KEY_SETTINGS.get(service)
    if DAILY_BUDGET in {last.reason, last.stopped_by}:
        return "rate limit (daily budget)"
    # A query skipped after Semantic Scholar's 5xx falls through to "network".
    skipped = last.outcome == "skipped: service throttled"
    if last.outcome == "rate limit" or (skipped and last.stopped_by != "network"):
        unkeyed = setting is not None and service not in keys
        return "rate limit, no key set" if unkeyed else "rate limit"
    if last.outcome == "not sent: limiter wait":
        return "rate limit (local pacing)"
    rejected = last.outcome == "refused" and last.reason == "key rejected"
    if rejected or (last.outcome == "authentication" and service in keys):
        return f"authentication: `{setting}` rejected"
    if last.outcome == "authentication":
        return "authentication"
    return "network"


# Invocation ---------------------------------------------------------------------------------


@dataclass
class QueryResult:
    """One query's outcome and records."""

    qid: str
    query: str
    outcome: str
    reason: str | None = None
    records: list[dict[str, object]] = field(default_factory=list)
    truncated: str | None = None
    attempts: list[Attempt] = field(default_factory=list)
    # What stops the service for the rest of the invocation: set on the query whose outcome
    # stops it, and on each query skipped after it (`rate limit`, `daily budget` or `network`).
    stopped_by: str | None = None


class Harvester:
    """One invocation: its settings, run directory, transport and connectors."""

    def __init__(self, args: Args, settings: dict[str, str]) -> None:
        """Prepare the environment, run directory, limits, adapter and connector.

        Args:
            args: The command line.
            settings: The settings values.

        Raises:
            SetupError: The rate-limit or run directory can't be used.
        """
        self.args = args
        self.redact = Redactor(settings)
        self.keys = {s: settings[n] for s, n in KEY_SETTINGS.items() if n in settings}
        shared = _prepare_environment()
        self.run = RunDir(args.run_dir, self.redact)
        self.limits_note = _choose_limits(shared, self.run.root)
        now = datetime.fromtimestamp(_wall(), UTC)
        self.invocation = f"{now:%Y%m%dT%H%M%SZ}-{secrets.token_hex(3)}"
        self.handler = _LogHandler(self.run)
        if self.limits_note is not None:
            self.run.append("harvest.log", f"WARNING harvest.py: {self.limits_note}")
        self.current: QueryState | None = None
        self.internal_trace: str | None = None
        self.connectors = self._connect()

    # @spec PRIOR-SCR-040, PRIOR-SCR-041, PRIOR-SCR-042, PRIOR-SCR-027
    def _connect(self) -> Connectors:
        # The fork is imported only now, after the environment is prepared.
        from paper_search_mcp import http_limits  # noqa: PLC0415
        from paper_search_mcp.academic_platforms import (  # noqa: PLC0415
            arxiv,
            openalex,
            openalex_relations,
            semantic,
        )

        limit = http_limits.ServiceLimit
        http_limits.register_service_limit(("export.arxiv.org",), limit("arxiv", 1, 3.0))
        http_limits.register_service_limit(
            ("api.openalex.org",),
            limit("openalex", 10, 1.0, credentialed_count=30, credential="Authorization"),
        )
        s2 = (
            limit("semantic_scholar", 1, 1.0, credentialed_count=1, credential="x-api-key")
            if S2 in self.keys
            else limit("semantic_scholar", 1, 8.0)
        )
        http_limits.register_service_limit(("api.semanticscholar.org",), s2)
        transport = Transport(
            http_limits,
            self.run,
            self.keys,
            arxiv.ArxivSearcher._is_usable_406_feed,  # noqa: SLF001 - the connector's own check
            action=self.args.action,
        )
        self.transport = transport

        class Adapter(http_limits.RateLimitedAdapter):
            max_wait = MAX_WAIT_SECONDS

            @override
            def send(
                self,
                request: requests.PreparedRequest,
                *args: Any,  # noqa: ANN401
                **kwargs: Any,  # noqa: ANN401
            ) -> requests.Response:
                if args:  # requests passes these as keywords; mirror them for any other caller
                    names = ("stream", "timeout", "verify", "cert", "proxies")
                    kwargs = dict(zip(names, args, strict=False)) | kwargs
                return transport.send(self, request, kwargs)

        # The adapter times every resend, so the connectors' own sleeps only add delay, and one
        # sleeps for whatever Retry-After a service sends, a day for a spent quota.
        self.connector_clocks = {m: m.time for m in (arxiv, semantic)}  # @spec PRIOR-SCR-077
        for module in self.connector_clocks:
            vars(module)["time"] = _NoSleep()
        logger = logging.getLogger("paper_search_mcp")
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        try:
            http_limits.set_adapter_factory(Adapter)
            searcher: Any = {
                ARXIV: arxiv.ArxivSearcher,
                OPENALEX: lambda: openalex.OpenAlexSearcher(
                    api_key=self.keys.get(OPENALEX, ""), email=""
                ),
                S2: semantic.SemanticSearcher,
            }[self.args.service]()
        except RuntimeError as exc:
            raise SetupError(str(exc)) from None
        errors = (
            http_limits.requests.RequestException,
            openalex_relations.OpenAlexRelationError,
            semantic.SemanticScholarRequestError,
        )
        return Connectors(
            http_limits,
            openalex_relations,
            errors,
            semantic.SemanticScholarRequestError,
            searcher,
            self.keys.get(S2),
            arxiv.ArxivSearcher._PAPER_ID_RE,  # noqa: SLF001 - the connector's own pattern
            arxiv.feedparser,
            transport,
        )

    def close(self) -> None:
        """Detach the log handler."""
        logger = logging.getLogger("paper_search_mcp")
        logger.removeHandler(self.handler)
        logger.propagate = True
        for module, clock in getattr(self, "connector_clocks", {}).items():
            vars(module)["time"] = clock

    # @spec PRIOR-SCR-055, PRIOR-SCR-113, PRIOR-SCR-119
    def run_query(self, number: int, query: str) -> QueryResult:
        """Run one query, calling the connector again while its failed request may be retried.

        Args:
            number: Its position on the command line, from 1.
            query: The query, paper ID, seed or title.

        Returns:
            Its result.
        """
        qid = f"{self.invocation}-q{number}"
        if invalid(self.connectors, self.args, query):
            return QueryResult(qid, query, "invalid input")
        state = QueryState(qid)
        self.current = state
        self.transport.query = state
        try:
            result = self._call(state, query)
            while result.outcome not in RAN:
                failed = first_failure(state)
                if failed is None or not failed.may_retry:
                    break
                sends = self.transport.sends
                result = self._call(state, query)
                if self.transport.sends == sends:  # nothing more was sent, so stop
                    break
        finally:
            self.transport.query = None
        result.attempts = state.attempts
        failed = first_failure(state)
        if result.outcome == "rate limit":
            result.stopped_by = result.reason or "rate limit"
        elif self.args.service == S2 and result.outcome == "network" and failed is not None:
            # Semantic Scholar sheds load with 5xx as well as 429 (a 503 is already a rate
            # limit); a connection error on the last attempt doesn't stop the service.
            result.stopped_by = "network" if failed.kind == SERVER else None
        return result

    def _reraise_internal(self) -> None:
        """Raise an error of the harvester's own that a connector swallowed."""
        if self.transport.internal is not None:
            error, trace = self.transport.internal
            self.transport.internal = None
            self.internal_trace = trace
            raise error

    def _call(self, state: QueryState, query: str) -> QueryResult:
        records: list[dict[str, object]] = []
        truncated = None
        raised = False
        try:
            records, truncated = fetch(self.connectors, self.args, query)
        except self.connectors.request_errors:
            raised = True
        self._reraise_internal()
        arxiv_get = (self.args.action, self.args.service) == ("get", ARXIV)
        # arXiv reports an unknown ID with an empty feed (below), never with a 404.
        paper_id = self.args.action in NOT_FOUND_ACTIONS and not arxiv_get
        kind, reason = outcome(state, paper_id=paper_id, records=len(records))
        if raised and kind in RAN:
            kind = "network"  # @spec PRIOR-SCR-076
        failed = first_failure(state)
        gone = failed is not None and failed.sends > 0 and failed.kind == NOT_FOUND
        if gone and self.args.action in SINGLE_WORK_ACTIONS and self.args.service == OPENALEX:
            # @spec PRIOR-SCR-065 - the paper's own 404, also when it follows a redirect; a
            # listed related work's 404 is usable, so it never gets here.
            kind = "not found"
        if kind == "empty" and arxiv_get:
            kind = "not found"  # @spec PRIOR-SCR-130 - arXiv's feed has no entry for the ID
        if kind not in RAN:
            return QueryResult(state.qid, query, kind, reason)
        return QueryResult(state.qid, query, kind, reason, records, truncated)

    @property
    def _sort(self) -> str | None:
        """The sort order to name for the invocation's queries: only an arXiv newest-first one."""
        named = (self.args.action, self.args.service) == ("search", ARXIV)
        return self.args.sort if named and self.args.sort != "relevance" else None

    # @spec PRIOR-SCR-082, PRIOR-SCR-083, PRIOR-SCR-129
    def write(self, result: QueryResult) -> None:
        """Append a query's log line and records.

        Args:
            result: The query's result.
        """
        for rank, record in enumerate(result.records, start=1):
            self.run.append_json("records.jsonl", {"query_id": result.qid, "rank": rank, **record})
        self.run.append_json(
            "queries.jsonl",
            {
                "id": result.qid,
                "round": self.args.round,
                "service": self.args.service,
                # @spec PRIOR-SCR-086 - a `get` fetches a known paper, which queries no route
                "route": None if self.args.action == "get" else ROUTES[self.args.service],
                "action": self.args.action,
                "query": result.query,
                "sort": self._sort,
                "outcome": result.outcome,
                "results": len(result.records),
                "reason": result.reason,
                "truncated": result.truncated,
                "attempts": [vars(a) for a in result.attempts],
            },
        )

    # @spec PRIOR-SCR-086, PRIOR-SCR-087, PRIOR-SCR-088
    def ledger(self, results: list[QueryResult]) -> dict[str, object] | None:
        """The invocation's ledger record for its route.

        Args:
            results: Every query result.

        Returns:
            The record, or None when every query was invalid input, a client error or not
            found, or the action is `get`, which queries no route.
        """
        counted = [r for r in results if r.outcome not in QUERY_FAULTS]
        if not counted or self.args.action == "get":
            return None
        searched = any(r.outcome in RAN for r in results)
        queries = [
            r.query if r.outcome in RAN else f"{r.query} (failed: {r.outcome})" for r in results
        ]
        return {
            "route": ROUTES[self.args.service],
            "state": "searched" if searched else "unavailable",
            "queries": queries,
            "reason": None if searched else diagnosis(results, self.args.service, self.keys),
            "as_of": datetime.fromtimestamp(_wall(), UTC).date().isoformat(),
            "invocation": self.invocation,
        }

    # @spec PRIOR-SCR-089, PRIOR-SCR-090, PRIOR-SCR-091, PRIOR-SCR-093
    def summary(self, results: list[QueryResult], ledger: dict[str, object] | None) -> str:
        """The text printed for the agent.

        Args:
            results: Every query result.
            ledger: The ledger record, if any.

        Returns:
            The summary.
        """
        lines: list[str] = [] if self.limits_note is None else [self.limits_note]
        shown: set[str] = set()
        for r in results:
            head = f"{r.qid}  {self.args.service}  {r.query!r}  {r.outcome}  {len(r.records)}"
            head += " results"
            if self._sort is not None:
                head += f"  sort: {self._sort}"  # @spec PRIOR-SCR-129
            if r.reason is not None:
                head += f"  ({r.reason})"
            if r.truncated is not None:
                head += f"  truncated: {r.truncated}"
            lines.append(head)
            open_access = (self.args.action, self.args.service) == ("get", OPENALEX)
            for position, record in enumerate(r.records[: self.args.show], start=1):
                rank = record.get("rank", position)
                lines.append(_result_line(cast("int", rank), record, shown))
                if open_access:
                    lines.append(_open_access_line(record))  # @spec PRIOR-SCR-133
            more = len(r.records) - min(len(r.records), self.args.show)
            if more:
                lines.append(f"    … {more} more in {self.run.root / 'records.jsonl'}")
        lines += [
            f"{name}: {self.run.root / name}"
            for name in ("queries.jsonl", "records.jsonl", "ledger.jsonl", "harvest.log", "raw")
        ]
        text = [self.redact(line) for line in lines]
        if ledger is not None:  # redacted field by field, so it stays valid JSON
            text.insert(len(text) - 5, dumps(self.redact.record(ledger)))
        return "\n".join(text)

    def harvest(self) -> int:
        """Run every query, write the files and print the summary.

        Returns:
            The exit status.
        """
        results: list[QueryResult] = []
        stopped_by: str | None = None
        for number, query in enumerate(self.args.queries, start=1):
            qid = f"{self.invocation}-q{number}"
            if stopped_by is not None:
                # @spec PRIOR-SCR-071, PRIOR-SCR-119
                result = QueryResult(qid, query, "skipped: service throttled")
                result.stopped_by = stopped_by
            else:
                try:
                    result = self.run_query(number, query)
                except Exception:  # noqa: BLE001 - any other error is a bug, reported as such
                    trace = self.internal_trace or traceback.format_exc()
                    return self._internal_error(results, number, trace)
                stopped_by = result.stopped_by
            self.write(result)
            results.append(result)
        return self._finish(results)

    # @spec PRIOR-SCR-075
    def _internal_error(self, results: list[QueryResult], number: int, trace: str) -> int:
        self.run.append("harvest.log", f"ERROR harvest.py: internal error\n{trace}")
        for later, query in enumerate(self.args.queries[number - 1 :], start=number):
            result = QueryResult(f"{self.invocation}-q{later}", query, "internal error")
            if later == number and self.current is not None:
                result.attempts = self.current.attempts  # what the failing query did send
            self.write(result)
            results.append(result)
        self._finish(results)
        return NOT_ALL_RAN if self.transport.sends else SETUP_ERROR

    def _finish(self, results: list[QueryResult]) -> int:
        ledger = self.ledger(results)
        if ledger is not None:
            self.run.append_json("ledger.jsonl", ledger)
        sys.stdout.write(self.summary(results, ledger) + "\n")
        return 0 if all(r.outcome in RAN for r in results) else NOT_ALL_RAN


def _result_line(rank: int, record: dict[str, object], shown: set[str]) -> str:
    service_id = str(record.get("service_id") or "-")
    if service_id != "-" and service_id in shown:
        return f"  {rank:>3}  {service_id}  (shown above)"
    shown.add(service_id)
    title = " ".join(str(record.get("title") or "").split())  # arXiv titles carry line breaks
    if len(title) > TITLE_WIDTH:
        title = title[: TITLE_WIDTH - 1] + "…"
    year = record.get("year")
    citations = record.get("citations")
    year_text = "-" if year is None else str(year)
    citations_text = "-" if citations is None else str(citations)
    return f"  {rank:>3}  {year_text}  {citations_text}  {service_id}  {title}"


def _open_access_line(record: dict[str, object]) -> str:
    """The line under an OpenAlex `get` result: its open-access status and link, or neither."""
    if record.get("is_oa") is not True:
        return "       not open access"
    status, url = (record.get(name) or "-" for name in ("oa_status", "oa_url"))
    return f"       open access: {status}  {url}"


def main(argv: list[str] | None = None) -> int:
    """Run the harvester.

    Args:
        argv: The arguments, without the program name.

    Returns:
        0 when every query ran, 3 when one didn't, 4 for a usage or setup error.
    """
    # Settings come first, so a usage error that echoes a pasted key is redacted too.
    settings: dict[str, str] = {}
    setup_error: SetupError | None = None
    try:
        settings = read_settings()
    except SetupError as exc:
        setup_error = exc
    redact = Redactor(settings)
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
    except UsageError as exc:
        # The agent fixes a usage error and reruns; only a setup error lets it fall back.
        sys.stderr.write(redact(f"harvest.py: usage error: {exc}\n"))
        return SETUP_ERROR
    if setup_error is not None:
        sys.stderr.write(redact(f"harvest.py: setup error: {setup_error}\n"))
        return SETUP_ERROR
    harvester: Harvester | None = None
    try:
        harvester = Harvester(args, settings)
        return harvester.harvest()
    except SetupError as exc:
        sys.stderr.write(redact(f"harvest.py: setup error: {exc}\n"))
        return SETUP_ERROR
    except Exception:  # noqa: BLE001 - an unexpected error before any query was handled
        sys.stderr.write(redact(f"harvest.py: internal error\n{traceback.format_exc()}"))
        sent = harvester is not None and getattr(harvester, "transport", None) is not None
        return NOT_ALL_RAN if sent and harvester.transport.sends else SETUP_ERROR
    finally:
        if harvester is not None:
            harvester.close()


if __name__ == "__main__":
    sys.exit(main())
