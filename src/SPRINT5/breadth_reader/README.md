# Breadth pilot reader — primary descriptive scope only

This is a separate adapter for SPRINT5_4. It does not modify or broaden the frozen ranking reader. Its utilities are imported only after verifying the complete frozen source manifest `02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c` and every listed dependency. The borrowed input binding remains `519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923`.

No actual candidate archive, roster, checkpoint or logit file was accessed during implementation. Generated archives/scores were used in tests. Actual training manifests, source-photo/person/geometry metadata, immutable source files and already admitted candidate-independent nuisance-floor inputs were checked.

## Exact pilot and inputs

Ten fits are required: narrow_more_variants and broad_fewer_variants, seeds511–515. Each fit uses100updates, batch32,3200image forwards, exactly32unique training images and100exposures per image, last checkpoint. The fit source manifest is fixed to `debbea9496cdcd553cf2b18671f0868452cfdc9cc16fa7ee66b0e81b97361a04`. There is no15-fit ranking fallback, seed replacement,6250-step allowance or smoke-to-pilot substitution.

The reader input binding is `experiments/SPRINT5_20261114/breadth/reader_implementation/PILOT_READER_BINDING.json`, SHA256`bf5c55bc6d6663f57be70503c68c939f6b0e0f579513548973e423cdc118e808`. Root adopted inputs only in ROOT_INPUT_ADMISSION.json; this is not permission to collect or read candidate payloads. The binding includes all inherited input pins, ten actual training manifests/assets, exact expected row/exposure receipts and a source-photo/person/geometry audit. All ten cases have no recorded primary overlap, including full person components. Narrow16-person units are nested in broad32-person units. Unit identities and actual pixel contributors remain distinct: S3 contributes its host's pixels; partner landmarks/hull count as geometry exposure.

The exact200native development S4/S3 rows,40full person/geometry components, fixed five D strata/edges and15existing nuisance predictions are reused. Existing nuisance predictions are not refitted or selected after candidate outcomes. This binding does not certify biometric duplicate exclusion beyond the recorded source provenance.

Camera calibration/utility is HOLD. This adapter never opens the TT1/MEDS/GD score payloads or computes a camera threshold/guard. The inherited camera metadata is checked as part of the immutable shared package, but no camera analysis is authorized or performed. Historical191 rows may be checked opaquely for complete dev manifest order/byte identity but are never returned or summarized.

## Pilot-specific statistics

The primary is broad-minus-narrow in the mean of five per-network, equal-five-D-stratum AUCs. It is not AUC of averaged logits. Five seed indices are resampled jointly for both arms, reflecting joint subset/optimizer/dropout variability. This is a tiny-data breadth-versus-capture/orientation budget contrast, not an isolated identity-count effect or full MAD superiority claim.

Exactly10000replicates use one numpydefault_rng(2026111404). Each replicate first draws full components within sorted source strata, retaining selected component multiplicity, then draws five paired seed indices. The same draw evaluates both arms and all15floor predictors; their maximum is recomputed each time. Root prospectively approved this order and the following descriptive missing-stratum policy before candidate access.

A draw with a missing class in any fixed D stratum is structurally undefined. It is retained with a null statistic and is never redrawn, merged or replaced. The exact metadata-only design has9849readable draws and151undefined draws,1.51%; its digest is `e00a90fec579dab0ce4c73245bbc4e644ef1c0f56e56a15f6b2698be87687bd9`. Report total/readable/undefined counts and all undefined indices. When any draws are undefined, call the endpoint a **95% percentile bootstrap interval conditional on readable draws**; make no unconditional95%coverage claim. Fewer than two finite draws or zero variation gives an INCONCLUSIVE interval. Unexpected nonfinite arithmetic on a structurally readable draw is fatal, not filtered.

Outputs retain all10000replicate records, per-seed effects, per-source unstratified cells, ordinary unstratified AUC and descriptive per-arm comparisons with the maximum nuisance floor. There is no .03gain threshold,4-of5success rule,5%unreadable decision gate, superiority/adoption verdict or NEXT-selection field. Floor comparisons are conditional on the existing cross-fitted nuisance predictions; they do not refit learners or prove finite-sample confidence coverage.

## Admission and irreversible read boundary

`collector.py` requires a separate independently reviewed GO_METADATA_COLLECTION_ONLY receipt, adopted input-binding hash and all ten opaque archive digests before reading any archive member. It interprets only fixed JSON/TXT/LOG metadata. Archive headers establish final-checkpoint/score presence; it never opens NPZ or checkpoint bodies. Score digests are copied from original scorer metadata. It checks source/task/arm/seed, exact100×32exposure receipt and row order, model/input shape, completed finite logged training, full four-set battery, H100/software/TF32/precision and strict2496reference plus21277own-fit byte gates. Unknown scientific payloads are ignored; duplicate/oversize requested metadata members fail through the frozen helper.

The collector writes immutable per-fit envelopes and READER_ROSTER.json. This does not create a scientific claim or authorize any score read. `admission.py` independently validates the committed clean input/reader source, all ten cases/digests, metadata hashes and separate collector/implementation/input reviews.

`read.py --admit-only` validates these envelopes and candidate-independent input/floor schema but stops before journal or NPZ access. The actual read requires a separate GO_READER_READ receipt. It creates and fsyncs the hardcoded O_EXCL claim `/mnt/t7/smad_next/SPRINT5_4/reader_once_v1/CLAIM.json`, then opens only the ordinary and battery **dev** NPZs. Full manifest ID order/hash, float32 finiteness and own-fit byte equality are checked; only the200primary IDs are returned. No model is loaded. No camera/historical output is returned.

Any existing claim refuses retries, even after failure or with a new output path. There is exactly one terminal disposition. The result is atomically published without overwrite and its hash is recorded. A failed read remains failed and needs prospective independent repair; no automatic new journal, seed selection or rerun is implemented.

## Release fields

Both collector and reader releases require experiment_idSPRINT5_4, scopePRIMARY_DESCRIPTIVE_ONLY, distinct author/reviewer, binding_sha256, independent_review_path/SHA256, reader_sums_sha256, roster_sha256 and input_admission_path/SHA256. The input adoption is the exact root GO_INPUT_BINDING_ONLY artifact, with its independent policy/root policy hashes and scientific_read/camera HOLD. The collector decision is GO_METADATA_COLLECTION_ONLY; the scientific decision is GO_READER_READ and additionally binds collector_review_path/SHA256. No permissive release template or actual candidate roster is installed.

Invoke only after those independent releases. Root alone registers them. Direct entry is the absolute breadth `read.py` path; tests explicitly select this entry by file path because the borrowed frozen directory also contains a `read.py` module.

## Verification already performed

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SPRINT5/breadth_reader/test_synthetic.py -v
```

Eighteen generated-fixture tests passed. They cover exact10roster/duplicates, wrong source/seed/manifest/platform/steps/precision, exposure/order drift, tolerance/partial/nonfinite gates, review/source/binding pin changes, exact registered RNG order, missing-stratum conditional intervals with no redraw, degenerate/nonfinite failure, mean AUC versus fusion, paired rather than armwise seed draws, positive/negative descriptive controls, changing floor maxima, no historical/camera return, no camera-payload parsing, permanent claims/no overwrite, admit-only boundary and metadata parsing of invalid-NPZ/invalid-checkpoint fixtures.

`metadata_only_check.py` accepts no candidate paths and reproduces the exact bound inputs/readability digest. It does not invoke a collector or scientific read. Independent implementation review and both actual collection/read releases remain pending. No job, rental, scheduler action or manuscript/result change was made by this owner.
