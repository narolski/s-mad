# Tail diagnostic binding proposal — 14 November 2026

PROPOSAL FOR INDEPENDENT REVIEW AND ROOT ADOPTION ONLY. No self-granted GO, no actual scientific read. Primary implementation continues unchanged. This separately resolves omitted AUC populations and quantile probabilities in adopted policy007a6fbd…/packet4268acf…/commitf18f8d1. No candidate payload, logit, checkpoint, image, GPU or scheduler access occurred. HN is out of scope.

## Recommended minimal binding

Add point-only descriptive diagnostics now, with uncertainty explicitly not estimated for these new diagnostics. Keep primary90%-positive-calibrated six-cell FAR and all8 NI guards, their RNG/call order/bootstrap/output labels exactly unchanged. Do not add p-values, diagnostic winner criteria, seed selection or substitute outcomes. Root must adopt this exact definition before candidate access; until then emit DIAGNOSTIC_POLICY_UNBOUND, never choose defaults.

### Exact populations and denominators

Reuse only adopted ordered metadata:
- TAIL_POSITIVE_EVALUATION_PROPOSAL.json SHA256 af657d9956641cc12d7026aaba40554f8d2e9b5442d4799aa7b89b72f0fa728a.
- TAIL_GENUINE_EVALUATION_PROPOSAL.json SHA256 03d13e815aba31377bb6e74b39dbd8fb6cd39d8a699fea817c33c18e5af89f1d.
- Calibration remains separately pinned9579aec3e68f1142f01658d6e11fd2c95241c5a4399fe25e899ccc49daf20135 and never enters diagnostic AUC/evaluation quantiles.

For each genuine source×processing cell, positive AUC population is ALL native held-out positive rows from the SAME SOURCE, pooled image-weighted across the three available families. Use this SAME positive list for native,s61,s112 genuine cells; do not manufacture softened positives or substitute R4s61 for missing af0_u5061. Explicit label: “same-source native attack mixture versus [processing] genuine”, not processing-matched AUC.

Metadata independently counted:

| Source | Positive rows/components | Fixed positive mixture | Genuine rows per cell/components | AUC pair denominator per cell |
|---|---:|---|---:|---:|
| feret |54/13|46af0_u50+4lad_R4+4lad_S4|70/20|3780|
| frgc |126/14|100af0_u50+13lad_R4+13lad_S4|26/14|3276|

All three genuine processing cells remain separate per source, six total. Repeated captures and shared components remain; no deduplication, source/family balancing, cross-source pooling or independent-pairs inference. Source AUC differences reflect fixed unequal attack mixtures and cannot establish a source effect. FRGC100 AF0 rows occupy one component as recorded in adopted policy.

Higher attack logit is positive. AUC = sum over every positive/genuine pair of [z_positive>z_genuine]+0.5*[equal], divided by n_positive*n_genuine. Calculate per arm and each seed521–525 first. Print all15 AUCs per cell and arithmetic mean of five per arm. Contrasts are mean of five PAIRED AUC differences CVaR−mean and BCE−mean, retain all5 differences. No pooled-seed AUC, rounded-score comparison or macro-AUC winner.

### Quantiles

Fixed probability grid P=[0.10,0.50,0.90,0.95]. Compute float64 empirical logit quantiles using NumPy method="linear": h=(n−1)p, linear interpolation between floor(h)/ceil(h) ordered observations. This method is ONLY descriptive quantiles; never replace primary threshold's nextafter/order-statistic rule with it.

Compute separately for each of six genuine cells AND each of the two same-source native positive pools above: eight distributions, each arm/seed, ordinary image weights. For each p print raw-logit quantile and margin-to-primary-threshold quantile Qp(z)−tau_arm,seed. The latter uses already-computed ORIGINAL primary calibration threshold, does not create a new threshold. This distinguishes global shift from threshold-relative movement; no sigmoid probabilities are necessary. Retain n_rows,n_components and source/family composition. At n26,p.95 there are only1.3 nominal rows above that fraction: explicitly finite-sample interpolation, not reliable extreme-tail estimation. No .99/extrapolation/max or extra score-driven probabilities.

Print per-arm arithmetic mean of five per-seed quantiles plus all individual values. For both fixed contrasts print five paired differences and their mean, for raw and threshold-relative quantities. Do not quantile pooled seed logits; do not confuse difference-of-quantiles with quantile-of-per-image differences. No calibration-population quantiles, identity-weighted version, baseline408 extension, or inherited119-cell auxiliary extension is added here.

### Uncertainty and missingness

These new diagnostics are POINT-ONLY, conditional on the exact fixed evaluation mixture and shared408 warmstart. Display `uncertainty_status=NOT_ESTIMATED_DESCRIPTIVE_DIAGNOSTIC`, interval=null, no p-value. All5seed values show continuation variability but are neither confidence bounds nor five independent pretrained backbones. Do not describe absence of diagnostic CI as evidence of equivalence.

Reason for bounded scope: source-positive support is only13/14components and FRGC AF0 is concentrated in one component. Binding additional bootstrapped source-specific rank/quantile coverage and handling zero-positive draws would require another prospective support policy; it must not alter the already adopted primary resampling stream or silently drop/redo draws. Diagnostic CIs remain separately HOLD until an independently reviewed pre-score amendment, if desired. Primary FAR descriptive intervals and NI bounds continue exactly as adopted. Diagnostics need no new RNG calls, so cannot perturb primary draw hashes.

No missing/nonfinite score may be dropped from a diagnostic distribution. Unknown ID, duplicate score ID, missing expected row, wrong orientation/seed or nonfinite admitted score is fatal admission failure under the reader's existing complete-roster rule, not a new scientific winner gate. The absent af0_u5061 remains absent in8-guard family; the3-family descriptive AUC mixture does not repair it. Overall NI/utility conclusion remains INCONCLUSIVE under adopted support policy.

## Review/adoption and synthetic acceptance

Independent reviewer checks exact IDs/source counts, pair denominators, no calibration overlap, complete six-cell/eight-distribution output, rank-tie formula and linear quantiles. Synthetic tests: all-tie AUC=.5; perfect/reversed ranks; unbalanced counts; constant additive shift leaves AUC and threshold-relative quantiles unchanged while raw quantiles shift; duplicate captures retained; contrast sign and paired-seed aggregation; quantile interpolation on n2/n26; no RNG advancement; diagnostics cannot change primary FAR/8NI outputs or conclusion. Reject calibration inputs or processed-positive proxies.

Root records exact file hash and adopted policy version separately; Sol may then implement tests/adapter without altering frozen primary definitions. A root implementation adoption is not collector/read release. If root prefers no added diagnostic scope now, preserve these fields as HOLD_SEPARATE_BINDING and deliver primary implementation; do not silently claim preregistered diagnostic reporting complete. All actual collector/reader/public scientific reads remain HOLD pending their existing independent admission/release gates.
