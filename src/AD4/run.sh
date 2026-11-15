#!/bin/bash
# AD4 slot-queue task (OWNER_BRIEF.md): one network = one task. Trains one row (recipe M3 or M3L, arm mf = the
# registered A47 I-3 morph-free data, or perm = the same data with labels permuted per seed), last checkpoint, then
# scores it on the AD4 evaluation manifest and on its own training manifest, and copies ONE result tar to
# $ROOT/smad-next/results/AD4/<TASK>.tar. Reads $TASK_DIR/task.env (TASK RECIPE ARM SEED).
# IO: three tars in (ad4_pack.tar from smad-next/packs/AD4; pylib.tar, pylib_a12.tar from smadcvpr/packs, each
# sha256-checked), everything else in $TASK_WORK (node-local), one tar out.
# Local test (DGX): AD4_LOCAL=1 (host python $AD4_PY, no container, no library packs), AD4_ROOT (mock root),
# AD4_STEPS (train.py --steps), AD4_LIMIT (rows scored per manifest). On WCSS none of these is set.
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
source "$TASK_DIR/task.env"
: "${TASK:?}" "${RECIPE:?}" "${ARM:?}" "${SEED:?}"
ROOT=${AD4_ROOT:-/lustre/pd03/hpc-narolski-1790461090}
PACK=$ROOT/smad-next/packs/AD4/ad4_pack.tar
PACK_SHA=1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde
LIBP=$ROOT/smadcvpr/packs
OUT=$ROOT/smad-next/results/AD4
SIF=/lustre/software-data/container-images/pytorch_latest.sif
W=$(cd -P "$TASK_WORK" && pwd)
die() { echo "AD4 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "AD4 task $TASK recipe $RECIPE arm $ARM seed $SEED host $(hostname) work $W $(date +%FT%T)"
case "$W" in /lustre*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") \
    && { echo "AD4 already done: $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
fi
case "$RECIPE" in
  m3)  ARCH=a12_clip_vitb16_madation; BSX=(--bs=256) ;;
  m3l) ARCH=a12_clip_vitl14_madation; BSX=(--bs=32 --accum=8) ;;
  *) die "recipe $RECIPE" ;;
esac
case "$ARM" in
  mf)   MAN=train_i3.csv ;;
  perm) MAN=train_perm_s$SEED.csv ;;
  *) die "arm $ARM" ;;
esac
case "$SEED" in 401|402|403|404|405) ;; *) die "seed $SEED" ;; esac
STEPS=${AD4_STEPS:-6250}
WORKERS=${AD4_WORKERS:-7}

# packs in
cp "$PACK" "$W/ad4_pack.tar"
[ "$(sha256sum "$W/ad4_pack.tar" | cut -c1-64)" = "$PACK_SHA" ] || die "ad4_pack.tar sha256 differs from $PACK_SHA"
tar -C "$W" -xf "$W/ad4_pack.tar" && rm -f "$W/ad4_pack.tar"
(cd "$W/ad4" && sha256sum -c --quiet SHA256SUMS) || die "pack content off its SHA256SUMS"
echo "AD4 pack ok ($((SECONDS - T0)) s)"
if [ "${AD4_LOCAL:-0}" != 1 ]; then
  for n in pylib pylib_a12; do
    cp "$LIBP/$n.tar" "$W/$n.tar"
    [ "$(sha256sum "$W/$n.tar" | cut -c1-64)" = "$(awk 'NR==1{print $1}' "$LIBP/$n.tar.sha256")" ] || die "$n.tar sha256"
    tar -C "$W" -xf "$W/$n.tar" && rm -f "$W/$n.tar"
  done
  echo "AD4 library packs ok ($((SECONDS - T0)) s)"
fi

# data root: the pack's data with manifests/train.csv = this arm's manifest
D=$W/data
mkdir -p "$D/manifests"
ln -s "$W/ad4/data/train" "$D/train"
ln -s "$W/ad4/data/eval" "$D/eval"
for f in "$W"/ad4/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
ln -s "$W/ad4/data/manifests/$MAN" "$D/manifests/train.csv"
echo "AD4 train.csv = $MAN sha256 $(sha256sum "$D/manifests/train.csv" | cut -c1-64)"

ENVS=(SMAD_DATA=$D HF_HOME=$W/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1)
py() {
  if [ "${AD4_LOCAL:-0}" = 1 ]; then
    env "${ENVS[@]}" "${AD4_PY:?AD4_PY}" "$@"
  else
    local e; e=$(IFS=,; echo "PYTHONPATH=$W/pylib_a12:$W/pylib:$W/ad4/code,${ENVS[*]}")
    apptainer exec --nv -B /lustre -B "$W" ${TMPDIR:+-B "$TMPDIR"} --env "$e" "$SIF" python "$@"
  fi
}
nvidia-smi -L || true
py -c "import torch, timm, sys; print('AD4 env', sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.is_available())"

RUN=$W/runs/AD4/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_ad4${ARM}
py "$W/ad4/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none --lr 3.33e-06 \
  --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 "${BSX[@]}" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
echo "AD4 trained ($((SECONDS - T0)) s)"

R=$W/res/$TASK
mkdir -p "$R"
py "$W/ad4/src/ad4_score.py" --run "$RUN" --code "$W/ad4/code" --eval-manifest ad4_eval.csv \
  --train-manifest train.csv --true-manifest train_i3.csv --out "$R" --workers "$WORKERS" --limit "${AD4_LIMIT:-0}"
cp "$RUN/meta.json" "$W/train.log" "$TASK_DIR/task.env" "$R/"
[ -f "$RUN/snapval/val10.json" ] && cp "$RUN/snapval/val10.json" "$R/" || true
echo "pack_sha256 $PACK_SHA wall_s $((SECONDS - T0)) host $(hostname) local ${AD4_LOCAL:-0} steps $STEPS limit ${AD4_LIMIT:-0}" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
[ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
echo "AD4_TASK_DONE $OUT/$TASK.tar $(cut -c1-64 "$W/$TASK.tar.sha256") wall $((SECONDS - T0)) s"
