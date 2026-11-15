#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J sm1-a16
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:120G
#SBATCH --time=0-02:00:00
#SBATCH --exclude=r10-15,r10-8,r18-8
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/sm1-a16-%j.out
# SM1 amendment A16 (H-n1) on WCSS H100: saved ViT-B/16 fits SM1B_{a,e,f}_s{401,402} scored on DG1 rungs FRESH1/NOISES/
# NOISEX/SEMS/SEMX/MIR/REC20 (development data only; no benchmark folder or manifest is staged). All work in $TMPDIR
# (local NVMe); inputs = a few tars on PD (sha256 checked); one result tar per fit back to PD with sha256.
# Platform equivalence (A16 WCSS line): each fit's rebuilt network must reproduce 256 stored AR1 camera-photo rows within
# 2e-3 (sm1_lora_audit.py --check-npz ar1eval); a failed check stops that fit (no scores written for it).
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/SM1A16; OUT=$L/results/SM1A16
PY=$HOME/dmenv/bin/python
mkdir -p "$OUT"
hostname; nvidia-smi -L; date -Is
cd "$P"
sha256sum -c ad4_pack.tar.sha256 sm1gpu_img_test.tar.sha256 sm1lora_manifests_v2.tar.sha256 sm1_dev16_files.tar.sha256 \
  sm1_dev16_eval.csv.sha256 SM1B_a_s401.tar.sha256 SM1B_a_s402.tar.sha256 SM1B_e_s401.tar.sha256 SM1B_e_s402.tar.sha256 \
  SM1B_f_s401.tar.sha256 SM1B_f_s402.tar.sha256
B=$TMPDIR/sm1r; mkdir -p "$B/data/x" "$B/manifests/v2" "$B/fits" "$B/res" "$B/work"
tar -C "$B" -xf ad4_pack.tar --exclude "ad4/data/eval" --exclude "ad4/data/train"   # no benchmark frame staged
(cd "$B/ad4" && sha256sum -c --quiet --ignore-missing SHA256SUMS)
tar -C "$B/data/x" -xf sm1gpu_img_test.tar --wildcards "mnt/t7/smad_next/AR1/src/*"   # FRGC / colorFERET camera photos only (check rows)
tar -C "$B/data/x" -xf sm1_dev16_files.tar
tar -C "$B/manifests/v2" -xf sm1lora_manifests_v2.tar
cp sm1_dev16_eval.csv sm1_lora_audit.py "$B/"
echo "staged $(date -Is)"; df -h "$TMPDIR" | tail -1
"$PY" -c "import torch, timm, numpy, PIL; print('env', torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))"
rc_all=0
for F in SM1B_a_s401 SM1B_a_s402 SM1B_e_s401 SM1B_e_s402 SM1B_f_s401 SM1B_f_s402; do
  T=SM1E_${F#SM1B_}
  tar -C "$B/fits" -xf "$P/$F.tar"
  W=$B/work/$F; mkdir -p "$W/data/manifests"; ln -s "$B/data/x" "$W/data/x"
  cp "$B/sm1_dev16_eval.csv" "$B/manifests/v2/sm1_ar1_eval.csv" "$W/data/manifests/"
  if env SMAD_DATA=$W/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 "$PY" "$B/sm1_lora_audit.py" \
       --fit "$B/fits/$F" --code "$B/ad4/code" --manifest sm1_dev16_eval.csv --out "$B/res/$T" --workers 6 \
       --check-npz ar1eval/scores_eval.npz --check-manifest sm1_ar1_eval.csv; then
    tar -C "$B/res" -cf "$B/$T.tar" "$T"; (cd "$B" && sha256sum "$T.tar" > "$T.tar.sha256")
    cp "$B/$T.tar" "$OUT/$T.tar.part" && mv "$OUT/$T.tar.part" "$OUT/$T.tar"; cp "$B/$T.tar.sha256" "$OUT/"
    (cd "$OUT" && sha256sum -c --quiet "$T.tar.sha256") && echo "SM1E_FIT_DONE $T $(date -Is)"
  else
    echo "SM1E_FIT_FAILED $F (reproduction check or scoring)"; rc_all=1
    [ -f "$B/res/$T/check.json" ] && cp "$B/res/$T/check.json" "$OUT/${T}_check_FAILED.json"
  fi
done
date -Is > "$OUT/SM1E_ALL_DONE"
exit $rc_all
