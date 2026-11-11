#!/bin/bash
# PN1 tier-1 task (Athena): one network = one task. Trains one ViT-B/16 row with the UNCHANGED train.py of the AD4 pack
# (the morph-free networks recipe M3, flag for flag as src/AD4/run.sh), manifest A, B or C, last checkpoint; scores it
# on the PN1 evaluation manifest and on its own training rows; writes ONE result tar plus .sha256 to $OUT.
# Reads $TASK_DIR/task.env (TASK ARM SEED). IO: one pack tar in (sha256-checked), all work in $TASK_WORK (RAM disk),
# one tar out. Python runs inside the project's container image (ATHENA.md "Container image"; sha256 fedeff10...).
# Test knobs: PN1_ROOT (results root), PN1_STEPS, PN1_LIMIT, PN1_WORKERS, PN1_PACK, PN1_SIF;
# PN1_LOCAL=1 + PN1_PY = host python instead of the container (DGX test only).
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
source "$TASK_DIR/task.env"
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
G=${PN1_ROOT:-/net/pr2/projects/plgrid/plggrestoration/smad-next}
PACK=${PN1_PACK:-$G/packs/PN1/pn1_pack.tar}
PACK_SHA=$(cut -c1-64 "$PACK.sha256")
OUT=$G/results/PN1
SIF=${PN1_SIF:-$G/containers/smad_torch221_cu121_v1.sif}
W=$(cd -P "$TASK_WORK" && pwd)
py() {
  if [ "${PN1_LOCAL:-0}" = 1 ]; then "${PN1_PY:?PN1_PY}" "$@"
  else apptainer exec --nv -B "$G:$G" -B "$W:$W" ${MEMFS:+-B "$MEMFS:$MEMFS"} "$SIF" python "$@"; fi
}
die() { echo "PN1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "PN1 task $TASK arm $ARM seed $SEED host $(hostname) work $W $(date +%FT%T)"
case "$W" in /net/pr2*|/net/tscratch*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") \
    && { echo "PN1 already done: $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
fi
case "$ARM" in A|B|C) MAN=train_$ARM.csv ;; *) die "arm $ARM" ;; esac
case "$SEED" in 401|402|403|404|405) ;; *) die "seed $SEED" ;; esac
STEPS=${PN1_STEPS:-6250}
WORKERS=${PN1_WORKERS:-7}

cp "$PACK" "$W/pn1_pack.tar"
[ "$(sha256sum "$W/pn1_pack.tar" | cut -c1-64)" = "$PACK_SHA" ] || die "pn1_pack.tar sha256 differs from $PACK_SHA"
tar -C "$W" -xf "$W/pn1_pack.tar" && rm -f "$W/pn1_pack.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "pack content off its SHA256SUMS"
echo "PN1 pack ok ($((SECONDS - T0)) s)"

D=$W/data
mkdir -p "$D/manifests"
ln -s "$W/pn1/data/train" "$D/train"
ln -s "$W/pn1/data/eval" "$D/eval"
for f in "$W"/pn1/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
ln -s "$W/pn1/data/manifests/$MAN" "$D/manifests/train.csv"
echo "PN1 train.csv = $MAN sha256 $(sha256sum "$D/manifests/train.csv" | cut -c1-64)"
export SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
nvidia-smi -L || true
py -c "import torch, timm, sys; print('PN1 env', sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.is_available())"

RUN=$W/runs/PN1/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s${SEED}_pn1${ARM}
py "$W/pn1/code/smadcvpr/train.py" --arch a12_clip_vitb16_madation --regime d0 --split train90 --lofo none \
  --lr 3.33e-06 --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
echo "PN1 trained ($((SECONDS - T0)) s)"

R=$W/res/$TASK
mkdir -p "$R"
py "$W/pn1/src/pn1_score.py" --run "$RUN" --code "$W/pn1/code" --eval-manifest pn1_eval.csv \
  --train-manifest train.csv --out "$R" --workers "$WORKERS" --limit "${PN1_LIMIT:-0}"
cp "$RUN/meta.json" "$W/train.log" "$TASK_DIR/task.env" "$R/"
echo "sif $SIF local ${PN1_LOCAL:-0} pack_sha256 $PACK_SHA wall_s $((SECONDS - T0)) host $(hostname) steps $STEPS limit ${PN1_LIMIT:-0}" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
[ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
echo "PN1_TASK_DONE $OUT/$TASK.tar $(cut -c1-64 "$W/$TASK.tar.sha256") wall $((SECONDS - T0)) s"
