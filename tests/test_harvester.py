"""Behavior tests of the prior-art search skill's harvester, run in-process against a fake server.

No test reaches the network: `HTTPAdapter.send` is replaced by a scripted server, sockets refuse
to connect, and the fork's limiter keeps its slots in a temporary directory on a fake clock.
"""

from __future__ import annotations

import ast
import contextlib
import email.utils
import fcntl
import itertools
import json
import os
import re
import socket
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

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
    s2_bulk,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType

OA = "api.openalex.org"
S2 = "api.semanticscholar.org"
AX = "export.arxiv.org"
S2_BULK = "/graph/v1/paper/search/bulk"
FORK_VARS = ["OPENALEX_API_KEY", "OPENALEX_EMAIL", "SEMANTIC_SCHOLAR_API_KEY", "RATE_LIMIT_DIR"]
SET_BY_HARVESTER = [
    "PAPER_SEARCH_MCP_RATE_LIMIT_DIR",
    "PAPER_SEARCH_MCP_ENV_FILE",
    "PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY",
]
CANARY = "canary-key-7f3a9c"
OPTIONS = {"--service", "--round", "--run-dir", "--max-results", "--show", "--help"}


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
            action: `search`, `citations` or `references`.
            service: The service.
            *queries: The queries or paper IDs.
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


def _patched(module: ModuleType, clock: FakeClock) -> ModuleType:
    # The harvester's own clock seams, used for its Retry-After waits.
    vars(module).update(_sleep=clock.sleep, _monotonic=clock.monotonic, _wall=clock.time)
    return module


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


def _argv(*parts: str) -> list[str]:
    return list(parts)


# @spec PRIOR-SCR-011
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
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    h.run("search", "openalex", "q")
    h.run("search", "semanticscholar", "q")
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


# @spec PRIOR-SCR-027, PRIOR-SCR-028
def test_each_key_goes_only_to_its_own_service(h: Harness) -> None:
    """The Semantic Scholar key goes in x-api-key, and no other key rides along."""
    h.settings(f'[openalex]\napi_key = "oa-{CANARY}"\n[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    assert h.run("search", "semanticscholar", "q").code == 0
    assert h.server.sent[0].headers.get("x-api-key") == CANARY
    assert "Authorization" not in h.server.sent[0].headers


# @spec PRIOR-SCR-029
def test_no_option_takes_a_setting_value(h: Harness) -> None:
    """Every action's options are the documented ones, none of which takes a setting value."""
    seen: set[str] = set()
    for argv in (["--help"], *([a, "--help"] for a in ("search", "citations", "references"))):
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
    ("service", "host", "path", "reply"),
    [
        ("openalex", OA, "/works", Reply(200, openalex_page(1))),
        ("arxiv", AX, "/api/query", Reply(200, arxiv_feed(1))),
        ("semanticscholar", S2, S2_BULK, Reply(200, s2_bulk(1))),
    ],
)
def test_every_request_carries_the_skill_user_agent(
    h: Harness, service: str, host: str, path: str, reply: Reply
) -> None:
    """The adapter replaces each connector's user agent with the skill's."""
    h.server.route(host, path, reply)
    assert h.run("search", service, "q").code == 0
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
    """With a key set, a request lacking that exact key is refused unsent."""
    h.settings(f'[semanticscholar]\napi_key = "{CANARY}"\n')
    monkeypatch.setattr(semantic.SemanticSearcher, "get_api_key", staticmethod(lambda: sent_key))
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    assert h.run("search", "semanticscholar", "q").code == 3
    assert h.server.sent == []
    (logged,) = h.queries()
    assert (logged["outcome"], logged["reason"]) == ("refused", "missing key")


# @spec PRIOR-SCR-048
def test_connector_anonymous_retry_never_goes_out(h: Harness) -> None:
    """Semantic Scholar's connector retries without its key after a 403; that retry is refused."""
    h.settings(f'[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, S2_BULK, Reply(403, {"message": "Forbidden"}))
    assert h.run("search", "semanticscholar", "q").code == 3
    assert len(h.server.sent) == 1
    assert h.server.sent[0].headers.get("x-api-key") == CANARY


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
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    assert h.run("search", "semanticscholar", "a", "b", "c").code == 0
    times = [s.wall for s in h.server.sent]
    assert len(times) == 3
    assert all(b - a >= 8 for a, b in itertools.pairwise(times))


# @spec PRIOR-SCR-042
def test_semantic_scholar_keyed_requests_are_1_second_apart(h: Harness) -> None:
    """With a key, Semantic Scholar gets one request a second."""
    h.settings(f'[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    assert h.run("search", "semanticscholar", "a", "b").code == 0
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
        h.settings(f'[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(1)))
    h.run("search", "semanticscholar", "q")
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


# @spec PRIOR-SCR-056
def test_semantic_scholar_uses_bulk_search(h: Harness) -> None:
    """Semantic Scholar searches go to the bulk endpoint."""
    h.server.route(S2, S2_BULK, Reply(200, s2_bulk(3)))
    assert h.run("search", "semanticscholar", "q").code == 0
    assert h.server.sent[0].path == S2_BULK


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


# @spec PRIOR-SCR-054, PRIOR-SCR-077
def test_connector_never_sleeps_for_a_huge_retry_after(h: Harness) -> None:
    """A keyed Semantic Scholar 429 asking for a day ends at once as rate limit."""
    h.settings(f'[semanticscholar]\napi_key = "{CANARY}"\n')
    h.server.route(S2, S2_BULK, Reply(429, {}, {"Retry-After": "86400"}))
    assert h.run("search", "semanticscholar", "q").code == 3
    assert len(h.server.sent) == 1
    assert max(h.clock.slept, default=0) <= 60
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
