"""Run one of the parallel-sessions Python scripts with its machine boundaries replaced.

Run as `python -I tests/parallel_sessions_shim.py <plan.json> <script> [args...]`. The plan,
written by `tests/parallel_sessions_support.py`, says what to replace:

- `platform`: the `[system, machine]` that `platform.system()`, `platform.machine()`,
  `platform.uname()` and `os.uname()` report, with `sys.platform` to match.
- `urls`: the responses `urllib.request.urlopen` gives, by URL (a body, an HTTP status, a network
  error, or the URL a redirect ended at). Any other URL gets a 404. Sockets
  are refused, so a request that bypasses `urlopen` fails rather than reaching the network.
- `processes`: when set, the command names the script's `running_command_names()` returns.
- `mutate`: `{"target": path, "content": text}`. The first time the script creates a file in the
  target's directory, other than the target itself, the target's content is replaced first: another
  program writing the file while the script prepares its own write.

Requests, renames and SQLite connections are appended to the plan's `log` as JSON lines.

What this asks of the scripts under test:
- The script is loaded as a module under its file's stem (so its `__main__` block doesn't run)
  and `main(argv)` is called with the arguments after the program name: each script defines
  `main(argv: list[str]) -> int`.
- The settings check defines `running_command_names() -> set[str]`, the command names of running
  processes, and judges whether Orca runs from it. The shim refuses to run the check without it,
  so a renamed lookup can't silently read the real process list.
- Network requests go through `urllib.request.urlopen`.
- A file is replaced by writing a temporary file beside it and calling `os.replace` (or
  `os.rename`). A lock file or other file created beside a target before the target is read
  would set off `mutate` too early.
"""

from __future__ import annotations

import base64
import builtins
import email.message
import importlib.util
import io
import json
import os
import platform
import socket
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

# The originals, typed loosely so the replacements can pass their arguments straight through.
_real_open: Callable[..., IO[Any]] = builtins.open
_real_os_open: Callable[..., int] = os.open
_real_replace: Callable[..., None] = os.replace
_real_rename: Callable[..., None] = os.rename
_real_connect: Callable[..., sqlite3.Connection] = sqlite3.connect
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT
WRITE_MODES = frozenset("wxa+")
HTTP_OK = 200
SYS_PLATFORMS = {"Linux": "linux", "Darwin": "darwin", "Windows": "win32"}
CHECK_SCRIPT = "orca_settings_check"
# The shim's own refusal: a status none of the scripts uses, so no test can mistake it for theirs.
SHIM_REFUSED = 70


def _replace(owner: object, name: str, value: object) -> None:
    """Replace an attribute of a module or class, whatever its declared type."""
    setattr(owner, name, value)


def _log(plan: dict[str, Any], event: dict[str, object]) -> None:
    with _real_open(plan["log"], "a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, default=str) + "\n")


def _path_text(path: object) -> str | None:
    """The text of a path argument, or None for a file descriptor or anything else."""
    if isinstance(path, (str, bytes, os.PathLike)):
        return os.fsdecode(path)
    return None


class _Response(io.BytesIO):
    """A urlopen response: readable bytes with a status, headers and a URL."""

    def __init__(self, url: str, body: bytes, headers: dict[str, str]) -> None:
        super().__init__(body)
        self.url = url
        self.status = HTTP_OK
        self.code = HTTP_OK
        self.reason = "OK"
        self.headers = email.message.Message()
        for key, value in headers.items():
            self.headers[key] = value

    def getcode(self) -> int:
        """The HTTP status."""
        return self.status

    def geturl(self) -> str:
        """The URL requested."""
        return self.url

    def info(self) -> email.message.Message:
        """The response headers."""
        return self.headers

    def getheader(self, name: str, default: str | None = None) -> str | None:
        """One response header, as `http.client.HTTPResponse.getheader` gives it."""
        return self.headers.get(name, default)

    def getheaders(self) -> list[tuple[str, str]]:
        """Every response header, as `http.client.HTTPResponse.getheaders` gives them."""
        return list(self.headers.items())

    @property
    def length(self) -> int:
        """The bytes not yet read."""
        return len(self.getbuffer()) - self.tell()


def _patch_network(plan: dict[str, Any]) -> None:
    urls: dict[str, dict[str, Any]] = plan.get("urls", {})

    def fake_urlopen(request: object, *_args: object, **_kwargs: object) -> _Response:
        if isinstance(request, urllib.request.Request):
            url = request.full_url
            headers = {k.lower(): v for k, v in request.header_items()}
        else:
            url = str(request)
            headers = {}
        _log(plan, {"event": "request", "url": url, "headers": headers})
        answer = urls.get(url, {"status": 404})
        if answer.get("error") == "network":
            reason = "simulated network failure"
            raise urllib.error.URLError(reason)
        status = answer.get("status", HTTP_OK)
        body = base64.b64decode(answer.get("body", ""))
        reply_headers = answer.get("headers", {})
        if status != HTTP_OK:
            message = email.message.Message()
            for key, value in reply_headers.items():
                message[key] = value
            raise urllib.error.HTTPError(url, status, "simulated", message, io.BytesIO(body))
        # `redirected_to`: the URL a followed redirect ended at, as `geturl()` reports it.
        return _Response(answer.get("redirected_to", url), body, reply_headers)

    def refuse(*_args: object, **_kwargs: object) -> None:
        _log(plan, {"event": "socket"})
        message = "the test shim refuses network connections"
        raise OSError(message)

    _replace(urllib.request, "urlopen", fake_urlopen)
    _replace(socket.socket, "connect", refuse)
    _replace(socket, "create_connection", refuse)


def _patch_platform(plan: dict[str, Any]) -> None:
    system, machine = plan.get("platform", ["Linux", "x86_64"])
    real = platform.uname()
    fake_uname = real._replace(system=system, machine=machine)
    _replace(platform, "system", lambda: system)
    _replace(platform, "machine", lambda: machine)
    _replace(platform, "uname", lambda: fake_uname)
    os_real = os.uname()
    fake = SimpleNamespace(
        sysname=system,
        nodename=os_real.nodename,
        release=os_real.release,
        version=os_real.version,
        machine=machine,
    )
    _replace(os, "uname", lambda: fake)
    _replace(sys, "platform", SYS_PLATFORMS.get(system, system.lower()))


def _mutator(plan: dict[str, Any]) -> Callable[[object], None]:
    """A function that, the first time a file is created beside the target, rewrites the target."""
    mutate = plan.get("mutate")
    done: list[bool] = []

    def maybe_mutate(path: object) -> None:
        text = _path_text(path)
        if not mutate or done or text is None:
            return
        target = Path(mutate["target"])
        created = Path(text).absolute()
        beside = created.parent in {target.parent, target.parent.resolve()}
        if beside and created.name != target.name:
            done.append(True)
            with _real_open(target, "w", encoding="utf-8") as stream:
                stream.write(mutate["content"])

    return maybe_mutate


def _patch_files(plan: dict[str, Any]) -> None:
    maybe_mutate = _mutator(plan)

    def fake_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> IO[Any]:
        if WRITE_MODES & set(mode):
            maybe_mutate(file)
        return _real_open(file, mode, *args, **kwargs)

    def fake_os_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        if flags & WRITE_FLAGS:
            maybe_mutate(path)
        return _real_os_open(path, flags, *args, **kwargs)

    def fake_replace(src: object, dst: object, *args: object, **kwargs: object) -> None:
        _log(plan, {"event": "rename", "src": _path_text(src), "dst": _path_text(dst)})
        _real_replace(src, dst, *args, **kwargs)

    def fake_rename(src: object, dst: object, *args: object, **kwargs: object) -> None:
        _log(plan, {"event": "rename", "src": _path_text(src), "dst": _path_text(dst)})
        _real_rename(src, dst, *args, **kwargs)

    def fake_connect(database: object, *args: object, **kwargs: object) -> sqlite3.Connection:
        _log(plan, {"event": "sqlite", "database": _path_text(database), "kwargs": kwargs})
        return _real_connect(database, *args, **kwargs)

    _replace(builtins, "open", fake_open)
    _replace(io, "open", fake_open)
    _replace(os, "open", fake_os_open)
    _replace(os, "replace", fake_replace)
    _replace(os, "rename", fake_rename)
    _replace(sqlite3, "connect", fake_connect)


def main() -> int:
    """Apply the plan's replacements, then run the script's `main` with the remaining arguments.

    Returns:
        The script's exit status.
    """
    plan_path, script, *args = sys.argv[1:]
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    _patch_platform(plan)
    _patch_network(plan)
    _patch_files(plan)
    script_path = Path(script).resolve()
    sys.path.insert(0, str(script_path.parent))
    sys.argv = [str(script_path), *args]
    name = script_path.stem
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        sys.stderr.write(f"shim: can't load {script_path}\n")
        return SHIM_REFUSED
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if name == CHECK_SCRIPT and not callable(getattr(module, "running_command_names", None)):
        sys.stderr.write(f"shim: {script_path.name} defines no running_command_names()\n")
        return SHIM_REFUSED
    if plan.get("processes") is not None:
        names = set(plan["processes"])
        _replace(module, "running_command_names", lambda: set(names))
    status = module.main(args)
    return int(status or 0)


if __name__ == "__main__":
    sys.exit(main())
