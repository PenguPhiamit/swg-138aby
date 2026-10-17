#!/bin/bash
# Hoth fill: build hoth-fill.patch from the staged tree (outputs/Hoth-fill/MMOCoreORB) against Core3-dev HEAD, then
# check it. Read-only on /opt/swg: a scratch git repo under /tmp holds the originals. Run in WSL as swgemu:
#   wsl -d Debian -u swgemu -- bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Hoth-fill/tools/build_patch.sh
set -euo pipefail
HF=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Hoth-fill
DEV=/opt/swg/Core3-dev
W=$(mktemp -d /tmp/hothfill.XXXXXX)
trap 'rm -rf "$W"' EXIT

git -C "$W" init -q
git -C "$W" config user.name "Hoth fill build"
git -C "$W" config user.email "build@localhost"
cd "$HF"
mapfile -t STAGED < <(find MMOCoreORB -type f -name '*.lua' | sort)
for f in "${STAGED[@]}"; do
	if git -C "$DEV" cat-file -e "HEAD:$f" 2>/dev/null; then
		mkdir -p "$W/$(dirname "$f")"
		git -C "$DEV" show "HEAD:$f" > "$W/$f"
		[ "$(git -C "$DEV" ls-tree HEAD -- "$f" | cut -c1-6)" = 100755 ] && chmod 755 "$W/$f"
	fi
done
git -C "$W" add -A
git -C "$W" commit -q -m base --allow-empty
for f in "${STAGED[@]}"; do
	mkdir -p "$W/$(dirname "$f")"
	if [ -x "$W/$f" ]; then mode=755; else mode=644; fi
	cp "$f" "$W/$f"
	chmod $mode "$W/$f"
done
git -C "$W" add -A
git -C "$W" diff --cached > "$HF/hoth-fill.patch"

echo "base: Core3-dev $(git -C "$DEV" rev-parse --short HEAD)"
git -C "$W" diff --cached --stat | tail -1
sha256sum "$HF/hoth-fill.patch"
git -C "$DEV" apply --check "$HF/hoth-fill.patch" && echo "git apply --check: clean"
fail=0
for f in "${STAGED[@]}"; do
	luac5.3 -p "$f" || fail=1
done
[ $fail -eq 0 ] && echo "luac5.3 -p: clean on ${#STAGED[@]} files"
lua5.3 "$HF/tools/load_test.lua" "$HF/MMOCoreORB/bin/scripts" || fail=1
exit $fail
