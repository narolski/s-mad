# Independent synthetic SDPA postresult review — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of probe/launcher author.
Job6323083. **Technical collection/integrity PASS. Default backend FAILED; math-only synthetic operator PASS.** No model-training, backend-equivalence, production-fix or scientific-result approval.

## Exact evidence

Collection /mnt/t7/smad_next/coordination_20261114/sdpa_probe_result_collection_20261114T190258Z/COLLECTION_VERIFIED.json SHA256 b9d333300b5013818b1f1ca9910d0219b47aab16b5fc77a71e295af2e15fe39c.
All25 collected files independently rehashed with exact sizes; all worker SHA256SUMS entries independently matched. Worker result manifestcf69efac62747e25fdf29880efd95057cf300444bd61837d80d6f41e73e96967.
Independent SDPA_SYNTHETIC_POSTRESULT_CHECKS_20261114.json SHAce17910cb3e285cb87d07f98af7d03b2d8c12943e78699111fe90321f8ede2f9.
- Default loga575a01095e0eff592034178764132c1ca33e015d8827c23c20419db66badff1.
- Math logebe750a368098ac73ac451c6cf927bda54971b2d4ced13edcf6c0df5df89392d.
- Root released411bee5965641b72ae9fa004a7438e4fe4d6c5739c16647759e74663b8fd4ae.
- Claimdc20fb448c1f2756bebfcc69eed819c63927676df614129a726d371805982f98.
- Terminal22f8ef99b409a2d93963faee0fc166a9e514c0ad9cb934f527d34691b4cdf355.
- Probe manifest8138eb69a50c9724ca20417148e1b5373fd12d2e1c8d139710e8eb9b9bb54b5b, worker7c3b602bdf091bf4d593ed5d5c0c5874ecea10723538b4feb32f4d2df6b3a76d, launcher644ea85a9d6308c6362e7c138fa7aec85f452217e338742abbe24ae15a3e47ce, release source commit7364262b68e8d1d94e2d0e7b5026c6d28b1f3aeb.

Claim binds exact root release; all copied review/prereg/owned-source/site-evidence hashes match it. Native transcript records actual --pty, resource request, controller jobID6323083, configuration wait, node launch and native-ID marker before worker source/pack checks. NODE_START includes native PTY fields and sanitized environment, no PYTHONPATH/PYTHONHOME/AD5_NG. Fresh worker processes and source assertions establish the reviewed paths; individual process PIDs were not separately recorded.

## Resources and runtime

Collected native accounting: COMPLETED0:0,19:54:59–19:56:17CET, elapsed1m18s,8CPUs,one hopper GPU,120G memory,one node. NODE_START confirms8CPUs,122880MiB memory,one CUDA device, interactive partition and local /mnt/lscratch/slurm/6323083. Transcript explicitly requests150G local storage and15minutes; native start/end-limit environment spans900seconds. Accounting excerpt does not independently enumerate granted storage capacity, so150G is verified as requested, with local TMPDIR use observed—not a measured storage-quota claim. Long CONFIGURING wait is distinct from78second recorded allocation runtime; --immediate60 did not mean the entire configuration phase was capped at60seconds.

Device NVIDIA H100,95830MiB,driver595.112.07. Both process records show torch2.0.1+cu118/CUDA11.8; pip freeze agrees. Probe's assertion and traceback path support Python3.9. Synthetic source seed20261114, not training seed401.

## Separate backend findings

Both fresh processes report identical three input hashes and upstream-gradient hash40c992fbe828c4954020f2a9353696bdada8cf90a6e1c9c70dcce377812cd196. Shape256×12×197×64, all three strides[768,64,196608,1],float32,maskNone,dropout0,noncausal. These are source-inferred synthetic tensors, not captured training activations.

Default exit1: INPUTS_READY and synchronized FORWARD_OK, grad_fn ScaledDotProductEfficientAttentionBackward0. Failure occurs at probe.py y.backward(grad), with CUDA “an illegal instruction was encountered”; stack names at::native::_efficient_attention_backward and _scaled_dot_product_efficient_attention_backward_cuda. No BACKWARD_FINITE record. This reproduces the efficient-SDPA-backward failure class described in the original AD5 diagnosis using synthetic inputs; it is not a different setup/import/OOM failure.

Math-only exit0: INPUTS_READY, FORWARD_OK (UnsafeViewBackward0), BACKWARD_FINITE. Output norm722.824951171875; q/k/v gradient norms706.9850463867188,711.9714965820312,721.8033447265625. Source verifies every output and each input gradient is finite after synchronization. Input records match default exactly except mode.

NODE_EXIT correctly retains default1/math0 despite worker0; srun/accounting0 describes wrapper completion, never both-backend success. Both outcomes and default traceback must remain visible.

## What follows and what does not

Evidence supports a backend-specific workaround hypothesis for this exact H100/runtime/layout: math-only completes the synthetic forward/backward while default selects efficient attention and fails. It does not isolate driver versus compiler/kernel/runtime cause, prove every shape/dtype works, compare default/math numerical gradients (default has no completed gradients), establish model-level correctness, or show improved detector utility. No model/data/weights were loaded by this probe. Do not label it AD5 training recovery or resubmit old FAILED6321768.

## Concrete next registered test — source preparation only

A separate producer should prepare a new immutable real-training first-step smoke, independently reviewed and separately root-released before any GPU. Preserve exact original admitted B/16 model/source/weights/data/preprocessing, ARM B,seed401,global256,float32,LoRA/head configuration, loss, optimizer and deterministic first effective batch. Sole computational intervention: explicit torch2.0.1 SDPA context enable_flash=False,enable_math=True,enable_mem_efficient=False around the relevant training forward/backward; no package upgrade, reduced batch, microbatch substitution, dtype change or altered loss. Context placement must be source-derived, tested and pinned; do not patch frozen original artifacts.

Register one effective training step only (forward, full backward, existing clipping and one optimizer update) with the same≤15minute1H100/8CPU120G/150Glocal envelope, pending fresh root native capacity validation. If resources/time fail, preserve failure; no silent smaller-batch or longer-run retry. Pre-run CPU/source review must verify exact one-change diff, original source/weights/input pins, no extra scorer, deterministic first-batch IDs, effective batch count, dtype and trainable parameter names.

New permanent journal/namespace, same durable actualPTY/early native-ID discipline, strict no-overwrite, no automatic retry; original failure and synthetic result remain intact. Record actual backend control, full batch/header, finite loss, finite expected trainable gradients before clipping, global gradient norm, finite updated trainable tensors, update completion and runtime/peak memory. No metric evaluation or benchmark scoring. Missing expected gradients, nonfinite values, OOM/timeout/illegal instruction are explicit failure/incomplete outcomes, not a production exception.

Passing that new independently reviewed smoke would establish only that one real effective training step completes under math-only in the pinned environment. Full fit/rescoring/bytegate/production admission would remain separate. This report supplies a bounded preparation plan, not implementation approval or execution authority.

No GPU, WCSS login/query, scheduler operation, cancellation, inference, model/dataset/weight read or scientific benchmark access was performed by this reviewer.
