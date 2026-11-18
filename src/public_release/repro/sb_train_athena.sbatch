#!/bin/bash -l
#SBATCH -J relrepro-sb
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/release_repro/logs/%x-%j.out
# Release reproduction (2026-11-18), Athena fallback (WCSS smoke did not start within an hour). Owner: release-
# reproduction agent. Same workload as sb_train.sbatch: published release code (git archive of $REL) trains Sb seed
# $SEED (STEPS optional) from the training pack unpacked on the node RAM disk, with the project's torch 2.2.1 venv
# (Athena has no apptainer); SCORE=1 re-scores the development and training image lists. One result tar out.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
: "${MEMFS:?RAM disk required}" "${REL:?}" "${SEED:?}"
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
R=$G/release_repro; I=$R/inputs; PY=$G/venv/bin/python
TAG=sb_s${SEED}_${STEPS:-full}_athena_${SLURM_JOB_ID}
W=$MEMFS/w; mkdir -p "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"; cd "$W"
echo "start $(date +%FT%T) host $(hostname) job $SLURM_JOB_ID rel $REL seed $SEED steps ${STEPS:-config}"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
cp "$I/pn1_pack_fs.tar" "$I/release_$REL.tar" "$I/repro_lists.tar" "$W/"
[ "$(sha256sum pn1_pack_fs.tar | cut -c1-64)" = "$(cut -c1-64 "$I/pn1_pack_fs.tar.sha256")" ] || { echo "pack sha256 differs"; exit 1; }
tar xf pn1_pack_fs.tar && rm -f pn1_pack_fs.tar
tar xf "release_$REL.tar" && tar xf repro_lists.tar
export HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
$PY -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'cudnn', torch.backends.cudnn.version(), 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)"
CW=$W/pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors
O=$W/out/$TAG; mkdir -p "$O"
$PY -I dcc/training/train.py --config dcc/training/configs/sb.json --list lists/train_Sb.csv --root pn1/data \
  --seed "$SEED" --out "$O/run" --clip-weights "$CW" --workers 7 ${STEPS:+--steps $STEPS}
sha256sum "$O/run/last_trainable.pt" | tee "$O/last_trainable.sha256"
if [ "${SCORE:-0}" = 1 ]; then
  for s in eval train; do
    $PY -I dcc/training/score.py --net "$O/run" --list "lists/score_$s.csv" --root pn1/data --out "$O/rescore_$s.npz" --clip-weights "$CW" --workers 7
  done
fi
tar -C "$W/out" -cf "$W/$TAG.tar" "$TAG" && cp "$W/$TAG.tar" "$R/results/"
echo "done $(date +%FT%T) $R/results/$TAG.tar"
