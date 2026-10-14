#!/bin/bash
# Apply Fable's Hoth mynock den (outdoor option) to the Core3-dev worktree (the Ossus O2 applier plus a replace mode). Run as swgemu:
#
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh --selftest   # every mode on scratch copies
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh --check      # dry run against Core3-dev
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh              # apply
#
# Copies NEW files from staged/MMOCoreORB/bin/scripts (new-files.txt; refused if a different file already exists) and
# applies LINE PATCHES from patches.tsv, each idempotent:
#   <file>\tafter\t<anchor line>\t<new line>        insert the new line after the anchor (anchor must occur exactly once)
#   <file>\tbefore\t<anchor line>\t<new line>       insert before the anchor
#   <file>\tbefore-file\t<anchor line>\t<snippet>   insert a snippet file before the anchor (skipped when the snippet's
#                                                   first line is already in the file)
#   <file>\tappend\t<marker>\t<snippet>             append the snippet when the marker string is absent
#   <file>\treplace\t<old line>\t<new line>         replace the old line (must occur exactly once) with the new one
# A literal \t in a field stands for a tab and \\ for a backslash (printf %b). Fields are split with parameter
# expansion, never `read` with IFS (batch C lost a tab-leading anchor that way), and awk gets the lines through
# ENVIRON, never -v (which would process escapes again). All checks run first; nothing is applied if any fails.
# luac5.3 -p runs on every touched file afterwards. No git commands.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"

split4() {   # $1 = tsv line -> F1..F4
  local line="$1"
  F1="${line%%$'\t'*}"; line="${line#*$'\t'}"
  F2="${line%%$'\t'*}"; line="${line#*$'\t'}"
  F3="${line%%$'\t'*}"; line="${line#*$'\t'}"
  F4="$line"
  F3="$(printf '%b' "$F3")"; F4="$(printf '%b' "$F4")"
}

run() {   # $1 = scripts root (Core3-dev or scratch), $2 = batch root, $3 = check-only (0/1)
  local DEV="$1" ROOT="$2" CHECK="$3"
  local SRC="$ROOT/staged/MMOCoreORB/bin/scripts"
  local refused=() new=() same=() todo=() skip=() touched=()
  [ -d "$DEV" ] || { echo "scripts root not found: $DEV"; return 2; }
  while IFS= read -r rel || [ -n "$rel" ]; do
    [ -z "$rel" ] && continue; case "$rel" in \#*) continue ;; esac
    if [ ! -f "$SRC/$rel" ]; then refused+=("$rel: staged file missing"); continue; fi
    if [ -e "$DEV/$rel" ]; then
      if cmp -s "$SRC/$rel" "$DEV/$rel"; then same+=("$rel"); else refused+=("$rel: a different file already exists"); fi
    else new+=("$rel"); fi
  done < "$ROOT/new-files.txt"
  while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue; case "$line" in \#*) continue ;; esac
    split4 "$line"
    local rel="$F1" mode="$F2" anchor="$F3" new_="$F4" target="$DEV/$F1" n
    if [ ! -f "$target" ]; then refused+=("$rel: missing in the scripts root"); continue; fi
    case "$mode" in
      after|before)
        if grep -qxF -- "$new_" "$target"; then skip+=("$rel: already has: $new_"); continue; fi
        n=$(grep -cxF -- "$anchor" "$target")
        [ "$n" = "1" ] || { refused+=("$rel: anchor occurs $n times: $anchor"); continue; }
        todo+=("$line") ;;
      before-file)
        [ -f "$ROOT/$new_" ] || { refused+=("$rel: snippet missing: $new_"); continue; }
        local first; first="$(head -n 1 "$ROOT/$new_")"
        if grep -qxF -- "$first" "$target"; then skip+=("$rel: already has the snippet $new_"); continue; fi
        n=$(grep -cxF -- "$anchor" "$target")
        [ "$n" = "1" ] || { refused+=("$rel: anchor occurs $n times: $anchor"); continue; }
        todo+=("$line") ;;
      append)
        [ -f "$ROOT/$new_" ] || { refused+=("$rel: snippet missing: $new_"); continue; }
        if grep -qF -- "$anchor" "$target"; then skip+=("$rel: already has marker $anchor"); continue; fi
        todo+=("$line") ;;
      replace)
        if grep -qxF -- "$new_" "$target"; then skip+=("$rel: already has: $new_"); continue; fi
        n=$(grep -cxF -- "$anchor" "$target")
        [ "$n" = "1" ] || { refused+=("$rel: old line occurs $n times: $anchor"); continue; }
        todo+=("$line") ;;
      *) refused+=("$rel: unknown mode $mode") ;;
    esac
  done < "$ROOT/patches.tsv"
  echo "new files: ${#new[@]}   identical already: ${#same[@]}   line patches to apply: ${#todo[@]}   already applied: ${#skip[@]}   refused: ${#refused[@]}"
  for r in "${refused[@]}"; do echo "  REFUSED $r"; done
  for r in "${skip[@]}"; do echo "  skip $r"; done
  [ ${#refused[@]} -gt 0 ] && { echo "nothing applied: fix the refused entries first."; return 1; }
  if [ "$CHECK" = "1" ]; then
    for t in "${todo[@]}"; do split4 "$t"; echo "  would patch ($F2): $F1"; done
    for r in "${new[@]}"; do echo "  would copy: $r"; done
    echo "--check: nothing changed."; return 0
  fi
  for rel in "${new[@]}"; do mkdir -p "$DEV/$(dirname "$rel")"; cp "$SRC/$rel" "$DEV/$rel" || { echo "copy failed: $rel"; return 1; }; echo "  copied $rel"; touched+=("$rel"); done
  for t in "${todo[@]}"; do
    split4 "$t"
    local rel="$F1" mode="$F2" anchor="$F3" new_="$F4" target="$DEV/$F1" tmp="$DEV/$F1.fable.tmp" before after
    before=$(wc -l < "$target")
    case "$mode" in
      after)  A="$anchor" L="$new_" awk '{print} $0==ENVIRON["A"] {print ENVIRON["L"]}' "$target" > "$tmp" ;;
      before) A="$anchor" L="$new_" awk '$0==ENVIRON["A"] {print ENVIRON["L"]} {print}' "$target" > "$tmp" ;;
      before-file) A="$anchor" F="$ROOT/$new_" awk '$0==ENVIRON["A"] {while ((getline x < ENVIRON["F"]) > 0) print x; close(ENVIRON["F"])} {print}' "$target" > "$tmp" ;;
      append) cat "$target" "$ROOT/$new_" > "$tmp" ;;
      replace) A="$anchor" L="$new_" awk '$0==ENVIRON["A"] {print ENVIRON["L"]; next} {print}' "$target" > "$tmp" ;;
    esac
    after=$(wc -l < "$tmp")
    if [ "$mode" = "replace" ]; then
      if ! grep -qxF -- "$new_" "$tmp" || grep -qxF -- "$anchor" "$tmp"; then rm -f "$tmp"; echo "  REPLACE DID NOT TAKE: $rel - left untouched"; return 1; fi
    elif [ "$after" -le "$before" ]; then rm -f "$tmp"; echo "  PATCH DID NOT ADD LINES: $rel ($mode) - left untouched"; return 1; fi
    mv "$tmp" "$target" && echo "  patched $rel ($mode): $before -> $after lines"; touched+=("$rel")
  done
  if command -v luac5.3 >/dev/null 2>&1; then
    for rel in "${touched[@]}"; do luac5.3 -p "$DEV/$rel" && echo "  luac ok $rel" || { echo "  LUAC FAILED $rel"; return 1; }; done
  fi
  return 0
}

selftest() {   # every mode on scratch copies, including a tab-leading anchor (the batch C bug), a backslash and a replace
  local T; T="$(mktemp -d)"; local S="$T/scripts" B="$T/batch"
  mkdir -p "$S/a" "$B/staged/MMOCoreORB/bin/scripts/a" "$B/snippets"
  printf 'one = 1\nt = {\n\t{ "tabbed", 1 },\n\t{ "last", 2 },\n}\nend_marker = true\nx = "a\\\\b"\n' > "$S/a/list.lua"
  printf 'block = {\n\tv = 1,\n}\n' > "$B/snippets/block.lua"
  printf -- '-- appended\nappended = true\n' > "$B/snippets/tail.lua"
  printf 'new = 1\n' > "$B/staged/MMOCoreORB/bin/scripts/a/new.lua"
  printf 'a/new.lua\n' > "$B/new-files.txt"
  cat > "$B/patches.tsv" <<'EOF'
a/list.lua	after	one = 1	two = 2
a/list.lua	before	\t{ "last", 2 },	\t{ "inserted", 9 },
a/list.lua	before-file	end_marker = true	snippets/block.lua
a/list.lua	append	appended = true	snippets/tail.lua
a/list.lua	after	x = "a\\\\b"	y = "c\\\\d"
a/list.lua	replace	\t{ "tabbed", 1 },	\t{ "tabbed", 1, flags = 7 },
EOF
  echo "== selftest in $T: check"; run "$S" "$B" 1 || { echo "SELFTEST FAILED (check)"; return 1; }
  echo "== selftest: apply"; run "$S" "$B" 0 || { echo "SELFTEST FAILED (apply)"; return 1; }
  local expect; expect="$(printf 'one = 1\ntwo = 2\nt = {\n\t{ "tabbed", 1, flags = 7 },\n\t{ "inserted", 9 },\n\t{ "last", 2 },\n}\nblock = {\n\tv = 1,\n}\nend_marker = true\nx = "a\\\\b"\ny = "c\\\\d"\n-- appended\nappended = true\n')"
  if [ "$(cat "$S/a/list.lua")" = "$expect" ] && [ -f "$S/a/new.lua" ]; then echo "== selftest: result matches the expected file"; else echo "SELFTEST FAILED: result differs"; diff <(echo "$expect") "$S/a/list.lua"; return 1; fi
  echo "== selftest: second apply must change nothing"; run "$S" "$B" 0 | grep -q 'line patches to apply: 0 ' && echo "== selftest: idempotent" || { echo "SELFTEST FAILED (idempotence)"; return 1; }
  rm -rf "$T"; echo "SELFTEST PASSED"
}

case "$MODE" in
  --selftest) selftest ;;
  --check) run "${CORE3_DEV:-/opt/swg/Core3-dev}/MMOCoreORB/bin/scripts" "$HERE" 1 ;;
  "") run "${CORE3_DEV:-/opt/swg/Core3-dev}/MMOCoreORB/bin/scripts" "$HERE" 0 && echo "done. Next: restart the test galaxy and run the bot check in README.md." ;;
  *) echo "usage: apply.sh [--selftest|--check]"; exit 2 ;;
esac
