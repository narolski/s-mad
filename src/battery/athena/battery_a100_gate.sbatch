#!/bin/bash -l
#SBATCH -J smadnext-BATTERY-a100gate
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-now
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/BATTERY-a100gate-%j.out
# Shared test battery (BATTERY) v1.0.0-rc2: A100 platform smoke on Athena (lead's decision 13 Nov). Smoke, never read
# as a result. In the torch 2.2.1 / CUDA 12.1 container smad_torch221_cu121_v1.sif (the image that reproduced the rented
# A100 PCIe gate scores of Sb 403-407 in NE1, job 3550470): battery.run with --test-gate-key for the pinned A100 PCIe key,
# i.e. the battery's own loader and scorer rescore the reference PN1_Sb_s403 on the 2,496 gate rows (39 whole stored
# batches) and compare with its stored A100 PCIe fit-job logits; the test-gate run scores nothing else. Athena's A100
# gets its own platform key (pinned in a later battery version) only if the result is byte-gated. Owner: BATTERY.
# Inputs (sha256-checked): packs/BATTERY/battery_code_v1rc2.tar, PN1_Sb_s403.tar, pn1_pack_fs.tar, ab1_overlay_v2.tar.
# Work on $MEMFS (about 10 GB); one result tar to results/BATTERY/. Expected run time 10-20 min.
set -eo pipefail
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
P=$G/packs/BATTERY; OUT=$G/results/BATTERY; mkdir -p "$OUT"
TAG=BATTERY_a100gate_${SLURM_JOB_ID:-local}
W=$MEMFS/work_BATTERY; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR" "$W"; cd "$W"
SIF=$G/containers/smad_torch221_cu121_v1.sif
R=$W/res/$TAG; mkdir -p "$R"
die() { echo "BATTERY FAIL: $*" >&2; exit 1; }
hostname | tee "$R/host.txt"; date -Is
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader | tee "$R/gpu.txt"
[ "$(sha256sum "$SIF" | cut -c1-64)" = fedeff10a26d14edad624fffc048fc197509618ba5012519c47699dd6419649f ] || die "container sha256"
chk() { [ "$(sha256sum "$1" | cut -c1-64)" = "$2" ] || die "$1 sha256"; }
chk "$P/battery_code_v1rc2.tar" 19bf00aeb0b6b1ade3a5b424087a7d00bf3f6ec13f4bf9a0a63fc84510c736f3
chk "$P/PN1_Sb_s403.tar" 8dec83b880b7bac28db4b6217bc10b58eb78dc65d699734614cf57ae6b444fde
chk "$P/pn1_pack_fs.tar" 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
chk "$P/ab1_overlay_v2.tar" 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149
mkdir -p "$W/code" "$W/nets"
tar -C "$W/code" -xf "$P/battery_code_v1rc2.tar"
tar -C "$W" -xf "$P/pn1_pack_fs.tar"
tar -C "$W" --skip-old-files -xf "$P/ab1_overlay_v2.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS && sha256sum -c --quiet AB1SUMS) || die "pack content"
tar -C "$W/nets" -xf "$P/PN1_Sb_s403.tar" PN1_Sb_s403/meta.json PN1_Sb_s403/last_trainable.pt
echo "inputs ok $(date -Is)"
rc=0
apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" --pwd "$W/code/src" "$SIF" env HF_HOME="$W/pn1/hf" HF_HUB_OFFLINE=1 \
  PYTHONUNBUFFERED=1 python -m battery.run --ckpt "$W/nets/PN1_Sb_s403" --arm Sb --seed 403 --out "$R/battery" \
  --code "$W/pn1/code" --hf-home "$W/pn1/hf" --ref "$P/PN1_Sb_s403.tar" --data dev="$W/pn1/data" --sets dev --workers 14 \
  --test-gate-key "NVIDIA A100-PCIE-40GB|torch 2.2.1|tf32 1/1" > "$R/battery.log" 2>&1 || rc=$?
tail -n 6 "$R/battery.log"
echo "battery.run exit $rc (0 = gate byte- or tolerance-gated, 2 = failed) host $(hostname) job ${SLURM_JOB_ID:-local}" | tee "$R/task_info.txt"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"; (cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
cp "$W/$TAG.tar" "$OUT/$TAG.tar.part" && mv "$OUT/$TAG.tar.part" "$OUT/$TAG.tar"; cp "$W/$TAG.tar.sha256" "$OUT/"
echo "BATTERY_A100GATE_DONE rc $rc $(date -Is)"
exit $rc
