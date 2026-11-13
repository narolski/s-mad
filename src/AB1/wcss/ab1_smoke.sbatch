#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1-smoke-%j.out
# Protocol ablation and replication (AB1) smoke through the real code path on WCSS H100. Owner: AB1 owner (Claude
# agent for the lead). (1) src/AB1/run.sh, arm SbH seed 408, 100 steps, 64 scoring rows (eval and train), real packs;
# results to results/AB1_smoke, never read as results; prints the step rate for the fit time limit. (2) Platform
# measurement: the FS1 network Sb seed 403 (A100 PCIe original, tar 8dec83b8...) rescored on this H100 with the
# unchanged src/PN1/rescore.py (6f6eede7) through src/TT1/rescore_tf32.py (0d0b6b6f; TF32 on as pn1_score.py) on the
# FS1 gate rows (fam af0 1,339 and ffhq 5,000); compared on the DGX with its stored A100 logits (descriptive only).
# (3) The smoke network rescored on the 1,480 hold-out rows (fam ms1ffhq) to exercise the hold-out image path.
# All IO in $TMPDIR; one tar out.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1; R=$L/results/AB1_smoke
hostname; nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader; date -Is
(cd "$P" && sha256sum -c run.sh.sha256 ab1_overlay.tar.sha256 rescore.py.sha256 rescore_tf32.py.sha256 PN1_Sb_s403.tar.sha256) \
  || { echo "AB1_SMOKE_FAIL pack or script check"; exit 1; }
[ "$(cut -c1-64 $P/rescore.py.sha256)" = 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e ] || { echo "AB1_SMOKE_FAIL rescore pin"; exit 1; }
[ "$(cut -c1-64 $P/rescore_tf32.py.sha256)" = 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 ] || { echo "AB1_SMOKE_FAIL wrapper pin"; exit 1; }
[ -e "$R/AB1smoke_platform.tar" ] && { echo "AB1_SMOKE_FAIL platform tar exists (never overwritten)"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W" "$R"
printf 'TASK=AB1smoke_SbH_s408\nARM=SbH\nSEED=408\n' > "$TD/task.env"
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L AB1_RESULTS=$R PN1_PY=$HOME/dmenv/bin/python PN1_STEPS=100 PN1_LIMIT=64 \
  PN1_WORKERS=7 bash "$P/run.sh"
echo "AB1_SMOKE_RUN_RC $? $(date -Is)"
O=$TMPDIR/out; N=$TMPDIR/nets; mkdir -p "$O" "$N"
tar -C "$N" -xf "$P/PN1_Sb_s403.tar" PN1_Sb_s403/meta.json PN1_Sb_s403/last_trainable.pt
nf=0
# hold-out image path on this platform: the 100-step smoke network scored on the 1,480 ms1ffhq rows of ab1_eval.csv
tar -C "$N" -xf "$R/AB1smoke_SbH_s408.tar" AB1smoke_SbH_s408/meta.json AB1smoke_SbH_s408/last_trainable.pt \
  && SMAD_DATA=$W/data HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 $HOME/dmenv/bin/python "$P/rescore_tf32.py" "$P/rescore.py" \
    --resdir "$N/AB1smoke_SbH_s408" --code "$W/pn1/code" --manifest ab1_eval.csv --fam ms1ffhq \
    --out "$O/AB1smoke_SbH_s408_ms1ffhq.npz" --workers 7 >> "$O/rescore.log" 2>&1 || { echo "rescore ms1ffhq failed"; nf=$((nf+1)); }
for FAM in af0 ffhq; do
  SMAD_DATA=$W/data HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 $HOME/dmenv/bin/python "$P/rescore_tf32.py" "$P/rescore.py" \
    --resdir "$N/PN1_Sb_s403" --code "$W/pn1/code" --manifest pn1_eval.csv --fam "$FAM" \
    --out "$O/AB1plat_PN1_Sb_s403_${FAM}.npz" --workers 7 >> "$O/rescore.log" 2>&1 || { echo "rescore $FAM failed"; nf=$((nf+1)); }
done
nvidia-smi --query-gpu=uuid,name,driver_version --format=csv,noheader > "$O/gpu.txt" 2>&1 || true
$HOME/dmenv/bin/python -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__)" > "$O/env.txt" 2>&1 || true
tar -C "$TMPDIR" -cf "$TMPDIR/AB1smoke_platform.tar" out && (cd "$TMPDIR" && sha256sum AB1smoke_platform.tar > AB1smoke_platform.tar.sha256)
cp "$TMPDIR/AB1smoke_platform.tar" "$R/AB1smoke_platform.tar.part" \
  && [ "$(sha256sum "$R/AB1smoke_platform.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$TMPDIR/AB1smoke_platform.tar.sha256")" ] \
  && mv "$R/AB1smoke_platform.tar.part" "$R/AB1smoke_platform.tar" && cp "$TMPDIR/AB1smoke_platform.tar.sha256" "$R/" \
  || { echo "AB1_SMOKE_FAIL copy-back"; exit 1; }
echo "AB1_SMOKE_DONE rescore_failures $nf $(date -Is)"
