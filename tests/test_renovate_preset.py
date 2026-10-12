"""Tests of the shared Renovate preset, statically and through the pinned Renovate CLI."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.support import PRESET, require_tool

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

RENOVATE_DEFAULT_IGNORES = [
    "**/node_modules/**",
    "**/bower_components/**",
    "**/vendor/**",
    "**/examples/**",
    "**/__tests__/**",
    "**/test/**",
    "**/tests/**",
    "**/__fixtures__/**",
]
LID = {"matchManagers": ["apm"], "matchPackageNames": ["jszmajda/lid"]}
EXEMPT_VALUES = (None, "0 days")


def _preset() -> dict[str, Any]:
    return json.loads(PRESET.read_text())


def _git_repo(root: Path, files: dict[str, str], links: dict[str, str] | None = None) -> Path:
    """Create a committed git repo with the given files and symlinks."""
    root.mkdir(parents=True)
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for name, target in (links or {}).items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "init", "-q"], cwd=root, check=True)  # noqa: S603
    subprocess.run([*git, "add", "-A"], cwd=root, check=True)  # noqa: S603
    subprocess.run([*git, "commit", "-qm", "fixture"], cwd=root, check=True)  # noqa: S603
    return root


def _renovate_log(repo: Path, dry_run: str) -> Iterator[dict[str, Any]]:
    """Run Renovate's local platform in `repo`, with the preset as its repo config.

    The preset goes in the repo's own `renovate.json`, as consumers use it, so its keys
    override those of the presets it extends. (As a global config file, its `ignorePaths`
    would instead be replaced by `config:best-practices`'s.)
    """
    renovate = require_tool("renovate")
    shutil.copy2(PRESET, repo / "renovate.json")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "add", "renovate.json"], cwd=repo, check=True)  # noqa: S603
    subprocess.run([*git, "commit", "-qm", "preset"], cwd=repo, check=True)  # noqa: S603
    env = {**os.environ, "LOG_LEVEL": "debug", "LOG_FORMAT": "json"}
    completed = subprocess.run(  # noqa: S603
        [
            renovate,
            "--platform=local",
            f"--dry-run={dry_run}",
            "--print-config",
            "--onboarding=false",
            "--require-config=required",
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    records = []
    for line in completed.stdout.splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    fatal = [record.get("msg", "") for record in records if record.get("level", 0) >= 50]
    assert completed.returncode == 0, fatal or completed.stderr[-2000:]
    yield from records


@pytest.fixture(scope="module")
def resolved_config(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """The preset after Renovate resolves its `extends` chain."""
    repo = _git_repo(tmp_path_factory.mktemp("resolved") / "repo", {"README.md": "x\n"})
    for record in _renovate_log(repo, "extract"):
        if record.get("msg", "").startswith("Full resolved config"):
            return record["config"]
    pytest.fail("Renovate logged no resolved config")


def _rules_setting(config: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [rule for rule in config.get("packageRules", []) if key in rule]


def _exempt_rules(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        rule
        for rule in _rules_setting(config, "minimumReleaseAge")
        if rule["minimumReleaseAge"] in EXEMPT_VALUES
    ]


def _matches_package_name(pattern: str, name: str) -> bool:
    """Apply Renovate's matchPackageNames semantics for exact names and /regex/ patterns."""
    if pattern.startswith("/"):
        body, _, flags = pattern[1:].rpartition("/")
        return re.search(body, name, re.IGNORECASE if "i" in flags else 0) is not None
    assert not any(char in pattern for char in "*?{"), f"glob patterns aren't allowed: {pattern}"
    return pattern == name


RULE_METADATA = {"description"}
UPDATE_TYPES = (
    "major", "minor", "patch", "pin", "pinDigest", "digest", "lockFileMaintenance", "replacement"
)  # fmt: skip


def _is_lid_rule(rule: dict[str, Any]) -> bool:
    return set(rule) - RULE_METADATA == {*LID, "automerge"} and all(
        rule[key] == value for key, value in LID.items()
    )


def _exempt_by_name(config: dict[str, Any], name: str) -> bool:
    """Whether any delay-exempt rule matches `name`, judged on its package-name matchers alone.

    A rule with other matchers too (managers, datasources) is still judged on its names,
    so a name-based exemption can't hide behind an extra key.
    """
    for rule in _exempt_rules(config):
        patterns = rule.get("matchPackageNames", []) + rule.get("matchDepNames", [])
        if any(_matches_package_name(pattern, name) for pattern in patterns):
            return True
    return False


# @spec PRESET-002
def test_extends_best_practices() -> None:
    """The preset builds on Renovate's best-practices preset."""
    assert "config:best-practices" in _preset()["extends"]


# @spec PRESET-AUTO-002
def test_pr_automerge_with_platform_automerge() -> None:
    """Updates arrive as PRs that GitHub merges once required checks pass."""
    preset = _preset()
    assert preset["automergeType"] == "pr"
    assert preset["platformAutomerge"] is True


# @spec PRESET-AGE-001
def test_three_day_minimum_release_age() -> None:
    """Third-party releases wait three days before Renovate proposes them."""
    assert _preset()["minimumReleaseAge"] == "3 days"


# @spec PRESET-PATH-001
def test_keeps_renovates_default_ignores() -> None:
    """The preset's ignorePaths repeats Renovate's defaults, which it replaces."""
    ignore_paths = _preset()["ignorePaths"]
    for pattern in RENOVATE_DEFAULT_IGNORES:
        assert pattern in ignore_paths


@pytest.mark.renovate
# @spec PRESET-001
def test_passes_the_config_validator() -> None:
    """The pinned Renovate's config validator accepts the preset."""
    validator = require_tool("renovate-config-validator")
    completed = subprocess.run(  # noqa: S603
        [validator, "--no-global", "--strict", str(PRESET)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.renovate
# @spec PRESET-AUTO-001
def test_resolved_config_automerges_everything_but_lid(resolved_config: dict[str, Any]) -> None:
    """After presets resolve, automerge is on, and only the LID rule turns it off."""
    assert resolved_config["automerge"] is True
    for update_type in UPDATE_TYPES:
        assert resolved_config.get(update_type, {}).get("automerge") is not False, update_type
    disabling = [
        rule for rule in _rules_setting(resolved_config, "automerge") if not rule["automerge"]
    ]
    assert len(disabling) == 1
    assert _is_lid_rule(disabling[0])


@pytest.mark.renovate
# @spec PRESET-AUTO-003
def test_lid_pins_never_automerge(resolved_config: dict[str, Any]) -> None:
    """The rule for LID plugin pins disables automerge."""
    assert any(
        _is_lid_rule(rule) and rule["automerge"] is False
        for rule in resolved_config["packageRules"]
    )


@pytest.mark.renovate
# @spec PRESET-AGE-002
def test_copier_templates_are_exempt_from_the_delay(resolved_config: dict[str, Any]) -> None:
    """Every copier-managed dependency is exempt from minimumReleaseAge."""
    assert any(
        set(rule) - RULE_METADATA == {"matchManagers", "minimumReleaseAge"}
        and rule["matchManagers"] == ["copier"]
        for rule in _exempt_rules(resolved_config)
    )


@pytest.mark.renovate
# @spec PRESET-AGE-003
def test_runner_images_are_exempt_from_the_delay(resolved_config: dict[str, Any]) -> None:
    """Every github-runners dependency is exempt from minimumReleaseAge."""
    assert any(
        rule.get("matchDatasources") == ["github-runners"]
        for rule in _exempt_rules(resolved_config)
    )


@pytest.mark.renovate
# @spec PRESET-AGE-004
@pytest.mark.parametrize(
    "name", ["jmbowman/agentic_development", "jmbowman/copier-python", "jmbowman/copier-rust"]
)
def test_own_repos_are_exempt_from_the_delay(resolved_config: dict[str, Any], name: str) -> None:
    """This system's own repos skip the delay."""
    assert _exempt_by_name(resolved_config, name)


@pytest.mark.renovate
# @spec PRESET-AGE-005
@pytest.mark.parametrize(
    "name",
    [
        "jmbowman/other",
        "jmbowman/copierx",
        "jmbowman/copier-1x",
        "jmbowman/copier-X",
        "renovatebot/renovate",
    ],
)
def test_no_exemption_by_owner_alone(resolved_config: dict[str, Any], name: str) -> None:
    """Other repos, including others from the same owner, wait the full delay."""
    assert not _exempt_by_name(resolved_config, name)


def _extracted_package_files(repo: Path) -> set[str]:
    files: set[str] = set()
    for record in _renovate_log(repo, "extract"):
        if record.get("msg") == "Extracted dependencies":
            for package_files in record["packageFiles"].values():
                files.update(str(package_file["packageFile"]) for package_file in package_files)
    return files


@pytest.mark.renovate
# @spec PRESET-PATH-002
def test_template_owned_paths_are_ignored_only_in_consumers(tmp_path: Path) -> None:
    """A consumer's template-owned mise files are ignored; a template repo's sources aren't."""
    pin = '[tools]\nruff = "0.6.0"\n'
    repo = _git_repo(
        tmp_path / "repo",
        {
            "mise.toml": pin,
            ".config/copier-python/mise.toml": pin,
            "template/.config/copier-python/mise.toml": pin,
            "tests/fixtures/x/mise.toml": pin,
            ".config/mise/conf.d/plain.toml": pin,
        },
        links={
            ".config/mise/conf.d/copier-python.toml": "../../copier-python/mise.toml",
            "template/.config/mise/conf.d/copier-python.toml": "../../copier-python/mise.toml",
        },
    )
    extracted = _extracted_package_files(repo)
    assert "mise.toml" in extracted
    assert "template/.config/copier-python/mise.toml" in extracted
    assert ".config/copier-python/mise.toml" not in extracted
    assert ".config/mise/conf.d/copier-python.toml" not in extracted
    assert ".config/mise/conf.d/plain.toml" not in extracted
    assert "template/.config/mise/conf.d/copier-python.toml" not in extracted
    assert "tests/fixtures/x/mise.toml" not in extracted


@pytest.mark.renovate
# @spec PRESET-AUTO-003
def test_lid_rule_matches_what_the_apm_manager_extracts(
    tmp_path: Path, resolved_config: dict[str, Any]
) -> None:
    """Renovate's apm manager extracts a LID pin under the package name the LID rule matches."""
    apm = (
        "name: fixture\nversion: 1.0.0\ndependencies:\n  apm:\n"
        "    - jszmajda/lid/plugins/linked-intent-dev#v1.2.0\n"
    )
    repo = _git_repo(tmp_path / "repo", {"apm.yml": apm})
    deps = [
        dep
        for record in _renovate_log(repo, "extract")
        if record.get("msg") == "Extracted dependencies"
        for package_file in record["packageFiles"].get("apm", [])
        for dep in package_file["deps"]
    ]
    lid_rule = next(rule for rule in resolved_config["packageRules"] if _is_lid_rule(rule))
    assert any(dep.get("packageName") in lid_rule["matchPackageNames"] for dep in deps), deps
