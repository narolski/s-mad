#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=01:00:00
#SBATCH --job-name=ad4-fu-h100
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ad4-fu-h100-%j.out
# Owner: reading owner of the morph-free networks experiment (AD4). Workload (prereg Amendment 6), all on Lustre before submission:
# the AD4 pack (packs/AD4/ad4_pack.tar), the follow-up pack (packs/AD4/fu_pack_wcss.tar: the eleven registered ViT-B/16 networks'
# meta.json + last_trainable.pt, the extra pool images and manifest, fu_rescore.py), the library packs. Scores the eleven networks on
# the unblanked evaluation images (gate), on the same images blanked in memory outside the fixed face ellipse (H-new-3), and on the
# extra pools (H-new-4, H-new-5), in the WCSS container on one H100. FU_LIMIT=8 for the smoke. One result tar to results/AD4_fu/.
set -euo pipefail
: "${TMPDIR:?local scratch required}"
L=/lustre/pd03/hpc-narolski-1790461090
B=$L/smad-next
SIF=/lustre/software-data/container-images/pytorch_latest.sif
PACK_SHA=1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde
FU_SHA=e4b60874484eda7d444f550f7722824b9937610f6f569883ced88f8d52c44a83   # pinned (pre-run check F5)
LIMIT=${FU_LIMIT:-0}
TAG=fu_h100_${SLURM_JOB_ID}_limit${LIMIT}
die() { echo "AD4FU FAIL: $*" >&2; exit 1; }
for f in "$B/packs/AD4/ad4_pack.tar" "$B/packs/AD4/fu_pack_wcss.tar" "$B/packs/AD4/fu_pack_wcss.tar.sha256" \
         "$L/smadcvpr/packs/pylib.tar" "$L/smadcvpr/packs/pylib_a12.tar"; do
  [ -f "$f" ] || { echo "AD4FU: missing $f; nothing to do"; exit 3; }
done
T0=$SECONDS
W=$TMPDIR/fu; mkdir -p "$W"
echo "AD4FU $SLURM_JOB_ID host $(hostname) limit $LIMIT $(date +%FT%T)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
cp "$B/packs/AD4/ad4_pack.tar" "$W/ad4_pack.tar"
[ "$(sha256sum "$W/ad4_pack.tar" | cut -c1-64)" = "$PACK_SHA" ] || die "ad4_pack.tar sha256"
tar -C "$W" -xf "$W/ad4_pack.tar" && rm -f "$W/ad4_pack.tar"
(cd "$W/ad4" && sha256sum -c --quiet SHA256SUMS) || die "ad4 pack content"
cp "$B/packs/AD4/fu_pack_wcss.tar" "$W/fu_pack.tar"
[ "$(sha256sum "$W/fu_pack.tar" | cut -c1-64)" = "$FU_SHA" ] || die "fu_pack sha256"
tar -C "$W" -xf "$W/fu_pack.tar" && rm -f "$W/fu_pack.tar"
[ "$(sha256sum "$W/fu/src/fu_rescore.py" | cut -c1-64)" = e0ab24b59ec8e8bf8c6b2704d8b5f82bd2dac1fadca0e75948597b799a145939 ] || die "fu_rescore.py sha256"
grep -q '"networks_from": "/mnt/t7/smad_next/AD4/results_wcss_m3"' "$W/fu/build_info.json" || die "fu pack networks are not the WCSS ones"
for n in pylib pylib_a12; do
  cp "$L/smadcvpr/packs/$n.tar" "$W/$n.tar"
  [ "$(sha256sum "$W/$n.tar" | cut -c1-64)" = "$(awk 'NR==1{print $1}' "$L/smadcvpr/packs/$n.tar.sha256")" ] || die "$n.tar sha256"
  tar -C "$W" -xf "$W/$n.tar" && rm -f "$W/$n.tar"
done
echo "AD4FU packs ok ($((SECONDS - T0)) s)"
D=$W/data; mkdir -p "$D/manifests"
ln -s "$W/ad4/data/eval" "$D/eval"; ln -s "$W/fu/data/extra" "$D/extra"
cp "$W/ad4/data/manifests/ad4_eval.csv" "$W/fu/data/manifests/fu_extra.csv" "$D/manifests/"
R=$W/res/$TAG; mkdir -p "$R"
apptainer exec --nv -B /lustre -B "$W" -B "$TMPDIR" \
  --env "PYTHONPATH=$W/pylib_a12:$W/pylib:$W/ad4/code,SMAD_DATA=$D,HF_HOME=$W/ad4/hf,HF_HUB_OFFLINE=1,PYTHONUNBUFFERED=1" \
  "$SIF" python "$W/fu/src/fu_rescore.py" score --code "$W/ad4/code" --nets "$W/fu/nets" \
  --manifests ad4_eval.csv,ad4_eval.csv:blank,fu_extra.csv --out "$R" --workers 7 --limit "$LIMIT"
cp "$W/fu/build_info.json" "$R/"
echo "wall_s $((SECONDS - T0)) host $(hostname) limit $LIMIT" > "$R/job_info.txt"
mkdir -p "$B/results/AD4_fu"
tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"
cp "$W/$TAG.tar" "$B/results/AD4_fu/$TAG.tar.part"
(cd "$W" && sha256sum "$TAG.tar") > "$B/results/AD4_fu/$TAG.tar.sha256"
mv "$B/results/AD4_fu/$TAG.tar.part" "$B/results/AD4_fu/$TAG.tar"
echo "AD4FU_DONE $B/results/AD4_fu/$TAG.tar wall $((SECONDS - T0)) s"
