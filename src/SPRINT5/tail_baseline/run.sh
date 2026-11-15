#!/bin/bash
set -euo pipefail
: "${TMPDIR:?}" "${SLURM_JOB_ID:?}"
G=/lustre/pd03/hpc-narolski-1790461090/smad-next
SP=$G/packs/SPRINT5_3_baseline_v1/source
OUT=$G/results/SPRINT5_3
mkdir -p "$OUT/logs"
TASK=SPRINT5_3_TRAIN_BASELINE_AB1Sb408_v1
exec > >(tee "$OUT/logs/${TASK}_${SLURM_JOB_ID}.log") 2>&1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=$HOME/dmenv/bin/python
W=$TMPDIR/tail_baseline;mkdir -p "$W"
(cd "$SP" && sha256sum -c --quiet SHA256SUMS)
"$PY" "$SP/verify_release.py" "$G/packs/SPRINT5_3_baseline_v1/TRAIN_BASELINE_RELEASE.json" "$SP"
STAGE=source_verified
failure_archive() {
 rc=$?;trap - EXIT;[ "$rc" -eq 0 ] && return
 set +e
 F=$W/failure/$TASK;mkdir -p "$F" "$OUT/failures"
 printf 'exit_status=%s\njob=%s\nstage=%s\n' "$rc" "$SLURM_JOB_ID" "$STAGE" > "$F/status.txt"
 cp "$SP/SHA256SUMS" "$F/"
 [ ! -d "${R:-/nonexistent}" ] || cp -r "$R" "$F/partial_result"
 n=${TASK}_failed_${SLURM_JOB_ID}
 tar -C "$W/failure" -cf "$W/$n.tar" "$TASK"
 cp "$W/$n.tar" "$OUT/failures/$n.tar.part"
 h=$(sha256sum "$W/$n.tar"|cut -c1-64)
 if [ "$(sha256sum "$OUT/failures/$n.tar.part"|cut -c1-64)" = "$h" ];then
  mv "$OUT/failures/$n.tar.part" "$OUT/failures/$n.tar"
  printf '%s  %s.tar\n' "$h" "$n" > "$OUT/failures/$n.tar.sha256"
 fi
 exit "$rc"
}
trap failure_archive EXIT
[ ! -e "$OUT/$TASK.tar" ] || { echo existing-output-needs-reconciliation;exit 1; }
die() { echo "TAIL_BASELINE_FAIL $*";exit 1; }
get() { local t=$1 h=$2 d=$3;cp "$t" "$W/input.tar";[ "$(sha256sum "$W/input.tar"|cut -c1-64)" = "$h" ]||die inputpin;mkdir -p "$d";tar -C "$d" -xf "$W/input.tar";rm "$W/input.tar"; }
STAGE=stage_pinned_inputs
get "$G/packs/BB2/pn1_pack_fs.tar" 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 "$W"
cp "$G/packs/AB1/ab1_overlay_v2.tar" "$W/overlay.tar"
[ "$(sha256sum "$W/overlay.tar"|cut -c1-64)" = 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 ]||die overlaypin
tar -C "$W" --skip-old-files -xf "$W/overlay.tar";rm "$W/overlay.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS && sha256sum -c --quiet AB1SUMS)
get "$G/packs/BATTERY/battery_code_v1rc2.tar" 19bf00aeb0b6b1ade3a5b424087a7d00bf3f6ec13f4bf9a0a63fc84510c736f3 "$W/bcode"
cp "$G/results/AB1/AB1_Sb_s408.tar" "$W/ref.tar"
[ "$(sha256sum "$W/ref.tar"|cut -c1-64)" = a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa ]||die referencepin
mkdir -p "$W/reference";tar -C "$W/reference" -xf "$W/ref.tar" AB1_Sb_s408/meta.json AB1_Sb_s408/last_trainable.pt AB1_Sb_s408/scores_eval.npz
R=$W/res/$TASK;mkdir -p "$R"
export HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 SMAD_DATA=$W/pn1/data
rc=0
STAGE=reference_bytegate
(cd "$W/bcode/src" && "$PY" -m battery.run --ckpt "$W/reference/AB1_Sb_s408" --arm Sb --seed 408 --out "$R/platform_gate" --code "$W/pn1/code" --hf-home "$W/pn1/hf" --ref "$W/ref.tar" --sets dev --data dev="$W/pn1/data" --expect-eval "$W/reference/AB1_Sb_s408/scores_eval.npz" --workers 7 --stats no) > "$R/platform_gate.log" 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  "$PY" "$SP/check_gate.py" "$R/platform_gate" || rc=$?
fi
if [ "$rc" -eq 0 ]; then
  STAGE=training_only_score
  "$PY" "$SP/score_training.py" --code "$W/pn1/code" --hf-home "$W/pn1/hf" --net "$W/reference/AB1_Sb_s408" --metadata "$SP/training_identity_groups.csv" --data "$W/pn1/data" --out "$R/training_only" --battery-code "$W/bcode" --workers 7 > "$R/score_training.log" 2>&1 || rc=$?
fi
cp "$SP/SHA256SUMS" "$R/";printf 'exit_status=%s\njob=%s\n' "$rc" "$SLURM_JOB_ID" > "$R/status.txt"
tar -C "$W/res" -cf "$W/$TASK.tar" "$TASK"
cp "$W/$TASK.tar" "$OUT/$TASK.tar.part"
h=$(sha256sum "$W/$TASK.tar"|cut -c1-64)
[ "$(sha256sum "$OUT/$TASK.tar.part"|cut -c1-64)" = "$h" ]||die copyback
mv "$OUT/$TASK.tar.part" "$OUT/$TASK.tar";printf '%s  %s.tar\n' "$h" "$TASK" > "$OUT/$TASK.tar.sha256"
echo "TAIL_BASELINE_ARCHIVED status=$rc sha256=$h"
exit "$rc"
