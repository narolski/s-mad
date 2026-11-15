# Proposed AD5 first-backward diagnostic — prospective registration

Status: CODE READY FOR INDEPENDENT REVIEW; not submitted/admitted. Supersedes earlier speculative clipping-probe branch. Original failures preserved. Training-only technical localization, no detector comparison, checkpoint saving, optimizer update or score read. Owner root executes; Astra authored package and cannot pre-review it independently.

## Fixed scope and inputs

One original MADation B smoke seed401, one H100, unchanged first batch256 from original reduced training list, original LoRA/float32/loss/preprocessing/package recipe. Existing ad5w_code.tar94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee, wheels39 and croppedSMDD sidecars retained. Root must verify exact wheel/data sidecars and code hash against collection before staging. No architecture, batch, precision, clipping, attention backend or package switch. Launch-blocking/CPPstack/faulthandler retained.

Sources:
- src/recovery_20261114/ad5_backward_instrument.py SHA25604668b872d83171bf7a2ae909a7955f266fd44b51237805e0b629e955b309f0f
- src/recovery_20261114/ad5w_firstbackward_diagnostic.sbatch SHA256e090bd45f69cbc30b58ac1faa5c711cde672a75d842e944e5882a1c0eb4e7f92
- Original packed trainer e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d; instrumented f9cfa6bcd457e21cf449c917621dd40c0122da6ea712355f74fd8380a53104f0.

Instrumenter only accepts exact trainer and single exact first training block, compiles replacement, writes scratch source. It wraps original encode/header/backward in detect_anomaly(check_nan=False), synchronizes before forward/after encoder/after header/after backward, prints shapes/dtypes and backend enable flags (NOT proof which kernel selected), and exits immediately after first backward. No tensor values/images/loss/scientific metrics are printed by added instrumentation. Existing training diagnostic logging stays training-only AD5_NO_TEST=1. No checkpoint deserialized during package preparation; actual run uses original admitted training base weights as existing smoke does.

## Execution and resources

Script is derived from reviewed launchblocking smoke, requires ARM=B and array seed401, uses fresh output namespace madation_B_s401_smoke_diag_firstbackward_20261114 and refuses existing keep directory. All computation/venv/source overlay in TMPDIR. Never mutate existing venv/packs.

Root after commit+independent GO, exact remote hash and duplicate/namespace check may use normal WCSS batch:

    cd /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
    /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR --partition=lem-gpu-short --gres=gpu:hopper:1,storage:local:150G --array=401 --cpus-per-task=8 --mem=120G --time=00:15:00 --export=ALL,ARM=B,SMOKE=1,AD5_BACKWARD_PATCHER=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_backward_instrument.py --job-name=ad5w-firstbackward ad5w_firstbackward_diagnostic.sbatch

Unset inherited AD5_L,AD5_PYTHON,AD5_NG,EPOCHS and any environment overrides before execution; root binds admitted environment just as prior smoke. Hardware/environment unchanged. Expected startup~1minute then first batch failure/success;15minute limit/0.25H100h maximum, estimate not measured for anomaly mode.

Consider lem-gpu-interactive explicitly: current owner record says srun --pty ONLY, not sbatch. Root must verify actual PTY/allocation limits and use a durable logged interactive launcher with equivalent resource/time/env settings and SLURM_ARRAY_TASK_ID=401. Do not simply put --partition=lem-gpu-interactive on sbatch. This package is directly batch-executable; interactive adapter must be separately reviewed before use. No new scheduler query here. WCSS connection only via gx10 flock /tmp/opencode/wcss-client.lock, no failed-login retry. Athena is not an equivalent reproduction of H100 illegal instruction; no A100 substitution now.

## Artifacts and acceptance

On training subprocess return, copy+cmp train_stdout.log,gpumem.csv,pip_freeze.txt,instrumentation.json,child_exit.txt into create-only Lustre keep directory, write SHA256SUMS. Root then durable-copy/checksum to /mnt/t7 (>=50GiB floor), retain native scheduler receipt and all failures. Partial early startup/timeout remains failure; outer scheduler stdout and retained TERM logs must also be collected. Script's prior training result packaging is unreachable for fixed B diagnostic path.

Diagnostic success means either:
(A) reproducible illegal instruction with anomaly's forward operation trace plus last completed phase and exact package metadata, sufficient to choose a narrow synthetic kernel reproduction; or
(B) explicit AD5_BACKWARD_DIAG_COMPLETE_NO_UPDATE and childexit0, recorded as first backward completed under instrumentation, NOT smoke pass or production release.
Failure without informative trace is retained as inconclusive. No automatic rerun or proposed cure from lack of reproduction.

If anomaly localizes an SDPA backward operation, next prospectively pin a synthetic tensor-shape/dtype/stride reproduction of that observed operation in fresh processes. Only THEN compare fixed default versus explicit math backend as diagnostic. A backend/package fix needs independent prospective equivalence/design review and actual complete gating smoke before production. If another operation appears, diagnose that operation instead. Never disable clipping as response to this evidence.

## Local checks and remaining gates

ASTRA_AD5_BACKWARD_PACKAGE_CHECKS_20261114.json records exact packed trainer patch+compile/AST and bash-n. Final sbatch also bash-n PASS after create-only/durable-copy checks added. No GPU/environment execution was performed; runtime compatibility/durable behavior still require reviewer inspection and actual diagnostic. No missing model source collection is required: exact packed code is present and hash-equal. Independent reviewer must inspect shell error/timeout preservation, source overlay invariance, export sanitization and no-test/no-update endpoint before root launch.
