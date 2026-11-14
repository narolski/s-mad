# Version 2 additive reporting repair — CODE ONLY, NO RELEASE

Copied from frozen paired_ranking_reader source manifest02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c. Original sources/approval remain untouched. All entry points use the explicit paired_ranking_reader_v2 package; data uses relative admit import. No implicit import of frozen statistics. Independent review and new exact source acceptance are required before ANY collector/read release. This folder does not inherit e1ee3a5 code approval.

New reporting.py adds descriptive strict-threshold flag counts, denominators and rates for all3arms×5seeds, at each network's unchanged camera-derived threshold and at own-rule zero. It reports S3 control flags/S4 sensitivity overall and by existing primary source, calibration-camera BPCER, and all119 heldout genuine cells. Every population includes the registered contrast pairs plus descriptive ranking−BCE, per seed and seed mean. S3 controls are not called camera BPCER. No confidence intervals, margins, reductions, new endpoints or verdicts are added. Counts are image-row denominators, not independent-person effective sample sizes.

Existing analyze inference code changes only by importing/calling the pure reporting function at result construction; reporting has no RNG/file I/O and uses existing allowlisted P/C/G arrays. The existing hardcoded once journal/output paths remain unchanged intentionally: versions cannot bypass a previous claim by changing journal names. Root must choose/review exact source before any first read. No actual archive, roster, collector or reader was invoked.

New test_reporting.py uses generated fixtures, tests all fields/counts/contrasts/cells, strict ties, uniform shift invariance under camera calibration plus own-rule shift visibility, exact unchanged old statistical results/RNG, v2 import provenance and historical/wrong-population rejection. The old loader allowlist sentinel test remains in copied test_synthetic.py. Test file reads frozen source as a pure generated-fixture differential reference only; it never reads candidate files.

# Paired-ranking reader: code-only handoff

This implements binding9c0e252, BINDING SHA256`519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923`. No real candidate archive, logit or checkpoint was accessed while developing it. Only pinned input metadata, existing admitted nuisance-floor definitions and generated fixtures were used. No actual read is authorized by this folder's presence.

## Boundary and workflow

`collect_metadata.py` is a separate, independently released metadata collector. It first requires all15 opaque archive digests/roster entries. It reads only fixed JSON/TXT/LOG metadata members: task identity, fit protocol, source manifest, final checkpoint existence, finite logged losses, GPU/software, strict reference/own-fit gates, complete four-set battery and exact runtime exposure-plan receipt. It NEVER opens NPZ or weight members. NPZ digests are copied from the original pinned scorer's battery metadata and checked against the actual score bytes only after the permanent claim. Generated invalid-NPZ/invalid-checkpoint fixtures verify that this collector does not deserialize payloads.

The collector writes immutable per-fit envelopes and `READER_ROSTER.json`. An independent collector review and GO_METADATA_COLLECTION_ONLY receipt are required. The collector itself must not be invoked on actual archives until separately authorized. Metadata failures remain metadata failures, never scientific losses.

`admit.py` requires the committed pre-fit verifier, exact source/BINDING/reader/independent-review/collector-review/roster hashes, full3×5 roster, unique15 archive digests/paths, metadata envelope hashes,6250steps/no limit/last checkpoint, unchanged model/input recipe and byte gates. The exact15pre-fit plans are copied into source-pinned EXPECTED_PLANS.json and recomputed from current bound training source/metadata during the metadata-only handoff check. Runtime schedule receipts must match those exactplans and show1.6M exposures over8386row indices,124pair units, equal exact exposure digests for each seed and identical paired schedules. There is no four-of-five fallback or NEXT-reader invocation.

`read.py` validates all input populations and the candidate-independent floor table before a claim. `--admit-only` stops there without reading candidate NPZs or creating a claim. Real score access requires a separately bound GO_READER_READ receipt. It then creates the hardcoded durable O_EXCL journal `/mnt/t7/smad_next/SPRINT5_1/reader_once_v1/CLAIM.json`, fsyncs file/parent and only afterwards calls `data.arrays`. Any existing claim refuses retry, regardless of new output name or previous failure. Exactly one terminal disposition is created. Output uses a no-overwrite atomic hard link and a completion hash.

The loader checks each full underlying manifest ID order/hash and complete finite float32 array, but returns only the pinned200primary IDs,132calibration IDs and119guard-cell selections. Historical191 rows are never returned or summarized. It never loads model weights, train-score NPZs or pickle arrays. Each score member's digest must match its admitted envelope; stored own-fit and battery dev arrays must match exactly.

## Fixed statistics

Mean of per-network AUCs, never AUC of mean logits. Fixed five D strata with equal weights and no hidden bin merging. Full person/geometry graph rederived from the pinned ladder split;40primary components. Component RNG2026111401, paired-seed RNG2026111403, calibration RNG2026111404;10000draws. Precomputed ragged component-row samplers preserve the exact legacy RNG choices and row multiplicities, with generated equivalence tests. Primary draws are generated first so guard enumeration cannot change the registered primary stream. Calibration is resampled by source/component jointly across arms/seeds. Original threshold is127th/132 ascending, strict`>`; each bootstrap recomputes ceil(.95(n+1)), with+infinity if the order exceeds n.

Both optimization contrasts use .0125/.9875 quantiles, minimum gain.03, at least4positive seed effects and positive unstratified gain. Any missing-class D stratum makes that draw unreadable; more than5%unreadable prevents a positive verdict. Every draw recomputes the maximum of all15precomputed nuisance statistics. Floor bootstrap is conditional on those existing cross-fitted learner predictions; it does not refit nuisance learners or prove finite-sample coverage.

All119 genuine cells plus S4 detection guard are retained. Ranking is compared with paired-BCE at resampled calibration thresholds. Each genuine guard requires marginal upper95%bound≤+.02; detection requires lower95%bound≥−.02. The all-guards decision is an IUT, not simultaneous-cellwise coverage. Each guard uses its own person-component marginal bootstrap, shared across compared arms and coupled to the shared seed/calibration draws. Co-occurring geometry-provider component IDs are unioned within a guard cell; this respects actual dependence without pretending unique provider IDs are independent observations.

The root prospectively approved an engineering support minimum of20independent components before candidate access. Fewer components or zero bootstrap variance means INCONCLUSIVE; no conservative-bound substitute is implemented. The20threshold is not a bootstrap-validity theorem. Unexpected nonfinite guard draws fail the entire read and record counts/fraction/context in the FAILED journal. Known metadata alone show52of119cells below20; these cannot be dropped, so operational qualification is already constrained to inconclusive unless a separately reviewed valid conservative treatment is bound. Optimization evidence is still reported separately. No automatic method adoption, benchmark release or NEXT winner is produced.

## Source-only verification

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SPRINT5/paired_ranking_reader_v2/test_synthetic.py -v
```

23 generated-fixture tests cover ties/missing D strata, strict127threshold, empty-calibration infinity, score-shift control, component multiplicity/provider union, sparse/zero-variance/nonfinite guards, all120 IUT logic, seed-mean vs fused scores, switching floor maxima, all15eligibility, task/seed/source/review/roster mismatch, calibration overlap, floor-label alignment, no-overwrite claim/result, loader allowlist/nonfinite/order checks and favorable optimization with inconclusive operational status. No test is derived from actual candidate output.

`metadata_only_check.py` accepts no candidate paths and validates only bound inputs. Its report records200rows,40primary components,132calibration persons/128components and119guard cells. Neither that check nor the synthetic tests invoke the scientific reader.

## Release schemas

Metadata collector release: decisionGO_METADATA_COLLECTION_ONLY, binding_sha256, distinct author/reviewer, independent_review_path/SHA256, reader_sums_sha256 and archive_roster_sha256. Archive roster has exactly15 entries with arm,seed,task,archive_path,archive_sha256. Collector returns an augmented roster with receipt_path/receipt_sha256.

Scientific release: decisionGO_READER_READ, binding_sha256, distinct author/reviewer, independent_review_path/SHA256, collector_review_path/SHA256, reader_sums_sha256, roster_sha256, minimum_guard_components20 and zero_variance_policyINCONCLUSIVE. All files must exist and match; no permissive release template is installed. Root/Astra must independently review this implementation and all remaining operational evidence before any real invocation.
