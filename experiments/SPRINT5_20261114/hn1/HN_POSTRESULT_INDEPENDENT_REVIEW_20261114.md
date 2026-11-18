# HN registered pilot — independent postresult review, 2026-11-14

Reviewer: Astra; independent of reader/training author Sol. **PASS for saved-result arithmetic and integrity; scientific outcome CRITERIA_NOT_MET.** This is an adverse descriptive point result, with an interval including zero. No method adoption, identity-specificity, deployment utility or benchmark claim is supported.

## Binding and admitted scope

Reviewed only the already-released RESULT.json and its saved 10,000 bootstrap replicates, frozen reader source, binding/policy metadata, root release, once journal, and ten admitted metadata envelopes. No raw candidate archive/NPZ, checkpoint, source image, camera array, baseline payload or sealed benchmark was opened. The reader was not rerun; no new claim or bootstrap resampling was created.

Exact pins independently checked:

- RESULT `/mnt/t7/smad_next/SPRINT5_2/reader_output_v1/RESULT.json`: `75af6d39e40126085ef05c1cbc83f3ea687c9b714af97dc74c6759290cbb3104`.
- Reader source manifest: `a8a083a686ab47cf8f02e5a7da9e6dec92a797e33c5ec9b4e75f979e30400794`; every listed source file verified.
- Input binding: `51ae40530ee4a848aece44693c143923a68636eb769468e5e5637904ab8eede3`.
- Root GO_READER_READ release: `e1938e1b14458789060974c5036d29240ff6a3f12e8e564bb186ecb3f88058ea`; committed at `c67fd5dc00012648012878a4b571cdbb54e42fda`.
- Prior actual metadata eligibility review: `731145d479dc721cfc1d3173986bdabcd95128db943ef203f54c4633d368e798`.
- Reader roster: `cc7fb2a7b96d39dd7735281db79f9e53d7832e64676de1f4307709cfef351742`.
- Once CLAIM: `228b94c276455ef2266463346d4bf7d279a480c2f937ae582e41c883b7e4ee45`; TERMINAL: `2725aa21c9559907f7cd00f88d46e63ad1875b78f1352494f2a42d242cecd9cd`.

Claim, release, result and roster pins agree; terminal is COMPLETE and its digest equals the actual RESULT bytes. Source places the permanent claim before payload access. Execution receipt records native exit0, start18:29:40.711707Z/end18:30:16.975767Z (36.264060 seconds), result/once present. This verifies the retained execution chain, not an independent reconstruction of raw model inference.

## Recomputed primary result

Statistic: per-network equal-five-fixed-D-stratum AUC, then five paired continuation-seed differences, matched minus self.

| Seed | Matched AUC | Self AUC | Matched − self |
|---|---:|---:|---:|
| 531 | 0.656103932 | 0.661676457 | −0.005572525 |
| 532 | 0.658107691 | 0.665241463 | −0.007133772 |
| 533 | 0.660672697 | 0.666523966 | −0.005851269 |
| 534 | 0.660392701 | 0.667026472 | −0.006633772 |
| 535 | 0.658387688 | 0.665521460 | −0.007133772 |

Means: matched **0.658732942**, self **0.665197964**. Mean difference **−0.006465022**; positive seeds **0/5**. Registered descriptive criteria are mean gain≥0.03 and at least4/5 positive: both fail. No new CI, floor-win or unstratified-positivity gate was added.

Independently recomputed linear percentile endpoints from all saved replicates: conditional descriptive95% interval **[−0.017471519, +0.000017188]**. The very small positive upper endpoint must not be rounded to a negative endpoint or used to claim significant inferiority. It is consistent with zero; neither support criteria nor statistical superiority is established. Unstratified descriptive mean difference is −0.0059; it does not replace the registered primary endpoint.

## Bootstrap and nuisance context

Exactly10,000 saved draws numbered0–9999; every saved arm-mean difference agrees with its saved contrast. Recomputed joint paired-seed-index digest `eb04e4b3ff18af8075453852642c7c0f1640b3a62e9879a01af25ccca03ab239` agrees. Registered input-only readability metadata and result agree on10,178 attempts,178 rejected (1.7488701%), RNG2026111402, component digest `0f045d8b9e71ebd627702a362bd473356de4091bec3aa6322bf92757c87f8dbd`. All component draws precede the joint seed matrix. Component-index streams are not stored in RESULT, so their digest is checked against pre-read metadata/source, not regenerated here. Coverage is conditional on every fixed D stratum retaining both classes, not an unconditional95% guarantee.

All15 fixed nuisance predictors are retained; their maximum point AUC is **0.750884398** (all_cue__logreg). Matched minus this maximum: **−0.092151457**, descriptive interval **[−0.224676846, +0.067284396]**. Self minus maximum: **−0.085686435**, interval **[−0.216969616, +0.071657135]**. Both intervals were independently recomputed from the saved per-draw arm means and saved maximum floor. Source computes the maximum over15 again within each shared accepted draw. This review does not recompute those maxima from raw nuisance predictions. Floor comparisons remain descriptive, not an added qualification gate.

Preserve separate native construction-floor context: max AUC **0.7433476**, conditional CI **[0.7125105,0.7959151]**, luma0.6043131, color0.5680630. It is neither the current dev-floor maximum nor an independently held-out construction/identity-specificity result.

## Complete cohort and limitations

Verified exact ten task IDs `SPRINT5_2_pilot_v1_{matched,self}_s{531,532,533,534,535}` against the roster and ten hash-bound collector envelopes, with all ten archive digest strings identical across roster/claim/result. Each envelope records training complete, checkpoint saved,100updates, batch248 and24,800forward images. Each envelope's SHA is recorded in the accompanying independent verification JSON. No best-seed substitution or fit omission.

All ten share one admitted AB1 Sb408 warmstart with fresh AdamW moments. These are five paired continuation/dropout seeds conditional on one warmstart, **not five independent full-training initializations**. Warmstart provenance follows the admitted archive/extraction chain; no independent checkpoint rehash is claimed. Per-fit training durations are **not recorded in the allowed collector envelopes** and therefore are not independently verified here; reference-gate seconds are not training duration. Reader wall duration above is verified separately. This reporting limitation does not change the already-admitted endpoint or its registered criteria.

Allowed narrow claim: “In this fixed native geometry-transfer pilot on200development rows/40full components, matched-target continuation did not meet the prespecified descriptive improvement criteria over self-target continuation; all five paired point differences were negative, and the conditional descriptive interval included zero.” Matching changes geometry/resampling while retaining source/color composition; this does not isolate identity specificity or establish general utility. No adoption or benchmark inference; camera auxiliary remains HOLD. Preserve all adverse outcomes and the permanent journal; no automatic retry or new read is justified by this result.

Evidence: `HN_POSTRESULT_INDEPENDENT_VERIFICATION_20261114.json` and `HN_POSTRESULT_VERIFY_20261114.py` alongside this review. The verification script uses standard-library arithmetic only and never imports or invokes the scientific reader. One initial reviewer-script path-resolution error (manifest-relative files resolved to repo rather than source directory) was corrected before the passing run; no scientific data or frozen source changed.
