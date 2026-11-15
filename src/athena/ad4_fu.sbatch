#!/bin/bash -l
#SBATCH -J smadnext-AD4FU
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -C memfs
#SBATCH --exclude=t0010,t0014,t0020
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD4FU-%j.out
# Follow-ups (b) and (c) of the morph-free networks experiment (AD4), prereg Amendment 4: the eleven ViT-B/16 networks
# rebuilt from the pack weights + their trained tensors, scored on the unblanked evaluation images (gate), on the same
# images with everything outside the fixed face ellipse set to grey (H-new-3), and on the landmark-ladder and generator
# pools (H-new-4, H-new-5). Same Python environment as AD4's Athena runs (shared venv). FU_LIMIT=8 for the smoke job.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
LIMIT=${FU_LIMIT:-0}
TAG=fu_${SLURM_JOB_ID}_limit${LIMIT}
PACK_SHA=1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde
W=$MEMFS/fu; mkdir -p "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
PY=$G/venv/bin/python
die() { echo "AD4FU FAIL: $*" >&2; exit 1; }
T0=$SECONDS
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cp "$G/packs/AD4/ad4_pack.tar" "$W/ad4_pack.tar"
[ "$(sha256sum "$W/ad4_pack.tar" | cut -c1-64)" = "$PACK_SHA" ] || die "ad4_pack.tar sha256"
tar -C "$W" -xf "$W/ad4_pack.tar" && rm -f "$W/ad4_pack.tar"
(cd "$W/ad4" && sha256sum -c --quiet SHA256SUMS) || die "ad4 pack content"
cp "$G/packs/AD4/fu_pack.tar" "$W/fu_pack.tar"
[ "$(sha256sum "$W/fu_pack.tar" | cut -c1-64)" = "$(cut -c1-64 "$G/packs/AD4/fu_pack.tar.sha256")" ] || die "fu_pack.tar sha256"
tar -C "$W" -xf "$W/fu_pack.tar" && rm -f "$W/fu_pack.tar"
echo "AD4FU packs ok ($((SECONDS - T0)) s)"
D=$W/data; mkdir -p "$D/manifests"
ln -s "$W/ad4/data/eval" "$D/eval"; ln -s "$W/fu/data/extra" "$D/extra"
cp "$W/ad4/data/manifests/ad4_eval.csv" "$W/fu/data/manifests/fu_extra.csv" "$D/manifests/"
export SMAD_DATA=$D HF_HOME=$W/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
$PY -c "import torch, timm, sys; print('AD4FU env', sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.is_available())"
$PY "$W/fu/src/fu_rescore.py" blank --manifest "$D/manifests/ad4_eval.csv" --root "$D" --limit "$LIMIT"
echo "AD4FU blanked ($((SECONDS - T0)) s)"
R=$W/res/$TAG; mkdir -p "$R"
$PY "$W/fu/src/fu_rescore.py" score --code "$W/ad4/code" --nets "$W/fu/nets" \
  --manifests ad4_eval.csv,ad4_eval_blank.csv,fu_extra.csv --out "$R" --workers 7 --limit "$LIMIT"
cp "$D/manifests/ad4_eval_blank.csv" "$W/fu/build_info.json" "$R/"
echo "wall_s $((SECONDS - T0)) host $(hostname) limit $LIMIT" > "$R/job_info.txt"
mkdir -p "$G/results/AD4_fu"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"
cp "$W/$TAG.tar" "$G/results/AD4_fu/$TAG.tar.part"
(cd "$W" && sha256sum "$TAG.tar") > "$G/results/AD4_fu/$TAG.tar.sha256"
mv "$G/results/AD4_fu/$TAG.tar.part" "$G/results/AD4_fu/$TAG.tar"
echo "AD4FU_DONE $G/results/AD4_fu/$TAG.tar wall $((SECONDS - T0)) s"
