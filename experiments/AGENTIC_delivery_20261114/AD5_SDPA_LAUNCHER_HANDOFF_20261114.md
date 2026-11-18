# NEW synthetic SDPA: durable PTY launcher handoff

Status: READY_FOR_INDEPENDENT_LAUNCHER_REVIEW; EXECUTION_HOLD. Astra authored this launcher addition; a different reviewer must approve exact bytes before new root execution release. Source/design review7d2b92f9f814a35608abc26870609f8bee421788067225fd9e008aaa2df3a45e granted preparation only. Original probe/worker/requirements manifest8138eb69a50c9724ca20417148e1b5373fd12d2e1c8d139710e8eb9b9bb54b5b unchanged. No cancellation/migration logic; FAILED6321768 is preserved and never touched.

## New source pins

src/recovery_20261114/ad5_sdpa_launcher_v1/SHA256SUMS644ea85a9d6308c6362e7c138fa7aec85f452217e338742abbe24ae15a3e47ce
- launch.py df9d6544e9169c049a317c0b50aefe33add924c95a945d9e4eab3c20596aba04
- allocation_entry.sh b6077a9ae271e5e99f3195498fae87b646aec30b383c05cbe24f1dd8c09db29c
- node.py e316761f11995870c85b4cf993be150b444433c03987934ee31eb537f9b4ecee
- test_mock.py4a8c2d6577b38ef1d3f9255975cec4e2757d843f40a1bfccae12a0ce9450a693

No original source edited. All Python AST/compile and bash-n PASS. Four generated-only test methods pass, including five launcher scenarios(normal completion,capacityfailure,timeout/nonzero with allocated ID,workerfailure,launch exception), four backend-exit combinations, re-entry, non-PTY refusal, and a real generated shell wrapper with a fake python executable returning73. That last test proves native ID is persisted BEFORE Python/worker startup failure and noclobber rejects re-entry. Tests invoke no real tmux,Slurm,GPU/model or candidate data; launcher subprocesses are mocks. They do not establish actual site scheduling or SIGKILL durability.

## Staging and root release

Stage new sources under /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_sdpa_launcher_v1 and unchanged probe at sibling ad5_sdpa_probe_v1. New journal AD5/dispatch/ad5_sdpa_launcher_v1_20261114 must be created once by root for pinned evidence and ROOT_RELEASE.json; worker keep namespace logs/keep/ad5_sdpa_probe_v1_20261114 must not exist. No actual staging or namespace allocation on WCSS performed here.

ROOT_RELEASE.json fields, all required:
- decision GO_ONE_NEW_SYNTHETIC_SDPA_INTERACTIVE_V1;scientific_read HOLD;automatic_retry false;root_authorized true;distinct author/reviewer.
- probe_manifest_sha2568138eb69…;launcher_manifest_sha256644ea85a….
- source_design_review_sha2567d2b92f9…;prereg_sha256d1d028032773f68541515cbd982c741ee031ef60cb5dc7ffb36be95416f6092a.
- For source_design_review,prereg,launcher_review,owned_source_commit_check,site_preflight: <key>_file basename of copied evidence in journal and <key>_sha256. Exact file bytes checked; launcher review hash supplied only after independent review.
- owned_source_clean_committed true;durable_free_gib>=50;old_failed_job6321768_401;old_job_action NONE.

Root is responsible for truthful native evidence: reviewed owned source/input paths committed+clean, actual staged hashes, partition/QoS/resource availability and no conflicting allocation/session/job for THIS new scope, durable space. Attestation does not mean source itself queries/commits/schedules to prove these fields. Launcher hashes full exact wheelpack3bd18def… before allocation; node worker hashes it again. No model/image packs involved. Root alone uses gx10 flock /tmp/opencode/wcss-client.lock for a single WCSS session and no failed-login retry.

## Concrete root command after independent GO and release

Use dedicated tmux session, absent beforehand; an existing name is HOLD, never killed/reused. From WCSS login shell after explicit root checks:

    tmux new-session -d -s ad5-sdpa-v1 'python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_sdpa_launcher_v1/launch.py'

tmux creates actual controlling PTY; launcher asserts stdin/stdoutTTY and TMUX_PANE. It verifies release/source/pack pins before writing/fsyncing permanent CLAIM.json, then enables remain-on-exit, installs independent pipe-pane terminal.log, writes INTENT.json and calls srun directly without stdout pipe/redirection:

    /opt/slurm/current/bin/srun --verbose --immediate=60 --job-name=ad5-sdpa-probe-v1 --partition=lem-gpu-interactive --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=120G --gres=gpu:hopper:1,storage:local:150G --time=00:15:00 --extra=FORCE_RM_TMPDIR --pty /bin/bash /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_sdpa_launcher_v1/allocation_entry.sh

The only addition to prereg's direct worker command is a source-bound allocation receipt wrapper. It writes+syncs NATIVE_JOB_ID.txt and emits an ID marker BEFORE starting Python. node.py then verifies realPTY/nativeID/partition8CPU/oneGPU/TMPDIR and exact unchanged worker hash; writes NODE_START; invokes /bin/bash <unchanged probe>/worker.sh. It does not alter the synthetic operator or worker arguments. Independent reviewer must approve this launcher-level wrapper change.

Launcher srun environment is exact clean HOME,USER,LOGNAME,PATH,SHELL,LANG,LC_ALL,TERM. Node forwards only native SLURM_*,CUDA_VISIBLE_DEVICES,TMPDIR,TERM plus that clean base. No AD5_NG/ARM/EPOCHS/PYTHONPATH/PYTHONHOME or backend overrides leak. Native allocation supplies TMPDIR; prior local TMPDIR is not forwarded. Root verifies native actual memory/storage/time/GPU allocation rather than treating environment assertion as full scheduler proof.

## Receipts, failure and no-retry semantics

Journal: ROOT_RELEASE+evidence,CLAIM,terminal.log,INTENT,NATIVE_JOB_ID,NODE_START,NODE_EXIT,TERMINAL. NODE_EXIT preserves default/math exit text separately even when workerexit0 and one/both backends failed; missing status explicit incomplete. TERM/timeout from native scheduler can prevent NODE_EXIT, but early nativeID and worker incremental durable statuses/transcript remain. TERMINAL records srun exit and native ID, never an operatorPASS.

--immediate60 bounds allocation waiting. Capacity rejection without ID is UNKNOWN_REQUIRES_ROOT_RECONCILIATION, not fabricated NOT_ALLOCATED: root must inspect verbose transcript and native scheduler state using unique jobname/time/user to prove no allocation. If allocation exists but wrapper never started, transcript/native reconciliation is mandatory to obtain its ID/terminal state before any future action. Native ID is guaranteed by wrapper only once it starts, not under arbitrary scheduler/node launch failure; no software can promise a missing native response.

A claimed failed/timeout/capacity attempt is permanent. No re-entry, hidden retry, auto batchfallback, resource relaxation or cancellation of old job. If launch.py exits after claim with caught exception, TERMINAL preserves error. AbruptSIGKILL/hostloss may leave CLAIM with no terminal; this is unresolved and requires root reconciliation, never automatic retry. Dedicated remain-on-exit pane and durable pipe transcript make disconnect survivable; verify pipe transcript/receipts rather than assuming tmux existence means success.

Root collects entire journal+worker keep logs/hashmanifest+native accounting state/exit/start/end to fresh /mnt/t7 directory with>=50GiBfloor, compares hashes/sizes, preserves failed attempts. Separate post-result review checks actualbackend,source/runtime/device,inputhash equality, both per-process statuses and finite phases. Worker/srun0 means collection/completion, NOT operatorPASS/training smoke or production admission. Scientific and baseline read gates unchangedHOLD.

## Remaining action

Independent reviewer inspects source/release boundary, actual tmux/srunargv, native-ID-before-worker path, mocked unavailable/failure/timeout/reentry branches and immutable worker hash. Root then adopts exact launcher+new release and performs one actual scheduling decision. Author performed no WCSSlogin, schedulerquery, GPU/submission/cancel, or timer installation.
