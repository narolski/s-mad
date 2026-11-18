# Actual three-image model sensitivity pilot: completed handoff

Seven published/frozen models have complete, checked outputs for the same deterministically selected FFHQ image00010 in three existing conditions: aligned native history, existing landmark_complete storage-matched history and existing TT1 added-black-border history. **21 actual input-gradient maps**, with raw RGB derivatives and gradient-times-input tensors, were computed locally on DGX GB10. No synthetic or illustrative map substitutes were used. No new image intervention, training, benchmark read, rental or cluster mutation occurred.

## Final output binding

Directory `/home/narolski/smad-next/manuscript_cvpr2027/figures/shortcut_attribution_20261114/`:

- `OUTPUT_MANIFEST.json`, SHA256 `4b8c99c4879b70a0fedb7cb5e5ec013c9a904f0d1657bc1cbfaf55bec975600d`: individual hashes and sizes of all completed model files; retained failed attempts.
- `per_image_scores.csv`, SHA256 `4dd8aebf658dc23d8620a1ff5771a2e0292d7afb1b0f777eef818b62bb3c1c09`: all21 actual noTTA logits/probabilities, flip-TTA probabilities and logit differences from this person's native condition, linked to exact raw-map/result hashes.
- Completed directories: `A_fp32`, `B_fp32`, `Sb_fp64`, `madation_vitb16_fp32`, `madation_vitl14_fp32`, `mixfacenet_mad_smdd_fp32`, `selfmad_hrnet_w18_fp32`.
- In each: `native_raw.npz`, `storage_raw.npz`, `border_raw.npz`, `result.json`, native-input-grid PNGs, signed-map PNGs, magnitude and raw-gradient grayscale PNGs. NPZ keys: `input`, `gradient`, `gradient_times_input` (CHW), and `signed`, `magnitude`, `gradient_magnitude` (HW). Native model grids224px, SelfMAD384px. No backprojection or new detector resize.

The output binder verified all21 NPZ hashes, finite arrays, compatible shapes, exact `gradient_times_input=input*gradient` and signed channel sums. All seven completed runs passed repeated no-grad/autograd score parity, noTTA/flip repeatability, finite nonzero input gradients, the unchanged two-epsilon finite-difference check and algebraic zero-head check. These checks establish an executed differentiable computation in the stated scope; zero-head is not a learned-feature-faithfulness or causal-localization test.

Model execution times were3.81s A,3.91s B,7.63s Sb,3.72s MADationB,8.94s MADationL,1.72s MixFaceNet,3.26s SelfMAD, excluding preparation and process/import overhead. Authoritative per-run UTC start/end/device/version details are in result.json. No spending.

## Precision failures retained and numerical repair

Original `A/` used TF32 and failed the border directional-derivative check. Its native/storage partial NPZs and failure.json remain preserved and are excluded from accepted figures. After independent pre-run review, the new FP32 runner disabled TF32 for inference/gradients/checks, recorded historical TF32-on reference forwards, and retained exactly the original epsilons/tolerances. A and five other models passed all3conditions.

`Sb_fp32/` then failed the unchanged storage check, preserving native partial data and failure. A separate independently reviewed, fresh `Sb_fp64/` ran all3conditions using float64 network/input arithmetic with float32 output. It passed. Its actual noTTA logits differ from its FP32 reference by only−2.38e−6 to−3.10e−6 on these3inputs; this is an observed numerical diagnostic, not a platform-equivalence or benchmark gate conclusion. Do not mix incomplete attempts into accepted comparisons or conceal the precision investigation.

**Wording erratum for immutable protocol/addendum/result history:** the retained `.float()` output cast belongs to the XAI runner's `fwd` lambda, inherited from the scoring implementation pattern. `common.forward_logit` itself returns the model output unchanged. Thus Sb is “float64 network/input with float32 output,” not pure end-to-end FP64. Existing pinned artifacts were preserved rather than rewritten. Other six completed models use float32 with TF32 disabled. Disclose this mixed arithmetic; raw map/logit strengths are not calibrated across models.

## Prospective sources, independent gates and commands

All below are under `experiments/AGENTIC_delivery_20261114/`:

| Artifact | SHA256 |
|---|---|
| `XAI_PROTOCOL_20261114.md` | `602ab77d2679b0b29811c863c8b9e39f1257476fbdef03b2a647e2e7e9f4e16e` |
| `xai_gradient_pilot_fp32.py` | `4db5da114b8b8df4dc3842c8c59a4ffd587e1a41998181e53a3b3223835b93c4` |
| `XAI_INVENTORY_20261114_FP32.json` | `b6874f51611854383946dc5afe4e333edc4e42913251fa2a3f13e8b8f972cb29` |
| `XAI_FP32_ADDENDUM_20261114.md` | `0dbb7ae93453c0e04eba500619f55d83ea0008b11b3dbe042e3d4c404245c4a1` |
| `xai_gradient_pilot_fp64.py` | `0ba34b628bb8ed2b6b9b291e874ce2ac8354c25a28ac3d7905c1450da28257ed` |
| `XAI_INVENTORY_20261114_FP64.json` | `7fc6f430113d91ba3d0ae09cea7bec0fc46755e055e7c6af3a7014686fa9d905` |
| `XAI_FP64_ADDENDUM_20261114.md` | `3f81271e589a605d613c0aaf8f387d61a2cfaffd9b63b3ca19ec0425479b6a43` |

The pinned inventories contain exact checkpoint/source/input hashes and paths. A/B/Sb are fixed frozen seed403 last-trainable checkpoints plus pinned original frozen CLIP weights, exact trainable-key-set validation and shape validation; no best-seed choice. Published checkpoints match the existing canonical AR1 hashes and load strict, using safetensors or torch.load(weights_only=True), under Python `-I`, offline local weights. Model-provenance archive lookup found none; implementation therefore reads actual existing source adapters rather than remembered model APIs. Existing source/dirty work was preserved.

Each model was executed once in its accepted namespace with:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 \
 /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
 experiments/AGENTIC_delivery_20261114/xai_gradient_pilot_fp32.py \
 --inventory experiments/AGENTIC_delivery_20261114/XAI_INVENTORY_20261114_FP32.json \
 --model MODEL --out manuscript_cvpr2027/figures/shortcut_attribution_20261114/MODEL_fp32
```

Sb alone uses the corresponding `fp64.py`, `FP64.json` and `Sb_fp64` namespace after its separate reviewed repair. Commands are historical reproduction records; do not overwrite/replay existing output directories. The six-model batch's exact argv, return codes, stdout/stderr and wall times are in `XAI_FP32_EXECUTION_20261114.jsonl`; original A/Sb diagnostic failures remain in their own failure.json files. A cuBLAS first-context warning occurred on own-model backprop; all accepted gates passed. Actual model outputs were obtained only after independent code/protocol GO and parent release; post-result independent review remains required for any interpretation.

## Interpretation and print handoff

These maps explain the noTTA **attack-oriented logit** in the already existing aligned-frame evaluation path. The sigmoid/softmax values are **uncalibrated model scores**, not empirical probabilities that this person/photo is an attack; CSV probability field names denote the mathematical head output only. SelfMAD uses384px RGB aligned-frame input, **not** its own dlib recropping; MADation/MixFaceNet use224px BGR affine0.5/0.5 adapters; A/B/Sb use their model's embedded CLIP normalization. Flip-TTA scores are recorded, but the maps do not explain flip-TTA. No inference on closed candidates/sealed sets occurred.

Signed maps are RGB-channel sums of gradient-times-input. Red locally increases morph logit; blue decreases it. Every black input pixel has zero gradient-times-input irrespective of sensitivity, so raw gradient/magnitude must remain separately visible. Neither map is a segmentation, completeness decomposition, explanation of a group average, evidence that a model “uses identity,” or causal proof of a shortcut. One genuine face cannot establish accuracy or a recipe benefit. There are no ground-truth saliency labels.

Render **storage history** separately from the **spatial/border** comparison as the author requested. One deterministic maximum across all3conditions per model/map type is recorded in `scales`; signed scale is symmetric. Preserve shared numerical colorbars and do not normalize each condition independently. Use at least8pt text at180mm width, readable large inputs/maps and a grayscale version. Contour/overlay layout is display-only; all raw arrays remain unchanged. Cross-model scales differ and strengths are not comparable.

All images remain private noncommercial working draft: CC BY-NC2.0 per-image attribution to Anjul Sahu is in the asset package; publication/likeness clearance remains pending. The source native frame already has a small border, added mask family is lfw_calfw, and storage is the existing landmark_complete history, **not** newly generated61.2/112.7px intervention. Do not attach aggregate matrix metrics to this face as if they were its scores. No external publication is authorized by this handoff.
