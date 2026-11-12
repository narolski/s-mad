#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ms1-heldout
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:40G
#SBATCH --no-requeue
#SBATCH --time=0-02:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ms1-heldout-%j.out
# MS1 held-out sharp sources (prereg part 2, 2.2): every fit's kept LoRA and head (result tar: meta.json +
# last_trainable.pt) rescored with the unchanged src/PN1/rescore.py on CFD and KDEF frames (ms1_heldout_pack.tar).
# Submitted only when all fit tars exist (MS1_TASKS lists them). All IO in $TMPDIR; one tar back to results/MS1H.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=${MS1_P:-$L/packs/MS1}; RES=${MS1_RES:-$L/results/MS1}; OUT=${MS1_OUT:-$L/results/MS1H}
TASKS=${MS1_TASKS:-"MS1_Sb_s403 MS1_SbM3_s403 MS1_SbV_s403 MS1_Sb_s404 MS1_SbM3_s404 MS1_SbV_s404 MS1_Sb_s405 MS1_SbM3_s405 MS1_SbV_s405 MS1_Sb_s406 MS1_SbM3_s406 MS1_SbV_s406 MS1_Sb_s407 MS1_SbM3_s407 MS1_SbV_s407"}
PY=${MS1_PY:-$HOME/dmenv/bin/python}
mkdir -p "$OUT"
hostname; nvidia-smi -L || true; date -Is
for T in $TASKS; do (cd "$RES" && sha256sum -c --quiet "$T.tar.sha256") || { echo "missing or bad $T"; exit 2; }; done
(cd "$P" && sha256sum -c --quiet ms1_heldout_pack.tar.sha256)
W=$TMPDIR/h; mkdir -p "$W/out"
tar -C "$W" -xf "$P/ms1_heldout_pack.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS)
D=$W/data; mkdir -p "$D"; ln -s "$W/pn1/data/eval" "$D/eval"; ln -s "$W/pn1/data/manifests" "$D/manifests"
"$PY" -c "import sys, torch, timm; print('env', sys.version.split()[0], torch.__version__, timm.__version__)" | tee "$W/out/env.txt"
for T in $TASKS; do
  tar -C "$W" -xf "$RES/$T.tar" "$T/meta.json" "$T/last_trainable.pt"
  ARM=${T#MS1_}; ARM=${ARM%_s*}; SEED=${T##*_s}
  for FAM in cfd kdef; do
    SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 "$PY" "$W/pn1/src/rescore.py" --resdir "$W/$T" --code "$W/pn1/code" \
      --manifest ms1_heldout.csv --fam "$FAM" --out "$W/out/MS1H_${ARM}_s${SEED}_${FAM}.npz" --workers 7
  done
  rm -rf "$W/$T"
done
TAG=MS1H_${SLURM_JOB_ID:-local}
tar -C "$W" -cf "$W/$TAG.tar" out
cp "$W/$TAG.tar" "$OUT/$TAG.tar.part"; (cd "$W" && sha256sum "$TAG.tar") > "$OUT/$TAG.tar.sha256"
mv "$OUT/$TAG.tar.part" "$OUT/$TAG.tar"; (cd "$OUT" && sha256sum -c "$TAG.tar.sha256")
echo "MS1H_DONE $OUT/$TAG.tar $(date -Is)"
