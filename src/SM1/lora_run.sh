#!/bin/bash
# SMDD five-partner audit and rebuild (SM1), amendment A9: one LoRA fit of the record's MADation ViT-L/14 recipe (the
# M3L command line of AD4's run.sh, unchanged) on one SM1 arm and seed, then scores on AD4's evaluation manifest and on
# the AR1 ladder manifest. Inputs on Athena: packs/AD4/ad4_pack.tar (code, CLIP weights, evaluation frames),
# packs/SM1/sm1gpu_img_{base,armsc,arme,test,audit}.tar (the SM1 images, extracted under data/x/), packs/SM1/
# sm1lora_manifests_v2.tar (train_sm1<arm>_s<seed>.csv, sm1_ar1_eval.csv). All work in $W (RAM disk), one result tar.
#   TASK=SM1L_c_s401 ARM=c SEED=401 W=... G=... PY=... [STEPS=6250] [LIMIT=0] bash lora_run.sh
set -euo pipefail
: "${TASK:?}" "${ARM:?}" "${SEED:?}" "${W:?}" "${G:?}" "${PY:?}"
STEPS=${STEPS:-6250}; LIMIT=${LIMIT:-0}; WORKERS=${WORKERS:-14}
OUT=$G/results/SM1
die() { echo "SM1L FAIL: $*" >&2; exit 1; }
T0=$SECONDS
mkdir -p "$W" "$OUT"; cd "$W"
if [ -e "$OUT/$TASK.tar" ]; then
  (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") && { echo "already done $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching sha256"
fi
(cd "$G/packs/AD4" && sha256sum -c --quiet ad4_pack.tar.sha256) || die "ad4_pack sha256"
tar -C "$W" -xf "$G/packs/AD4/ad4_pack.tar"
(cd "$W/ad4" && sha256sum -c --quiet SHA256SUMS) || die "ad4 pack content"
rm -rf "$W/ad4/data/train"                                  # not used by SM1 (frees RAM disk)
mkdir -p "$W/data/x" "$W/data/manifests"
SETS="base armsc arme test audit"
[ "$ARM" = f ] && SETS="$SETS armf"                                 # A10: the JPEG copies of arm (f)
case "$ARM" in b|bp) SETS="$SETS armsb" ;; esac                     # A12 item 12: arms b, b' (ViT-B/16)
[ -f "$G/packs/SM1/sm1gpu_img_jpegeval.tar.sha256" ] && SETS="$SETS jpegeval"   # A10: FRLL genuine JPEG frames
for s in $SETS; do
  (cd "$G/packs/SM1" && sha256sum -c --quiet "sm1gpu_img_$s.tar.sha256") || die "sm1gpu_img_$s sha256"
  tar -C "$W/data/x" -xf "$G/packs/SM1/sm1gpu_img_$s.tar"
done
MAN=${MANIFESTS:-sm1lora_manifests_v2}                             # A12 item 12: sm1lora_manifests_b for b, b'
(cd "$G/packs/SM1" && sha256sum -c --quiet "$MAN.tar.sha256") || die "manifests sha256"
tar -C "$W/data/manifests" -xf "$G/packs/SM1/$MAN.tar"
ln -s "$W/ad4/data/eval" "$W/data/eval"
for f in "$W"/ad4/data/manifests/ad4_eval.csv; do ln -s "$f" "$W/data/manifests/"; done
cp "$W/data/manifests/train_sm1${ARM}_s${SEED}.csv" "$W/data/manifests/train.csv"
head -9 "$W/data/manifests/train.csv" > "$W/data/manifests/train_head8.csv"
echo "SM1L inputs ready ($((SECONDS - T0)) s); train.csv $(sha256sum "$W/data/manifests/train.csv" | cut -c1-64) rows $(($(wc -l < "$W/data/manifests/train.csv") - 1))"
df -h "$W" | tail -1
ENVS=(SMAD_DATA=$W/data HF_HOME=$W/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1)
py() { env "${ENVS[@]}" "$PY" "$@"; }
py -c "import torch, timm, sys; print('SM1L env', sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.is_available())"
RECIPE=${RECIPE:-m3l}                                       # A11: m3 = the ViT-B/16 recipe (AD4's M3 row)
case "$RECIPE" in
  m3l) ARCH=a12_clip_vitl14_madation; BSX=(--bs=32 --accum=8) ;;
  m3)  ARCH=a12_clip_vitb16_madation; BSX=(--bs=256) ;;
  *) die "recipe $RECIPE" ;;
esac
RUN=$W/runs/SM1/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_sm1${ARM}
py "$W/ad4/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none --lr 3.33e-06 \
  --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 "${BSX[@]}" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
echo "SM1L trained ($((SECONDS - T0)) s)"
R=$W/res/$TASK; mkdir -p "$R"
py "$W/ad4/src/ad4_score.py" --run "$RUN" --code "$W/ad4/code" --eval-manifest ad4_eval.csv --train-manifest train.csv \
  --true-manifest train.csv --out "$R/ad4eval" --workers "$WORKERS" --limit "$LIMIT"
py "$W/ad4/src/ad4_score.py" --run "$RUN" --code "$W/ad4/code" --eval-manifest sm1_ar1_eval.csv \
  --train-manifest train_head8.csv --true-manifest train_head8.csv --out "$R/ar1eval" --workers "$WORKERS" --limit "$LIMIT"
if [ -f "$W/data/manifests/sm1_jpeg_eval.csv" ] && [[ " $SETS " == *" jpegeval "* ]]; then
  py "$W/ad4/src/ad4_score.py" --run "$RUN" --code "$W/ad4/code" --eval-manifest sm1_jpeg_eval.csv \
    --train-manifest train_head8.csv --true-manifest train_head8.csv --out "$R/jpegeval" --workers "$WORKERS" --limit "$LIMIT"
fi
cp "$RUN/meta.json" "$W/train.log" "$R/"
echo "task $TASK recipe $RECIPE arm $ARM seed $SEED steps $STEPS limit $LIMIT wall_s $((SECONDS - T0)) host $(hostname)" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part" && mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/"
echo "SM1L_TASK_DONE $OUT/$TASK.tar wall $((SECONDS - T0)) s"
