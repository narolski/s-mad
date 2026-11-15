# Tail pilot reader: primary and NI adapter

This separate adapter imports only the exact paired reader utility manifest `02c74015…`. Paired, breadth and HN sources are untouched. Method inputs come from the root-adopted policy packet `4268acf…7fbc9b`, proposal `007a6f…d414`, commit `f18f8d1`. This package grants no collection or scientific read release.

The exact roster is BCE, mean and CVaR × seeds 521–525: 15 fits, 100 updates, batch 256, 25,600 forwards per fit and one common Sb408 warmstart. These are five continuation/sampler/dropout seeds conditional on that warmstart. The three arms have identical training schedules and per-image exposures within each seed, reproduced from pinned source without importing torch or loading a model. The admitted TRAIN_ONLY reference hash is checked as training metadata; it never supplies the evaluation threshold.

## Primary and uncertainty

The fixed populations contain 70 calibration positives in 26 components, 180 evaluation positives in 27 components and 288 genuine rows in six source × processing cells. Their ordered IDs, labels and person/photo/full-component provenance are pinned. Calibration and evaluation share no person, source photograph or component.

For every network, sort its positive calibration scores in float64, set `k=floor(.10*n)` and `tau=nextafter(z[k],-inf)`, and classify with strict `score>tau`. The original 70-row threshold lies immediately below the eighth ordered score. This pooled, image-weighted threshold serves all six genuine cells and every positive family. Report achieved calibration sensitivity and held-out sensitivity: 90% describes the calibration operating point, not guaranteed evaluation sensitivity. Camera order 127, zero thresholds and the training anchor are never substituted.

CVaR−mean is the primary contrast; BCE−mean is the prespecified control. Each of the six FA effects averages five paired per-network rate differences. Negative means fewer genuine false alarms. All cells and seeds remain visible; logits are not fused and no cell or arm is selected as a winner.

The bootstrap uses PCG64/default_rng `2026111403`, exactly 10,000 attempted draws. Each attempt samples full evaluation components within source, carrying all their positives and genuine variants jointly; independently samples calibration components within source; then draws five joint seed indices. All models, contrasts, cells and families share those indices. Each network’s positive threshold is recomputed. There is no redraw, filtering or component merging. An unexpected empty required genuine/calibration cell or supported positive guard is fatal. Input metadata and the generated design hash are checked before the permanent claim.

FA intervals are linear percentile [.025,.975], descriptive and pointwise rather than simultaneous. Zero variance yields an inconclusive interval. There is no favorable-effect gate or finite-sample coverage guarantee.

## Eight fixed utility guards

All four positive families × both contrasts remain in the NI family. Eligible guards use one-sided Bonferroni alpha .05/8=.00625 and margin −.02. Pass requires a lower bound >=−.02. A missing family, fewer than 20 evaluation components, fewer than 20 calibration components or zero variance means INCONCLUSIVE. Nonfinite supported draws are fatal; zero events cannot automatically pass. The 20-component minimum is engineering conservatism, not proof of bootstrap validity.

The actual family component counts are 10, 0, 17 and 17. Thus complete utility remains INCONCLUSIVE regardless of candidate effects. AF0-s61 is not replaced by an R4 proxy. No .03/4-of-5, AUC, superiority, adoption or NEXT rule is added.

## Panels still on HOLD

AUC and score-quantile diagnostics are `HOLD_PENDING_PROSPECTIVE_DIAGNOSTIC_BINDING`. Their quantile grid and AUC positive population were unspecified in the adopted packet. Root assigned that exact planning request to Astra. Proposed defaults are not approved inputs, and this does not remove the preregistered diagnostic requirement. Full scientific read stays held until the relevant plan, review and root adoption are settled and the exact implementation version is reviewed.

The frozen-baseline-threshold auxiliary needs a separate Sb408 score-member and ID binding using the same 70 calibration positives. No baseline archive is opened here. Inherited camera auxiliaries, including the 119 cells and 132-person/order-127 calibration, need separate pilot-specific provenance and binding. No TT1, MEDS or GD payload or checkpoint is selected.

## Admission and claim

`prepare_inputs.py` and `metadata_only_check.py` accept no candidate arguments. Preparation refuses to overwrite a binding. It validates source and policy pins, the admitted training reference, population overlap and identical arm schedules. Metadata reproduction gives all 10,000 attempts with no empty required genuine/calibration cells. AF0-s61 is absent in every draw; the other three positive families are present throughout.

`collector.py` requires a distinct `GO_METADATA_COLLECTION_ONLY` release, the complete opaque 15-archive roster, exact source/input/review hashes and root adoption of the new binding. It interprets only fixed JSON/TXT/LOG metadata. NPZ, checkpoint and objective-state contents are never opened; their headers must be unique regular nonempty members. It checks manifests, schedules, architecture/resolution/budget, H100 software/TF32 flags, reference hash, finite 100-step objective traces, monotone dual commits and both mandatory byte gates. BCE cannot inherit auxiliary state. No actual collector has been invoked.

`read.py` requires a separate `GO_READER_READ`, all 15 eligible envelopes, exact archive/review/roster/input/source hashes, independent collector review and clean committed source/input paths. Before claim it rechecks input metadata and all 10,000 design attempts. It then creates and fsyncs its fixed, create-only journal at `/mnt/t7/smad_next/SPRINT5_3/reader_once_primary_ni_v1/CLAIM.json`.

Only after that claim can it open the own-fit/dev NPZ pair for byte equality, returning exactly the 538 allowlisted IDs. Parent’s existing opaque AB1 byte-gate ruling permits full-pack equality without reporting historical-191 or auxiliary scientific metrics. Atomic output refuses overwrite. A post-claim failure writes a permanent FAILED terminal; there is no automatic retry, alternative journal, replacement seed or policy fallback.

## Release schema

Existing `GO_POLICY_INPUTS_ONLY` adopts method inputs, not this new implementation binding. Root must separately register `ROOT_INPUT_ADMISSION.json` with `GO_INPUT_BINDING_ONLY`, distinct author/reviewer, exact binding SHA, scientific_read HOLD, camera_auxiliary HOLD, baseline_threshold_auxiliary HOLD, diagnostic_panels HOLD and policy_input_admission_path/SHA.

Collection/read releases require: decision, experiment_id SPRINT5_3, scope TAIL_POSITIVE_CALIBRATED_PRIMARY_NI_ONLY, author, reviewer, binding_sha256, reader_sums_sha256, roster_sha256, independent_review_path/SHA and input_admission_path/SHA. Read release additionally binds collector_review_path/SHA. The exact 15-entry archive roster contains arm, seed, task, archive_path and archive_sha256; the reader roster adds receipt_path and receipt_sha256. No actual roster or live release is created here.

## Allowed verification

From `/home/narolski/smad-next`:

```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/SPRINT5/tail_reader/test_synthetic.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/SPRINT5/tail_reader/metadata_only_check.py
```

These use generated fixtures or admitted input metadata only. Passing them does not establish eligibility of actual fits or a scientific result.
