#!/bin/sh
# Print each file with a header and line numbers. Read-only helper, run from Windows as:
#   MSYS_NO_PATHCONV=1 wsl -d Debian -u swgemu -- sh /mnt/c/.../Fable-planet-test/tools/wslcat.sh /opt/swg/... [...]
for f in "$@"; do
  echo "=================== $f"
  cat -n "$f"
done
