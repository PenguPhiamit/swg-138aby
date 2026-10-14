#!/bin/bash
# Apply Fable's staged backport batch to the Core3-dev worktree. Run as swgemu inside Debian:
#
#   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-backport/apply.sh [--check] [--manifest FILE] [--staged DIR]
#
# Default manifest: apply-manifest.tsv next to this script (batch 1). For batch 2 pass
#   --manifest apply-manifest-batch2.tsv --staged staged-batch2
#
# Each manifest line:  <path relative to MMOCoreORB/bin/scripts/object><TAB><sha256 of the Core3-dev file the
# staged copy was diffed against, or "new">
#
# Rules: a changed file is copied only when the current Core3-dev file still has the recorded hash; a new file
# is copied only when it does not exist yet (or already has identical content). Anything else is refused and
# listed; nothing is partially applied: all checks run first, then all copies. --check only reports.
# No git commands are run; commit afterwards yourself.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$HERE/apply-manifest.tsv"
STAGED="$HERE/staged"
DEV="${CORE3_DEV:-/opt/swg/Core3-dev}/MMOCoreORB/bin/scripts/object"
CHECK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1 ;;
    --manifest) shift; MANIFEST="$1"; [ "${MANIFEST#/}" = "$MANIFEST" ] && MANIFEST="$HERE/$MANIFEST" ;;
    --staged) shift; STAGED="$1"; [ "${STAGED#/}" = "$STAGED" ] && STAGED="$HERE/$STAGED" ;;
    *) echo "unknown argument: $1"; exit 2 ;;
  esac
  shift
done
SRC="$STAGED/MMOCoreORB/bin/scripts/object"
[ -f "$MANIFEST" ] || { echo "manifest not found: $MANIFEST"; exit 2; }
[ -d "$SRC" ] || { echo "staged tree not found: $SRC"; exit 2; }
[ -d "$DEV" ] || { echo "Core3-dev object scripts not found: $DEV"; exit 2; }

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
      if cmp -s "$staged" "$target"; then same+=("$rel"); else refused+=("$rel: Core3-dev file changed since the diff (have ${have:0:16}, diffed against ${want:0:16})"); fi
    else
      ok_change+=("$rel")
    fi
  fi
done < "$MANIFEST"

echo "manifest: $MANIFEST"
echo "staged:   $SRC"
echo "target:   $DEV"
echo "to change: ${#ok_change[@]}   new: ${#ok_new[@]}   already identical: ${#same[@]}   refused: ${#refused[@]}"
for r in "${refused[@]}"; do echo "  REFUSED $r"; done

if [ ${#refused[@]} -gt 0 ]; then
  echo "nothing applied: fix the refused entries first (re-stage against the current Core3-dev files)."
  exit 1
fi
if [ $CHECK -eq 1 ]; then
  echo "--check: nothing copied."
  exit 0
fi
for rel in "${ok_change[@]}" "${ok_new[@]}"; do
  mkdir -p "$DEV/$(dirname "$rel")"
  cp "$SRC/$rel" "$DEV/$rel" || { echo "copy failed: $rel"; exit 1; }
done
echo "applied: ${#ok_change[@]} changed, ${#ok_new[@]} new. Next: luac5.3 -p on the changed files (outputs/tools/check_lua.py), then build/test."
for rel in "${ok_change[@]}"; do echo "  changed $rel"; done | head -40
[ ${#ok_change[@]} -gt 40 ] && echo "  ... (${#ok_change[@]} changed files; see the manifest)"
for rel in "${ok_new[@]}"; do echo "  new     $rel"; done
exit 0
