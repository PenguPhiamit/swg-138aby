#!/bin/bash
# Syntax-check every staged Lua file with luac5.3 -p (inside Debian). Usage:
#   bash tools/luac_staged.sh [staged|staged-batch2] [batch1|batch2]
# Writes work/luac_<batch>.txt. Reads the staged tree only.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TREE="$HERE/${1:-staged}"
OUT="$HERE/work/luac_${2:-batch1}.txt"
LUAC="$(command -v luac5.3 || command -v luac)"
[ -n "$LUAC" ] || { echo "no luac found" | tee "$OUT"; exit 2; }
n=0; bad=0
: > "$OUT"
while IFS= read -r f; do
  n=$((n+1))
  if ! "$LUAC" -p -- "$f" >>"$OUT" 2>&1; then bad=$((bad+1)); fi
done < <(find "$TREE" -name '*.lua' | sort)
echo "luac: $LUAC; checked $n files, $bad failed" | tee -a "$OUT"
