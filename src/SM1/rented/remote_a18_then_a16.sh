#!/bin/bash
# SM1 sm1dg reorder (13 Nov): one GPU user at a time. A18 first (remote_hn2.sh: smoke, RS 401, 402, 403), then A16
# (remote_dev16.sh) as soon as the driver has staged its inputs (A16_READY). Writes BOTH_DONE at the end.
set -u
B=/workspace/sm1r; mkdir -p "$B/logs"
bash "$B/bin/remote_hn2.sh" > "$B/logs/hn2_queue_driver.log" 2>&1; echo "A18 rc $?" >> "$B/logs/orchestrator.log"
while [ ! -f "$B/A16_READY" ] && [ ! -f "$B/A16_ABANDON" ]; do sleep 60; done
if [ -f "$B/A16_READY" ]; then
  bash "$B/bin/remote_dev16.sh" > "$B/logs/dev16.log" 2>&1; echo "A16 rc $?" >> "$B/logs/orchestrator.log"
fi
date > "$B/BOTH_DONE"
