#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:100G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=03:00:00
#SBATCH --job-name=relrepro-sb
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/release_repro/logs/%x-%j.out
# Release reproduction (2026-11-18). Owner: release-reproduction agent. Workload: the PUBLISHED release code (git archive
# of commit $REL) trains one Sb network (seed $SEED, $STEPS updates; STEPS empty = the config's 6,250) from the training
# pack unpacked on node-local $TMPDIR, inside the original torch 2.2.1 container; with SCORE=1 it then re-scores the
# development (pn1_eval) and training image lists with release training/score.py. One result tar out.
# Env: REL (commit), SEED, STEPS (optional), SCORE (0/1).
set -euo pipefail
: "${TMPDIR:?local scratch required}" "${REL:?}" "${SEED:?}"
R=/lustre/pd03/hpc-narolski-1790461090/smad-next/release_repro
I=$R/inputs
SIF=$I/smad_torch221_cu121_v1.sif
TAG=sb_s${SEED}_${STEPS:-full}_${SLURM_JOB_ID}
W=$TMPDIR/w; mkdir -p "$W"; cd "$W"
echo "start $(date +%FT%T) host $(hostname) job $SLURM_JOB_ID rel $REL seed $SEED steps ${STEPS:-config}"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
cp "$I/pn1_pack_fs.tar" "$I/release_$REL.tar" "$I/repro_lists.tar" "$W/"
[ "$(sha256sum pn1_pack_fs.tar | cut -c1-64)" = "$(cut -c1-64 "$I/pn1_pack_fs.tar.sha256")" ] || { echo "pack sha256 differs"; exit 1; }
tar xf pn1_pack_fs.tar && rm -f pn1_pack_fs.tar
tar xf "release_$REL.tar" && tar xf repro_lists.tar
run() { apptainer exec --nv -B "$W" -B "$TMPDIR" --env "HF_HUB_OFFLINE=1,PYTHONUNBUFFERED=1" "$SIF" "$@"; }
run python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'cudnn', torch.backends.cudnn.version(), 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)"
CW=$W/pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors
O=$W/out/$TAG; mkdir -p "$O"
run python -I dcc/training/train.py --config dcc/training/configs/sb.json --list lists/train_Sb.csv --root pn1/data \
  --seed "$SEED" --out "$O/run" --clip-weights "$CW" --workers 7 ${STEPS:+--steps $STEPS}
sha256sum "$O/run/last_trainable.pt" | tee "$O/last_trainable.sha256"
if [ "${SCORE:-0}" = 1 ]; then
  for s in eval train; do
    run python -I dcc/training/score.py --net "$O/run" --list "lists/score_$s.csv" --root pn1/data --out "$O/rescore_$s.npz" --clip-weights "$CW" --workers 7
  done
fi
tar -C "$W/out" -cf "$W/$TAG.tar" "$TAG" && cp "$W/$TAG.tar" "$R/results/"
echo "done $(date +%FT%T) $R/results/$TAG.tar"
