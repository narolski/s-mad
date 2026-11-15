#!/bin/bash
# SM1 rented A100: one ViT-B/16 LoRA fit (amendment A13). The training and scoring command lines are those of
# src/SM1/lora_run.sh with RECIPE=m3, unchanged; only the data are read from the once-unpacked packs under
# /workspace/sm1r (lora_run.sh unpacks the same tars into a RAM disk per job). After the registered scores, the Part 2
# audit set is scored by the same network (A12 item 10, sm1_lora_audit.py). One result tar + .sha256 per fit.
#   TASK=SM1B_a_s401 ARM=a SEED=401 [STEPS=6250] [LIMIT=0] [WORKERS=6] [RESULTS=/workspace/sm1r/results] bash fit_local.sh
set -euo pipefail
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
STEPS=${STEPS:-6250}; LIMIT=${LIMIT:-0}; WORKERS=${WORKERS:-6}
B=/workspace/sm1r; OUT=${RESULTS:-$B/results}; PY=python
die() { echo "SM1R FAIL: $*" >&2; exit 1; }
T0=$SECONDS
for n in ad4_pack sm1gpu_img_base sm1gpu_img_armsc sm1gpu_img_arme sm1gpu_img_test sm1gpu_img_audit sm1gpu_img_jpegeval \
         sm1lora_manifests_v2 sm1lora_manifests_audit; do [ -f "$B/done/$n" ] || die "pack $n not unpacked"; done
[ "$ARM" = f ] && { [ -f "$B/done/sm1gpu_img_armf" ] || die "armf not unpacked"; }
case "$ARM" in b|bp) MAN=$B/manifests/b; [ -f "$B/done/sm1gpu_img_armsb" ] && [ -f "$B/done/sm1lora_manifests_b" ] || die "armsb / manifests_b";;
               *) MAN=$B/manifests/v2 ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") && { echo "already done $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching sha256"
fi
W=$B/work/$TASK; rm -rf "$W"; mkdir -p "$W/data/manifests"; cd "$W"
ln -s "$B/data/x" "$W/data/x"
ln -s "$B/ad4/data/eval" "$W/data/eval"
ln -s "$B/ad4/data/manifests/ad4_eval.csv" "$W/data/manifests/ad4_eval.csv"
cp "$MAN/sm1_ar1_eval.csv" "$MAN/sm1_jpeg_eval.csv" "$W/data/manifests/"
cp "$B/manifests/audit/sm1_audit_eval.csv" "$W/data/manifests/"
cp "$MAN/train_sm1${ARM}_s${SEED}.csv" "$W/data/manifests/train.csv"
head -9 "$W/data/manifests/train.csv" > "$W/data/manifests/train_head8.csv"
echo "SM1R inputs ready ($((SECONDS - T0)) s); train.csv $(sha256sum "$W/data/manifests/train.csv" | cut -c1-64) rows $(($(wc -l < "$W/data/manifests/train.csv") - 1))"
ENVS=(SMAD_DATA=$W/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1)
py() { env "${ENVS[@]}" "$PY" "$@"; }
py -c "import torch, timm, sys; print('SM1R env', sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
ARCH=a12_clip_vitb16_madation; BSX=(--bs=256)                      # RECIPE m3 of lora_run.sh (AD4's M3 row)
RUN=$W/runs/SM1/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_sm1${ARM}
TT=$SECONDS
py "$B/ad4/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none --lr 3.33e-06 \
  --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 "${BSX[@]}" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
TRAIN_S=$((SECONDS - TT))
echo "SM1R trained ($TRAIN_S s of training, $((SECONDS - T0)) s total; $(python -c "print(round($STEPS / max($TRAIN_S, 1), 3))") steps/s incl. start-up)"
R=$W/res/$TASK; mkdir -p "$R"
py "$B/ad4/src/ad4_score.py" --run "$RUN" --code "$B/ad4/code" --eval-manifest ad4_eval.csv --train-manifest train.csv \
  --true-manifest train.csv --out "$R/ad4eval" --workers "$WORKERS" --limit "$LIMIT"
py "$B/ad4/src/ad4_score.py" --run "$RUN" --code "$B/ad4/code" --eval-manifest sm1_ar1_eval.csv \
  --train-manifest train_head8.csv --true-manifest train_head8.csv --out "$R/ar1eval" --workers "$WORKERS" --limit "$LIMIT"
py "$B/ad4/src/ad4_score.py" --run "$RUN" --code "$B/ad4/code" --eval-manifest sm1_jpeg_eval.csv \
  --train-manifest train_head8.csv --true-manifest train_head8.csv --out "$R/jpegeval" --workers "$WORKERS" --limit "$LIMIT"
cp "$RUN/meta.json" "$W/train.log" "$R/"
py "$B/bin/sm1_lora_audit.py" --fit "$R" --code "$B/ad4/code" --manifest sm1_audit_eval.csv --out "$R/audit" \
  --workers "$WORKERS" --ncheck "$([ "$LIMIT" = 0 ] && echo 256 || echo "$LIMIT")"
echo "task $TASK recipe m3 arm $ARM seed $SEED steps $STEPS limit $LIMIT train_s $TRAIN_S wall_s $((SECONDS - T0)) host rented $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part" && mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/"
(cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") || die "copy-back check"
echo "SM1R_TASK_DONE $OUT/$TASK.tar wall $((SECONDS - T0)) s"
