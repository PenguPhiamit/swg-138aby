#!/bin/bash
# Apply Fable's Hoth batch C to the Core3-dev worktree. Run as swgemu inside Debian:
#
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchC/apply.sh [--check]
#
# Unlike the earlier batches this one does not replace whole list files (screenplays.lua and the include lists are
# being edited by Claude at the same time). It copies NEW files (refused if a different file already exists) and
# applies LINE PATCHES from patches.tsv, each idempotent:
#   <file>\tafter\t<anchor line>\t<new line>    insert the new line after the anchor (anchor must occur exactly once)
#   <file>\tbefore\t<anchor line>\t<new line>   insert before the anchor
#   <file>\tappend\t<marker>\t<snippet file>    append the snippet when the marker string is absent from the file
# A patch whose new line (or marker) is already present is skipped. All checks run first; nothing is applied if any
# check fails. --check only reports. luac5.3 -p runs on every touched file afterwards. No git commands.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/staged/MMOCoreORB/bin/scripts"
DEV="${CORE3_DEV:-/opt/swg/Core3-dev}/MMOCoreORB/bin/scripts"
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
[ -d "$SRC" ] || { echo "staged tree not found: $SRC"; exit 2; }
[ -d "$DEV" ] || { echo "Core3-dev scripts not found: $DEV"; exit 2; }
[ -f "$HERE/new-files.txt" ] || { echo "new-files.txt missing"; exit 2; }
[ -f "$HERE/patches.tsv" ] || { echo "patches.tsv missing"; exit 2; }

refused=(); new=(); same=(); todo=(); skip=(); touched=()
while read -r rel; do
  [ -z "$rel" ] && continue; case "$rel" in \#*) continue ;; esac
  if [ ! -f "$SRC/$rel" ]; then refused+=("$rel: staged file missing"); continue; fi
  if [ -e "$DEV/$rel" ]; then
    if cmp -s "$SRC/$rel" "$DEV/$rel"; then same+=("$rel"); else refused+=("$rel: a different file already exists in Core3-dev"); fi
  else new+=("$rel"); fi
done < "$HERE/new-files.txt"

while IFS=$'\t' read -r rel mode anchor line; do
  [ -z "$rel" ] && continue; case "$rel" in \#*) continue ;; esac
  anchor="$(printf '%b' "$anchor")"; line="$(printf '%b' "$line")"   # a literal \t in the TSV stands for a tab
  target="$DEV/$rel"
  if [ ! -f "$target" ]; then refused+=("$rel: missing in Core3-dev"); continue; fi
  case "$mode" in
    after|before)
      if grep -qxF -- "$line" "$target"; then skip+=("$rel: already has: $line"); continue; fi
      n=$(grep -cxF -- "$anchor" "$target")
      if [ "$n" != "1" ]; then refused+=("$rel: anchor occurs $n times: $anchor"); continue; fi
      todo+=("$rel"$'\t'"$mode"$'\t'"$anchor"$'\t'"$line") ;;
    append)
      if grep -qF -- "$anchor" "$target"; then skip+=("$rel: already has marker $anchor"); continue; fi
      [ -f "$HERE/$line" ] || { refused+=("$rel: snippet missing: $line"); continue; }
      todo+=("$rel"$'\t'"$mode"$'\t'"$anchor"$'\t'"$line") ;;
    *) refused+=("$rel: unknown mode $mode") ;;
  esac
done < "$HERE/patches.tsv"

echo "new files: ${#new[@]}   identical already: ${#same[@]}   line patches to apply: ${#todo[@]}   already applied: ${#skip[@]}   refused: ${#refused[@]}"
for r in "${refused[@]}"; do echo "  REFUSED $r"; done
for r in "${skip[@]}"; do echo "  skip $r"; done
[ ${#refused[@]} -gt 0 ] && { echo "nothing applied: fix the refused entries first."; exit 1; }
[ $CHECK -eq 1 ] && { for t in "${todo[@]}"; do echo "  would patch: ${t%%$'\t'*}"; done; for r in "${new[@]}"; do echo "  would copy: $r"; done; echo "--check: nothing changed."; exit 0; }

for rel in "${new[@]}"; do mkdir -p "$DEV/$(dirname "$rel")"; cp "$SRC/$rel" "$DEV/$rel" || { echo "copy failed: $rel"; exit 1; }; echo "  copied $rel"; touched+=("$rel"); done
for t in "${todo[@]}"; do
  IFS=$'\t' read -r rel mode anchor line <<< "$t"
  anchor="$(printf '%b' "$anchor")"; line="$(printf '%b' "$line")"
  target="$DEV/$rel"; tmp="$target.fable.tmp"
  case "$mode" in
    after)  awk -v a="$anchor" -v l="$line" '{print} $0==a {print l}' "$target" > "$tmp" ;;
    before) awk -v a="$anchor" -v l="$line" '$0==a {print l} {print}' "$target" > "$tmp" ;;
    append) cat "$target" "$HERE/$line" > "$tmp" ;;
  esac
  mv "$tmp" "$target" && echo "  patched $rel ($mode)"; touched+=("$rel")
done
if command -v luac5.3 >/dev/null 2>&1; then
  for rel in "${touched[@]}"; do luac5.3 -p "$DEV/$rel" && echo "  luac ok $rel" || echo "  LUAC FAILED $rel"; done
fi
echo "done. Next: pack the string file from strings.tsv into local_planets.tre (the quest NPC's dialogue), then test galaxy with hoth enabled."
