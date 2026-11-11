#!/bin/bash -l
#SBATCH -J smadnext-SM1A
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH -C memfs
#SBATCH --exclude=t0010
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/SM1A-%j.out
# SM1 amendment A12 item 10: scoring-only pass of the Part 2 audit set (10,055 images) with finished LoRA fits.
# FITS="SM1L_a_s403 SM1L_c_s401 ..." (result tars in results/SM1). Per fit: sha256 of the tar, extract, rebuild the
# network from meta.json + ad4eval/last_trainable.pt (sm1_lora_audit.py; reproduction check on 256 AD4 eval rows),
# score the audit manifest; one result tar SM1A_<fit>.tar per fit.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}" "${FITS:?}"
W=$MEMFS/work_SM1A; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR" "$W"; cd "$W"
OUT=$G/results/SM1; PY=$G/venv/bin/python
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date -Is
(cd "$G/packs/AD4" && sha256sum -c --quiet ad4_pack.tar.sha256)
tar -C "$W" -xf "$G/packs/AD4/ad4_pack.tar"; rm -rf "$W/ad4/data/train"
mkdir -p "$W/data/x" "$W/data/manifests"
(cd "$G/packs/SM1" && sha256sum -c --quiet sm1gpu_img_audit.tar.sha256 && sha256sum -c --quiet sm1lora_manifests_audit.tar.sha256)
tar -C "$W/data/x" -xf "$G/packs/SM1/sm1gpu_img_audit.tar"
tar -C "$W/data/manifests" -xf "$G/packs/SM1/sm1lora_manifests_audit.tar"
ln -s "$W/ad4/data/eval" "$W/data/eval"; ln -s "$W/ad4/data/manifests/ad4_eval.csv" "$W/data/manifests/"
cp "$G/tasks/SM1/sm1_lora_audit.py" "$W/"
for F in $FITS; do
  T=SM1A_$F
  if [ -e "$OUT/$T.tar" ]; then echo "already done $T"; continue; fi
  (cd "$OUT" && sha256sum -c --quiet "$F.tar.sha256")
  mkdir -p "$W/fits"; tar -C "$W/fits" -xf "$OUT/$F.tar"
  env SMAD_DATA=$W/data HF_HOME=$W/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 "$PY" "$W/sm1_lora_audit.py" \
    --fit "$W/fits/$F" --code "$W/ad4/code" --manifest sm1_audit_eval.csv --out "$W/res/$T" --workers 12
  tar -C "$W/res" -cf "$W/$T.tar" "$T"; (cd "$W" && sha256sum "$T.tar") > "$W/$T.tar.sha256"
  cp "$W/$T.tar" "$OUT/$T.tar.part" && mv "$OUT/$T.tar.part" "$OUT/$T.tar"; cp "$W/$T.tar.sha256" "$OUT/"
  rm -rf "$W/fits/$F"
  echo "SM1A_FIT_DONE $T $(date -Is)"
done
echo "SM1A_ALL_DONE $(date -Is)"
