"""Behavior tests of the prior-art search skill's harvester, run in-process against a fake server.

No test reaches the network: `HTTPAdapter.send` is replaced by a scripted server, sockets refuse
to connect, and the fork's limiter keeps its slots in a temporary directory on a fake clock.
"""

from __future__ import annotations

import ast
import contextlib
import email.utils
import fcntl
import inspect
import itertools
import json
import os
import re
import socket
import subprocess
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, override
from urllib.parse import urlsplit

import pytest
import requests
from paper_search_mcp import config, http_limits
from paper_search_mcp.academic_platforms import arxiv, openalex, openalex_relations, semantic
from requests.adapters import HTTPAdapter

from tests.harvester_support import (
    HARVEST,
    UA,
    FakeClock,
    FakeServer,
    Reply,
    arxiv_feed,
    jsonl,
    load_harvest,
    openalex_page,
    openalex_work,
    s2_no_match,
    s2_paper,
    s2_recommendations,
    s2_sparse_paper,
    s2_title_match,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType

    from tests.harvester_support import Sent

OA = "api.openalex.org"
S2 = "api.semanticscholar.org"
AX = "export.arxiv.org"
S2_MATCH = "/graph/v1/paper/search/match"
S2_RECOMMEND = "/recommendations/v1/papers/forpaper/"
TITLE = "Attention Is All You Need"
SEED = "10.1145/3368089.3409741"
FORK_VARS = ["OPENALEX_API_KEY", "OPENALEX_EMAIL", "SEMANTIC_SCHOLAR_API_KEY", "RATE_LIMIT_DIR"]
SET_BY_HARVESTER = ["PAPER_SEARCH_MCP_RATE_LIMIT_DIR", "PAPER_SEARCH_MCP_ENV_FILE"]
CANARY = "canary-key-7f3a9c"
# Maps ASCII digits to Arabic-Indic ones, which a regex `\d` also matches.
ARABIC_INDIC_DIGITS = str.maketrans("0123456789", "".join(chr(0x0660 + i) for i in range(10)))
S2_KEY = f'[semanticscholar]\napi_key = "{CANARY}"\n'
OPTIONS = {"--service", "--round", "--run-dir", "--sort", "--max-results", "--show", "--help"}


@dataclass
class Result:
    """One in-process run of the harvester."""

    code: int
    out: str
    err: str


@dataclass
class Harness:
    """A harvester under test, with its fake server and clock and a scratch git repo."""

    module: ModuleType
    server: FakeServer
    clock: FakeClock
    repo: Path
    home: Path
    cache: Path
    run_dir: Path
    capsys: pytest.CaptureFixture[str]
    results: list[Result] = field(default_factory=list)

    @property
    def limits_dir(self) -> Path:
        """Where the harvester should keep the shared limiter store."""
        return self.cache / "prior-art-search" / "rate-limits"

    def run(
        self, action: str, service: str, *queries: str, rnd: int = 1, extra: tuple[str, ...] = ()
    ) -> Result:
        """Run the harvester in-process.

        Args:
            action: `search`, `citations`, `references`, `recommend` or `lookup`.
            service: The service.
            *queries: The queries, paper IDs or titles.
            rnd: The round number.
            extra: More options, placed before the queries.

        Returns:
            The exit status and what was printed.
        """
        argv = [action, "--service", service, "--round", str(rnd), "--run-dir", str(self.run_dir)]
        code = self.module.main([*argv, *extra, *queries])
        out, err = self.capsys.readouterr()
        result = Result(code, out, err)
        self.results.append(result)
        return result

    def main(self, argv: list[str]) -> int:
        """Call the harvester's `main` directly, absorbing a `SystemExit`.

        Args:
            argv: The arguments.

        Returns:
            The exit status.
        """
        try:
            return int(self.module.main(argv))
        except SystemExit as exit_:
            return int(exit_.code or 0)
        finally:
            self.capsys.readouterr()

    def reload(self) -> None:
        """Load the harvester again, as a new invocation's process would."""
        _reset_fork()
        self.module = _patched(load_harvest(), self.clock)

    def settings(self, body: str, *, ignored: bool = True) -> Path:
        """Write the host repo's settings file.

        Args:
            body: Its TOML.
            ignored: Whether to make git ignore it.

        Returns:
            Its path.
        """
        path = self.repo / ".config" / "prior-art-sources.toml"
        path.parent.mkdir(exist_ok=True)
        path.write_text(body)
        if ignored:
            (self.repo / ".gitignore").write_text(".config/prior-art-sources.toml\n")
        return path

    def queries(self) -> list[dict[str, Any]]:
        """The query log's lines."""
        return jsonl(self.run_dir / "queries.jsonl")

    def outcomes(self) -> list[object]:
        """Each logged query's outcome, in order."""
        return [q["outcome"] for q in self.queries()]

    def ledger(self) -> list[dict[str, Any]]:
        """The ledger file's records."""
        return jsonl(self.run_dir / "ledger.jsonl")

    def written(self) -> str:
        """Everything the harvester printed or wrote into the run directory so far."""
        texts = [text for r in self.results for text in (r.out, r.err)]
        texts += [
            p.read_bytes().decode("utf-8", errors="replace")
            for p in self.run_dir.rglob("*")
            if p.is_file()
        ]
        return "\n".join(texts)


def _reset_fork() -> None:
    connection = http_limits._connection  # noqa: SLF001
    if connection is not None:
        connection.close()
    http_limits._connection = None  # noqa: SLF001
    http_limits.set_adapter_factory(None)
    config._ENV_LOADED = False  # noqa: SLF001


def _no_jitter(a: float, b: float) -> float:  # noqa: ARG001 - random.uniform's signature
    return a


def _patched(module: ModuleType, clock: FakeClock) -> ModuleType:
    # The harvester's own clock seams, used for its Retry-After waits, and its random source for
    # Semantic Scholar's backoff jitter, fixed at no jitter unless a test replaces it.
    seams = {
        "_sleep": clock.sleep,
        "_monotonic": clock.monotonic,
        "_wall": clock.time,
        "_uniform": _no_jitter,
    }
    # A renamed seam would leave the real clock or random source in place: fail loudly instead.
    missing = sorted(name for name in seams if name not in vars(module))
    assert not missing, f"the harvester has no seam named {missing}"
    vars(module).update(seams)
    return module


def _gaps(sent: list[Sent]) -> list[float]:
    """The fake-clock seconds between consecutive sends."""
    return [b.wall - a.wall for a, b in itertools.pairwise(sent)]


def _backoff(retries: int, jitter: float) -> float:
    """Semantic Scholar's wait before a retry, as PRIOR-SCR-111 gives it."""
    return min(15.0, 1.5 * 1.6**retries + jitter)


def _anonymous_sends() -> int:
    """How many sends an always-failing anonymous S2 request gets, with no jitter.

    Each retry goes at the later of its backoff and the next 8-second slot (PRIOR-SCR-111), and
    none goes more than 60 seconds after the first response (PRIOR-SCR-112); the attempt limit is
    7 (PRIOR-SCR-050).
    """
    elapsed, sends = 0.0, 1
    for retries in range(6):
        elapsed += max(8.0, _backoff(retries, 0.0))
        if elapsed > 60:
            break
        sends += 1
    return sends


@pytest.fixture
def h(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> Iterator[Harness]:
    """A harvester in a scratch git repo, with a fake server and clock, and sockets refused."""

    def refuse(*_args: object, **_kwargs: object) -> None:
        msg = "network access in a harvester test"
        raise AssertionError(msg)

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)  # noqa: S603, S607
    home = tmp_path / "home"
    home.mkdir()
    cache = tmp_path / "cache"
    monkeypatch.chdir(repo)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache))
    # setenv then delenv, so teardown removes whatever the harvester sets.
    for name in [*FORK_VARS, *(f"PAPER_SEARCH_MCP_{v}" for v in FORK_VARS), *SET_BY_HARVESTER]:
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name)
    monkeypatch.setattr(http_limits, "SERVICE_LIMITS", dict(http_limits.SERVICE_LIMITS))

    clock = FakeClock()
    monkeypatch.setattr(time, "sleep", clock.sleep)
    monkeypatch.setattr(http_limits, "_sleep", clock.sleep)
    monkeypatch.setattr(http_limits, "_clock", clock.time)
    monkeypatch.setattr(http_limits, "_monotonic", clock.monotonic)
    server = FakeServer(clock)

    def send(
        _adapter: HTTPAdapter, request: requests.PreparedRequest, *_a: object, **kw: object
    ) -> requests.Response:
        return server.send(request, **kw)

    monkeypatch.setattr(HTTPAdapter, "send", send)
    _reset_fork()
    harness = Harness(
        _patched(load_harvest(), clock),
        server,
        clock,
        repo,
        home,
        cache,
        tmp_path / "run",
        capsys,
    )
    yield harness
    _reset_fork()
    assert server.unexpected == []


class _Connector(Protocol):
    session: requests.Session


def _stray_search(url: str, **kwargs: Any) -> Callable[..., list[object]]:  # noqa: ANN401
    """A connector `search` that sends one request of the test's choosing through its session."""

    def search(self: _Connector, *_args: object, **_kwargs: object) -> list[object]:
        self.session.get(url, **kwargs)
        return []

    return search


# Arguments ----------------------------------------------------------------------------------


# @spec PRIOR-SCR-010
def test_search_takes_queries_and_writes_one_log_line_each(h: Harness) -> None:
    """Each query gets its own log line, and the run directory is created."""
    h.server.route(OA, "/works", Reply(200, openalex_page(3)))
    result = h.run("search", "openalex", "regression test selection", "test prioritization")
    assert result.code == 0
    assert [q["query"] for q in h.queries()] == ["regression test selection", "test prioritization"]
    assert h.run_dir.is_dir()


# @spec PRIOR-SCR-010
@pytest.mark.parametrize(
    ("action", "service", "param", "expected"),
    [
        ("search", "openalex", "per_page", "50"),
        ("search", "arxiv", "max_results", "50"),
        ("citations", "openalex", "per_page", "100"),
    ],
)
def test_default_fetch_depth(
    h: Harness, action: str, service: str, param: str, expected: str
) -> None:
    """Searches fetch 50 results and citations 100 when no depth is given."""
    h.server.route(OA, "/works/", Reply(200, {"id": "https://openalex.org/W9"}))
    h.server.route(OA, "/works", Reply(200, openalex_page(2)))
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(2)))
    h.run(action, service, "query terms" if action == "search" else "W9")
    asked = [s.query[param][0] for s in h.server.sent if param in s.query]
    assert asked[0] == expected


# @spec PRIOR-SCR-010
@pytest.mark.parametrize(("action", "depth"), [("search", "100"), ("citations", "500")])
def test_maximum_fetch_depth_is_accepted(h: Harness, action: str, depth: str) -> None:
    """The largest allowed depth runs."""
    h.server.route(OA, "/works/", Reply(200, {"id": "https://openalex.org/W9"}))
    h.server.route(OA, "/works", Reply(200, openalex_page(2)))
    paper = "q" if action == "search" else "W9"
    assert h.run(action, "openalex", paper, extra=("--max-results", depth)).code == 0


# @spec PRIOR-SCR-010, PRIOR-SCR-114
@pytest.mark.parametrize(("extra", "limit"), [((), "100"), (("--max-results", "500"), "500")])
def test_recommend_fetch_depth(h: Harness, extra: tuple[str, ...], limit: str) -> None:
    """Recommendations fetch 100 results when no depth is given, and up to 500."""
    h.server.route(S2, S2_RECOMMEND, Reply(200, s2_recommendations(2)))
    assert h.run("recommend", "semanticscholar", SEED, extra=extra).code == 0
    assert h.server.sent[0].query["limit"] == [limit]


# @spec PRIOR-SCR-010
def test_lookup_takes_a_depth_of_1(h: Harness) -> None:
    """A lookup returns its one best match, so a depth of 1 is accepted."""
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match()))
    assert h.run("lookup", "semanticscholar", TITLE, extra=("--max-results", "1")).code == 0
    assert len(h.server.sent) == 1


def _argv(*parts: str) -> list[str]:
    return list(parts)


def _s2_argv(action: str, *rest: str, service: str = "semanticscholar") -> list[str]:
    return [action, "--service", service, "--round", "1", "--run-dir", "R", *rest]


# @spec PRIOR-SCR-010, PRIOR-SCR-011
@pytest.mark.parametrize(
    "argv",
    [
        _argv("citations", "--service", "arxiv", "--round", "1", "--run-dir", "R", "W1"),
        _argv("search", "--service", "openalex", "--round", "0", "--run-dir", "R", "q"),
        _argv("search", "--service", "openalex", "--round", "1", "--run-dir", "R"),
        _argv("search", "--service", "openalex", "--round", "1", "--run-dir", "R", ""),
        _argv("search", "--service", "openalex", "--round", "1", "--run-dir", "R", "--bogus", "q"),
        _argv("search", "--service", "nope", "--round", "1", "--run-dir", "R", "q"),
        _argv(
            "search",
            "--service",
            "openalex",
            "--round",
            "1",
            "--run-dir",
            "R",
            "--max-results",
            "101",
            "q",
        ),
        _argv(
            "search",
            "--service",
            "openalex",
            "--round",
            "1",
            "--run-dir",
            "R",
            "--max-results",
            "0",
            "q",
        ),
        _argv(
            "citations",
            "--service",
            "openalex",
            "--round",
            "1",
            "--run-dir",
            "R",
            "--max-results",
            "501",
            "W1",
        ),
        _argv(
            "search", "--service", "openalex", "--round", "1", "--run-dir", "R", "--show", "-1", "q"
        ),
        _argv(
            "search",
            "--service",
            "openalex",
            "--service",
            "arxiv",
            "--round",
            "1",
            "--run-dir",
            "R",
            "q",
        ),
        _s2_argv("search", "q"),
        _s2_argv("citations", "W1"),
        _s2_argv("references", "W1"),
        _s2_argv("recommend", SEED, service="openalex"),
        _s2_argv("recommend", SEED, service="arxiv"),
        _s2_argv("lookup", TITLE, service="openalex"),
        _s2_argv("lookup", TITLE, service="arxiv"),
        _s2_argv("lookup", "   "),
        _s2_argv("lookup", "\t\n"),
        _s2_argv("lookup", "--max-results", "2", TITLE),
        _s2_argv("lookup", "--max-results", "0", TITLE),
        _s2_argv("recommend", "--max-results", "501", SEED),
        _s2_argv("recommend", "--max-results", "0", SEED),
        _s2_argv("recommend", ""),
    ],
)
def test_invalid_command_line_exits_4_and_sends_nothing(h: Harness, argv: list[str]) -> None:
    """Every invalid command line exits 4 before any request."""
    assert h.main(argv) == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-011
@pytest.mark.parametrize(
    "more",
    [
        _argv("search", "--service", "openalex", "--round", "1", "--run-dir", "", "q"),
        _argv("search", "--serv", "openalex", "--round", "1", "--run-dir", "R", "q"),
        _argv("search", "--service", "openalex", "--round", "1", "--run-dir", "R", "-h"),
    ],
)
def test_empty_run_dir_abbreviations_and_stray_help_exit_4(h: Harness, more: list[str]) -> None:
    """An empty run directory, an abbreviated option or a query of -h is a usage error."""
    assert h.main(more) == 4
    assert h.server.sent == []
    assert not (h.repo / "queries.jsonl").exists()


# @spec PRIOR-SCR-030
def test_usage_error_is_redacted(h: Harness) -> None:
    """A key pasted on the command line is redacted from the usage error."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    code = h.module.main(["search", "--service", "openalex", "--api-key", CANARY, "q"])
    err = h.capsys.readouterr().err
    assert code == 4
    assert CANARY not in err


# Environment and settings ---------------------------------------------------------------------


# @spec PRIOR-SCR-020, PRIOR-SCR-022
def test_fork_settings_from_the_environment_are_ignored(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No variable the fork reads, nor the fork's own settings file, reaches a request."""
    canaries = {}
    for i, name in enumerate(FORK_VARS[:3]):
        for prefix in ("", "PAPER_SEARCH_MCP_"):
            canaries[prefix + name] = f"{CANARY}-{i}-{len(prefix)}"
    fork_env = h.home / "fork.env"
    fork_env.write_text("".join(f"{k}={v}-file\n" for k, v in canaries.items()))
    for name, value in canaries.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("PAPER_SEARCH_MCP_ENV_FILE", str(fork_env))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match()))
    h.run("search", "openalex", "q")
    h.run("lookup", "semanticscholar", TITLE)
    assert {s.host for s in h.server.sent} == {OA, S2}
    for sent in h.server.sent:
        assert CANARY not in json.dumps(sent.headers) + sent.url
    for name in canaries:
        assert CANARY not in os.environ.get(name, "")
    assert not Path(os.environ["PAPER_SEARCH_MCP_ENV_FILE"]).exists()


# @spec PRIOR-SCR-020
def test_harvester_does_not_import_the_fork_at_module_level() -> None:
    """The fork is imported only after the environment is prepared."""
    tree = ast.parse(HARVEST.read_text())
    for node in tree.body:
        if isinstance(node, ast.Import):
            assert not any(a.name.startswith("paper_search_mcp") for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert not (node.module or "").startswith("paper_search_mcp")


# @spec PRIOR-SCR-021
def test_limits_are_shared_under_the_cache_directory(
    h: Harness, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The limiter store goes under the cache directory, whatever the environment named."""
    elsewhere = tmp_path / "elsewhere"
    monkeypatch.setenv("PAPER_SEARCH_MCP_RATE_LIMIT_DIR", str(elsewhere))
    monkeypatch.setenv("RATE_LIMIT_DIR", str(elsewhere))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert (h.limits_dir / "rate_limits.sqlite").exists()
    assert not elsewhere.exists()
    assert Path(os.environ["PAPER_SEARCH_MCP_RATE_LIMIT_DIR"]).is_absolute()


# @spec PRIOR-SCR-021
@pytest.mark.parametrize("xdg", [None, "", "relative/cache"])
def test_limits_fall_back_to_home_cache(
    h: Harness, monkeypatch: pytest.MonkeyPatch, xdg: str | None
) -> None:
    """Without a usable absolute XDG_CACHE_HOME, the store goes under ~/.cache."""
    if xdg is None:
        monkeypatch.delenv("XDG_CACHE_HOME")
    else:
        monkeypatch.setenv("XDG_CACHE_HOME", xdg)
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    store = h.home / ".cache" / "prior-art-search" / "rate-limits" / "rate_limits.sqlite"
    assert store.exists()


# @spec PRIOR-SCR-023, PRIOR-SCR-094
@pytest.mark.parametrize("blocker", ["file", "read-only"])
def test_unusable_shared_limits_fall_back_to_the_run_directory(h: Harness, blocker: str) -> None:
    """A sandbox that blocks the cache directory moves the limiter into the run directory."""
    if blocker == "file":
        h.cache.mkdir()
        (h.cache / "prior-art-search").write_text("a file where a directory should be")
    else:
        h.limits_dir.mkdir(parents=True)
        h.limits_dir.chmod(0o555)
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    try:
        result = h.run("search", "openalex", "q")
    finally:
        if blocker != "file":
            h.limits_dir.chmod(0o755)
    assert result.code == 0
    assert (h.run_dir / "rate-limits" / "rate_limits.sqlite").exists()
    assert os.environ["PAPER_SEARCH_MCP_RATE_LIMIT_DIR"] == str(h.run_dir / "rate-limits")
    first = result.out.splitlines()[0]
    assert "only within this run" in first
    assert "only within this run" in (h.run_dir / "harvest.log").read_text()


# @spec PRIOR-SCR-023
def test_no_writable_limits_directory_exits_4(h: Harness) -> None:
    """With neither the shared nor the run directory usable, nothing is sent."""
    h.cache.mkdir()
    (h.cache / "prior-art-search").write_text("blocked")
    h.run_dir.mkdir()
    (h.run_dir / "rate-limits").write_text("blocked too")
    assert h.run("search", "openalex", "q").code == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-023
def test_writable_shared_limits_print_no_note(h: Harness) -> None:
    """With the shared directory usable, the summary has no pacing note."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert "only within this run" not in h.run("search", "openalex", "q").out


# @spec PRIOR-SCR-024, PRIOR-SCR-027
def test_ignored_settings_file_supplies_the_openalex_key(h: Harness) -> None:
    """The OpenAlex key from the ignored settings file goes in its Authorization header."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[0].headers.get("Authorization") == f"Bearer {CANARY}"


# @spec PRIOR-SCR-024
def test_settings_file_is_found_from_a_subdirectory(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The settings file is looked up at the repo's top, not the working directory."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    sub = h.repo / "deep" / "er"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", "q")
    assert h.server.sent[0].headers.get("Authorization") == f"Bearer {CANARY}"


# @spec PRIOR-SCR-024, PRIOR-SCR-025
def test_settings_file_not_ignored_is_not_read(h: Harness) -> None:
    """A settings file git doesn't ignore is never read."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n', ignored=False)
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-024
def test_tracked_settings_file_is_not_read(h: Harness) -> None:
    """A committed settings file counts as not ignored, even when a pattern matches it."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    subprocess.run(
        ["git", "add", "-f", ".config/prior-art-sources.toml"],  # noqa: S607
        cwd=h.repo,
        check=True,
    )
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", "q")
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-025
def test_outside_a_git_repo_runs_without_settings(
    h: Harness, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Outside a repository the harvester runs with no setting values."""
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-025
def test_without_git_runs_without_settings(
    h: Harness, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When git can't be run, the harvester runs with no setting values."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    empty = tmp_path / "no-tools"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-026
@pytest.mark.parametrize("value", ["", "   "])
def test_blank_value_counts_as_not_set(h: Harness, value: str) -> None:
    """An empty or whitespace value sends no key."""
    h.settings(f'[openalex]\napi_key = "{value}"\n')
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-026
def test_value_is_trimmed(h: Harness) -> None:
    """Surrounding whitespace is stripped from a value."""
    h.settings(f'[openalex]\napi_key = "  {CANARY} "\n')
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", "q")
    assert h.server.sent[0].headers.get("Authorization") == f"Bearer {CANARY}"


# @spec PRIOR-SCR-020, PRIOR-SCR-027, PRIOR-SCR-028
@pytest.mark.parametrize(
    ("action", "path", "reply", "query"),
    [
        ("lookup", S2_MATCH, Reply(200, s2_title_match()), TITLE),
        ("recommend", S2_RECOMMEND, Reply(200, s2_recommendations(1)), SEED),
    ],
)
def test_each_key_goes_only_to_its_own_service(
    h: Harness, action: str, path: str, reply: Reply, query: str
) -> None:
    """The harvester puts the Semantic Scholar key in x-api-key itself; no other key rides along."""
    h.settings(f'[openalex]\napi_key = "oa-{CANARY}"\n[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, path, reply)
    assert h.run(action, "semanticscholar", query).code == 0
    (sent,) = h.server.sent
    assert sent.headers.get("x-api-key") == CANARY
    assert "Authorization" not in sent.headers
    assert "PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY" not in os.environ


# @spec PRIOR-SCR-028
def test_no_key_set_sends_no_key_header(h: Harness) -> None:
    """Without a Semantic Scholar key, its requests carry no x-api-key header."""
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match()))
    assert h.run("lookup", "semanticscholar", TITLE).code == 0
    assert "x-api-key" not in h.server.sent[0].headers


# @spec PRIOR-SCR-029
def test_no_option_takes_a_setting_value(h: Harness) -> None:
    """Every action's options are the documented ones, none of which takes a setting value."""
    seen: set[str] = set()
    actions = ("search", "get", "citations", "references", "related", "recommend", "lookup")
    for argv in (["--help"], *([a, "--help"] for a in actions)):
        with contextlib.suppress(SystemExit):
            h.module.main(argv)
        out = h.capsys.readouterr().out
        seen |= set(re.findall(r"(?<![\w-])--[a-z][\w-]*", out))
    assert "--service" in seen
    assert seen <= OPTIONS


# @spec PRIOR-SCR-030
def test_values_are_redacted_everywhere(h: Harness) -> None:
    """Every settings value, as written or percent-encoded, is redacted in all output."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n[crossref]\nmailto = "me+x@example.org"\n')
    echo = {"error": f"bad key {CANARY}", "contact": "me+x@example.org me%2Bx%40example.org"}
    h.server.route(OA, "/works", Reply(500, echo))
    h.run("search", "openalex", "q")
    written = h.written()
    for leaked in (CANARY, "me+x@example.org", "me%2Bx%40example.org"):
        assert leaked not in written
    assert "[redacted:openalex.api_key]" in written
    assert "[redacted:crossref.mailto]" in written


# @spec PRIOR-SCR-030
def test_longer_values_are_redacted_first(h: Harness) -> None:
    """A value containing another is redacted under its own name."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n[semanticscholar]\napi_key = "{CANARY}-long"\n')
    h.server.route(OA, "/works", Reply(500, {"echo": f"{CANARY}-long"}))
    h.run("search", "openalex", "q")
    written = h.written()
    assert "[redacted:semanticscholar.api_key]" in written
    assert "[redacted:openalex.api_key]-long" not in written


# @spec PRIOR-SCR-031
def test_no_request_header_is_written(h: Harness) -> None:
    """No request header's name or value appears in any output."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    h.server.route(OA, "/works", Reply(500, {}))
    h.run("search", "openalex", "q")
    written = h.written()
    for text in ("Bearer", UA, "Authorization", "User-Agent"):
        assert text not in written


SECRET = 739182465


# @spec PRIOR-SCR-032
@pytest.mark.parametrize(
    ("body", "kind"),
    [
        (f'[openalex\napi_key = "{SECRET}"\n', "TOML"),
        (f"[openalex]\napi_key = {SECRET}\n", "string"),
    ],
)
def test_broken_settings_file_exits_4_without_values(h: Harness, body: str, kind: str) -> None:
    """A broken settings file stops the run, naming the file and the problem but no value."""
    h.settings(body)
    result = h.run("search", "openalex", "q")
    assert result.code == 4
    assert h.server.sent == []
    message = result.out + result.err
    assert "prior-art-sources.toml" in message
    assert kind.lower() in message.lower()
    assert str(SECRET) not in message


# @spec PRIOR-SCR-032
def test_unreadable_settings_file_exits_4(h: Harness) -> None:
    """A settings file that can't be read stops the run."""
    path = h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    path.chmod(0o000)
    try:
        result = h.run("search", "openalex", "q")
    finally:
        path.chmod(0o600)
    assert result.code == 4
    assert "read" in (result.out + result.err).lower()
    assert h.server.sent == []


# Transport ----------------------------------------------------------------------------------


# @spec PRIOR-SCR-040, PRIOR-SCR-046
@pytest.mark.parametrize(
    ("action", "service", "host", "path", "reply", "query"),
    [
        ("search", "openalex", OA, "/works", Reply(200, openalex_page(1)), "q"),
        ("search", "arxiv", AX, "/api/query", Reply(200, arxiv_feed(1)), "q"),
        ("lookup", "semanticscholar", S2, S2_MATCH, Reply(200, s2_title_match()), TITLE),
        (
            "recommend",
            "semanticscholar",
            S2,
            S2_RECOMMEND,
            Reply(200, s2_recommendations(1)),
            SEED,
        ),
    ],
)
def test_every_request_carries_the_skill_user_agent(  # noqa: PLR0913, PLR0917
    h: Harness, action: str, service: str, host: str, path: str, reply: Reply, query: str
) -> None:
    """The adapter replaces each connector's user agent with the skill's."""
    h.server.route(host, path, reply)
    assert h.run(action, service, query).code == 0
    assert h.server.sent
    assert all(s.headers.get("User-Agent") == UA for s in h.server.sent)


# @spec PRIOR-SCR-040, PRIOR-SCR-044
def test_redirect_hops_pass_through_the_adapter(h: Harness) -> None:
    """A redirect on the same host carries the skill's user agent; one elsewhere is refused."""
    h.server.route(
        OA, "/works", Reply(302, b"", {"Location": "https://api.openalex.org/works-moved"})
    )
    h.server.route(OA, "/works-moved", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "a").code == 0
    assert [s.path for s in h.server.sent] == ["/works", "/works-moved"]
    assert h.server.sent[1].headers.get("User-Agent") == UA


# @spec PRIOR-SCR-044, PRIOR-SCR-070
@pytest.mark.parametrize(
    "url",
    [
        "https://sci-hub.example/paper",
        "http://api.openalex.org/works",
        "https://api.openalex.org:8443/works",
        "https://arxiv.org/pdf/2401.00001",
    ],
)
def test_other_hosts_schemes_and_ports_are_refused(
    h: Harness, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    """A request off the three API hosts, or not plain https, is refused unsent."""
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", _stray_search(url))
    assert h.run("search", "openalex", "q").code == 3
    assert h.server.sent == []
    (logged,) = h.queries()
    assert (logged["outcome"], logged["reason"]) == ("refused", "host")


# @spec PRIOR-SCR-045, PRIOR-SCR-070
def test_verification_off_is_refused(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """A request with verify=False is refused unsent."""
    stray = _stray_search("https://api.openalex.org/works", verify=False)
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", stray)
    assert h.run("search", "openalex", "q").code == 3
    assert h.server.sent == []
    (logged,) = h.queries()
    assert (logged["outcome"], logged["reason"]) == ("refused", "tls")


# @spec PRIOR-SCR-047
def test_credential_headers_go_only_to_their_service(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Authorization and x-api-key are stripped from requests to other services."""
    stray = _stray_search(
        "https://export.arxiv.org/api/query",
        headers={"Authorization": "Bearer stray", "x-api-key": "stray"},
    )
    monkeypatch.setattr(arxiv.ArxivSearcher, "search", stray)
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    h.run("search", "arxiv", "q")
    (sent,) = h.server.sent
    assert "Authorization" not in sent.headers
    assert "x-api-key" not in sent.headers


# @spec PRIOR-SCR-048, PRIOR-SCR-070
@pytest.mark.parametrize("sent_key", [None, "wrong-value"])
def test_keyed_service_refuses_a_request_without_its_key(
    h: Harness, monkeypatch: pytest.MonkeyPatch, sent_key: str | None
) -> None:
    """With a key set, a request to its service lacking that exact key is refused unsent."""
    h.settings(S2_KEY)
    headers = {} if sent_key is None else {"x-api-key": sent_key}
    stray = _stray_search(f"https://{S2}{S2_MATCH}?query=q", headers=headers)
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", stray)
    assert h.run("search", "openalex", "q").code == 3
    assert h.server.sent == []
    (logged,) = h.queries()
    assert (logged["outcome"], logged["reason"]) == ("refused", "missing key")


# @spec PRIOR-SCR-028, PRIOR-SCR-061, PRIOR-SCR-067, PRIOR-SCR-072
def test_semantic_scholar_auth_failure_is_sent_once_with_the_key(h: Harness) -> None:
    """A keyed lookup's 403 isn't retried, with the key or without it, and rejects the key."""
    h.settings(S2_KEY)
    h.server.route(S2, S2_MATCH, Reply(403, {"message": "Forbidden"}))
    assert h.run("lookup", "semanticscholar", TITLE).code == 3
    (sent,) = h.server.sent
    assert sent.headers.get("x-api-key") == CANARY
    assert h.outcomes() == ["authentication"]
    assert "semanticscholar" in (h.run_dir / "state.json").read_text()


# @spec PRIOR-SCR-049, PRIOR-SCR-072
def test_rejected_key_is_recorded_and_blocks_later_invocations(h: Harness) -> None:
    """A rejected key is written to state.json, and a fresh process refuses that service."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    h.server.route(OA, "/works", Reply(401, {"error": "invalid key"}))
    assert h.run("search", "openalex", "a", "b").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["authentication", "refused"]
    state = (h.run_dir / "state.json").read_text()
    assert "openalex" in state
    assert CANARY not in state
    h.reload()
    assert h.run("search", "openalex", "c").code == 3
    assert len(h.server.sent) == 1
    last = h.queries()[-1]
    assert (last["outcome"], last["reason"]) == ("refused", "key rejected")


# @spec PRIOR-SCR-041
def test_limiter_wait_is_capped_at_60_seconds(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every slot request allows at most 60 seconds, counted after any Retry-After wait."""
    calls: list[tuple[float, float]] = []
    real = http_limits.acquire

    def spy(
        limit: http_limits.ServiceLimit,
        max_wait: float = http_limits.MAX_WAIT_SECONDS,
        credentialed: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        calls.append((max_wait, h.clock.mono))
        real(limit, max_wait, credentialed)

    monkeypatch.setattr(http_limits, "acquire", spy)
    h.server.route(
        OA, "/works", Reply(429, {}, {"Retry-After": "50"}), Reply(200, openalex_page(1))
    )
    assert h.run("search", "openalex", "q").code == 0
    assert [wait for wait, _ in calls] == [60, 60]
    assert calls[1][1] - calls[0][1] >= 50


# @spec PRIOR-SCR-041, PRIOR-SCR-042
def test_semantic_scholar_anonymous_requests_are_8_seconds_apart(h: Harness) -> None:
    """Without a key, Semantic Scholar gets one request every 8 seconds."""
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match()))
    h.server.route(S2, S2_RECOMMEND, Reply(200, s2_recommendations(1)))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 0
    assert h.run("recommend", "semanticscholar", SEED).code == 0
    times = [s.wall for s in h.server.sent]
    assert len(times) == 3
    assert all(b - a >= 8 for a, b in itertools.pairwise(times))


# @spec PRIOR-SCR-042
def test_semantic_scholar_keyed_requests_are_1_second_apart(h: Harness) -> None:
    """With a key, Semantic Scholar gets one request a second."""
    h.settings(S2_KEY)
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match()))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 0
    gap = h.server.sent[1].wall - h.server.sent[0].wall
    assert 1 <= gap < 8


# @spec PRIOR-SCR-042
def test_arxiv_requests_are_3_seconds_apart(h: Harness) -> None:
    """The arXiv API gets one request every 3 seconds."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    assert h.run("search", "arxiv", "a", "b").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall >= 3


# (host, count, seconds, credentialed count, credential, keyed run, phrase in sources.md)
LIMITS = [
    (AX, 1, 3.0, None, None, False, r"no more than one request every three seconds"),
    (OA, 10, 1.0, 30, "Authorization", False, r"10 requests a second without a key and 30 with"),
    (S2, 1, 8.0, None, None, False, r"space them 8 seconds apart"),
    (S2, 1, 1.0, 1, "x-api-key", True, r"their own limit of 1 a second"),
]
# An invocation of each host's own service: (action, service, path, reply, query).
INVOCATIONS = {
    AX: ("search", "arxiv", "/api/query", Reply(200, arxiv_feed(1)), "q"),
    OA: ("search", "openalex", "/works", Reply(200, openalex_page(1)), "q"),
    S2: ("lookup", "semanticscholar", S2_MATCH, Reply(200, s2_title_match()), TITLE),
}


# @spec PRIOR-SCR-042, PRIOR-SCR-043
@pytest.mark.parametrize(
    ("host", "count", "seconds", "cred_count", "cred", "keyed", "phrase"),
    LIMITS,
    ids=["arxiv", "openalex", "semanticscholar", "semanticscholar-keyed"],
)
def test_registered_limits_match_sources(  # noqa: PLR0913, PLR0917
    h: Harness,
    host: str,
    count: int,
    seconds: float,
    cred_count: int | None,
    cred: str | None,
    keyed: bool,  # noqa: FBT001
    phrase: str,
) -> None:
    """Each registered limit is the figure that sources.md's Rate limits section states."""
    sources = HARVEST.parent.parent / "references" / "sources.md"
    rate_limits = sources.read_text().split("## Rate limits", 1)[1].split("\n## ", 1)[0]
    assert re.search(phrase, rate_limits), phrase
    if keyed:
        h.settings(S2_KEY)
    action, service, path, reply, query = INVOCATIONS[host]
    h.server.route(host, path, reply)
    assert h.run(action, service, query).code == 0
    limit = http_limits.SERVICE_LIMITS[host]
    assert (limit.seconds, limit.credential) == (seconds, cred)
    if keyed:
        assert limit.credentialed_count == cred_count
    else:
        assert (limit.count, limit.credentialed_count) == (count, cred_count)


# @spec PRIOR-SCR-050, PRIOR-SCR-055, PRIOR-SCR-070
def test_one_retry_per_request_whoever_asks(h: Harness) -> None:
    """The arXiv connector retries a soft rate limit by itself; only two sends go out."""
    h.server.route(AX, "/api/query", Reply(200, "Rate exceeded."))
    assert h.run("search", "arxiv", "q").code == 3
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["rate limit"]


# @spec PRIOR-SCR-055
def test_harvester_retries_a_connector_that_does_not(h: Harness) -> None:
    """OpenAlex's search never retries; the harvester calls it once more."""
    h.server.route(OA, "/works", Reply(500, {}), Reply(200, openalex_page(2)))
    assert h.run("search", "openalex", "q").code == 0
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-051, PRIOR-SCR-055, PRIOR-SCR-084
def test_retry_does_not_resend_pages_that_worked(h: Harness) -> None:
    """On the second call, the seed and first page come from memory; only page 2 is resent."""
    h.server.route(OA, "/works/W7", Reply(200, {"id": "https://openalex.org/W7"}))
    h.server.route(
        OA,
        "/works",
        Reply(200, openalex_page(100, total=150)),
        Reply(503, {}),
        Reply(200, openalex_page(50, start=101, total=150)),
        params={"filter": "cites:W7"},
    )
    assert h.run("citations", "openalex", "W7", extra=("--max-results", "150")).code == 0
    assert [s.path for s in h.server.sent].count("/works/W7") == 1
    pages = [s.query.get("page", ["?"])[0] for s in h.server.sent if s.path == "/works"]
    assert pages == ["1", "2", "2"]
    (logged,) = h.queries()
    assert any(a["from_memory"] for a in logged["attempts"])
    assert len(list((h.run_dir / "raw").iterdir())) == len(h.server.sent)


# @spec PRIOR-SCR-052
def test_retry_after_seconds_is_honored(h: Harness) -> None:
    """The retry waits for Retry-After given in seconds."""
    h.server.route(OA, "/works", Reply(429, {}, {"Retry-After": "5"}), Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall >= 5
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-052
def test_retry_after_date_is_honored(h: Harness) -> None:
    """The retry waits for Retry-After given as an HTTP date."""
    when = email.utils.formatdate(h.clock.wall + 7, usegmt=True)
    h.server.route(
        OA, "/works", Reply(429, {}, {"Retry-After": when}), Reply(200, openalex_page(1))
    )
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall >= 6


# @spec PRIOR-SCR-052
def test_retry_after_in_the_past_means_no_extra_wait(h: Harness) -> None:
    """A Retry-After date already past adds no wait."""
    when = email.utils.formatdate(h.clock.wall - 600, usegmt=True)
    h.server.route(
        OA, "/works", Reply(503, {}, {"Retry-After": when}), Reply(200, openalex_page(1))
    )
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall < 15


# @spec PRIOR-SCR-052, PRIOR-SCR-053
def test_unparseable_retry_after_waits_15_seconds(h: Harness) -> None:
    """A Retry-After that parses as neither form counts as absent."""
    h.server.route(
        OA, "/works", Reply(429, {}, {"Retry-After": "soon"}), Reply(200, openalex_page(1))
    )
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall >= 15


# @spec PRIOR-SCR-053
def test_rate_limit_without_retry_after_waits_15_seconds(h: Harness) -> None:
    """A rate-limit response without Retry-After waits 15 seconds."""
    h.server.route(OA, "/works", Reply(429, {}), Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall >= 15


# @spec PRIOR-SCR-053
def test_other_failure_waits_only_for_the_next_slot(h: Harness) -> None:
    """Any other failure waits only for the limiter's next slot."""
    h.server.route(OA, "/works", Reply(502, {}), Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    assert h.server.sent[1].wall - h.server.sent[0].wall < 2


# @spec PRIOR-SCR-054, PRIOR-SCR-066, PRIOR-SCR-071
def test_long_retry_after_means_no_retry_and_skips_the_service(h: Harness) -> None:
    """A Retry-After over 60 seconds ends the query and skips the service's remaining queries."""
    h.server.route(OA, "/works", Reply(429, {}, {"Retry-After": "120"}))
    assert h.run("search", "openalex", "a", "b", "c").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == [
        "rate limit",
        "skipped: service throttled",
        "skipped: service throttled",
    ]


# @spec PRIOR-SCR-054, PRIOR-SCR-055, PRIOR-SCR-068
def test_5xx_with_long_retry_after_gets_no_retry(h: Harness) -> None:
    """A 5xx whose Retry-After exceeds 60 seconds is sent once and ends as network."""
    h.server.route(OA, "/works", Reply(502, {}, {"Retry-After": "300"}))
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["network"]


# @spec PRIOR-SCR-050, PRIOR-SCR-113
@pytest.mark.parametrize(
    ("action", "service", "host", "path", "query", "sends"),
    [
        ("search", "arxiv", AX, "/api/query", "q", 2),
        ("search", "openalex", OA, "/works", "q", 2),
        ("lookup", "semanticscholar", S2, S2_MATCH, TITLE, 7),
        ("recommend", "semanticscholar", S2, S2_RECOMMEND, SEED, 7),
    ],
)
def test_attempts_per_request_by_service(  # noqa: PLR0913, PLR0917
    h: Harness, action: str, service: str, host: str, path: str, query: str, sends: int
) -> None:
    """A request that keeps failing is sent twice on arXiv and OpenAlex, 7 times on S2."""
    h.settings(S2_KEY)  # S2's 1-second slots, so the 60-second cap can't cut the attempts short
    h.server.route(host, path, Reply(500, {}))
    assert h.run(action, service, query).code == 3
    assert len(h.server.sent) == sends
    assert h.outcomes() == ["network"]


# Jitter drawn for each retry in turn: a distinct value per call, each within 0 to 0.75.
JITTERS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]


# @spec PRIOR-SCR-111, PRIOR-SCR-050, PRIOR-SCR-053, PRIOR-SCR-113
@pytest.mark.parametrize(
    ("reply", "outcome"),
    [
        (Reply(500, {}), "network"),
        (Reply(429, {}), "rate limit"),
        (Reply(error=requests.ConnectionError("reset")), "network"),
        (Reply(500, {}, latency=2.0), "network"),
    ],
    ids=["500", "429", "connection-error", "500-after-2-seconds"],
)
def test_semantic_scholar_backoff_grows_and_is_capped_after_jitter(
    h: Harness, monkeypatch: pytest.MonkeyPatch, reply: Reply, outcome: str
) -> None:
    """Each retry waits min(15, 1.5 x 1.6^r + j) after the failed response arrived."""
    drawn: list[tuple[float, float]] = []

    def uniform(a: float, b: float) -> float:
        drawn.append((a, b))
        return JITTERS[len(drawn) - 1]

    monkeypatch.setattr(h.module, "_uniform", uniform)
    h.settings(S2_KEY)  # 1 request a second, so the limiter never decides a retry's time
    h.server.route(S2, S2_MATCH, reply)
    h.run("lookup", "semanticscholar", TITLE)
    assert len(h.server.sent) == 7
    assert drawn == [(0, 0.75)] * 6
    # Send to send is the response's latency plus the backoff timed from its arrival. The last
    # retry's base, 1.5 x 1.6^5 = 15.73, is over the cap, so its jitter is capped away too.
    expected = [reply.latency + _backoff(r, j) for r, j in enumerate(JITTERS)]
    assert expected[-1] == reply.latency + 15.0
    assert _gaps(h.server.sent) == pytest.approx(expected, abs=0.01)
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-111, PRIOR-SCR-041
def test_semantic_scholar_backoff_overlaps_the_limiter_slot(h: Harness) -> None:
    """Without a key, a retry goes at the later of its backoff and the next 8-second slot."""
    h.server.route(S2, S2_MATCH, Reply(500, {}))
    h.run("lookup", "semanticscholar", TITLE)
    expected = [max(8.0, _backoff(r, 0.0)) for r in range(6)]
    assert expected[:4] == [8.0] * 4
    assert _gaps(h.server.sent) == pytest.approx(expected, abs=0.01)


# @spec PRIOR-SCR-111, PRIOR-SCR-052
def test_semantic_scholar_later_retry_after_wins(h: Harness) -> None:
    """A Retry-After ending after the backoff governs; one ending before it doesn't."""
    h.settings(S2_KEY)
    h.server.route(
        S2,
        S2_MATCH,
        Reply(429, {}, {"Retry-After": "5"}),
        Reply(500, {}),
        Reply(429, {}, {"Retry-After": "1"}),
        Reply(200, s2_title_match()),
    )
    assert h.run("lookup", "semanticscholar", TITLE).code == 0
    assert _gaps(h.server.sent) == pytest.approx([5.0, 2.4, 3.84], abs=0.01)
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-112, PRIOR-SCR-055, PRIOR-SCR-066, PRIOR-SCR-070
@pytest.mark.parametrize(
    ("limiter", "replies", "sends", "outcome"),
    [
        (
            "keyed",
            [
                Reply(429, {}, {"Retry-After": "50"}),
                Reply(429, {}, {"Retry-After": "20"}),
                Reply(200, s2_title_match()),
            ],
            2,
            "rate limit",
        ),
        ("keyed", [Reply(500, {}, {"Retry-After": "25"})], 3, "network"),
        (
            "keyed",
            [
                Reply(429, {}, {"Retry-After": "30"}),
                Reply(429, {}, {"Retry-After": "30"}),
                Reply(200, s2_title_match()),
            ],
            3,
            "ok",
        ),
        # The first response arrives 2 s after its send; the third send, at 61 s, is 59 s after
        # that arrival, so it goes.
        (
            "keyed",
            [
                Reply(429, {}, {"Retry-After": "30"}, latency=2.0),
                Reply(429, {}, {"Retry-After": "27"}, latency=2.0),
                Reply(200, s2_title_match(), latency=2.0),
            ],
            3,
            "ok",
        ),
        # The second wait ends at 59 s, but the next 8-second slot is at 63 s.
        (
            "anonymous",
            [
                Reply(429, {}, {"Retry-After": "55"}),
                Reply(429, {}, {"Retry-After": "4"}),
                Reply(200, s2_title_match()),
            ],
            2,
            "rate limit",
        ),
    ],
    ids=[
        "retry-after-50-then-20",
        "slow-500s",
        "exactly-60-seconds",
        "measured-from-arrival",
        "crossed-by-limiter-slot",
    ],
)
def test_semantic_scholar_sends_no_retry_after_60_seconds(
    h: Harness, limiter: str, replies: list[Reply], sends: int, outcome: str
) -> None:
    """No retry goes more than 60 seconds after the first response; the failure decides."""
    if limiter == "keyed":
        h.settings(S2_KEY)
    h.server.route(S2, S2_MATCH, *replies)
    h.run("lookup", "semanticscholar", TITLE)
    assert len(h.server.sent) == sends
    first_arrival = h.server.sent[0].wall + replies[0].latency
    assert all(s.wall - first_arrival <= 60 for s in h.server.sent)
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-054, PRIOR-SCR-066, PRIOR-SCR-071, PRIOR-SCR-113
def test_semantic_scholar_long_retry_after_means_no_retry(h: Harness) -> None:
    """A Retry-After over 60 seconds on a lookup ends it as rate limit and skips the rest."""
    h.server.route(S2, S2_MATCH, Reply(429, {}, {"Retry-After": "61"}))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["rate limit", "skipped: service throttled"]


# @spec PRIOR-SCR-113, PRIOR-SCR-082, PRIOR-SCR-084
def test_recommend_retry_is_logged_like_a_connector_request(h: Harness) -> None:
    """The harvester's own resend is logged, timed and saved like any other attempt."""
    h.settings(S2_KEY)
    h.server.route(
        S2, S2_RECOMMEND, Reply(500, {"error": "busy"}), Reply(200, s2_recommendations(1))
    )
    assert h.run("recommend", "semanticscholar", SEED).code == 0
    (logged,) = h.queries()
    assert (logged["service"], logged["route"], logged["action"], logged["outcome"]) == (
        "semanticscholar",
        "Semantic Scholar",
        "recommend",
        "ok",
    )
    first, second = logged["attempts"]
    assert (first["status"], second["status"]) == (500, 200)
    assert all(S2_RECOMMEND in a["url"] for a in (first, second))
    assert second["wait"] == pytest.approx(1.5, abs=0.01)
    qid = logged["id"]
    names = sorted(p.name for p in (h.run_dir / "raw").iterdir())
    assert names == [f"{qid}-1-1.json", f"{qid}-1-2.json"]


# @spec PRIOR-SCR-114
@pytest.mark.parametrize(
    ("seed", "sent_as"),
    [
        (SEED, f"DOI:{SEED}"),
        (f"doi:{SEED}", f"DOI:{SEED}"),
        (f"DOI:{SEED}", f"DOI:{SEED}"),
        (f"Doi:{SEED}", f"DOI:{SEED}"),
        (f"https://doi.org/{SEED}", f"DOI:{SEED}"),
        (f"https://dx.doi.org/{SEED}", f"DOI:{SEED}"),
        (f"http://doi.org/{SEED}", f"DOI:{SEED}"),
        (f"http://dx.doi.org/{SEED}", f"DOI:{SEED}"),
        (
            "10.1002/(SICI)1097-4571(199806)49:8<693::AID-ASI4>3.0.CO;2-0",
            "DOI:10.1002/%28SICI%291097-4571%28199806%2949:8%3C693::AID-ASI4%3E3.0.CO%3B2-0",
        ),
        ("2401.12345", "arXiv:2401.12345"),
        ("2401.12345v2", "arXiv:2401.12345"),
        ("0704.0001", "arXiv:0704.0001"),
        ("arXiv:2401.12345v2", "arXiv:2401.12345"),
        ("ARXIV:2401.12345", "arXiv:2401.12345"),
        ("arxiv:0704.0001v12", "arXiv:0704.0001"),
        ("arXiv:2401.12345V3", "arXiv:2401.12345"),
        (" 2401.12345 ", "arXiv:2401.12345"),
        ("\tdoi:10.1234/abc\n", "DOI:10.1234/abc"),
        (
            "649def34f8be52c8b66281af98ae884c09aef38b",
            "649def34f8be52c8b66281af98ae884c09aef38b",
        ),
        (
            "649DEF34F8BE52C8B66281AF98AE884C09AEF38B",
            "649def34f8be52c8b66281af98ae884c09aef38b",
        ),
    ],
)
def test_recommend_seed_forms(h: Harness, seed: str, sent_as: str) -> None:
    """Each seed form goes to its forpaper path, percent-encoded except for : and /."""
    h.server.route(S2, S2_RECOMMEND, Reply(200, s2_recommendations(2)))
    assert h.run("recommend", "semanticscholar", seed).code == 0
    (sent,) = h.server.sent
    path = re.sub(r"%[0-9a-fA-F]{2}", lambda m: m[0].upper(), sent.path)
    assert path == S2_RECOMMEND + sent_as
    assert sent.query["from"] == ["all-cs"]
    assert sent.query["limit"] == ["100"]


# @spec PRIOR-SCR-114, PRIOR-SCR-083
def test_recommendations_become_harvest_records(h: Harness) -> None:
    """Each recommended paper becomes a harvest record, a sparse one included."""
    body = {"recommendedPapers": [s2_paper(1), s2_paper(2), s2_paper(3), s2_sparse_paper(4)]}
    h.server.route(S2, S2_RECOMMEND, Reply(200, body))
    assert h.run("recommend", "semanticscholar", SEED).code == 0
    records = jsonl(h.run_dir / "records.jsonl")
    assert [r["service_id"] for r in records] == ["s2paper1", "s2paper2", "s2paper3", "s2paper4"]
    assert [r["rank"] for r in records] == [1, 2, 3, 4]
    assert (records[0]["title"], records[0]["doi"], records[0]["citations"]) == (
        "Semantic Scholar paper 1",
        "10.5555/s21",
        49,
    )
    sparse = records[3]
    assert sparse["title"] == "Semantic Scholar paper 4"
    for name in ("abstract", "year", "doi"):
        assert not sparse.get(name), name
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-114, PRIOR-SCR-116
@pytest.mark.parametrize(
    ("action", "path", "reply", "query", "papers"),
    [
        ("recommend", S2_RECOMMEND, Reply(200, s2_recommendations(3)), SEED, 3),
        ("lookup", S2_MATCH, Reply(200, s2_title_match()), TITLE, 1),
    ],
)
def test_papers_are_parsed_by_the_connectors_parser(  # noqa: PLR0913, PLR0917
    h: Harness,
    monkeypatch: pytest.MonkeyPatch,
    action: str,
    path: str,
    reply: Reply,
    query: str,
    papers: int,
) -> None:
    """Each paper goes through the Semantic Scholar connector's own parser, once."""
    real = semantic.SemanticSearcher._parse_paper  # noqa: SLF001
    parsed: list[object] = []

    def spy(self: semantic.SemanticSearcher, item: Any) -> object:  # noqa: ANN401
        parsed.append(item.get("paperId"))
        return real(self, item)

    monkeypatch.setattr(semantic.SemanticSearcher, "_parse_paper", spy)
    h.server.route(S2, path, reply)
    assert h.run(action, "semanticscholar", query).code == 0
    assert len(parsed) == papers
    assert len(jsonl(h.run_dir / "records.jsonl")) == papers


# @spec PRIOR-SCR-114, PRIOR-SCR-115
@pytest.mark.parametrize(
    "seed",
    [
        "Attention is all you need",
        "W2741809807",
        "hep-th/9901001",
        "arXiv:hep-th/9901001",
        "ARXIV:hep-th/9901001",
        "2401.123456",
        "12345",
        "arXiv:",
        "https://arxiv.org/abs/2401.12345",
        "https://example.org/10.1145/3368089.3409741",
        "649def34f8be52c8b66281af98ae884c09aef38",
        "649def34f8be52c8b66281af98ae884c09aef38bb",
        "649def34f8be52c8b66281af98ae884c09aef3zz",
        # DOI URLs with a query string or fragment, which the citations lookup refuses too.
        "https://doi.org/10.1234/abc?utm=x",
        "https://doi.org/10.1234/abc#section",
        # Dot segments, which requests would resolve into another endpoint's path.
        "10.1234/../../../graph/v1/paper/search",
        "doi:10.1234/a/./b",
        "https://doi.org/10.1234/..",
        # Digits outside ASCII, which a bare `\d` would accept.
        "2021.00001".translate(ARABIC_INDIC_DIGITS),
        "10." + "1234".translate(ARABIC_INDIC_DIGITS) + "/x",
    ],
)
def test_invalid_seed_is_invalid_input(h: Harness, seed: str) -> None:
    """A seed in none of the accepted forms is invalid input and sends nothing."""
    h.server.route(S2, S2_RECOMMEND, Reply(200, s2_recommendations(1)))
    assert h.run("recommend", "semanticscholar", seed).code == 3
    assert h.outcomes() == ["invalid input"]
    assert h.server.sent == []


class _KeyRecorder(dict[str, Any]):
    """A paper that records every key read from it."""

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)
        self.read: set[str] = set()

    @override
    def __getitem__(self, key: str) -> Any:
        self.read.add(key)
        return super().__getitem__(key)

    @override
    def get(self, key: str, default: Any = None, /) -> Any:  # ty: ignore[incompatible-method-override] - dict.get's overloads
        self.read.add(key)
        return super().get(key, default)

    @override
    def __contains__(self, key: object) -> bool:
        self.read.add(str(key))
        return super().__contains__(key)


def _parser_fields() -> set[str]:
    """The keys of a paper that the Semantic Scholar connector's `_parse_paper` reads.

    The keys it names in its source, found by walking its syntax tree, together with the keys it
    reads at run time from a fully populated paper.
    """
    parse = semantic.SemanticSearcher._parse_paper  # noqa: SLF001
    tree = ast.parse(textwrap.dedent(inspect.getsource(parse)))
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    item = function.args.args[1].arg  # the parameter after self
    fields: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == item
            and node.args
            and isinstance(node.args[0], ast.Constant)
        ):
            fields.add(str(node.args[0].value))
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == item
            and isinstance(node.slice, ast.Constant)
        ):
            fields.add(str(node.slice.value))
    full = {
        **s2_paper(1),
        "venue": "ICSE",
        "fieldsOfStudy": ["Computer Science"],
        "openAccessPdf": {"url": "https://example.org/p.pdf", "disclaimer": "Open access."},
    }
    probe = _KeyRecorder(full)
    assert parse(object.__new__(semantic.SemanticSearcher), probe) is not None
    return fields | probe.read


# @spec PRIOR-SCR-122
@pytest.mark.parametrize(
    ("action", "path", "reply", "query"),
    [
        ("lookup", S2_MATCH, Reply(200, s2_title_match()), TITLE),
        ("recommend", S2_RECOMMEND, Reply(200, s2_recommendations(1)), SEED),
    ],
)
def test_requests_ask_for_every_field_the_parser_reads(
    h: Harness, action: str, path: str, reply: Reply, query: str
) -> None:
    """Both requests ask for each field the connector's parser reads."""
    needed = _parser_fields()
    assert {"title", "authors", "externalIds", "citationCount"} <= needed
    h.server.route(S2, path, reply)
    assert h.run(action, "semanticscholar", query).code == 0
    (sent,) = h.server.sent
    (fields,) = sent.query["fields"]
    assert needed <= set(fields.split(","))


# @spec PRIOR-SCR-116, PRIOR-SCR-083
def test_lookup_sends_the_trimmed_title_and_records_the_match(h: Harness) -> None:
    """A lookup sends its trimmed title, and its record carries the matched title and score."""
    h.server.route(S2, S2_MATCH, Reply(200, s2_title_match(4, score=161.8)))
    assert h.run("lookup", "semanticscholar", f"  {TITLE} \t").code == 0
    (sent,) = h.server.sent
    assert sent.path == S2_MATCH
    assert sent.query["query"] == [TITLE]
    (record,) = jsonl(h.run_dir / "records.jsonl")
    assert (record["title"], record["service_id"]) == ("Semantic Scholar paper 4", "s2paper4")
    assert record["match_score"] == 161.8
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-062, PRIOR-SCR-074, PRIOR-SCR-116
@pytest.mark.parametrize(
    ("body", "outcome", "code"),
    [
        (s2_no_match(), "empty", 0),
        (
            {"error": "Paper with id 649def34f8be52c8b66281af98ae884c09aef38b not found"},
            "client error",
            3,
        ),
        (b"", "client error", 3),
    ],
    ids=["no-match", "other-404", "empty-404"],
)
def test_lookup_404s(h: Harness, body: bytes | dict[str, object], outcome: str, code: int) -> None:
    """The no-match 404 ran and found nothing; any other lookup 404 is a client error."""
    h.server.route(S2, S2_MATCH, Reply(404, body))
    assert h.run("lookup", "semanticscholar", TITLE).code == code
    assert len(h.server.sent) == 1
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-057
@pytest.mark.parametrize(
    ("query", "refused"),
    [
        ("a AND b AND c AND d AND e AND f", False),
        ("a AND b OR c NOT d AND e OR f AND g", True),
        ('"x AND y" AND a OR b NOT c AND d OR e', True),
        ("ANDROID OR and or not NOT", False),
    ],
)
def test_openalex_boolean_operator_cap(h: Harness, query: str, refused: bool) -> None:  # noqa: FBT001
    """More than 5 capitalised operators in total make a query invalid input."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", query)
    assert (h.outcomes() == ["invalid input"]) is refused
    assert (h.server.sent == []) is refused


# @spec PRIOR-SCR-058
@pytest.mark.parametrize(
    ("paper", "seed"),
    [
        ("10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("doi:10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("https://doi.org/10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("https://dx.doi.org/10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("W2741809807", "/works/W2741809807"),
        ("https://openalex.org/W2741809807", "/works/W2741809807"),
        ("Attention is all you need", None),
        ("https://example.org/W1", None),
    ],
)
def test_relations_paper_id_forms(h: Harness, paper: str, seed: str | None) -> None:
    """Accepted ID forms look up their seed; others are invalid input and send nothing."""
    h.server.route(OA, "/works/", Reply(200, {"id": "https://openalex.org/W2741809807"}))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("references", "openalex", paper)
    if seed is None:
        assert h.outcomes() == ["invalid input"]
        assert h.server.sent == []
    else:
        assert h.outcomes() == ["ok"]
        assert h.server.sent[0].url.split("?")[0].endswith(seed)


# Outcomes -----------------------------------------------------------------------------------


# @spec PRIOR-SCR-060, PRIOR-SCR-066
@pytest.mark.parametrize(
    "reply",
    [
        Reply(429, {}),
        Reply(503, {}),
        Reply(403, {}, {"Retry-After": "not a number"}),
        Reply(403, {}, {"x-ratelimit-remaining": "0"}),
        Reply(403, {}, {"X-Rate-Limit-Remaining": "0"}),
        Reply(403, {"message": "Too Many Requests"}),
        Reply(403, {"message": "daily QUOTA exceeded"}),
    ],
)
def test_rate_limit_responses(h: Harness, reply: Reply) -> None:
    """Each form of rate-limit response gets one retry and then the outcome rate limit."""
    h.server.route(OA, "/works", reply)
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["rate limit"]


# @spec PRIOR-SCR-060, PRIOR-SCR-062
def test_arxiv_rate_exceeded_with_200_is_not_a_result(h: Harness) -> None:
    """An arXiv 200 with a 'Rate exceeded' body is a rate-limit response, not an empty result."""
    h.server.route(AX, "/api/query", Reply(200, "  rate EXCEEDED.\n"), Reply(200, arxiv_feed(2)))
    assert h.run("search", "arxiv", "q").code == 0
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-061, PRIOR-SCR-067
@pytest.mark.parametrize("reply", [Reply(401, {}), Reply(403, {"message": "Forbidden"})])
def test_authentication_failures_are_not_retried(h: Harness, reply: Reply) -> None:
    """A 401, or a 403 that isn't a rate limit, is sent once."""
    h.server.route(OA, "/works", reply)
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["authentication"]


# @spec PRIOR-SCR-062, PRIOR-SCR-063, PRIOR-SCR-068
def test_connector_empty_list_after_a_failure_is_not_empty(h: Harness) -> None:
    """OpenAlex returns [] after a 500; the outcome is still network."""
    h.server.route(OA, "/works", Reply(500, {}))
    assert h.run("search", "openalex", "q").code == 3
    assert h.outcomes() == ["network"]


# @spec PRIOR-SCR-062, PRIOR-SCR-068
def test_unparseable_2xx_body_is_network(h: Harness) -> None:
    """A 200 whose body isn't JSON is retried once and ends as network."""
    h.server.route(OA, "/works", Reply(200, "<html>maintenance</html>"))
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["network"]


# @spec PRIOR-SCR-062
@pytest.mark.parametrize(("body", "outcome"), [(arxiv_feed(2), "ok"), (arxiv_feed(0), "network")])
def test_arxiv_406_counts_only_when_the_connector_accepts_it(
    h: Harness, body: str, outcome: str
) -> None:
    """A 406 feed the arXiv connector accepts is usable; an empty one isn't."""
    h.server.route(AX, "/api/query", Reply(406, body))
    h.run("search", "arxiv", "q")
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-063, PRIOR-SCR-064
@pytest.mark.parametrize(
    ("reply", "outcome"),
    [(Reply(200, openalex_page(2)), "ok"), (Reply(200, openalex_page(0)), "empty")],
)
def test_ok_and_empty(h: Harness, reply: Reply, outcome: str) -> None:
    """A query that ran is ok with results and empty without."""
    h.server.route(OA, "/works", reply)
    assert h.run("search", "openalex", "q").code == 0
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-063, PRIOR-SCR-074
def test_first_failed_request_decides_a_multi_request_outcome(h: Harness) -> None:
    """A citations query whose second page gets a 400 ends as client error."""
    h.server.route(OA, "/works/W7", Reply(200, {"id": "https://openalex.org/W7"}))
    h.server.route(
        OA,
        "/works",
        Reply(200, openalex_page(100, total=300)),
        Reply(400, {"error": "bad page"}),
        params={"filter": "cites:W7"},
    )
    assert h.run("citations", "openalex", "W7", extra=("--max-results", "300")).code == 3
    assert h.outcomes() == ["client error"]


# @spec PRIOR-SCR-064, PRIOR-SCR-073
def test_truncated_snowball_still_ran(h: Harness) -> None:
    """A references query stopped by the page budget is ok, and says it was truncated."""
    h.server.route(OA, "/works/W7", Reply(200, {"id": "https://openalex.org/W7"}))
    # Repeated pages keep the connector deduplicating until its five-page budget runs out.
    h.server.route(
        OA, "/works", Reply(200, openalex_page(100, total=1000)), params={"filter": "cited_by:W7"}
    )
    result = h.run("references", "openalex", "W7", extra=("--max-results", "500"))
    assert result.code == 0
    (logged,) = h.queries()
    assert logged["outcome"] == "ok"
    assert logged["truncated"] == "page_budget"
    head = next(line for line in result.out.splitlines() if str(logged["id"]) in line)
    assert "truncated" in head


# @spec PRIOR-SCR-073
def test_stop_at_max_results_is_not_truncation(h: Harness) -> None:
    """A query that stops at --max-results isn't reported as truncated."""
    h.server.route(OA, "/works/W7", Reply(200, {"id": "https://openalex.org/W7"}))
    h.server.route(
        OA, "/works", Reply(200, openalex_page(100, total=300)), params={"filter": "cites:W7"}
    )
    result = h.run("citations", "openalex", "W7", extra=("--max-results", "100"))
    (logged,) = h.queries()
    assert not logged.get("truncated")
    assert "truncated" not in result.out


# @spec PRIOR-SCR-065
def test_missing_paper_is_not_found(h: Harness) -> None:
    """A 404 on the seed lookup is not found."""
    h.server.route(OA, "/works/", Reply(404, {"error": "no such work"}))
    assert h.run("citations", "openalex", "10.9999/none").code == 3
    assert h.outcomes() == ["not found"]


# @spec PRIOR-SCR-065, PRIOR-SCR-087
def test_unknown_recommend_seed_is_not_found(h: Harness) -> None:
    """A 404 for a recommend seed is not found, sent once, and faults no route."""
    missing = {"error": "Paper with id DOI:10.9999/none not found"}
    h.server.route(S2, S2_RECOMMEND, Reply(404, missing))
    assert h.run("recommend", "semanticscholar", "10.9999/none").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["not found"]
    assert h.ledger() == []


# @spec PRIOR-SCR-063, PRIOR-SCR-113
@pytest.mark.parametrize(
    ("replies", "outcome"),
    [
        (
            [
                Reply(429, {}),
                Reply(500, {}),
                Reply(429, {}),
                Reply(504, {}, {"Retry-After": "300"}),
            ],
            "network",
        ),
        (
            [
                Reply(500, {}),
                Reply(429, {}),
                Reply(504, {}),
                Reply(429, {}, {"Retry-After": "120"}),
            ],
            "rate limit",
        ),
    ],
    ids=["ends-504", "ends-429"],
)
def test_last_attempt_decides_mixed_failures(
    h: Harness, replies: list[Reply], outcome: str
) -> None:
    """A request whose attempts failed in different ways is judged by its last attempt."""
    h.server.route(S2, S2_MATCH, *replies)
    assert h.run("lookup", "semanticscholar", TITLE).code == 3
    assert len(h.server.sent) == 4
    assert h.outcomes() == [outcome]


# @spec PRIOR-SCR-119, PRIOR-SCR-088
@pytest.mark.parametrize("status", [500, 502, 504])
def test_semantic_scholar_5xx_stops_the_service(h: Harness, status: int) -> None:
    """A lookup that ends network on a 5xx skips S2's later queries, diagnosed as network."""
    h.server.route(S2, S2_MATCH, Reply(status, {}))
    assert h.run("lookup", "semanticscholar", "a", "b", "c").code == 3
    # Anonymous, so the send count is what the 8-second slots leave under the 60-second cap.
    assert len(h.server.sent) == _anonymous_sends()
    assert h.outcomes() == [
        "network",
        "skipped: service throttled",
        "skipped: service throttled",
    ]
    (record,) = h.ledger()
    assert (record["state"], record["reason"]) == ("unavailable", "network")


# @spec PRIOR-SCR-119, PRIOR-SCR-060, PRIOR-SCR-071, PRIOR-SCR-088
def test_semantic_scholar_503_follows_the_rate_limit_path(h: Harness) -> None:
    """A 503 on every attempt is a rate limit, not the network stop."""
    h.server.route(S2, S2_MATCH, Reply(503, {}))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 3
    # Anonymous, so the send count is what the 8-second slots leave under the 60-second cap.
    assert len(h.server.sent) == _anonymous_sends()
    assert h.outcomes() == ["rate limit", "skipped: service throttled"]
    (record,) = h.ledger()
    assert record["reason"] == "rate limit, no key set"


# @spec PRIOR-SCR-119
def test_semantic_scholar_connection_errors_do_not_stop_the_service(h: Harness) -> None:
    """Only a 5xx on the last attempt stops the service; a connection error doesn't."""
    reset = Reply(error=requests.ConnectionError("reset"))
    h.settings(S2_KEY)
    h.server.route(S2, S2_MATCH, *[reset] * 7, Reply(200, s2_title_match()))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 3
    assert len(h.server.sent) == 8
    assert h.outcomes() == ["network", "ok"]


# @spec PRIOR-SCR-119
def test_semantic_scholar_5xx_before_the_last_attempt_does_not_stop_the_service(
    h: Harness,
) -> None:
    """A query whose 5xx attempts end in a connection error doesn't stop the service."""
    h.settings(S2_KEY)
    reset = Reply(error=requests.ConnectionError("reset"))
    h.server.route(S2, S2_MATCH, *[Reply(500, {})] * 6, reset, Reply(200, s2_title_match()))
    assert h.run("lookup", "semanticscholar", "a", "b").code == 3
    assert [s.query["query"][0] for s in h.server.sent] == ["a"] * 7 + ["b"]
    assert h.outcomes() == ["network", "ok"]


TEXT_BODY = {"Content-Type": "text/plain"}
BUDGET_REPLIES = [
    Reply(429, {"error": "Insufficient budget for this request"}),
    Reply(429, {"error": "Daily BUDGET exhausted"}),
    Reply(429, {"error": "Please consider a plan upgrade"}),
    Reply(429, {"error": "PLAN UPGRADE required"}),
    Reply(429, {"message": "Insufficient budget for this request"}),
    Reply(429, {"message": "Plan Upgrade required"}),
    Reply(429, "Daily budget exhausted; consider a plan upgrade.", TEXT_BODY),
]


# @spec PRIOR-SCR-117, PRIOR-SCR-118, PRIOR-SCR-055, PRIOR-SCR-066, PRIOR-SCR-071
# @spec PRIOR-SCR-082, PRIOR-SCR-088
@pytest.mark.parametrize(
    "reply",
    BUDGET_REPLIES,
    ids=[
        "error-budget",
        "error-budget-caps",
        "error-plan-upgrade",
        "error-plan-upgrade-caps",
        "message-budget",
        "message-plan-upgrade",
        "plain-text",
    ],
)
def test_openalex_budget_response_ends_openalex_without_a_retry(h: Harness, reply: Reply) -> None:
    """An OpenAlex budget 429 isn't retried, ends rate limit for its budget, and skips the rest."""
    h.server.route(OA, "/works", reply)
    assert h.run("search", "openalex", "a", "b").code == 3
    assert len(h.server.sent) == 1
    first, second = h.queries()
    assert (first["outcome"], first["reason"]) == ("rate limit", "daily budget")
    assert second["outcome"] == "skipped: service throttled"
    (record,) = h.ledger()
    assert (record["state"], record["reason"]) == ("unavailable", "rate limit (daily budget)")


# @spec PRIOR-SCR-118, PRIOR-SCR-070, PRIOR-SCR-088
def test_spent_budget_refuses_openalex_in_later_invocations(h: Harness) -> None:
    """A later process on the same run directory refuses every OpenAlex request unsent."""
    h.server.route(OA, "/works", Reply(429, {"error": "Insufficient budget"}))
    h.run("search", "openalex", "a")
    # A lone budget rate limit decides the diagnosis too, with no skipped query after it.
    first = h.ledger()[-1]
    assert (first["state"], first["reason"]) == ("unavailable", "rate limit (daily budget)")
    h.reload()
    assert h.run("search", "openalex", "b").code == 3
    assert h.ledger()[-1]["reason"] == "rate limit (daily budget)"
    assert h.run("citations", "openalex", "W7").code == 3
    assert len(h.server.sent) == 1
    for later in h.queries()[1:]:
        assert (later["outcome"], later["reason"]) == ("refused", "daily budget")


# @spec PRIOR-SCR-118
def test_spent_budget_record_survives_a_key_rejection(h: Harness) -> None:
    """Recording a rejected key later never removes the budget record."""
    h.settings(S2_KEY)
    h.server.route(OA, "/works", Reply(429, {"error": "Insufficient budget"}))
    h.server.route(S2, S2_MATCH, Reply(401, {"message": "invalid key"}))
    h.run("search", "openalex", "a")
    h.reload()
    assert h.run("lookup", "semanticscholar", TITLE).code == 3
    assert h.outcomes()[-1] == "authentication"
    h.reload()
    h.run("search", "openalex", "b")
    assert len(h.server.to(OA)) == 1
    last = h.queries()[-1]
    assert (last["outcome"], last["reason"]) == ("refused", "daily budget")


# @spec PRIOR-SCR-070
def test_rejected_key_outranks_spent_budget(h: Harness) -> None:
    """With OpenAlex's key rejected and its budget spent, the refusal names the key."""
    h.settings('[openalex]\napi_key = "oa-key"\n')
    h.server.route(OA, "/works", Reply(429, {"error": "Insufficient budget"}))
    h.run("search", "openalex", "a")
    # Once the budget is spent no OpenAlex request is sent, so no 401 can record the rejection;
    # record it the way the harvester does, through its run directory.
    h.module.RunDir(h.run_dir, h.module.Redactor({})).reject("openalex")
    h.reload()
    assert h.run("search", "openalex", "b").code == 3
    last = h.queries()[-1]
    assert (last["outcome"], last["reason"]) == ("refused", "key rejected")


# @spec PRIOR-SCR-062, PRIOR-SCR-055, PRIOR-SCR-113
@pytest.mark.parametrize(
    ("action", "path", "query", "body"),
    [
        ("recommend", S2_RECOMMEND + "arXiv:2401.12345", "2401.12345", {}),
        ("recommend", S2_RECOMMEND + "arXiv:2401.12345", "2401.12345", {"data": []}),
        ("lookup", S2_MATCH, TITLE, {"recommendedPapers": []}),
        ("lookup", S2_MATCH, TITLE, [1, 2]),
    ],
)
def test_semantic_scholar_body_without_its_list_is_unparsable(
    h: Harness, action: str, path: str, query: str, body: dict[str, Any] | list[Any]
) -> None:
    """A 200 without the action's list of papers is retried like any unparsable body."""
    h.settings(S2_KEY)
    h.server.route(S2, path, Reply(200, body), Reply(200, body), Reply(200, body), Reply(200, {}))
    assert h.run(action, "semanticscholar", query).code == 3
    assert h.outcomes() == ["network"]
    assert len(h.server.to(S2)) == 7


# @spec PRIOR-SCR-117, PRIOR-SCR-060
@pytest.mark.parametrize(
    "reply",
    [Reply(429, {"error": "Too many requests"}), Reply(503, {"error": "Insufficient budget"})],
    ids=["429-without-budget-words", "503-with-budget-words"],
)
def test_other_openalex_rate_limits_are_retried_once(h: Harness, reply: Reply) -> None:
    """Only a 429 that names the budget is a budget response; others get their one retry."""
    h.server.route(OA, "/works", reply, reply, Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 2
    (logged,) = h.queries()
    assert (logged["outcome"], logged["reason"]) == ("rate limit", None)
    h.reload()
    assert h.run("search", "openalex", "r").code == 0


# @spec PRIOR-SCR-117
def test_semantic_scholar_budget_words_are_an_ordinary_rate_limit(h: Harness) -> None:
    """The budget response is OpenAlex's; a Semantic Scholar 429 naming a budget is retried."""
    h.server.route(
        S2, S2_MATCH, Reply(429, {"error": "budget exceeded"}), Reply(200, s2_title_match())
    )
    assert h.run("lookup", "semanticscholar", TITLE).code == 0
    assert len(h.server.sent) == 2
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-068
@pytest.mark.parametrize(
    "reply",
    [
        Reply(error=requests.ConnectionError("reset")),
        Reply(error=requests.Timeout("slow")),
        Reply(502, {}),
    ],
)
def test_network_failures(h: Harness, reply: Reply) -> None:
    """Connection errors, timeouts and 5xx responses end as network after one retry."""
    h.server.route(OA, "/works", reply)
    assert h.run("search", "openalex", "a", "b").code == 3
    assert len(h.server.sent) == 4
    assert h.outcomes() == ["network", "network"]


# @spec PRIOR-SCR-069
def test_limiter_wait_is_not_service_throttling(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A limiter wait over the cap sends nothing and doesn't skip the service's other queries."""

    def busy(*_a: object, **_k: object) -> None:
        msg = "next request slot is 900 s away"
        raise http_limits.RateLimited(msg)

    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    monkeypatch.setattr(http_limits, "acquire", busy)
    assert h.run("search", "openalex", "a", "b").code == 3
    assert h.server.sent == []
    assert h.outcomes() == ["not sent: limiter wait", "not sent: limiter wait"]


# @spec PRIOR-SCR-074
@pytest.mark.parametrize("status", [400, 404, 422])
def test_other_4xx_is_client_error(h: Harness, status: int) -> None:
    """Any other 4xx on a search is client error, sent once."""
    h.server.route(OA, "/works", Reply(status, {"error": "bad"}))
    assert h.run("search", "openalex", "q").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["client error"]


# @spec PRIOR-SCR-075, PRIOR-SCR-092
def test_internal_error_after_a_request_exits_3(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unexpected exception marks that query and the rest, logs it and exits 3."""

    def boom(self: openalex.OpenAlexSearcher, *_a: object, **_k: object) -> None:
        self.session.get("https://api.openalex.org/works")
        msg = "unexpected"
        raise ZeroDivisionError(msg)

    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", boom)
    assert h.run("search", "openalex", "a", "b").code == 3
    assert h.outcomes() == ["internal error", "internal error"]
    assert "ZeroDivisionError" in (h.run_dir / "harvest.log").read_text()


# @spec PRIOR-SCR-075, PRIOR-SCR-092
def test_internal_error_before_any_request_exits_4(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unexpected exception before anything was sent exits 4, so a fallback repeats nothing."""

    def boom(*_a: object, **_k: object) -> None:
        msg = "unexpected"
        raise ZeroDivisionError(msg)

    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", boom)
    assert h.run("search", "openalex", "a").code == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-076
def test_connector_rejecting_usable_responses_is_network(h: Harness) -> None:
    """A seed lookup that returns JSON without a work ID ends as network, not empty."""
    h.server.route(OA, "/works/W7", Reply(200, {"unexpected": True}))
    assert h.run("citations", "openalex", "W7").code == 3
    assert h.outcomes() == ["network"]


# Run directory and output -------------------------------------------------------------------


# @spec PRIOR-SCR-080
def test_invocation_and_query_ids(h: Harness) -> None:
    """Query IDs carry their invocation's ID and number from 1."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", "a", "b")
    h.run("search", "openalex", "c")
    ids = [str(q["id"]) for q in h.queries()]
    assert all(re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{6}-q\d+", i) for i in ids)
    assert [i.rsplit("-q", 1)[1] for i in ids] == ["1", "2", "1"]
    invocations = [i.rsplit("-q", 1)[0] for i in ids]
    assert invocations[0] == invocations[1] != invocations[2]


# @spec PRIOR-SCR-081
def test_shared_files_are_written_under_flock(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each shared file is written while the harvester holds an exclusive lock on it."""
    locked: set[str] = set()
    real = fcntl.flock

    def spy(fd: int, operation: int) -> None:
        if operation & fcntl.LOCK_EX:
            locked.add(Path(f"/proc/self/fd/{fd}").readlink().name)
        real(fd, operation)

    monkeypatch.setattr(fcntl, "flock", spy)
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    h.server.route(OA, "/works", Reply(200, openalex_page(1)), Reply(401, {}))
    h.run("search", "openalex", "a", "b")
    expected = {"queries.jsonl", "records.jsonl", "ledger.jsonl", "harvest.log", "state.json"}
    assert expected <= locked


# @spec PRIOR-SCR-082
def test_query_log_line(h: Harness) -> None:
    """A query's log line has its fields and every attempt."""
    h.server.route(OA, "/works", Reply(429, {}, {"Retry-After": "2"}), Reply(200, openalex_page(2)))
    h.run("search", "openalex", "q", rnd=3)
    (line,) = h.queries()
    keys = {"id", "round", "service", "route", "action", "query", "outcome", "results", "attempts"}
    assert keys <= line.keys()
    assert (line["round"], line["service"], line["route"], line["action"]) == (
        3,
        "openalex",
        "OpenAlex",
        "search",
    )
    assert line["results"] == 2
    first, second = line["attempts"]
    assert {"time", "url", "status", "wait", "refused", "from_memory"} <= first.keys()
    assert (first["status"], second["status"]) == (429, 200)
    assert second["wait"] >= 2


# @spec PRIOR-SCR-083
def test_harvest_records(h: Harness) -> None:
    """Each result becomes a harvest record with its query ID and rank."""
    h.server.route(OA, "/works", Reply(200, openalex_page(2)))
    h.run("search", "openalex", "q")
    records = jsonl(h.run_dir / "records.jsonl")
    assert [r["rank"] for r in records] == [1, 2]
    fields = {"query_id", "title", "authors", "year", "venue", "doi", "arxiv_id"}
    fields |= {"service_id", "abstract", "citations", "url", "pdf_url"}
    assert fields <= records[0].keys()
    assert (records[0]["service_id"], records[0]["doi"]) == ("W1", "10.1234/oa1")
    assert records[0]["query_id"] == h.queries()[0]["id"]


TEXT = {"Content-Type": "text/plain"}
ATOM = {"Content-Type": "application/atom+xml"}


# @spec PRIOR-SCR-084
@pytest.mark.parametrize(
    ("service", "host", "path", "replies", "suffixes"),
    [
        ("openalex", OA, "/works", [Reply(500, {"e": 1}), Reply(200, openalex_page(1))], "jj"),
        (
            "arxiv",
            AX,
            "/api/query",
            [Reply(500, "busy", TEXT), Reply(200, arxiv_feed(1), ATOM)],
            "tx",
        ),
    ],
)
def test_raw_bodies_per_attempt(  # noqa: PLR0913, PLR0917
    h: Harness, service: str, host: str, path: str, replies: list[Reply], suffixes: str
) -> None:
    """Every response body, errors included, is saved by query, request and attempt."""
    extension = {"j": "json", "t": "txt", "x": "xml"}
    h.server.route(host, path, *replies)
    h.run("search", service, "q")
    qid = h.queries()[0]["id"]
    names = sorted(p.name for p in (h.run_dir / "raw").iterdir())
    assert names == [f"{qid}-1-{n}.{extension[s]}" for n, s in enumerate(suffixes, start=1)]


# @spec PRIOR-SCR-084
def test_no_raw_file_without_a_response(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """An attempt that raised or was refused leaves no file."""
    h.server.route(
        OA, "/works", Reply(error=requests.ConnectionError("x")), Reply(200, openalex_page(1))
    )
    h.run("search", "openalex", "a")
    qid = h.queries()[0]["id"]
    assert sorted(p.name for p in (h.run_dir / "raw").iterdir()) == [f"{qid}-1-2.json"]
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", _stray_search("https://x.example/"))
    h.run("search", "openalex", "b")
    assert len(list((h.run_dir / "raw").iterdir())) == 1


# @spec PRIOR-SCR-085
def test_connector_logs_go_only_to_the_log_file(h: Harness) -> None:
    """Connector log lines go to harvest.log, never to standard output or error."""
    h.server.route(OA, "/works", Reply(500, {}))
    result = h.run("search", "openalex", "q")
    assert "OpenAlex search failed" not in result.out + result.err
    assert "OpenAlex search failed" in (h.run_dir / "harvest.log").read_text()


# @spec PRIOR-SCR-086, PRIOR-SCR-087
def test_ledger_record_per_route(h: Harness) -> None:
    """A route with one query that ran is searched."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)), Reply(500, {}))
    h.run("search", "openalex", "a", "b")
    (record,) = h.ledger()
    assert {"route", "state", "queries", "reason", "as_of", "invocation"} <= record.keys()
    assert (record["route"], record["state"]) == ("OpenAlex", "searched")


# @spec PRIOR-SCR-087
def test_invalid_input_only_gives_no_ledger_record(h: Harness) -> None:
    """A route whose queries were all invalid input gets no record."""
    h.run("references", "openalex", "not an id", "nor this")
    assert h.ledger() == []


# @spec PRIOR-SCR-087
def test_client_error_only_gives_no_ledger_record(h: Harness) -> None:
    """A route whose queries were all client errors gets no record."""
    h.server.route(OA, "/works", Reply(400, {}))
    h.run("search", "openalex", "a", "b")
    assert h.ledger() == []


# @spec PRIOR-SCR-087, PRIOR-SCR-088
@pytest.mark.parametrize(
    ("setup", "reply", "diagnosis"),
    [
        ("", Reply(429, {}, {"Retry-After": "120"}), "rate limit, no key set"),
        (
            f'[openalex]\napi_key = "{CANARY}"\n',
            Reply(429, {}, {"Retry-After": "120"}),
            "rate limit",
        ),
        (
            f'[openalex]\napi_key = "{CANARY}"\n',
            Reply(401, {}),
            "authentication: `openalex.api_key` rejected",
        ),
        ("", Reply(401, {}), "authentication"),
        ("", Reply(500, {}), "network"),
    ],
)
def test_unavailable_route_diagnosis(h: Harness, setup: str, reply: Reply, diagnosis: str) -> None:
    """An unavailable route's diagnosis comes from its failed query's outcome."""
    if setup:
        h.settings(setup)
    h.server.route(OA, "/works", reply)
    h.run("search", "openalex", "q", "r")
    (record,) = h.ledger()
    assert (record["state"], record["reason"]) == ("unavailable", diagnosis)


# @spec PRIOR-SCR-088
def test_limiter_wait_diagnosis(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """A route that only met limiter waits is unavailable for local pacing."""

    def busy(*_a: object, **_k: object) -> None:
        raise http_limits.RateLimited

    monkeypatch.setattr(http_limits, "acquire", busy)
    h.run("search", "openalex", "q")
    (record,) = h.ledger()
    assert record["reason"] == "rate limit (local pacing)"


# @spec PRIOR-SCR-088
def test_last_failed_query_in_command_line_order_decides(h: Harness) -> None:
    """With a network failure then a rate limit, the diagnosis is rate limit."""
    h.server.route(
        OA, "/works", Reply(500, {}), Reply(500, {}), Reply(429, {}, {"Retry-After": "120"})
    )
    h.run("search", "openalex", "a", "b")
    assert h.outcomes() == ["network", "rate limit"]
    (record,) = h.ledger()
    assert record["reason"] == "rate limit, no key set"


# @spec PRIOR-SCR-088
def test_arxiv_rate_limit_diagnosis_has_no_key_clause(h: Harness) -> None:
    """The arXiv route has no setting, so its throttled diagnosis is plain rate limit."""
    h.server.route(AX, "/api/query", Reply(429, {}, {"Retry-After": "120"}))
    h.run("search", "arxiv", "q")
    (record,) = h.ledger()
    assert record["reason"] == "rate limit"


# @spec PRIOR-SCR-088
def test_refused_for_a_rejected_key_diagnosis(h: Harness) -> None:
    """A later invocation refused for a rejected key gets the rejected-key diagnosis."""
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    h.server.route(OA, "/works", Reply(401, {}))
    h.run("search", "openalex", "a")
    h.run("search", "openalex", "b")
    assert h.ledger()[-1]["reason"] == "authentication: `openalex.api_key` rejected"


def _result_lines(out: str, qid: str) -> list[str]:
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if qid in line)
    following = []
    for line in lines[start + 1 :]:
        if "-q" in line or line.startswith("{"):
            break
        following.append(line)
    return following


# @spec PRIOR-SCR-089, PRIOR-SCR-090, PRIOR-SCR-093
def test_summary_lines(h: Harness) -> None:
    """A query line, then its top 10 results, then how many more are on disk."""
    works = [openalex_work(i) for i in range(1, 13)]
    works[0]["title"] = "T" * 150
    works[1]["publication_year"] = None
    works[1]["publication_date"] = None
    h.server.route(OA, "/works", Reply(200, {"meta": {"count": 12}, "results": works}))
    result = h.run("search", "openalex", "query one")
    qid = str(h.queries()[0]["id"])
    head = next(line for line in result.out.splitlines() if qid in line)
    for part in ("openalex", "query one", "ok", "12"):
        assert part in head
    body = _result_lines(result.out, qid)
    first, second = body[0], body[1]
    assert "W1" in first
    assert "T" * 99 + "…" in first
    assert "T" * 100 not in first
    assert "W2" in second
    assert "None" not in second
    assert re.search(r"(^|\s)-(\s|$)", second)
    assert not any(re.search(r"\bW1[12]\b", line) for line in body)
    assert any("2 more" in line and "records.jsonl" in line for line in body)


# @spec PRIOR-SCR-090
def test_repeated_result_prints_only_its_id(h: Harness) -> None:
    """A result already printed in the invocation is shown again by ID only."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    result = h.run("search", "openalex", "a", "b")
    assert result.out.count("OpenAlex paper 1") == 1
    assert len(re.findall(r"\bW1\b", result.out)) >= 2


# @spec PRIOR-SCR-090, PRIOR-SCR-093
def test_show_zero_prints_no_result_lines(h: Harness) -> None:
    """--show 0 prints no results, only how many are on disk."""
    h.server.route(OA, "/works", Reply(200, openalex_page(3)))
    result = h.run("search", "openalex", "q", extra=("--show", "0"))
    assert "OpenAlex paper" not in result.out
    assert any("3 more" in line for line in result.out.splitlines())


# @spec PRIOR-SCR-091
def test_summary_ends_with_ledger_and_paths(h: Harness) -> None:
    """The summary ends with the ledger as JSON lines and the files' paths."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    result = h.run("search", "openalex", "q")
    ledger = [json.loads(line) for line in result.out.splitlines() if line.startswith("{")]
    assert ledger[0]["route"] == "OpenAlex"
    for name in ("queries.jsonl", "records.jsonl", "ledger.jsonl", "harvest.log", "raw"):
        assert str(h.run_dir / name) in result.out


# @spec PRIOR-SCR-092
@pytest.mark.parametrize(
    ("replies", "code"),
    [
        ([Reply(200, openalex_page(1))], 0),
        ([Reply(200, openalex_page(1)), Reply(500, {})], 3),
    ],
)
def test_exit_status(h: Harness, replies: list[Reply], code: int) -> None:
    """0 when every query ran, 3 when one didn't."""
    h.server.route(OA, "/works", *replies)
    assert h.run("search", "openalex", "a", "b").code == code


# @spec PRIOR-SCR-092
def test_invalid_input_makes_exit_3(h: Harness) -> None:
    """A query that is invalid input means not every query ran."""
    h.server.route(OA, "/works/W5", Reply(200, {"id": "https://openalex.org/W5"}))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("references", "openalex", "W5", "no id here").code == 3
    assert h.outcomes() == ["ok", "invalid input"]


# Connector quirks and odd inputs ------------------------------------------------------------


# The arXiv connector's sleep before its first retry of a 429: `(attempt + 1) * 1.5` in
# `ArxivSearcher._request_with_retries` (paper_search_mcp/academic_platforms/arxiv.py).
ARXIV_CONNECTOR_RETRY_SLEEP = 1.5


# @spec PRIOR-SCR-054, PRIOR-SCR-077
def test_connector_never_sleeps_for_a_huge_retry_after(h: Harness) -> None:
    """An arXiv 429 asking for a day ends at once as rate limit, with no connector sleep."""
    h.server.route(AX, "/api/query", Reply(429, {}, {"Retry-After": "86400"}))
    assert h.run("search", "arxiv", "q").code == 3
    assert len(h.server.sent) == 1
    assert max(h.clock.slept, default=0) <= 60
    assert ARXIV_CONNECTOR_RETRY_SLEEP not in h.clock.slept
    assert h.outcomes() == ["rate limit"]


# @spec PRIOR-SCR-075
def test_error_inside_the_adapter_is_internal(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """An error of the harvester's own inside a request isn't swallowed as a network failure."""

    def full_disk(*_a: object, **_k: object) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(h.module.RunDir, "save_raw", full_disk)
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "a", "b").code == 3
    assert h.outcomes() == ["internal error", "internal error"]
    assert h.queries()[0]["attempts"]
    assert "No space left" in (h.run_dir / "harvest.log").read_text()


# @spec PRIOR-SCR-075, PRIOR-SCR-079
def test_corrupt_state_file_is_internal(h: Harness) -> None:
    """A state.json the harvester didn't write stops the run rather than forgetting a rejection."""
    h.run_dir.mkdir(parents=True)
    (h.run_dir / "state.json").write_text("[]")
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-078
def test_relations_lookups_get_the_longest_time_budget(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Citation lookups get the connector's 60-second budget, so a Retry-After wait fits."""
    seen: dict[str, object] = {}
    real = openalex_relations.related_works

    def spy(*args: Any, **kwargs: Any) -> object:  # noqa: ANN401
        seen.update(kwargs)
        return real(*args, **kwargs)

    monkeypatch.setattr(openalex_relations, "related_works", spy)
    h.server.route(OA, "/works/W7", Reply(200, {"id": "https://openalex.org/W7"}))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("citations", "openalex", "W7")
    assert seen["timeout_seconds"] == 60


# @spec PRIOR-SCR-045
def test_any_false_verify_is_refused(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    """Any false verify value turns verification off in requests, so all of them are refused."""
    stray = _stray_search("https://api.openalex.org/works", verify=0)
    monkeypatch.setattr(openalex.OpenAlexSearcher, "search", stray)
    h.run("search", "openalex", "q")
    assert h.server.sent == []
    assert h.queries()[0]["reason"] == "tls"


# @spec PRIOR-SCR-030, PRIOR-SCR-083
def test_redaction_keeps_json_valid_and_catches_escaped_forms(h: Harness) -> None:
    """A short value can't corrupt a record, and a JSON-escaped value is still redacted."""
    h.settings('[openalex]\napi_key = "k\\"ey-7f3a"\n[other]\nnumber = "1"\n')
    h.server.route(OA, "/works", Reply(200, openalex_page(2)), Reply(500, {"echo": 'k"ey-7f3a'}))
    h.run("search", "openalex", "a", "b")
    for name in ("records.jsonl", "queries.jsonl", "ledger.jsonl"):
        jsonl(h.run_dir / name)  # every line still parses
    assert 'k\\"ey-7f3a' not in h.written()
    assert 'k"ey-7f3a' not in h.written()


# @spec PRIOR-SCR-032
def test_control_character_in_a_value_exits_4(h: Harness) -> None:
    """A value with a control character could reach a log escaped, past redaction."""
    h.settings('[openalex]\napi_key = "ab\\ncd"\n')
    assert h.run("search", "openalex", "q").code == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-090
def test_titles_fold_onto_one_line_and_missing_ids_still_print(h: Harness) -> None:
    """A title's line breaks are folded, and results without an ID each keep their title."""
    works = [openalex_work(1), openalex_work(2)]
    works[0]["title"] = "Split\n  across lines"
    works[0]["id"] = ""
    works[1]["id"] = ""
    h.server.route(OA, "/works", Reply(200, {"meta": {"count": 2}, "results": works}))
    result = h.run("search", "openalex", "q")
    assert "Split across lines" in result.out
    assert "OpenAlex paper 2" in result.out


# @spec PRIOR-SCR-083
def test_arxiv_records_have_no_citation_count(h: Harness) -> None:
    """The arXiv API reports no citations, so the count is unknown, not zero."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    h.run("search", "arxiv", "q")
    (record,) = jsonl(h.run_dir / "records.jsonl")
    assert record["citations"] is None


# @spec PRIOR-SCR-087, PRIOR-SCR-088
def test_not_found_gives_no_ledger_record(h: Harness) -> None:
    """A paper ID that doesn't exist faults the query, not the route."""
    h.server.route(OA, "/works/", Reply(404, {"error": "no such work"}))
    h.run("citations", "openalex", "10.9999/none", "W404")
    assert h.ledger() == []


# @spec PRIOR-SCR-092
def test_status_4_names_a_usage_error(h: Harness) -> None:
    """A usage error is labeled as one, so the agent fixes it instead of falling back."""
    h.module.main(["search", "--service", "nope", "--round", "1", "--run-dir", "R", "q"])
    assert h.capsys.readouterr().err.startswith("harvest.py: usage error:")


# @spec PRIOR-SCR-092
def test_status_4_names_a_setup_error(h: Harness) -> None:
    """A setup error is labeled as one, so the agent falls back."""
    h.settings("[openalex\n")
    h.module.main(["search", "--service", "openalex", "--round", "1", "--run-dir", "R", "q"])
    assert h.capsys.readouterr().err.startswith("harvest.py: setup error:")


# @spec PRIOR-SCR-069, PRIOR-SCR-071
def test_limiter_blocking_only_the_retry_keeps_the_rate_limit(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The service's 429 decides the outcome when the limiter blocks only the retry."""
    real = http_limits.acquire
    calls = 0

    def second_blocked(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        nonlocal calls
        calls += 1
        if calls > 1:
            raise http_limits.RateLimited
        real(*args, **kwargs)

    monkeypatch.setattr(http_limits, "acquire", second_blocked)
    h.server.route(OA, "/works", Reply(429, {}, {"Retry-After": "5"}))
    assert h.run("search", "openalex", "a", "b").code == 3
    assert len(h.server.sent) == 1
    assert h.outcomes() == ["rate limit", "skipped: service throttled"]


# Lookups by ID ------------------------------------------------------------------------------

RELATED_SELECT = "id,related_works"
BUDGET_429 = Reply(429, {"error": "Insufficient budget"})


def _oa_work(i: int, **more: object) -> dict[str, object]:
    """An OpenAlex work that is open access unless `more` says otherwise."""
    return {
        **openalex_work(i),
        "open_access": {
            "is_oa": True,
            "oa_status": "gold",
            "oa_url": f"https://example.org/oa{i}.pdf",
        },
        "best_oa_location": {"license": "cc-by", "pdf_url": f"https://repo.example.org/{i}.pdf"},
        **more,
    }


def _related(h: Harness, listed: list[object], *, seed: int = 9) -> None:
    """Script the seed request of a `related` query on work `W<seed>`."""
    body = {"id": f"https://openalex.org/W{seed}", "related_works": listed}
    h.server.route(OA, f"/works/W{seed}", Reply(200, body), params={"select": RELATED_SELECT})


def _work_urls(*numbers: int) -> list[object]:
    return [f"https://openalex.org/W{n}" for n in numbers]


def _records(h: Harness) -> list[dict[str, Any]]:
    path = h.run_dir / "records.jsonl"
    return jsonl(path) if path.exists() else []


# @spec PRIOR-SCR-123
@pytest.mark.parametrize(
    ("given", "sent_as"),
    [
        ("2401.00001", "2401.00001"),
        ("  2401.00001  ", "2401.00001"),
        ("arXiv:2401.00001", "2401.00001"),
        ("ARXIV:2401.00001v2", "2401.00001v2"),
        ("  arXiv:2401.00001 ", "2401.00001"),
        ("hep-th/9901001", "hep-th/9901001"),
        ("math.GT/0309136v1", "math.GT/0309136v1"),
    ],
)
def test_arxiv_get_sends_one_id_list_request(h: Harness, given: str, sent_as: str) -> None:
    """An arXiv `get` asks the API for the ID alone and records the paper it returns."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    assert h.run("get", "arxiv", given).code == 0
    (sent,) = h.server.sent
    assert sent.query["id_list"] == [sent_as]
    assert sent.query["max_results"] == ["1"]
    assert "search_query" not in sent.query
    (record,) = _records(h)
    assert (record["title"], record["arxiv_id"]) == ("arXiv paper 1", "2401.00001v1")
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-123, PRIOR-SCR-010, PRIOR-SCR-042
def test_arxiv_get_sends_each_id_in_its_own_request(h: Harness) -> None:
    """Each ID is its own query and request, the same ID twice included."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    assert h.run("get", "arxiv", "2401.00001", "2401.00002", "2401.00001").code == 0
    assert [s.query["id_list"] for s in h.server.sent] == [
        ["2401.00001"],
        ["2401.00002"],
        ["2401.00001"],
    ]
    assert _gaps(h.server.sent) == [3.0, 3.0]
    assert len(h.queries()) == 3


# @spec PRIOR-SCR-124
@pytest.mark.parametrize(
    "given",
    [
        "arXiv: 2401.00001",
        "arXiv:arXiv:2401.00001",
        "arXiv:",
        "https://arxiv.org/abs/2401.00001",
        "2401.00001V2",
        "2401.001",
        "not-an-id",
        "2401.00001,2401.00002",
        "2401.00001".translate(ARABIC_INDIC_DIGITS),
    ],
)
def test_arxiv_get_refuses_other_id_forms(h: Harness, given: str) -> None:
    """An ID the arXiv connector's pattern doesn't match is invalid input, and isn't sent."""
    assert h.run("get", "arxiv", given).code == 3
    assert h.outcomes() == ["invalid input"]
    assert h.server.sent == []


# @spec PRIOR-SCR-130, PRIOR-SCR-087, PRIOR-SCR-092
def test_arxiv_get_of_an_unknown_id_is_not_found(h: Harness) -> None:
    """A feed with no entry means arXiv doesn't hold the ID: not found, sent once, exit 3."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(0)))
    assert h.run("get", "arxiv", "2912.99999").code == 3
    assert h.outcomes() == ["not found"]
    assert len(h.server.sent) == 1
    assert _records(h) == []


# @spec PRIOR-SCR-062, PRIOR-SCR-123
def test_arxiv_get_accepts_a_usable_406_feed(h: Harness) -> None:
    """A 406 that the connector accepts as a feed gives the paper, as for a search."""
    h.server.route(AX, "/api/query", Reply(406, arxiv_feed(1)))
    assert h.run("get", "arxiv", "2401.00001").code == 0
    assert [r["arxiv_id"] for r in _records(h)] == ["2401.00001v1"]


# @spec PRIOR-SCR-074
def test_arxiv_get_404_is_a_client_error(h: Harness) -> None:
    """A 404 from arXiv faults the request: it reports an unknown ID with an empty feed."""
    h.server.route(AX, "/api/query", Reply(404, "not here"))
    assert h.run("get", "arxiv", "2401.00001").code == 3
    assert h.outcomes() == ["client error"]


# @spec PRIOR-SCR-086, PRIOR-SCR-133
def test_arxiv_get_queries_no_route_and_prints_no_open_access_line(h: Harness) -> None:
    """An arXiv `get` has no route or ledger record either, and no open-access line."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    result = h.run("get", "arxiv", "2401.00001")
    assert result.code == 0
    assert "arXiv paper 1" in result.out
    assert "open access" not in result.out
    assert [q["route"] for q in h.queries()] == [None]
    assert not (h.run_dir / "ledger.jsonl").exists()


# @spec PRIOR-SCR-113, PRIOR-SCR-050, PRIOR-SCR-068
def test_arxiv_get_is_retried_once(h: Harness) -> None:
    """A failed arXiv `get` gets the one retry of any arXiv request."""
    h.server.route(AX, "/api/query", Reply(500), Reply(200, arxiv_feed(1)))
    assert h.run("get", "arxiv", "2401.00001").code == 0
    assert len(h.server.sent) == 2
    h.reload()
    h.server.routes.clear()
    h.server.route(AX, "/api/query", Reply(500))
    assert h.run("get", "arxiv", "2401.00001").code == 3
    assert len(h.server.sent) == 4
    assert h.outcomes()[-1] == "network"


# @spec PRIOR-SCR-125, PRIOR-SCR-058
@pytest.mark.parametrize(
    ("given", "path"),
    [
        ("10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("doi:10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("https://doi.org/10.1145/3368089.3409741", "/works/doi:10.1145%2F3368089.3409741"),
        ("W2741809807", "/works/W2741809807"),
        ("https://openalex.org/W2741809807", "/works/W2741809807"),
        ("Attention is all you need", None),
        ("2401.00001", None),
    ],
)
def test_openalex_get_id_forms(h: Harness, given: str, path: str | None) -> None:
    """An OpenAlex `get` takes the IDs the citations lookup takes, and sends nothing for others."""
    h.server.route(OA, "/works/", Reply(200, _oa_work(1)))
    result = h.run("get", "openalex", given)
    if path is None:
        assert (result.code, h.outcomes()) == (3, ["invalid input"])
        assert h.server.sent == []
    else:
        assert (result.code, h.outcomes()) == (0, ["ok"])
        (sent,) = h.server.sent
        assert sent.url.split("?")[0] == f"https://{OA}{path}"


# @spec PRIOR-SCR-125
def test_openalex_get_asks_for_the_parser_fields_and_open_access(h: Harness) -> None:
    """The request selects each field the connector's work parser reads, plus open access."""
    probe = _KeyRecorder({**_oa_work(1), "concepts": [], "referenced_works": []})
    searcher = object.__new__(openalex.OpenAlexSearcher)
    assert searcher._parse_work(probe) is not None
    assert {"id", "title", "authorships", "cited_by_count"} <= probe.read
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    assert h.run("get", "openalex", "W1").code == 0
    (select,) = h.server.sent[0].query["select"]
    assert probe.read | {"open_access", "best_oa_location"} <= set(select.split(","))


# @spec PRIOR-SCR-125, PRIOR-SCR-048
def test_openalex_get_carries_the_session_key(h: Harness) -> None:
    """A keyed `get` carries the key the connector's session holds, and no key when none is set."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    assert h.run("get", "openalex", "W1").code == 0
    assert "Authorization" not in h.server.sent[0].headers
    h.reload()
    h.settings(f'[openalex]\napi_key = "{CANARY}"\n')
    assert h.run("get", "openalex", "W1").code == 0
    assert h.server.sent[1].headers["Authorization"] == f"Bearer {CANARY}"


# @spec PRIOR-SCR-132, PRIOR-SCR-083
def test_openalex_get_record_has_open_access_fields(h: Harness) -> None:
    """A `get` record adds the work's open-access status, link and license."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    closed = _oa_work(2, open_access={"is_oa": False, "oa_status": "closed", "oa_url": None})
    closed["best_oa_location"] = None
    h.server.route(OA, "/works/W2", Reply(200, closed))
    bare = openalex_work(3)
    h.server.route(OA, "/works/W3", Reply(200, bare))
    assert h.run("get", "openalex", "W1", "W2", "W3").code == 0
    one, two, three = _records(h)
    assert (one["service_id"], one["title"], one["rank"]) == ("W1", "OpenAlex paper 1", 1)
    assert (one["is_oa"], one["oa_status"], one["oa_url"], one["oa_license"]) == (
        True,
        "gold",
        "https://example.org/oa1.pdf",
        "cc-by",
    )
    assert (two["is_oa"], two["oa_status"], two["oa_url"], two["oa_license"]) == (
        False,
        "closed",
        None,
        None,
    )
    for name in ("is_oa", "oa_status", "oa_url", "oa_license"):
        assert name in three
        assert three[name] is None


# @spec PRIOR-SCR-132
def test_other_actions_records_have_no_open_access_fields(h: Harness) -> None:
    """Only `get` and `related` records carry the open-access fields."""
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    assert h.run("search", "openalex", "q").code == 0
    (record,) = _records(h)
    assert "is_oa" not in record
    assert "oa_url" not in record


# @spec PRIOR-SCR-133
def test_openalex_get_prints_an_open_access_line(h: Harness) -> None:
    """Under each `get` result, a line gives its open-access status and link, or says closed."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    closed = _oa_work(2, open_access={"is_oa": False, "oa_status": "closed", "oa_url": None})
    h.server.route(OA, "/works/W2", Reply(200, closed))
    no_link = _oa_work(3, open_access={"is_oa": True, "oa_status": "bronze", "oa_url": None})
    h.server.route(OA, "/works/W3", Reply(200, no_link))
    no_status = _oa_work(4, open_access={"is_oa": True, "oa_url": "https://example.org/4"})
    h.server.route(OA, "/works/W4", Reply(200, no_status))
    h.server.route(OA, "/works/W5", Reply(200, _oa_work(5, open_access={"oa_status": "gold"})))
    h.server.route(OA, "/works/W6", Reply(200, openalex_work(6)))
    result = h.run("get", "openalex", "W1", "W2", "W3", "W4", "W5", "W6", "W1")
    one, two, three, four, five, six, again = (
        _result_lines(result.out, str(q["id"])) for q in h.queries()
    )
    assert "OpenAlex paper 1" in one[0]
    assert "open access: gold  https://example.org/oa1.pdf" in one[1]
    assert "not open access" in two[1]
    assert "open access: bronze  -" in three[1]
    assert "open access: -  https://example.org/4" in four[1]
    assert "not open access" in five[1]  # `is_oa` missing isn't open access
    assert "not open access" in six[1]
    assert "OpenAlex paper 1" not in again[0]
    assert "open access: gold  https://example.org/oa1.pdf" in again[1]


# @spec PRIOR-SCR-133
def test_open_access_line_only_under_a_printed_get_result(h: Harness) -> None:
    """No open-access line with --show 0, nor under the results of another action."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    _related(h, _work_urls(1))
    assert "open access" not in h.run("get", "openalex", "W1", extra=("--show", "0")).out
    h.reload()
    assert "open access" not in h.run("related", "openalex", "W9").out


# @spec PRIOR-SCR-062, PRIOR-SCR-068
@pytest.mark.parametrize("body", [{}, {"id": ""}, {"id": 7}, ["https://openalex.org/W1"]])
def test_openalex_get_body_without_a_work_id_is_unparsable(
    h: Harness, body: dict[str, Any] | list[Any]
) -> None:
    """A 200 that isn't a work with an ID is retried once, then ends network."""
    h.server.route(OA, "/works/W1", Reply(200, body))
    assert h.run("get", "openalex", "W1").code == 3
    assert h.outcomes() == ["network"]
    assert len(h.server.sent) == 2


# @spec PRIOR-SCR-065
def test_openalex_get_of_an_unknown_work_is_not_found(h: Harness) -> None:
    """A 404 means OpenAlex doesn't hold the work."""
    h.server.route(OA, "/works/W1", Reply(404, {"error": "Not found"}))
    assert h.run("get", "openalex", "W1").code == 3
    assert h.outcomes() == ["not found"]
    assert len(h.server.sent) == 1


# @spec PRIOR-SCR-062, PRIOR-SCR-125
def test_openalex_get_follows_a_merged_work_redirect(h: Harness) -> None:
    """A work OpenAlex merged into another is returned under the other's ID."""
    target = f"https://{OA}/works/W6"
    h.server.route(OA, "/works/W5", Reply(301, b"", {"Location": target}))
    h.server.route(OA, "/works/W6", Reply(200, _oa_work(6)))
    assert h.run("get", "openalex", "W5").code == 0
    assert [s.path for s in h.server.sent] == ["/works/W5", "/works/W6"]
    (record,) = _records(h)
    assert record["service_id"] == "W6"


# @spec PRIOR-SCR-065
@pytest.mark.parametrize("action", ["get", "related"])
def test_merged_work_whose_replacement_is_gone_is_not_found(h: Harness, action: str) -> None:
    """A 404 after a merged-work redirect still means the paper isn't found."""
    h.server.route(OA, "/works/W5", Reply(301, b"", {"Location": f"https://{OA}/works/W6"}))
    h.server.route(OA, "/works/W6", Reply(404, {"error": "Not found"}))
    assert h.run(action, "openalex", "W5").code == 3
    assert h.outcomes() == ["not found"]


# @spec PRIOR-SCR-125, PRIOR-SCR-126, PRIOR-SCR-062
def test_related_seed_redirect_keeps_its_select_and_its_checks(h: Harness) -> None:
    """A redirected seed request asks the replacing work for the same fields, judged the same."""
    h.server.route(OA, "/works/W5", Reply(301, b"", {"Location": "/works/W6"}))
    h.server.route(OA, "/works/W6", Reply(200, {"id": "https://openalex.org/W6"}))
    assert h.run("related", "openalex", "W5").code == 3
    assert h.outcomes() == ["network"]
    hops = [s for s in h.server.sent if s.path == "/works/W6"]
    assert len(hops) == 2
    assert all(s.query["select"] == [RELATED_SELECT] for s in hops)


# @spec PRIOR-SCR-125, PRIOR-SCR-044
@pytest.mark.parametrize(
    "location",
    [
        "https://evil.example.org/works/W6",
        f"https://{OA}/authors/A6",
        f"http://{OA}/works/W6",
        f"https://{OA}/works/W5/../../other",
    ],
)
def test_openalex_get_follows_no_redirect_but_to_a_work(h: Harness, location: str) -> None:
    """A redirect to anything but another OpenAlex work isn't followed, and ends network."""
    h.server.route(OA, "/works/W5", Reply(301, b"", {"Location": location}))
    assert h.run("get", "openalex", "W5").code == 3
    assert h.outcomes() == ["network"]
    assert [s.path for s in h.server.sent] == ["/works/W5"]


# @spec PRIOR-SCR-125
def test_openalex_get_gives_up_on_a_redirect_loop(h: Harness) -> None:
    """Redirects that never reach a work end the query as network."""
    h.server.route(OA, "/works/W5", Reply(301, b"", {"Location": "/works/W6"}))
    h.server.route(OA, "/works/W6", Reply(301, b"", {"Location": "/works/W5"}))
    assert h.run("get", "openalex", "W5").code == 3
    assert h.outcomes() == ["network"]
    assert len(h.server.sent) <= 4


# @spec PRIOR-SCR-126, PRIOR-SCR-064
def test_openalex_work_without_a_title_is_not_a_result(h: Harness) -> None:
    """A work the connector's parser returns no paper for ran and found nothing."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1, title=None)))
    assert h.run("get", "openalex", "W1").code == 0
    assert h.outcomes() == ["empty"]


# @spec PRIOR-SCR-076
@pytest.mark.parametrize("action", ["get", "related"])
def test_work_the_parser_cannot_read_is_network(h: Harness, action: str) -> None:
    """A usable response whose work the connector's parser raises on ends network, not internal."""
    _related(h, _work_urls(1))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1, primary_location="elsewhere")))
    target = "W1" if action == "get" else "W9"
    assert h.run(action, "openalex", target, "W1").code == 3
    assert h.outcomes()[0] == "network"
    assert "internal error" not in h.outcomes()


# @spec PRIOR-SCR-074
@pytest.mark.parametrize("action", ["get", "related"])
def test_single_work_client_error_is_not_resent(h: Harness, action: str) -> None:
    """A 400 to a `get` or `related` request is a client error, sent once."""
    h.server.route(OA, "/works/W1", Reply(400, {"error": "bad select"}))
    assert h.run(action, "openalex", "W1").code == 3
    assert h.outcomes() == ["client error"]
    assert len(h.server.sent) == 1


# @spec PRIOR-SCR-086, PRIOR-SCR-082
def test_get_queries_no_route(h: Harness) -> None:
    """A `get` invocation appends no ledger record, and its log lines have no route."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)), Reply(500))
    result = h.run("get", "openalex", "W1", "W1")
    assert result.code == 3
    assert h.outcomes() == ["ok", "network"]
    assert not (h.run_dir / "ledger.jsonl").exists()
    assert [q["route"] for q in h.queries()] == [None, None]
    assert not [line for line in result.out.splitlines() if line.startswith("{")]
    assert str(h.run_dir / "ledger.jsonl") in result.out


# @spec PRIOR-SCR-010
@pytest.mark.parametrize(
    ("action", "service", "query"),
    [("get", "arxiv", "2401.00001"), ("get", "openalex", "W1")],
)
def test_get_takes_a_depth_of_1(h: Harness, action: str, service: str, query: str) -> None:
    """A `get` returns its one paper, so a depth of 1 is accepted."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    assert h.run(action, service, query, extra=("--max-results", "1")).code == 0


def _run_argv(action: str, service: str, *rest: str) -> list[str]:
    return [action, "--service", service, "--round", "1", "--run-dir", "R", *rest]


# @spec PRIOR-SCR-010, PRIOR-SCR-011
@pytest.mark.parametrize(
    "argv",
    [
        _run_argv("get", "semanticscholar", "W1"),
        _run_argv("get", "openalex", "--max-results", "2", "W1"),
        _run_argv("get", "arxiv", "--max-results", "0", "2401.00001"),
        _run_argv("get", "arxiv", "   "),
        _run_argv("related", "arxiv", "W1"),
        _run_argv("related", "semanticscholar", "W1"),
        _run_argv("related", "openalex", "--max-results", "101", "W1"),
        _run_argv("related", "openalex", "--max-results", "0", "W1"),
        _run_argv("search", "openalex", "--sort", "submitted", "q"),
        _run_argv("search", "openalex", "--sort", "relevance", "q"),
        _run_argv("get", "arxiv", "--sort", "submitted", "2401.00001"),
        _run_argv("search", "arxiv", "--sort", "newest", "q"),
        _run_argv("search", "arxiv", "--sort", "submitted", "--sort", "relevance", "q"),
        _run_argv("search", "arxiv", "--sort", "q"),
    ],
)
def test_invalid_lookup_and_sort_command_lines_exit_4(h: Harness, argv: list[str]) -> None:
    """A mismatched service, an out-of-range depth or a misplaced sort is a usage error."""
    assert h.main(argv) == 4
    assert h.server.sent == []


# @spec PRIOR-SCR-126, PRIOR-SCR-132, PRIOR-SCR-086
def test_related_fetches_each_listed_work(h: Harness) -> None:
    """A `related` query asks for the seed's list, then for each listed work in order."""
    _related(h, _work_urls(1, 2, 3))
    for i in (1, 2, 3):
        h.server.route(OA, f"/works/W{i}", Reply(200, _oa_work(i)))
    result = h.run("related", "openalex", "W9")
    assert result.code == 0
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W2", "/works/W3"]
    assert h.server.sent[0].query["select"] == [RELATED_SELECT]
    selects = {s.query["select"][0] for s in h.server.sent[1:]}
    h.reload()
    h.run("get", "openalex", "W1")
    assert selects == {h.server.sent[-1].query["select"][0]}
    records = _records(h)[:3]
    assert [(r["rank"], r["service_id"]) for r in records] == [(1, "W1"), (2, "W2"), (3, "W3")]
    first = records[0]
    assert (first["is_oa"], first["oa_status"], first["oa_url"], first["oa_license"]) == (
        True,
        "gold",
        "https://example.org/oa1.pdf",
        "cc-by",
    )
    logged = h.queries()[0]
    assert (logged["outcome"], logged["results"], logged["truncated"]) == ("ok", 3, None)
    assert logged["route"] == "OpenAlex"
    ledger = h.ledger()[0]
    assert (ledger["route"], ledger["state"]) == ("OpenAlex", "searched")


# @spec PRIOR-SCR-010, PRIOR-SCR-126, PRIOR-SCR-128, PRIOR-SCR-064
@pytest.mark.parametrize(
    ("extra", "listed", "fetched"),
    [
        ((), 25, 20),
        (("--max-results", "2"), 5, 2),
        (("--max-results", "3"), 3, 3),
        (("--max-results", "100"), 3, 3),
    ],
)
def test_related_fetch_depth_and_truncation(
    h: Harness, extra: tuple[str, ...], listed: int, fetched: int
) -> None:
    """The first N listed works are fetched (20 by default), and a longer list is noted."""
    _related(h, _work_urls(*range(1, listed + 1)))
    h.server.route(OA, "/works/", Reply(200, _oa_work(1)))
    result = h.run("related", "openalex", "W9", extra=extra)
    assert result.code == 0
    assert len(h.server.sent) == 1 + fetched
    (logged,) = h.queries()
    head = next(line for line in result.out.splitlines() if str(logged["id"]) in line)
    if listed > fetched:
        assert logged["truncated"] == f"{listed} listed"
        assert f"truncated: {listed} listed" in head
    else:
        assert logged["truncated"] is None
        assert "truncated" not in head
    assert logged["outcome"] == "ok"


# @spec PRIOR-SCR-127, PRIOR-SCR-062
def test_related_leaves_out_a_listed_work_that_is_gone(h: Harness) -> None:
    """A listed work answering 404 is skipped, without fetching one beyond the first N instead."""
    _related(h, _work_urls(1, 2, 3, 4))
    h.server.route(OA, "/works/W2", Reply(404, {"error": "Not found"}))
    h.server.route(OA, "/works/", Reply(200, _oa_work(1)))
    assert h.run("related", "openalex", "W9", extra=("--max-results", "3")).code == 0
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W2", "/works/W3"]
    assert [r["rank"] for r in _records(h)] == [1, 3]
    assert h.outcomes() == ["ok"]


# @spec PRIOR-SCR-126
def test_related_skips_repeated_and_malformed_entries(h: Harness) -> None:
    """A repeated entry, or one that isn't a work ID, keeps its position and isn't requested."""
    listed = [
        *_work_urls(1, 1),
        "W1",
        "https://example.org/W7",
        None,
        "https://doi.org/10.1234/oa8",
        "W3",
        *_work_urls(4),
    ]
    _related(h, listed)
    for i in (1, 3, 4):
        h.server.route(OA, f"/works/W{i}", Reply(200, _oa_work(i)))
    assert h.run("related", "openalex", "W9").code == 0
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W3", "/works/W4"]
    assert [(r["rank"], r["service_id"]) for r in _records(h)] == [(1, "W1"), (7, "W3"), (8, "W4")]


# @spec PRIOR-SCR-126, PRIOR-SCR-128
def test_related_counts_skipped_entries_toward_the_number_to_fetch(h: Harness) -> None:
    """The first N entries are considered, a repeated or malformed one among them included."""
    _related(h, [*_work_urls(1, 1), "junk", *_work_urls(2, 3)])
    h.server.route(OA, "/works/", Reply(200, _oa_work(1)))
    assert h.run("related", "openalex", "W9", extra=("--max-results", "3")).code == 0
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1"]
    (logged,) = h.queries()
    assert (logged["results"], logged["truncated"]) == (1, "5 listed")


# @spec PRIOR-SCR-062, PRIOR-SCR-135
def test_related_listed_work_body_without_an_id_is_unparsable(h: Harness) -> None:
    """A listed work's 200 that isn't a work is retried once, then ends the query as network."""
    _related(h, _work_urls(1, 2))
    h.server.route(OA, "/works/W1", Reply(200, {}))
    h.server.route(OA, "/works/W2", Reply(200, _oa_work(2)))
    assert h.run("related", "openalex", "W9").code == 3
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W1"]
    assert h.outcomes() == ["network"]
    assert _records(h) == []


# @spec PRIOR-SCR-064, PRIOR-SCR-127
@pytest.mark.parametrize("listed", [[], _work_urls(1, 2)], ids=["none-listed", "all-gone"])
def test_related_with_nothing_to_show_is_empty(h: Harness, listed: list[object]) -> None:
    """A seed that lists no related works, or only works that are gone, ran and found nothing."""
    _related(h, listed)
    h.server.route(OA, "/works/", Reply(404, {"error": "Not found"}))
    assert h.run("related", "openalex", "W9").code == 0
    assert h.outcomes() == ["empty"]
    assert _records(h) == []


# @spec PRIOR-SCR-065, PRIOR-SCR-058
def test_related_of_an_unknown_or_invalid_paper(h: Harness) -> None:
    """A seed OpenAlex doesn't hold is not found; an ID in no accepted form isn't sent."""
    h.server.route(OA, "/works/W9", Reply(404, {"error": "Not found"}))
    assert h.run("related", "openalex", "W9", "not an id").code == 3
    assert h.outcomes() == ["not found", "invalid input"]
    assert len(h.server.sent) == 1


# @spec PRIOR-SCR-062, PRIOR-SCR-068
@pytest.mark.parametrize(
    "body",
    [{"id": "https://openalex.org/W9"}, {"related_works": []}, {"id": "W9", "related_works": "x"}],
)
def test_related_seed_body_without_its_list_is_unparsable(h: Harness, body: dict[str, Any]) -> None:
    """A seed 200 without both its ID and its list of related works is retried, then network."""
    h.server.route(OA, "/works/W9", Reply(200, body))
    assert h.run("related", "openalex", "W9").code == 3
    assert h.outcomes() == ["network"]
    assert len(h.server.sent) == 2


# @spec PRIOR-SCR-135, PRIOR-SCR-113, PRIOR-SCR-051, PRIOR-SCR-063
def test_related_ends_at_a_listed_work_that_fails(h: Harness) -> None:
    """A listed work failing both attempts ends the query: no records, nothing further sent."""
    _related(h, _work_urls(1, 2, 3))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    h.server.route(OA, "/works/W2", Reply(500))
    h.server.route(OA, "/works/W3", Reply(200, _oa_work(3)))
    result = h.run("related", "openalex", "W9")
    assert result.code == 3
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W2", "/works/W2"]
    (logged,) = h.queries()
    assert (logged["outcome"], logged["results"]) == ("network", 0)
    assert _records(h) == []
    assert "OpenAlex paper 1" not in result.out
    replayed = [a["url"] for a in logged["attempts"] if a["from_memory"]]
    assert [urlsplit(u).path for u in replayed] == ["/works/W9", "/works/W1"]


# @spec PRIOR-SCR-113, PRIOR-SCR-055
def test_related_retries_a_listed_work_once(h: Harness) -> None:
    """A listed work that fails once is resent, and the query then runs in full."""
    _related(h, _work_urls(1, 2))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    h.server.route(OA, "/works/W2", Reply(503, {}, {"Retry-After": "2"}), Reply(200, _oa_work(2)))
    assert h.run("related", "openalex", "W9").code == 0
    assert [s.path for s in h.server.sent] == ["/works/W9", "/works/W1", "/works/W2", "/works/W2"]
    assert [r["service_id"] for r in _records(h)] == ["W1", "W2"]


# @spec PRIOR-SCR-129, PRIOR-SCR-082, PRIOR-SCR-089
def test_arxiv_search_newest_first(h: Harness) -> None:
    """--sort submitted asks arXiv for the newest first, and the log and summary say so."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(2)))
    result = h.run("search", "arxiv", "cat:cs.SE", extra=("--sort", "submitted"))
    assert result.code == 0
    (sent,) = h.server.sent
    assert (sent.query["sortBy"], sent.query["sortOrder"]) == (["submittedDate"], ["descending"])
    assert sent.query["search_query"] == ["cat:cs.SE"]
    (logged,) = h.queries()
    assert logged["sort"] == "submitted"
    head = next(line for line in result.out.splitlines() if str(logged["id"]) in line)
    assert re.search(r"2 results\s+sort: submitted", head)
    (ledger,) = h.ledger()
    assert ledger["route"] == "arXiv"


# @spec PRIOR-SCR-129, PRIOR-SCR-010
@pytest.mark.parametrize("extra", [(), ("--sort", "relevance")])
def test_arxiv_search_by_relevance_names_no_sort(h: Harness, extra: tuple[str, ...]) -> None:
    """A relevance search, the default, sorts by relevance and names no sort."""
    h.server.route(AX, "/api/query", Reply(200, arxiv_feed(1)))
    result = h.run("search", "arxiv", "q", extra=extra)
    assert h.server.sent[0].query["sortBy"] == ["relevance"]
    (logged,) = h.queries()
    assert logged["sort"] is None
    assert "sort:" not in result.out


# @spec PRIOR-SCR-129
def test_only_an_arxiv_search_log_line_can_name_a_sort(h: Harness) -> None:
    """Every query log line has a `sort`, null for any query but a newest-first search."""
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    h.server.route(OA, "/works", Reply(200, openalex_page(1)))
    h.run("search", "openalex", "q")
    h.reload()
    result = h.run("get", "openalex", "W1")
    assert [q["sort"] for q in h.queries()] == [None, None]
    assert "sort:" not in result.out


# @spec PRIOR-SCR-118
def test_spent_budget_still_allows_single_work_requests(h: Harness) -> None:
    """Once a search spent the budget, `get` and `related` go on, and other actions don't."""
    h.server.route(OA, "/works", BUDGET_429)
    assert h.run("search", "openalex", "q").code == 3
    _related(h, _work_urls(1))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    h.reload()
    assert h.run("get", "openalex", "W1").code == 0
    h.reload()
    assert h.run("related", "openalex", "W9").code == 0
    for action in ("citations", "references"):
        h.reload()
        sent = len(h.server.sent)
        assert h.run(action, "openalex", "W1").code == 3
        assert len(h.server.sent) == sent
        last = h.queries()[-1]
        assert (last["outcome"], last["reason"]) == ("refused", "daily budget")


# @spec PRIOR-SCR-131, PRIOR-SCR-071, PRIOR-SCR-070
@pytest.mark.parametrize("action", ["get", "related"])
def test_budget_response_to_a_single_work_request_stops_openalex(h: Harness, action: str) -> None:
    """A budget response to a `get` or `related` request ends every OpenAlex request for the run."""
    h.server.route(OA, "/works/W1", BUDGET_429)
    assert h.run(action, "openalex", "W1", "W2").code == 3
    assert len(h.server.sent) == 1
    first, second = h.queries()
    assert (first["outcome"], first["reason"]) == ("rate limit", "daily budget")
    assert second["outcome"] == "skipped: service throttled"
    state = json.loads((h.run_dir / "state.json").read_text())
    assert state["openalex_budget_spent"] is True
    assert state["openalex_single_work_budget_spent"] is True
    for later in ("get", "related", "search"):
        h.reload()
        assert h.run(later, "openalex", "W3").code == 3
        last = h.queries()[-1]
        assert (last["outcome"], last["reason"]) == ("refused", "daily budget")
    assert len(h.server.sent) == 1


# @spec PRIOR-SCR-131, PRIOR-SCR-088
def test_related_budget_response_diagnosis(h: Harness) -> None:
    """A `related` invocation stopped by the budget reports its route as out of daily budget."""
    h.server.route(OA, "/works/W1", BUDGET_429)
    h.run("related", "openalex", "W1")
    (record,) = h.ledger()
    assert (record["state"], record["reason"]) == ("unavailable", "rate limit (daily budget)")


# @spec PRIOR-SCR-079, PRIOR-SCR-131
def test_state_file_without_the_single_work_record_is_read(h: Harness) -> None:
    """A state file that records only the budget is still the harvester's own."""
    h.run_dir.mkdir()
    state = {"rejected_keys": {}, "openalex_budget_spent": True}
    (h.run_dir / "state.json").write_text(json.dumps(state))
    h.server.route(OA, "/works/W1", Reply(200, _oa_work(1)))
    assert h.run("get", "openalex", "W1").code == 0
