# Proposed synthetic efficient-attention backward probe — new diagnostic

Status: SOURCE_READY_REQUIRES_INDEPENDENT_PRE_REVIEW_AND_ROOT_RELEASE. Author Astra. No GPU/scheduler/job/cluster execution performed. This is a new operation-localization experiment motivated by FAILED6321768, not migration/replay of its batch. All previous failures and firstbackward namespace remain intact.

## Source binding

New directory src/recovery_20261114/ad5_sdpa_probe_v1/:
- SHA256SUMS8138eb69a50c9724ca20417148e1b5373fd12d2e1c8d139710e8eb9b9bb54b5b
- probe.py98d13a375bc9d171307fba2596aa81cba4a9089a82643c7f38ccbe93d9eb7c8f
- worker.sh7c3b602bdf091bf4d593ed5d5c0c5874ecea10723538b4feb32f4d2df6b3a76d
- requirements.txt5b370b16905aba7465e5dffc79c42061e29298d1a55c996d62ec56e86dffe05d, exact source member from original codepack94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee.

Original wheel pack3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c unchanged; fresh scratch Python3.9 venv and same requirements as failed H100. Existing venv/package dirs preserved. No original codepack weights or image pack is staged/extracted by worker. Only exact requirements source was read during preparation. Context-manager signature verified directly in packed torch2.0.1+cu118 wheel torch/backends/cuda/__init__.py SHA50402c114760d90f8da2a5b5b1c2f954c0642c01aafb8eb036dadea0fdbdb3cf: sdp_kernel(enable_flash,enable_math,enable_mem_efficient). No recalled newer API substituted.

## Fixed diagnostic

Two fresh Python processes, in order default then math; failed first CUDA context is never reused. Torch CPU seed20261114. Independently generate three float32 tensors originally197×256×768 (B/16 registered224input =>197tokens,12heads×64width), then original view/transpose/view pattern to256×12×197×64. This shape/layout is inferred from registered architecture and exact LoRA source, NOT a capture of actual failing activations; emitted strides make it auditable. All q/k/v require gradients, representing a synthetic fully differentiable attention input, not exact first-layer gradient flags. Same generated upstream gradient in both processes, input/gradient hashes logged. No saved generated tensor payload required.

Call F.scaled_dot_product_attention with maskNone,dropout0,is_causalFalse, matching vision attention path. Default leaves backend flags unchanged; log actual autograd grad_fn to confirm whether efficient backend selected. Math uses enable_flash=False,enable_math=True,enable_mem_efficient=False only in this SYNTHETIC process. Synchronize before forward/after forward/after backward, anomaly tracing enabled check_nan=False. Record finite output/qkv gradients plus norms, package/device and exit status; no model, optimizer, image, checkpoint or performance score.

These tests do not prove numerical equivalence from norms/hash or prove training safety. They compare reproduction/completion under one prospectively specified backend intervention, without altering real training. No extra shape/seed/batch/precision/backend choices if outcome is inconvenient.

## Root execution package and resources

Stage exact new source dir as AD5/ad5_sdpa_probe_v1 on WCSS after independent GO and source/pack/hash checks. Worker is executable inside a NEW real interactive allocation and refuses non-PTY or non-lem-gpu-interactive. Unique create-only logs/keep/ad5_sdpa_probe_v1_20261114 prevents replay. Duplicate check is for THIS new scope; no cancellation of completed/failed original batch.

Root's new independently reviewed durable tmux launcher must use sanitized base environment (same HOME/USER/LOGNAME/PATH/SHELL/LANG/LC_ALL/TERM as original) and explicit command:

    /opt/slurm/current/bin/srun --immediate=60 --job-name=ad5-sdpa-probe-v1 --partition=lem-gpu-interactive --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=120G --gres=gpu:hopper:1,storage:local:150G --time=00:15:00 --extra=FORCE_RM_TMPDIR --pty bash /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_sdpa_probe_v1/worker.sh

Use actual tmux pane/PTY with durable transcript, one-shot intent/exit/native allocation receipts and root fresh resource/QoS/namespace checks. WCSS via gx10 shared flock only; no failed login retry. This note does NOT authorize old CANCELLED_UNSTARTED migration launcher, whose guard is correctly unsatisfied. Its durable-PTY pattern may inform a NEW launcher under independent review; do not edit its release boolean to pass it. Missing interactive slot => explicit NOT_ALLOCATED/HOLD, no auto retry/batch fallback.

Estimate environment setup~46s previously; two synthetic attention forward/backward likely minutes,15minute cap <=.25H100h. Actual peak/time unknown; source-derived synthetic shape intentionally fixed, so OOM is a retained diagnostic failure rather than license to shrink tensor. OneH100 only, no Athena/paid GPU. Local scratch only; worker builds same offline packages, no global install. Preserve logs incrementally after each process. EXIT/TERM trap collects technical files and hash manifest; SIGKILL can still leave partial logs. Root collects all files/native status/transcript with remote/local SHA and >=50GiB durable reserve.

## Acceptance and next branch

Worker exit0 means both subprocesses were ATTEMPTED and collected, not both passed. Review each default_exit/math_exit, phase marker, actual grad_fn, finite checks, identical input+upstream-gradient hashes, package/driver/device. If default selects EfficientAttentionBackward and reproduces illegal instruction while math completes finite: supports efficient-backend-specific failure on this synthetic shape and identifies math as candidate remedy. NOT production GO or full smoke pass. Next is prospective registered real-first-backward math-only comparison/equivalence criteria and complete gating smoke before any fit; preserve original recipe and disclose backend change.

If default succeeds, does not select efficient backend, or fails elsewhere: synthetic reproduction not established. Capture actual qkv shape/stride/dtype/gradient flags at exact sourcecall in a separately reviewed training-only instrumentation pass; no hidden retries. If both fail, inspect their first trace, environment/native stack; no blind upgrade. If math fails OOM, keep original shape/result; a separately reviewed alternate diagnostic is needed.

Local verification only: Python AST/compile PASS, bash-n PASS, exact requirements/source API checked; no torch import or kernel run. Another reviewer must inspect probe source assumptions, same-input generation, fresh-context behavior, shell failure collection and sanitized tmux launcher BEFORE root release. This prospective package is not self-reviewed GO.
