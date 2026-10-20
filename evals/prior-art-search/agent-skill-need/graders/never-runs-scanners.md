---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:(?:[^"\\]|\\.)*?(?:;|&&|\|\||\||\\n|\())?\s*(?:(?:(?:npx|uvx|pipx\s+run)(?:\s+-\S+)*\s+)?(?:\S*skill-?scan\S*|mcp-scan|snyk|semgrep|trufflehog|gitleaks)\b)'
min: 0
max: 0
arm: both
---
