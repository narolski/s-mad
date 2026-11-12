#!/bin/bash
# Retrains of released methods (AD5), rented variant: runs ON the rented machine (started detached by start.sh).
# Gets Python 3.9 (system python3.9, else a conda env), then runs the WCSS job script unchanged as a plain script, one
# seed per GPU at a time: seeds are split over the visible GPUs (all of one type), each run at batch 256 on 1 GPU
# (prereg amendment 4). Results: /root/ad5/results/madation_B_s<seed>.tar + .sha256; logs /root/ad5/logs/.
set -uo pipefail
cd /root/ad5
PYB=$(command -v python3.9 || true)
if [ -z "$PYB" ]; then
  command -v conda >/dev/null || { echo "no python3.9 and no conda"; exit 2; }
  [ -x /root/py39/bin/python ] || conda create -y -q -p /root/py39 python=3.9 > logs/conda.log 2>&1
  PYB=/root/py39/bin/python
fi
$PYB --version > logs/python.txt 2>&1
NG=$(nvidia-smi -L | wc -l); nvidia-smi --query-gpu=name,memory.total --format=csv,noheader > logs/gpus.txt
SEEDS=(${AD5_SEEDS:-401 402 403 404 405})
for g in $(seq 0 $((NG-1))); do
  ( for i in $(seq $g $NG $(( ${#SEEDS[@]} - 1 ))); do s=${SEEDS[$i]}
      mkdir -p /root/ad5/tmp/s$s
      CUDA_VISIBLE_DEVICES=$g TMPDIR=/root/ad5/tmp/s$s AD5_L=/root/ad5 AD5_PYTHON=$PYB SLURM_ARRAY_TASK_ID=$s \
        SLURM_ARRAY_JOB_ID=rented ARM=B bash packs/ad5w_train.sbatch > logs/madation_B_s$s.log 2>&1
      echo "seed $s exit $? $(date +%FT%T)" >> logs/progress.txt; rm -rf /root/ad5/tmp/s$s
    done ) &
done
wait; echo ALL_DONE >> logs/progress.txt
