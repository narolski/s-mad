#!/bin/bash
# RZ1 amendment 1: rescoring job for AB1's kept A and Sb networks at seeds 408-412 (one job, ten networks, sequential),
# on the RZ1 inputs and data root of run_rz1.sh (input section copied unchanged), with src/RZ1/rz1_rescore.py (bit-identity
# gate against AB1's stored logits, then rz1_score.py with the 13-spec cross table). Results: $G/results/RZ1R/RZ1R_<arm>_s<seed>.tar.
# The header below is run_rz1.sh's: one network = one task. Copy of src/AB1/run.sh v2 (cfa4ed26; the proven WCSS
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
: "${TASK_WORK:?}"
G=${PN1_ROOT:-/lustre/pd03/hpc-narolski-1790461090/smad-next}
PACK=${PN1_PACK:-$G/packs/BB2/pn1_pack_fs.tar};         PACK_SHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
OV1=${AB1_OVERLAY:-$G/packs/AB1/ab1_overlay_v2.tar};    OV1_SHA=171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149
OVX=${AB1X_OVERLAY:-$G/packs/AB1/ab1x_overlay.tar};     OVX_SHA=e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c
TT1P=${TT1_PACK:-$G/packs/TT1/tt1_pack.tar};            TT1_SHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
MEDSP=${MEDS_PACK:-$G/packs/RZ1/tt1m_meds.tar};         MEDS_SHA=3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61
OVR=${RZ1_OVERLAY:-$G/packs/RZ1/rz1_overlay.tar};       OVR_SHA=dccf37d20ca0074780a15d99012c3302f52e4ad5a7773b66981b5d316276d383
ARCH=a12_clip_vitb16_madation
OUT=${RZ1R_RESULTS:-$G/results/RZ1R}
W=$(cd -P "$TASK_WORK" && pwd)
py() { "${PN1_PY:?PN1_PY}" "$@"; }
die() { echo "RZ1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "RZ1R rescoring host $(hostname) work $W $(date +%FT%T)"
case "$W" in /lustre*|/net/pr2*|/net/tscratch*) die "TASK_WORK is on Lustre" ;; esac
mkdir -p "$OUT"
WORKERS=${PN1_WORKERS:-7}
RS=${RZ1R_SCRIPT:-$G/packs/RZ1/rz1_rescore.py}; RS_SHA=f9eaa7d2f3c3c2731af4db5e9b16350a31139ed8294f3bf9ce9fa87ad10821ee
AB=${AB1_RESULTS:-$G/results/AB1}
declare -A PIN=(
 [AB1_A_s408]=bb1a0e9c4fd49c322839ea552994836066668246cef7b3749729ef725cba30e2 [AB1_A_s409]=d9a8c1b8ceb78f735e37fdf14b69eb0a957d8233d6523285fe9517d85c211f0d
 [AB1_A_s410]=78ef2e47b1c1feec3cb5bb59ed9c22206126d249bc6a47be4194d57845905b56 [AB1_A_s411]=fd71be56dd4858b9d03ec94a74c9d4c5546fc0c22d8c66ef6e57e2b1ba9d293a
 [AB1_A_s412]=c0496a0f219e747f9d606b69c0392dec7f20edebce23fae2b1286068fac510a3 [AB1_Sb_s408]=a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa
 [AB1_Sb_s409]=dd575673e437b2ad34aa50e9f2785ee2c17a1b89b424b2324b4beb6ae5f32352 [AB1_Sb_s410]=40b47155a7a1ca1a13bc9ae101b135b3d0730d70d968af6e7ad235453ca96875
 [AB1_Sb_s411]=764a4e5e6a5692cb974a15957cf55ac88d475a519381d8ef827f932791144aa6 [AB1_Sb_s412]=c1e0f081194ffb46395e896bd872f509a930967b8ed5da101823d95659070c84)
NETS=${RZ1R_NETS:-"AB1_A_s408 AB1_Sb_s408 AB1_A_s409 AB1_Sb_s409 AB1_A_s410 AB1_Sb_s410 AB1_A_s411 AB1_Sb_s411 AB1_A_s412 AB1_Sb_s412"}
K9=fixed:pil_bilinear,fixed:pil_nearest,fixed:pil_bicubic,fixed:pil_lanczos,fixed:pil_box,fixed:cv_area,fixed:cv_linear,fixed:cv_cubic,fixed:cv_lanczos4,fixed:pil_hamming,fixed:cv_nearest,fixed:cv_linear_exact,two:300:pil_hamming:cv_linear_exact
cp "$RS" "$W/rz1_rescore.py"
[ "$(sha256sum "$W/rz1_rescore.py" | cut -c1-64)" = "$RS_SHA" ] || die "rz1_rescore.py sha256 differs from $RS_SHA"
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
echo "RZ1R inputs ok ($((SECONDS - T0)) s)"
export SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 RZ1_TRANSFORM=fixed:pil_bilinear RZ1_RES512=0
nvidia-smi -L || true
for N in $NETS; do
  TASK=RZ1R_${N#AB1_}
  if [ -e "$OUT/$TASK.tar" ] && [ -f "$OUT/$TASK.tar.sha256" ] && (cd "$OUT" && sha256sum -c --quiet "$TASK.tar.sha256"); then
    echo "RZ1R already done: $TASK"; continue; fi
  [ -e "$OUT/$TASK.tar" ] && die "$OUT/$TASK.tar exists without a matching .sha256 (never overwritten)"
  cp "$AB/$N.tar" "$W/$N.tar"
  [ "$(sha256sum "$W/$N.tar" | cut -c1-64)" = "${PIN[$N]}" ] || die "$N.tar sha256 differs from its pin"
  case "$N" in AB1_A_*) MAN=train_A.csv ;; AB1_Sb_*) MAN=train_Sb.csv ;; *) die "net $N" ;; esac
  ln -sfn "$W/pn1/data/manifests/$MAN" "$D/manifests/train.csv"
  R=$W/res/$TASK; mkdir -p "$R"
  py "$W/rz1_rescore.py" --tar "$W/$N.tar" --code "$W/pn1/code" --rz1 "$W/rz1/src" --out "$R" --cross "$K9" \
     --workers "$WORKERS" --limit "${PN1_LIMIT:-0}" 2>&1 | tee "$R/rescore.log"
  grep -q "RZ1R_NET_DONE" "$R/rescore.log" || die "$N rescoring did not finish"
  py -c "import sys, torch, timm, numpy, PIL, cv2; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'cv2', cv2.__version__)" > "$R/env.txt" 2>&1 || true
  echo "source_tar $N.tar ${PIN[$N]} pack_sha256 $PACK_SHA ab1_overlay $OV1_SHA ab1x_overlay $OVX_SHA tt1 $TT1_SHA meds $MEDS_SHA rz1_overlay $OVR_SHA rz1_rescore $RS_SHA train_manifest $MAN host $(hostname) limit ${PN1_LIMIT:-0}" > "$R/task_info.txt"
  { echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"; nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader; } > "$R/gpu.txt" 2>&1 || true
  tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
  cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
  (cd "$W" && sha256sum "$TASK.tar") > "$W/$TASK.tar.sha256"
  [ "$(sha256sum "$OUT/$TASK.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TASK.tar.sha256")" ] || die "copy-back sha256"
  mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar"; cp "$W/$TASK.tar.sha256" "$OUT/$TASK.tar.sha256"
  rm -rf "$W/$N.tar" "$R"
  echo "RZ1R_TASK_DONE $TASK $(cut -c1-64 "$W/$TASK.tar.sha256") $(date +%FT%T)"
done
echo "RZ1R_ALL_DONE $(date -Is)"
