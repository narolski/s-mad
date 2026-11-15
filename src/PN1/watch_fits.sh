#!/bin/bash
# PN1: follow the eight fits (3545976) and the reference job (3545977); one short ssh per check (command lock),
# every 10 minutes until the forecast start, then at the projected end of each running task (1.5 h after its start),
# then every 10 minutes. Logs state lines; fetches results (fetch.sh) whenever a task has ended.
set -u
A=plgpnarolski@athena.cyfronet.pl
for k in $(seq 1 60); do
  s=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "sacct -j 3545976,3545977 -n -X -o JobID%16,State%12,Elapsed,Start%20" 2>&1)
  echo "== $(date +%T)"; echo "$s"
  n_end=$(echo "$s" | grep -cE "COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_ME|NODE_FAIL")
  n_all=$(echo "$s" | grep -cE "^ *354597[67]")
  if [ "$n_end" -gt 0 ]; then bash /home/narolski/smad-next/src/PN1/fetch.sh > /mnt/t7/smad_next/PN1/fetch_last.log 2>&1; echo "fetched rc $?"; fi
  if [ "$n_all" -ge 9 ] && [ "$n_end" -ge 9 ]; then echo ALL_ENDED; break; fi
  if echo "$s" | grep -q RUNNING; then sleep 1200; else sleep 600; fi
done
echo WATCH_FITS_END
