# Independent AD5 interactive adapter review — 2026-11-14

Verdict: SOURCE_ONLY_REVIEW_COMPLETE; ACTUAL_MIGRATION_AND_EXECUTION_HOLD. The original PENDING-only transition is no longer applicable: root supplied a fresh coordinator snapshot at17:52:28Z reporting original6321768 FAILED1:0 at18:46:20CET, causeUNKNOWN. This reviewer did not query WCSS or inspect its raw output. No cancellation, automatic retry or interactive run is authorized by this review. Root's exact technical collection and independent failed-run diagnosis must precede any new execution disposition.

## Exact reviewed bytes

launch.py a269f5df5a6f9ddd4eee07a3291f8f071554e0b9d1261de24d64648558882ab4; worker.py0ce8edfd861098443c9008950d8ee3aff0396112353d64d6f5cacba2e1779ffd; amendment aae30f857471306af76e473bcbe76ef0742213c25c0d0e735d1a2d47959586e2. Independently matched remote hashes; author files unchanged.

Original workload e090bd45f69cbc30b58ac1faa5c711cde672a75d842e944e5882a1c0eb4e7f92 and instrumenter04668b872d83171bf7a2ae909a7955f266fd44b51237805e0b629e955b309f0f remain bound by the prior root release/commit2c6ee4ba675f45ceec60b6b00a4b29b02edbf1c7. Worker verifies these and code94964c…/wheels3bd18d…/croppedSMDD3189e5… full pack hashes. No pack/checkpoint contents were opened by this reviewer.

## Source and local mock findings

Both files pass independent AST parse/compile. Original workload passes bash-n. Inspected actual original workload and ROOT_AD5_FIRST_BACKWARD_RELEASE: seed401,ARM=B,SMOKE1, one first backward, no optimizer update/save/scoring. The script's historical12hourSBATCH directive is ignored by bash under srun; adapter explicitly requests15minutes, onehopper,8CPU,120G,150Glocal and FORCE_RM_TMPDIR. This does not become a full smoke or training success.

Local tests use temporary directories, transformed ROOT path and fully mocked subprocess/TTY calls; no tmux/Slurm/GPU process is actually executed. Seven branch cases passed: return0,return1,signal−15 with correct nativeexit preservation and no second invocation; started-source rejection; evidence-hash mismatch rejection; existing tmux pipe rejection with persistent claim; nonTTY rejection. Successful branches verify exact--pty,--immediate=60,--time00:15:00 and exclusion of injectedAD5_NG/EPOCHS/SLURM_JOB_ID/PYTHONPATH from launcher environment. Re-entry raisesFileExistsError before srun. MOCK_RESULTS.txt and mock_review.py preserve the harness/evidence; no worker execution is claimed.

Worker source preserves only nativeSLURM_*,CUDA_VISIBLE_DEVICES,TMPDIR,TERM plus explicit base environment and ARM/SMOKE/patcher/seed adapter. SLURM_ARRAY_TASK_ID401 is clearly seed input, not a fabricated native array; NODE_START records actualSLURM_JOB_ID and native_array=false. GPU count/partition/CPU assertions are useful guards but not evidence of memory/storage/time availability or actualH100 type. Those require native root checks.

## Race and release boundary

The proposed PENDING path is coherent only with root's native hold fence: exact owner/task reconciliation; controller-confirmed user-heldPENDING/zero priority/no start/no step; guardedscancel--state=PENDING; terminalCANCELLED plus never-started evidence BEFORE interactive allocation. A snapshot followed by unconditional cancellation would be unsafe and is expressly disallowed. RUNNING/COMPLETING/COMPLETED/started evidence forbids migration. FAILED is not CANCELLED_UNSTARTED and cannot be recast as it. Current FAILED notification therefore closes this path regardless of source correctness.

The launcher does not independently parse/prove native state: it trusts root-attested booleans and checks evidence bytes. It only checks independent_review_sha256 is nonempty, not the review file itself. Root's release audit must actually verify that review hash, source/adoption/commit and native records; do not claim the Python code proves those facts. No arbitrary cancellation capability exists in these files. They never query/cancel/requeue jobs. One-shotCLAIM plus unchanged create-only workload namespace guards duplicate launches, but cannot repair a false root attestation.

Site hold semantics, native task targeting, actual interactiveQoS/resources and future capacity remain unverified by this source review. No blanketGO for real migration. If a later independently approved plan again uses a pending transition, root must demonstrate these properties immediately before action or HOLD; a mock is not proof of site support. Current run needs failed-run disposition instead, not that pending transition.

## Durability and incomplete outcomes

Dedicated real tmuxPTY plus pipe-pane transcript allows disconnect survival; root must verify unique session and remain-on-exit. LAUNCH_INTENT/EXIT and NODE_START/EXIT are create-only/fsynced. --immediate60 is one actual workload allocation attempt, not a capacity probe/retry loop. No slot means explicitHOLD with native rejection/exit evidence, never automatic resubmission or relaxed resources.

NODE_START is written only AFTER workload/pack hashes. Thus absence of that file does not establish absence of an allocated/started native job; root must reconcile nativeID/steps/accounting even if srun fails before worker receipts. A pre-hash allocation receipt would improve observability in any future version, but is not present here. Launcher exceptions afterCLAIM may leave noLAUNCH_EXIT; TERM/SIGKILL can preventNODE_EXIT and ordinaryworkload preservation. These are incomplete diagnostics, not success. Original keep/log/sidecar receipts and batchfailed evidence must remain intact; no new namespace or deletion can silently bypass them. Root collection must verify durablecopy hashes and native terminal status.

Required next action now: collect only exact failed6321768technical logs/receipts, diagnose under its existing technical scope and independently decide whether any distinct retry is justified. Preserve this adapter as reviewed source-only material. If a new attempt is approved, use a new explicit preregistered disposition/release appropriate to FAILED history, retain the original failure and reevaluate exact resource/source/one-shot gates; do not manufacture MIGRATION_RELEASE.json with cancelled=true/ever_started=false.

No scheduler query, WCSS SSH, GPU, srun, sbatch, scancel, cancellation, inference, timer or source mutation occurred. This review used gx10 source/technical registration reads and local CPU mocks only. No scientific or publication permission is granted.
