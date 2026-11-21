---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:(?:[^"\\]|\\.)*?(?:;|&&|\|\||\||\\n|\())?\s*git(?:\s+-[Cc]\s+\S+|\s+--\S+)*\s+(?!(?:status|diff|log|show|ls-files|rev-parse)\b)[a-z]'
min: 0
max: 0
arm: both
---
