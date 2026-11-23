#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Verify a downloaded Orca package against its GitHub release, then install it.

Run it as `uv run --script orca_install.py <package> --tag <tag>`. It checks that the release is a
published, stable release old enough to take, and that the file matches the release's manifest,
before writing anything. It then installs the package as `orca-<version>.AppImage` in the install
directory and points `orca.AppImage` at it, keeping every earlier version.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import hashlib
import http.client
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from parallel_sessions_common import (
    DIFFERS,
    FAILED,
    OK,
    Platform,
    StopError,
    complain,
    current_platform,
    load_config,
    prepare_output,
    say,
)

REPO = "stablyai/orca"
API = "https://api.github.com/repos/{repo}/releases/tags/{tag}"
DOWNLOAD = "https://github.com/{repo}/releases/download/{tag}/{name}"
RAW = "https://raw.githubusercontent.com/{repo}/{tag}/{path}"
USER_AGENT = "parallel-sessions-orca-installer"
TIMEOUT_SECONDS = 60
SECONDS_PER_DAY = 86_400
CHUNK = 1 << 20
HTTP_NOT_FOUND = 404
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY = 429
RECORD = "install-record.json"
CURRENT = "orca.AppImage"
QUOTES = "'\""
RELEASE_CHECK = "the release"
MANIFEST_CHECK = "the release manifest"
TAG = re.compile(r"v?[0-9A-Za-z][0-9A-Za-z.+-]*")


def fetch(url: str) -> bytes:
    """GET a public HTTPS URL, sending no credentials (PAR-ALL-003).

    Raises:
        urllib.error.URLError: When the request fails (`HTTPError` for an HTTP status), or a
            redirect leaves HTTPS.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310 - fixed https URLs
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
            if not str(response.geturl()).startswith("https://"):
                reason = f"{url} redirected to {response.geturl()}, which isn't HTTPS"
                raise urllib.error.URLError(reason)
            return bytes(response.read())
    except http.client.HTTPException as error:  # a malformed URL, or a dropped download
        reason = f"{type(error).__name__}: {error}"
        raise urllib.error.URLError(reason) from error


def cannot_check(check: str, error: Exception) -> StopError:
    """The error for a check a request kept from completing (PAR-INSTALL-008)."""
    if isinstance(error, urllib.error.HTTPError):
        remaining = error.headers.get("x-ratelimit-remaining") if error.headers else None
        if error.code == HTTP_TOO_MANY or (error.code == HTTP_FORBIDDEN and remaining == "0"):
            return StopError(f"couldn't check {check}: GitHub rate-limited the request")
        return StopError(f"couldn't check {check}: GitHub answered HTTP {error.code}")
    return StopError(f"couldn't check {check}: the network request failed ({error})")


@dataclass(frozen=True)
class Package:
    """The downloaded file: its path, size and sha512."""

    path: Path
    size: int
    digest: bytes

    @property
    def digest_b64(self) -> str:
        """The sha512, base64-encoded as manifests record it."""
        return base64.b64encode(self.digest).decode()


def file_digest(path: Path) -> bytes:
    """The sha512 of a file's content."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha512").digest()


def read_package(path: Path) -> Package:
    """Hash the downloaded package (PAR-INSTALL-022).

    Raises:
        StopError: When the path isn't a readable regular file.
    """
    if not path.is_file():
        message = f"the downloaded package {path} isn't a regular file"
        raise StopError(message)
    try:
        size = path.stat().st_size
        digest = file_digest(path)
    except OSError as error:
        message = f"can't read the downloaded package {path}: {error}"
        raise StopError(message) from error
    return Package(path, size, digest)


def fetch_release(tag: str) -> dict[str, object]:
    """The release's description from GitHub's releases API.

    Raises:
        StopError: For a release not found (status 1), or a request that failed (status 2).
    """
    try:
        release = json.loads(fetch(API.format(repo=REPO, tag=tag)))
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            message = f"release {tag} not found on GitHub (a draft release also reads as not found)"
            raise StopError(message, DIFFERS) from error
        raise cannot_check(RELEASE_CHECK, error) from error
    except (urllib.error.URLError, OSError) as error:
        raise cannot_check(RELEASE_CHECK, error) from error
    except ValueError as error:
        message = f"couldn't check the release: GitHub's answer isn't JSON ({error})"
        raise StopError(message) from error
    if not isinstance(release, dict):
        message = "couldn't check the release: GitHub's answer isn't a release"
        raise StopError(message)
    return {str(key): value for key, value in release.items()}


# @spec PAR-INSTALL-002, PAR-INSTALL-003, PAR-INSTALL-004
def check_release(tag: str, min_age_days: int, *, allow_young: bool) -> None:
    """Check the release is published, stable and old enough.

    Raises:
        StopError: When a check fails (status 1) or can't be completed (status 2).
    """
    release = fetch_release(tag)
    if release.get("draft"):
        message = f"release {tag} not found on GitHub as a published release (it's a draft)"
        raise StopError(message, DIFFERS)
    if release.get("prerelease"):
        message = f"release {tag} is a prerelease"
        raise StopError(message, DIFFERS)
    if allow_young:
        say("Skipped the release-age check (--allow-young).")
        return
    try:
        published = datetime.fromisoformat(str(release["published_at"]))
    except (KeyError, ValueError) as error:
        message = "couldn't check the release's age: it has no valid published_at"
        raise StopError(message) from error
    if published.tzinfo is None:  # GitHub writes UTC with a Z; take a bare time as UTC too
        published = published.replace(tzinfo=UTC)
    age = max(0.0, (datetime.now(UTC) - published).total_seconds())
    if age < min_age_days * SECONDS_PER_DAY:
        message = (
            f"release {tag} is {age / SECONDS_PER_DAY:.1f} days old, younger than the minimum of "
            f"{min_age_days:.1f} days; pass --allow-young to install it anyway"
        )
        raise StopError(message, DIFFERS)


def _unquote(value: str) -> str:
    if len(value) > 1 and value[0] == value[-1] and value[0] in QUOTES:
        return value[1:-1]
    return value


def _key_value(text: str, number: int) -> tuple[str, str]:
    key, colon, value = text.partition(":")
    if not colon:
        message = f"line {number} isn't `key: value`"
        raise ValueError(message)
    return key.strip(), _unquote(value.strip())


def parse_manifest(text: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse an electron-builder release manifest: its top-level keys, and its `files` list.

    Raises:
        ValueError: When a line doesn't fit the format.
    """
    top: dict[str, str] = {}
    files: list[dict[str, str]] = []
    in_files = False
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            key, value = _key_value(line, number)
            in_files = key == "files" and not value
            if not in_files:
                top[key] = value
            continue
        item = line.strip()
        if item.startswith("- ") and in_files:
            files.append({})
            item = item[2:]
        elif not (in_files and files):
            message = f"line {number} is indented outside the items of `files`"
            raise ValueError(message)
        key, value = _key_value(item, number)
        files[-1][key] = value
    return top, files


def fetch_manifest(tag: str, row: Platform) -> tuple[dict[str, str], list[dict[str, str]]]:
    """The platform's release manifest, parsed.

    Raises:
        StopError: When it can't be fetched or parsed (status 2).
    """
    try:
        raw = fetch(DOWNLOAD.format(repo=REPO, tag=tag, name=row.manifest))
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            message = f"couldn't check the package: release {tag} has no manifest {row.manifest}"
            raise StopError(message) from error
        raise cannot_check(MANIFEST_CHECK, error) from error
    except (urllib.error.URLError, OSError) as error:
        raise cannot_check(MANIFEST_CHECK, error) from error
    try:
        return parse_manifest(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        message = f"couldn't check the package: the release manifest can't be parsed ({error})"
        raise StopError(message) from error


def entry_field(entry: dict[str, str], key: str, row: Platform) -> str:
    """One field of the package's manifest entry.

    Raises:
        StopError: When the entry lacks it (status 2).
    """
    if key not in entry:
        message = f"couldn't check the package: the manifest entry for {row.package} has no {key}"
        raise StopError(message)
    return entry[key]


# @spec PAR-INSTALL-005, PAR-INSTALL-006, PAR-INSTALL-007, PAR-INSTALL-008
def check_manifest(tag: str, row: Platform, package: Package) -> str:
    """Check the file against the release manifest: version, then size, then sha512.

    Returns:
        The release's version.

    Raises:
        StopError: When a check fails (status 1) or can't be completed (status 2).
    """
    top, files = fetch_manifest(tag, row)
    version = top.get("version", "")
    if not version:
        message = "couldn't check the package: the release manifest has no version"
        raise StopError(message)
    expected = tag.removeprefix("v")
    if version != expected:
        message = f"the release manifest's version {version} isn't the tag's version {expected}"
        raise StopError(message, DIFFERS)
    entry = next((item for item in files if item.get("url") == row.package), None)
    if entry is None:
        message = f"couldn't check the package: the release manifest has no entry for {row.package}"
        raise StopError(message)
    size_text = entry_field(entry, "size", row)
    if not size_text.isdigit():
        message = f"couldn't check the package: the manifest's size {size_text!r} isn't a number"
        raise StopError(message)
    if int(size_text) != package.size:
        message = f"sizes differ: the file is {package.size} bytes, the manifest says {size_text}"
        raise StopError(message, DIFFERS)
    try:
        digest = base64.b64decode(entry_field(entry, "sha512", row), validate=True)
    except (binascii.Error, ValueError) as error:
        message = "couldn't check the package: the manifest's sha512 isn't valid base64"
        raise StopError(message) from error
    if digest != package.digest:
        message = "the downloaded file's sha512 differs from the release manifest's"
        raise StopError(message, DIFFERS)
    return version


def read_record(install_dir: Path) -> dict[str, str]:
    """The install record, or an empty one when there's none yet.

    Raises:
        StopError: When it exists but isn't a JSON object of strings (status 2).
    """
    path = install_dir / RECORD
    if not path.exists():
        return {}
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        message = f"couldn't check the install record {path}: {error}"
        raise StopError(message) from error
    if not isinstance(record, dict) or not all(isinstance(v, str) for v in record.values()):
        message = f"couldn't check the install record {path}: it isn't a JSON object of sha512s"
        raise StopError(message)
    return {str(key): str(value) for key, value in record.items()}


# @spec PAR-INSTALL-013, PAR-INSTALL-014, PAR-INSTALL-023
def check_install_dir(install_dir: Path, version: str, package: Package) -> dict[str, str]:
    """Check the install directory's own state: the versioned file, the record, the link.

    Returns:
        The install record.

    Raises:
        StopError: When a check fails (status 1) or can't be completed (status 2).
    """
    versioned = install_dir / f"orca-{version}.AppImage"
    if versioned.is_symlink() or (
        versioned.exists()
        and not (versioned.is_file() and file_digest(versioned) == package.digest)
    ):
        message = f"{versioned} already exists with other content; the installer never replaces it"
        raise StopError(message, DIFFERS)
    record = read_record(install_dir)
    recorded = record.get(version)
    if recorded is not None and recorded != package.digest_b64:
        message = f"the install record holds another sha512 for {version} than the file's"
        raise StopError(message, DIFFERS)
    current = install_dir / CURRENT
    if current.exists() and not current.is_symlink():
        message = f"{current} exists and isn't a symbolic link; move it aside, then install again"
        raise StopError(message, DIFFERS)
    return record


def _remove(path: Path) -> None:
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


def write_atomically(path: Path, data: bytes, mode: int) -> None:
    """Write a file through a temporary file in its directory, renamed into place."""
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), mode)
        temporary.replace(path)
    except BaseException:
        _remove(temporary)
        raise


def copy_package(package: Package, versioned: Path) -> None:
    """Copy the package to its versioned name, through a temporary file renamed into place.

    Raises:
        StopError: When the copy doesn't match the file checked.
    """
    descriptor, name = tempfile.mkstemp(
        dir=versioned.parent, prefix=f".{versioned.name}.", suffix=".tmp"
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as target, package.path.open("rb") as source:
            for chunk in iter(lambda: source.read(CHUNK), b""):
                target.write(chunk)
            os.fchmod(target.fileno(), 0o755)
        copied = file_digest(temporary)
    except BaseException:
        _remove(temporary)
        raise
    if copied != package.digest:
        _remove(temporary)
        message = f"the copy of {package.path} doesn't match the file checked; nothing installed"
        raise StopError(message)
    temporary.replace(versioned)


def point_current_at(install_dir: Path, versioned: Path) -> None:
    """Make `orca.AppImage` a relative link to the versioned package, by renaming a new link."""
    temporary = install_dir / f".{CURRENT}.{os.getpid()}.tmp"
    _remove(temporary)
    temporary.symlink_to(versioned.name)
    try:
        temporary.replace(install_dir / CURRENT)
    except BaseException:
        _remove(temporary)
        raise


# @spec PAR-INSTALL-018, PAR-INSTALL-019
def save_icon(install_dir: Path, row: Platform, tag: str) -> None:
    """Save Orca's icon at the release's tag, carrying on without it if that fails.

    The install is complete by now, so a missing icon only leaves the menu entry as it was.
    """
    url = RAW.format(repo=REPO, tag=tag, path=row.icon_path)
    try:
        icon = fetch(url)
    except (urllib.error.URLError, OSError) as error:
        say(f"Couldn't fetch Orca's icon ({error}); the menu entry keeps any icon it has.")
        return
    try:
        write_atomically(install_dir / "icon.png", icon, 0o644)
    except OSError as error:
        say(f"Couldn't save Orca's icon ({error}); the menu entry keeps any icon it has.")


# @spec PAR-INSTALL-010, PAR-INSTALL-011, PAR-INSTALL-012, PAR-INSTALL-015, PAR-INSTALL-016
# @spec PAR-INSTALL-017
def install(row: Platform, install_dir: Path, package: Package, tag: str, version: str) -> None:
    """Install a checked package, never deleting or overwriting a versioned package."""
    record = check_install_dir(install_dir, version, package)
    install_dir.mkdir(parents=True, exist_ok=True)
    versioned = install_dir / f"orca-{version}.AppImage"
    if versioned.exists():
        say(f"{versioned.name} is already installed with the same content.")
    else:
        copy_package(package, versioned)
    record[version] = package.digest_b64
    text = json.dumps(dict(sorted(record.items())), indent=2) + "\n"
    write_atomically(install_dir / RECORD, text.encode(), 0o644)
    point_current_at(install_dir, versioned)
    save_icon(install_dir, row, tag)


def check_tag(tag: str) -> None:
    """Refuse a tag that isn't shaped like a release tag, before it reaches a URL.

    Raises:
        StopError: For a tag with characters a release tag doesn't have (status 2).
    """
    if not TAG.fullmatch(tag):
        message = f"{tag!r} isn't a release tag such as v1.4.269"
        raise StopError(message)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Read the command line."""
    parser = argparse.ArgumentParser(prog="orca_install.py", description=__doc__.splitlines()[0])
    parser.add_argument("package", type=Path, help="the downloaded Orca package")
    parser.add_argument("--tag", required=True, help="the release tag it came from, like v1.4.269")
    parser.add_argument(
        "--allow-young", action="store_true", help="skip only the minimum-release-age check"
    )
    return parser.parse_args(argv)


NEXT_STEPS = """\
Installed Orca {version} in {install_dir}. Next:
  1. Quit Orca if it's running.
  2. Re-run setup: uv run --script tools/parallel-sessions/setup.py --apply
  3. Relaunch Orca with orca-launch (or its menu entry).
  4. Check its settings, quit it, and run
     uv run --script tools/parallel-sessions/orca_settings_check.py"""


# @spec PAR-INSTALL-001, PAR-INSTALL-009, PAR-INSTALL-020, PAR-INSTALL-021, PAR-INSTALL-022
# @spec PAR-ALL-001, PAR-ALL-003
def main(argv: list[str] | None = None) -> int:
    """Check, then install; returns the exit status."""
    prepare_output()
    try:
        row = current_platform()
        args = parse_args(sys.argv[1:] if argv is None else argv)
        check_tag(args.tag)
        config = load_config(row)
        package = read_package(args.package)
        check_release(args.tag, config.min_release_age_days, allow_young=args.allow_young)
        version = check_manifest(args.tag, row, package)
        install(row, config.install_dir, package, args.tag, version)
    except StopError as error:
        complain(error.message)
        return error.status
    except OSError as error:
        complain(f"the install failed: {error}")
        return FAILED
    except Exception as error:  # noqa: BLE001 - fail closed: never exit 1 or 0 on a surprise
        complain(f"the install failed unexpectedly: {type(error).__name__}: {error}")
        return FAILED
    say(NEXT_STEPS.format(version=version, install_dir=config.install_dir))
    return OK


if __name__ == "__main__":
    sys.exit(main())
