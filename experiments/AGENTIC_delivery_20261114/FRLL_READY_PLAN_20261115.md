# FRLL-Morphs final evaluation — conditional execution plan (author ruling required)
Continuation session, 2026-11-15. Status: ALL FRLL gates REMAIN as registered; this file prepares execution for the day an author ruling re-opens the read. It does NOT release the read, does NOT score anything, and does NOT change prereg.

## Gate by gate (current state)

| Gate | Required (registered sources) | State now |
|---|---|---|
| 1. Dataset inventory/labels | Verify 5 families AMSL, FaceMorpher, OpenCV, StyleGAN, Webmorph + 204 genuine (102 persons, _03 neutral, _08 smiling); per-family masks; .tem for 102 neutral originals | PARTIAL: frame-level prep artifacts complete and durable under `/mnt/t7/smad_heldout/a46_corrective_20261108/{bgr_clip,rgb_clip}/frllm_{amsl,facemorpher,opencv,stylegan,webmorph,frll_bona}`; FINAL prereg inventories the genuine side (204 photos/102 persons). A signed one-file FRLL roster with row-level SHA256 (create-only, metadata only) is NOT yet bound. |
| 2. Population/preprocessing/metrics/threshold freeze | Freeze: tamper-free population CSV, preprocessing variant (bgr_clip vs rgb_clip = same as A46 reference runtime), metric set (per-family EER, AUC, own rule, one dev-frozen threshold from pool unused in training), uncertainty procedure, complete model roster | NOT BOUND. Metrics/threshold policy already registered inside FINAL prereg §read choices (history-matched genuine side, dev threshold `127th ascending logit camera` is separate; dev threshold pool chosen before read). Need one committed roster+freeze JSON. |
| 3. Model roster incl. 4 released baselines | Frozen Sb seeds 403–407 + released SelfMAD (hrnet_w18) + released MADation B/L + MixFaceNet-MAD; retrains only if their eligibility+inclusion settled BEFORE the read, independent of performance | BLOCKED. Retrain scientific admission incomplete: technical metadata admission only (17/17 archives `COLLECTED_TECHNICAL_ONLY`; no conversion/equivalence/scientific admission). Released weights eligible. Own Sb 403–407 eligible by registration. |
| 4. Overlap/exposure disclosure | Training/development overlap + FRLL genuine exposure through MAD22 | CONTENT PREPARED (disclosure lines exist in FINAL prereg §222 and manuscript caption); needs assembly into the results paragraph. |
| 5. Reproduction checks and explicit evaluation release | Registered reproduction checks + separate `evaluation release` grant after independent review | NOT DONE. WCSS 6310087-style smoke exists only for the own 8-photo path (`FINAL/selfmad/smoke`, `scores_smoke_frll8.npz`, conditioned rows). Family-level reproduction gate never released. |

## Prepared, ready-to-run artifacts once authorization lands

1. **Sample runtime probe (create-only, ~minutes, GB10):** run the registered RS1 scorer unchanged, `--manifest <froze sample CSV of 8 already-exposed FRLL rows identical to FINAL smoke>` for one released MADation-B checkpoint and frozen Sb seed 403. Expected order-of-magnitude from measured v2r1 GB10 native runtimes (noTTA/TF32-off, batch 1): res 224 ≈ 8.4 ms/response, res 384 ≈ 19.5 ms/response → 7,127-row approved eval (METADATA_CAPTURE counts) ≈ **1.0–3.5 min GPU per model-seed on-batch-1** (batch 32 will be faster; dominant cost will be image I/O/preprocess, not forward).
2. **Full registered read after release (single-pass):** one manifest, all 5 families, seeds 403–407 for Sb, plus released baselines, dev-frozen thresholds, outputs `/mnt/t7/smad_next/FINAL/frll_read_v1/` create-only; per-family EER + attack-miss/genuine-FA at development-frozen thresholds; no re-read.
3. **Manuscript targets:** `results.tex` FRLL paragraph + `tables/` family table (currently pending cells).

## Stop rules (unchanged)

- No author ruling → nothing runs, pending cells stay pending, no numbers imagined.
- Any unresolved gate → no read. FRLL can never be described as wholly untouched by this project (204 genuine already exposed through MAD22 — disclose regardless).
- Runtime numbers generated here are execution-cost estimates, not scientific results.
