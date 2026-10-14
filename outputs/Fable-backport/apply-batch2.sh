#!/bin/bash
# Batch 2 wrapper: same checks as apply.sh, with the batch-2 manifest and staged tree.
# Batch 2 builds on batch 1 (its allobjects.lua diff is against batch 1's staged copy), so apply batch 1 first.
#   bash apply-batch2.sh [--check]
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$HERE/apply.sh" --manifest "$HERE/apply-manifest-batch2.tsv" --staged "$HERE/staged-batch2" "$@"
