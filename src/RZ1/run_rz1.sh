#!/bin/bash
# Input resolution and resize method (RZ1): one network = one task. Copy of src/AB1/run.sh v2 (cfa4ed26; the proven WCSS
# H100 path of AB1 6310270) with these changes, all marked RZ1:
#  - inputs: the FS1 pack + AB1 overlay v2 + AB1 border overlay (ab1x, gives ab1x_eval.csv) unpacked as in AB1; the TT1
#    pack (unseen genuine sources, border and geometry references) and the TT1-M MEDS pack unpacked beside it and linked
#    into the data root; the RZ1 overlay (code, rz1_cross.csv); every tar sha256-pinned here, every tree checked
#    against its own SUMS file;
#  - training through src/RZ1/rz1_train.py (unchanged pack train.py, input transform of rz1_kernels.py) with the arm's
#    transform, resolution, batch and accumulation; FS1 recipe flags otherwise unchanged;
#  - first-step guard rz1_guard.py pre (tokens, position embedding, item shape) and post (meta res/bs/accum/steps);
#  - scoring by src/RZ1/rz1_score.py inside the job (primary transform on ab1x_eval, training rows, TT1, MEDS; the
#    cross table under every kernel for the resize arms); results to $G/results/RZ1.
# Reads $TASK_DIR/task.env (TASK ARM SEED). Test knobs: PN1_STEPS, PN1_LIMIT, PN1_WORKERS, RZ1_RESULTS, RZ1_SKIP_TT1.
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
source "$TASK_DIR/task.env"
: "${TASK:?}" "${ARM:?}" "${SEED:?}"
G=${PN1_ROOT:-/lustre/pd03/hpc-narolski-1790461090/smad-next}
PACK=${PN1_PACK:-$G/packs/BB2/pn1_pack_fs.tar};         PACK_SHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
OV1=${AB1_OVERLAY:-$G/packs/AB1/ab1_overlay_v2.tar};    OV1_SHA=171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149
OVX=${AB1X_OVERLAY:-$G/packs/AB1/ab1x_overlay.tar};     OVX_SHA=e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c
TT1P=${TT1_PACK:-$G/packs/TT1/tt1_pack.tar};            TT1_SHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
MEDSP=${MEDS_PACK:-$G/packs/RZ1/tt1m_meds.tar};         MEDS_SHA=3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61
OVR=${RZ1_OVERLAY:-$G/packs/RZ1/rz1_overlay.tar};       OVR_SHA=dccf37d20ca0074780a15d99012c3302f52e4ad5a7773b66981b5d316276d383
ARCH=a12_clip_vitb16_madation
OUT=${RZ1_RESULTS:-$G/results/RZ1}
W=$(cd -P "$TASK_WORK" && pwd)
py() { "${PN1_PY:?PN1_PY}" "$@"; }
die() { echo "RZ1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "RZ1 task $TASK arm $ARM seed $SEED host $(hostname) work $W $(date +%FT%T)"
case "$W" in /lustre*|/net/pr2*|/net/tscratch*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
if [ -e "$OUT/$TASK.tar" ]; then
  [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256") \
    && { echo "RZ1 already done: $OUT/$TASK.tar"; exit 0; }
  die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
fi
STEPS=${PN1_STEPS:-6250}
K9=fixed:pil_bilinear,fixed:pil_nearest,fixed:pil_bicubic,fixed:pil_lanczos,fixed:pil_box,fixed:cv_area,fixed:cv_linear,fixed:cv_cubic,fixed:cv_lanczos4,fixed:pil_hamming,fixed:cv_nearest,fixed:cv_linear_exact,two:300:pil_hamming:cv_linear_exact   # RZ1: 9 training kernels + 4 held-out test transforms (review M2)
RES=224; BS=256; ACC=1; RES512=0; CROSS=$K9; PRIM=fixed:pil_bilinear                # RZ1: arm table (prereg section 2)
case "$ARM" in
  A0)     MAN=train_A.csv;  SPEC=fixed:pil_bilinear ;;
  Sb0)    MAN=train_Sb.csv; SPEC=fixed:pil_bilinear ;;
  AN)     MAN=train_A.csv;  SPEC=fixed:pil_nearest; PRIM=fixed:pil_nearest ;;
  AM)     MAN=train_A.csv;  SPEC=mix ;;
  SbM)    MAN=train_Sb.csv; SPEC=mix ;;
  AMR)    MAN=train_A.csv;  SPEC=mixR ;;
  SbMR)   MAN=train_Sb.csv; SPEC=mixR ;;
  Ac)     MAN=train_A.csv;  SPEC=crop:144:160; PRIM=$SPEC; CROSS="" ;;
  Sbc)    MAN=train_Sb.csv; SPEC=crop:144:160; PRIM=$SPEC; CROSS="" ;;
  A512)   MAN=train_A.csv;  SPEC=fixed:pil_bilinear; RES=512; BS=64; ACC=4; RES512=1; CROSS="" ;;
  Sb512)  MAN=train_Sb.csv; SPEC=fixed:pil_bilinear; RES=512; BS=64; ACC=4; RES512=1; CROSS="" ;;
  SbMR512) MAN=train_Sb.csv; SPEC=mixR; RES=512; BS=64; ACC=4; RES512=1; CROSS="" ;;
  *) die "arm $ARM" ;; esac
case "$SEED" in 408|409|410|411|412) ;; *) die "seed $SEED" ;; esac
WORKERS=${PN1_WORKERS:-7}

fetch() {   # tar sha dest: copy one tar to local disk, check its pin, unpack, remove the copy
  cp "$1" "$W/in.tar"
  [ "$(sha256sum "$W/in.tar" | cut -c1-64)" = "$2" ] || die "$(basename "$1") sha256 differs from $2"
  tar -C "$3" ${4:-} -xf "$W/in.tar" && rm -f "$W/in.tar"
}
fetch "$PACK" "$PACK_SHA" "$W"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "pack content off its SHA256SUMS"
fetch "$OV1" "$OV1_SHA" "$W" --skip-old-files
(cd "$W/pn1" && sha256sum -c --quiet AB1SUMS) || die "AB1 overlay content off its AB1SUMS"
fetch "$OVX" "$OVX_SHA" "$W" --skip-old-files
(cd "$W/pn1" && sha256sum -c --quiet AB1XSUMS) || die "AB1X overlay content off its AB1XSUMS"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "FS1 files changed by the overlays"
echo "RZ1 FS1 pack + AB1 overlays ok ($((SECONDS - T0)) s)"
if [ -z "${RZ1_SKIP_TT1:-}" ]; then
  fetch "$TT1P" "$TT1_SHA" "$W"
  (cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || die "TT1 pack off its SHA256SUMS"
  fetch "$MEDSP" "$MEDS_SHA" "$W"
  (cd "$W/tt1m" && sha256sum -c --quiet SHA256SUMS) || die "MEDS pack off its SHA256SUMS"
fi
fetch "$OVR" "$OVR_SHA" "$W"
(cd "$W/rz1" && sha256sum -c --quiet RZ1SUMS) || die "RZ1 overlay off its RZ1SUMS"
echo "RZ1 inputs ok ($((SECONDS - T0)) s)"

D=$W/data
mkdir -p "$D/manifests" "$D/eval"
ln -s "$W/pn1/data/train" "$D/train"
for e in "$W"/pn1/data/eval/*; do ln -s "$e" "$D/eval/$(basename "$e")"; done              # RZ1: eval root built of links
if [ -z "${RZ1_SKIP_TT1:-}" ]; then
  for e in "$W"/tt1/data/eval/* "$W"/tt1m/data/eval/*; do
    [ -e "$D/eval/$(basename "$e")" ] && die "eval folder collision $(basename "$e")"
    ln -s "$e" "$D/eval/$(basename "$e")"
  done
  ln -s "$W/tt1/data/manifests/tt1_score.csv" "$D/manifests/tt1_score.csv"
  ln -s "$W/tt1m/data/manifests/meds_score.csv" "$D/manifests/meds_score.csv"
fi
for f in "$W"/pn1/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
ln -s "$W/rz1/manifests/rz1_cross.csv" "$D/manifests/rz1_cross.csv"
ln -s "$W/pn1/data/manifests/$MAN" "$D/manifests/train.csv"
echo "RZ1 train.csv = $MAN sha256 $(sha256sum "$D/manifests/train.csv" | cut -c1-64) spec $SPEC res $RES bs $BS accum $ACC primary $PRIM"
export SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 RZ1_TRANSFORM=$SPEC RZ1_RES512=$RES512
nvidia-smi -L || true
py -c "import torch, timm, sys, cv2, PIL; print('RZ1 env', sys.version.split()[0], torch.__version__, timm.__version__, cv2.__version__, PIL.__version__, torch.cuda.is_available())"
py "$W/rz1/src/rz1_guard.py" pre "$W/pn1/code" "$ARCH" "$RES" "$SPEC" train.csv 2>&1 | tee "$W/guard.log"   # RZ1: pipefail stops on failure

RUN=$W/runs/RZ1/${ARCH}_r${RES}_d0_train90_none_lr3.33e-06_s${SEED}_rz1${ARM}
py "$W/rz1/src/rz1_train.py" "$W/pn1/code" --arch "$ARCH" --regime d0 --split train90 --lofo none \
  --lr 3.33e-06 --seed "$SEED" --res "$RES" --workers "$WORKERS" --out "$RUN" \
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps="$STEPS" --ft=lora \
  --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw \
  --wd=0.05 --head-lr=3.33e-05 --bs="$BS" --accum="$ACC" --aug=flip --sched=const --clip-grad=5 --pos-weight=1 2>&1 | tee "$W/train.log"
[ -f "$RUN/last.pt" ] && [ -f "$RUN/meta.json" ] || die "train.py returned without last.pt / meta.json"
py "$W/rz1/src/rz1_guard.py" post "$RUN" "$RES" "$BS" "$ACC" "$STEPS" "$SPEC" 2>&1 | tee -a "$W/guard.log"
echo "RZ1 trained ($((SECONDS - T0)) s)"

R=$W/res/$TASK
mkdir -p "$R"
if [ -n "${RZ1_SKIP_TT1:-}" ]; then XS="--tt1-manifest ab1x_eval.csv --meds-manifest ab1x_eval.csv"; CROSS=""; else XS=""; fi   # test knob: no TT1 rows, so no cross table
py "$W/rz1/src/rz1_score.py" --run "$RUN" --code "$W/pn1/code" --primary "$PRIM" --cross "$CROSS" --out "$R" \
  --workers "$WORKERS" --limit "${PN1_LIMIT:-0}" $XS
cp "$RUN/meta.json" "$RUN/rz1_transform.json" "$W/train.log" "$W/guard.log" "$TASK_DIR/task.env" "$R/"
py -c "import sys, torch, timm, numpy, PIL, cv2; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'cv2', cv2.__version__, 'tf32', torch.backends.cuda.matmul.allow_tf32)" > "$R/env.txt" 2>&1 || true
echo "pack_sha256 $PACK_SHA ab1_overlay $OV1_SHA ab1x_overlay $OVX_SHA tt1 $TT1_SHA meds $MEDS_SHA rz1_overlay $OVR_SHA arch $ARCH spec $SPEC primary $PRIM res $RES bs $BS accum $ACC wall_s $((SECONDS - T0)) host $(hostname) steps $STEPS limit ${PN1_LIMIT:-0} skip_tt1 ${RZ1_SKIP_TT1:-0}" > "$R/task_info.txt"
{ echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"; nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader; } > "$R/gpu.txt" 2>&1 || true
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
(cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
[ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"
cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
echo "RZ1_TASK_DONE $OUT/$TASK.tar $(cut -c1-64 "$W/$TASK.tar.sha256") wall $((SECONDS - T0)) s"
