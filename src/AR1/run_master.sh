#!/bin/bash
# all remaining AR1 GPU scoring with thread caps and nice 10 (lead, 11 Nov evening); two lanes. Waits until no AR1
# score.py / crop_rgb.py process is left from the earlier, uncapped chains, then runs the chains (finished files skip).
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
cd /tmp
while pgrep -f "src/AR1/score.py|src/AR1/crop_rgb.py" > /dev/null; do sleep 30; done
echo "lanes start $(date)"
( nice -n 10 bash $S/run_rel.sh >> $O/run_rel.log 2>&1; nice -n 10 bash $S/run_extra2.sh >> $O/run_extra2.log 2>&1;
  nice -n 10 bash $S/run_extra.sh >> $O/run_extra.log 2>&1 ) &
( nice -n 10 bash $S/run_own_nets.sh >> $O/run_own_nets.log 2>&1 ) &
wait
echo "MASTER_DONE $(date)"
