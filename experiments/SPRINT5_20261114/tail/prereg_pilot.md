# Genuine-tail continuation [SPRINT5-3]: bounded three-arm fit pilot

Prospective, 14 November 2026, before intervention fits or candidate reads. MAD22-informed new cycle outside NEXT. This supplements `prereg_baseline.md`, which fixes the training-only anchor/reference pass. No benchmark is opened and seeds413–417 remain reserved.

All arms begin from the same pinned H100 AB1 Sb seed408 LoRA/head checkpoint, with the same FS1 backbone/base weights. Seeds521–525 describe conditional continuation and sampler/dropout variability, not five independently trained backbones. Scoped seed audit and lead reservation are required before fitting. One last checkpoint per arm/seed, no ensembles or picking seeds.

## Fixed arms and common training stream

Three arms: BCE; BCE plus mean camera-negative penalty and positive-family constraints; BCE plus CVaR camera-negative penalty and the SAME constraints. This is end-to-end LoRA/head continuation, not NE1 group-head refitting. The mean arm controls simple score lowering.

Each effective batch has256 rows, with exactly128positive rows (32distinct contributing-identity-pair units per each of af0_u50, af0_u5061, lad_R4, lad_S4),118camera negatives (32distinct identities in each of the three large source/processing groups, ALL22identities in FRGC/s61), and10other protocol-negative controls. Within an identity/unit choose one existing unique variant uniformly; each step samples new units without replacement within the step. The ten controls are sampled without replacement within the step. Every selected row already exists in the pinned Sb training manifest; no new image or transform is constructed.

The entire100-step plan is deterministic per seed and byte-identical across the three arms. Thus total rows, source/processing/class/family shares and EACH image's exposure count are exactly equal across arms. This deliberately stratified stream changes the original Sb prior; the BCE arm controls that change. Remaining training images need not all appear in this small pilot, but no arm receives extra images/exposure. Actual full-data plan checks for all five seeds are saved in `CPU_REAL_SAMPLER_SMOKE.json`.

Each fit:100optimizer updates×256=25600image forwards, accumulation1, no extra encoder forward for tail loss. Same FS1 CLIPViT-B/16 LoRA q/v rank2, alpha4, rsLoRA, dropout.4, frozen norms, encoder LR3.33e-6, headLR3.33e-5, AdamWwd.05, constantLR, label smoothing0, BCEposweight1, pureflip and gradient clipping5. No hyperparameter/step search or early stopping. This is a bounded training-continuation pilot, not a convergence claim.

## Objective and state

Use the exact admitted training-only reference JSON before any fit. Optimization anchor is its source-balanced training camera identity-logit95%quantile, not an evaluation threshold. Camera groups contribute equally; within each group, identities contribute equally. Non-camera protocol negatives remain in BCE but have label-1 for the auxiliary objective and cannot silently enter the camera tail.

Mean penalty is.1times mean camera softplus(z-anchor), averaged by identity and equally by source/processing group. CVaR replaces each group mean with eta+meanReLU(loss-eta)/.1. Initialize eta from the fixed baseline's training camera identity-loss90%quantile. A separate Adam optimizer withLR.01 updates eta; it never inherits the encoder LR. The22-person group therefore has an empirical2.2-person10%tail; this is explicitly reported rather than hidden behind an arbitrary minimum population. Larger groups use32identities/step and have3.2-person empirical tails. Record actual identity-tail occupancy every step.

For each of the four positive families constrain the identity-pair mean softplus(-(z-anchor)) to its frozen baseline training reference+.02. The same nonnegative dual rule applies to mean and CVaR: current dual enters the loss; after the complete effective batch's model/eta optimizer step, update dual by.01times violation and clamp[0,10]. Commit once per effective step with a monotone step counter. Forward does not mutate dual state. BCE has no auxiliary penalty or dual updates.

Store full trace of eta, identity counts, tail occupancy, violation and dual, plus final objective/eta-optimizer state. Save detector last checkpoint and ordinary metadata independently. Warmstart trainable names must exactly equal the reference trainable names; baseline reference SHA must match actual checkpoint bytes and training-group metadata.

## Execution gates

First a two-step real H100 smoke runs ALL THREE arms at521 using the same stratified rows and common warmstart, with full existing opaque development scoring and mandatory strict battery byte gate. Check all camera/positive groups are present, finite loss/eta/dual, actual tail occupancy, correct positive-gradient constraint behavior on step2, identical plan receipts, durable checkpoint/state/hash preservation and all21277own-fit dev logits byte-identical. The reference2496-row gate must be byte-identical; tolerance is not success.

Both smoke and pilot require independently reviewed JSON receipts binding idSPRINT5_3, decisionGO_SMOKE/GO_PILOT, source SHA256SUMS, distinct reviewer/author, exact independent review hash, seeds521–525/fresh allocation, and the admitted baseline archive path/SHA256. Pilot additionally requires three verified smoke archives and byte-gate/H100 passes. Runtime independently rechecks this receipt before training. Missing/failed baseline archive, nonfinite state, incomplete arm or failed gate means hold. Keep every failure and never replace seeds, delete an output or retry automatically.

Leader alone dispatches. Stage source at `$G/packs/SPRINT5_3_v1/source`; smoke actualPTY uses one H100,8CPU64G,200Gscratch,2hours; normal-short pilot array0–14%1 requests one H100,8CPU64G,100Gscratch,1hour/task. Resource estimates are prospective; use measured smoke timing before pilot. No paid H100 or Athena login retry.

## Prespecified scientific read and limits

No scientific candidate read is performed by these runners. Historical191ladder rows are opaquely preserved only for the existing path/platform checks; no new191-host inference is released. Still-sealed external benchmarks are excluded by exact existing manifest allowlists and pinned packs.

Primary descriptive pilot contrast: CVaR minus mean on genuine false alarms at thresholds set on INDEPENDENT positive calibration persons for90%sensitivity. Heldout positive-family sensitivity must be reported jointly with each source/processing genuine false-alarm rate; show simultaneous2percentage-point noninferiority guards as a utility check. Calibration/person partitions and confidence multiplicity must be pinned before candidate access. Also report frozen baseline-threshold results, score quantiles and AUC, so uniform score shifting is visible. BCE versus mean is a prespecified control, not an alternative winning arm selected post hoc.

Use person-component and matched-seed bootstrap, resampling calibration components in their own partition, with10000draws and numpydefault_rng2026111403; publish all seed effects and failures. Exact component graphs, source cells, guard family and confidence method remain reader-admission gates before score access. This pilot is descriptive: inadequate NI precision or no gain remains a valid outcome, and no result licenses adopting a successor or opening a benchmark. All statements condition on the shared seed408 warmstart and small empirical tails.
