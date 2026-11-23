"""Tests of the Orca installer, tools/parallel-sessions/orca_install.py, on fixture releases."""

from __future__ import annotations

import base64
import json
import os
import re
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.parallel_sessions_support import (
    INSTALLER,
    KNOWN_VERSION,
    TAG,
    Machine,
    Release,
    Result,
    api_url,
    b64_sha512,
    download_url,
    icon_urls,
    install_package,
    requires_non_root,
    serve_release,
    snapshot,
)

if TYPE_CHECKING:
    from collections.abc import Callable

VERSIONED = f"orca-{KNOWN_VERSION}.AppImage"
# A token the installer must never send.
FAKE_TOKEN = "ghp_" + "x" * 36


def install(machine: Machine, release: Release, *extra: str) -> Result:
    """Run the installer on a downloaded package."""
    return machine.run(INSTALLER, str(release.package), "--tag", release.tag, *extra)


def assert_installed(machine: Machine, release: Release) -> None:
    """The versioned package, its record and the link are in place."""
    versioned = machine.install_dir / VERSIONED
    assert versioned.read_bytes() == release.content
    assert os.access(versioned, os.X_OK)
    record = json.loads((machine.install_dir / "install-record.json").read_text())
    assert record[KNOWN_VERSION] == b64_sha512(release.content)
    link = machine.install_dir / "orca.AppImage"
    assert link.is_symlink()
    assert str(link.readlink()) == VERSIONED


@pytest.fixture
def machine(tmp_path: Path) -> Machine:
    """A machine on Linux x86_64 with no Orca installed."""
    return Machine(tmp_path)


# --- Arguments ------------------------------------------------------------------------------


# @spec PAR-INSTALL-001
@pytest.mark.parametrize(
    "form",
    [
        lambda pkg: [pkg, "--tag", TAG],
        lambda pkg: [pkg, f"--tag={TAG}"],
        lambda pkg: ["--tag", TAG, pkg],
    ],
    ids=["separate", "equals", "option-first"],
)
def test_installer_accepts_the_usual_option_forms(
    machine: Machine, form: Callable[[str], list[str]]
) -> None:
    """The package path and `--tag` work in each of the usual forms."""
    release = serve_release(machine)
    result = machine.run(INSTALLER, *form(str(release.package)))
    assert result.returncode == 0, result.output
    assert_installed(machine, release)


# --- Checks before installing ---------------------------------------------------------------


# @spec PAR-INSTALL-002
def test_installer_refuses_a_prerelease(machine: Machine) -> None:
    """A prerelease stops the install with status 1, writing nothing."""
    release = serve_release(machine, prerelease=True)
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search("prerelease", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-002
def test_installer_refuses_a_release_github_does_not_find(machine: Machine) -> None:
    """A tag GitHub reports as not found (as it does a draft) stops the install with status 1."""
    release = serve_release(machine)
    machine.urls[api_url()] = {"status": 404, "body": ""}
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search("not found", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-003
@pytest.mark.parametrize(
    ("age", "shown_age"),
    [(timedelta(days=1), "1.0"), (timedelta(hours=-5), "0.0")],
    ids=["one-day", "future"],
)
def test_installer_refuses_a_young_release(
    machine: Machine, age: timedelta, shown_age: str
) -> None:
    """A release younger than the minimum age stops the install, giving both ages in days."""
    release = serve_release(machine, age=age)
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert shown_age in result.output
    assert "3.0" in result.output
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-003
def test_installer_takes_the_minimum_release_age_from_the_config_file(machine: Machine) -> None:
    """With `min_release_age_days = 0`, a release published an hour ago installs."""
    machine.write_config("min_release_age_days = 0\n")
    release = serve_release(machine, age=timedelta(hours=1))
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert_installed(machine, release)


# @spec PAR-INSTALL-003
def test_installer_accepts_a_release_just_over_the_minimum_age(machine: Machine) -> None:
    """A release a little over 3 days old passes the default minimum."""
    release = serve_release(machine, age=timedelta(days=3, minutes=5))
    result = install(machine, release)
    assert result.returncode == 0, result.output


# @spec PAR-INSTALL-003
def test_installer_accepts_a_release_exactly_the_minimum_age(machine: Machine) -> None:
    """With a minimum of 0, a release dated in the future (age 0) is exactly old enough."""
    machine.write_config("min_release_age_days = 0\n")
    release = serve_release(machine, age=timedelta(hours=-5))
    result = install(machine, release)
    assert result.returncode == 0, result.output


# @spec PAR-INSTALL-004
def test_allow_young_skips_only_the_age_check(machine: Machine) -> None:
    """`--allow-young` installs a young release and says the age check was skipped."""
    release = serve_release(machine, age=timedelta(hours=1))
    result = install(machine, release, "--allow-young")
    assert result.returncode == 0, result.output
    assert re.search("skip", result.output, re.IGNORECASE)
    assert_installed(machine, release)


# @spec PAR-INSTALL-004
def test_allow_young_does_not_skip_the_other_checks(machine: Machine) -> None:
    """`--allow-young` still refuses a prerelease and a file that doesn't match."""
    release = serve_release(machine, age=timedelta(hours=1), prerelease=True)
    assert install(machine, release, "--allow-young").returncode == 1
    machine.urls.clear()
    release = serve_release(machine, age=timedelta(hours=1), manifest_digest=b64_sha512(b"other"))
    assert install(machine, release, "--allow-young").returncode == 1


# @spec PAR-INSTALL-005
def test_installer_refuses_a_file_whose_sha512_differs(machine: Machine) -> None:
    """A sha512 that differs from the manifest's stops the install with status 1."""
    release = serve_release(machine, manifest_digest=b64_sha512(b"another build"))
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search(r"sha512|hash", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-006
def test_installer_refuses_a_file_whose_size_differs(machine: Machine) -> None:
    """A size that differs from the manifest's stops the install with status 1."""
    content = b"#!/bin/sh\necho orca\n"
    release = serve_release(machine, content=content, manifest_size=len(content) + 1)
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search("size", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-007
@pytest.mark.parametrize("tag", ["v1.4.269", "1.4.269"])
def test_installer_matches_the_manifest_version_to_the_tag(machine: Machine, tag: str) -> None:
    """The tag, with or without its leading `v`, matches the manifest's `version`."""
    release = serve_release(machine, tag=tag)
    result = install(machine, release)
    assert result.returncode == 0, result.output


# @spec PAR-INSTALL-007
def test_installer_refuses_a_manifest_for_another_version(machine: Machine) -> None:
    """A manifest `version` that isn't the tag's stops the install, giving both."""
    release = serve_release(machine, manifest_version="1.4.270")
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert "1.4.270" in result.output
    assert "1.4.269" in result.output
    assert snapshot(machine.home) == before


def _no_network(machine: Machine) -> None:
    for url in list(machine.urls):
        machine.urls[url] = {"error": "network"}


def _rate_limited(machine: Machine) -> None:
    machine.urls[api_url()] = {
        "status": 403,
        "headers": {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "9999999999"},
        "body": "",
    }


def _no_manifest(machine: Machine) -> None:
    machine.urls[download_url("latest-linux.yml")] = {"status": 404}


def _unparsable_manifest(machine: Machine) -> None:
    machine.urls[download_url("latest-linux.yml")] = {"body": "//4A"}  # bytes ff fe 00: not UTF-8


def _manifest_without_entry(machine: Machine) -> None:
    serve_release(machine, manifest="version: 1.4.269\nfiles:\n  - url: other.deb\n    size: 1\n")


def _entry_without_sha512(machine: Machine) -> None:
    serve_release(
        machine, manifest="version: 1.4.269\nfiles:\n  - url: orca-linux.AppImage\n    size: 20\n"
    )


def _entry_without_size(machine: Machine) -> None:
    digest = b64_sha512(b"#!/bin/sh\necho orca\n")
    serve_release(
        machine,
        manifest=f"version: 1.4.269\nfiles:\n  - url: orca-linux.AppImage\n    sha512: {digest}\n",
    )


def _manifest_without_version(machine: Machine) -> None:
    content = b"#!/bin/sh\necho orca\n"
    serve_release(
        machine,
        manifest=(
            f"files:\n  - url: orca-linux.AppImage\n    sha512: {b64_sha512(content)}\n"
            f"    size: {len(content)}\n"
        ),
    )


def _bad_record(machine: Machine) -> None:
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "install-record.json").write_text("[1, 2]")


# @spec PAR-INSTALL-008
@pytest.mark.parametrize(
    ("breakage", "named"),
    [
        (_no_network, "network|connect|request"),
        (_rate_limited, "rate"),
        (_no_manifest, "manifest"),
        (_unparsable_manifest, "manifest"),
        (_manifest_without_entry, "manifest|entry|orca-linux.AppImage"),
        (_entry_without_sha512, "sha512"),
        (_entry_without_size, "size"),
        (_manifest_without_version, "version"),
        (_bad_record, "record"),
    ],
    ids=[
        "network",
        "rate-limit",
        "no-manifest",
        "unparsable-manifest",
        "no-entry",
        "no-sha512",
        "no-size",
        "no-version",
        "bad-record",
    ],
)
def test_installer_exits_2_when_it_cannot_complete_a_check(
    machine: Machine, breakage: Callable[[Machine], None], named: str
) -> None:
    """A check that can't complete stops the install with status 2, naming it, writing nothing."""
    release = serve_release(machine)
    breakage(machine)
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 2, result.output
    assert re.search(named, result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-022
@pytest.mark.parametrize(
    "problem", ["missing", "directory", pytest.param("unreadable", marks=requires_non_root)]
)
def test_installer_refuses_a_package_path_it_cannot_read(machine: Machine, problem: str) -> None:
    """A package path that isn't a readable regular file stops the install before any request."""
    release = serve_release(machine)
    release.package.unlink()
    if problem == "directory":
        release.package.mkdir()
    elif problem == "unreadable":
        release.package.write_bytes(release.content)
        release.package.chmod(0)
    result = install(machine, release)
    assert result.returncode == 2
    assert str(release.package.name) in result.output
    assert result.events("request") == []


# @spec PAR-INSTALL-023
def test_installer_refuses_when_the_install_record_disagrees(machine: Machine) -> None:
    """A recorded sha512 for the version that isn't the file's stops the install with status 1."""
    release = serve_release(machine)
    machine.install_dir.mkdir(parents=True)
    record = {KNOWN_VERSION: b64_sha512(b"an earlier file")}
    (machine.install_dir / "install-record.json").write_text(json.dumps(record))
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search("record", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


def _prerelease_and_young(machine: Machine) -> Release:
    return serve_release(machine, prerelease=True, age=timedelta(hours=1))


def _young_and_wrong_version(machine: Machine) -> Release:
    return serve_release(machine, age=timedelta(hours=1), manifest_version="1.4.270")


def _wrong_version_and_size(machine: Machine) -> Release:
    return serve_release(machine, manifest_version="1.4.270", manifest_size=1)


def _wrong_size_and_sha512(machine: Machine) -> Release:
    return serve_release(machine, manifest_size=1, manifest_digest=b64_sha512(b"x"))


def _wrong_sha512_and_existing_file(machine: Machine) -> Release:
    install_package(machine, content=b"other content", link=False, record=False)
    return serve_release(machine, manifest_digest=b64_sha512(b"x"))


def _existing_file_and_record(machine: Machine) -> Release:
    install_package(machine, content=b"other content", link=False)
    return serve_release(machine)


def _record_and_plain_file(machine: Machine) -> Release:
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "install-record.json").write_text(
        json.dumps({KNOWN_VERSION: b64_sha512(b"x")})
    )
    (machine.install_dir / "orca.AppImage").write_bytes(b"a plain file")
    return serve_release(machine)


# @spec PAR-INSTALL-009
@pytest.mark.parametrize(
    ("setup", "first", "later"),
    [
        (_prerelease_and_young, "prerelease", r"\b3\.0\b"),
        (_young_and_wrong_version, r"\b3\.0\b", "1.4.270"),
        (_wrong_version_and_size, "1.4.270", "size"),
        (_wrong_size_and_sha512, "size", "sha512|hash"),
        (_wrong_sha512_and_existing_file, "sha512|hash", VERSIONED),
        (_existing_file_and_record, VERSIONED, "record"),
        (_record_and_plain_file, "record", "link"),
    ],
    ids=[
        "prerelease-before-age",
        "age-before-version",
        "version-before-size",
        "size-before-sha512",
        "sha512-before-existing",
        "existing-before-record",
        "record-before-link",
    ],
)
def test_installer_runs_its_checks_in_order_and_stops_at_the_first_failure(
    machine: Machine, setup: Callable[[Machine], Release], first: str, later: str
) -> None:
    """When two checks would fail, only the earlier one is reported."""
    release = setup(machine)
    result = install(machine, release)
    assert result.returncode == 1
    assert re.search(first, result.output, re.IGNORECASE)
    assert not re.search(later, result.output, re.IGNORECASE)


# --- Installing -----------------------------------------------------------------------------


# @spec PAR-INSTALL-010, PAR-INSTALL-011, PAR-INSTALL-015, PAR-INSTALL-016, PAR-INSTALL-018
def test_installer_installs_into_a_new_install_directory(machine: Machine) -> None:
    """A first install creates the directory, the package, its record, the link and the icon."""
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert_installed(machine, release)
    assert (machine.install_dir / "icon.png").read_bytes() == b"\x89PNG fake icon"
    names = {path.name for path in machine.install_dir.iterdir()}
    assert names == {VERSIONED, "install-record.json", "orca.AppImage", "icon.png"}


# @spec PAR-INSTALL-011, PAR-INSTALL-016, PAR-INSTALL-018
def test_installer_writes_through_renames_in_the_install_directory(machine: Machine) -> None:
    """The package, the link and the icon each arrive by a rename within the install directory."""
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    renamed = {Path(e["dst"]).name: e for e in result.events("rename")}
    for name in (VERSIONED, "orca.AppImage", "icon.png"):
        assert name in renamed, f"{name} wasn't renamed into place"
        assert Path(renamed[name]["src"]).parent == machine.install_dir


# @spec PAR-CONF-001
def test_installer_expands_the_install_directory_from_the_config_file(machine: Machine) -> None:
    """An `install_dir` of `~/opt/orca` installs under the home directory."""
    machine.write_config('install_dir = "~/opt/orca"\n')
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert (machine.home / "opt" / "orca" / VERSIONED).read_bytes() == release.content


# @spec PAR-INSTALL-012, PAR-INSTALL-015, PAR-INSTALL-016
def test_installer_keeps_an_identical_versioned_package(machine: Machine) -> None:
    """Reinstalling the same file leaves the versioned package alone and still links to it."""
    release = serve_release(machine)
    versioned = install_package(machine, content=release.content, link=False, record=False)
    inode = versioned.stat().st_ino
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert versioned.stat().st_ino == inode
    assert_installed(machine, release)


# @spec PAR-INSTALL-013
def test_installer_refuses_to_replace_a_different_versioned_package(machine: Machine) -> None:
    """A versioned package with other content stops the install, naming the file."""
    release = serve_release(machine)
    install_package(machine, content=b"tampered", link=False, record=False)
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert VERSIONED in result.output
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-014
def test_installer_refuses_when_orca_appimage_is_not_a_link(machine: Machine) -> None:
    """A regular file at `orca.AppImage` stops the install with status 1."""
    release = serve_release(machine)
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "orca.AppImage").write_bytes(b"a plain file")
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 1
    assert "orca.AppImage" in result.output
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-015, PAR-INSTALL-016, PAR-INSTALL-017
def test_installer_keeps_earlier_versions_and_their_records(machine: Machine) -> None:
    """An upgrade repoints the link and keeps the earlier package and its record entry."""
    earlier = install_package(machine, version="1.4.268", content=b"earlier build")
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert_installed(machine, release)
    assert earlier.read_bytes() == b"earlier build"
    record = json.loads((machine.install_dir / "install-record.json").read_text())
    assert record["1.4.268"] == b64_sha512(b"earlier build")


# @spec PAR-INSTALL-019
def test_installer_carries_on_when_the_icon_cannot_be_fetched(machine: Machine) -> None:
    """A failed icon fetch is reported, keeps any existing icon, and doesn't fail the install."""
    release = serve_release(machine, icon=False)
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "icon.png").write_bytes(b"old icon")
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert re.search("icon", result.output, re.IGNORECASE)
    assert (machine.install_dir / "icon.png").read_bytes() == b"old icon"
    assert_installed(machine, release)


# @spec PAR-INSTALL-019, PAR-INSTALL-021
def test_installer_carries_on_when_the_icon_cannot_be_written(machine: Machine) -> None:
    """A failed icon write is reported, and the finished install still exits 0."""
    release = serve_release(machine)
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "icon.png").mkdir()  # a directory can't be renamed over
    result = install(machine, release)
    assert result.returncode == 0, result.output
    assert re.search("icon", result.output, re.IGNORECASE)
    assert (machine.install_dir / "icon.png").is_dir()
    assert_installed(machine, release)
    assert not [p for p in machine.install_dir.iterdir() if p.name.startswith(".")]


# @spec PAR-INSTALL-020, PAR-INSTALL-021
def test_installer_ends_with_the_next_steps(machine: Machine) -> None:
    """A finished install says to quit Orca, re-run setup, relaunch and run the settings check."""
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    for step in ("quit", "setup", "orca-launch", "orca_settings_check"):
        assert re.search(step, result.output, re.IGNORECASE), step


# @spec PAR-PLAT-001
def test_installer_uses_the_arm64_rows_on_arm64(tmp_path: Path) -> None:
    """On arm64 the installer reads the arm64 manifest and its package's entry."""
    machine = Machine(tmp_path, platform=("Linux", "aarch64"))
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    requested = [entry["url"] for entry in result.events("request")]
    assert download_url("latest-linux-arm64.yml") in requested
    assert_installed(machine, release)


# @spec PAR-ALL-003
def test_installer_requests_only_https_without_credentials(machine: Machine) -> None:
    """Every request is HTTPS with no credentials, even with a GitHub token in the environment."""
    machine.env["GITHUB_TOKEN"] = FAKE_TOKEN
    machine.env["GH_TOKEN"] = FAKE_TOKEN
    release = serve_release(machine)
    result = install(machine, release)
    assert result.returncode == 0, result.output
    requests = result.events("request")
    assert requests
    for entry in requests:
        assert entry["url"].startswith("https://")
        assert "authorization" not in entry["headers"]
        assert FAKE_TOKEN not in json.dumps(entry)
    assert result.events("socket") == []
    assert set(icon_urls()) & {entry["url"] for entry in requests}


# @spec PAR-ALL-003, PAR-INSTALL-008
def test_installer_refuses_a_redirect_away_from_https(machine: Machine) -> None:
    """A release request that a redirect took to plain HTTP can't complete: exit 2."""
    release = serve_release(machine)
    machine.urls[api_url()]["redirected_to"] = "http://example.test/release.json"
    before = snapshot(machine.home)
    result = install(machine, release)
    assert result.returncode == 2, result.output
    assert re.search("https", result.output, re.IGNORECASE)
    assert snapshot(machine.home) == before


# @spec PAR-INSTALL-008
@pytest.mark.parametrize("tag", ["v1.4.269/../../x", "v1 4", "v1.4.269?x=1"])
def test_installer_refuses_a_tag_that_is_not_a_tag(machine: Machine, tag: str) -> None:
    """A tag with characters no release tag has stops before any request, with status 2."""
    release = serve_release(machine)
    result = machine.run(INSTALLER, str(release.package), "--tag", tag)
    assert result.returncode == 2, result.output
    assert result.events("request") == []


# @spec PAR-INSTALL-003
def test_installer_reads_a_publish_time_without_a_zone_as_utc(machine: Machine) -> None:
    """A `published_at` with no time zone is taken as UTC rather than crashing."""
    release = serve_release(machine)
    answer = machine.urls[api_url()]
    data = json.loads(base64.b64decode(answer["body"]))
    data["published_at"] = data["published_at"].removesuffix("Z")
    answer["body"] = base64.b64encode(json.dumps(data).encode()).decode()
    result = install(machine, release)
    assert result.returncode == 0, result.output
