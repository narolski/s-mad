#!/bin/bash -l
#SBATCH -J pn1-ref
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/results/PN1/logs/ref-%j.out
# Protocol network, first tests (PN1), amendment 5: reference row "standard recipe on released SMDD" = the eight
# existing ViT-B/16 MADation-recipe retrains scored on the PN1 evaluation manifest with pn1_score.py (container image).
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
PIN=5c6427907d92514ed284881fcf859f92a4294da74e03ada46226fdd7b0dd2676   # prereg.md "Pack pin"
[ "$(cut -c1-64 "$G/packs/PN1/pn1_pack.tar.sha256")" = "$PIN" ] || { echo "pack sha256 file differs from the registered pin"; exit 1; }
W=$MEMFS/work_ref; mkdir -p "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd "$W"
TASK_WORK="$W" bash "$G/tasks/PN1/score_ref.sh"
