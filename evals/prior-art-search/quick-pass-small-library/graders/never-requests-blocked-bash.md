---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?=(?:[^"\\]|\\.)*?\b(?:curl|wget|http|urlopen|requests\.get)\b)(?=(?:[^"\\]|\\.)*?(?:https?://(?:www\.)?codeberg\.org/(?:api/|explore/[^\s''"\\]*\?|[^/\s''"\\]+/[^/\s''"\\]+/(?:raw|src|media)/)|https?://(?:www\.)?lib\.rs\b|(?<![\w/.-])lib\.rs/|pypi\.org/search))'
min: 0
max: 0
---
