#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > greet.py <<'EOF'
def greet(name):
    return f"Helo, {name}!"
EOF
cat > fix.patch <<'EOF'
--- a/greet.py
+++ b/greet.py
@@ -1,2 +1,2 @@
 def greet(name):
-    return f"Helo, {name}!"
+    return f"Hello, {name}!"
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
