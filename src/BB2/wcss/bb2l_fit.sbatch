#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2l-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --array=0-14%15
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2l-fit-%A_%a.out
# Second backbone (BB2), amendment 4 (E3): 15 fits at the rule-fixed LoRA learning rate (run_lr.sh), arms A, B, Sb, seeds 403-407, one per array task,
# seed by seed (403-405 first), at most 15 GPUs at once; src/BB2/run_lr.sh (sha256 in run_lr.sh.sha256) on the FS1 pack + BB2 overlay (both
# sha256-checked by run.sh). The batch rule (BB2_BS / BB2_ACCUM) and --time are given on the sbatch command line
# (registered command, prereg section 9); this file is unchanged. A wrong or missing batch setting is refused at once.
# All IO in $TMPDIR; one result tar per fit to results/BB2L. A task whose verified tar exists exits at once.
# Optional BB2_TASKS="i j ..." (a registered rerun, prereg section 6): the array index picks from that list.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
case "${BB2_BS:-}/${BB2_ACCUM:-}" in 256/1|128/2) ;; *) echo "BB2 refuse: batch setting '${BB2_BS:-}/${BB2_ACCUM:-}'"; exit 1 ;; esac
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2
ARMS=(A B Sb A B Sb A B Sb A B Sb A B Sb)
SEEDS=(403 403 403 404 404 404 405 405 405 406 406 406 407 407 407)
I=$SLURM_ARRAY_TASK_ID
if [ -n "${BB2_TASKS:-}" ]; then read -r -a TL <<< "$BB2_TASKS"; [ "$I" -lt "${#TL[@]}" ] || { echo "BB2 no task for index $I"; exit 0; }; I=${TL[$I]}; fi
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
(cd "$P" && sha256sum -c --quiet run_lr.sh.sha256) || { echo "BB2L run_lr.sh off its sha256"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=BB2L_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "BB2 fit $ARM $SEED bs $BB2_BS accum $BB2_ACCUM job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
nvidia-smi --query-gpu=timestamp,memory.used --format=csv,noheader,nounits -l 30 > "$TMPDIR/gpumem.csv" 2>&1 &
# amendment 4, lead 13 Nov: first-step guard on the effective learning rates (static check, then the optimiser groups
# that train.py prints before step 1 must read LoRA 1.17e-05 and head 3.33e-05; otherwise the run is killed at once)
grep -q '^BB2_LR=1.17e-05 ' "$P/run_lr.sh" || { echo "BB2L_GUARD_FAIL run_lr.sh learning rate"; exit 3; }
WANT="('1.17e-05', 0.05, 96), ('3.33e-05', 0.05, 2)"
FL=$TMPDIR/fit.log; : > "$FL"
setsid bash -c "TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_fs.tar BB2_OVERLAY=$P/bb2_overlay.tar BB2_RESULTS=$L/results/BB2L \
  BB2_BS=$BB2_BS BB2_ACCUM=$BB2_ACCUM PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash $P/run_lr.sh" > "$FL" 2>&1 &
RPID=$!
tail -n +1 -f "$FL" &
TPID=$!
G=0
while kill -0 $RPID 2>/dev/null; do
  if [ $G = 0 ] && grep -q "optimiser groups" "$FL"; then
    if grep "optimiser groups" "$FL" | head -1 | grep -qF "$WANT"; then echo "BB2L_GUARD_OK learning rates $WANT"; G=1
    else echo "BB2L_GUARD_FAIL $(grep 'optimiser groups' "$FL" | head -1)"; kill -- -$RPID 2>/dev/null; sleep 2; kill $TPID; exit 3; fi
  fi
  sleep 5
done
wait $RPID; RC=$?
sleep 2; kill $TPID 2>/dev/null
[ $G = 1 ] || { echo "BB2L_GUARD_FAIL the optimiser groups line never appeared"; [ $RC = 0 ] && RC=3; }
[ $RC = 0 ] || { echo "BB2L fit failed rc $RC"; exit $RC; }
echo "BB2 fit end $ARM $SEED peak_mib $(cut -d, -f2 "$TMPDIR/gpumem.csv" | tr -dc '0-9\n' | sort -n | tail -1) $(date -Is)"
