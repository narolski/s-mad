# Paired splice ranking [SPRINT5-1]: handoff

Status: CPU smoke PASS; independent bounded GPU-smoke review pending final signature. No GPU job submitted by this owner. Production and candidate read HOLD. New MAD22-informed cycle outside NEXT; seeds413–417 untouched.

Code: `src/SPRINT5/paired_ranking/`. Registration and metadata evidence: this folder. Durable source tar `/mnt/t7/smad_next/SPRINT5_1/source_v1.tar`, SHA256 `c783c6c0abbc8bea35755554a7a95aa3f42f964f206b5c4c9fb17eadf2d3a25f`. Internal SHA256SUMS digest `162b2846eed036aecae33adf3cb973abaa4dfdc5db5940ea01db02906df2f8ae`.

Verified: all15 production index plans exact1.6M exposure equality across3arms; paired schedules identical; actual8development training images load at224; expected opposite rank gradients; no-pair differentiablezero; d0 val10 rows0; seed501 two-step smoke pair counts5/4. Metadata allowlists: dev21277,tt134411,meds1018,gd11042; primary200splice rows/100development hosts. Scoped prior registration/source seed audit found0allocations for501–505; leader must cross-check concurrent allocations and bind. This is not a universal scheduler-history proof.

## Leader staging and exact smoke

Leader only: through the existing shared WCSS lock transfer the source tar into `$G/packs/SPRINT5_1/source_v1.tar`, where G is `/lustre/pd03/hpc-narolski-1790461090/smad-next`. Verify tar SHA above, extract into new `$G/packs/SPRINT5_1/source/`, verify `(cd .../source && sha256sum -c SHA256SUMS)`. Existing input packs remain unchanged; runner pins all pack hashes and train/eval manifests. Required pre-existing packs: BB2/pn1_pack_fs.tar, AB1/ab1_overlay_v2.tar, BATTERY/battery_code_v1rc1.tar, TT1/tt1_pack.tar, BB2/tt1m_meds.tar, BB2/pr1_gd.tar and reference results/AB1/AB1_Sb_s408.tar.

Run in a real PTY (e.g. leader's persistent tmux session) after independent smoke GO:

```bash
/opt/slurm/current/bin/srun --partition=lem-gpu-interactive --nodes=1 --cpus-per-task=8 --mem=64G --gres=gpu:hopper:1,storage:local:80G --time=02:00:00 --extra=FORCE_RM_TMPDIR --pty bash /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SPRINT5_1/source/worker.sh smoke
```

Interactive admission is not guaranteed; do not submit sbatch on interactive. Current cluster access/QoS is leader's responsibility. No retries after failed login. The worker executes3arms at seed501,2steps each, full existing scorer and mandatory byte-gated battery, no scientific score report. Logs go directly to results/SPRINT5_1/logs; successes to results/SPRINT5_1/smoke. Run.sh persists failure archives/logs and any checkpoint before normal nonzero exit; scheduler SIGKILL can defeat traps, so preserve external job/PTY status too. Existing result paths refuse overwrite/reuse until explicit reconciliation. Keep logs and status until durable verified recovery.

Leader should preserve the outer srun return status and job ID in a durable receipt after tmux ends. Internal workers return nonzero on any failed arm/battery. Failed battery still copies the checkpoint/full ordinary result before returning nonzero. Do not interpret smoke scores. Independently verify GPU/environment, finite rank/BCE and pairs5/4 in log, all3archives and battery byte identity before production.

## Production receipt and unresolved gates

Production.sbatch has15tasks,3h each,normal short partition,%1; use only after measured runtime and independent GO. Source verifies PRODUCTION_RELEASE.json schema: idSPRINT5_1,decisionGO_PRODUCTION, distinct reviewer/author, fresh_seed_allocation_pass=true,h100_smoke_pass=true,byte_gate_pass=true,seeds501–505,source_sums_sha256,independent_review_path+sha256,seed_audit_path+sha256,smoke_archives with arm/path/sha256 for all3arms. These files/paths must exist on WCSS and match exact staged bytes. Receipt is generated and reviewed by the leader; no permissive template is installed. A pathname alone cannot unlock fitting.

Before production: finish exact D/person components/pair provenance and independent floor population/calibration pins; enumerate multiplicity guard family and calibration order-statistic uncertainty; verify fresh allocations against concurrent work; finalize source after any fixes and rerun review/smoke as needed. Before read: implement/review permanent once-only reader with all15eligibility gates. No method/adoption result follows from the package alone.

Retained: sources, metadata scope receipts, full CPU test evidence and source tar. Nothing was deleted. Existing unrelated dirty tree remains unchanged. No sealed benchmark, challenger score, external dataset or candidate checkpoint was opened.
