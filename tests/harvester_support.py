"""Fakes for the harvester's tests: a scripted HTTP server, a fake clock and response bodies.

The harvester's adapter subclasses the fork's rate-limited adapter, whose `send` ends in
`requests.adapters.HTTPAdapter.send`. The fake server replaces that one method, so every check the
harvester's adapter and the fork's limiter make still runs, and nothing reaches the network.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlsplit

import requests

from tests.support import SKILLS

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

HARVEST = SKILLS / "prior-art-search" / "scripts" / "harvest.py"
UA = "prior-art-search agent skill (+https://github.com/jmbowman/agentic_development)"

type Json = dict[str, Any] | list[Any]


def load_harvest() -> ModuleType:
    """The harvester loaded as a fresh module, so module state never leaks between tests.

    Returns:
        The loaded module.

    Raises:
        AssertionError: The harvester doesn't exist yet.
    """
    spec = importlib.util.spec_from_file_location("harvest_under_test", HARVEST)
    if spec is None or spec.loader is None or not HARVEST.exists():
        msg = f"the harvester is missing: {HARVEST}"
        raise AssertionError(msg)
    module = importlib.util.module_from_spec(spec)
    # Dataclasses look their module up in sys.modules while the module runs.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClock:
    """Wall and monotonic time that advance only when something sleeps."""

    def __init__(self) -> None:
        """Start at fixed times, with nothing slept."""
        self.wall = 1_800_000_000.0
        self.mono = 1_000.0
        self.slept: list[float] = []

    def time(self) -> float:
        """The fake wall-clock time, in seconds since the epoch.

        Returns:
            The time.
        """
        return self.wall

    def monotonic(self) -> float:
        """The fake monotonic time.

        Returns:
            The time.
        """
        return self.mono

    def sleep(self, seconds: float) -> None:
        """Advance both clocks instead of sleeping.

        Args:
            seconds: How long the caller asked to sleep.
        """
        if seconds > 0:
            self.slept.append(seconds)
            self.wall += seconds
            self.mono += seconds


@dataclass
class Reply:
    """One scripted reply: a status, a body and headers, or an exception to raise."""

    status: int = 200
    body: bytes | str | Json = b""
    headers: dict[str, str] = field(default_factory=dict)
    error: Exception | None = None


@dataclass
class Sent:
    """One request that reached the fake server, with the fake wall time it arrived."""

    method: str
    url: str
    headers: dict[str, str]
    verify: object
    wall: float

    @property
    def host(self) -> str:
        """The request's host."""
        return urlsplit(self.url).hostname or ""

    @property
    def path(self) -> str:
        """The request's path."""
        return urlsplit(self.url).path

    @property
    def query(self) -> dict[str, list[str]]:
        """The request's query parameters."""
        return parse_qs(urlsplit(self.url).query)


@dataclass
class Route:
    """Scripted replies for one host and path, optionally narrowed by query parameters.

    A path ending in `/` matches every path under it; any other path matches only itself.
    """

    host: str
    path: str
    params: dict[str, str]
    replies: list[Reply]

    def matches(self, sent: Sent) -> bool:
        """Whether a request belongs to this route.

        Args:
            sent: The request.

        Returns:
            True when the host, path and parameters match.
        """
        if sent.host != self.host:
            return False
        if self.path.endswith("/"):
            if not sent.path.startswith(self.path):
                return False
        elif sent.path != self.path:
            return False
        return all(sent.query.get(k, [None])[0] == v for k, v in self.params.items())


class FakeServer:
    """Answers each request from the first matching route's script, and records every request."""

    def __init__(self, clock: FakeClock) -> None:
        """Start with no routes.

        Args:
            clock: The clock whose wall time stamps each request.
        """
        self.clock = clock
        self.routes: list[Route] = []
        self.sent: list[Sent] = []
        self.unexpected: list[str] = []

    def route(
        self, host: str, path: str, *replies: Reply, params: dict[str, str] | None = None
    ) -> None:
        """Script replies for a host and path; the last reply repeats once the others are used.

        Args:
            host: The host.
            path: The path, or a prefix ending in `/`.
            *replies: The replies, in order.
            params: Query parameters a request must carry to match.
        """
        self.routes.append(Route(host, path, params or {}, list(replies)))

    def send(self, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
        """Answer a request as `HTTPAdapter.send` would.

        Args:
            request: The prepared request.
            **kwargs: `HTTPAdapter.send`'s keyword arguments.

        Returns:
            The scripted response.

        Raises:
            Exception: The scripted error, or an `AssertionError` for an unscripted request.
        """
        sent = Sent(
            request.method or "",
            request.url or "",
            {k: str(v) for k, v in request.headers.items()},
            kwargs.get("verify", True),
            self.clock.wall,
        )
        self.sent.append(sent)
        for route in self.routes:
            if not route.matches(sent):
                continue
            reply = route.replies[0] if route.replies else Reply(404)
            if len(route.replies) > 1:
                route.replies.pop(0)
            if reply.error is not None:
                raise reply.error
            return _response(request, reply)
        self.unexpected.append(f"{sent.method} {sent.url}")
        msg = f"unexpected request: {sent.method} {sent.url}"
        raise AssertionError(msg)

    def to(self, host: str) -> list[Sent]:
        """The requests sent to one host.

        Args:
            host: The host.

        Returns:
            Its requests, in order.
        """
        return [s for s in self.sent if s.host == host]


def _response(request: requests.PreparedRequest, reply: Reply) -> requests.Response:
    response = requests.Response()
    response.status_code = reply.status
    headers = dict(reply.headers)
    body = reply.body
    if isinstance(body, (dict, list)):
        body = json.dumps(body)
        headers.setdefault("Content-Type", "application/json")
    content = body.encode() if isinstance(body, str) else body
    response._content = content  # noqa: SLF001
    response._content_consumed = True  # noqa: SLF001
    response.raw = io.BytesIO(content)
    response.headers.update(headers)
    response.url = request.url or ""
    response.request = request
    response.encoding = "utf-8"
    return response


# Bodies -------------------------------------------------------------------------------------


def openalex_work(i: int) -> dict[str, object]:
    """An OpenAlex work with ID `W<i>`.

    Args:
        i: The work's number.

    Returns:
        The work, as OpenAlex's API returns it.
    """
    return {
        "id": f"https://openalex.org/W{i}",
        "title": f"OpenAlex paper {i}",
        "publication_year": 2021,
        "publication_date": "2021-03-04",
        "doi": f"https://doi.org/10.1234/oa{i}",
        "authorships": [{"author": {"display_name": "Ada Author"}}],
        "cited_by_count": 1000 - i,
        "abstract_inverted_index": {"An": [0], "abstract": [1]},
        "primary_location": {"landing_page_url": f"https://example.org/oa{i}", "pdf_url": None},
    }


def openalex_page(count: int, *, start: int = 1, total: int | None = None) -> dict[str, object]:
    """A page of OpenAlex works, numbered from `start`.

    Args:
        count: How many works the page holds.
        start: The first work's number.
        total: The `meta.count` to report; the page's own count when omitted.

    Returns:
        The page.
    """
    works = [openalex_work(i) for i in range(start, start + count)]
    return {"meta": {"count": count if total is None else total}, "results": works}


def arxiv_feed(count: int, *, start: int = 1) -> str:
    """An arXiv API Atom feed with `count` entries, which the arXiv connector accepts.

    Args:
        count: How many entries.
        start: The first entry's number.

    Returns:
        The feed's XML.
    """
    entries = "".join(
        f"""<entry>
  <id>http://arxiv.org/abs/2401.{i:05d}v1</id>
  <updated>2024-01-02T00:00:00Z</updated>
  <published>2024-01-01T00:00:00Z</published>
  <title>arXiv paper {i}</title>
  <summary>An abstract.</summary>
  <author><name>Ada Author</name></author>
  <link href="http://arxiv.org/abs/2401.{i:05d}v1" rel="alternate" type="text/html"/>
  <link title="pdf" href="http://arxiv.org/pdf/2401.{i:05d}v1" rel="related"
        type="application/pdf"/>
  <category term="cs.SE" scheme="http://arxiv.org/schemas/atom"/>
</entry>"""
        for i in range(start, start + count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
        "<title>arXiv Query</title><id>http://arxiv.org/api/x</id>"
        "<updated>2024-01-02T00:00:00Z</updated>"
        f"<opensearch:totalResults>{count}</opensearch:totalResults>"
        f"{entries}</feed>"
    )


def s2_bulk(count: int, *, start: int = 1) -> dict[str, object]:
    """A Semantic Scholar bulk search response.

    Args:
        count: How many papers.
        start: The first paper's number.

    Returns:
        The response body.
    """
    data = [
        {
            "paperId": f"s2paper{i}",
            "title": f"Semantic Scholar paper {i}",
            "abstract": "An abstract.",
            "year": 2022,
            "citationCount": 50 - i,
            "authors": [{"name": "Ada Author"}],
            "url": f"https://www.semanticscholar.org/paper/s2paper{i}",
            "publicationDate": "2022-05-06",
            "externalIds": {"DOI": f"10.5555/s2{i}"},
        }
        for i in range(start, start + count)
    ]
    return {"total": count, "token": None, "data": data}


def jsonl(path: Path) -> list[dict[str, Any]]:
    """The JSON objects in a JSON Lines file.

    Args:
        path: The file.

    Returns:
        Its objects, or none when it doesn't exist.
    """
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
