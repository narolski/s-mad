#!/bin/bash
# Protocol ablation and replication (AB1) task: one network = one task. Copy of src/SE1/run.sh (b2a975f1; itself a copy of
# src/BB2/run.sh and src/PN1/run.sh 6a23a7a4) with these changes, all marked AB1: the AB1 overlay (train_SbZ, SbH, SbS,
# AS, Sp manifests made from FS1 manifests by dropping row kinds; ab1_eval.csv = FS1 pn1_eval.csv rows + the 1,480 MS1
# FFHQ hold-out rows and their images; AB1SUMS) unpacked over the unchanged FS1 pack after both are hash-checked; arms
# B|SbZ|SbH|SbS|AS|Sp (A|Sb only as the registered fallback; SbL = train_Sb.csv at 12,500 steps, conditional); seeds 408-412; scoring on ab1_eval.csv; results to
# $G/results/AB1. train.py, its flags and pn1_score.py are unchanged (FS1 recipe, CLIP ViT-B/16 LoRA, batch 256, 6,250 steps).
# Reads $TASK_DIR/task.env (TASK ARM SEED). IO: pack tars in (sha256-checked), all work in $TASK_WORK (local disk), one
# tar out. Test knobs: PN1_STEPS, PN1_LIMIT, PN1_WORKERS, AB1_RESULTS.
# v2 (13 Nov, pre-run review F2): overlay ab1_overlay_v2.tar (SbH keeps af0_half61). v1 (893e856a, overlay 4e3afaa1) ran the smoke only.
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
source "$TASK_DIR/task.env"
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
G=${PN1_ROOT:-/lustre/pd03/hpc-narolski-1790461090/smad-next}
PACK=${PN1_PACK:-$G/packs/BB2/pn1_pack_fs.tar}
PACK_SHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004                 # pinned, not read from a file
OVERLAY=${AB1_OVERLAY:-$G/packs/AB1/ab1_overlay_v2.tar}                                  # AB1
OVERLAY_SHA=171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149           # AB1: pinned, not read from a file
ARCH=a12_clip_vitb16_madation                                                           # the FS1 arch
OUT=${AB1_RESULTS:-$G/results/AB1}                                                       # AB1
W=$(cd -P "$TASK_WORK" && pwd)
py() {                                                                                  # SE1: host python (WCSS) or the
  if [ -n "${PN1_SIF:-}" ]; then apptainer exec --nv -B "$G:$G" -B "$W:$W" "$PN1_SIF" python "$@"   # project container (Athena)
  else "${PN1_PY:?PN1_PY}" "$@"; fi
}
die() { echo "PN1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "AB1 task $TASK arm $ARM seed $SEED host $(hostname) work $W $(date +%FT%T)"
case "$W" in /lustre*|/net/pr2*|/net/tscratch*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") \
    && { echo "AB1 already done: $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
fi
STEPS=${PN1_STEPS:-6250}
case "$ARM" in B|SbZ|SbH|SbS|AS|Sp|A|Sb) MAN=train_$ARM.csv ;;                          # AB1
  SbL) MAN=train_Sb.csv; [ -n "${PN1_STEPS:-}" ] || STEPS=12500 ;;                      # AB1: conditional arm, Sb twice as long
  *) die "arm $ARM" ;; esac
case "$SEED" in 408|409|410|411|412) ;; *) die "seed $SEED" ;; esac                     # AB1
WORKERS=${PN1_WORKERS:-7}

cp "$PACK" "$W/pn1_pack.tar"
[ "$(sha256sum "$W/pn1_pack.tar" | cut -c1-64)" = "$PACK_SHA" ] || die "pn1_pack.tar sha256 differs from $PACK_SHA"
tar -C "$W" -xf "$W/pn1_pack.tar" && rm -f "$W/pn1_pack.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "pack content off its SHA256SUMS"
echo "PN1 pack ok ($((SECONDS - T0)) s)"
cp "$OVERLAY" "$W/ab1_overlay.tar"                                                      # AB1
[ "$(sha256sum "$W/ab1_overlay.tar" | cut -c1-64)" = "$OVERLAY_SHA" ] || die "ab1_overlay.tar sha256 differs from $OVERLAY_SHA"
tar -C "$W" --skip-old-files -xf "$W/ab1_overlay.tar" && rm -f "$W/ab1_overlay.tar"     # AB1: adds files, replaces none
(cd "$W/pn1" && sha256sum -c --quiet AB1SUMS) || die "overlay content off its AB1SUMS"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "FS1 files changed by the overlay"
echo "AB1 overlay ok $OVERLAY_SHA ($((SECONDS - T0)) s)"

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

RUN=$W/runs/AB1/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_ab1${ARM}               # AB1
py "$W/pn1/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none \
  --lr 3.33e-06 --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
echo "PN1 trained ($((SECONDS - T0)) s)"

R=$W/res/$TASK
mkdir -p "$R"
py "$W/pn1/src/pn1_score.py" --run "$RUN" --code "$W/pn1/code" --eval-manifest ab1_eval.csv \
  --train-manifest train.csv --out "$R" --workers "$WORKERS" --limit "${PN1_LIMIT:-0}"
cp "$RUN/meta.json" "$W/train.log" "$TASK_DIR/task.env" "$R/"
py -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'tf32', torch.backends.cuda.matmul.allow_tf32)" > "$R/env.txt" 2>&1 || true
echo "pack_sha256 $PACK_SHA overlay_sha256 $OVERLAY_SHA arch $ARCH wall_s $((SECONDS - T0)) host $(hostname) steps $STEPS limit ${PN1_LIMIT:-0}" > "$R/task_info.txt"
{ echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"; nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader; } > "$R/gpu.txt" 2>&1 || true
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
[ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
echo "PN1_TASK_DONE $OUT/$TASK.tar $(cut -c1-64 "$W/$TASK.tar.sha256") wall $((SECONDS - T0)) s"
