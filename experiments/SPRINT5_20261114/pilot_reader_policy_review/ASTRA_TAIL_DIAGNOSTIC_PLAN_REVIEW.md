# Independent tail diagnostic proposal review — 2026-11-14

Verdict: GO_FOR_ROOT_PROSPECTIVE_ADOPTION of the exact point-only diagnostic scope below. Not implementation approval, collection permission or scientific-read release. Reviewer astra_sprint_plan_review is distinct from proposal author Astra_compute_unblock_plan. No changes to author files.

Reviewed proposal SHA256 1bd8504fe153f733d8fd038be52c99752d669eba251fc592410668db12dae446; tail/prereg.md 0e6b0a6f0dea38ac311efcc4e9ca30dfc9c95b6178fe4cb5e40d1ab1235a12d1; tail/prereg_pilot.md 5c385eed74bfc77031314453905d6c4cd7796798c50c4a21314d7d16a2eb6154; adopted POLICY_PROPOSAL.md 86045c0c36f34e7ad109233dfe70b2f31cdb0d16cf48821af36c7afca0622a9c. Root admission007a6fbd…/packet4268acf… remains the primary source of truth.

## Metadata independently verified

Positive evaluation hash af657d9956641cc12d7026aaba40554f8d2e9b5442d4799aa7b89b72f0fa728a; genuine evaluation03d13e815aba31377bb6e74b39dbd8fb6cd39d8a699fea817c33c18e5af89f1d; calibration9579aec3e68f1142f01658d6e11fd2c95241c5a4399fe25e899ccc49daf20135. Recomputed exact source/family/processing counts from those JSON metadata only:

|Source|Positive rows/components|Family rows AF0/R4/S4|Genuine rows/components per processing|Pair denominator|
|---|---:|---:|---:|---:|
|FERET|54/13|46/4/4|70/20|3780|
|FRGC|126/14|100/13/13|26/14|3276|

Each native/s61/s112 cell has the stated genuine denominator. Total evaluation180positive+288genuine; calibration70. Calibration and combined evaluation are disjoint by exact ID, component, person and photograph sets. Pair denominator is an empirical rank-comparison count, not an independent sample size. Shared components/captures remain intentionally represented.

## Approved interpretation and deterministic definitions

Six AUCs per model use the same-source native attack mixture versus each genuine processing cell, explicitly not processing-matched AUC. Unequal attack-family composition, AF0 rendering/geometry versus ladder constructions, and positive-native versus softened-genuine processing remain alternative explanations. No source superiority, geometry-invariant detection or causal source effect follows. No processed positive or missing AF0-s61 proxy may be introduced. FRGC AF0 concentration in one component must remain visible.

The pairwise greater-than plus half-ties AUC definition is correct for high attack logits. Compute each of15models separately, then five-seed means and all five paired differences for CVaR-minus-mean and BCE-minus-mean. No seed fusion, seed choice or alternative winning arm.

The eight distributions (six genuine cells plus two positive pools), grid[.10,.50,.90,.95], float64 linear empirical quantiles and raw/primary-threshold-centered reporting are coherent. Q(z)-tau equals Q(z-tau) for a fixed per-model scalar tau. Difference-of-quantiles is not quantile-of-paired-image-differences. Centering uses the original independently positive-calibrated threshold, not the training anchor, camera quantile or a new operating point. Uniform additive shift of BOTH logits and their calibrated threshold leaves centered quantities invariant; raw quantiles shift. Tests must shift calibration and evaluation together. The n26 upper quantile is interpolation with sparse tail support, not reliable extreme-tail estimation.

## CI deferral is an explicit scope clarification

Preregistration requires AUC/quantile reporting and broadly specifies component/paired-seed bootstrap, while adopted policy binds uncertainty explicitly for six primary FA effects and eight NI slots. It does not already establish point-only diagnostic reporting as a fully completed uncertainty analysis. Root should therefore adopt this proposal explicitly as a prospective diagnostic-uncertainty clarification before score access. Under that exact clarification, point-only diagnostics with interval=null and NOT_ESTIMATED_DESCRIPTIVE_DIAGNOSTIC are acceptable; this must not be called PASS for uncertainty or evidence of equivalence. No diagnostic CI may later be selected after examining scores under this approval. Any later interval requires separate prospective policy/admission, or clear post-hoc exploratory labeling and review.

No new RNG calls: the existing primary draw stream, calibration resampling, six-cell FA intervals and all eight simultaneous2pp NI guards remain byte-for-byte semantically unchanged. Missing AF0-s61 and sparse families continue to force overall NI/utility INCONCLUSIVE regardless of diagnostic AUCs. Diagnostic omission, negative effects and failed/unknown eligibility must remain explicit. The separately registered frozen-baseline-threshold report remains required or visibly HOLD; this diagnostic approval does not admit its baseline score member or close that separate reporting gap. Nor does it admit the inherited camera auxiliary.

## Implementation acceptance requirements

Implement and independently test complete six-cell/eight-distribution output for all15models and both paired contrasts; exact metadata identities; tie/perfect/reversed/unbalanced AUCs; linear n2/n26 quantiles; retained duplicate captures; common-shift invariance; no RNG advancement; unchanged primary results/conclusion. Reject missing/duplicate/unknown/nonfinite score rows and calibration substitution. Print denominators, component counts, family composition, all seed effects, conditional warmstart limitation and unestimated uncertainty. Any unsupported field remains explicitly unknown/HOLD, not omitted or replaced by a favorable proxy.

Root may bind this exact proposal and review for implementation. Actual input/source/collector eligibility and scientific read still require their separate releases. This review read only preregistration, policy and input metadata; no candidate archive, score/logit, checkpoint, sealed member, image, GPU or scheduler was accessed.
