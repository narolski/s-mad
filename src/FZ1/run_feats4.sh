#!/bin/bash
# FZ1 stage 4 (18:30): the single SMDD pass was GPU-bound at ~2.8 images/s (loader workers idle, shared GPU at 96%),
# about 3 h left. Restart as two contiguous halves in parallel (2 loader workers each: 6 CPU processes in total,
# about 4.6 GB GPU memory), TF32, then merge. Each step retried up to 6 times on failure (CUDA OOM at load).
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ1/fz1_feats.py
L=/mnt/t7/smad_next/FZ1/logs
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
B=$(pgrep -f "^/bin/bash /home/narolski/smad-next/src/FZ1/run_feats3b.sh" || true)
P=$(pgrep -f "fz1_feats.py --backbone clip_mad --set smdd\+flip$" || true)
echo "killing bash $B python $P"
[ -n "$B" ] && kill $B
[ -n "$P" ] && kill $P
sleep 15
run() {  # $1 = log name, rest = args
  local log=$1; shift
  for k in 1 2 3 4 5 6; do
    $PY -I $S "$@" > $L/${log}_try$k.log 2>&1 && { echo "$log ok on try $k $(date)" >> $L/progress.txt; return 0; }
    echo "$log failed try $k $(date): $(grep -m1 -E 'Error' $L/${log}_try$k.log)" >> $L/progress.txt
    sleep 90
  done
  return 1
}
run smdd_part_smoke --backbone clip_mad --set smdd+flip --part 2/2 --smoke --workers 2 || exit 1
run smdd_part1of2 --backbone clip_mad --set smdd+flip --part 1/2 --workers 2 &
sleep 60
run smdd_part2of2 --backbone clip_mad --set smdd+flip --part 2/2 --workers 2 &
wait
$PY -I /home/narolski/smad-next/src/FZ1/merge_parts.py clip_mad smdd 2 > $L/merge_parts.log 2>&1 && echo "clip_mad smdd merged $(date)" >> $L/progress.txt
