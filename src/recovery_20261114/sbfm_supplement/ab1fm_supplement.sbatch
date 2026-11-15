#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --job-name=ab1fm-supplement
#SBATCH --partition=lem-gpu-short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1fm-supplement-%j.out
# Existing SbFM and paired AB1 Sb, seeds408-412: exact fit-manifest gate then unchanged TT1/MEDS scorer.
# No fit, transforms, statistical read or benchmark. Registered runtime admission required before tar extraction.
set -euo pipefail
: "${TMPDIR:?allocated local scratch required}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1FMSUPP
for spec in \
  "config.json:4ec95da9ac37d3f958124b5d5cb72a812497601b3acaad4d264bc00e41294ddf" \
  "run_supplement.py:2dd5535b64901691176f0268130fecc48f34145709d7081bde8f9f9cbb41474b" \
  "validate_family.py:cf7904f910e939f5a0a3eef16ef5b92596925a76981fab1a4801861e606fc0a2"; do
  f=${spec%%:*}; expected=${spec##*:}
  [ "$(sha256sum "$P/$f" | cut -c1-64)" = "$expected" ] || { echo "SUPPLEMENT_FAIL sourcepin $f"; exit 1; }
done
hostname; date -Is
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
"$HOME/dmenv/bin/python" -I "$P/run_supplement.py" --stage "$P" --work "$TMPDIR/ab1fm_supplement" --results "$L/results/AB1FMSUPP"
