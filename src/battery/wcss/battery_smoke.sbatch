#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J battery-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/battery-smoke-%j.out
# Shared test battery (BATTERY) v1 smoke on WCSS H100 (a smoke, never read as a result). Owner: BATTERY owner (Claude agent
# for the lead). Workload, all on Lustre before submission: the battery code tar (packs/BATTERY, pinned below), the FS1
# pack + AB1 overlay v2 (dev set), the TT1 pack, the MEDS pack, the GD pack, and two stored H100 networks
# (results/AB1/AB1_Sb_s408.tar = the H100 gate reference, AB1_A_s408.tar = a second network).
# Steps: copy and verify every tar into $TMPDIR (one at a time, tar removed after unpacking); run
#   1) battery.run on AB1_Sb_s408 (gate + all four sets; its dev logits must equal its stored fit-job logits on all
#      21,277 rows, checked after the job on the DGX);
#   2) battery.run on AB1_A_s408 (same; a second network).
# --stats no (statistics are completed on the DGX with --stats-only). One result tar back to results/BATTERY/.
# A missing or mismatched input fails within a minute. Expected run time: about 25-40 min (copies 21 GB, scores 2 x 67,700 rows).
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs
CODE_TAR=$P/BATTERY/battery_code_v1rc1.tar
CODE_SHA=8a86676d17c2aea33ac5f05ee40589c2a199ff709982619f810f353cdc4615dd
OUTD=$L/results/BATTERY
TAG=BATTERY_smoke_${SLURM_JOB_ID:-local}
W=$TMPDIR/bw; mkdir -p "$W"
case "$W" in /lustre*) echo "BATTERY FAIL: work on Lustre"; exit 1 ;; esac
die() { echo "BATTERY FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "BATTERY smoke job ${SLURM_JOB_ID:-local} host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader || true
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
for n in AB1_Sb_s408 AB1_A_s408; do
  cp "$L/results/AB1/$n.tar" "$W/$n.tar"
  (cd "$W" && [ "$(sha256sum "$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$L/results/AB1/$n.tar.sha256")" ]) || die "$n sha256"
  mkdir -p "$W/nets"; tar -C "$W/nets" -xf "$W/$n.tar" "$n/meta.json" "$n/last_trainable.pt"
done
df -h "$TMPDIR" | tail -1
export HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2
R=$W/res/$TAG; mkdir -p "$R"
PY=$HOME/dmenv/bin/python
$PY -c "import sys, torch, timm, numpy, PIL; print('BATTERY env', sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__)" | tee "$R/env.txt"
rc=0
for n in AB1_Sb_s408 AB1_A_s408; do
  arm=${n#AB1_}; arm=${arm%_s*}
  if ! (cd "$W/code/src" && $PY -m battery.run --ckpt "$W/nets/$n" --arm "$arm" --seed 408 --out "$R/$n" --code "$W/pn1/code" \
          --ref "$W/AB1_Sb_s408.tar" --data dev="$W/pn1/data" tt1="$W/tt1/data" meds="$W/tt1m/data" gd="$W/pr1g/data" \
          --hf-home "$W/pn1/hf" --workers 7 --stats no) > "$R/$n.log" 2>&1; then rc=1; fi
  tail -n 12 "$R/$n.log"
done
echo "rc $rc wall_s $((SECONDS - T0)) host $(hostname) job ${SLURM_JOB_ID:-local} code_sha256 $CODE_SHA" > "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"
mkdir -p "$OUTD"
cp "$W/$TAG.tar" "$OUTD/$TAG.tar.part"
(cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
[ "$(sha256sum "$OUTD/$TAG.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TAG.tar.sha256")" ] || die "copy-back sha256"
mv "$OUTD/$TAG.tar.part" "$OUTD/$TAG.tar"; cp "$W/$TAG.tar.sha256" "$OUTD/"
echo "BATTERY_RESULT $OUTD/$TAG.tar $(cut -c1-64 "$W/$TAG.tar.sha256") rc $rc"
exit $rc
