# The sealed MAD22 read of the frozen candidate (FINAL): result

The read ran once, on 13 Nov 2026 (machine clock, CET). Registration: `prereg.md` (a7d7454); amendment G1 and the pin
addendum: a2d6dc9. This file gives numbers and registered verdicts only. The verdict strings are exactly as the reader printed them; the
per-detector and secondary tables were assembled from `final_read.json` and checked against it. Results review
(results-reviewer, opus): `experiments/reviews/REVIEW_FINAL_MAD22_20261113.md`. Its corrections C1-C9 are applied
here.

**Labels attached to everything below.**
- "Seen during development (corrected MAD22; genuine side = the 204 FRLL photos)".
- FaceMorpher, and every mean that contains it: "shortcut-saturated (a morph-free network reaches 0.0% EER on this
  cell, AD4): no state-of-the-art sentence".
- MIPGAN-I, MIPGAN-II, and every mean that contains them: "not shown to be morph-specific: the network flags one-photo
  GAN renders". The MIPGAN E7 pool equals the native genuine photos by construction.
- "Frozen by the authors' decision on 13 Nov 2026; the registered freeze rule did not freeze any method."
- "Its recipe had been chosen after benchmark scores of earlier seeds (401/402) were seen; the networks 403-407 were
  never scored on any benchmark before this read. The frozen networks' scores on the 204 FRLL genuine photos now
  exist." (C6; BENCHMARK_EXPOSURE choice 8: the tier-0 lead that motivated the Sb LoRA arm was chosen on MAD22.)
- "For the released detectors, morphs are the raw benchmark files and the history-matched genuine photos pass through
  our aligner; each release is compared at the better of its raw-genuine and aligned-history forms."

## Run record

| Step | What happened |
|---|---|
| Lease | final2, instance 60540801, A100 PCIe 40 GB (offer 54026813), rented by the lead. The GPU name is exactly "NVIDIA A100-PCIE-40GB" (GPU-cfd72d54…, driver 610.57.04). |
| Stage | 5.76 GB uploaded in 186 s; pack sha256 5ec63472… and scripts verified on the host (20:58:13). |
| Gate dry run | Development rows only, 20:58:50-21:01:02: 5 of 5 byte-identical; each network 6,613 rows, max \|Δ\| 0.0, 0 rows differing, 0 flips. Result `FINAL_mad22_final2_dryrun.tar`. |
| Start | Only after the lead's word "START the sealed MAD22 read on final2": 21:02:37. |
| The read | The gate passed again (5 of 5, max \|Δ\| 0.0), then 9,930 rows × 5 networks. rc 0. FINAL_DONE at 21:06:50. Two copies verified: sha256 c5205a5835176d6589d3c1d5f5544dbcbc9213633c1e37f55119de2201e07ead. |
| Platform | torch 2.2.1, CUDA 12.1, cuDNN 8902, timm 1.0.27, numpy 1.26.4, Pillow 10.2.0; TF32 on (rescore_tf32.py); float32; batch 64. |
| Reader | Run once, default pins and marker (`/mnt/t7/smad_next/FINAL/READ_ONCE_FINAL_mad22/done`). Outputs `final_read.json` (sha256 ee9b6bce…) and `final_tables.md` (859e60a7…). |

- `n_differs` is empty for every cell (n table below).

## Primary endpoint (registered)

History-matched form, mean EER over OpenCV, Webmorph, MIPGAN-I and MIPGAN-II (`mean4`).

| | Value |
|---|---|
| Ours, seeds 403-407 | 2.5, 4.6, 3.9, 4.2, 1.7%; mean 3.37% (SD 1.2); two-level 95% interval [2.04, 4.96] |
| Best comparison | SelfMAD (raw genuine photos), 4.72% |
| Difference (ours − best) | −1.4 points [−3.51, +0.98] |
| p(d ≥ 0) | 0.122 |
| p(d ≤ 0) | 0.879 |
| p(d ≥ +1.0) | 0.02499 (threshold 0.025) |
| Seeds individually lower | 5 of 5 (used only by the "exceeded" rule; s404 4.61 against 4.72) |
| **Registered verdict** | **"matched"** |

**Reader's primary sentence:** "On corrected MAD22 (seen during development; genuine side the 204 FRLL photos), against
genuine photos with aligned-frame history (our aligner plus history), the frozen network's mean EER over OpenCV,
Webmorph, MIPGAN-I and MIPGAN-II (FaceMorpher is solvable without morphs and excluded) is within one point of the best
released detector (SelfMAD (raw genuine photos)): difference -1.4 points [-3.5, 1.0] (non-inferiority margin +1.0
point)."

**Primary sentence, as registered (§6 with the M4 rule; C1):** "On corrected MAD22 (seen during development; genuine
side the 204 FRLL photos), against genuine photos with aligned-frame history (our aligner plus history), the frozen
network's mean EER over OpenCV, Webmorph, MIPGAN-I and MIPGAN-II (FaceMorpher is solvable without morphs and excluded)
is within one point of the best released detector (SelfMAD, raw genuine photos): difference −1.4 points [−3.5, +1.0]
(non-inferiority margin +1.0 point). On the two landmark families alone (OpenCV, Webmorph) the verdict differs: the
network is not separated from SelfMAD (raw genuine photos), difference −1.0 points [−4.7, +3.0]. Half of the
four-family mean is the two MIPGAN cells, where the network is not shown to be morph-specific (it flags one-photo GAN
renders)."

**Fragility (post hoc, descriptive; the registered verdict stands; C2).**
- The verdict is at its threshold: p(d ≥ +1.0) = 0.02499 against 0.025. That is 49 of 2,000 replicates beyond the
  margin; one more would give "comparable, not separated".
- The standard form (the same comparison with native genuine photos) gives p = 0.0255, "comparable, not separated".
- Re-running the registered bootstrap with 20,000 replicates gives p = 0.023. Over 200 other random seeds, 74% give
  p ≤ 0.025 (reviewer's scratch recomputation).
- The non-inferiority is therefore borderline, and the point advantage (−1.4) is not significant (p(d ≥ 0) = 0.12).
- For the means, the best comparison is the single release with the lowest mean, not the best release per family
  (C8). Against SelfMAD (raw genuine), the H differences per family are:

  | Family | Difference (points) |
  |---|---|
  | MIPGAN-I | −1.9 |
  | MIPGAN-II | −1.4 |
  | OpenCV | +1.2 |
  | Webmorph | −3.3 |

  Against the per-family best releases, the mean difference would be −0.7.

**Landmark-only rule (M4).** The reader printed: "Landmark families only (OpenCV, Webmorph), history-matched:
comparable, not separated against SelfMAD (raw genuine photos) (differs from the primary verdict; the primary sentence
must say so)."
- `mean2` ours 6.32% against 7.37%; difference −1.0 [−4.7, +3.0].

## Per family and means, every form

Seed-mean EER %. The best comparison is the release with the lowest point EER. The difference carries its 95%
two-level interval. Family verdicts use Holm across the five families; mean verdicts are unadjusted.

| Form | Cell | Ours (seed mean) | Best release (EER %) | Difference [95%] | Verdict |
|---|---|---|---|---|---|
| S | FaceMorpher | 2.3 | MADation ViT-B/16 (0.0) | +2.3 [+0.9, +4.2] | lost |
| S | MIPGAN-I | 0.6 | SelfMAD (2.5) | −1.9 [−3.7, −0.3] | matched |
| S | MIPGAN-II | 0.3 | SelfMAD (1.7) | −1.4 [−2.8, −0.2] | matched |
| S | OpenCV | 2.3 | SelfMAD (1.0) | +1.3 [−0.6, +2.9] | comparable, not separated |
| S | Webmorph | 10.7 | MADation ViT-B/16 (11.0) | −0.3 [−6.7, +6.4] | comparable, not separated |
| S | mean4 | 3.5 | SelfMAD (4.7) | −1.3 [−3.4, +1.0] | comparable, not separated |
| S | mean5 | 3.2 | SelfMAD (3.8) | −0.6 [−2.4, +1.4] | comparable, not separated |
| S | mean2 | 6.5 | SelfMAD (7.4) | −0.9 [−4.6, +3.1] | comparable, not separated |
| H | FaceMorpher | 3.7 | MADation ViT-B/16, raw genuine (0.0) | +3.7 [+1.6, +6.1] | lost |
| H | MIPGAN-I | 0.6 | SelfMAD, raw genuine (2.5) | −1.9 [−3.7, −0.3] | matched |
| H | MIPGAN-II | 0.3 | SelfMAD, raw genuine (1.7) | −1.4 [−2.8, −0.2] | matched |
| H | OpenCV | 2.3 | SelfMAD, raw genuine (1.0) | +1.2 [−0.5, +3.1] | comparable, not separated |
| H | Webmorph | 10.4 | MADation ViT-B/16, raw genuine (11.0) | −0.6 [−7.2, +6.2] | comparable, not separated |
| H | **mean4 (primary)** | 3.4 | SelfMAD, raw genuine (4.7) | −1.4 [−3.5, +1.0] | **matched** |
| H | mean5 | 3.4 | SelfMAD, raw genuine (3.8) | −0.3 [−2.2, +1.6] | comparable, not separated |
| H | mean2 | 6.3 | SelfMAD, raw genuine (7.4) | −1.0 [−4.7, +3.0] | comparable, not separated |
| BE_S | FaceMorpher | 4.4 | MADation ViT-B/16 (0.0) | +4.4 [+2.4, +6.5] | lost |
| BE_S | MIPGAN-I | 0.9 | MixFaceNet-MAD (16.3) | −15.4 [−20.5, −11.1] | exceeded |
| BE_S | MIPGAN-II | 0.5 | MADation ViT-L/14 (16.3) | −15.8 [−20.2, −11.8] | exceeded |
| BE_S | OpenCV | 2.3 | MADation ViT-B/16 (4.0) | −1.7 [−5.1, +0.7] | comparable, not separated |
| BE_S | Webmorph | 10.7 | MADation ViT-B/16 (11.0) | −0.3 [−6.7, +6.4] | comparable, not separated |
| BE_S | mean4 | 3.6 | MixFaceNet-MAD (15.9) | −12.3 [−16.5, −8.2] | exceeded |
| BE_S | mean5 | 3.8 | MixFaceNet-MAD (13.7) | −9.9 [−13.7, −6.2] | exceeded |
| BE_S | mean2 | 6.5 | MADation ViT-B/16 (7.5) | −1.0 [−5.5, +3.1] | comparable, not separated |
| BE_H | FaceMorpher | 4.5 | MADation ViT-B/16, raw genuine (0.0) | +4.5 [+2.4, +6.8] | lost |
| BE_H | MIPGAN-I | 0.9 | MixFaceNet-MAD, raw genuine (16.3) | −15.4 [−20.5, −11.1] | exceeded |
| BE_H | MIPGAN-II | 0.5 | MADation ViT-L/14 (14.9) | −14.4 [−18.7, −10.9] | exceeded |
| BE_H | OpenCV | 2.3 | MADation ViT-B/16, raw genuine (4.0) | −1.7 [−5.1, +0.7] | comparable, not separated |
| BE_H | Webmorph | 10.4 | MADation ViT-B/16, raw genuine (11.0) | −0.6 [−7.2, +6.2] | comparable, not separated |
| BE_H | mean4 | 3.5 | MixFaceNet-MAD, raw genuine (15.9) | −12.4 [−16.6, −8.3] | exceeded |
| BE_H | mean5 | 3.7 | MixFaceNet-MAD, raw genuine (13.7) | −10.0 [−13.6, −6.3] | exceeded |
| BE_H | mean2 | 6.3 | MADation ViT-B/16, raw genuine (7.5) | −1.2 [−5.6, +3.1] | comparable, not separated |

- **Border-equalised forms: scope of the "exceeded" verdicts (C3).**
  - SelfMAD has no border-equalised rows ("not available"; §3.2). It is absent from the comparator set in BE_S and
    BE_H, although it is the best release in most S and H cells.
  - For MADation ViT-B/16, ViT-L/14 and MixFaceNet-MAD, the BE rows are their unblanked S and H rows, by registration
    (their own crops have under 0.01% black pixels).
  - Every BE "exceeded" (MIPGAN-I, MIPGAN-II, mean4, mean5) is therefore against those three releases only. It rests
    on the MIPGAN cells, where those three have 15-40% EER.
  - On the landmark families, BE gives "comparable, not separated" (mean2 −1.0 and −1.2).
  - No sentence may say that the network exceeds "the released detectors" or SelfMAD in a border-equalised form. The
    reader's BE secondary sentences are quoted with "(SelfMAD not available in this form)".
- **Holm (C7).** In S and H, MIPGAN-I and MIPGAN-II read "matched", not "exceeded", because of Holm: unadjusted
  p(d ≥ 0) is 0.010 and 0.008, Holm-adjusted 0.042 and 0.040. Their flip to "exceeded" in BE is the change of
  comparator, not a change in our network.
- **Per-seed values,** per-detector absolute intervals, AUC, BPCER@APCER, the neutral-only EER and the own-rule and
  τ_FFHQ rates are in `final_read.json` and `final_tables.md`.

## Every detector, EER %, per form

Variant-1 crop for MADation and MixFaceNet-MAD; SelfMAD own preprocessing on the DGX. Columns:
- **S:** raw morphs against raw genuine photos (ours: native genuine);
- **H:** against our aligned E7 frames;
- **Hraw:** the raw-genuine comparator used in H (B1);
- **BE_S / BE_H:** border-equalised. For the three releases these equal S and H by registration (their crops are
  border-free); for SelfMAD they are "not available".

Our values are seed means. Per-seed values and all intervals are in `final_read.json`.

| Cell | Ours S / H / BE_S / BE_H | MADation ViT-B/16 S / H / Hraw | MADation ViT-L/14 S / H / Hraw | MixFaceNet-MAD S / H / Hraw | SelfMAD S / H / Hraw (BE n/a) | Reference statistic S / H / BE_S / BE_H |
|---|---|---|---|---|---|---|
| FaceMorpher | 2.32 / 3.67 / 4.39 / 4.46 | 0.00 / 13.60 / 0.00 | 0.49 / 2.45 / 0.49 | 4.90 / 13.40 / 4.90 | 0.00 / 0.98 / 0.00 | 0.00 / 11.60 / 0.00 / 46.08 |
| MIPGAN-I | 0.57 / 0.57 / 0.95 / 0.95 | 40.20 / 40.70 / 40.20 | 32.30 / 30.00 / 32.30 | 16.30 / 21.57 / 16.30 | 2.45 / 4.00 / 2.45 | 41.67 / 41.67 / 41.67 / 41.67 |
| MIPGAN-II | 0.28 / 0.28 / 0.50 / 0.50 | 28.43 / 28.33 / 28.43 | 16.32 / 14.91 / 16.32 | 20.59 / 25.98 / 20.59 | 1.70 / 2.70 / 1.70 | 27.94 / 27.94 / 27.94 / 27.94 |
| OpenCV | 2.28 / 2.26 / 2.28 / 2.26 | 3.96 / 6.61 / 3.96 | 4.78 / 4.57 / 4.78 | 8.43 / 11.99 / 8.43 | 1.02 / 2.94 / 1.02 | 15.85 / 22.06 / 15.85 / 22.06 |
| Webmorph | 10.69 / 10.39 / 10.69 / 10.39 | 11.00 / 14.22 / 11.00 | 28.43 / 24.60 / 28.43 | 18.20 / 24.20 / 18.20 | 13.73 / 29.90 / 13.73 | 16.67 / 25.49 / 16.67 / 25.49 |
| mean4 | 3.45 / 3.37 / 3.60 / 3.52 | 20.90 / 22.46 / 20.90 | 20.46 / 18.52 / 20.46 | 15.88 / 20.94 / 15.88 | 4.72 / 9.89 / 4.72 | 25.53 / 29.29 / 25.53 / 29.29 |
| mean5 | 3.23 / 3.43 / 3.76 / 3.71 | 16.72 / 20.69 / 16.72 | 16.46 / 15.31 / 16.46 | 13.69 / 19.43 / 13.69 | 3.78 / 8.11 / 3.78 | 20.43 / 25.75 / 20.43 / 32.65 |
| mean2 | 6.48 / 6.32 / 6.48 / 6.32 | 7.48 / 10.41 / 7.48 | 16.60 / 14.59 / 16.60 | 13.32 / 18.10 / 13.32 | 7.37 / 16.42 / 7.37 | 16.26 / 23.77 / 16.26 / 23.77 |

**Variant-2 crop, printed only (S / H):**

| Cell | MADation ViT-B/16 | MADation ViT-L/14 | MixFaceNet-MAD |
|---|---|---|---|
| FaceMorpher | 0.00 / 17.65 | 0.20 / 2.94 | 9.40 / 20.59 |
| MIPGAN-I | 39.22 / 43.10 | 28.60 / 26.47 | 17.16 / 21.00 |
| MIPGAN-II | 26.96 / 31.03 | 14.71 / 14.71 | 21.12 / 25.00 |
| OpenCV | 3.05 / 4.67 | 4.47 / 4.41 | 9.80 / 13.41 |
| Webmorph | 9.80 / 13.73 | 23.04 / 20.59 | 19.20 / 25.80 |
| mean4 | 19.76 / 23.13 | 17.70 / 16.54 | 16.82 / 21.30 |

- The aligned-native release rows (printed only) are in the json under `releases_aligned_native_printed`.
- **n per cell** (morphs / genuine), identical for every detector and form:

  | Family | Morphs | Genuine |
  |---|---|---|
  | FaceMorpher | 1,000 | 204 |
  | MIPGAN-I | 1,000 | 204 |
  | MIPGAN-II | 999 | 204 |
  | OpenCV | 984 | 204 |
  | Webmorph | 500 | 204 |

  The neutral-only genuine variant has 102.

**AD4 morph-free reference lines,** EER %, printed only (ViT-B/16 WCSS / ViT-L/14):

| Family | Native | E7 |
|---|---|---|
| FaceMorpher | 0.0 / 0.0 | 0.0 / 37.7 (per seed 2.0 to 55.4) |
| MIPGAN-I | reversed in 5 of 5 seeds (per seed 52.8-84.9 / 72.0-94.1); no seed mean (AD4 withdrew it) | same (E7 = native) |
| MIPGAN-II | reversed in 5 of 5 seeds (55.4-83.4 / 80.4-97.9); no seed mean | same |
| OpenCV | 37.0 / 46.6 | 39.6 / 49.8 |
| Webmorph | 26.7 / 36.5 | 28.9 / 39.9 |

## Secondary rates of our networks, history-matched form

Per seed 403-407, in %: own rule APCER / BPCER; then τ_FFHQ APCER / BPCER; then AUC.

| Family | s403 | s404 | s405 | s406 | s407 |
|---|---|---|---|---|---|
| FaceMorpher | 10.1/0.0; 7.1/0.0; 0.9996 | 19.6/0.5; 18.3/0.5; 0.9965 | 4.3/2.5; 4.0/2.5; 0.9930 | 9.0/6.9; 9.2/6.4; 0.9805 | 7.3/1.5; 5.1/2.9; 0.9953 |
| MIPGAN-I | 0.5/0.0; 0.3/0.0; 1.0000 | 0.3/1.0; 0.3/1.0; 1.0000 | 0.2/2.0; 0.2/2.5; 0.9997 | 0.2/2.0; 0.2/2.0; 0.9997 | 0.3/0.5; 0.3/1.5; 0.9998 |
| MIPGAN-II | 0.0/0.0; 0.0/0.0; 1.0000 | 0.0/1.0; 0.0/1.0; 1.0000 | 0.0/2.0; 0.0/2.5; 0.9999 | 0.0/2.0; 0.0/2.0; 0.9999 | 0.0/0.5; 0.0/1.5; 1.0000 |
| OpenCV | 16.8/0.0; 13.0/0.0; 0.9935 | 11.6/1.0; 11.1/1.0; 0.9934 | 4.1/2.0; 4.0/2.5; 0.9970 | 2.6/2.0; 2.6/2.0; 0.9971 | 0.9/0.5; 0.4/2.0; 0.9995 |
| Webmorph | 57.6/0.0; 50.2/0.0; 0.9707 | 54.2/0.5; 53.6/1.0; 0.9054 | 41.2/2.0; 39.8/2.5; 0.9479 | 47.8/2.5; 48.4/2.0; 0.9447 | 23.8/0.5; 20.6/2.0; 0.9851 |

## Forecasts and the border rule (registered before the read)

- **F1** ("trails MADation ViT-B/16 on the standard form for landmark cells"): **"falsified"**. It held on 1 of 3
  cells:
  - FaceMorpher +2.3 [+0.9, +4.2], trails;
  - OpenCV −1.7 [−5.1, +0.7], does not trail;
  - Webmorph −0.3 [−6.7, +6.4], does not trail.
- **F2** ("GAN cells look good by render response"): **"held"**. Seed-mean EER is MIPGAN-I 0.57% and MIPGAN-II 0.28%.
  Label: "not shown to be morph-specific: the network flags one-photo GAN renders".
- **F3** (the border-equalised form raises our EER by ≤ 2 points): **"held"**. Δ = BE_H − H: FaceMorpher +0.79
  [−2.07, +3.53], MIPGAN-I +0.37 [−0.25, +1.05], MIPGAN-II +0.22 [−0.20, +0.73] points.
  - Held on the seed-mean point estimate, as registered (C5). The FaceMorpher interval reaches +3.5, so a rise above
    3 points is not excluded.
  - On the standard form (not registered for F3), FaceMorpher rises by +2.1 (2.32 → 4.39).
- **Border sentence (reader):** "No family's EER rises by more than 3 points when the border is equalised."
  - As it may be written (C5): "No family's seed-mean EER rises by more than 3 points when the border is equalised
    (FaceMorpher +0.8 [−2.1, +3.5]; MIPGAN-I +0.4; MIPGAN-II +0.2; OpenCV and Webmorph carry no border)."
- **Secondary sentences (reader):**
  - "standard (native genuine): comparable, not separated against SelfMAD (descriptive).";
  - "border-equalised history-matched: exceeded against MixFaceNet-MAD (raw genuine photos) (descriptive)." (SelfMAD
    not available in this form);
  - "border-equalised standard: exceeded against MixFaceNet-MAD (descriptive)." (SelfMAD not available in this form)

## What failed, what was not verified

- Nothing failed. Both gates passed (dry run and read).
- Not verified: SelfMAD's per-row `cropped` flags (all rows used, as registered); the border on SelfMAD's own
  preprocessing path (hence no SelfMAD BE rows).
- Results review: `experiments/reviews/REVIEW_FINAL_MAD22_20261113.md` (corrections applied here).

## Files

- `final_read.json`, `final_tables.md` (this folder).
- Result tar `/mnt/t7/smad_next/FINAL/results/FINAL_mad22_final2.tar`, with a second copy in
  `/mnt/t7/smad_next/vast/final2/final/results/`.
- Dry-run tar `FINAL_mad22_final2_dryrun.tar` (the same two places).
