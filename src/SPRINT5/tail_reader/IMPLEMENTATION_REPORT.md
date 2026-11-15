# Tail primary/NI implementation handoff

Status: CODE_ONLY_READY_FOR_INDEPENDENT_REVIEW. New source is `/home/narolski/smad-next/src/SPRINT5/tail_reader/`; evidence is `experiments/SPRINT5_20261114/tail/reader_implementation/`. Paired, breadth, HN and accepted policy files were not modified. No actual candidate archive, logits, checkpoint, model weights or score member was accessed. No actual collector/reader, GPU job or scheduler command was invoked.

Implemented the adopted 70-positive calibration rule, six-cell FA contrasts, fixed eight NI slots, independent calibration and joint evaluation component resampling, exact 15-fit metadata collector/admission, immutable utility adapter and permanent pre-payload claim. Original training reference SHA comes from the existing root admission, without opening its archive. Exact 100-step plans and exposure receipts are reproduced from the pinned source function using an isolated AST extraction, without importing torch or running a model.

Verification: 19 generated-only tests PASS. They cover exact roster/source/reference/platform/budget/schedule and byte-gate rejection; independent release and input/source pins; positive order index and strict tie handling; rejection of camera/zero-threshold substitution; exact evaluation→calibration→joint-seed RNG order; component multiplicity across positives and processing variants; recalculated thresholds under calibration resampling; cancellation of a common score shift; per-network rate averaging rather than logit fusion; all eight guard slots including missing AF0-s61; Bonferroni rather than marginal bounds; missing/sparse/zero-variance inconclusive states; fatal supported nonfinite values; primary-only payload extraction; admit-only without payload; permanent failure claim before payload and no retry; metadata collector ignoring invalid NPZ/weight bytes; monotone/finite objective trace checks.

Input-only validation PASS: 70 calibration positives/26 components; 180 evaluation positives/27 components; 288 genuine rows/six cells; all ordered 15 training plans; person/photo/component separation. The exact 10,000 attempted draw design has SHA `54ffe7325dfbd9d1821bafbdf916f8ed5cef24aed5388a66f5295e65749d5db4`, zero redraws and zero empty required genuine/calibration cells. AF0-s61 is absent in every draw; the other three positive families are present throughout. Their evaluation component counts remain 10/17/17, hence all eight utility slots are inconclusive from metadata support alone.

Outstanding gates:

1. Independent implementation, collector and test review of the final source manifest.
2. Root adoption of the new adapter input binding; the existing policy-input adoption does not grant this.
3. Separate exact 15-fit opaque archive roster, metadata collection release, complete eligibility envelopes and scientific read release, each bound to the reviewed version. Submission or file existence is not eligibility.
4. Diagnostic policy and implementation remain pending separately. Root delegated the exact AUC population/quantile-grid request to Astra; no proposed defaults are adopted here. This does not erase diagnostics from the preregistration or grant full scientific read.
5. Frozen-baseline score-member/70-ID binding and inherited camera provenance remain separate HOLD gates.

No scientific or adoption result is claimed. Source and input bytes freeze at handoff; any later diagnostic integration or fix needs an explicit reviewed version and rebinding before actual use.
