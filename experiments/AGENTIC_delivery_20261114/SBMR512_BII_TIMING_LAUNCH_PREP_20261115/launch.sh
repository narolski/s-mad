#!/bin/bash
# SOURCE ONLY. Root stages immutable files, pins this bootstrap/tool runtime and
# supplies the final adopted JSON path and SHA, then runs this under shared lock.
set -euo pipefail
umask 077
: "${1:?absolute node config path required}" "${2:?external SHA256 required}"
case "$1" in /*) ;; *) exit 64;; esac
[[ "$2" =~ ^[0-9a-f]{64}$ ]] || exit 64
# cwd is the separately pinned extension package; python is WCSS bootstrap,
# never the GX dmenv path. Actual node bootstrap SHA must be admitted first.
: "${SBMR_NODE_BOOTSTRAP:?root-pinned native bootstrap absolute path required}"
[[ "$SBMR_NODE_BOOTSTRAP" == /* ]] || exit 64
exec srun --partition=lem-gpu-interactive --gres=gpu:1 --cpus-per-task=8 --mem=32G --tmp=8G --time=00:15:00 --extra=FORCE_RM_TMPDIR --pty "$SBMR_NODE_BOOTSTRAP" -E -s "$(pwd)/node_driver.py" "$1" "$2"
