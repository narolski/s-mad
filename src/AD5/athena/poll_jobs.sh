#!/bin/bash
# Retrains of released methods (AD5): poll Athena job states every 170 s (command lock), append changes to a state
# file; exits when the given number of tasks have reached a terminal state or when STOP_ON_CHANGE=1 and anything changed.
#   poll_jobs.sh STATE_FILE JOBIDS(comma-separated)
S=$1; J=$2; prev=$(tail -1 "$S" 2>/dev/null | cut -d' ' -f2-)
while true; do
  s=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes -o ConnectTimeout=30 plgpnarolski@athena.cyfronet.pl \
      "bash -lc 'sacct -n -X -P -j $J -o JobID,State'" 2>/dev/null | sort | tr '\n' ' ')
  if [ -n "$s" ] && [ "$s" != "$prev" ]; then echo "$(date +%H:%M) $s" >> "$S"; prev=$s; [ "${STOP_ON_CHANGE:-1}" = 1 ] && exit 0; fi
  sleep 170
done
