# Genuine-tail continuation [SPRINT5-3]: training-only reference pass

Prepared prospectively on 14 November 2026. This is a new MAD22-informed cycle outside NEXT. The author authorized implementation of this direction; the lead specifically authorized preparation of a training-only reference pass and bounded common-warmstart pilot. Independent review is still required before the GPU command.

This amendment replaces the earlier draft's independently calibrated optimization anchor with a **training-only anchor** for a limited continuation pilot. It does not replace the independent evaluation calibration or permit an adoption claim. All three eventual arms will start from the SAME existing AB1 Sb seed408 checkpoint. Later seeds521–525 describe continuation/subset/dropout variability conditional on this checkpoint, not five independent full training replications. Seeds413–417 remain protected.

## Exactly what this pass does

Use pinned H100 reference `AB1_Sb_s408.tar`, SHA256 `a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa`. Load its actual meta/LoRA/head through the unchanged battery backbone loader and exact pinned FS1 common/model/base weights. Use H100, torch2.11.0+cu128, float32, TF32 on/on, batch64, no augmentation. First reproduce the reference's2496-row byte gate and all21277 own development logits byte-for-byte; these are opaque platform checks under the lead's existing historical191-row ruling, with no scientific interpretation of those rows.

Then score ONLY the5535unique rows of the original training Sb manifest, as ordered in `training_identity_groups.csv`. All paths must begin `train/`; no validation, still-sealed benchmark or external-evaluation image is selected. Save training-only logits and derive algorithm constants directly on GPU-side output. The owner does not interpret or select a detector using these logits. This narrow training-score computation is explicitly part of the authorized preparation; it is not a read of historical sealed train90/val10 result archives.

Camera-genuine rows are exactly `af0_photo`, `af0_photo61`, `lad_R0`. True texture-identity counts in source×processing groups are colorFERET/native467, colorFERET/s61220, FRGC/native170, FRGC/s6122. The last group's empirical10%tail is2.2identities, a finite-population limitation to report; no arbitrary80-identity admission bar applies. Other protocol negatives stay in the common training stream but do not silently enter the camera-tail objective. Four positive families: af0_u50, af0_u5061, lad_R4, lad_S4.

## Constants frozen before intervention fitting

For camera negatives average logits within identity×source×processing. Give each of the four groups total weight1/4, each identity equal weight within its group. Anchor is the first observed identity-mean logit whose sorted cumulative weight reaches.95. This is a training optimization anchor, not an evaluation threshold.

At that anchor, compute per-camera-image softplus(z-anchor), average within identity/group, and initialize each group's CVaR eta to the90%linear quantile of those identity means. Eta has its own Adam optimizer at learning rate.01; it must not inherit the tiny encoder learning rate. For each positive family, average softplus(-(z-anchor)) within each contributing-identity-pair and then equally across pairs. These four fixed means are the training detection-surrogate references, each with epsilon.02. Pin every constant and source hash in `TRAIN_ONLY_reference.json` before any intervention fit. No output-dependent retuning of q=.1, tailweight=.1, dualstep=.01, dualcap10 or epsilon.02.

The objective forward must not mutate dual state. After the entire effective batch and its backward/optimizer step, commit the aggregated positive-family violation ONCE, with a monotone effective-step counter. Record eta, actual identity-tail occupancy, violations and dual values. The prototype has separate tests for these behaviors; full trainer integration and GPU smoke remain separate gates.

## Output and failure policy

No intervention is trained by this command. Output is a durable verified tar with platform gate, training-only logits/reference, exact source receipt, status and logs. Fail closed on any byte-gate or input failure; retain unique failure archives and durable outer logs. No automatic overwrite or reuse. Missing/failed reference preparation holds every intervention arm.

Package `src/SPRINT5/tail_baseline/`, staged to `$G/packs/SPRINT5_3_baseline_v1/source`. G=`/lustre/pd03/hpc-narolski-1790461090/smad-next`. Review receipt `TRAIN_BASELINE_RELEASE.json` must bind source SHA256SUMS, exact independent review bytes, distinct author/reviewer, idSPRINT5_3, decisionGO_TRAINING_BASELINE_ONLY and scope`training-only anchor/reference, no intervention fit or scientific dev read`.

Leader-only command after independent review, using a real PTY and current QoS:

```bash
/opt/slurm/current/bin/srun --partition=lem-gpu-interactive --nodes=1 --cpus-per-task=8 --mem=64G --gres=gpu:hopper:1,storage:local:100G --time=01:00:00 --extra=FORCE_RM_TMPDIR --pty bash /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SPRINT5_3_baseline_v1/source/run.sh
```

No paid H100 or Athena retry. Follow the shared WCSS lock for contacts; persistent PTY orchestration and scheduler status belong to the lead. No command has been submitted by this owner. The future three-arm100-update warmstart pilot will receive its own pinned sampler, source, seed audit, registration and independent review before execution. A favorable small pilot cannot adopt a successor or open a benchmark.
