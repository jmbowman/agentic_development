"""Tests that README.md doesn't point at paths that no longer exist."""

from __future__ import annotations

import re

from tests.support import REPO_ROOT

README = REPO_ROOT / "README.md"


def test_listed_and_linked_paths_exist() -> None:
    """Every path in the contents table's first column, and every relative link, exists."""
    text = README.read_text()
    paths = re.findall(r"^\| `([^`]+)` \|", text, flags=re.MULTILINE)
    paths += [
        link for link in re.findall(r"\]\(([^)#]+)\)", text) if not re.match(r"[a-z]+:", link)
    ]
    assert paths
    missing = [path for path in paths if not (REPO_ROOT / path).exists()]
    assert not missing, missing
