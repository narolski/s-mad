#!/bin/bash
# FZ2: poll Athena (command lock, one short ssh per poll, every 5 min) until results/FZ2/FZ2_<TAG>.tar.sha256 exists
# or the job has left the queue, then fetch. usage: bash fz2_wait_fetch.sh TAG JOBID [max_polls]
set -uo pipefail
T=$1; J=$2; N=${3:-30}
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
for k in $(seq 1 $N); do
  s=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl \
      "if test -f $G/results/FZ2/FZ2_$T.tar.sha256; then echo DONE; else st=\$(squeue -h -j $J -o %T 2>/dev/null | head -1); echo STATE:\${st:-NONE}; fi")
  echo "$(date +%H:%M) poll $k: ${s:-<no answer>}"
  case "$s" in
    DONE) bash /home/narolski/smad-next/src/FZ2/fz2_fetch.sh $T; exit $? ;;
    STATE:NONE) echo "job $J not in queue and no result"; exit 2 ;;
  esac
  sleep 300
done
exit 3
