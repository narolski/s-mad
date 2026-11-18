# Proposed resource-only AD5 first-backward migration

Status: CONDITIONAL HOLD FOR INDEPENDENT PRE-RUN REVIEW AND ONE ROOT DECISION. This is scheduling migration of the SAME diagnostic, not a retry of failed job. Original6321768_401 was PENDING in last supplied snapshot; no current scheduler state was queried here. If it has started or completed, keep original batch and DO NOT execute this adapter.

Prepared by Astra. Another agent must independently review these sources and race/receipt rules before root adoption. No GPU, srun, sbatch, scancel, scheduler query or WCSS login performed by author. Only gx10 source/technical receipts inspected. No timer/monitor installed. Existing partial files from interrupted turn were checked and retained, not recreated.

## Scope and exact pins

Original registration/review/launch commit2c6ee4ba675f45ceec60b6b00a4b29b02edbf1c7 remains binding. Workload and instrumenter bytes unchanged:
- ad5w_firstbackward_diagnostic.sbatch e090bd45f69cbc30b58ac1faa5c711cde672a75d842e944e5882a1c0eb4e7f92
- ad5_backward_instrument.py04668b872d83171bf7a2ae909a7955f266fd44b51237805e0b629e955b309f0f
- codepack94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee
- wheels393bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c
- croppedSMDD3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900.

New source files src/recovery_20261114/ad5_interactive_v1/:
- launch.py a269f5df5a6f9ddd4eee07a3291f8f071554e0b9d1261de24d64648558882ab4
- worker.py0ce8edfd861098443c9008950d8ee3aff0396112353d64d6f5cacba2e1779ffd
- SOURCE_CHECKS.json records AST/compile only, no import or execution of either launcher.

Basis: inspected actual prior successful SPRINT5_3 launch_smoke.sh and SPRINT5_1 launch_smoke_v3.sh from /mnt/t7, both use real srun--pty on lem-gpu-interactive with durable start/exit logs. This adapter adds a one-shot claim, root cancellation evidence, exact source and pack checks, clean environment, dedicated tmux transcript and node/job receipts. Existing Sol review da355e… covers batch only, NOT this new adapter.

Only partition/allocation interface changes: lem-gpu-short batch array to lem-gpu-interactive actual srun PTY. Retain one H100,8CPU,120G RAM,150G local,15minute limit, FORCE_RM_TMPDIR, ARM=B,SMOKE=1, seed401, original first training batch, recipe/stack/code packs. No learned optimizer update/save/scoring; optimizer objects constructed as original. No backend/precision/batch/gate modification. No paid capacity.

## Root transition protocol: fail closed on races

All WCSS contact must be a single root-controlled session from gx10 under flock /tmp/opencode/wcss-client.lock. No failed login retry. Root reconciles actual job identity/owner/array task against SUBMISSION_RECEIPT.json; never act on a name wildcard or stale snapshot. The adapter itself does not query or cancel jobs.

1. Before ANY cancellation, independently review/commit/stage exact adapter, workload and patcher hashes; verify original source/pack sidecars and archives against ROOT_AD5_FIRST_BACKWARD_RELEASE_20261114.json. Check actual interactive partition/QoS/resources permit8CPU120G150G/oneH100/15min and no conflicting user interactive allocation. Inspect current capacity but do not claim future availability. Check >=50GiB durable reserve, requested session/journal absent, original workload keep namespace absent. Have one-time root decision accepting loss of queue position if no immediate interactive allocation follows. No allocation reservation/dummy job is permitted.
2. Fresh native state must identify6321768_401 as PENDING, elapsed0, no start/step/output. RUNNING,COMPLETING,COMPLETED or any evidence of start => NO MIGRATION; preserve original and collect/review its outcome. Unknown/unavailable/inconsistent state => HOLD. A prior failure/cancel state also requires a separate disposition; this migration does not automatically retry it.
3. Fence the PENDING job before cancellation: root issues `scontrol hold 6321768_401`, then obtains fresh controller state proving SAME task still PENDING with user-held zero priority/reason, no Start and no step. This hold prevents subsequent scheduler launch while cancellation is being verified, assuming sole root controller under shared lock. If hold fails or state is running/started, DO NOT cancel. Do not release/alter a running job to force this migration. If a hold was applied but migration aborted, root explicitly decides whether to release its own hold on still-pending job; no automatic release loop.
4. Only after confirmed held-PENDING does root issue guarded `scancel --state=PENDING 6321768_401`, retaining exact stdout/stderr/time/exit. Wait for native controller/accounting confirmation of terminal CANCELLED for exact task and absence of active steps. Verify Start remains Unknown/None and elapsed0; preserve pre/post raw technical evidence. A zero scancel exit or missing squeue line is NOT confirmation. If state lags/unknown, stop before interactive start. If accounting reveals actual start or namespace appeared, STOP and investigate, even if final status is CANCELLED: no duplicate diagnostic.
5. Only verified unstarted cancellation permits root to write create-only MIGRATION_RELEASE.json and start one interactive attempt. This document does not treat check-PENDING→unconditional-scancel as race-safe. If site cannot prove held-PENDING semantics/controller state, NO-GO: leave original batch. Root must not cancel first and investigate eligibility afterwards.

The human-readable command sketches in steps3–4 deliberately require exact native task identity verification. Root uses /opt/slurm/current/bin/{scontrol,scancel,sacct,squeue}; no bare Slurm PATH assumptions. No command in this plan was executed by author.

## Concrete staging/launch interface

Stage new sources unchanged at /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_interactive_v1/. Keep original workload at its original reviewed location. New create-only journal directory AD5/dispatch/ad5_firstbackward_interactive_v1/ stores root evidence and launcher logs; it is distinct from batch submission receipt. Original workload keep namespace remains unchanged, since changing it would change reviewed script; cancelled-unstarted batch must not have created it. The exact script's mkdir guard still prevents competing starts.

Root MIGRATION_RELEASE.json must contain:

    {
      "decision":"GO_ONE_INTERACTIVE_AFTER_CANCELLED_UNSTARTED",
      "original_job":"6321768_401",
      "native_cancelled":true,
      "ever_started":false,
      "root_authorized":true,
      "independent_review_sha256":"<exact new independent review hash>",
      "source_hashes":{"launch.py":"a269f5df5a6f9ddd4eee07a3291f8f071554e0b9d1261de24d64648558882ab4","worker.py":"0ce8edfd861098443c9008950d8ee3aff0396112353d64d6f5cacba2e1779ffd"},
      "evidence_hashes":{"<root native held-pending evidence filename>":"<sha256>","<root native terminal cancellation evidence filename>":"<sha256>","<native no-start/no-step evidence filename>":"<sha256>"}
    }

Filenames are basenames within journal, never paths/traversals. This is a root-attested operational release with hash-bound native evidence, not a source parser that independently proves Slurm state. Reviewer/root must inspect native records; fabricated/self-filled booleans do not satisfy protocol. Bind independent review+resource checks in root decision receipt alongside it.

After all gates, root creates a dedicated tmux session on WCSS login host with a real pane/TTY and executes python3 -I <staged>/launch.py. Use a unique session name ad5-fb-int-v1 and verify no prior session; never reuse/destroy another owner's pane. launch.py asserts actual stdin/stdoutTTY+TMUX_PANE, atomically creates CLAIM, refuses existing tmux pipe, creates terminal.log, installs tmux pipe-pane, writes LAUNCH_INTENT, then invokes:

    /opt/slurm/current/bin/srun --immediate=60 --job-name=ad5w-firstbackward-interactive-v1 --partition=lem-gpu-interactive --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=120G --gres=gpu:hopper:1,storage:local:150G --time=00:15:00 --extra=FORCE_RM_TMPDIR --pty python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_interactive_v1/worker.py

No pipe/redirection between srun and PTY. tmux transcript captures output independently, allowing SSH disconnect without losing the controlling pane. Root should configure remain-on-exit for this pane/session so exit remains inspectable; do not create polling daemon. Log files, not pane lifetime alone, are receipts.

Launcher environment is a clean explicit HOME/USER/LOGNAME/PATH/SHELL/LANG/LC_ALL/TERM map matching original submission base. Worker preserves only native SLURM_*,CUDA_VISIBLE_DEVICES,TMPDIR,TERM plus that base and explicit ARM/SMOKE/patcher/SLURM_ARRAY_TASK_ID401. The last is seed adaptation only; native interactive job is NOT an array and retains its actual SLURM_JOB_ID in NODE_START. Legacy AD5_L/AD5_PYTHON/AD5_NG/EPOCHS overrides are absent. Worker asserts interactive partition,8CPU,one exposed CUDA device,TMPDIR,realPTY; verifies workload/patcher and all three fullpack hashes before exact bash invocation. Root still verifies actual native allocation memory/storage/time/GPUidentity; environment assertions alone do not establish those quantities.

## Unavailable slot, timeout and durability

--immediate=60 bounds allocation wait; it is not a dummy probe, it requests this actual workload once. If no allocation, record native rejection/expiry plus LAUNCH_EXIT with node_started=false; original remains deliberately CANCELLED_UNSTARTED. Do not auto-retry interactive, requeue original, submit batch or weaken resources. Root chooses a separately documented later scheduling disposition. If interactive job id exists despite missing NODE_START, root must reconcile it and its terminal state before any later attempt; absence of marker is not proof nothing ran. CLAIM persists after any launcher error and prohibits silent re-entry.

Normal worker writes NODE_START(native job/environment), invokes exact workload, then NODE_EXIT. Launcher writes LAUNCH_EXIT. Normal workload preserves five technical files+SHA256SUMS through existing copy/cmp path. Original startup/TERM/SIGKILL preservation limitations remain; native timeout/failure and missing logs are explicit incomplete diagnostic, never success. No callback/loop executes another attempt.

Root collects native allocation/accounting IDs/state/start/end/exit plus whole new journal and original keep logs opaquely/technically to new /mnt/t7 coordination directory, checks SHA+size and >=50GiB reserve, preserves old submission/cancellation records. Native old batch outcome is CANCELLED_UNSTARTED_FOR_RESOURCE_MIGRATION, never FAILED. Interpret trace only after independent post-run technical review. No scientific read/admission is released.

## Remaining review gates

AST/compile PASS only; no mocked tmux/srun or cluster execution claimed. Independent reviewer must test create-only failure/re-entry and sanitized-env handling with mocks, inspect root release schema/evidence boundary, confirm srun option validity and hold-fence protocol for site's actual Slurm, inspect tty/transcript retention and native ID receipts, then issue exact source-bound GO or fixes. Missing site support, inadequate resource limits, unprovable cancellation/start state or any changed source => HOLD/NO-GO, not improvisation. Root can preserve existing batch while this review runs; no reason to cancel merely because preparation exists.
