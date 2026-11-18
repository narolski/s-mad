# Independent numerical and interpretation review: seven-model XAI pilot

14 November 2026. Reviewer Astra, independent of runner and result author. **GO for displaying the completed real per-image responses and local-sensitivity maps as a private descriptive pilot, subject to the caption limits below. No population, causal-shortcut or detection-improvement conclusion is approved.** This review reads only the specifically authorized pilot outputs; no closed scores, candidate archives or benchmarks were opened. No inference was rerun.

## Bound output package and independent verification

Root: `manuscript_cvpr2027/figures/shortcut_attribution_20261114/`.

- `OUTPUT_MANIFEST.json`: SHA256 `4b8c99c4879b70a0fedb7cb5e5ec013c9a904f0d1657bc1cbfaf55bec975600d`.
- `per_image_scores.csv`: SHA256 `4dd8aebf658dc23d8620a1ff5771a2e0292d7afb1b0f777eef818b62bb3c1c09`.
- Seven completed models, three fixed conditions each, 21 raw map files. Independently verified all 119 manifest-file sizes/hashes and both preserved failure hashes. Checked all 21 CSV rows exactly against their result JSON, including noTTA/TTA scores and native-relative logit changes.
- Independently read every raw NPZ and verified finite arrays, exact gradient-times-input multiplication, signed channel sum, sum of absolute channel attributions, raw-gradient magnitude and exact shared three-condition maximum scales. Checked ordered native/storage/border coverage, COMPLETE status, head-zero PASS and the registered finite-difference acceptance rule for every condition. Sigmoid/logit consistency passed.
- All six `_fp32` models are complete. `Sb_fp64` is complete at result SHA256 `8144971373e3fa5386f2a508f75fff49efc56e747b18294c6232246fea862c68`. Original `A/` and `Sb_fp32/` failures are preserved and excluded. Accepted precision repairs were reviewed before execution; epsilons and tolerances were not relaxed.

“Passed numerical gates” means the prospectively fixed rule: at least one of the two epsilon checks passes, alongside parity, finite-gradient and algebraic-head checks. It does **not** mean both epsilon checks always pass. In Sb storage, epsilon0.001 still fails, while epsilon0.0001 error is0.001942 against the unchanged tolerance0.014945 and passes. Preserve this detail; numerical checks do not establish explanation faithfulness.

## Descriptive response transcription

Attack-oriented noTTA logit changes relative to native, rounded for display:

| Model | Storage change | Border change |
|---|---:|---:|
| A_s403 | -0.00890 | +0.08784 |
| B_s403 | -0.12748 | +0.19893 |
| Sb_s403 | -0.23933 | -0.07275 |
| MADation ViT-B/16 | +0.34146 | +0.07640 |
| MADation ViT-L/14 | +0.00291 | +0.01787 |
| MixFaceNet-MAD | +13.00903 | -8.30976 |
| SelfMAD | +3.80020 | +0.15750 |

These are model-specific logit units, **not a cross-model robustness ranking**. SelfMAD's noTTA sigmoid score is0.155714 native,0.891845 storage and0.177560 border. MixFaceNet's logits are-48.924057,-35.915024,-57.233814 despite sigmoid scores near zero; rendering only0.000 would conceal substantial model-score changes. Use logits and scientific notation for tiny sigmoid outputs. A sigmoid output is a model score, not established calibrated probability of a real-world attack.

The pilot's numerical pattern does not reproduce every aggregate result and must not be chosen/replaced to do so. In particular, this single face cannot establish that Sb reduces artifact reliance relative to A/B; its native model score is also higher, and no attack example is present. Exact per-image changes are legitimate descriptions of these existing variants under the specified preprocessing.

## Precision and scope qualifications

Sb uses float64 network/input with float32 output; six models use float32 with TF32 disabled for maps. Sb's absolute noTTA FP64-minus-FP32 differences are at most3.10e-6 logit, and FP64-minus-historical-TF32 differences at most0.000910. The largest observed FP32-versus-TF32 discrepancy among the other models is MixFaceNet0.056355 logit. These observations concern these inputs only and are not a registered equivalence or platform-generalization result. Maps explain their associated current-precision noTTA scores, never historical TF32 or flip-TTA scores.

Required captions/legends:

1. One deterministically selected FFHQ bona-fide photograph in three existing history variants; seed403 last checkpoints for A/B/Sb; released single checkpoints for the others. No confidence intervals or population inference.
2. Aligned-frame preprocessing, not own-crop evaluation; SelfMAD has384px input, other models224px. Existing storage history is landmark_complete; existing border is lfw_calfw-shaped. Neither is the aggregate61.2px/CFP-FF experiment.
3. Signed gradient-times-input represents local score sensitivity times intensity, not causal evidence, segmentation or an additive completeness decomposition. Black pixels suppress this map, so raw-gradient magnitude must remain visible.
4. Deterministic shared scale across the three conditions within each model and map type; separate scales across models. A signed sum, its absolute value, and sum of absolute channel values are three distinct objects. Numeric colorbars, precise map labels and no per-panel clipping/normalization are required.
5. Preserve mixed precision disclosure and failed-attempt record. Print-legibility/layout approval is separate from this numerical review; parent inspects final180mm figures. Private noncommercial scope and existing attribution/publication-clearance restrictions remain.

No statement that the method is shortcut-free, that attribution proves causal use of a region, that a finite score response identifies a unique mechanism, or that face-spliced detection improved follows from these figures. The last question requires actual attacks and the separately designed fixed-threshold controlled experiment.

CLAIMS:
- file OUTPUT_MANIFEST.json sha256 4b8c99c4879b70a0
- file per_image_scores.csv sha256 4dd8aebf658dc23d
- number completed model-condition outputs = 21 @ OUTPUT_MANIFEST.json
- number manifest files independently rehashed = 119 @ independent audit
- number preserved failed attempts = 2 @ OUTPUT_MANIFEST.json:failed_attempts
