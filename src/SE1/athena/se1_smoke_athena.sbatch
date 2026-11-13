#!/bin/bash -l
#SBATCH -J se1-smoke
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=00:45:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/results/SE1/logs/smoke-%j.out
# Seam-shortcut training arm (SE1), Athena twin of the WCSS smoke: src/SE1/run.sh in the project container, arm SE seed 408,
# 100 steps, 64 scoring rows, real packs; results to results/SE1_smoke, never read as results.
set -uo pipefail
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
P=$G/packs/SE1
: "${MEMFS:?RAM disk required (-C memfs)}"
hostname; nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader; date -Is
[ "$(sha256sum "$P/run.sh" | cut -c1-64)" = b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb ] || { echo "SE1 FAIL run.sh not at its registered pin"; exit 1; }
(cd "$P" && sha256sum -c run.sh.sha256 se1_overlay.tar.sha256 pn1_pack_fs.tar.sha256) || { echo "SE1_SMOKE_FAIL pack or script check"; exit 1; }
TD=$MEMFS/td; W=$MEMFS/w; mkdir -p "$TD" "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
printf 'TASK=SE1smoke_SE_s408\nARM=SE\nSEED=408\n' > "$TD/task.env"
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$G PN1_PACK=$P/pn1_pack_fs.tar SE1_OVERLAY=$P/se1_overlay.tar \
  SE1_OVERLAY_SHA=de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c PN1_SIF=$G/containers/smad_torch221_cu121_v1.sif \
  SE1_RESULTS=$G/results/SE1_smoke PN1_STEPS=100 PN1_LIMIT=64 PN1_WORKERS=7 bash "$P/run.sh"
echo "SE1_SMOKE_RC $? $(date -Is)"
# Platform reproduction check (prereg section 9, printed): FS1's Sb seed 403 (A100, torch 2.2.1) rescored on this platform
# with the unchanged src/PN1/rescore.py (6f6eede7) on the C2P gate rows (fam af0, ffhq); compared on the DGX with the
# stored A100 logits by c2p_read.gate (99th pct |dlogit| <= 0.05, max <= 0.10, own-rule agreement >= 99.5%).
mkdir -p "$TMPDIR/nets" "$TMPDIR/pc"
(cd "$P" && sha256sum -c rescore.py.sha256 PN1_Sb_s403.tar.sha256) && tar -C "$TMPDIR/nets" -xf "$P/PN1_Sb_s403.tar" PN1_Sb_s403/meta.json PN1_Sb_s403/last_trainable.pt \
  && for FAM in af0 ffhq; do SMAD_DATA=$W/data HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" $G/containers/smad_torch221_cu121_v1.sif python "$P/rescore.py" --resdir "$TMPDIR/nets/PN1_Sb_s403" \
     --code "$W/pn1/code" --manifest pn1_eval.csv --fam $FAM --out "$TMPDIR/pc/PC_PN1_Sb_s403_$FAM.npz" --workers 7 || echo "SE1_PC_FAIL $FAM"; done
tar -C "$TMPDIR" -cf "$TMPDIR/SE1_platformcheck.tar" pc && cp "$TMPDIR/SE1_platformcheck.tar" "$G/results/SE1_smoke/SE1_platformcheck_${SLURM_JOB_ID}.tar" && echo "SE1_PC_DONE $(date -Is)"
