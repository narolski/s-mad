#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2l-w2
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --no-requeue
#SBATCH --time=0-04:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2l-w2-%j.out
# BB2 DINOv3 programme, wave 2 (merged rescoring; plan PLAN_DINOV3_PROGRAMME_20261113.md section 8, lead's go 20:00):
# every E3 network (results/BB2L/BB2L_<arm>_s<seed>.tar present with a matching .sha256 when the job starts) is rescored
# with the unchanged src/PN1/rescore.py through src/TT1/rescore_tf32.py (TF32 on, pn1_score.py's numerics) on
#   (0) amendment 7c: the platform gate by bit identity, reproducing the fit job's scorer (src/BB2/bb2_gate.py: the whole
#       fit evaluation manifest in manifest order, batch 64, TF32; pn1_eval.csv of the FS1 pack for BB2/BB2L networks,
#       ab1_eval.csv of the FS1 pack + AB1 overlay v2 for AB1 networks); a network that fails is not scored further
#   (a) the MS1 FFHQ hold-out (fam ms1ffhq)      -> C2P, H-new-1
#   (b) the PR1 GAN and diffusion development families (pr1_gd.csv fams gd0, gd1, gd2)  -> PR1 GD reads
#   (c) the TT1 unseen-source pools incl. border and geometry references (tt1_score.csv fam tt1) -> TT1 reads
#   (d) NIST MEDS aligned frontal mugshots (meds_score.csv fam meds; aggregate reads only; no MEDS image or identifier
#       leaves the job except as scores keyed by the pack's own row ids)                -> TT-M1
# Code tree: the MS1 pack's (train.py, common.py identical to FS1's; archs_a12.py asserted at its pin) with the BB2 overlay
# (DINOv3 entry and weights). GPU name asserted and precision logged (precision_probe.py). All IO in $TMPDIR; one tar out:
# $R/$OUTN.tar (+ .sha256). Submitted with --dependency=afterany:<E3 array> (its only later inputs are the E3 tars).
# Overrides (smoke): BB2_W2_TARS (space-separated tar paths), BB2_W2_RESULTS, BB2_W2_OUT, BB2_W2_CMP (comparator names,
# default the five AB1 Sb), BB2_W2_NO_CMP=1. Exits within a minute if a pack
# or script is missing or off its sha256, or if no network tar is present.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2; R=${BB2_W2_RESULTS:-$L/results/BB2L}; OUTN=${BB2_W2_OUT:-BB2LW2}
fail() { echo "BB2L_W2_FAIL $*"; exit 1; }
[ -e "$R/$OUTN.tar" ] && fail "$OUTN.tar exists (never overwritten)"
(cd "$L/packs/MS1" && sha256sum -c pn1_pack_ms1.tar.sha256) && [ "$(cut -c1-64 $L/packs/MS1/pn1_pack_ms1.tar.sha256)" = c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d ] || fail "MS1 pack"
(cd "$L/packs/TT1" && sha256sum -c tt1_pack.tar.sha256) && [ "$(cut -c1-64 $L/packs/TT1/tt1_pack.tar.sha256)" = 2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554 ] || fail "TT1 pack"
(cd "$P" && sha256sum -c bb2_overlay.tar.sha256 pr1_gd.tar.sha256 tt1m_meds.tar.sha256 rescore.py.sha256 rescore_tf32.py.sha256 precision_probe.py.sha256 pn1_pack_fs.tar.sha256 bb2_gate.py.sha256) || fail "BB2 packs or scripts"
[ "$(cut -c1-64 $P/pn1_pack_fs.tar.sha256)" = 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 ] || fail "FS1 pack pin"
[ "$(cut -c1-64 $P/bb2_gate.py.sha256)" = 08d430dc6451b10f66754ad7185a3a96d01ea9788aececd033d17dc92e73f168 ] || fail "bb2_gate.py pin"
(cd "$L/packs/AB1" && sha256sum -c ab1_overlay_v2.tar.sha256) && [ "$(cut -c1-64 $L/packs/AB1/ab1_overlay_v2.tar.sha256)" = 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 ] || fail "AB1 overlay v2"
[ "$(cut -c1-64 $P/bb2_overlay.tar.sha256)" = 7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad ] || fail "overlay pin"
[ "$(cut -c1-64 $P/pr1_gd.tar.sha256)" = 40aa95d2b48719025bc3b80ebf9fa997bb1adf6c69da894120716a6e962b7329 ] || fail "GD pack pin"
[ "$(cut -c1-64 $P/tt1m_meds.tar.sha256)" = 3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61 ] || fail "MEDS pack pin"
[ "$(cut -c1-64 $P/rescore.py.sha256)" = 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e ] || fail "rescore.py pin"
[ "$(cut -c1-64 $P/rescore_tf32.py.sha256)" = 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 ] || fail "wrapper pin"
[ "$(cut -c1-64 $P/precision_probe.py.sha256)" = b49c1e704bc8957db76398abfd5ab54218ee152ac32ed9e061c634378148605e ] || fail "probe pin"
DEF=""; for s in 403 404 405 406 407; do for a in A B Sb; do DEF="$DEF $L/results/BB2L/BB2L_${a}_s$s.tar"; done; done
TARS=""
for t in ${BB2_W2_TARS:-$DEF}; do
  if [ -f "$t" ] && (cd "$(dirname "$t")" && sha256sum -c --quiet "$(basename "$t").sha256" 2>/dev/null); then TARS="$TARS $t"
  else echo "BB2L_W2 skip (absent or off its sha256): $t"; fi
done
[ -n "$TARS" ] || fail "no network tar present"
# amendment 7a (lead 18:58): the CLIP comparator, AB1's H100 Sb networks 408-412, scored in the same job; each is used
# only if its own stored scores on the 6,339 gate rows reproduce bit for bit first (else its other families are skipped)
declare -A CPIN=([AB1_Sb_s408]=a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa [AB1_Sb_s409]=dd575673e437b2ad34aa50e9f2785ee2c17a1b89b424b2324b4beb6ae5f32352 \
  [AB1_Sb_s410]=40b47155a7a1ca1a13bc9ae101b135b3d0730d70d968af6e7ad235453ca96875 [AB1_Sb_s411]=764a4e5e6a5692cb974a15957cf55ac88d475a519381d8ef827f932791144aa6 \
  [AB1_Sb_s412]=c1e0f081194ffb46395e896bd872f509a930967b8ed5da101823d95659070c84)
CTARS=""
if [ "${BB2_W2_NO_CMP:-0}" != 1 ]; then
  for c in ${BB2_W2_CMP:-AB1_Sb_s408 AB1_Sb_s409 AB1_Sb_s410 AB1_Sb_s411 AB1_Sb_s412}; do
    [ -n "${CPIN[$c]:-}" ] || fail "comparator $c not in the pinned list"
    t=$L/results/AB1/$c.tar
    [ -f "$t" ] && [ "$(sha256sum "$t" | cut -c1-64)" = "${CPIN[$c]}" ] && CTARS="$CTARS $t" || fail "comparator $c missing or off its pin"
  done
fi
hostname; date -Is
C=$TMPDIR/c; O=$TMPDIR/out; mkdir -p "$C" "$O" "$C/nets"
cp "$L/packs/MS1/pn1_pack_ms1.tar" "$TMPDIR/p.tar" && tar -C "$C" -xf "$TMPDIR/p.tar" && rm -f "$TMPDIR/p.tar"
(cd "$C/pn1" && sha256sum -c --quiet SHA256SUMS) || fail "MS1 pack content"
[ "$(sha256sum $C/pn1/code/smadcvpr/archs_a12.py | cut -c1-64)" = bedfeb86af2c92aed717e4f43e0b6c466306756d911afc93bcbdd1aae9994876 ] || fail "MS1 archs_a12.py is not the pinned one"
tar -C "$C" -xf "$P/bb2_overlay.tar" && (cd "$C/pn1" && sha256sum -c --quiet BB2SUMS) || fail "overlay content"
# the fit jobs' own tree for the gate: FS1 pack + AB1 overlay v2 (ab1_eval.csv and its images) + BB2 overlay
mkdir -p "$C/fs"
cp "$P/pn1_pack_fs.tar" "$TMPDIR/p.tar" && tar -C "$C/fs" -xf "$TMPDIR/p.tar" && rm -f "$TMPDIR/p.tar"
(cd "$C/fs/pn1" && sha256sum -c --quiet SHA256SUMS) || fail "FS1 pack content"
tar -C "$C/fs" -xf "$L/packs/AB1/ab1_overlay_v2.tar" && (cd "$C/fs/pn1" && sha256sum -c --quiet AB1SUMS) || fail "AB1 overlay content"
tar -C "$C/fs" -xf "$P/bb2_overlay.tar" && (cd "$C/fs/pn1" && sha256sum -c --quiet BB2SUMS) || fail "BB2 overlay content (fs)"
for pk in "$P/pr1_gd.tar:pr1g" "$L/packs/TT1/tt1_pack.tar:tt1" "$P/tt1m_meds.tar:tt1m"; do
  f=${pk%%:*}; top=${pk##*:}
  cp "$f" "$TMPDIR/p.tar" && tar -C "$C" -xf "$TMPDIR/p.tar" && rm -f "$TMPDIR/p.tar"
  (cd "$C/$top" && sha256sum -c --quiet SHA256SUMS) || fail "$top pack content"
done
mk() {  # data root with manifests/ and eval/ of one pack
  local d=$C/data_$1; mkdir -p "$d/manifests"; ln -sfn "$2/eval" "$d/eval"
  for f in "$2"/manifests/*.csv; do ln -sf "$f" "$d/manifests/$(basename "$f")"; done; echo "$d"
}
DMS1=$(mk ms1 "$C/pn1/data"); DGD=$(mk gd "$C/pr1g/data"); DTT=$(mk tt1 "$C/tt1/data"); DMD=$(mk meds "$C/tt1m/data")
DFS=$C/data_fs; mkdir -p "$DFS/manifests"; ln -sfn "$C/fs/pn1/data/eval" "$DFS/eval"; ln -sfn "$C/fs/pn1/data/train" "$DFS/train"
for f in "$C"/fs/pn1/data/manifests/*.csv; do ln -sf "$f" "$DFS/manifests/$(basename "$f")"; done
PY=$HOME/dmenv/bin/python
$PY -I "$P/precision_probe.py" --expect-gpu "NVIDIA H100" > "$O/precision.txt" 2>&1 || fail "GPU or probe: $(tail -1 $O/precision.txt)"
(cd "$P" && sha256sum rescore_tf32.py rescore.py precision_probe.py) > "$O/scripts.sha256"
nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$O/gpu.txt" 2>&1 || true
n_fail=0; n_ref=0; : > "$O/tasks.txt"
for t in $TARS $CTARS; do
  T=$(basename "$t" .tar); echo "$T" >> "$O/tasks.txt"
  tar -C "$C/nets" -xf "$t" "$T/meta.json" "$T/last_trainable.pt"
  case "$T" in AB1_*) GMAN=ab1_eval.csv ;; *) GMAN=pn1_eval.csv ;; esac
  SMAD_DATA=$DFS HF_HOME=$C/fs/pn1/hf HF_HUB_OFFLINE=1 $PY -I "$P/bb2_gate.py" --tar "$t" --code "$C/fs/pn1/code" \
    --manifest "$GMAN" --out "$O" --workers 7 >> "$O/rescore.log" 2>&1
  grc=$?
  rm -rf "$O/_net"     # amendment 7d: no fit-time score or weight file may enter the output tar
  if [ $grc -ne 0 ]; then
    n_ref=$((n_ref+1))
    echo "$(date +%T) $T REFUSED by the bit-identity gate (rc $grc): $(grep BB2GATE "$O/rescore.log" | tail -1 | cut -c1-300)" | tee -a "$O/rescore.log"; continue
  fi
  echo "$(date +%T) $T gate passed (bit-identical on its whole fit manifest)" | tee -a "$O/rescore.log"
  JOBS="$DMS1:pn1_eval.csv:ms1ffhq $DGD:pr1_gd.csv:gd0 $DGD:pr1_gd.csv:gd1 $DGD:pr1_gd.csv:gd2 $DTT:tt1_score.csv:tt1 $DMD:meds_score.csv:meds"
  for job in $JOBS; do
    IFS=: read -r D MAN FAM <<< "$job"
    SMAD_DATA=$D HF_HOME=$C/pn1/hf HF_HUB_OFFLINE=1 $PY "$P/rescore_tf32.py" "$P/rescore.py" --resdir "$C/nets/$T" \
      --code "$C/pn1/code" --manifest "$MAN" --fam "$FAM" --out "$O/W2_${T}_${FAM}.npz" --workers 7 >> "$O/rescore.log" 2>&1 \
      || { echo "$(date +%T) $T $FAM failed" | tee -a "$O/rescore.log"; n_fail=$((n_fail+1)); }
  done
  echo "$(date +%T) $T done" | tee -a "$O/rescore.log"
done
echo "$n_fail" > "$O/n_fail.txt"; echo "$n_ref" > "$O/n_refused.txt"
tar -C "$TMPDIR" -cf "$TMPDIR/$OUTN.tar" out && (cd "$TMPDIR" && sha256sum $OUTN.tar > $OUTN.tar.sha256)
mkdir -p "$R"
cp "$TMPDIR/$OUTN.tar" "$R/$OUTN.tar.part" && [ "$(sha256sum "$R/$OUTN.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$TMPDIR/$OUTN.tar.sha256")" ] \
  && mv "$R/$OUTN.tar.part" "$R/$OUTN.tar" && cp "$TMPDIR/$OUTN.tar.sha256" "$R/" || fail "copy-back"
echo "BB2L_W2_DONE failures $n_fail refused $n_ref $(date -Is)"
[ $n_ref -eq 0 ] && [ $n_fail -eq 0 ] || exit 4     # amendment 7d (review fix a): a refusal or a failed family is not a clean exit
