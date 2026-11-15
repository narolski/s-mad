#!/bin/bash -l
#SBATCH -J smadnext-SM1F
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/SM1F-%j.out
# SMDD five-partner audit and rebuild (SM1), amendment A7: the frozen CLIP ViT-L/14 feature pass on Athena.
# MODE=smoke (sbatch --export=ALL,MODE=smoke -t 01:00:00): code + test tars only, 400 rows of each test list (the
# DGX equivalence check), one result tar. MODE=full: every tar in packs/SM1, every list. Work in $MEMFS (RAM disk;
# ATHENA.md: -C localfs gives only 4 GB; memfs counts toward --mem, at most 120G per GPU for one-GPU billing).
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
MODE=${MODE:-full}
PY=$G/venv/bin/python
W=$MEMFS/sm1_$MODE; mkdir -p "$W/in"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date -Is
[ -x "$PY" ] || { echo "no $PY" >&2; exit 3; }
if [ "$MODE" = f ]; then                     # A10: only the new lists (FRLL JPEG frames, arm f JPEG copies)
  for n in sm1gpu_code_v2.tar sm1gpu_img_jpegeval.tar sm1gpu_img_armf.tar; do ln -sf "$G/packs/SM1/$n" "$W/in/$n"; ln -sf "$G/packs/SM1/$n.sha256" "$W/in/$n.sha256"; done
  EXTRA="--lists test_eval_jpeg,train_armf_jpeg"
elif [ "$MODE" = a12 ]; then                 # A12 items 11, 13: armd5 morphs and the AF0 softened AR1 copies
  for n in sm1gpu_code_v2.tar sm1gpu_lists_a12.tar sm1gpu_img_a12.tar; do ln -sf "$G/packs/SM1/$n" "$W/in/$n"; ln -sf "$G/packs/SM1/$n.sha256" "$W/in/$n.sha256"; done
  EXTRA="--lists train_armd5,test_af0soft"
elif [ "$MODE" = smoke ]; then
  for n in sm1gpu_code.tar sm1gpu_img_test.tar; do ln -sf "$G/packs/SM1/$n" "$W/in/$n"; ln -sf "$G/packs/SM1/$n.sha256" "$W/in/$n.sha256"; done
  EXTRA="--limit 400 --lists test_eval,test_mad22,test_ar1"
else
  for f in "$G"/packs/SM1/sm1gpu_*.tar; do n=$(basename "$f"); ln -sf "$f" "$W/in/$n"; ln -sf "$f.sha256" "$W/in/$n.sha256"; done
  EXTRA=""
fi
mkdir -p "$W/pack/images" "$W/feats"
for t in "$W"/in/*.tar; do
  n=$(basename "$t")
  (cd "$W/in" && sha256sum -c "$n.sha256") || { echo "sha256 mismatch $n" >&2; exit 2; }
  case "$n" in
    sm1gpu_code.tar|sm1gpu_code_v2.tar) tar -C "$W/pack" -xf "$t" ;;
    sm1gpu_lists_*.tar) ;;                # extracted after the code pack (below)
    *) tar -C "$W/pack/images" -xf "$t" ;;
  esac
  echo "extracted $n $(date -Is)"
done
for t in "$W"/in/sm1gpu_lists_*.tar; do [ -e "$t" ] && tar -C "$W/pack" -xf "$t" && echo "lists overlay $(basename "$t")"; done
"$PY" -c "import torch, timm, numpy, PIL, sys; print(sys.version.split()[0], torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.is_available())"
"$PY" "$W/pack/code/feats_gpu.py" --pack "$W/pack" --out "$W/feats" --workers 14 --bs 128 $EXTRA 2>&1 | tee "$W/feats/run.log"
cp "$G/logs/SM1F-$SLURM_JOB_ID.out" "$W/feats/" 2>/dev/null || true
TAG=sm1gpu_feats_${MODE}_$SLURM_JOB_ID
tar -C "$W" -cf "$W/$TAG.tar" feats
(cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
mkdir -p "$G/results/SM1"
cp "$W/$TAG.tar" "$G/results/SM1/$TAG.tar.part" && mv "$G/results/SM1/$TAG.tar.part" "$G/results/SM1/$TAG.tar"
cp "$W/$TAG.tar.sha256" "$G/results/SM1/"
echo "SM1F_DONE $G/results/SM1/$TAG.tar $(date -Is)"
