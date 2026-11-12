#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J sm1-a18
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:60G
#SBATCH --time=0-08:00:00
#SBATCH --exclude=r10-15,r10-8,r18-8
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/sm1-a18-%j.out
# SM1 amendment A18 (H-n2) on WCSS H100: the A11 m3 recipe trained on DG1 shards 0-5 (arm RS), scored only on shards
# 6-7 and its training rows; a 200-step smoke fit first, then seeds 401, 402, 403 one after another (fit_hn2.sh,
# unchanged command line). Development data only: only code / weights (ad4_pack without its evaluation and training
# frames), the DG1 images and the A18 manifests are staged. All work in $TMPDIR; one result tar per fit back to PD.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/SM1A18; OUT=$L/results/SM1A18
mkdir -p "$OUT"
hostname; nvidia-smi -L; date -Is
cd "$P"
A=$L/packs/SM1A16                                   # ad4_pack shared with A16 (same pinned file)
(cd "$A" && sha256sum -c ad4_pack.tar.sha256)
sha256sum -c sm1_hn2_manifests.tar.sha256 sm1_hn2_files.tar.sha256
B=$TMPDIR/sm1r; mkdir -p "$B/data/x" "$B/manifests/hn2" "$B/bin" "$B/done"
tar -C "$B" -xf "$A/ad4_pack.tar" --exclude "ad4/data/eval" --exclude "ad4/data/train"
(cd "$B/ad4" && sha256sum -c --quiet --ignore-missing SHA256SUMS) && touch "$B/done/ad4_pack"
tar -C "$B/manifests/hn2" -xf sm1_hn2_manifests.tar
tar -C "$B/data/x" -xf sm1_hn2_files.tar
cp fit_hn2.sh "$B/bin/"
export SM1R_BASE=$B SM1R_PY=$HOME/dmenv/bin/python
"$SM1R_PY" -c "import torch, timm, numpy, PIL; print('env', torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))"
echo "staged $(date -Is)"
TASK=HN2_RS_s401_smoke ARM=RS SEED=401 STEPS=200 LIMIT=64 RESULTS=$B/smoke bash "$B/bin/fit_hn2.sh" > "$OUT/hn2_smoke_$SLURM_JOB_ID.log" 2>&1 \
  || { echo "SMOKE FAILED"; exit 1; }
echo "smoke passed $(date -Is)"
for T in HN2_RS_s401 HN2_RS_s402 HN2_RS_s403; do
  SEED=${T##*_s}
  for try in 1 2; do
    if TASK=$T ARM=RS SEED=$SEED RESULTS=$B/results_hn2 bash "$B/bin/fit_hn2.sh" >> "$OUT/${T}_$SLURM_JOB_ID.log" 2>&1; then
      cp "$B/results_hn2/$T.tar" "$OUT/$T.tar.part" && mv "$OUT/$T.tar.part" "$OUT/$T.tar"; cp "$B/results_hn2/$T.tar.sha256" "$OUT/"
      (cd "$OUT" && sha256sum -c --quiet "$T.tar.sha256") && echo "HN2_FIT_DONE $T try $try $(date -Is)"
      break
    fi
    echo "HN2_FIT_FAILED $T try $try $(date -Is)"
    grep -qiE "loss +nan|loss +inf|non-finite" "$OUT/${T}_$SLURM_JOB_ID.log" && { echo "$T non-finite: not rerun"; break; }
  done
done
date -Is > "$OUT/HN2_ALL_DONE"
