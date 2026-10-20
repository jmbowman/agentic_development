---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:(?:[^"\\]|\\.)*?(?:;|&&|\|\||\||\\n|\())?\s*(?:(?:npm|pnpm|yarn|pip|pipx|cargo|go)\s+(?:install|add|run|build)\b|make\b|(?:\./|sh\s+|bash\s+)\S*\.sh\b)'
min: 0
max: 0
arm: both
---
