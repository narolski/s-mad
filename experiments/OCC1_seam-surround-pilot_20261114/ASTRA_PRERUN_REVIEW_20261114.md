# Independent OCC1 pre-run review — 14 November 2026

**Method/code GO at the exact hashes below, conditional on the lead's separate rights/input admission and execution release. No image-export clearance or final scientific/print-display GO is issued.** Reviewer Astra did not author the runner, select an outcome or execute real inference. Review covered source, registration and inventory; independently executed synthetic self-test only.

| Artifact | SHA256 |
|---|---|
| src/OCC1/occlusion_runner.py | 2d89d00054bdcae2a4f3f99b791b8af6280f702d3ea071a876b0307f8388776a |
| experiments/OCC1_seam-surround-pilot_20261114/prereg.md | e57b042df42fcfe6f0d261b2d7995d1d8699594638e39c72a4d15e11f57c484a |
| experiments/OCC1_seam-surround-pilot_20261114/INPUT_MODEL_PINS.json | 42f6f16c17a34b501dbb87ce98872186a6ffcb3510743a95ede29a9eda9057d4 |

The numeric-only pilot is a new development diagnostic, not a Batch-C/NEXT amendment. Earlier Batch-C review snapshots are unrelated and do not supersede later Batch-C admission/results. Closed scores and benchmark payloads remain outside this assignment.

## Reviewed design and implementation

- Fixed metadata-selected development host and eight existing rungs, seven fixed models with own seed403 last checkpoints. No outcome-based example/model choice. Inventory binds source manifests, original H/B landmarks, code, image bytes and model/base weights. I inspected the inventory but did not independently decode/checkpoint-load these payloads; runner enforces current byte pins before inference.
- Actual AR1 amendment7b hull helper is reused. Pixel compositing gates require S4=R2w4 outside/R4 inside, S3=R2w outside/R3 inside, S0=R2w4 outside/R2w inside. Inclusion of both warp backgrounds correctly exposes that S3 does not share S0/S4's surroundings. No obsolete separate S3 hull is silently substituted.
- Fixed nonoverlapping8×8grid of64×64native patches, both RGB0 and128 fills, no smoothing/inpainting or score-guided ROI. Every patch has4096native pixels; complete map includes unclassified cells. Same-size seam-overlapping and lexicographically selected pure-surround cells form a bounded spatial diagnostic. Exact masks, category indices and post-standard-resize support/soft areas are retained.
- Memory preprocessing must exactly equal unchanged ImageItems tensors for all eight original images before any sweep. Existing attack-oriented noTTA heads/normalization, float32 TF32-off, eval, offline weights and strict release/exact-trainable-key own reconstruction match the previously reviewed source adapters. Single/batch8 baseline comparison at1e-4 is prospectively fixed; repeated/no-op logits at1e-5, finite output, complete-grid gates and permanent failure receipts are implemented.
- Delta is occluded minus original attack logit; negative means less attack-like. Baseline, actual perturbed output and uncalibrated sigmoid score are retained. All fill-specific regional means and paired S4/S0/S3/background map contrasts are printed; no hypothesis test, threshold fitting or population interval is introduced.
- NPZ contains numerical responses, grid coordinates and geometry masks, **no original or occluded face pixels**. Create-only outputs, 50GiB free-space check and failure receipts are implemented. No sealed loader, cluster mutation or spend is present.

Independently ran `python -I src/OCC1/occlusion_runner.py --self-test` with four numerical-thread limits2 and nice10: **PASS** exact mask/support, no source mutation, identity sham, signed linear delta and full tiling. No real image or model inference was used by that test.

## Required interpretation and documentation precision

1. Call selected cells **seam-overlapping patches**: the >=10%ring criterion leaves other facial/surround pixels inside each intervention. This is not isolated removal of the seam. Constant fills add artificial boundaries and remove content; two fills and paired controls do not eliminate that nuisance.
2. Surround controls match native area and square shape, not texture, image position or semantic content. Seam-minus-surround effects are conditional replacement contrasts, not identified causal region importance. No area normalization or comparison of whole-surround versus narrow-ring effects is licensed.
3. R3/R4 and S0/S3/S4 labels must distinguish same-person/two-person and full-frame/splice constructions. Do not infer identity-specificity from S4−S3 alone, especially given differing backgrounds; preserve both background comparisons and both fills even if inconvenient.
4. Scope is a single selected host with dependent derivatives and one fixed seed per own model. No population robustness, superiority, shortcut-removal or attack-detection improvement follows. Sigmoid values are uncalibrated head scores, not established real-world attack probabilities; no false-positive/miss labels without a stated fixed threshold.
5. Minor workload arithmetic: the full sweep is7models×8rungs×64patches×2fills=**7,168occluded forwards**, with smoke/baseline/parity calls additional. The prereg estimate7,728 is not the occlusion count. This is a documentation correction, not a gate/analysis change.

## Remaining release and display gates

The present protocol/inventory explicitly forbid original/occluded pixel export pending separately documented rights admission. This review does not decide which historical/current FERET agreement applies. The lead must record that disposition before real input processing; no face-containing figure follows from this code GO alone.

After admitted smoke passes, full execution may use the same pinned code, masks, fills and inputs. Any failed gate remains visible and requires independent disposition before changing numerical tolerances, source host, geometry or controls. Smoke covers first eight black-fill grid cells, not a complete scientific map, and must not be presented as one.

Final GO requires independent numerical checks of complete outputs, both fill conditions and all fixed models/rungs, followed by actual180mm print inspection (>=8pt), explicit grid/mask geometry, signed colorbar, grayscale/sign legibility, fixed within-model scales across the complete relevant set, and correct baseline/delta captions. Only then may the user-facing result be shown. No smoothed pseudo-localization or aggregate values placed onto an individual face.
