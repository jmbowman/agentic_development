---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?(?:(?<![0-9&=-])>>?(?!\s*/dev/null)|\btee\b|\bsed\s+-i|\b(?:cp|mv|rm|touch|mkdir|truncate|ln)\s|\bopen\([^),]*,\s*(?:mode\s*=\s*)?\\?[\x27"][wax])'
min: 0
max: 0
---
