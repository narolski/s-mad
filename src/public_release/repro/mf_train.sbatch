#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:100G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=06:00:00
#SBATCH --job-name=relrepro-mf
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/release_repro/logs/%x-%j.out
# Release reproduction (2026-11-18). Owner: release-reproduction agent. Workload: the PUBLISHED release code (git archive
# of commit $REL) trains one morph-free network (BACKBONE vitb16|vitl14, seed $SEED) on the data written by release
# morph_free/build_data.py (shipped as one tar, unpacked on node-local $TMPDIR), in the torch 2.2.1 container, then
# re-scores its own training images (no benchmark image is staged). One result tar out.
set -euo pipefail
: "${TMPDIR:?local scratch required}" "${REL:?}" "${SEED:?}" "${BACKBONE:?}"
R=/lustre/pd03/hpc-narolski-1790461090/smad-next/release_repro
I=$R/inputs
SIF=$I/smad_torch221_cu121_v1.sif
TAG=mf_${BACKBONE}_s${SEED}_${STEPS:-full}_${SLURM_JOB_ID}
W=$TMPDIR/w; mkdir -p "$W"; cd "$W"
echo "start $(date +%FT%T) host $(hostname) job $SLURM_JOB_ID rel $REL $BACKBONE seed $SEED steps ${STEPS:-config}"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
cp "$I/mf_data.tar" "$I/clip_weights.tar" "$I/release_$REL.tar" "$I/repro_lists_mf.tar" "$W/"
for t in mf_data clip_weights; do
  [ "$(sha256sum $t.tar | cut -c1-64)" = "$(cut -c1-64 "$I/$t.tar.sha256")" ] || { echo "$t sha256 differs"; exit 1; }
  tar xf $t.tar && rm -f $t.tar
done
tar xf "release_$REL.tar" && tar xf repro_lists_mf.tar
run() { apptainer exec --nv -B "$W" -B "$TMPDIR" --env "HF_HUB_OFFLINE=1,PYTHONUNBUFFERED=1" "$SIF" "$@"; }
run python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'cudnn', torch.backends.cudnn.version(), 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)"
case $BACKBONE in vitb16) CW=$W/a12/vit_base_patch16_clip_224.openai.safetensors;; vitl14) CW=$W/a12/vit_large_patch14_clip_224.openai.safetensors;; esac
O=$W/out/$TAG; mkdir -p "$O"
run python -I dcc/training/train.py --config dcc/training/configs/morph_free_$BACKBONE.json --list mfdata/train_morph_free.csv \
  --root mfdata --seed "$SEED" --out "$O/run" --clip-weights "$CW" --workers 7 ${STEPS:+--steps $STEPS}
sha256sum "$O/run/last_trainable.pt" | tee "$O/last_trainable.sha256"
run python -I dcc/training/score.py --net "$O/run" --backbone "$BACKBONE" --list lists/score_mf_train.csv --root mfdata \
  --out "$O/rescore_train.npz" --clip-weights "$CW" --workers 7
tar -C "$W/out" -cf "$W/$TAG.tar" "$TAG" && cp "$W/$TAG.tar" "$R/results/"
echo "done $(date +%FT%T) $R/results/$TAG.tar"
