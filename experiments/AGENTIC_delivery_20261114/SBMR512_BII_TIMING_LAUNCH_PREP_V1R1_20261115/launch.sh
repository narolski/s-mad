#!/bin/bash
# SOURCE ONLY. Run inside root-created detached tmux real PTY after exact
# source/bootstrap/tool/config pins and OTHER/root admission. No execution here.
set -euo pipefail
umask 077
: "${1:?absolute final config path}" "${2:?external final config SHA}" "${SBMR_LAUNCH_BOOTSTRAP:?externally pinned native bootstrap}"
[[ "$1" == /* && "$SBMR_LAUNCH_BOOTSTRAP" == /* && "$2" =~ ^[0-9a-f]{64}$ ]] || exit 64
exec "$SBMR_LAUNCH_BOOTSTRAP" -I -S -B /lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/SbMR512_bii_timing_wcss_v1/source/launch.py "$1" "$2"
