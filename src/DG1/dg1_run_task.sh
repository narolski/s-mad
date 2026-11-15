#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): one task = one job list run through dg1_gen.py in the job's RAM
# disk $MEMFS (-C memfs; Athena's -C localfs scratch is only 4 GB); one result tar with a .sha256 in $G/results/DG1/.
# Arguments: TAG (result name), then one or more job-list names inside the pack's jobs/ (each runs into its own folder).
# Needs: G, DG1_PY (from dg1_env.sh), MEMFS. The pack: $G/packs/DG1/dg1_pack.tar (+ .sha256).
set -euo pipefail
TAG=$1; shift
: "${MEMFS:?RAM disk required (-C memfs)}"
W=$MEMFS/dg1_$TAG
R=$G/results/DG1
[ ! -e "$R/DG1_$TAG.tar" ] || { echo "refused: $R/DG1_$TAG.tar exists"; exit 4; }
mkdir -p "$W" "$R"
export TMPDIR=$MEMFS/tmp TORCH_HOME=$MEMFS/torch XDG_CACHE_HOME=$MEMFS/cache OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "$TMPDIR"
t0=$(date +%s)
( cd "$G/packs/DG1" && sha256sum -c dg1_pack.tar.sha256 )      # read once from the project store
tar -C "$W" -xf "$G/packs/DG1/dg1_pack.tar"                       # extracted straight into the RAM disk
K=$W/dg1pack
( cd "$K" && sha256sum -c --quiet MANIFEST.sha256 )
echo "pack manifest ok"
echo "unpack $(( $(date +%s) - t0 )) s"
O=$W/out_$TAG; mkdir -p "$O"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$O/gpumem.csv"; sleep 10; done ) & SM=$!
trap 'kill $SM 2>/dev/null || true' EXIT
mkdir -p "$W/run"
for L in "$@"; do
  ( cd "$W/run" && "$DG1_PY" -I "$K/code/dg1_gen.py" --repo "$K/repo" --repo-manifest "$K/repo_manifest.sha256" \
      --ckpt "$K/ckpt/last.ckpt" --inputs "$K/inputs/a256" --jobs "$K/jobs/$L.csv" --out-root "$O/$L" --bs 16 ) \
      2>&1 | tee "$O/$L.log"
done
kill $SM 2>/dev/null || true
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$O/gpumem.csv" | tee "$O/peak.txt"
cp "$G/envs/DG1/versions.txt" "$O/versions.txt"
hostname > "$O/host.txt"; echo "${SLURM_JOB_ID:-} ${SLURM_ARRAY_JOB_ID:-} ${SLURM_ARRAY_TASK_ID:-}" > "$O/slurm.txt"
tar -C "$W" -cf "$W/DG1_$TAG.tar" "out_$TAG"
( cd "$W" && sha256sum "DG1_$TAG.tar" > "DG1_$TAG.tar.sha256" )
cp "$W/DG1_$TAG.tar" "$W/DG1_$TAG.tar.sha256" "$R/"
( cd "$R" && sha256sum -c "DG1_$TAG.tar.sha256" )
echo "TASK_OK $TAG $(( $(date +%s) - t0 )) s"
