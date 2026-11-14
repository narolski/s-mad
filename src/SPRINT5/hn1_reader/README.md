# HN native transfer reader — code only

Immutable separate adapter to paired_ranking_reader manifest02c74015…; no shared source is modified. The adopted policy is commitf18f8d1, packet4268acf…7fbc9b and ROOT_POLICY_INPUT_ADMISSION.json. This source grants no collection or scientific read release.

Exact scope: matched/self × seeds531–535, ten100-step/batch248 last checkpoints. Each fit uses248unique native rows,100exposures/image,24800forwards and one common admitted AB1Sb408 warmstart with resetAdamW moments. The effect is conditional geometry-transfer under equal source/color composition, not identity isolation or independent full-training repetitions.

The primary uses exactly200nativeS4/S3dev100rows/40fullcomponents, fixedfiveDstrata and mean per-network AUC (no score fusion). Contrast matched−self. PCG64/default_rng2026111402 draws fullcomponents within sources, accepts only label-readably populated fixedD strata until10000draws, then jointly samples a10000×5 continuation-seed matrix from that same stream. Exact adopted attempts10178/rejections178 and both drawSHA256s are verified from input metadata before claim and again in analysis. Percentile[.025,.975] is explicitly approximate and conditional on readableD strata, without unconditional95%coverage claim. No alternate seeds, component merging or draw-policy fallback.

Only the adopted descriptive point criteria mean_gain>=.03 and positive_seed_effects>=4 produce DESCRIPTIVE_TRANSFER_SUPPORT_CRITERIA_MET. The interval is always beside that label; it may include zero. No lowerCI>0, unstratified/floor positivity,5%unreadable gate, statistical-superiority or adoption rule is added. Zero variance is an INCONCLUSIVE_INTERVAL, independently of the point-criteria label. Unexpected nonfinite scores/statistics abort. Unstratified AUC and15fixed nuisance predictions are descriptive; every accepted shared draw recomputes the maximum over all15floors.

## Stages

1. `prepare_inputs.py` is candidate-free: validates adopted policy/source/input pins,534training source/geometry input pins,372native output image hashes,248ordered rows per arm,common124positives and existing direct-primary exclusion audit. Prepares immutable input binding, exact10schedules and reproduced draw report. It refuses any existing binding; never rerun over an adopted binding.
2. `metadata_only_check.py` validates the binding/floors/source provenance and exact draw hashes only; accepts no arguments. `test_synthetic.py` uses generated scores/archives/metadata in temporary directories, including invalidNPZ/weight sentinels.
3. `collector.py` requires a separate GO_METADATA_COLLECTION_ONLY release bound to codeSUMS,exactinputbinding,independentreview and exact10opaque archive roster. It opens only fixedJSON/TXT/LOG members; weights/NPZ are checked only as unique regular nonempty headers. It validates exact train/eval manifests,arch/res/budget,schedule,rowIDs,warmstart conditioning,H100software/TF32 flags,battery completeness and both mandatory zero-difference gates. It never opens score/weight member bytes. Candidate collector has NOT been invoked.
4. `read.py` requires a distinct GO_READER_READ release plus root input adoption,committed clean own/shared bindings,independent implementation/collector review,complete10fit envelopes and opaque hashes. Allmetadata/floors and draw hashes are checked before the durablecreate-only/fsynced CLAIM.json in fixed `/mnt/t7/smad_next/SPRINT5_2/reader_once_v1`. No user-overridablejournal/seed/arm/output scope. FirstNPZ access follows claim; only ownfit anddevNPZ byteequality and the200allowedID scores are returned. A postclaim failure writes permanentFAILED terminal; no automatic retry. Atomic output refuses overwrite.

The primary bytes live inside the existing21277-row AB1 pack. Parent's prospective opaque bytegate ruling permits equality checks over thatpack, while the loader returns only200primary values and never reports historical191/camera scientific metrics. No TT1/MEDS/GD payload is selected. Camera auxiliaries remain HOLD pending separate fullpopulation provenance and prospective binding. Checkpoints are never interpreted.

## Release schema

Root must separately adopt `PILOT_READER_BINDING.json` using `ROOT_INPUT_ADMISSION.json` with decisionGO_INPUT_BINDING_ONLY,author!=reviewer,exactbindingSHA,scientific_readHOLD,camera_auxiliaryHOLD,policy_input_admission_path/SHA. Current common policy-input adoption alone does not admit the new implementation binding.

Both collection/read release require: decision,experiment_idSPRINT5_2,scopePRIMARY_DESCRIPTIVE_ONLY,author,reviewer,binding_sha256,independent_review_path/SHA,reader_sums_sha256,roster_sha256,input_admission_path/SHA. Read release additionally binds collector_review_path/SHA. The archive roster has exactly10entries arm/seed/task/archive_path/archive_sha256; read roster additionally receipt_path/receipt_sha256. No real roster or live release is created here.

## Allowed verification commands

From /home/narolski/smad-next, use CPU threadlimits and the existing sparkPython. These commands contain no candidate paths:

```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/SPRINT5/hn1_reader/test_synthetic.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/SPRINT5/hn1_reader/metadata_only_check.py
```

Live collection/read are HOLD until root's separate reviewed releases. This package does not claim their completion or any scientific result.
