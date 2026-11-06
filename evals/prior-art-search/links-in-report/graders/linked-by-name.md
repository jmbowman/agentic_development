---
type: llm
focus: trace
---

PASS if all hold in the report:
- alphaslug is a Markdown link whose text is the name and whose target is the repository URL from its `pyproject.toml` (`https://git.fixture.invalid/fixture-org/alphaslug`);
- betaslug is a Markdown link whose target is the documentation URL from its README (`https://betaslug.fixture.invalid/docs/`), which is its official page because it names no repository;
- gammaslug, which has no URL anywhere in its clone, is not linked to an address composed from memory (for example a guessed GitHub or PyPI URL) or to a local path, and "no link found" stands beside its name;
- no full URL is shown as link text, and no bare URL stands in place of a name.
FAIL if a link target was composed rather than taken from the candidate's files, a candidate that has a link isn't linked, or "no link found" is missing for gammaslug.
