#!/usr/bin/env bash
# Sequential GPU feature queue for AF0. Each line of the job file: <backbone> <list> <name> [flip]
# Retries a job up to 5 times (the shared GB10 sometimes refuses the first allocation); resumable via feat.py.
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AF0
while read -r bb lst name flip; do
  [ -z "${bb:-}" ] && continue
  case "$bb" in \#*) continue;; esac
  for t in 1 2 3 4 5; do
    echo "$(date +%T) start $bb $name try $t"
    if nice -n 10 $PY -I feat.py --backbone "$bb" --list /mnt/t7/smad_next/AF0/lists/$lst.csv --name "$name" \
        ${flip:+--flip} --bs 16 --workers 4 2>&1 | grep -v -i warning; then
      d=/mnt/t7/smad_next/AF0/feat/$bb/$name
      n=$(wc -l < /mnt/t7/smad_next/AF0/lists/$lst.csv); n=$((n-1))
      if [ "$(cat $d.done 2>/dev/null)" = "$n" ]; then echo "$(date +%T) done $bb $name"; break; fi
    fi
    sleep 30
  done
done < "$1"
