#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1), amendment 2: one add-on task = one shard's job list through
# dg1_addon.py, in the job's RAM disk $MEMFS. The base pack (checkpoint, inputs, DiffAE repo) and the small add-on pack
# (code/dg1_addon.py, jobs/addon_*.csv) are sha-checked and extracted. The result tar (+ .sha256) is ALWAYS written,
# also when dg1_addon.py exits non-zero (review finding 8); the task then exits with the generator's code.
# Arguments: TAG LIST. Needs: G, DG1_PY (dg1_env.sh), MEMFS.
set -euo pipefail
TAG=$1; L=$2
: "${MEMFS:?RAM disk required (-C memfs)}"
W=$MEMFS/dg1_$TAG
R=$G/results/DG1
[ ! -e "$R/DG1_$TAG.tar" ] && [ ! -e "$R/DG1_${TAG}_codes.tar" ] || { echo "refused: a result tar of $TAG exists"; exit 4; }
mkdir -p "$W" "$R"
export TMPDIR=$MEMFS/tmp TORCH_HOME=$MEMFS/torch XDG_CACHE_HOME=$MEMFS/cache OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "$TMPDIR"
t0=$(date +%s)
( cd "$G/packs/DG1" && sha256sum -c dg1_pack.tar.sha256 && sha256sum -c dg1_addon_pack.tar.sha256 )
tar -C "$W" -xf "$G/packs/DG1/dg1_pack.tar"
tar -C "$W" -xf "$G/packs/DG1/dg1_addon_pack.tar"
K=$W/dg1pack
A=$W/dg1addon
( cd "$K" && sha256sum -c --quiet MANIFEST.sha256 )
( cd "$A" && sha256sum -c --quiet MANIFEST.sha256 )
echo "packs ok, unpack $(( $(date +%s) - t0 )) s"
O=$W/out_$TAG; mkdir -p "$O"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$O/gpumem.csv"; sleep 10; done ) & SM=$!
trap 'kill $SM 2>/dev/null || true' EXIT
mkdir -p "$W/run"
set +e
( cd "$W/run" && "$DG1_PY" -I "$A/code/dg1_addon.py" --repo "$K/repo" --repo-manifest "$K/repo_manifest.sha256" \
    --ckpt "$K/ckpt/last.ckpt" --inputs "$K/inputs/a256" --jobs "$A/jobs/$L.csv" --out-root "$O/$L" --bs 16 ) \
    > "$O/$L.log" 2>&1
RC=$?
set -e
tail -n 40 "$O/$L.log"
kill $SM 2>/dev/null || true
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$O/gpumem.csv" | tee "$O/peak.txt"
cp "$G/envs/DG1/versions.txt" "$O/versions.txt"
hostname > "$O/host.txt"; echo "${SLURM_JOB_ID:-} ${SLURM_ARRAY_JOB_ID:-} ${SLURM_ARRAY_TASK_ID:-} rc=$RC" > "$O/slurm.txt"
# codes and fresh-noise draws go into their own tar, which stays on Athena (lead, 11 Nov 20:45: T7 disk is full);
# their sha256 is recorded inside the image tar
C=$W/codes_$TAG; mkdir -p "$C/$L"
for f in codes.npz fresh.npz; do [ -f "$O/$L/$f" ] && mv "$O/$L/$f" "$C/$L/"; done
( cd "$C/$L" && sha256sum ./*.npz > "$O/$L/codes_sha256.txt" 2>/dev/null || true )
tar -C "$W" -cf "$W/DG1_$TAG.tar" "out_$TAG"
tar -C "$W" -cf "$W/DG1_${TAG}_codes.tar" "codes_$TAG"
( cd "$W" && sha256sum "DG1_$TAG.tar" > "DG1_$TAG.tar.sha256" && sha256sum "DG1_${TAG}_codes.tar" > "DG1_${TAG}_codes.tar.sha256" )
cp "$W/DG1_$TAG.tar" "$W/DG1_$TAG.tar.sha256" "$W/DG1_${TAG}_codes.tar" "$W/DG1_${TAG}_codes.tar.sha256" "$R/"
( cd "$R" && sha256sum -c "DG1_$TAG.tar.sha256" "DG1_${TAG}_codes.tar.sha256" )
echo "TASK_END $TAG rc=$RC $(( $(date +%s) - t0 )) s"
exit $RC
