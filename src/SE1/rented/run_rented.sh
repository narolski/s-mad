#!/bin/bash
# SE1 RENTED VARIANT (deviation SE1-D1): identical to src/SE1/run.sh (b2a975f1) except the base pack. The base is the MS1 pack
# already on the rented L40S hosts (pn1_pack_ms1.tar, c11b16bc..., read in place, never copied), which holds every FS1 file
# byte-identical except train_A.csv/train_B.csv/pn1_eval.csv; se1_fs1sup.tar adds FS1's train_A.csv and FS1SUMS (FS1's
# SHA256SUMS without pn1_eval.csv and train_B.csv), and FS1SUMS is checked, so the tree holds every FS1 file the arms use.
# Original header:
# Seam-shortcut training arm (SE1) task: one network = one task. Copy of src/BB2/run.sh (itself a copy of src/PN1/run.sh
# 6a23a7a4) with these changes, all marked SE1: the CLIP ViT-B/16 MADation arch of the FS1 pack (unchanged
# archs_a12.py, no architecture overlay); the SE1 overlay (train_SE.csv, se_eval.csv, their images, SE1SUMS) unpacked
# over the unchanged FS1 pack after both are hash-checked; arms A|Sb|SE; seeds 408-412; scoring on se_eval.csv;
# results to $G/results/SE1. train.py, its flags and pn1_score.py are unchanged (FS1 recipe, batch 256, 6,250 steps).
# Reads $TASK_DIR/task.env (TASK ARM SEED). IO: pack tars in (sha256-checked), all work in $TASK_WORK (local disk), one
# tar out. Test knobs: PN1_STEPS, PN1_LIMIT, PN1_WORKERS, SE1_RESULTS.
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
source "$TASK_DIR/task.env"
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
G=${PN1_ROOT:-/lustre/pd03/hpc-narolski-1790461090/smad-next}
PACK=${PN1_PACK:?PN1_PACK}                                                                # SE1-D1: the MS1 pack
PACK_SHA=c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d                 # SE1-D1: MS1 pack pin
SUP=${SE1_SUP:?SE1_SUP}; SUP_SHA=76ff67c4a1afca25958919080b35cf3e113f666f9ef87d10913e81aa8ba431a3     # SE1-D1
OVERLAY=${SE1_OVERLAY:-$G/packs/SE1/se1_overlay.tar}                                   # SE1
OVERLAY_SHA=${SE1_OVERLAY_SHA:?SE1_OVERLAY_SHA}                                         # SE1: given by the job file
ARCH=a12_clip_vitb16_madation                                                           # SE1: the FS1 arch
OUT=${SE1_RESULTS:-$G/results/SE1}
W=$(cd -P "$TASK_WORK" && pwd)
py() {                                                                                  # SE1: host python (WCSS) or the
  if [ -n "${PN1_SIF:-}" ]; then apptainer exec --nv -B "$G:$G" -B "$W:$W" "$PN1_SIF" python "$@"   # project container (Athena)
  else "${PN1_PY:?PN1_PY}" "$@"; fi
}
die() { echo "PN1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "SE1 task $TASK arm $ARM seed $SEED host $(hostname) work $W $(date +%FT%T)"
case "$W" in /lustre*|/net/pr2*|/net/tscratch*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") \
    && { echo "SE1 already done: $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
fi
case "$ARM" in A|Sb|SE) MAN=train_$ARM.csv ;; *) die "arm $ARM" ;; esac                # SE1
case "$SEED" in 408|409|410|411|412) ;; *) die "seed $SEED" ;; esac                     # SE1
STEPS=${PN1_STEPS:-6250}
WORKERS=${PN1_WORKERS:-7}

[ "$(sha256sum "$PACK" | cut -c1-64)" = "$PACK_SHA" ] || die "base pack sha256 differs from $PACK_SHA"      # SE1-D1
tar -C "$W" -xf "$PACK"                                                                                  # SE1-D1: in place
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "base pack content off its SHA256SUMS"
[ "$(sha256sum "$SUP" | cut -c1-64)" = "$SUP_SHA" ] || die "se1_fs1sup.tar sha256 differs"              # SE1-D1
tar -C "$W" --skip-old-files -xf "$SUP"
(cd "$W/pn1" && sha256sum -c --quiet FS1SUMS) || die "tree differs from the FS1 pack (FS1SUMS)"
echo "PN1 pack ok ($((SECONDS - T0)) s)"
cp "$OVERLAY" "$W/se1_overlay.tar"                                                      # SE1
[ "$(sha256sum "$W/se1_overlay.tar" | cut -c1-64)" = "$OVERLAY_SHA" ] || die "se1_overlay.tar sha256 differs from $OVERLAY_SHA"
tar -C "$W" --skip-old-files -xf "$W/se1_overlay.tar" && rm -f "$W/se1_overlay.tar"     # SE1: adds files, replaces none
(cd "$W/pn1" && sha256sum -c --quiet SE1SUMS) || die "overlay content off its SE1SUMS"
(cd "$W/pn1" && sha256sum -c --quiet FS1SUMS) || die "FS1 files changed by the overlay"
echo "SE1 overlay ok $OVERLAY_SHA ($((SECONDS - T0)) s)"

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

RUN=$W/runs/SE1/${ARCH}_r224_d0_train90_none_lr3.33e-06_s${SEED}_se1${ARM}
py "$W/pn1/code/smadcvpr/train.py" --arch "$ARCH" --regime d0 --split train90 --lofo none \
  --lr 3.33e-06 --seed "$SEED" --res 224 --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
echo "PN1 trained ($((SECONDS - T0)) s)"

R=$W/res/$TASK
mkdir -p "$R"
py "$W/pn1/src/pn1_score.py" --run "$RUN" --code "$W/pn1/code" --eval-manifest se_eval.csv \
  --train-manifest train.csv --out "$R" --workers "$WORKERS" --limit "${PN1_LIMIT:-0}"
cp "$RUN/meta.json" "$W/train.log" "$TASK_DIR/task.env" "$R/"
py -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'tf32', torch.backends.cuda.matmul.allow_tf32)" > "$R/env.txt" 2>&1 || true
echo "base MS1 sup $SUP_SHA pack_sha256 $PACK_SHA overlay_sha256 $OVERLAY_SHA arch $ARCH wall_s $((SECONDS - T0)) host $(hostname) steps $STEPS limit ${PN1_LIMIT:-0}" > "$R/task_info.txt"
{ echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"; nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader; } > "$R/gpu.txt" 2>&1 || true
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
[ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
echo "PN1_TASK_DONE $OUT/$TASK.tar $(cut -c1-64 "$W/$TASK.tar.sha256") wall $((SECONDS - T0)) s"
