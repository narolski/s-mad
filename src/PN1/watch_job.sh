#!/bin/bash
# PN1: wait for an Athena job to end (first check at a given time, then every $3 seconds), print its final state and
# the tail of its log. One short ssh command per check under the command lock. Args: JOBID HH:MM INTERVAL LOGPATH
set -u
J=$1; T=$2; I=$3; LOG=$4
A=plgpnarolski@athena.cyfronet.pl
now=$(date +%s); tgt=$(date -d "$T" +%s); [ $tgt -gt $now ] && sleep $((tgt - now))
for k in $(seq 1 60); do
  s=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "sacct -j $J -X -n -o State%20,Elapsed,Start | head -3" 2>&1)
  echo "$(date +%T) $s"
  case "$s" in *COMPLETED*|*FAILED*|*CANCELLED*|*TIMEOUT*|*OUT_OF_ME*|*NODE_FAIL*) break ;; esac
  sleep $I
done
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "tail -80 $LOG"
echo JOB_WATCH_END
