#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=01:00:00
#SBATCH --job-name=ad4-smoke-equiv
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ad4-smoke-equiv-%j.out
# Owner: reading owner of the morph-free networks experiment (AD4). Workload, all already on Lustre (prereg Amendment 5 (c), (d)):
# 1. smoke: the unchanged run.sh of AD4_m3mf_s401 with 50 steps and 8 scored images, into a separate smoke root (never read);
# 2. scorer-equivalence gate on the H100 stack: the original A47 I-3 ViT-B/16 morph-free network (seed 1, last.pt) re-scored with
#    ad4_score.py in the container, using the extraction the smoke made; one result tar to smad-next/results/AD4_equiv/.
set -euo pipefail
: "${TMPDIR:?local scratch required}"
L=/lustre/pd03/hpc-narolski-1790461090
B=$L/smad-next
A47=$L/smadcvpr/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3
SIF=/lustre/software-data/container-images/pytorch_latest.sif
[ -f "$A47/last.pt" ] && [ -f "$A47/meta.json" ] || { echo "AD4 equiv: no A47 run at $A47; nothing to do"; exit 3; }
SR=$B/smoke_AD4/root
mkdir -p "$SR/smad-next/packs/AD4" "$SR/smad-next/results" "$SR/smadcvpr" "$B/results/AD4_equiv"
ln -sfn "$B/packs/AD4/ad4_pack.tar" "$SR/smad-next/packs/AD4/ad4_pack.tar"
ln -sfn "$L/smadcvpr/packs" "$SR/smadcvpr/packs"
W=$TMPDIR/task_smoke; mkdir -p "$W"
echo "AD4 smoke+equiv $SLURM_JOB_ID host $(hostname) $(date +%FT%T)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
cd "$W"
TASK_DIR="$B/staging/AD4/AD4_m3mf_s401" TASK_WORK="$W" AD4_ROOT="$SR" AD4_STEPS=50 AD4_LIMIT=8 \
  bash "$B/staging/AD4/AD4_m3mf_s401/run.sh"
echo "AD4 smoke done $(date +%FT%T)"
D=$W/data
head -n 9 "$W/ad4/data/manifests/train_i3.csv" > "$W/equiv_train8.csv"
ln -sfn "$W/equiv_train8.csv" "$D/manifests/equiv_train8.csv"
O=$W/equiv_h100; mkdir -p "$O"
apptainer exec --nv -B /lustre -B "$W" -B "$TMPDIR" \
  --env "PYTHONPATH=$W/pylib_a12:$W/pylib:$W/ad4/code,SMAD_DATA=$D,HF_HOME=$W/ad4/hf,HF_HUB_OFFLINE=1,PYTHONUNBUFFERED=1" \
  "$SIF" python "$W/ad4/src/ad4_score.py" --run "$A47" --code "$W/ad4/code" --eval-manifest ad4_eval.csv \
  --train-manifest equiv_train8.csv --true-manifest train_i3.csv --out "$O" --workers 7
tar -C "$W" -cf "$W/equiv_h100_$SLURM_JOB_ID.tar" equiv_h100
cp "$W/equiv_h100_$SLURM_JOB_ID.tar" "$B/results/AD4_equiv/"
(cd "$W" && sha256sum "equiv_h100_$SLURM_JOB_ID.tar") > "$B/results/AD4_equiv/equiv_h100_$SLURM_JOB_ID.tar.sha256"
echo "AD4 equiv done $(date +%FT%T)"
