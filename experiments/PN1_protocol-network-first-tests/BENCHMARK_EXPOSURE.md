# PN1 benchmark exposure (from the record only)

Written 12 Nov 2026 (`date`: Thu Nov 12 08:11:57 AM CET 2026) after the author's ruling: "We can't use the set for
development we're using to benchmark methods, that is a grave error. We are aiming for CVPR."

**Sources and limits.**
- This file is written from prereg.md, result.md, README.md, the committed JSON files and the git log.
- No score was computed and no score file was opened beyond what is already in result files.
- "Seen" means the numbers were printed in a committed result file, a report to the lead, or a review.

**Plain summary.** PN1 used published benchmarks as development data from its first registration onward.
- H1, corrected MAD22 and FRLL / FRLL-Morphs were gating or reporting cells of the registered marks (P-c2, P-d, P-e, P-g; prereg sections 6–8, commit dce4ae6, 11 Nov 19:08).
- They were read for every tier-0 head, every tier-1 network and the reference row.
- Several later choices were made after those numbers were seen.
- For PN1-family networks these three benchmarks are compromised. They can be reported only with that label.

## 1. Sets, networks, registrations, numbers seen

| Benchmark set | What was scored | Registration (first commit) | Numbers seen (where) |
|---|---|---|---|
| H1 (CASIA-WebFace Poisson face splices, 598 morphs / 598 genuine, 112 px) | Tier-0 frozen heads A0, B0, Bn0 (CLIP ViT-L/14, DINOv3) at seeds 401–405. Spliced heads S-a, S-b and the face-only head F. Face-blanked H1 copies. The eight tier-1 networks A, B, Bn, C × 401/402. The eight reference-row SMDD retrains. Sb and Bv × 401/402. | Initial registration dce4ae6 (P-d: H1 AUC ≥ 0.85; P-g gating family). Amendments 8 (eee624d), 9 (00bed1d), 10 and 11 (1c52cbe), 12 (1ab1256). | H1 AUC of every head and network. Own-rule and τ_cam genuine flags (0.3–25.6% / 99.5–100%). Morph miss. Post hoc paired morph-above-own-host shares (posthoc_b2, 33f4d0c). Sb's H1 gains +0.13 / +0.23 over B, +0.06 / +0.09 over A. Read in result.md, README 5.1d–f, tier1/*.json, tier1_sb, tier1/posthoc_b2.json, and the reviews REVIEW_PN1_TIER1 and REVIEW_PN1_BATCH2. |
| Corrected MAD22 (OpenCV, Webmorph, FaceMorpher, MIPGAN I/II; genuine = the 204 FRLL photos) | The same heads and networks as H1, on the full cells of the AD4 evaluation manifest (tier 1) and the bench_s subsample (tier 0). Face-blanked MAD22 copies (amendment 11). | dce4ae6 (P-e: history-matched EER on MAD22; P-g gating cells MAD22 OpenCV and Webmorph). Amendments 8, 9, 11. | E7 and native EER / AUC for OpenCV and Webmorph (headlines). Fixed-rule flags and misses of every MAD22 cell (tier1 JSON). Resampling ranges of the frozen heads. C − A Webmorph E7 EER differences. HN3 raw-file formats and blockiness correlation (followups.json). |
| FRLL (genuine native, benign variants jpeg90/70/50, blur1, resample50) and FRLL-Morphs (AMSL, FaceMorpher, OpenCV, StyleGAN, Webmorph; orig and E7 pools) | The same heads and networks (tier 1 on the full AD4 cells; tier 0 on bench_s and frll_e5). JPEG verification reproduced 4 FRLL jpeg70 evaluation files, an image check only. | dce4ae6 (fixed-rule table (f); P-c2 kernels and E7 strengths; JPEG mark), amendment 1. | FRLL native, jpeg and blur flags at τ_0.5 and τ_cam (30–95% at τ_cam). E7 pool flags (P-c2). FRLL-Morphs cells printed (non-gating). Native eye-distance table beside the flags (native_history.json). |
| FFHQ-Morphs and FFHQ genuine (`/mnt/t7/smad_heldout/ffhq_morphs`) | The eight tier-1 networks on ffhq_bona orig 2,000, landmark_complete orig 1,000 and landmark_complete resmatch 2,000. landmark_combined, stylegan_w, stylegan_wplus and diffae have not been scored. | Amendment 13 (a1c6664, before any score); read in a51ca22. Post hoc paired table 33f4d0c. | HN2 flags 3.5–22.5% (own rule) and 95–98% (τ_cam). AUC 0.988–1.000 and history-matched 0.935–0.999. Paired history shares (A 0.72 / 0.78, others 0.30–0.44). |
| FEI (gtest, 385 genuine, 1,000 morphs) | No score of any PN1 network. Manifest metadata only (native size, eye distance, format) for native_history.json. | — | Metadata only. |
| MorDIFF, DiM (all variants) | Not scored by PN1. Not in pn1_eval.csv. | — | None. |
| Sealed sets (valx, FST, A12SP) | Never opened. | — | None. |

The 8 reference-row networks (A12-BR SMDD retrains, another program's recipe) were scored by PN1 on the same H1, MAD22
and FRLL cells (amendment 5, 9bb7295). Those numbers were seen in result.md.

## 2. Choices the benchmark numbers could have influenced

1. **The C (JPEG) contrast.**
   - The C − A contrast on MAD22 Webmorph E7 (−10.6 / −13.6 points) was picked out after the tier-1 read, as the strongest arm difference.
   - It entered HN6 of the fresh-seed draft v1/v2 as a prediction to replicate.
2. **Selection of Sb for a refit.**
   - Sb was killed by its own rule.
   - The batch-2 review then read its H1 gains (+0.13 / +0.23 over B; "above all 8 reference seeds") and recommended refitting it.
   - The plan v3 was built on that recommendation. Its stated grounds were development-ladder reads, but the recommendation came after H1 had been seen.
3. **Margins 0.05 and −0.02.**
   - These were fixed for the fresh-seed contrasts while knowing the 401/402 H1 gains.
   - They are kept in the development-only plan (v4) for landmark_combined, and this is disclosed there.
4. **P-c′.**
   - It was written after tier 1, on the test ladder, with thresholds that B, Bn and C already met and A failed.
   - It was shaped by the tier-1 flag results, which include the FRLL / H1 τ_cam failures that motivated "a mark not read on the saturated floor".
5. **HN2 on FFHQ landmark_complete (amendment 13).** It was registered before scoring, but it is a read of an FFHQ family that the main registration's draft named as a possible endpoint (REGISTRATION_DRAFT lines 46–47). The post hoc FFHQ paired table (33f4d0c) re-read the same scores.
6. **The threshold-transfer framing.**
   - "Thresholds do not transfer to unseen genuine sources" rests on FRLL, H1 and FFHQ flags.
   - The step-1 design of the fresh-seed v2 (τ_multi, leave-one-source-out, FRLL and H1 as test pools) was built on those numbers.
7. **The loss-rule reading and the "protocol costs face-spliced detection" sentence.** Both rest on H1 (P-d) and MAD22 (P-e, P-g).
8. **The tier-0 "best of 8 heads" lead.** Protocol plus spliced on DINOv3, MAD22 2.0 / 3.0%, was chosen on MAD22 and labelled "a lead to re-test". It motivated amendment 10 (the Sb LoRA arm).
9. **HN7 (amendment 14 draft).** It was defined against H1 AUC with all 12 H1 values known. The revived development version uses FFHQ landmark_combined instead.

10. **The FFHQ storage mark (FS1 contrast 2).**
    - Its 0.65 threshold and A's positive control were set knowing the 401/402 paired shares on the same FFHQ images: A 0.72 / 0.78, others 0.30–0.44 (post hoc table, 33f4d0c).
    - FFHQ is a development set by designation, but this choice was not blind.

## 3. Status of each set for PN1-family networks

Lead's designation, 12 Nov (`date` above):
- FFHQ (genuine and all morph families) is the development comparison set of this sprint and will not be reported as a benchmark.
- FRLL, MAD22, MorDIFF, DiM, H1, FEI and the sealed sets stay sealed for candidate networks until the method is frozen.

| Set | Status for PN1-family networks |
|---|---|
| H1 | Compromised (read for every PN1 network; shaped choices 2, 3, 7, 8, 9) |
| Corrected MAD22 (all cells) | Compromised (read for every network; shaped choices 1, 7, 8) |
| FRLL and FRLL-Morphs (all cells, benign variants) | Compromised (read for every network; shaped choices 4, 6) |
| FFHQ-Morphs / FFHQ genuine | Development set by designation (not a benchmark); landmark_complete already read |
| FEI (gtest) | Clean for scores (metadata only) |
| MorDIFF | Clean |
| DiM | Clean |
| Sealed sets (valx, FST, A12SP) | Clean (never opened) |

## 4. What a single sealed final read would look like

1. **Freeze.** One network configuration is frozen on development data only: arm, recipe, seeds, last checkpoint, and the threshold rule fixed on development genuine pools. It is committed with the sha256 of the weights, code and lists.
2. **Sets.**
   - Clean sets as the primary report: MorDIFF, DiM (all variants), FEI-based gtest, and the sealed sets if the main registration assigns them.
   - Compromised sets (FRLL-Morphs, MAD22, H1) may appear only in a separate table labelled "seen during development (PN1)", never as evidence of generalisation.
3. **Metrics.**
   - Per family: EER on the history-matched E7 pool (the main registration's reading rule).
   - At the frozen threshold: BPCER on genuine and APCER per family.
   - AUC printed.
   - One number per set, no selection across seeds or checkpoints.
4. **One read.**
   - The scoring scripts and lists are pinned before the read.
   - The read is run once by the lead (or another person who did not tune the method).
   - Results are committed unaltered with the git hash of the frozen configuration.
   - No re-run after seeing results, except an infrastructure failure re-run unchanged.
