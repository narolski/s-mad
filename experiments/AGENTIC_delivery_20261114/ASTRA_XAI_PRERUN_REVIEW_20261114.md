# Independent pre-run review: one-person three-condition attribution pilot

14 November 2026. Reviewer Astra, independent of protocol/runner author. Scope is seven allowed fixed/released models on the three already-bound FFHQ00010 PNGs only. No closed payload, benchmark score or checkpoint was opened by this reviewer. No model inference or GPU action was performed by this reviewer.

## Protocol review

Protocol reviewed at SHA256 `602ab77d2679b0b29811c863c8b9e39f1257476fbdef03b2a647e2e7e9f4e16e`. **GO for the scientific protocol; executable/source/checkpoint pin review still required before execution.** This is not a population experiment or causal-localization test. The user's requested per-image responses must be actual model outputs, never the aggregate evidence-matrix numbers.

Checked the actual frozen adapters, not recalled APIs: `/home/narolski/mambamorph-code-a46/smadcvpr/a12_released.py:114–140` returns morph-minus-bona logit with model-specific class index, and differentiable channel permutation/normalization. `/mnt/t7/smad_next/PN1/fs_tree/pn1/code/smadcvpr/common.py:816–860` supplies the existing PIL bilinear model-input resize; `build_run_model` reconstructs architecture/LoRA from metadata. The selected aligned-frame path must remain labelled as such, particularly SelfMAD384 RGB with no native face recrop. A/B/Sb fixed seed403 last checkpoints avoid outcome-based seed choice; no claim about the five-seed recipe follows.

Required implementation checks:

- Bind exact runner, dependency, base/release/trainable-checkpoint, model metadata and three PNG hashes before inference. For trainable-only checkpoints, validate the complete expected trainable-key set, shapes and absence of unexpected keys against the frozen base; a blanket `strict=False` without validation is insufficient.
- Differentiate the attack-oriented noTTA logit with respect to pre-normalization RGB input; eval mode, no AMP, frozen weights with input gradients. Record noTTA outputs and clearly separate flip-TTA diagnostics. Parity between gradient-enabled and inference forwards, repeated-score checks, finite derivatives and the prespecified finite-difference test must actually pass.
- Preserve raw gradients and gradient-times-input. Zero black pixels suppress gradient-times-input even where the derivative is nonzero, so raw-gradient magnitude must remain visible. Signed channel sum may cancel directions; magnitude and signed maps have different meanings.
- Use a deterministic shared scale across all three conditions within a model and map type: unsigned maps 0 to shared maximum; signed maps symmetric around zero at shared maximum absolute value. No per-panel normalization, percentile clipping, smoothing or thresholding. Print numeric scale/colorbar and separate units for gradient versus gradient-times-input. Raw cross-model strength is not calibrated or comparable.
- The finite-difference perturbed tensors are derivative diagnostics only, never extra reported image conditions or new stored transformed images. Head-zero is an algebraic sanity check and does not validate faithfulness of localization to learned features. Unsupported/failed checks must be explicit; do not substitute heuristic maps or hide a weak map.
- Rendering must preserve native-grid numerical artifacts and be legible at 180mm (at least 8pt text), with standalone high-contrast/grayscale sensitivity views as well as overlays. Any display interpolation is labelled display-only and never fed back to inference. No pseudo-saliency enhancement.

## Mandatory interpretation/caption limits

There is **one person in three history variants**, not three independent people. All are bona fide. No face-spliced attack is shown, so this pilot does not establish improved attack detection, population false-alarm reduction, invariance, shortcut removal or causal pixel importance. Gradients show local score sensitivity at the observed input; gradient-times-input is not integrated attribution or a completeness decomposition.

Native already contains black border pixels. The existing storage variant is landmark_complete history, not a newly constructed 61.2px intervention. The existing border mask is lfw_calfw-shaped; TT1 aggregate B/Sb values concern training-source camera photos with CFP-FF-shaped masks. Keep those source populations, transformations and endpoints separate. The supplied assets remain private noncommercial draft material under their existing attribution/scope record.

Every failed model/check and every fixed condition must be retained. No replacement person, favorable seed, different checkpoint, target or normalization may be chosen because the maps look unhelpful. A narrowly reviewed technical repair is possible before new execution; any previously produced outputs remain recorded.

## Final executable admission — GO

Independently inspected the complete runner and inventory and verified their hashes:

| Artifact | SHA256 |
|---|---|
| xai_gradient_pilot.py | 8ee9d872e04bdad609fbb3bf6e968825c7ab0e6692b75d4f1c42e63973f1da9a |
| XAI_INVENTORY_20261114.json | 62a2add3532681e069630d356c4a392c91dc8571774e24624af64b3dedb1c65e |
| XAI_PROTOCOL_20261114.md | 602ab77d2679b0b29811c863c8b9e39f1257476fbdef03b2a647e2e7e9f4e16e |

**GO for the bounded real pilot at exactly these bytes, under the parent's execution release.** First A/native is the smoke, followed by the remaining fixed conditions/models with unchanged code. No closed benchmark, challenger score or additional example is admitted. The provisional protocol-only disposition above is superseded for this exact executable snapshot.

The runner hashes sources/inputs/current model checkpoint dependencies before loading; refuses existing output directories; uses isolated Python, weights_only loading or safetensors; reconstructs fixed seed403/last models. Own trainable checkpoint key sets must exactly equal the model's trainable parameter set, with native shape validation and only frozen state missing; released checkpoints load strictly. The inventory includes metadata and the frozen CLIP base. I inspected the inventory but did not load/hash model weight payloads myself; execution verifies their pinned bytes.

Actual gradients are taken through the reused input adapter to the noTTA morph logit. Model.eval, float32, disabled parameter gradients, repeated-forward/parity checks, finite nonzero gradients, two fixed finite-difference diagnostics and algebraic head-zero checks are implemented. The final Linear is the own `head.cls`, MADation official `head`, and MixFaceNet `linear2` in inspected sources. For any architecture where head identification or backward fails, the runner retains failure and does not generate a substitute explanation. The author reports a real-torch synthetic linear/sign/channel/black-input/finite-difference test PASS; this reviewer checked the corresponding runner algebra rather than independently executing that reported test.

Raw NPZ arrays are saved before rendering. Signed scale is max absolute signed channel sum across all three conditions; each unsigned scale is its shared three-condition maximum. Rendering has no per-image percentile clipping. Signed positive is red and negative blue in the runner's basic RGB export. Parent composite uses an explicitly labelled diverging palette; its display-only alpha is 0.85×abs(signed)/shared maximum, with native grids preserved. Parent's absolute signed-sum grayscale is **abs(sum(channelwise gradient-times-input))**, which differs from runner `magnitude = sum(abs(channelwise gradient-times-input))`; label the exact object. Raw-gradient grayscale remains separately required. Both forms can cancel or suppress different signals and must not be conflated.

Execution success, print-layout verification and post-result interpretation are not asserted by this pre-run GO. Failure receipts and partial numerical files remain available for independent diagnosis; no automatic alternate checkpoint, map, target or tolerance follows. All final maps/scores must be labelled this one-person descriptive pilot, not causal evidence or an attack-detection result.

## Precision-repair addendum — GO for a fresh bounded run

After the initial A run failed its border finite-difference diagnostic, the method author proposed a prospective precision repair. Original partial outputs and failure remain preserved and are excluded from deliverable panels. TF32 numerical effects are a plausible explanation, not an established cause from that failure alone.

Independently inspected the entire runner diff and inventory diff and verified:

- `xai_gradient_pilot_fp32.py`: `4db5da114b8b8df4dc3842c8c59a4ffd587e1a41998181e53a3b3223835b93c4`
- `XAI_INVENTORY_20261114_FP32.json`: `b6874f51611854383946dc5afe4e333edc4e42913251fa2a3f13e8b8f972cb29`
- `XAI_FP32_ADDENDUM_20261114.md`: `0dbb7ae93453c0e04eba500619f55d83ea0008b11b3dbe042e3d4c404245c4a1`

**GO for fresh A_fp32 across all three conditions, followed by the same precision for the remaining six fixed models under parent release.** The diff disables TF32 for actual attribution/inference/checks, adds recorded historical TF32-on noTTA/flip forward diagnostics and immediately restores TF32-off, and detaches a scalar warning. Both finite-difference epsilons and tolerances, target, input bytes, checkpoints, normalization, output scales and failure gates remain unchanged. The inventory changes only runner binding and inclusion of the precision addendum. No selective rerun of only the failed condition is admitted.

Maps explain FP32/TF32-off noTTA scores, not the historical TF32 output. Report precision deltas without an equivalence claim. Only complete runs passing all unchanged gates may enter figures; another failure requires independent disposition with outputs retained. This is a reviewed technical precision repair, not an outcome-driven relaxation of the scientific test.

## Second precision addendum — Sb only

Six models completed FP32 checks; Sb failed its storage finite-difference check. Independently inspected complete runner/inventory diffs and verified `xai_gradient_pilot_fp64.py` SHA256 `0ba34b628bb8ed2b6b9b291e874ce2ac8354c25a28ac3d7905c1450da28257ed`, inventory `7fc6f430113d91ba3d0ae09cea7bec0fc46755e055e7c6af3a7014686fa9d905`, and addendum `3f81271e589a605d613c0aaf8f387d61a2cfaffd9b63b3ca19ec0425479b6a43`. **GO for fresh Sb_fp64, all three fixed conditions only.** Inputs/checkpoints/epsilons/tolerances are unchanged, previous failure remains preserved, FP32 TF32-on/off references are explicitly recorded before conversion.

Precision is float64 network/input with a float32 output cast. Correction to the addendum's attribution of that cast: it occurs in the runner's `fwd` lambda, not the inspected `C.forward_logit` function. This does not change permitted execution, but figures/records must not claim entirely double-precision output. Mixed precision across models must be disclosed; no cross-model map-strength comparison or further automatic retry is admitted.
