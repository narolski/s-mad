# Look-alike eligibility [LA1-0 / SPRINT5-5]: variable-resolution aligned CelebA calibration

Prospective, 14 November 2026. This is a bounded source-calibration experiment, not detector fitting or HQ mining. The actual local HQ ZIP cannot yet be linked safely to the official PGGAN indices; this experiment does not guess that mapping or admit any HQ training image. It uses the separate correctly labelled variable-resolution aligned JPEG CelebA source already used by MS1.

## Fixed selection and separation

The existing split.csv has202084images/10177identities and agrees with every corresponding official identity label. Pin the label file SHA256`0deb3834a4e323d2db722a5a969d119662d070b0e87666a1442ed48d6efa3ac0`. With PythonRandom(2026111405), select1000persons having at least2images, then2images/person. First500persons calibrate the filter, next500validate it; partitions are person-disjoint. Original historical split labels remain in the manifest. These are source-calibration partitions, not a fresh detector benchmark or a claim of disjointness from the face recognizer's pretraining.

The selection is already materialized with all2000actual image SHA256s: `/mnt/t7/smad_next/SPRINT5_5/lowres_calibration_v1/selected_images.csv`, SHA256`2ba96c20a3b214be6cacfd951937077e98160d1b57c857a5c7948e5dc6054e52`. `SELECTION.json` records labels and RNG. No post-failure replacement of identities or images.

## CPU model path and smoke

Use actual existing `src/AR1/fr.py` image preprocessing, `prep_eval.kps`, InsightFace norm_crop and the same glintr100 graph/normalization. The original helper hardcodes CUDA, so the wrapper injects the SAME existing TorchSession with device`cpu` for recognition and detection. It does not edit third-party source or implement new image transforms. Pin helper/model bytes, assert CUDA unavailable, and verify every actual detector/recognizer parameter is on CPU. Historical helper's provider-label string is not used as proof of device. CPU measurements are not pooled with old GPU embeddings without a separate correspondence gate.

Preserve no new image/crop; retain all selected image identifiers/labels/pins, embeddings, found flags, backend/source/model receipts and logs. Embedding progress is saved every32images. First run exactly8preselected images as infrastructure smoke after independent review. Record elapsed time, shape8×512, finite normalized vectors and face-found count. A full calibration requires an independently bound smoke result hash and GO_CPU_CALIBRATION receipt. It is a finite2000image job, not an unattended monitor; measure its runtime from the smoke before starting.

## Fixed filter and noise test

Keep only complete originally selected2-image person pairs after the existing face-found filter, while retaining every failure count. No identities are replaced. Set the genuine-cosine lower cutoff to the1%linear quantile of the500-person calibration partition's complete genuine pairs. Never refit the threshold on validation.

For each validation image, compare median cosine to other images bearing its label with the largest median cosine to any other labelled identity. Flag if its own-labelled median is absent, below the fixed cutoff, or no larger than the best other-identity median. Report clean validation flag rate before injecting noise.

Inject wrong labels into a fixed10%of validation images using numpydefault_rng(2026111406), each reassigned uniformly to another validation identity. No pixel or image is changed. Report wrong-label detection rate and false flags among unmodified images. With only2images/person, injection can leave singletons and cannot always identify which image is wrong; this is a prespecified limitation, not a reason to hide false flags or tune the rule. These rates are a feasibility measurement, not certified noise rejection.

Print raw cross-identity image-pair counts and unique identity-edge counts at cosine≥.60,.70,.77 on validation. These are not fully eligible disjoint matched triplets: pose, W, sex/IED and overlap filters are absent. Raw tails cannot trigger LA1go, license generation, resolve HQ index provenance or justify training. No detector output or sealed reference set is read.

## Commands and review gate

Code: `src/SPRINT5/la1_calibration/run_cpu.py`. Metadata preparation does not run a model. CPU smoke and full calibration both require a JSON receipt binding decisionGO_CPU_SMOKE/GO_CPU_CALIBRATION, scope`LA1-0 variable-resolution aligned CelebA calibration only; no HQ admission`, distinct author/reviewer, script SHA256, selection SHA256, and actual independent-review file/SHA256. Full calibration additionally binds cpu8_smoke_pass and exact cpu8 result path/SHA256.

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python /home/narolski/smad-next/src/SPRINT5/la1_calibration/run_cpu.py --selection /mnt/t7/smad_next/SPRINT5_5/lowres_calibration_v1/selected_images.csv --out /mnt/t7/smad_next/SPRINT5_5/lowres_cpu8_v1 --review-receipt REVIEW_JSON --smoke
# After independent smoke admission, new output and GO_CPU_CALIBRATION receipt:
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python /home/narolski/smad-next/src/SPRINT5/la1_calibration/run_cpu.py --selection /mnt/t7/smad_next/SPRINT5_5/lowres_calibration_v1/selected_images.csv --out /mnt/t7/smad_next/SPRINT5_5/lowres_cpu2000_v1 --review-receipt REVIEW_JSON
```

No existing output is overwritten. Exceptions preserve progress embeddings and FAILED.json; retain a durable outer log and process status as well. All measurements stay labelled low-resolution source calibration. No scientific/model pass has been executed by this preparation owner before independent review.


## Actual image geometry correction before full execution

The original128px description was incorrect. Header audit of the SAME2000pinned images gives widths66–147 and heights79–169; only19images are exactly128×128. They are variable-resolution aligned CelebA crops. This correction changes no selected person/image, bytes, threshold, model, preprocessing, split or RNG. No resize or new filtering is introduced. The runner now records the actual dimension histogram. The old CPU8 result and mistaken metadata/failed dimension assertion remain historical evidence. The root may admit that CPU8 result after confirming the inference implementation is unchanged; the full2000-image pass requires a new source hash/review receipt. All current claims refer to this actual variable-resolution source, never a uniform128px population.
