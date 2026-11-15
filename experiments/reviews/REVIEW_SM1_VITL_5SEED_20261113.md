# Review: SM1 ViT-L/14 five-seed reading and five-seed partner-trace AUC (results-reviewer, opus), 13 Nov 2026

Saved verbatim.

---

**Review of the SM1 ViT-L/14 LoRA five-seed reading (seeds 401–405, arm a)**

**Verdict: needs qualification. There is no error that changes a registered decision, so SM1 can stay closed.** Every number in result.md matches the JSONs.

I also re-checked the audit conversion independently. For all five seeds, `/mnt/t7/smad_next/SM1/lora_audit_vitl/a_s40{1..5}.npz` equals logit(`score_noTTA`):
- largest difference ≤1.7e-7 (float32 precision)
- ids identical
- same audit manifest sha256 prefix `dfcc916a9b1e5e40` in all five tars
- the TTA score differs by up to 0.46, so the s404 fix mattered and was applied

There are three real problems with how the result is stated:
- the intervals cover only person or key resampling and are printed without the seed spread;
- the 2-seed text calls the MorDIFF storage rise "absent", but it is positive in every seed;
- the audit-table caption and the A23 comparison still use the 2-seed 0.756.

**Findings**

1. **Correction: the MorDIFF rise is not absent.** result.md:586 says "its absent MorDIFF rise is no robustness either", and :570 says the head "shows no storage rise". In fact `rise:mordiff:mordiff` = +4.07, positive in all 5 seeds (4.41, 5.40, 2.38, 6.29, 1.88); seed SD 1.90, seed t95 [1.71, 6.43]. It is uninterpretable only because both MorDIFF EERs sit at or past chance: native 50.6, history-matched 54.7. Rewrite :586 as: "This head does not detect MorDIFF (native EER 50.6%, history-matched 54.7%, own-rule miss 99.6–100%), so its MorDIFF change under storage history (+4.1, every seed positive) is a change at chance and carries no meaning, neither failure nor robustness." Replace "no storage rise" at :570 with "no rise on the landmark cells (−0.26) and no diffusion-7 rise (−3.9, seeds −8.9 to +0.3)".

2. **Correction: the brackets understate the uncertainty.** `read_p3.py` (docstring and `summarise`) resamples persons on the 5-seed mean and treats the seeds as fixed. A12_rank does the same with keys. Seed-level spread compared with the printed brackets:

| Metric | Printed bracket | Seed SD | Seed t95 |
|---|---|---|---|
| Landmark EER | [1.73, 2.83] (person) | 0.69 | [1.45, 3.16] |
| Diffusion-7 rise | [−4.86, −2.90] (excludes 0) | 3.75 | [−8.54, +0.76] (includes 0) |
| MorDIFF native EER | — | 7.6 | [41.2, 60.1] |
| Partner-trace AUC | [0.715, 0.732] (key) | 0.032 | [0.684, 0.763] |

   The key-bootstrap interval for the AUC is about 5× narrower than the seed spread and is misleading on its own. Hard rule 1 asks for per-seed mean ± SD. Print mean ± SD (n = 5) plus the seed range first, and give the bootstrap only as "within-network sampling (seed variance not included)". Never cite the diffusion-7 person interval as "excludes 0".

3. **Correction: H-new-D at five seeds needs plainer wording.** The registered A14 decision (2 seeds, 0.756 ≥ 0.70) stands, since A14 fixed the 2 seeds and the reading was clean. Five seeds show regression to the mean, 0.756 → 0.723:
   - 2 of 5 seeds fall below the 0.70 prediction bar (0.699, 0.685);
   - the seed t95 [0.684, 0.763] straddles 0.70;
   - every seed sits far above the 0.60 falsification bar and above 0.5.

   Add to :682: "At five seeds the AUC is 0.723 ± 0.032 (range 0.685–0.756); two seeds fall below the 0.70 prediction bar and none comes near the 0.60 falsification bar. The trace is consistent; its size is about 0.72, not 0.76."

4. **Correction: the stale 2-seed caption and A23 sentence.** The caption at :690–694 still says 0.756, 2 seeds. :712 compares "retrained 0.756 (2 seeds)" with released whole-file 0.835 and claims no difference because ViT-B seeds differ by 0.06. With 5 ViT-L seeds, all lie 0.08–0.15 below 0.835. Rewrite: "retrained 0.723 ± 0.032 (5 seeds, 0.685–0.756) against released 0.835 (one network); every retrained seed lies below the released network, which is one draw of a possibly different recipe, so no recipe-level difference is claimed."

5. **Note: the zero flags on history-matched photos are not robustness.** `e7flag:own_rule` is 0.00 in every pool and seed (`e7flag_max:own_rule` 0.0). They come with own-rule miss of MorDIFF 0.996–1.0 and of the DiM cells 0.80–1.0: the own threshold sits above every diffusion-history image. The camera branch (floor-calibrated, descriptive only) flags 0.918 of the MorDIFF history pool (seeds 1.00, 0.71, 0.91, 1.00, 0.97). The 2-seed A11 line at :582 (0.85; 1.00 / 0.71) should be updated to this. Wording: "0.00 of history-matched genuine photos flagged at the head's own threshold in every pool and seed, a threshold at which the head also misses 99.6–100% of MorDIFF morphs; descriptive, not robustness."

6. **Note: housekeeping.**
   - Status header :7–11 still says "Waiting: ViT-L/14 audit scoring".
   - :577 still says "2 of the 25 ViT-L/14 fits".
   - "Train hours 3.50 per fit" should include 3:54 / 3:37.
   - The 2-seed diffusion bracket at :579 also lacks a seed label.

**Reviewed numbers**

All are 5 seeds (401–405), arm a, our frames, first-test data. The bootstrap brackets do not include seed variance.

| Quantity | Mean ± SD | Seeds | Bracket |
|---|---|---|---|
| Landmark-7 native EER | 2.30 ± 0.69% | 2.28, 2.96, 2.00, 1.33, 2.95 | person bootstrap [1.73, 2.83] |
| MorDIFF native EER (chance level) | 50.6 ± 7.6% | 51.5, 38.7, 54.0, 59.3, 49.6 | — |
| MorDIFF history-matched EER | 54.7% | — | — |

Change under storage history:
- landmark-7: −0.26 ± 0.07 (all seeds negative)
- diffusion-7: −3.9 ± 3.7 (−1.8, +0.3, −8.9, −6.6, −2.5); driven by DiM cells the head misses at its own rule
- MorDIFF: +4.1 ± 1.9 (all positive), at chance, not interpretable

Flagged history-matched genuine photos, own rule: 0.00 in all 16 pools × 5 seeds, with MorDIFF own-rule miss 0.996–1.0. At the camera threshold (floor-calibrated, descriptive), the largest pool is MorDIFF at 0.92 (0.71–1.00).

Partner-trace AUC: 0.723 ± 0.032 (range 0.685–0.756; seeds 0.755, 0.756, 0.699, 0.685, 0.721). The key bootstrap gives [0.715, 0.732], seed variance not included. Trained − KE 0.041 logit [0.029, 0.056].

**Audit-table cell** (row "SMDD partner trace", column retrained ViT-L/14):

"Within-key AUC, morphs with SMDD's five training partners over morphs with SMDD evaluation partners (same first contributor, 500 keys): 0.723 ± 0.032 (mean ± SD, 5 seeds, range 0.685–0.756); key bootstrap within network [0.715, 0.732], seed variance not included. Registered decision on seeds 401–402: 0.756, supported (A14). MADation-recipe ViT-L/14 LoRA retrained on SMDD release files; whole image, no TTA; audit set, not a benchmark."

Keep the released detector's logit gap in a separate column.

**New hypotheses: none required.** No error changes a decision. H-new-5 stays untested (no ViT-L arm c before 22 Dec). The only open question is a possible post-deadline one: does the released-vs-retrained gap (0.835 vs ≤0.756) reflect a recipe difference? It needs the release's exact training recipe and is not worth GPU now.

**Files**
- /home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/result.md (lines 566–586, 665–694, 712)
- /home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/p3_lora_vitl.json
- /home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/a14_rank_vitl_5seed.json
- /home/narolski/smad-next/src/SM1/read_p3.py, /home/narolski/smad-next/src/SM1/audit_conv.py
- /home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild/prereg.md:462 (A14)

I opened no benchmark score files, nor valx, FST or A12SP. I read only the registered SM1 JSONs and the audit-set npz files.
