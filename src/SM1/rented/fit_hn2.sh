#!/bin/bash
# SM1 H-n2 (DRAFT A18): one ViT-B/16 LoRA fit of the A11 m3 recipe (command line of lora_run.sh RECIPE=m3, unchanged)
# on our own diffusion ladder (DG1 shards 0-5), scored ONLY on the held-out test shards 6-7 (sm1_hn2_test.csv) and on
# its own training rows. Development data only: no benchmark manifest or folder is linked. One result tar + .sha256.
#   TASK=HN2_RS_s401 ARM=RS SEED=401 [STEPS=6250] [LIMIT=0] [WORKERS=6] bash fit_hn2.sh
set -euo pipefail
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
STEPS=${STEPS:-6250}; LIMIT=${LIMIT:-0}; WORKERS=${WORKERS:-6}
B=/workspace/sm1r; OUT=${RESULTS:-$B/results_hn2}; PY=python
die() { echo "HN2 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
[ -f "$B/done/ad4_pack" ] || die "ad4_pack not unpacked"
(cd "$B/data/x" && sha256sum -c --quiet "$B/manifests/hn2/hn2_files.sha256") || die "DG1 files hash"
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") && { echo "already done $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching sha256"
fi
W=$B/work/$TASK; rm -rf "$W"; mkdir -p "$W/data/manifests"; cd "$W"
ln -s "$B/data/x" "$W/data/x"
cp "$B/manifests/hn2/sm1_hn2_test.csv" "$W/data/manifests/"
cp "$B/manifests/hn2/train_hn2${ARM}.csv" "$W/data/manifests/train.csv"
echo "HN2 inputs ready; train.csv $(sha256sum "$W/data/manifests/train.csv" | cut -c1-64) rows $(($(wc -l < "$W/data/manifests/train.csv") - 1))"
ENVS=(SMAD_DATA=$W/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1)
py() { env "${ENVS[@]}" "$PY" "$@"; }
ARCH=a12_clip_vitb16_madation; BSX=(--bs=256)
RUN=$W/runs/SM1/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_hn2${ARM}
TT=$SECONDS
py "$B/ad4/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none --lr 3.33e-06 \
  --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 "${BSX[@]}" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
TRAIN_S=$((SECONDS - TT))
R=$W/res/$TASK; mkdir -p "$R"
py "$B/ad4/src/ad4_score.py" --run "$RUN" --code "$B/ad4/code" --eval-manifest sm1_hn2_test.csv --train-manifest train.csv \
  --true-manifest train.csv --out "$R/hn2test" --workers "$WORKERS" --limit "$LIMIT"
cp "$RUN/meta.json" "$W/train.log" "$R/"
echo "task $TASK recipe m3 arm hn2$ARM seed $SEED steps $STEPS limit $LIMIT train_s $TRAIN_S wall_s $((SECONDS - T0)) host rented $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part" && mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/"
(cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") || die "copy-back check"
rm -rf "$W"
echo "HN2_TASK_DONE $OUT/$TASK.tar wall $((SECONDS - T0)) s"
