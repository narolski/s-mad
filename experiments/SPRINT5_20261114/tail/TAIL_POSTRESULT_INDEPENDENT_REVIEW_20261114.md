# Independent tail postresult review — 2026-11-14

Reviewer: Astra. Scope: exact root-admitted development RESULT.json and saved replicate records only; registered metadata/source and release/journal receipts. No reader rerun, archive/NPZ/checkpoint/camera/baseline/sealed access.

## Numerical and interpretation verdict

PASS saved-result arithmetic, registered intervals, eight NI dispositions and release/journal integrity. Permitted narrow conclusion: the registered operating-point pilot provides no demonstrated CVaR false-alarm advantage; CVaR also has an adverse descriptive S4 sensitivity difference. Utility/noninferiority is not established. This is not proof of equivalence or population-zero FAR, shortcut removal, benchmark superiority or adoption.

Calibration70 positive rows/26 components achieves0.90 sensitivity in every network; this is calibration sensitivity, not guaranteed held-out sensitivity. All90 point genuine rates (3arms×5seeds×6cells) are0: FERET70 rows per native/s61/s112 cell; FRGC26 per cell. Thus all12 registered mean contrast point estimates are0. All cells, including zero-variance cases, are retained according to the actual stored distribution; specifically:
- CVaR-minus-mean: FERET native/s61/s112 and FRGC native intervals INCONCLUSIVE due zero variance; FRGC s61 interval[−0.0384615385,+0.0714285714]; FRGC s112 percentile endpoints[0,0] despite nonzero full replicate range.
- BCE-minus-mean: FERET native/s61/s112, FRGC native and s112 intervals INCONCLUSIVE; FRGC s61 interval[0,+0.0384615385].
The [0,0] central interval does not mean no uncertainty or equivalence: rare nonzero draws exist outside its central percentiles. Calibration is jointly resampled, so nonzero bootstrap effects can occur despite zero original-point false alarms.

Held-out S4: BCE and mean each11/17=0.6470588235 for allfive seeds. CVaR seeds521–525:9/17,9/17,10/17,9/17,9/17 (0.5294117647,0.5294117647,0.5882352941,0.5294117647,0.5294117647). CVaR-minus-mean mean−0.1058823529, or−10.588percentage points. AF0_u50 sensitivity145/146 and R4 17/17 are unchanged across arms/seeds. AF0_u5061 is absent, not a zero effect. Every one of8 simultaneous2pp NI guards remains INCONCLUSIVE: support10/0/17/17 components, below registered20 or absent. No lower bound or NI pass can be inferred from these point effects.

Independent checks recomputed every FA per-seed/mean contrast and all12 registered intervals from saved10,000 replicate effects; zero-range guards and nonzero-range percentile intervals match. All8 positive-family contrast means/null patterns and NI statuses match. Diagnostic6 source/processing AUC cells and8 quantile distributions were checked for per-arm means, all paired-seed contrasts, denominators and raw-minus-primary-threshold arithmetic. No diagnostic CI was estimated. No original AUC ranks, calibration order statistics or raw empirical quantiles were reconstructed because raw scores are outside this review.

Point-only diagnostic native AUC means BCE/mean/CVaR are FERET0.99761905/0.99396825/0.98931217 and FRGC1/1/1. Denominators are54native positives×70genuine=3,780 FERET pairs, and126×26=3,276 FRGC pairs—not independent support counts. Source-specific mixture and native-positive versus processed-genuine confounding preclude interpreting these near-perfect AUCs as general morph specificity. All six diagnostic cells and every seed remain in the result.

CVaR-minus-mean genuine p95 raw/threshold-centered shifts, respectively: FERET native−.03096/+.04327, s61−.01076/+.06346, s112−.01749/+.05674; FRGC native−.66703/−.59280, s61−1.64508/−1.57085, s112−1.51799/−1.44376. The calibration threshold also moves: raw lowering alone is not improved operating separation. The strongest alternative is score/threshold movement in this conditional short warmstart continuation, with source/processing mixtures and tiny effective support. At FRGC26 rows, p95 is especially weak tail evidence.

Baseline threshold auxiliary remains REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION; camera HOLD. Missing/sparse guards, adverse S4 change, zero-event uncertainty and point-only diagnostics must accompany any report.

## Exact evidence and limits

Independent numeric-check receipt TAIL_POSTRESULT_NUMERIC_CHECKS_20261114.json: SHA256 4a25c0ce5b7824562aae7f3a12e4da967662eef75b9b3c1d759467ed4e454415.
- result_sha256: b5aaf0d368dcf46f819a1fd0b1489e1067d5d00ccb70520531f9e66c3fa9599f
- claim_sha256: 6bffcc81ade96e4d3ecc02bf31c0135ca6d688398fb422e8e68469e04cb0eb94
- terminal_sha256: 7544fc198f46ac3949f8c9a8b5ffa5d275cd9d5173cfb29c44bdd0e1c3887f00
- release_sha256: cee816232869b06bf8097fa8204dc866b78e3d3f575b29913ce8d2062de48644
- roster_sha256: 08502ee93c955e5e43c645d2a7a2230cecf52c38558aabf80dcaeae0d11c7e88
- binding_sha256: ff2aa74853658d1d318725e42eedbdd2ac16cde8d7da57971c04e4447626c6a2
- reader_sums_sha256: 943d47ef9ac0638c46dc1fdaf65782cabbd43d93405ce80305c4bac58c1fce5b

Claim matches root release, binding, exact reader source, roster and archive identities; TERMINAL is COMPLETE and hashes the exact result. Independent/postcollection and prior collector review hashes match root release references. Durable execution summary reports native0 for both runs. Arithmetic tolerance1e-12. Independent recomputation starts from saved summaries/replicates: it cannot replace raw-score verification and does not assert independently reconstructed per-image AUC, calibration threshold or empirical quantile ranks. Stored maximum-floor replicate values are used, not refitted or recomputed from hidden per-image scores. No alternative statistic or post-hoc threshold was selected.

GO for accurately qualified internal development reporting of these results; no SOTA, benchmark, utility, causal-mechanism, final publication or adoption GO. Preserve original results and permanent claims.
