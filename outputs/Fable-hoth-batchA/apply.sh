#!/bin/bash
# Apply Fable's staged Hoth batch A (area spawn regions, spawn groups, glacial rancor template) to the Core3-dev worktree. Run as swgemu inside Debian:
#
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/apply.sh [--check]
#
# Manifest lines (apply-manifest.tsv): <path relative to MMOCoreORB/bin/scripts><TAB><sha256 of the Core3-dev
# file the staged copy was made from, or "new">. A changed file is copied only when the current Core3-dev file
# still has the recorded hash; a new file only when it does not exist yet (or is already identical). All checks
# run first, then all copies; afterwards luac5.3 -p parses every copied file. No git commands; commit yourself.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$HERE/apply-manifest.tsv"
SRC="$HERE/staged/MMOCoreORB/bin/scripts"
DEV="${CORE3_DEV:-/opt/swg/Core3-dev}/MMOCoreORB/bin/scripts"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1
[ -f "$MANIFEST" ] || { echo "manifest not found: $MANIFEST"; exit 2; }
[ -d "$SRC" ] || { echo "staged tree not found: $SRC"; exit 2; }
[ -d "$DEV" ] || { echo "Core3-dev scripts not found: $DEV"; exit 2; }

ok_change=(); ok_new=(); same=(); refused=()
while IFS=$'\t' read -r rel want; do
  [ -z "$rel" ] && continue
  case "$rel" in \#*) continue ;; esac
  staged="$SRC/$rel"; target="$DEV/$rel"
  if [ ! -f "$staged" ]; then refused+=("$rel: staged file missing"); continue; fi
  if [ "$want" = "new" ]; then
    if [ -e "$target" ]; then
      if cmp -s "$staged" "$target"; then same+=("$rel"); else refused+=("$rel: exists in Core3-dev but was staged as new"); fi
    else
      ok_new+=("$rel")
    fi
  else
    if [ ! -f "$target" ]; then refused+=("$rel: missing in Core3-dev (expected sha256 $want)"); continue; fi
    have="$(sha256sum "$target" | cut -d' ' -f1)"
    if [ "$have" != "$want" ]; then
      if cmp -s "$staged" "$target"; then same+=("$rel"); else refused+=("$rel: Core3-dev file changed since staging (have ${have:0:16}, staged against ${want:0:16})"); fi
    else
      ok_change+=("$rel")
    fi
  fi
done < "$MANIFEST"

echo "manifest: $MANIFEST"
echo "to change: ${#ok_change[@]}   new: ${#ok_new[@]}   already identical: ${#same[@]}   refused: ${#refused[@]}"
for r in "${refused[@]}"; do echo "  REFUSED $r"; done
if [ ${#refused[@]} -gt 0 ]; then echo "nothing applied: re-stage against the current Core3-dev files."; exit 1; fi
if [ $CHECK -eq 1 ]; then echo "--check: nothing copied."; exit 0; fi
for rel in "${ok_change[@]}" "${ok_new[@]}"; do
  mkdir -p "$DEV/$(dirname "$rel")"
  cp "$SRC/$rel" "$DEV/$rel" || { echo "copy failed: $rel"; exit 1; }
  echo "  copied $rel"
done
if command -v luac5.3 >/dev/null 2>&1; then
  for rel in "${ok_change[@]}" "${ok_new[@]}"; do luac5.3 -p "$DEV/$rel" && echo "  luac ok $rel" || echo "  LUAC FAILED $rel"; done
fi
echo "applied: ${#ok_change[@]} changed, ${#ok_new[@]} new. Next: test galaxy with hoth enabled; watch the area spawners fill and the lair counts."
