#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J battery-nets
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/battery-nets-%A_%a.out
# Shared test battery (BATTERY) v1.0.0-rc2 on WCSS H100: one stored AB1 network per array task (A, B, Sb x 408-412),
# battery-scored on all four development sets with the platform gate, the network check (--expect-eval against the
# network's own AB1 fit-job scores_eval.npz) and its registered training manifest. --stats no (completed on the DGX).
# Used for (a) the rc2 smoke on a node other than r18-8 (--array=0-1 --exclude=r18-8, only if smoke 6316361 ran on
# r18-8) and (b) the registered comparator step (experiments/BATTERY_shared-test-battery/prereg_ab1_comparators.md,
# --array=0-14). Owner: BATTERY. All IO in $TMPDIR; one result tar per task to results/BATTERY/nets/. A missing or
# mismatched input fails within a minute. Expected run time per task: 15-30 min (copies 21 GB, scores 67,748 rows + gate).
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs
CODE_TAR=$P/BATTERY/battery_code_v1rc2.tar
CODE_SHA=__CODE_SHA__
NETS=(AB1_Sb_s408 AB1_A_s408 AB1_B_s408 AB1_A_s409 AB1_B_s409 AB1_Sb_s409 AB1_A_s410 AB1_B_s410 AB1_Sb_s410
      AB1_A_s411 AB1_B_s411 AB1_Sb_s411 AB1_A_s412 AB1_B_s412 AB1_Sb_s412)
I=${SLURM_ARRAY_TASK_ID:?array task}
N=${NETS[$I]}; ARM=${N#AB1_}; ARM=${ARM%_s*}; SEED=${N##*_s}
OUTD=$L/results/BATTERY/nets
TAG=BATTERY_${N}_${SLURM_ARRAY_JOB_ID:-local}_${I}
W=$TMPDIR/bw; mkdir -p "$W"
case "$W" in /lustre*) echo "BATTERY FAIL: work on Lustre"; exit 1 ;; esac
die() { echo "BATTERY FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "BATTERY nets $N job ${SLURM_ARRAY_JOB_ID:-local}/$I host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader || true
if [ -e "$OUTD/$TAG.tar" ]; then echo "BATTERY already done: $OUTD/$TAG.tar"; exit 0; fi
get() {   # tar sha256 destdir: copy, verify, unpack, remove the tar
  local t=$1 h=$2 d=$3 n; n=$(basename "$t")
  [ -f "$t" ] || die "$t missing"
  cp "$t" "$W/$n"
  [ "$(sha256sum "$W/$n" | cut -c1-64)" = "$h" ] || die "$n sha256"
  mkdir -p "$d"; tar -C "$d" -xf "$W/$n"; rm -f "$W/$n"
  echo "BATTERY got $n ($((SECONDS - T0)) s)"
}
get "$CODE_TAR" "$CODE_SHA" "$W/code"
get "$P/BB2/pn1_pack_fs.tar" 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 "$W"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "FS1 pack content off its SHA256SUMS"
cp "$P/AB1/ab1_overlay_v2.tar" "$W/ov.tar"
[ "$(sha256sum "$W/ov.tar" | cut -c1-64)" = 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 ] || die "overlay sha256"
tar -C "$W" --skip-old-files -xf "$W/ov.tar" && rm -f "$W/ov.tar"
(cd "$W/pn1" && sha256sum -c --quiet AB1SUMS) || die "overlay content off its AB1SUMS"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "FS1 files changed by the overlay"
get "$P/TT1/tt1_pack.tar" 2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554 "$W"
(cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || die "TT1 pack SHA256SUMS"
get "$P/BB2/tt1m_meds.tar" 3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61 "$W"
(cd "$W/tt1m" && sha256sum -c --quiet SHA256SUMS) || die "MEDS pack SHA256SUMS"
get "$P/BB2/pr1_gd.tar" 40aa95d2b48719025bc3b80ebf9fa997bb1adf6c69da894120716a6e962b7329 "$W"
(cd "$W/pr1g" && sha256sum -c --quiet SHA256SUMS) || die "GD pack SHA256SUMS"
for n in AB1_Sb_s408 "$N"; do
  [ -f "$W/$n.tar" ] && continue
  cp "$L/results/AB1/$n.tar" "$W/$n.tar"
  (cd "$W" && [ "$(sha256sum "$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$L/results/AB1/$n.tar.sha256")" ]) || die "$n sha256"
done
mkdir -p "$W/nets"; tar -C "$W/nets" -xf "$W/$N.tar" "$N/meta.json" "$N/last_trainable.pt" "$N/scores_eval.npz"
case "$ARM" in A|B|Sb) MAN=train_$ARM.csv ;; *) die "arm $ARM" ;; esac
df -h "$TMPDIR" | tail -1
export HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2
R=$W/res/$TAG; mkdir -p "$R"
PY=$HOME/dmenv/bin/python
$PY -c "import sys, torch, timm, numpy, PIL; print('BATTERY env', sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__)" | tee "$R/env.txt"
rc=0
(cd "$W/code/src" && $PY -m battery.run --ckpt "$W/nets/$N" --arm "$ARM" --seed "$SEED" --out "$R/battery" --code "$W/pn1/code" \
    --ref "$W/AB1_Sb_s408.tar" --data dev="$W/pn1/data" tt1="$W/tt1/data" meds="$W/tt1m/data" gd="$W/pr1g/data" \
    --hf-home "$W/pn1/hf" --train-manifest "$W/pn1/data/manifests/$MAN" --expect-eval "$W/nets/$N/scores_eval.npz" \
    --workers 7 --stats no) > "$R/battery.log" 2>&1 || rc=$?
tail -n 15 "$R/battery.log"
echo "rc $rc wall_s $((SECONDS - T0)) host $(hostname) job ${SLURM_ARRAY_JOB_ID:-local}/$I net $N code_sha256 $CODE_SHA" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"
mkdir -p "$OUTD"
cp "$W/$TAG.tar" "$OUTD/$TAG.tar.part"
(cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
[ "$(sha256sum "$OUTD/$TAG.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TAG.tar.sha256")" ] || die "copy-back sha256"
mv "$OUTD/$TAG.tar.part" "$OUTD/$TAG.tar"; cp "$W/$TAG.tar.sha256" "$OUTD/"
echo "BATTERY_RESULT $OUTD/$TAG.tar $(cut -c1-64 "$W/$TAG.tar.sha256") rc $rc"
exit $rc
