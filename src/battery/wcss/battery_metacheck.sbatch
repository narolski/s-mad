#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J battery-metacheck
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:40G
#SBATCH --no-requeue
#SBATCH --time=0-00:45:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/battery-metacheck-%j.out
# Shared test battery (BATTERY) v1.0.0-rc2, release condition (lead, 13 Nov): exercise the exit-5 refusal on WCSS H100.
# A copy of AB1_A_s408 whose meta.json differs from the gate reference in one inference key (lora_r 2 -> 4; nothing is
# scored with it) is passed to battery.run; the run must stop with exit code 5 before the gate and before any scoring.
# The job succeeds (exit 0) only if battery.run exits 5 and no logits file exists. Smoke, never read as a result.
# Owner: BATTERY. All IO in $TMPDIR; one result tar to results/BATTERY/metacheck/. Expected run time 10-20 min.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs
CODE_SHA=19bf00aeb0b6b1ade3a5b424087a7d00bf3f6ec13f4bf9a0a63fc84510c736f3
OUTD=$L/results/BATTERY/metacheck
TAG=BATTERY_metacheck_${SLURM_JOB_ID:-local}
W=$TMPDIR/bw; mkdir -p "$W"
case "$W" in /lustre*) echo "BATTERY FAIL: work on Lustre"; exit 1 ;; esac
die() { echo "BATTERY FAIL: $*" >&2; exit 1; }
echo "BATTERY metacheck job ${SLURM_JOB_ID:-local} host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader || true
cp "$P/BATTERY/battery_code_v1rc2.tar" "$W/c.tar"; [ "$(sha256sum "$W/c.tar" | cut -c1-64)" = "$CODE_SHA" ] || die "code sha256"
mkdir -p "$W/code"; tar -C "$W/code" -xf "$W/c.tar"; rm -f "$W/c.tar"
cp "$P/BB2/pn1_pack_fs.tar" "$W/p.tar"
[ "$(sha256sum "$W/p.tar" | cut -c1-64)" = 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 ] || die "pack sha256"
tar -C "$W" -xf "$W/p.tar"; rm -f "$W/p.tar"
cp "$P/AB1/ab1_overlay_v2.tar" "$W/ov.tar"
[ "$(sha256sum "$W/ov.tar" | cut -c1-64)" = 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 ] || die "overlay sha256"
tar -C "$W" --skip-old-files -xf "$W/ov.tar"; rm -f "$W/ov.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS && sha256sum -c --quiet AB1SUMS) || die "pack content"
for n in AB1_Sb_s408 AB1_A_s408; do
  cp "$L/results/AB1/$n.tar" "$W/$n.tar"
  (cd "$W" && [ "$(sha256sum "$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$L/results/AB1/$n.tar.sha256")" ]) || die "$n sha256"
done
mkdir -p "$W/nets"; tar -C "$W/nets" -xf "$W/AB1_A_s408.tar" AB1_A_s408/meta.json AB1_A_s408/last_trainable.pt
mkdir -p "$W/nets/mod"; cp "$W/nets/AB1_A_s408/last_trainable.pt" "$W/nets/mod/"
PY=$HOME/dmenv/bin/python
$PY - "$W/nets/AB1_A_s408/meta.json" "$W/nets/mod/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1])); assert m["lora_r"] == 2, m["lora_r"]; m["lora_r"] = 4
json.dump(m, open(sys.argv[2], "w"), indent=1)
EOF
R=$W/res/$TAG; mkdir -p "$R"
rc=0
(cd "$W/code/src" && HF_HOME="$W/pn1/hf" HF_HUB_OFFLINE=1 $PY -m battery.run --ckpt "$W/nets/mod" --arm A --seed 408 --out "$R/battery" \
   --code "$W/pn1/code" --ref "$W/AB1_Sb_s408.tar" --data dev="$W/pn1/data" --sets dev --hf-home "$W/pn1/hf" --workers 7 --stats no) \
   > "$R/battery.log" 2>&1 || rc=$?
tail -n 5 "$R/battery.log"
ok=0; [ "$rc" = 5 ] && ! ls "$R/battery"/*logits* >/dev/null 2>&1 && ok=1
echo "battery.run exit $rc; expected 5; refusal_ok $ok host $(hostname) job ${SLURM_JOB_ID:-local}" | tee "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"; mkdir -p "$OUTD"
cp "$W/$TAG.tar" "$OUTD/$TAG.tar.part"; (cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
[ "$(sha256sum "$OUTD/$TAG.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TAG.tar.sha256")" ] || die "copy-back sha256"
mv "$OUTD/$TAG.tar.part" "$OUTD/$TAG.tar"; cp "$W/$TAG.tar.sha256" "$OUTD/"
[ "$ok" = 1 ] || die "the meta-mismatch refusal did not happen as designed (exit $rc)"
echo "BATTERY_METACHECK_OK $OUTD/$TAG.tar"
