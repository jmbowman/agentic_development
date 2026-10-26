"""Tests of this repo's own setup: skills layout, ignore rule, APM pin, tasks, LID gate and hook."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tarfile
import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from tests.support import PRESET, REPO_ROOT, git_repo, load_workflow, renovate_log

if TYPE_CHECKING:
    from pathlib import Path

SKILLS = REPO_ROOT / "skills"
CLAUDE_SKILLS = REPO_ROOT / ".claude" / "skills"
AGENTS_SKILLS = REPO_ROOT / ".agents" / "skills"
APM_YML = REPO_ROOT / "apm.yml"
APM_LOCK = REPO_ROOT / "apm.lock.yaml"
MISE_TOML = REPO_ROOT / "mise.toml"
GITIGNORE = REPO_ROOT / ".gitignore"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
HOOK = REPO_ROOT / ".claude" / "hooks" / "session-start.sh"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
OWN_RENOVATE = REPO_ROOT / ".github" / "renovate.json"

LID_DEPENDENCY = re.compile(r"jszmajda/lid/plugins/linked-intent-dev#v\d+\.\d+\.\d+")
DEPLOYED_SKILL = re.compile(r"\.claude/skills/([^/]+)")
EXACT_VERSION = re.compile(r"\d+\.\d+\.\d+")


# --- Shared readers ------------------------------------------------------------------------


def own_skills(root: Path = REPO_ROOT) -> list[str]:
    """Return the names of the skills developed in a repo: directories of `skills/` with a SKILL.md.

    Args:
        root: The repo root.

    Returns:
        The skill names, sorted.
    """
    skills = root / "skills"
    return sorted(p.name for p in skills.iterdir() if (p / "SKILL.md").is_file())


def lid_entries(lock: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the lock file's entries for LID's linked-intent-dev package.

    Args:
        lock: A parsed `apm.lock.yaml`.

    Returns:
        Every matching entry.
    """
    return [
        entry
        for entry in lock.get("dependencies") or []
        if entry.get("repo_url") == "jszmajda/lid"
        and entry.get("virtual_path") == "plugins/linked-intent-dev"
    ]


def lid_skills(lock: dict[str, Any]) -> list[str]:
    """Return the names of the skills LID's lock entry deploys.

    Args:
        lock: A parsed `apm.lock.yaml` with exactly one LID entry.

    Returns:
        The skill names, sorted.
    """
    (entry,) = lid_entries(lock)
    names = (DEPLOYED_SKILL.fullmatch(path) for path in entry.get("deployed_files", []))
    return sorted(match.group(1) for match in names if match)


def _lock() -> dict[str, Any]:
    """Parse this repo's `apm.lock.yaml`."""
    return yaml.safe_load(APM_LOCK.read_text())


def _mise() -> dict[str, Any]:
    """Parse this repo's `mise.toml`."""
    return tomllib.loads(MISE_TOML.read_text())


def _mise_version() -> str:
    """Return the hook's `MISE_VERSION`."""
    match = re.search(r"^MISE_VERSION=(\S+)$", HOOK.read_text(), flags=re.MULTILINE)
    assert match, f"{HOOK.relative_to(REPO_ROOT)} has no MISE_VERSION= line"
    version = match.group(1)
    assert isinstance(version, str)
    return version


def _mise_action_steps() -> list[tuple[str, dict[str, Any]]]:
    """Return each workflow step that uses jdx/mise-action, with its workflow's file name."""
    steps = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for job in load_workflow(path)["jobs"].values():
            steps.extend(
                (path.name, step)
                for step in job.get("steps", [])
                if str(step.get("uses", "")).startswith("jdx/mise-action@")
            )
    return steps


# --- Layout ----------------------------------------------------------------------------------


def layout_problems(root: Path, own: list[str], lid: list[str]) -> list[str]:
    """Return each way a repo's skill directories differ from the layout the specs require.

    Args:
        root: The repo root.
        own: The names of the skills developed in the repo.
        lid: The names of the skills LID's package deploys.

    Returns:
        One message per problem; empty when the layout is right.
    """
    claude, agents = root / ".claude" / "skills", root / ".agents" / "skills"
    problems = [
        f"{d.relative_to(root)} must be a real directory, not a link or missing"
        for d in (claude, agents)
        if d.is_symlink() or not d.is_dir()
    ]
    if problems:
        return problems
    problems.extend(
        f"{name} is the name of both a skill in skills/ and one of LID's skills"
        for name in sorted(set(own) & set(lid))
    )
    wanted_claude = {name: f"../../skills/{name}" for name in own}
    wanted_agents = {name: f"../../.claude/skills/{name}" for name in lid}
    wanted_agents.update({name: f"../../skills/{name}" for name in own})
    for directory, wanted in ((claude, wanted_claude), (agents, wanted_agents)):
        for name, target in wanted.items():
            link = directory / name
            if not link.is_symlink():
                problems.append(f"{link.relative_to(root)} is missing: link it to {target}")
            elif str(link.readlink()) != target:
                problems.append(
                    f"{link.relative_to(root)} points to {link.readlink()}, not {target}"
                )
    for entry in sorted(claude.iterdir()):
        installed = entry.name in lid and entry.is_dir() and not entry.is_symlink()
        if entry.name not in wanted_claude and not installed:
            problems.append(f"{entry.relative_to(root)} is unexpected: delete it")
    problems.extend(
        f"{entry.relative_to(root)} is unexpected: delete it"
        for entry in sorted(agents.iterdir())
        if entry.name not in wanted_agents
    )
    problems.extend(
        f"{entry.relative_to(root)} doesn't resolve to a directory; run `mise run skills`"
        for directory in (claude, agents)
        for entry in sorted(directory.iterdir())
        if entry.is_symlink() and not entry.is_dir()
    )
    return problems


# @spec SETUP-LAYOUT-001
def test_claude_skills_is_a_real_directory() -> None:
    """Installed skills sit beside the links as real files."""
    assert CLAUDE_SKILLS.is_dir()
    assert not CLAUDE_SKILLS.is_symlink()


# @spec SETUP-LAYOUT-002
def test_agents_skills_is_a_real_directory() -> None:
    """A skill can be offered to other agents without offering it to Claude Code."""
    assert AGENTS_SKILLS.is_dir()
    assert not AGENTS_SKILLS.is_symlink()


# @spec SETUP-LAYOUT-003, SETUP-LAYOUT-004, SETUP-LAYOUT-005, SETUP-LAYOUT-006, SETUP-LAYOUT-007
# @spec SETUP-LAYOUT-010
def test_skills_layout() -> None:
    """Every agent here sees the skills developed here and LID's, and nothing else."""
    own, lid = own_skills(), lid_skills(_lock())
    assert own, "skills/ has no skill"
    assert lid, "apm.lock.yaml's LID entry deploys no skill"
    problems = layout_problems(REPO_ROOT, own, lid)
    assert not problems, "\n".join(problems)


def _layout_fixture(root: Path, *, claude: dict[str, str], agents: dict[str, str]) -> Path:
    """Build a repo with one own skill `own`, LID skill `lid` installed, and the given links.

    Args:
        root: The directory to build in.
        claude: Link targets in `.claude/skills/`, by name.
        agents: Link targets in `.agents/skills/`, by name.

    Returns:
        `root`.
    """
    (root / "skills" / "own").mkdir(parents=True)
    (root / "skills" / "own" / "SKILL.md").write_text("---\nname: own\n---\n")
    (root / ".claude" / "skills" / "lid").mkdir(parents=True)
    (root / ".agents" / "skills").mkdir(parents=True)
    for base, links in (
        (root / ".claude" / "skills", claude),
        (root / ".agents" / "skills", agents),
    ):
        for name, target in links.items():
            (base / name).symlink_to(target)
    return root


GOOD_CLAUDE = {"own": "../../skills/own"}
GOOD_AGENTS = {"own": "../../skills/own", "lid": "../../.claude/skills/lid"}


def test_good_layout_fixture_passes(tmp_path: Path) -> None:
    """The fixture the layout tests break is itself a correct layout."""
    root = _layout_fixture(tmp_path, claude=GOOD_CLAUDE, agents=GOOD_AGENTS)
    assert layout_problems(root, ["own"], ["lid"]) == []


# @spec SETUP-LAYOUT-008
@pytest.mark.parametrize(
    ("claude", "named"),
    [(GOOD_CLAUDE, ".agents/skills/lid"), ({**GOOD_CLAUDE, "own": "../../skills/gone"}, None)],
    ids=["agents", "claude"],
)
def test_dangling_link_says_to_install(
    tmp_path: Path, claude: dict[str, str], named: str | None
) -> None:
    """A dangling link in either directory points the reader at the install task."""
    root = _layout_fixture(tmp_path, claude=claude, agents=GOOD_AGENTS)
    if named is None:
        named = ".claude/skills/own"
    else:
        (root / ".claude" / "skills" / "lid").rmdir()
    problems = layout_problems(root, ["own"], ["lid"])
    assert any(named in p and "mise run skills" in p for p in problems), problems


# @spec SETUP-LAYOUT-009
@pytest.mark.parametrize(
    ("claude", "agents", "named"),
    [
        ({}, GOOD_AGENTS, ".claude/skills/own"),
        ({"own": "../skills/own"}, GOOD_AGENTS, ".claude/skills/own"),
        (GOOD_CLAUDE, {"lid": "../../.claude/skills/lid"}, ".agents/skills/own"),
        (GOOD_CLAUDE, {"own": "../../skills/own"}, ".agents/skills/lid"),
        (GOOD_CLAUDE, {**GOOD_AGENTS, "own": "../skills/own"}, ".agents/skills/own"),
        ({**GOOD_CLAUDE, "extra": "../../skills/own"}, GOOD_AGENTS, ".claude/skills/extra"),
        (GOOD_CLAUDE, {**GOOD_AGENTS, "extra": "../../skills/own"}, ".agents/skills/extra"),
    ],
    ids=[
        "missing-claude-own",
        "wrong-claude-target",
        "missing-agents-own",
        "missing-agents-lid",
        "wrong-agents-target",
        "extra-claude",
        "extra-agents",
    ],
)
def test_layout_problem_is_named(
    tmp_path: Path, claude: dict[str, str], agents: dict[str, str], named: str
) -> None:
    """Each missing, mistargeted or extra link is reported by its path."""
    root = _layout_fixture(tmp_path, claude=claude, agents=agents)
    problems = layout_problems(root, ["own"], ["lid"])
    assert any(named in p for p in problems), problems


# @spec SETUP-LAYOUT-009
def test_every_unexpected_entry_is_named(tmp_path: Path) -> None:
    """A leftover skill, a link in place of an installed skill and a stray file are all named."""
    root = _layout_fixture(tmp_path, claude=GOOD_CLAUDE, agents=GOOD_AGENTS)
    claude = root / ".claude" / "skills"
    (claude / "dropped").mkdir()
    (claude / "lid").rmdir()
    (claude / "lid").symlink_to("../../skills/own")
    (root / ".agents" / "skills" / "notes.txt").write_text("x\n")
    problems = "\n".join(layout_problems(root, ["own"], ["lid"]))
    for named in (".claude/skills/dropped", ".claude/skills/lid", ".agents/skills/notes.txt"):
        assert named in problems, problems


# @spec SETUP-LAYOUT-010
def test_name_clash_is_named(tmp_path: Path) -> None:
    """A skill developed here can't share a name with one of LID's."""
    root = _layout_fixture(tmp_path, claude=GOOD_CLAUDE, agents=GOOD_AGENTS)
    problems = layout_problems(root, ["own", "lid"], ["lid"])
    assert any("lid is the name of both" in p for p in problems), problems


# --- Ignore rule -----------------------------------------------------------------------------


def _ignored(path: str) -> bool:
    """Whether `.gitignore`'s rules ignore `path`, whether or not git tracks it.

    Args:
        path: A path relative to the repo root.

    Returns:
        True when a rule ignores it.
    """
    completed = subprocess.run(  # noqa: S603
        ["git", "check-ignore", "-q", "--no-index", path],  # noqa: S607
        cwd=REPO_ROOT,
        check=False,
    )
    assert completed.returncode in {0, 1}, f"git check-ignore failed on {path}"
    return completed.returncode == 0


# @spec SETUP-IGNORE-001
def test_apm_cache_is_ignored() -> None:
    """APM's download cache never reaches a commit."""
    assert _ignored("apm_modules/jszmajda/lid")


# @spec SETUP-IGNORE-002
def test_installed_lid_skills_are_ignored() -> None:
    """Installed skills are rebuilt from the lock file, so they're never committed."""
    names = lid_skills(_lock())
    assert names
    assert [name for name in names if not _ignored(f".claude/skills/{name}")] == []


# @spec SETUP-IGNORE-003
def test_own_skill_links_are_not_ignored() -> None:
    """The links to skills developed here are committed."""
    names = own_skills()
    assert names
    assert [name for name in names if _ignored(f".claude/skills/{name}")] == []


# @spec SETUP-IGNORE-004
def test_every_negation_names_an_own_skill() -> None:
    """A stale `!` line can't let an installed skill of the same name into a commit."""
    allowed = {f"!/.claude/skills/{name}" for name in own_skills()}
    negations = [
        line for line in GITIGNORE.read_text().splitlines() if line.startswith("!/.claude/skills/")
    ]
    assert [line for line in negations if line not in allowed] == []


# --- APM pin ---------------------------------------------------------------------------------


# @spec SETUP-APM-001
def test_apm_deploys_only_for_claude() -> None:
    """APM writes one copy of each skill, under `.claude/skills/`."""
    assert yaml.safe_load(APM_YML.read_text())["targets"] == ["claude"]


# @spec SETUP-APM-002
def test_apm_pins_only_lid_at_a_release_tag() -> None:
    """The manifest pins LID's core plugin at a release, and nothing else."""
    dependencies = yaml.safe_load(APM_YML.read_text())["dependencies"]
    assert {key: value for key, value in dependencies.items() if key != "apm" and value} == {}
    (dependency,) = dependencies["apm"]
    assert isinstance(dependency, str)
    assert LID_DEPENDENCY.fullmatch(dependency), dependency


# @spec SETUP-APM-003
def test_apm_tool_is_pinned_exactly() -> None:
    """Every install uses the same APM release."""
    pin = _mise()["tools"]["apm"]
    version = pin.get("version") if isinstance(pin, dict) else pin
    assert isinstance(version, str)
    assert EXACT_VERSION.fullmatch(version), version


# --- Tasks -----------------------------------------------------------------------------------


# @spec SETUP-TASK-001
def test_skills_task_installs_from_the_lock() -> None:
    """The install task deploys exactly what the lock file records, from the repo root."""
    task = _mise()["tasks"]["skills"]
    run = task["run"] if isinstance(task["run"], list) else [task["run"]]
    assert run == ["apm install --frozen"]
    assert task.get("dir", "{{config_root}}") == "{{config_root}}"


# @spec SETUP-TASK-002
def test_setup_installs_tools_then_skills_then_hooks() -> None:
    """A fresh clone gets its tools, then its skills, then its git hooks."""
    assert _mise()["tasks"]["setup"]["run"] == [
        "mise install",
        "mise run skills",
        "prek install -c .config/prek.toml",
    ]


# @spec SETUP-TASK-003
def test_tests_install_the_skills_first() -> None:
    """`mise run check` installs the skills its layout tests read, in CI and locally alike."""
    assert "skills" in _mise()["tasks"]["test"]["depends"]


# --- LID version gate ------------------------------------------------------------------------


def lid_version_problems(agents_md: str, lock: dict[str, Any]) -> list[str]:
    """Return why the instruction file's LID version disagrees with the locked LID package.

    Args:
        agents_md: The text of `AGENTS.md`.
        lock: A parsed `apm.lock.yaml`.

    Returns:
        One message per problem; empty when the versions agree.
    """
    entries = lid_entries(lock)
    if len(entries) != 1:
        return [f"apm.lock.yaml has {len(entries)} LID entries, not exactly one"]
    locked = entries[0].get("version")
    if not isinstance(locked, str):
        return [f"apm.lock.yaml's LID version {locked!r} isn't a string"]
    lines = agents_md.splitlines()
    starts = [i for i, line in enumerate(lines) if line == "## LID"]
    if len(starts) != 1:
        return [f"AGENTS.md has {len(starts)} `## LID` blocks, not exactly one"]
    block = []
    for line in lines[starts[0] + 1 :]:
        if line.startswith("#"):
            break
        block.append(line)
    versions = [
        line.removeprefix("- Version:").strip() for line in block if line.startswith("- Version:")
    ]
    if len(versions) != 1:
        return [f"AGENTS.md's `## LID` block has {len(versions)} `- Version:` bullets, not one"]
    if versions[0] != locked:
        return [
            (
                f"AGENTS.md records LID {versions[0]}, but apm.lock.yaml pins LID {locked}: "
                f"run /update-lid to walk the docs to {locked}"
            )
        ]
    return []


# @spec SETUP-GATE-001, SETUP-GATE-002, SETUP-GATE-003, SETUP-GATE-004
def test_lid_version_matches_the_lock() -> None:
    """The docs conform to the LID release whose skills are installed."""
    problems = lid_version_problems(AGENTS_MD.read_text(), _lock())
    assert not problems, "\n".join(problems)


def _lid_lock(*versions: Any) -> dict[str, Any]:  # noqa: ANN401
    """Build a parsed lock file with one LID entry per version, beside an unrelated entry."""
    entries = [
        {"repo_url": "jszmajda/lid", "virtual_path": "plugins/linked-intent-dev", "version": v}
        for v in versions
    ]
    return {"dependencies": [{"repo_url": "jmbowman/agentic_development"}, *entries]}


GOOD_AGENTS_MD = "# Repo\n\n## LID\n- Mode: Full\n- Version: 1.4.0\n\n## Other\n- Version: 9.9.9\n"


def test_gate_passes_matching_versions() -> None:
    """Text after the next heading isn't part of the `## LID` block."""
    assert lid_version_problems(GOOD_AGENTS_MD, _lid_lock("1.4.0")) == []


# @spec SETUP-GATE-001
def test_gate_names_both_versions_and_the_walk() -> None:
    """A LID bump without its walk fails, saying what to run."""
    (problem,) = lid_version_problems(GOOD_AGENTS_MD, _lid_lock("1.5.0"))
    assert "1.4.0" in problem
    assert "1.5.0" in problem
    assert "/update-lid" in problem


# @spec SETUP-GATE-001
def test_gate_compares_versions_as_written() -> None:
    """A version YAML reads as a number can't pass by coincidence."""
    assert lid_version_problems(GOOD_AGENTS_MD.replace("1.4.0", "1.4"), _lid_lock(1.4))


# @spec SETUP-GATE-002
@pytest.mark.parametrize("versions", [(), ("1.4.0", "1.4.0")], ids=["none", "two"])
def test_gate_needs_exactly_one_lid_entry(versions: tuple[str, ...]) -> None:
    """Without a single LID entry, there's no pinned version to compare."""
    assert lid_version_problems(GOOD_AGENTS_MD, _lid_lock(*versions))


# @spec SETUP-GATE-003
@pytest.mark.parametrize(
    "agents_md",
    ["# Repo\n", "# Repo\n\n## LID\n- Mode: Full\n\n## Other\n- Version: 1.4.0\n"],
    ids=["no-block", "no-bullet"],
)
def test_gate_needs_a_version_bullet(agents_md: str) -> None:
    """A missing block or bullet fails rather than passing for want of a version."""
    assert lid_version_problems(agents_md, _lid_lock("1.4.0"))


# @spec SETUP-GATE-004
@pytest.mark.parametrize(
    "agents_md",
    [
        GOOD_AGENTS_MD + "\n## LID\n- Version: 1.4.0\n",
        "## LID\n- Version: 1.4.0\n- Version: 1.4.0\n",
    ],
    ids=["two-blocks", "two-bullets"],
)
def test_gate_rejects_duplicates(agents_md: str) -> None:
    """Two versions can't both be the one the docs conform to."""
    assert lid_version_problems(agents_md, _lid_lock("1.4.0"))


# --- Cloud-session hook ----------------------------------------------------------------------

STUB_MISE = """#!/bin/bash
# A stand-in for mise that logs each call and fails the one named in STUB_FAIL.
words=""
for arg in "$@"; do case "$arg" in -*) ;; *) words="$words $arg" ;; esac; done
words="${words# }"
if [ "$1" = "--version" ]; then echo "@VERSION@ linux-x64 (2026-10-15)"; exit 0; fi
echo "$PWD|${MISE_TASK_RUN_AUTO_INSTALL-unset}|$words" >> "$STUB_LOG"
if [ -n "${STUB_FAIL:-}" ] && [ "$words" = "$STUB_FAIL" ]; then echo "stub failure" >&2; exit 1; fi
if [ "$words" = "bin-paths" ]; then
  [ -n "${STUB_NO_PATHS:-}" ] || { echo /stub/one/bin; echo /stub/two/bin; }
  exit 0
fi
echo "stub mise output"
"""

BROKEN_MISE = "#!/bin/bash\nexit 1\n"

STUB_CURL = """#!/bin/bash
# A stand-in for curl that serves files from RELEASE_DIR by the URL's last path segment.
out="" url=""
while [ $# -gt 0 ]; do
  case "$1" in -o) out="$2"; shift 2 ;; -*) shift ;; *) url="$1"; shift ;; esac
done
echo "$url" >> "$CURL_LOG"
[ -f "$RELEASE_DIR/${url##*/}" ] || exit 22
cp "$RELEASE_DIR/${url##*/}" "$out"
"""

HOOK_STEPS = ["trust", "install apm", "run skills", "install"]
OTHER_ENV_LINE = "export UNRELATED=1"


@dataclass
class HookRun:
    """The result of running the hook against stubs."""

    returncode: int
    stdout: str
    calls: list[tuple[str, str, str]]
    urls: list[str]
    home: Path
    env_file: Path

    def output(self) -> dict[str, Any]:
        """Parse stdout, which must be exactly one JSON object and a newline.

        Returns:
            The object's `hookSpecificOutput`.
        """
        assert self.stdout.endswith("\n"), repr(self.stdout)
        assert self.stdout.count("\n") == 1, repr(self.stdout)
        return json.loads(self.stdout)["hookSpecificOutput"]

    def steps(self) -> list[str]:
        """Return the mise commands the hook ran, without flags, in order."""
        return [words for _, _, words in self.calls if words != "bin-paths"]


def _stub(path: Path, text: str) -> None:
    """Write an executable script, creating its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)


def _release(directory: Path, version: str, checksums: str) -> None:
    """Write a fake mise release: its archive and a `SHASUMS256.txt` of the given kind.

    Args:
        directory: Where to write the release's files.
        version: The release's mise version.
        checksums: `good`, `no-line`, `bad-hash`, or `no-archive` (a good checksum file but
            no archive to download).
    """
    asset = f"mise-v{version}-linux-x64.tar.gz"
    staging = directory / "staging" / "mise" / "bin" / "mise"
    _stub(staging, STUB_MISE.replace("@VERSION@", version))
    with tarfile.open(directory / asset, "w:gz") as archive:
        archive.add(directory / "staging" / "mise", arcname="mise")
    digest = hashlib.sha256((directory / asset).read_bytes()).hexdigest()
    lines = {
        "good": f"{digest}  ./{asset}\n",
        "no-archive": f"{digest}  ./{asset}\n",
        "no-line": f"{digest}  ./mise-v{version}-macos-arm64.tar.gz\n",
        "bad-hash": f"{'0' * 64}  ./{asset}\n",
    }
    (directory / "SHASUMS256.txt").write_text(lines[checksums])
    if checksums == "no-archive":
        (directory / asset).unlink()


@dataclass
class HookSandbox:
    """A temporary home, project and stub set for running the hook, reusable across runs."""

    root: Path
    env: dict[str, str]

    @property
    def home(self) -> Path:
        """The hook's home directory."""
        return self.root / "home"

    @property
    def env_file(self) -> Path:
        """The file `CLAUDE_ENV_FILE` names, when it's set."""
        return self.root / "env"

    def run(self) -> HookRun:
        """Run the hook in this sandbox.

        Returns:
            What the hook printed and did.
        """
        for log in ("mise.log", "curl.log"):
            (self.root / log).unlink(missing_ok=True)
        completed = subprocess.run(  # noqa: S603
            ["/bin/bash", str(HOOK)],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        log, curl_log = self.root / "mise.log", self.root / "curl.log"
        lines = log.read_text().splitlines() if log.exists() else []
        calls = [(cwd, auto, words) for cwd, auto, words in (line.split("|", 2) for line in lines)]
        urls = curl_log.read_text().splitlines() if curl_log.exists() else []
        return HookRun(
            completed.returncode, completed.stdout, calls, urls, self.home, self.env_file
        )


def hook_sandbox(  # noqa: PLR0913
    tmp_path: Path,
    *,
    remote: str | None = "true",
    installed: str | None = None,
    checksums: str = "good",
    fail: str | None = None,
    env_file: bool = True,
) -> HookSandbox:
    """Set up a temporary home with a stub mise and curl for running the hook.

    The hook's environment holds only what's set here and the system `PATH`, behind the stubs.

    Args:
        tmp_path: A fresh directory for the sandbox.
        remote: The value of `CLAUDE_CODE_REMOTE`, or None to leave it unset.
        installed: The version of a mise already in `~/.local/bin`, `broken` for one whose
            `--version` fails, or None for none.
        checksums: The kind of release `_release` serves.
        fail: The flagless mise command the stub fails, such as `run skills`.
        env_file: Whether to set `CLAUDE_ENV_FILE`, to a file holding one unrelated line.

    Returns:
        The sandbox.
    """
    for name in ("home", "project", "stubs", "release"):
        (tmp_path / name).mkdir()
    if installed == "broken":
        _stub(tmp_path / "home" / ".local" / "bin" / "mise", BROKEN_MISE)
    elif installed is not None:
        _stub(
            tmp_path / "home" / ".local" / "bin" / "mise",
            STUB_MISE.replace("@VERSION@", installed),
        )
    _release(tmp_path / "release", _mise_version(), checksums)
    _stub(tmp_path / "stubs" / "curl", STUB_CURL)
    (tmp_path / "env").write_text(f"{OTHER_ENV_LINE}\n")
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": f"{tmp_path / 'stubs'}:{os.environ['PATH']}",
        "CLAUDE_PROJECT_DIR": str(tmp_path / "project"),
        "STUB_LOG": str(tmp_path / "mise.log"),
        "CURL_LOG": str(tmp_path / "curl.log"),
        "RELEASE_DIR": str(tmp_path / "release"),
    }
    if remote is not None:
        env["CLAUDE_CODE_REMOTE"] = remote
    if fail is not None:
        env["STUB_FAIL"] = fail
    if env_file:
        env["CLAUDE_ENV_FILE"] = str(tmp_path / "env")
    return HookSandbox(tmp_path, env)


# @spec SETUP-HOOK-001
def test_hook_is_registered_for_every_session_start() -> None:
    """The hook runs on startup, resume, clear and compact alike."""
    settings = json.loads(SETTINGS.read_text())
    (entry,) = settings["hooks"]["SessionStart"]
    assert "matcher" not in entry
    (hook,) = entry["hooks"]
    assert hook == {
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh",
    }


# @spec SETUP-HOOK-002
@pytest.mark.parametrize("remote", [None, "false", "1"], ids=["unset", "false", "one"])
def test_hook_does_nothing_locally(tmp_path: Path, remote: str | None) -> None:
    """Local sessions keep the developer's own mise."""
    run = hook_sandbox(tmp_path, remote=remote).run()
    assert run.returncode == 0
    assert run.stdout == ""
    assert run.calls == []
    assert run.urls == []
    assert list(run.home.iterdir()) == []
    assert run.env_file.read_text() == f"{OTHER_ENV_LINE}\n"


# @spec SETUP-HOOK-003
def test_hook_installs_mise_from_its_release(tmp_path: Path) -> None:
    """A fresh container gets the pinned mise, verified against the release's checksums."""
    version = _mise_version()
    run = hook_sandbox(tmp_path).run()
    base = f"https://github.com/jdx/mise/releases/download/v{version}"
    assert sorted(run.urls) == sorted(
        [f"{base}/mise-v{version}-linux-x64.tar.gz", f"{base}/SHASUMS256.txt"]
    )
    installed = run.home / ".local" / "bin" / "mise"
    assert installed.read_text() == STUB_MISE.replace("@VERSION@", version)
    assert run.steps() == HOOK_STEPS


# @spec SETUP-HOOK-003
@pytest.mark.parametrize("installed", ["2000.1.1", "broken"], ids=["older", "broken"])
def test_hook_replaces_another_mise(tmp_path: Path, installed: str) -> None:
    """A container whose mise isn't the pinned one, or doesn't run, gets the pinned one."""
    run = hook_sandbox(tmp_path, installed=installed).run()
    assert len(run.urls) == 2
    assert _mise_version() in (run.home / ".local" / "bin" / "mise").read_text()


# @spec SETUP-HOOK-003
def test_hook_keeps_the_pinned_mise(tmp_path: Path) -> None:
    """A reused container doesn't download mise again."""
    run = hook_sandbox(tmp_path, installed=_mise_version()).run()
    assert run.urls == []
    assert run.steps() == HOOK_STEPS


# @spec SETUP-HOOK-004
@pytest.mark.parametrize("checksums", ["no-line", "bad-hash"])
def test_hook_rejects_an_unverified_mise(tmp_path: Path, checksums: str) -> None:
    """A download that doesn't match the release's checksums is never installed."""
    run = hook_sandbox(tmp_path, installed="2000.1.1", checksums=checksums).run()
    assert "2000.1.1" in (run.home / ".local" / "bin" / "mise").read_text()
    assert run.returncode == 0
    assert "installing mise" in run.output()["additionalContext"]
    assert run.calls == []


# @spec SETUP-HOOK-005
def test_hook_installs_skills_before_other_tools(tmp_path: Path) -> None:
    """Skills need only apm, so an unrelated tool's failure can't cost the session its skills."""
    run = hook_sandbox(tmp_path, installed=_mise_version()).run()
    assert run.steps() == HOOK_STEPS
    assert {cwd for cwd, _, _ in run.calls} == {str(tmp_path / "project")}
    auto_install = {words: auto for _, auto, words in run.calls}
    assert auto_install["run skills"] == "false"


# @spec SETUP-HOOK-006
def test_hook_puts_tools_on_path_once(tmp_path: Path) -> None:
    """Later commands find mise and its tools, and a resumed session doesn't stack lines."""
    sandbox = hook_sandbox(tmp_path, installed=_mise_version())
    line = f'export PATH="{sandbox.home / ".local" / "bin"}:/stub/one/bin:/stub/two/bin:$PATH"'
    for _ in range(2):
        sandbox.run()
        assert sandbox.env_file.read_text() == f"{OTHER_ENV_LINE}\n{line}\n"


# @spec SETUP-HOOK-007
def test_hook_fails_without_an_env_file(tmp_path: Path) -> None:
    """Without CLAUDE_ENV_FILE, later commands couldn't find the tools, so the agent is told."""
    run = hook_sandbox(tmp_path, installed=_mise_version(), env_file=False).run()
    assert run.returncode == 0
    assert "CLAUDE_ENV_FILE" in run.output()["additionalContext"]


# @spec SETUP-HOOK-008
@pytest.mark.parametrize(
    ("failing", "missing"),
    [
        ("trust", "LID skills"),
        ("install apm", "LID skills"),
        ("run skills", "LID skills"),
        ("install", "pinned tools"),
    ],
)
def test_hook_stops_at_a_failed_step_and_tells_the_agent(
    tmp_path: Path, failing: str, missing: str
) -> None:
    """A failed step stops the hook, and its notice says what failed and what's missing."""
    run = hook_sandbox(tmp_path, installed=_mise_version(), fail=failing).run()
    assert run.returncode == 0
    assert run.steps() == HOOK_STEPS[: HOOK_STEPS.index(failing) + 1]
    notice = run.output()["additionalContext"]
    assert re.search(rf"mise {failing}\b(?! apm)", notice), notice
    assert missing in notice, notice
    assert run.env_file.read_text() == f"{OTHER_ENV_LINE}\n"


# @spec SETUP-HOOK-008
@pytest.mark.parametrize("problem", ["bin-paths-fails", "no-paths", "unwritable-env-file"])
def test_hook_reports_a_failed_path_step(tmp_path: Path, problem: str) -> None:
    """A PATH line that couldn't be built or written is reported, not silently skipped."""
    sandbox = hook_sandbox(tmp_path, installed=_mise_version())
    if problem == "bin-paths-fails":
        sandbox.env["STUB_FAIL"] = "bin-paths"
    elif problem == "no-paths":
        sandbox.env["STUB_NO_PATHS"] = "1"
    else:
        sandbox.env["CLAUDE_ENV_FILE"] = str(tmp_path / "home")
    run = sandbox.run()
    assert run.returncode == 0
    assert run.steps() == HOOK_STEPS
    assert "PATH" in run.output()["additionalContext"]
    assert run.env_file.read_text() == f"{OTHER_ENV_LINE}\n"


# @spec SETUP-HOOK-008
@pytest.mark.parametrize("project", [None, "missing"], ids=["unset", "missing"])
def test_hook_needs_the_project_directory(tmp_path: Path, project: str | None) -> None:
    """Without a project directory, no mise command runs, and the agent is told why."""
    sandbox = hook_sandbox(tmp_path, installed=_mise_version())
    if project is None:
        del sandbox.env["CLAUDE_PROJECT_DIR"]
    else:
        sandbox.env["CLAUDE_PROJECT_DIR"] = str(tmp_path / project)
    run = sandbox.run()
    assert run.returncode == 0
    assert run.calls == []
    assert "project directory" in run.output()["additionalContext"]


# @spec SETUP-HOOK-008
def test_hook_stops_when_mise_can_not_be_downloaded(tmp_path: Path) -> None:
    """A failed download stops the hook before any mise command."""
    run = hook_sandbox(tmp_path, checksums="no-archive").run()
    assert run.returncode == 0
    assert run.calls == []
    assert "installing mise" in run.output()["additionalContext"]


# @spec SETUP-HOOK-009
def test_hook_mise_version_matches_ci() -> None:
    """Cloud sessions and GitHub's runners use one mise."""
    steps = _mise_action_steps()
    assert steps
    for workflow, step in steps:
        assert str(step.get("with", {}).get("version")) == _mise_version(), workflow


# @spec SETUP-HOOK-010
@pytest.mark.renovate
def test_renovate_bumps_the_hook_with_the_workflows(tmp_path: Path) -> None:
    """A mise release updates the hook and the workflows as one dependency."""
    files = {f".github/workflows/{p.name}": p.read_text() for p in WORKFLOWS.glob("*.yml")}
    files[".claude/hooks/session-start.sh"] = HOOK.read_text()
    repo = git_repo(tmp_path / "repo", files)
    # Renovate's local platform can't resolve this repo's `local>` reference to the preset, so
    # the preset stands in for it: this repo's own keys are layered on top, lists appended.
    config = json.loads(PRESET.read_text())
    for key, value in json.loads(OWN_RENOVATE.read_text()).items():
        if key in {"$schema", "extends"}:
            continue
        config[key] = [*config.get(key, []), *value] if isinstance(value, list) else value
    hook_deps, version_deps = [], []
    for record in renovate_log(repo, "extract", config):
        if record.get("msg") != "Extracted dependencies":
            continue
        for manager, package_files in record["packageFiles"].items():
            for package_file in package_files:
                for dep in package_file["deps"]:
                    key = (
                        dep.get("depName"),
                        dep.get("datasource"),
                        dep.get("versioning"),
                        dep.get("currentValue"),
                    )
                    if package_file["packageFile"] == ".claude/hooks/session-start.sh":
                        hook_deps.append(key)
                    elif (
                        manager == "github-actions"
                        and dep.get("depType") == "uses-with"
                        and dep.get("depName") == "jdx/mise"
                    ):
                        version_deps.append(key)
    assert len(hook_deps) == 1, hook_deps
    assert hook_deps[0][3] == _mise_version()
    assert len(version_deps) == len(_mise_action_steps())
    assert set(version_deps) == set(hook_deps)


# @spec SETUP-HOOK-011
def test_hook_prints_one_reload_object(tmp_path: Path) -> None:
    """Claude Code re-scans skills after the hook, and nothing else shares its stdout."""
    run = hook_sandbox(tmp_path, installed=_mise_version()).run()
    assert run.returncode == 0
    assert run.output() == {"hookEventName": "SessionStart", "reloadSkills": True}


# @spec SETUP-HOOK-011
@pytest.mark.parametrize("failing", ["run skills", "install"])
def test_hook_asks_for_a_reload_after_a_failure(tmp_path: Path, failing: str) -> None:
    """Skills installed before a failure are still loaded."""
    output = hook_sandbox(tmp_path, installed=_mise_version(), fail=failing).run().output()
    assert output["hookEventName"] == "SessionStart"
    assert output["reloadSkills"] is True


# @spec SETUP-HOOK-011
def test_hook_still_prints_its_object_when_it_aborts(tmp_path: Path) -> None:
    """An abort outside the defined steps still reaches the agent as a notice."""
    sandbox = hook_sandbox(tmp_path, installed=_mise_version())
    del sandbox.env["HOME"]
    run = sandbox.run()
    assert run.returncode == 0
    output = run.output()
    assert output["reloadSkills"] is True
    assert "unexpectedly" in output["additionalContext"]
