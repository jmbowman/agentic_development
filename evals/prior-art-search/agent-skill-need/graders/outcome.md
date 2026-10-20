---
type: llm
---

PASS if all hold:
- the coverage ledger includes skill-catalog routes (skill directories such as skills.sh, plugin marketplaces, the MCP Registry, Anthropic's skills repo, awesome lists for agent skills, or GitHub topics such as agent-skills);
- for each skill it evaluated, it read the SKILL.md and the files it references;
- it records each skill's portability: frontmatter fields outside the Agent Skills spec, tools or connectors only one agent provides, and any install step, service or credentials;
- it treats any scanner results as leads, and runs no scanner itself.
FAIL if any is missing.
