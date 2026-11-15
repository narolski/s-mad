#!/bin/bash
# Watches the three ViT-L/14 morph-free reruns of the morph-free networks experiment (AD4) on Athena (array 3546123_[2-4]):
# one short ssh under the command lock every 15 minutes (ATHENA.md: at most every 10 minutes), copies each finished tar with
# its .sha256 under the transfer lock and checks it. Exits 0 when all three are verified, 1 on a failed / cancelled / timed-out
# task, 3 on a login problem (never retried), 2 after MAXH hours.
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
L=/mnt/t7/smad_next/AD4/results_athena
H=plgpnarolski@athena.cyfronet.pl
MAXH=${1:-14}
END=$((SECONDS + MAXH * 3600))
while [ $SECONDS -lt $END ]; do
  out=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $H "sacct -j 3546123 -n -X -o JobID,State | tr -s ' ' | tr '\n' ';'; echo; ls $G/results/AD4/ | tr '\n' ' '" 2>&1)
  rc=$?
  echo "$(date +%FT%T) rc=$rc $out"
  if [ $rc -ne 0 ] && [ $rc -ne 1 ]; then echo "LOGIN OR SSH PROBLEM rc=$rc; stopping (never retried)"; exit 3; fi
  case "$out" in *FAILED*|*TIMEOUT*|*OUT_OF_ME*|*NODE_FAIL*|*CANCELLED*) echo "A RERUN TASK ENDED BADLY"; exit 1;; esac
  n=0
  for s in 403 404 405; do
    t=AD4_m3lmf_s$s
    if [ -f "$L/$t.tar" ] && (cd "$L" && sha256sum -c --quiet "$t.tar.sha256" 2>/dev/null); then n=$((n + 1)); continue; fi
    case "$out" in *"$t.tar.sha256"*)
      flock -w 1800 /tmp/smadnext-athena.lock rsync -a "$H:$G/results/AD4/$t.tar" "$H:$G/results/AD4/$t.tar.sha256" "$L/" \
        && (cd "$L" && sha256sum -c "$t.tar.sha256") && n=$((n + 1)) ;;
    esac
  done
  [ $n -eq 3 ] && { echo "ALL THREE VERIFIED $(date +%FT%T)"; exit 0; }
  sleep 900
done
echo "TIMEOUT after $MAXH h"; exit 2
