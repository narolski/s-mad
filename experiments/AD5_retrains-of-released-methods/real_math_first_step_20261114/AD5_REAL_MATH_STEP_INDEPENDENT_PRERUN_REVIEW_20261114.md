# Independent AD5 real math first-step prerun review — 2026-11-14

Reviewer: Astra / astra_sprint_plan_review, independent of Sol implementation.

**GO_CODE_AND_LAUNCHER_FOR_ONE_NEW_AD5_REAL_MATH_STEP_V1, conditional on the separate exact root release and native prelaunch gates below.** This is source/preregistration/launcher approval for one new technical experiment, not execution authorization, recovered training, scientific read, production or benchmark approval. No author source changed.

## Exact frozen package and independent checks

Source SHA256SUMS: 40e6cb24e6a97b87020f61d47f786024b7472d651a2dfd97620a5999fdc9c9f4. All 33 listed files independently rehashed successfully.
Immutable evidence manifest: 110d7f55a97e4a154a6727725892d921c00b22f4e2dde42d12a1b28abc50a91c. All 29 evidence entries independently rehashed successfully.
Preregistration: e1c3bf3a5f575a928d46f9390e57165cf7bc33b843cdc5b525fa2551f497adbd.
Handoff: a4e6eb5bbc694fb0a9b59faefbf015227a601b36ae9b4b5b83c02f6f2f3b30f5.
Exact trainer delta: 9b078b8de3303103dc37f909effbdf68f5c62c35461029480cfdc9455bfcd481.
Launcher delta: be49a4fad93f40f800a34a7a5a9ac455684ec7563ff1d03fec7e6729713687ff.
Original source trainer: e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d; resulting patched trainer: 199f2433a1242d91cc319ddf9f5ddc6d75e33092a2b3136d74a88be89088abfb.
Prior independent synthetic review: d3ecb92faeacbc262483481eba6137bfed67315d896d53d98cb346dead5b8abe.

Independently ran python3 src/recovery_20261114/ad5_real_math_step_v1/test_cpu.py: 12 tests PASS in 0.072 s. Independently parsed top-level Python AST and ran bash -n on worker.sh and allocation_entry.sh: PASS. Fixtures are generated/mocked, including executable shell early-ID failure73; no real torch/model/data/GPU invocation. Tests verify original two AdamW constructor ASTs, math scope, one backward/two clipping calls/two optimizer steps then return, gradient/update failure contracts, exact256 index order, five launcher outcomes, reentry/nonPTY refusal, clean node environment and missing/malformed receipt failures. Unsigned/wrong-scope release proposals reject.

## Model/training source assessment

Reviewed packed-source copies of original trainer, train/config, backbone, data loader, runtime observation and patch, rather than inventing model APIs. No standalone model-provenance archive was available; GROUNDING documents this limitation. The existing pack pins, not a newly read weight tensor, bind weights and original modifications: code94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee; wheels3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c; crops3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900. Reviewer did not reopen their weight/data bodies. Worker must independently hash all three complete packs BEFORE extraction; this runtime prerequisite is not represented as already completed here.

B/16 ARM B seed401, 3311-row every12th original list, original loader/transform and full256 effective batch remain fixed. FP32 input/targets/expected trainables and exact torch2.0.1+cu118, CUDA11.8, Python3.9, one H100 are runtime assertions. Original backbone converts half parameters to float32. No microbatch, reduced batch, altered optimizer, clipping order, loss, package or schedule substitution. Explicit torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=False) surrounds encoder/header forward and backward; backend flags are asserted inside. Clipping and original optimizer_model.step then optimizer_header.step remain outside and in original order. The unconditional return occurs before original poststep logging/callback/scheduler/evaluation/save paths. Outer train.main only destroys the process group after start_training returns; AD5_NO_TEST empties evaluation datasets at configuration time.

Probe verifies exact48 visual q/v LoRA trainables and2 header tensors, each gradient present and finite before clipping, and finite parameters with optimizer step1 after updates. Individual zero A gradients are valid because B initializes to zero; all-zero or all-unchanged groups fail. Fresh optimizer states are asserted. First batch IDs and ordered indices are observed from the original loader; sampler replay uses its own generator and asserts unchanged global RNG. This checks index/label order, not byte-identical stochastic augmentations or numerical equivalence to the failed default run. Background prefetch and original nondeterministic runtime behavior remain original; do not describe the observation as proof of bitwise reproducibility. Original backward could not complete, so backend-gradient equivalence is unavailable.

## Launcher, retention and remaining root gates

New dispatch/keep/source namespaces only. Real tmux PTY is required, pipe transcript and remain-on-exit installed, fsynced exclusive CLAIM precedes allocation. Exact srun requests lem-gpu-interactive, one task/node/H100 hopper,8CPU,120G,150G local,15min, --immediate=60 and --pty. Allocation shell writes and syncs native ID before Python; shell fake-Python73 fixture confirms preservation. Clean environment excludes inherited PYTHONPATH/PYTHONHOME/AD5_NG. Node checks partition, CPU, memory, one device and local TMPDIR; native runtime assertions enforce H100. Missing allocation ID is UNKNOWN_REQUIRES_ROOT_RECONCILIATION, never proof of no allocation. No cancellation, old-job migration, fallback or retry exists. Old6321768_401 and synthetic6323083 are untouched.

The worker preserves technical JSON/text/logs and status through EXIT trap and hashes the durable copy. Startup failures before that trap remain visible through dispatch/native/terminal records; hard kill or storage failure can prevent a complete keep archive and must be classified INCOMPLETE, never inferred PASS. STEP_RESULT plus worker/node/native outcomes and retained finite-gradient/update records are necessary for eventual technical PASS. Node refuses worker0 with missing/malformed success receipt. --immediate60 is not a bound on the whole CONFIGURING phase, as prior actual probe demonstrated. Native resource/time/capacity and local-storage allocation must be checked by root; this source review did not query the site.

At review, source/evidence namespace is untracked in Git. Root must commit exact owned source/prereg/evidence without unrelated changes; verify clean owned paths and staged native hashes; bind this review as source and launcher review (same independent combined report is acceptable), actual commit proof and fresh native site/capacity/storage proof into a new ROOT_RELEASE.json. Proposed release is unsigned/nonexecutable and correctly fails. Root must verify the evidence content, not just file existence/hash. Require durable free space>=50GiB as registered and original packs present/unchanged; do not infer quota from requested150G. Preserve permanent claim and reconcile any unknown allocation before further action. No revised source is needed for this scoped review; any later source change voids these pins and needs a delta review.

## Interpretation boundary

Synthetic default failed efficient SDPA backward while math completed. This justifies one new real-model technical test, not an automatic retry of failed training. A successful full real first step would establish only that the registered forward/backward/clipping/two updates complete with finite expected trainables under math-only on the pinned setup. It would not establish full training recovery, speed feasibility, backend equivalence, root cause, model utility or scientific performance. Failure/OOM/timeout remains a retained outcome; no smaller batch or longer run is preauthorized.

No WCSS login/query, scheduler operation, GPU/model/data/weight load, candidate/sealed read, score export, source edit or execution release was performed by this reviewer.
