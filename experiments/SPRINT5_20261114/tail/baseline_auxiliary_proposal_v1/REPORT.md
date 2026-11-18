# Required tail baseline-threshold auxiliary: source/metadata proposal

This is coverage closure for a previously registered auxiliary, prepared **after the primary pilot results were read and independently reviewed**. It is not a new model/data/threshold search and does not turn the negative pilot into permission for a retry. The completed primary result and permanent claim remain unchanged.

The original pilot preregistration required frozen-baseline-threshold reporting. The adopted pre-read policy fixes the same 70 positive calibration IDs of the one admitted Sb408 baseline, distinct from the TRAIN_ONLY optimization anchor. Its per-model threshold rule is strict `score > nextafter(sorted_positive[floor(.10*n)], -inf)` in float64. This proposal does not choose another baseline, threshold, positive pool or seed.

## What is verified now

`prepare_metadata.py` is candidate-free. It verifies the committed original tail input binding/source, then maps exactly 538 ordered IDs to the original 21,277-row AB1 evaluation manifest: 70 calibration positives, 180 held-out positives and 288 genuine rows. ID/path/label and native/processing provenance match. For every selected input image, actual file SHA256 matches the FS1 or AB1 overlay checksum table; duplicate captures are retained. Calibration/evaluation source-person/photo/component separation is inherited and revalidated by the exact adopted input loader.

Baseline location: `/mnt/t7/smad_next/AB1/results/AB1_Sb_s408.tar`, admitted archive SHA `a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa`. The source-established member is `AB1_Sb_s408/scores_eval.npz`, field `logit` (float32 original no-TTA logit, not score_TTA/probability). The original scorer writes ordered manifest IDs and its manifest SHA. Source runner uses the exact original FS1/AB1 packs. Whole-archive pin plus exact member name fixes a viable immutable reuse target, but is not a fresh observed payload/schema pass.

Current baseline access was limited to filesystem stat and the already-admitted sidecar. **No baseline archive bytes/member, NPZ, score, checkpoint or image decoding was accessed.** Source image bytes were hashed only. No reader, auxiliary collector, model, GPU, scheduler or claim was run. No independent checkpoint or whole-baseline-archive rehash is asserted.

## Remaining concrete HOLD

The exact baseline member digest, unique regular member, actual NPZ manifest/ID ordering, full 21,277 finite logits and selected 538 IDs have not been inspected here. `baseline_score_member_sha256` is null rather than guessed. Existing root training-reference and strict own-fit/reference gates support no-GPU reuse; they do not silently admit this auxiliary payload.

A separate reviewed metadata-only baseline admission can inspect only fixed technical JSON/TXT members and opaque member digest/header, after an explicit root release. A subsequent auxiliary-only scientific release would permit baseline 70-calibration plus 468-evaluation values and candidate evaluation-only values. No checkpoint load or fresh inference is needed. A missing/mismatched member/ID/byte gate holds the auxiliary; this proposal does not automatically rescore or switch archives.

The earlier registration does not fully specify auxiliary uncertainty treatment or authorize an alternate claim after primary completion. `ASTRA_PLAN_REQUEST.json` identifies those exact questions. Any completion policy adopted now must be labelled as a clarification after primary outcomes were seen, preserving its pre-existing auxiliary requirement. This proposal does not label new point-only/CI choices as pre-read preregistration.

## Mathematical code proposal

`kernel_proposal.py` has no file I/O, reader, RNG, model or journal code. Generated arrays only are tested. It computes one original Sb408 threshold from the exact 70 scores, then all 15 candidate fixed-threshold rates and the baseline's own rates on the six fixed genuine cells and all four positive-family slots. Missing AF0-s61 stays missing; no proxy, zero sensitivity or NI pass is invented. Both prespecified paired contrasts and all seed values remain visible.

Companion own-recalibrated values must come from the pinned, already completed primary result. The kernel does not recompute primary calibration, bootstrap, NI, diagnostics or a winner. Auxiliary uncertainty remains explicitly unresolved pending independent policy review. There is no actual-data entry point or read release.

If allowed by independent review/root adoption, an auxiliary adapter must use a **separate auxiliary-specific journal and release** fenced to the exact completed primary claim/result, never rerun or replace the primary and never create a second primary claim. No auxiliary journal is selected/created by this proposal. A future immutable implementation/version would bind exact technical metadata, baseline/candidate members and IDs, source manifest, policy adoption, independent review and the completed result hashes before any auxiliary payload access.

Expected work after the missing admissions is CPU-only: one small baseline NPZ and the 15 already available candidate NPZ members, with opaque archive hashing dominating I/O. A prospective estimate is minutes rather than GPU hours; it is not a measured runtime promise. Utility is transparent coverage of score/threshold movement at the original fixed operating point, not rescue of the pilot or an adoption criterion.

## Verification

Six synthetic tests pass: exact n70/index7 and strict tie handling, one common threshold across all 15 candidates, missing family retention, both paired contrasts/no threshold selection, nonfinite/shape rejection and no RNG/primary recomputation. Run only the generated fixture command:

```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SPRINT5/tail_baseline_aux_proposal_v1/test_synthetic.py
```

Preparation never overwrites an existing proposal. Its completed metadata artifact is `experiments/SPRINT5_20261114/tail/baseline_auxiliary_proposal_v1/INPUT_BINDING_PROPOSAL.json`. Scientific auxiliary read and camera remain HOLD.
