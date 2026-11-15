#!/bin/bash
# SE1 amendment SE1-A1: fetch the five WCSS H100 SE tars (results/SE1H) to /mnt/t7/smad_next/SE1/results_h100 (copy 1) and
# /home/narolski/se1_results_copy/h100 (copy 2); verify both. One rsync connection under the shared WCSS lock.
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next; D=/mnt/t7/smad_next/SE1/results_h100; C=/home/narolski/se1_results_copy/h100
mkdir -p "$D" "$C"
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a --partial -e "ssh -o BatchMode=yes" --include='SE1H_SE_s*.tar' --include='SE1H_SE_s*.tar.sha256' --exclude='*' "narolski@ui.wcss.pl:$L/results/SE1H/" "$D/"
n=0; for f in "$D"/SE1H_SE_s*.tar; do [ -e "$f" ] || continue; b=$(basename "$f")
  (cd "$D" && sha256sum -c --quiet "$b.sha256") && cp -n "$f" "$f.sha256" "$C/" && (cd "$C" && sha256sum -c --quiet "$b.sha256") && n=$((n + 1)) || echo "$b not verified"; done
echo "verified in two copies: $n of 5"
