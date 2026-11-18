# Astra compute unblock plan — 2026-11-14

Bounded planning task, source/metadata inspection at 14:22 CET. No GPU work, cluster login/mutation, package change, score-archive opening or failed-run deletion. Lead alone submits. This is a proposed execution plan, not independent run admission.

## Immediate decisions

1. Collect and independently admit completed IDistill diagnostic6319494 before spending another GPU minute. COMPLETED alone is insufficient.
2. Read first synchronous traceback from MADation6319495_401 before proposing a training repair. Its FAILED status is not a diagnosis.
3. Keep five completed OCC1 models for independent numerical/print review. For B/L, register an instrumentation-only diagnostic in current local environment; do not rerun full sweeps or change tolerances.
4. A small WCSS synthetic kernel probe is straightforward to package now. Athena is conditional on association/duplicate checks. OCC1 cluster transfer is NOT currently ready: its prereg prohibits copying/exporting FERET pixels and permits in-place local analysis.

## Sources and pins

Read mambamorph AGENTS.md/CONTINUE and CLAUDE.md; requested smad-next/CLAUDE.md is absent. Read smad-next notebook, WORKSTREAMS, recovery registrations and scripts, OCC1 prereg/source/pins/failure receipts, figures handoff and compute policy/snapshots. Repository HEAD observed 78490ba27a148cce2545041fea51cfd53746721d is a snapshot, not a claim all worktree files are committed.

Verified SHA256:
- src/recovery_20261114/clip_grad_probe.py: 7a8201f67ee73f3c757b7c033dea7cb52b2c09e249cf8285641a78d38cd77279
- src/recovery_20261114/ad5w_launchblocking_smoke.sbatch: a1faf156564b3e98ce3e3c61bc3012d2a6bae48dee07a49215f1cb47dd28d37e
- src/recovery_20261114/cb1_idistill_waitfix.sbatch: 24304001f933259ffdb82f50695719f1ad82233b65def8e50c876ba871c4b541
- experiments/OCC1_seam-surround-pilot_20261114/prereg.md: e57b042df42fcfe6f0d261b2d7995d1d8699594638e39c72a4d15e11f57c484a
- same folder INPUT_MODEL_PINS.json: 42f6f16c17a34b501dbb87ce98872186a6ffcb3510743a95ede29a9eda9057d4
- src/OCC1/occlusion_runner.py: 2d89d00054bdcae2a4f3f99b791b8af6280f702d3ea071a876b0307f8388776a

OCC1 official-release weights B ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f and L bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980 are distinct from AD5 retrained networks. Their failure modes must not be conflated.

## First lead action: one technical collection, zero GPU

Reuse any newer cached collection. My bounded filename search through depth5 under /mnt/t7/smad_next found no 6319494/6319495/launchblocking/waitfix-named files; this is not proof no cached log exists.

Use one WCSS connection from gx10 under flock /tmp/opencode/wcss-client.lock to batch accounting/current queue for6319494,6319495,6312778 and matching recovery names; technical smoke logs; tar/sidecar sizes/hashes/member names; current lem-gpu-interactive limits/QoS and GPU availability. No failed login retries across accounts/hosts. Scheduler outage means unknown state.

IDistill stdout can contain Lowest EER and other model metrics: expose only allowlisted architecture/matmul, worker-exit, DONE and error markers. Store raw log opaquely if necessary; do not print metric lines or extract score payloads. MADation AD5_NO_TEST=1 training-only traceback and retained train_stdout.log may be inspected to identify failure. Collect pip_freeze and original path/timestamps. Verify archive SHA remotely and after durable copy to /mnt/t7. No smoke replay while receipt exists.

14:08 metadata says IDistill6319494 COMPLETED0:0 in3m11s; MADation6319495_401 FAILED1:0 in1m30s. These are historical accounting observations, not new live polls.

## IDistill acceptance and production disposition

Original bare wait included infinite GPU monitor; waitfix records worker PIDs, checks their status and reaps only its monitor. Actual smoke pass requires all of: COMPLETED/0, fresh DONE idistill_all_smoke_waitfix_20261114, verified durable tar+sidecar, workers401/402/403 exit0, nonempty expected best/valbest/last checkpoint and score-file members, no unresolved subprocess error, original H100 architecture/runtime checks. DONE alone is insufficient: source packages/prints DONE before final FAILED check can exit4. Inspect existence/hash, never metric contents.

Preserve original smoke TIMEOUT and prose deviation: implemented workload2 AE epochs/256BF and6 classifier epochs differs from original1epoch/64images. If independent technical review passes, no additional smoke is needed. Existing production6312778 remains unadmitted: reviewer must explicitly accept an unchanged-output operational salvage exception, otherwise outputs remain diagnostic and fixed production is rerun. Never choose disposition using scores.

Before interruption identify current phase/worker PIDs; preserve all .pt/.pt.valbest/.pt.last, logs, crops/latents and opaque score files to verified durable archive. Only after every classifier/scoring worker exits may lead stop the exact owned monitor, documenting before/after. Do not kill unrelated controllers.

Fresh production if required: pinned waitfix, new unique CB1_RECOVERY_TAG, unchanged seeds/settings, separate pre-run review. Estimate walltime from full production phase timings; three-minute smoke does not prove <=6h. H100 stays WCSS; use normal eligible partition when >6h. No epoch truncation or unregistered resume. A100 port requires environment/hardware amendment and true smoke. Preserve existing venv/wheelhouse.

## MADation training: smallest discriminating diagnostic

Read6319495 first. Original asynchronous report: illegal instruction at clip_grad_norm_/_foreach_norm on torch2.0.1+cu118/H100; later SIGABRT was cleanup. Do not assume synchronous failure is identical.

If it still implicates clipping, or remains inconclusive, run existing clip_grad_probe.py --foreach default, true, false in THREE FRESH PROCESSES in one15minute H100 allocation. Keep Python3.9, AD5 wheel pack and packages exact; record wheel hashes, pip_freeze, torch/CUDA/arch/driver/GPU and per-mode command/exit/stderr. Probe uses no model/data/checkpoint. Wrapper must preserve failed mode status and continue other modes; failed CUDA contexts must never be reused. Current registration describes this optional synthetic isolation; write/pin the execution wrapper and obtain independent pre-run GO before submission.

Proposed WCSS envelope: --partition=lem-gpu-interactive --gres=gpu:hopper:1,storage:local:150G --cpus-per-task=8 --mem=120G --time=00:15:00 --extra=FORCE_RM_TMPDIR, no requeue/exclusion.120G follows existing AD5 envelope, not a measured minimum. Verify live partition/QoS compatibility before dispatch; choose a smaller measured resource requirement if necessary and record it. Execute entirely in TMPDIR, preserve logs to Lustre then verified /mnt/t7 copy. Estimated <=0.25GPUh including environment startup, not guaranteed.

Decision tree:
- default/true fail, false passes: evidence of foreach-path issue only. Register foreach=False code amendment with unchanged clipping formula. Prospectively bind synthetic clipped-gradient/norm equivalence checks/tolerances; then real gating smoke. Probe success never admits production.
- all pass: synthetic LoRA-shaped tensors did not reproduce failure. Add synchronize checkpoints after forward/backward/unscale/norm/clip/optimizer in original training-only first update, log gradient dtype/shape/nonfinite counts, no images/values. One reviewed instrumented smoke, <=15min expected. No blind repair.
- earlier operation fails: build smallest synthetic reproduction for that operation; do not substitute a clipping workaround.
- all fail: investigate architecture/native stack in a NEW isolated environment directory; preserve existing packages. Any package/environment change needs prospective amendment, independent review and actual gating smoke.

Once supported repair exists, repeat true B gating smoke; L must pass its own real configuration/memory smoke before L production. Preserve seeds401–405, epoch40 last checkpoints, global batch256, optimizer/loss/augmentation. No smaller batch, AMP/TF32, favourable-seed replacement or fewer epochs. Derive production GPU count/time from measured successful smoke and original registration. >6h means normal WCSS partition. Check Athena arrays3545814_[401–405],3545813_[402–405] before dispatching any A100 equivalent; stale pending metadata is no reason to duplicate/cancel.

## OCC1: diagnose B numerical parity and L placement separately

B source raises before recording offending rung and batch discrepancy. Current receipt has no magnitude. L traceback reaches model.to(dev), before inference; allocation pressure is plausible, but asynchronous CUDA reporting prevents a proven root-cause claim. Smaller occlusion batch alone does not fix placement OOM.

Prospective instrumentation amendment + independent pre-run review, then lead release:
1. Create new diagnostic source/run root; original failures/inventory unchanged. Pin new runner/dependencies. Keep all8 images, same checkpoints/adapters, FP32/noAMP/TF32off/eval/noTTA, original1e-5 repeat/no-op and1e-4 batch parity bars.
2. Log GPU total/free/used and own allocated/reserved/peak, host available RAM, parameter/buffer byte counts and dtype histogram, package/driver/device identity before load and before/after model.to. No global cleanup, process termination or environment change.
3. L fresh-process placement-only diagnostic with launch-blocking and synchronization. If available memory is insufficient, record BLOCKED and await a free slot; do not invent smaller precision/model. On unified-memory hardware record host and CUDA availability. No sweep.
4. B fresh-process all8 baseline/repeat/no-op/batch8 diagnostic, saving per-rung values/max discrepancies BEFORE gate enforcement. Record identical batch slots. Continue baseline diagnostic collection for all fixed rungs but final status FAIL if any gate fails. No occlusions/full sweep. Expected seconds/minutes; reserve<=15min/model locally, one model at a time.
5. If B still fails, fixed small synthetic-input CPU/GPU batch1vs8 reference can distinguish model batch dependence from kernel rounding. Any deterministic math/attention implementation experiment must first be supported by source inspection, prospectively fixed and independently reviewed. Do not search implementations on actual effect maps until one passes. FP64 or batch1-only would be a different protocol, never a pass of current OCC1.

If original bars pass in prospectively declared implementation, real smoke then full1024occlusions/model (8rungs×2fills×64patches). Initial full reservation<=1h/model, revise from actual smoke. Numeric-only outputs, create-only durable directories, >=50GiB free. Five completed models need independent review, not recomputation.

### Conditional cluster port

Athena A100 is sensible for additional memory only after requested association is visible and FERET placement is authorized. Current OCC1 explicitly forbids copies/exports and specifies in-place inputs; general compute permission does not silently remove that restriction. Do not stage FERET/source/occluded images now. A permitted existing on-cluster copy with verified provenance, or separately documented rights-consistent transfer disposition, is necessary.

ARM local venv cannot be copied to x86 as working environment. Pin separate compatible x86 package environment, preserve original. Amend hardware/environment and root mapping: runner hardcodes /mnt/t7 free-space test and absolute paths. Verify all8 preprocessing tensors exact; unchanged numerical gates on destination. Allowlist only admitted checkpoints/code; never copy entire mad22_production_cpu_stage payload containing unrelated data.

Conditional envelope after review: Athena1A100,8CPU,64–96GiB host RAM,150GiB local scratch,30min smoke then<=1h/model full. Verify actual GPU capacity/free-memory fit. WCSS1H100 can substitute after same port gates, lem-gpu-interactive<=6h subject live limits. No paid H100. Athena last saved14:00 association unavailable; approved project name does not establish usable Slurm access. No invented account switch.

## Ready versus blocked

READY now without GPU: collect technical metadata; independent IDistill smoke review; five-model OCC1 numerical/print review; package synthetic probe wrapper. Existing code pins above are concrete, but new wrapper and diagnostic source are not yet authored/reviewed.
NEEDS prereg/review: AD5 instrumentation/foreach/package changes; IDistill salvage exception or rerun disposition; all OCC1 retries and platform/batch/precision changes.
BLOCKED: synchronous MADation diagnosis until log collected; Athena requested association until visible; OCC1 cluster images until placement/rights resolved; production score release until admission.

Lead records intent before submit, exact source/config/input/env hashes, duplicate check, native job receipt, unique durable output root. Independently verify technical acceptance before next step. Keep every original failed attempt. No smoke-derived scientific conclusion, weakened tolerance, sealed-read expansion or automatic retry is authorized by this plan.
