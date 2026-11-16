#!/bin/bash
# AD6 (matched-recipe retrains Hsbr): pull finished result tars back from WCSS through gx10 and verify hashes.
#   fetch_ad6_wcss.sh [PATTERN]     default: all *.tar with .sha256 beside them on lustre results dir.
# Route: THIS machine (DGX GB10) -> narolski@gx10-c326 -> ui.wcss.pl (tar over ssh, flock part ticket).
# Local target: /home/narolski/ad6_stage/ad6_wcss_pull/  (/mnt/t7 is 100% full as of 2026-11-16 - do NOT write there.)
set -uo pipefail
L=/home/narolski/ad6_stage/ad6_wcss_pull; mkdir -p "$L"
R=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6/results
PAT=${1:-*}
LIST=$(ssh -o BatchMode=yes -o ConnectTimeout=30 narolski@gx10-c326 \
  "flock /tmp/opencode/wcss-client.lock ssh ui.wcss.pl 'cd $R && ls ${PAT}.tar 2>/dev/null; ls ${PAT}.tar.sha256 2>/dev/null || true'") \
  || { echo "LIST_FAILED (gx10/wcss route)"; exit 1; }
[ -n "$LIST" ] || { echo "NOTHING_ON_WCSS matching $PAT"; exit 0; }
rc_all=0
for f in $LIST; do
  [ -f "$L/$f" ] && { echo "have $f"; continue; }
  flock /tmp/opencode/wcss-client.lock ssh narolski@gx10-c326 \
    "ssh ui.wcss.pl 'cd $R && tar -cf - $f'" > "$L/.bundle_$f" || { echo "PULL_FAILED $f"; rc_all=1; continue; }
  tar -xf "$L/.bundle_$f" -C "$L" || { echo "EXTRACT_FAILED $f"; rc_all=1; continue; }
  rm -f "$L/.bundle_$f"
done
cd "$L"
for s in ${PAT}.tar.sha256; do
  [ -f "$s" ] || continue
  if sha256sum -c --quiet "$s"; then echo "OK ${s%.tar.sha256}"; else echo "BAD ${s%.tar.sha256}"; rc_all=1; fi
done
exit $rc_all
