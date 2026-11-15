#!/usr/bin/env bash
# after.sh <backbone> <name> <n> <queue> : wait until feat/<backbone>/<name>.done == n, then run the queue.
d=/mnt/t7/smad_next/AF0/feat/$1/$2.done
until [ "$(cat $d 2>/dev/null)" = "$3" ] && ! pgrep -f "feat.py --backbone $1 .*--name $2( |$)" >/dev/null; do sleep 20; done
exec /home/narolski/smad-next/src/AF0/run_feats.sh "$4"
