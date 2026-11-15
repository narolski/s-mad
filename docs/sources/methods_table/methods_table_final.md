# Competing detectors under controls for known construction differences: regular, GAN and diffusion morphs

Prepared for Paweł Narolski, 2026-11-07. Built from the three read-only gathers in this folder (`gather_regular.md`, `gather_gan.md`, `gather_diffusion.md`), which copy values out of logged reader outputs. Two checkers' corrections are applied. A few values were re-read from the registered readers: the H1 `orig` labels in `a36_a1.md` §(5) and the recipe MIPGAN-I arm means in `a12_4_read_stage1.json`. No new number was computed, apart from E7 − native differences and ranges of logged values.

- **MADMamba is not in this table.** Its results are sealed ("MADMamba not evaluated on H3 (sealed)").
- No W3, E10 or FST number is used. No `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- Grades and allowed wording follow the final section of `experiments/CONCLUSIONS.md`, "What we can claim about shortcuts". That wording still awaits the author's sign-off (Sun 8 Nov 12:00), which can only drop or weaken it.

## 1. What "once shortcuts are not available" means, and how we tested it

**The problem.** A morph detector has to tell morphs (one face image built from two people) from genuine photos of one person. On the standard benchmarks the two classes were also made in different ways:

- The genuine photos are large, high-quality camera JPEG files.
- The morphs are files of other sizes and formats. In most families their faces are also smaller. The exceptions are MAD22 OpenCV and Webmorph and FRLL StyleGAN, where the face sizes already match.
- Several landmark families also carry black alignment borders. Border fraction alone separates several evaluation families almost perfectly (AUC 0.99–1.00; E07 README).
- **Claim B.** Ten cells are registered: the seven FRLL diffusion families and MAD22 MIPGAN-I, MIPGAN-II and FaceMorpher. In each, one documented file attribute alone separates morphs from genuine photos: "Morph and bona fide files differ in documented construction attributes that alone separate the classes (O = 1.000 per decision cell)." The attributes are file format, width, bits per pixel and face size. The other landmark families show the same in descriptive header checks (A41 DC-A).
  - FRLL is the Face Research Lab London set.
  - MAD22 is the SYN-MAD 2022 benchmark.
- The networks never see file headers. They see decoded pixels: our re-aligned 512-px frames or, for some SelfMAD runs, the raw files through its own crop. File attributes matter only through what they leave in the pixels.
- GAN morphs (GAN: generative adversarial network) and diffusion morphs are generator output, while the genuine photos come from a camera.

So a detector can score well by noticing how the file or picture was made, without noticing that two identities were blended. In plain words, that is the "shortcut" the request refers to.

In this note such a difference is called a **construction difference**. "Shortcut" and "shortcut-carried" are kept for A41's definition, which so far applies to C1 only. Under that definition, three things must all hold:
1. A property separates the classes.
2. The property can be put into genuine photos without morphing.
3. A control that removes it removes at least half of the separation.

No control below removes every difference: E7 leaves the borders, and H1 leaves file size.

To see what a detector does without a given difference, we either:
- **change the genuine side** so that it shares one construction property with the morphs (face size in E7, the generator family in X3), or
- **build a new set** in which both classes are made the same way and only the number of identities differs (H1, H2, H3, H4b).

We then score the same networks again.

**The two kinds of number.**
- **Equal error rate (EER, %).** This is thresholded. It is the error rate at the threshold where missed morphs and false alarms on genuine images are equally frequent.
  - 0 is perfect and 50 is chance.
  - Above 50 means the detector rates the genuine images as more morph-like than the morphs ("inverted"). That is possible here because we keep "morph = high score" and do not cap. The exception is the UA8c summary, which is capped (see [e]).
  - The threshold is re-chosen for each comparison, so EER does not show how a deployed detector behaves. The flag rates at a fixed threshold, quoted in §3, do.
- **Area under the curve (AUC).** This is threshold-free. It is the chance that a random morph scores above a random comparison image.
  - 0.5 is chance.
  - Below 0.5 means the comparison images look more morph-like than the morphs.

**Floors.** Some controls have a "floor": the AUC that a simple statistic (file size, eye position, or a combination) reaches on the same comparison. A detector shows something beyond that statistic only if it clearly beats the floor. The floors used here are:

| Control | Floors (AUC) | Rule |
|---|---|---|
| H1 | bytes 0.620 (`orig`) / 0.681 (`pp`); eye geometry 0.526 / 0.522 | A36 amendment 1 label rule ([b]) |
| H3 | bytes 0.526; eye geometry 0.560; combined covariates 0.607–0.617 | |
| H4b | bytes 0.912 | |
| H2 | bytes 0.522; eye geometry 0.518 | |
| Arc2Face | bytes 0.514; eye geometry 0.509 | |
| X4 | none logged (only a kill rule) | |
| X3 | cue floors are print-only (Q-G2) | not used for any statement here |

**How we tested it, by morph type.**

**Regular (landmark) morphs.** These are made by warping two faces onto shared facial landmarks and blending them. The tools are AMSL, FaceMorpher, OpenCV and WebMorph. There are two tests:
- **Shrunk genuine photos (E7).**
  - Each genuine photo is shrunk (area averaging) to the family's median morph face size before the same alignment.
  - The shrinking factor depends on the family: ~1.0x for MAD22 OpenCV and Webmorph, 3.3x for MAD22 FaceMorpher.
  - This matches face size only. It does not give the photos the morphs' processing history.
  - The alignment borders remain. E7 controls only resolution, not borders (E07 README).
- **The controlled Poisson set (H1).**
  - A fifth landmark tool: MediaPipe Delaunay warp plus Poisson blend.
  - Built on CASIA-WebFace identities at 112 px. The native inter-eye distance is ~37 px, upscaled ~3.6x.
  - 598 pairs. Both classes come from the same source photos, at the same size, with the same ~40% black border and the same post-processing.
  - The only known remaining difference is file size: the morphs are 3–5% smaller PNGs. File size alone gives AUC 0.620 on `orig` and 0.681 on `pp`.
  - The registered primary variant is `orig`; `pp` is printed beside it (PROTOCOL A27 l.7751; A36 amendment 1, l.9929).

**GAN morphs.** The genuine side is replaced by output of a generator:
- **H3.** StyleGAN3 two-person latent-average morphs against single-person renders of the same generator. H3's classes differ in latent spread by construction (CONCLUSIONS l.155).
- **X4.** The same morphs against renders matched to the morphs' latent spread. For a latent-average morph, a spread-matched render is almost the same kind of image by construction. So X4 especially has little power against a two-identity signal (CONCLUSIONS l.155, l.241).
- **H4b.** StyleGAN v1 MIPGAN-I-style morphs against single-identity renders of the host. File size alone gives 0.912 here.
- **Renders vs camera (H-new-83).** A separate check: does a detector score generator output above camera photos?
  - Its registered verdict was "neither". The per-pool AUCs are descriptive.
  - H3, X4 and H4b ask something else: whether a detector scores two-person above one-person generator output.

**Diffusion morphs** (FRLL's six DiM variants and MorDIFF). There are three tests:
- **Shrunk genuine photos (E7).** Each diffusion family has its own dose; the DiM pools average 3.19x (A41 S7 levels). For the SelfMAD release it was also run on the raw files with its own face crop, with three shrinking methods. That is one result, not three replications. Write "not specific to INTER_AREA", never "kernel-independent".
- **Genuine photos passed through the morphs' generator family (X3).** The generator family is DiffAE, a diffusion autoencoder. There are three pools:
  - DiffAE reconstructions of the genuine photos ("rec");
  - photos only resized by DiffAE's aligner;
  - one-person "morphs" made from a person's own two photos.

  X3 was run on official releases only. Its positive control failed (FE ViT-L/14 0.636 ≤ 0.65), so it is not shown that X3 could detect identity mixing at all ("assay sensitivity not shown").
- **Other diffusion generators: morphs against single-person renders of the same generator (H2, Arc2Face).** These are not the FRLL DiM or MorDIFF generators.
  - H2 is "a low-potency, mechanism-only set": only 1.1% of H2 morphs verify against both contributors (PROTOCOL A29, l.8087–8090).
  - Arc2Face is the potent set: 94.7% verify against both contributors (PROTOCOL A23, l.7376).
  - Both columns are descriptive, with no hypothesis or positive control.

## 2. Comparison table

**How to read a cell.** An arrow "→" joins a benchmark number and its controlled number of the same metric (EER → EER). A bar " | " separates different tests or metrics. The controlled numbers are defined in notes [a]–[f] below the table.

**Rows.**
- **Releases** are the authors' official weights, one network each. They are scored on our 512-px eye-aligned frames unless the row says otherwise.
- **Recipes** are our re-implementation of the published training recipe, trained on SMDD only (d0). SMDD is the synthetic morph training set of the SYN-MAD 2022 competition. Recipe numbers are means over the stated number of networks (seeds).
- **‡** marks the 12 primary rows of the registered GAN test (C3). Rows 4–8 are descriptive and outside C3.

**Verdicts.** The verdict words ("holds", "partly holds", "does not hold", "not shown") are post hoc labels of this note, not A41 grades (rules below).

| # | Method (networks) | Regular (landmark) morphs [a][b] | GAN morphs [c][d] | Diffusion morphs [e][f] |
|---|---|---|---|---|
| **Official releases** | | | | |
| 1 | SelfMAD release, HRNet-W18, its own dlib crop and resize on our frames (1) ‡ | EER FM/OCV/AMSL/WM 0.4/0.1/2.9/5.9 → 4.8/3.9/33.3/51.9 (WM above 50 under E7); MAD22 FM 0.0 → 0.11 \| H1 `orig` 0.872 (point; above in A39's count, descriptive) · `pp` 0.821 (point, no label). **partly holds** | MIPGAN-I EER 0.5 \| H3 0.353 (reversed) \| X4 0.447 \| H4b 0.405. **not shown** | EER Greedy-DiM 8.4 → 90.7, MorDIFF 2.5 → 61.3 (C1; inverted) \| X3 rec 0.024 / 0.330 (reversed) \| H2 0.510. **does not hold** |
| 2 | MADation release, CLIP ViT-B/16 + LoRA (1) ‡ | EER 2.8/2.9/15.1/4.9 → 4.4/4.4/28.9/10.8; MAD22 FM 0.6 → 5.9 \| H1 `orig` 0.770 (above) · `pp` 0.727 (not above). **partly holds** | MIPGAN-I EER 18.4; G-test 9.9 \| H3 0.554 \| X4 0.423 \| H4b 0.716. **not shown** | EER MorDIFF 4.9 → 19.6 (C2), DiM-C 6.4 → 29.5, DiM-A 20.6 → 56.4, Greedy-DiM 54.0 → 84.9 \| X3 rec MorDIFF 0.847 (open), DiM-A 0.361 \| H2 0.497. **does not hold** |
| 3 | MADation release, CLIP ViT-L/14 + LoRA (1) ‡ | EER 1.0/1.0/17.7/4.9 → 1.0/1.0/14.7/4.4; MAD22 FM 0.0 → 0.55 \| H1 `orig` 0.718 (above) · `pp` 0.684 (not above). **holds** | MIPGAN-I EER 11.9; G-test 69.5 (inverted) \| H3 0.427 (reversed) \| X4 0.445 \| H4b 0.902. **not shown** | EER Greedy-DiM 9.8 → 9.8, DiM-A 22.0 → 16.7, MorDIFF 28.9 → 39.7 \| X3 rec Greedy-DiM 0.749 (floor-limited) \| H2 0.466. **partly holds** |
| 4 | MADation baseline FE ViT-B/16, frozen CLIP + head (1) | EER 16.7/18.6/26.0/22.5 → 22.6/26.0/38.7/31.9; MAD22 FM 1.0 → 7.2 \| H1 `orig` 0.681 (above, descriptive) · `pp` 0.681 (not above). **partly holds** | MIPGAN-I EER 35.1; G-test 35.1 \| H3 0.514 \| X4 0.451 \| H4b 0.661. **not shown** | EER DiM 21.0–47.0 → 41.6–73.6, MorDIFF 39.7 → 53.5 \| X3 not run \| H2 0.498. **does not hold** |
| 5 | MADation baseline FE ViT-L/14, frozen CLIP + head (1) | EER 3.9/4.4/21.6/9.8 → 4.4/4.9/23.0/10.3; MAD22 FM 1.6 → 2.7 \| H1 `orig` 0.735 · `pp` 0.745 (both above, descriptive). **holds** | MIPGAN-I EER 8.5; G-test 29.1 \| H3 0.505 \| X4 0.475 \| H4b 0.804. **not shown** | EER Greedy-DiM-S 11.8 → 13.8, Greedy-DiM 22.0 → 28.0, MorDIFF 34.8 → 32.4 \| X3 rec Greedy-DiM 0.636 (positive-control gate failed), DiM-A 0.772, MorDIFF 0.742 \| H2 0.502. **partly holds** |
| 6 | MADation baseline FS ViT-B/16, from scratch + head (1) | EER 16.7/3.9/40.6/32.1 → 17.3/5.4/40.7/34.8; MAD22 FM 30.3 → 47.6 \| H1 `orig` 0.472 · `pp` 0.422 (not above; below 0.5). **does not hold** (collapses under E7) | MIPGAN-I EER 17.8; G-test 46.4 \| H3 0.511 \| X4 0.466 \| H4b 0.546. **not shown** | EER DiM 16.1–24.0 → 41.6–45.6, MorDIFF 67.6 → 62.2 (inverted) \| X3 not run \| H2 0.476. **does not hold** |
| 7 | MADation baseline FS ViT-L/14, from scratch + head (1) | EER 38.2/31.9/39.2/32.9 → 37.7/32.8/39.7/32.8; MAD22 FM 32.9 → 35.7 \| H1 `orig` 0.554 · `pp` 0.536 (not above). **does not hold** (weak natively) | MIPGAN-I EER 32.5; G-test 67.4 (inverted) \| H3 0.540 \| X4 0.470 \| H4b 0.641. **not shown** | EER DiM 38.1–47.0 → 40.2–49.0, MorDIFF 43.0 → 42.1 \| X3 not run \| H2 0.502. **does not hold** |
| 8 | MixFaceNet-MAD, the official release, on our frames (loader checked on its own training files) (1) | EER 98.0/98.0/82.8/75.5 → 98.0/98.1/86.8/80.4 (inverted); MAD22 FM 85.4 → 91.9 \| H1 `orig` 0.572 · `pp` 0.598 (below floor, descriptive). **does not hold** (inverted natively) | MIPGAN-I EER 47.0; G-test 39.5 \| H3 0.581 \| X4 not scored \| H4b 0.695. **not shown** | EER DiM 27.1–50.1 → 43.6–66.7, MorDIFF 27.5 → 40.1 \| X3 not run \| H2 0.536. **does not hold** |
| **Published recipes, our re-implementation, SMDD only** | | | | |
| 9 | M1 Inception-MAD, Inception-v3 from scratch (5) ‡ | EER 53.6/53.6/27.5/24.9 → 71.5/72.2/46.3/42.1 (FM, OCV inverted); MAD22 FM 6.4 → 39.0 \| H1 `orig` 0.564 · `pp` 0.603 (not above). **does not hold** (inverted natively; collapses under E7) | MIPGAN-I EER 19.8; G-test 37.5 \| H3 0.555 \| X4 0.441 \| H4b 0.672. **not shown** | UA8c 14.4 → 49.4 (uncapped UA8 under E7: 63.0) \| X3 not run \| H2 0.534. **does not hold** |
| 10 | M2 MorphHRNet-style, HRNet-W48 from scratch (5) ‡ | EER 90.7/87.1/73.2/67.5 → 92.5/90.0/79.7/73.7 (inverted); MAD22 FM 51.6 → 73.8 \| H1 `orig` 0.570 · `pp` 0.594 (not above). **does not hold** (inverted natively) | MIPGAN-I EER 43.0; G-test 38.2 \| H3 0.591 \| X4 0.469 \| H4b 0.678. **not shown** | UA8c 41.7 → 48.5 (uncapped: 66.4) \| X3 not run \| H2 0.532. **does not hold** |
| 11 | M3 MADation recipe, CLIP ViT-B/16 + LoRA (8) ‡ | EER 3.3/5.7/10.8/8.6 → 3.6/5.8/11.4/8.8; MAD22 FM 5.0 → 5.3 \| H1 `orig` 0.805 · `pp` 0.750 (both above). **holds** | MIPGAN-I EER 7.0; G-test 35.6 \| H3 0.448 (reversed) \| X4 0.458 \| H4b 0.847. **not shown** | UA8c 12.6 → 12.1; MorDIFF 35.1 → 28.6 \| X3 not run \| H2 0.483. **partly holds** |
| 12 | M3L MADation recipe, CLIP ViT-L/14 + LoRA (5) ‡ | EER 0.4/0.3/15.0/7.8 → 0.4/0.3/14.5/7.6; MAD22 FM 0.6 → 0.5 \| H1 `orig` 0.833 · `pp` 0.810 (both above). **holds** | MIPGAN-I EER 0.8; G-test 37.6 \| H3 0.401 (reversed) \| X4 0.442 \| H4b 0.923. **not shown** | UA8c 17.7 → 16.1; MorDIFF 45.7 → 41.5 \| X3 not run \| H2 0.474. **partly holds** |
| 13 | M4 SelfMAD-style, HRNet-W18 + self-blended fakes from SMDD genuine photos only (5) ‡ | EER 90.9/38.3/100/100 → 82.0/24.5/100/100 (FM, AMSL, WM inverted); MAD22 FM 99.8 → 0.8 (shrinking made the photos look genuine to it) \| H1 `orig` 0.761 · `pp` 0.761 (both above). **partly holds** (inverted on the benchmarks) | MIPGAN-I EER 34.5; G-test 24.3 \| H3 0.551 \| X4 0.517 \| H4b 0.403. **not shown** | UA8c 50.0 (capped; 100 uncapped in all 7) → 42.8 (uncapped: 49.3) \| X3 not run \| H2 0.475. **does not hold** |
| 14 | M5 PW-MAD, DenseNet-121 with pixel-wise labels (8) ‡ | EER 14.4/15.8/8.9/4.2 → 24.5/28.8/25.7/14.3; MAD22 FM 1.2 → 20.7 \| H1 `orig` 0.533 · `pp` 0.547 (not above). **does not hold** (collapses under E7) | MIPGAN-I EER 36.8; G-test 56.0 (inverted) \| H3 0.564 \| X4 0.460 \| H4b 0.455. **not shown** | UA8c 28.0 → 49.5 (uncapped: 72.3) \| X3 not run \| H2 0.491. **does not hold** |
| 15 | M6 OrthoMAD, ResNet-18 from scratch (5) ‡ | EER 61.3/81.4/66.8/59.8 → 67.7/85.8/74.6/69.3 (inverted); MAD22 FM 24.4 → 47.5 \| H1 `orig` 0.623 · `pp` 0.653 (not above). **does not hold** (inverted natively; collapses under E7) | MIPGAN-I EER 37.0; G-test 33.7 \| H3 0.574 \| X4 0.469 \| H4b 0.647. **not shown** | UA8c 36.8 → 48.2 (uncapped: 60.9) \| X3 not run \| H2 0.525. **does not hold** |
| 16 | M8 MixFaceNet-MAD recipe, MixFaceNet-S from scratch (5) ‡ | EER 66.5/57.4/46.9/44.8 → 75.2/70.1/63.6/61.7 (FM, OCV inverted natively; all four under E7); MAD22 FM 27.6 → 65.7 \| H1 `orig` 0.588 · `pp` 0.648 (not above). **does not hold** (inverted natively; collapses under E7) | MIPGAN-I EER 35.5; G-test 37.3 \| H3 0.560 \| X4 0.448 \| H4b 0.623. **not shown** | UA8c 28.1 → 48.9 (uncapped: 63.8) \| X3 not run \| H2 0.533. **does not hold** |
| 17 | M8O MixFaceNet-MAD, official training code (5) ‡ | EER 85.1/78.4/55.8/54.1 → 88.5/84.1/66.4/65.2 (inverted); MAD22 FM 30.8 → 70.3 \| H1 `orig` 0.580 · `pp` 0.631 (not above). **does not hold** (inverted natively; collapses under E7) | MIPGAN-I EER 45.8; G-test 36.8 \| H3 0.556 \| X4 0.453 \| H4b 0.630. **not shown** | UA8c 36.3 → 49.0 (uncapped: 66.0) \| X3 not run \| H2 0.534. **does not hold** |

### Notes to the table

**[a] Regular, benchmark.**
- **Metric.** EER in % (thresholded). FRLL families are in the order FaceMorpher / OpenCV / AMSL / WebMorph. Each is scored against the 204 FRLL genuine photos (102 persons).
- **MAD22 FaceMorpher** is scored against the 185 MAD22 genuine photos. These are byte copies of FRLL photos. Every MAD22 number is on our 185 + 4,069 MAD22 files, against the published 204 + 4,483 (CONCLUSIONS).
- **Release CIs.** One network each, no seed spread.
  - Image-bootstrap 95% CIs (A36 RSX `boot95`) exist only for the ViT-B/16, ViT-L/14 and MixFaceNet-MAD releases.
  - The SelfMAD own-crop row (A32) and the FE / FS rows have none.
  - Person-clustered 95% CIs exist only for the A41 S3 cells (see [b]).
- **Recipes.** Seed means; SDs are in `gather_regular.md` §2–3. A12.4 calls the recipes' benchmark pool "an eval-pipeline diagnostic, never a detection result".

**[b] Regular, controlled.**
- **E7 EER (thresholded).** The same genuine photos, shrunk (INTER_AREA) to each family's median morph face size before alignment. The shrinking factors are FRLL FM 1.47x, OCV 1.56x, AMSL and WebMorph 1.80x, MAD22 FaceMorpher 3.30x.
- **Families left out.** MAD22 OpenCV and Webmorph are left out of the table: E7 shrinks them by only ~1.0x, so it tests nothing there.
- **Borders.** E7 leaves the alignment borders in place (E07 README). No header comparison of morphs against the E7 pool is logged. DC-A compares the shipped morph files with the native genuine files only.
- **Person-clustered 95% CIs (A41 S3).**
  - SelfMAD FRLL FM 4.8 [1.95, 7.34] and OCV 3.9 [1.41, 5.85].
  - ViT-B/16 FRLL FM 4.42 [2.12, 6.93] and OCV 4.42 [2.08, 7.37].
  - MAD22 FM: SelfMAD 0.11 [0.00, 0.89] and ViT-B/16 5.94 [3.25, 10.62].
- **H1 AUC (threshold-free).** The controlled Poisson set: 598 pairs, both classes from the same source at the same size, with the same border and post-processing.
  - `orig` is the registered primary variant (PROTOCOL A27 l.7751; A36 amendment 1, l.9929), with a floor of 0.620 (bytes; eye geometry 0.526).
  - `pp` is printed beside it, with a floor of 0.681 (bytes; eye geometry 0.522).
- **The H1 label rule** (A36 amendment 1, PROTOCOL l.9924–9926). "Above the floor" needs all three of:
  - a point margin D ≥ +0.05;
  - a one-sided Bonferroni lower bound of D > 0 (the 0.4545th percentile over the 11 primary rows);
  - a seed-CI lower bound of AUC − floor > 0.

  The pair-clustered 90% CIs are only printed beside the label. For example, ViT-B/16 `pp` is +0.045 [+0.029, +0.061], so it is not labelled above.
- **Status of the H1 labels.** Labels on the 11 primary rows (M1–M8O and the ViT-B/16 and ViT-L/14 releases) are registered. Labels on the other rows are descriptive. All were set after the point AUCs were known (exploratory, post-freeze).
- **SelfMAD own-crop H1.** `orig` 0.872 is a point estimate, counted above the floor in A39's sensitivity read (descriptive). `pp` 0.821 is a point estimate with no CI or label; its `pp` EER is 26.9%.

**[c] GAN, benchmark.**
- **MIPGAN-I.** EER % on MAD22 MIPGAN-I (generator PNG against camera JPEG). It carries the MAD22 subset caveat.
  - Releases: SelfMAD from `rsx_read.md`.
  - ViT-B/16 18.4 [13.4, 23.6] and ViT-L/14 11.9 [8.0, 15.6] (person 95%) from `a41_eval.json` DC-8.
  - FE / FS from `a36_read_own.md` "RSX". MixFaceNet-MAD release from `a36_a2.md`.
  - Recipes: arm means of the registered A12.4 reader, `a12_4_read_stage1.json` `arms[…].family_eer_orig["MAD22/MIPGAN_I"]`. These are seed means; the SDs are in the same file. For these families the E7 value equals native. The pool is the A12.4 eval-pipeline diagnostic (descriptive).
- **G-test.** Held-out StyleGAN2 latent-average morphs of FEI face-database pairs, against FEI frontal captures.
  - It sits on the benchmark side of the table, but its morphs are scaled to the genuine photos' face size by construction, and its genuine image is the one the morphs are built from (PROTOCOL l.122–126).
  - For the recipes it is the mean of the neutral and smiling families (`a12_5_read_stage1.md` (i)).
  - The SelfMAD own-crop G-test is not logged.
- **C4.** "These sets compare generator output (PNG) with camera photos (JPEG)." Report them as "synthetic vs camera", with H3 beside them. See flag 1.

**[d] GAN, controlled** (all threshold-free AUC).
- **H3.** 423 StyleGAN3 two-person latent-average morphs against single-person renders of the same generator, `orig`, full pairs.
  - Floors: bytes 0.526, eye geometry 0.560, combined covariates 0.607–0.617.
  - "Reversed" means the 95% pair CI lies below 0.5 (`a41_h3.md`). The A36 intervals quoted in §3 are pair 90%.
- **X4.** The same morphs against renders matched to the morphs' latent spread. Pair-clustered 95% CIs are in `a41g_x4.md`. No floor is logged (only a kill rule).
- **H4b.** StyleGAN v1 MIPGAN-I-style morphs against single-identity renders of the host. The file-size floor is 0.912.
- **"Not shown" rule.** A row would count as "shown" only if H3 is above its combined covariate floor (0.607–0.617) by its CI and X4 is above 0.5 by its CI. No row meets this.
  - The highest H3 is M2 at 0.591 [pair 90% 0.572, 0.610].
  - The highest X4 is M4 at 0.517 [95% 0.493, 0.541].
- **C3** (‡ rows only): "No primary row scores the morphs above single-person renders at AUC ≥ 0.65 (one-sided pair and seed bounds; full / potent, orig / pp); 15 row-cells rank the renders higher (0.35–0.45); on spread-matched renders 0.42–0.52, 11 of 12 with an upper bound below 0.5."
- **Rows 4–8** are descriptive and outside C3.

**[e] Diffusion, benchmark.**
- EER % on the FRLL diffusion families against the original genuine photos.
- Releases are shown per family.
- **Recipes show UA8c.** UA8c is the mean EER over the seven held-out diffusion families (six DiM variants plus MorDIFF), each capped at 50. The seed t-based 95% half-width is in `a36_a2.md` "UA8c per row".
  - The cap hides inversion, so the uncapped UA8 under E7 is shown beside it (`a12_4_read_stage1.json` `endpoints_e7.UA8`).
  - The recipes' native pool is the A12.4 eval-pipeline diagnostic.

**[f] Diffusion, controlled.**
- **E7 EER.** Each family is shrunk to its own median morph face size; the DiM pools average 3.19x (A41 S7 levels).
  - Person-clustered 95% CIs (`a41_eval.json` S2) exist only for the SelfMAD own-crop, SelfMAD our-pipeline, ViT-B/16, ViT-L/14 and FE ViT-L/14 releases.
  - The FE ViT-B/16, FS and MixFaceNet-MAD release values have no person CI.
- **X3 AUC.** The published morphs against DiffAE reconstructions of the genuine photos ("rec"). Values are in the order Greedy-DiM / MorDIFF unless a family is named. X3 was run on releases only: the recipes, the FE ViT-B/16 and FS releases and the MixFaceNet-MAD release were never scored on it.
  - Its cue floors are print-only and not used here.
  - The Greedy-DiM vs rec comparison is floor-limited: file bytes alone give 0.987–0.998 (`a41g_x3.md`).
  - X3 is not part of any diffusion verdict (see the rules).
- **H2 AUC.** IP-Adapter-FaceID Stable Diffusion 1.5 embedding-midpoint morphs against single-identity renders of the same generator.
  - Floors: bytes 0.522, eye geometry 0.518.
  - It is low-potency (1.1% of morphs verify against both contributors).
- **Arc2Face** (548 + 548 images, both generated; the potent set). Every row is at 0.482–0.539 (`gather_diffusion.md` §3h).
- **Status.** Both the H2 and Arc2Face columns are descriptive.

### Verdict rules

All verdict rules are post hoc. They were written for this note after the numbers were seen. They are **not** A41 grades, and "partly holds" is not the dropped phrase "partly carried".

**Regular morphs.**
- **holds:** both conditions hold.
  1. Under E7 the EER is ≤ 10% on at least two FRLL landmark families, and no FRLL landmark family or MAD22 FaceMorpher rises by more than 3 points.
  2. H1 `orig` is labelled above its floor.
- **partly holds:** exactly one of the two holds.
- **does not hold:** neither holds.
- **Tags on "does not hold" rows** (descriptive):
  - *inverted natively:* native EER above 50% on at least two FRLL landmark families.
  - *weak natively:* native EER ≥ 25% on all four FRLL landmark families, without being inverted.
  - *collapses under E7:* a family at ≤ 35% natively rises by at least 10 points.

**GAN morphs.**
- **shown / not shown,** as in [d]. Every row is "not shown".
- "Not shown" means no detection beyond what the H3 / X4 design can show. It does **not** mean the detector is blind to two identities.

**Diffusion morphs.**
- **E7 "holds" on a family** when the E7 EER is within 5 points of native and at most 25%.
- **holds:** E7 holds on at least one family, and H2 or Arc2Face is clearly above its floor. No row qualifies: every row is at 0.466–0.539 on H2 and Arc2Face.
- **partly holds:** E7 holds on at least one family.
  - ViT-L/14 release: Greedy-DiM 9.8 → 9.8 and Fast-DiM 22.6 → 18.6.
  - FE ViT-L/14: Greedy-DiM-S 11.8 → 13.8, DiM-A 14.8 → 19.5 and Fast-DiM-ODE 15.7 → 19.1.
  - M3 and M3L: several DiM families (§3).
- **does not hold:** E7 holds on no family.
- **X3 is left out of the verdicts.** Its positive control failed, and C2 says of the one row that separates morphs from reconstructions: "Identity evidence or a file/frame property: open." X3 is printed in the cells as a separate descriptive item.

### Counts

| Morph type | holds | partly holds | does not hold |
|---|---|---|---|
| Regular | 4 (ViT-L/14 release, FE ViT-L/14, M3, M3L) | 4 (SelfMAD release, ViT-B/16 release, FE ViT-B/16, M4) | 9 |
| Diffusion | 0 | 4 (ViT-L/14 release, FE ViT-L/14, M3, M3L) | 13 |

The GAN column has no count. It is "not shown" in every row, and C3 above is the only allowed summary.

### Status of the numbers

**Registered decision cells.**
- SelfMAD release, MAD22 FaceMorpher under E7: A41 F4 (i), supported.
- MADation ViT-B/16, FRLL FaceMorpher under E7: F4 (ii).
- SelfMAD release, Greedy-DiM and MorDIFF: C1 (F1, F2, F3), grade "strong (final)".
- ViT-B/16, MorDIFF: C2 (F5, F6, F7), "descriptive row (final)". The registered refuter F7 fired.
- ViT-L/14, Greedy-DiM, as the negative control: F4 (iii), supported.
- FE ViT-L/14, as the X3 positive-control gate: it failed (0.636 ≤ 0.65).

**Registered tests.**
- H3 and X4 on the ‡ rows: C3, "strong (narrow)".
- Claim B: "meets its registered criterion".
- C4: "construction sentence".

**Registered labels without a grade.**
- The H1 `orig` labels on the 11 primary rows (A36 amendment 1; exploratory, post-freeze).
- H4b, through the A36 H-new-72 route ("neither").
- Renders vs camera, H-new-83 ("neither").
- "CLIP carries the render cue", H-new-84 ("neither").

**Printed beside C1, C2 and C3.**
- The earlier registered tests of the same questions said "neither": A32 H1 for C1, A36 H-new-75 for C2, A36 H-new-72 for C3.
- The positive controls: the X3 gate failed (assay sensitivity not shown), and the ViT-L/14 release is unchanged on Greedy-DiM (Δ 0.00 [−3.15, 3.41]).
- "MADMamba not evaluated on H3 (sealed)".

**How A41's rules were made.** A41's rules were written after earlier estimates on the same questions had been seen. The amendment G and G2 numbers were blind, except for the INTER_AREA kernel already in use. Never call A41 "confirmatory". The wording awaits the author's sign-off (Sun 8 Nov 12:00), which can only drop or weaken it.

**Everything else is descriptive**, including every verdict word, every `pp` H1 label and every recipe number. No landmark (regular) cell has a shortcut grade, and no registered shortcut rule was applied to the recipes.

## 3. Method by method

### SelfMAD release

Official HRNet-W18 checkpoint, one network. Its own dlib crop and resize are applied to our 512-px frames. Raw-file runs give the native numbers for all FRLL families, but E7 for three diffusion families only.

- **Photo-only and generator-vs-camera checks.**
  - In a test with no morphs at all, its score climbs with how much a genuine photo was shrunk. Shrunk copies against the same photos give AUC 0.584 at ~1.0x, 0.968 at 1.80x and 0.998 at 3.30x (A41 S7, registered secondary rule, "dose response").
  - At its own native 5% threshold it flags 95.1% of half-size genuine photos (thresholded).
  - Threshold-free, it scores StyleGAN3 single-person renders above FRLL photos at AUC 1.000 and above FFHQ photos at 0.952 (descriptive).
  - The allowed cue wording is "bona fide processing history; cue not identified".
- **Reproduction.** On the raw files with its own crop, its published regime reproduces (Greedy-DiM 6.4% against the published 7.6%; H-new-145).
- **Regular.**
  - FaceMorpher- and OpenCV-tool morphs stay detected against shrunk photos: FRLL FaceMorpher 4.8% [person 95% 1.95, 7.34] and MAD22 FaceMorpher 0.11% [0.00, 0.89] (registered).
  - AMSL and FRLL WebMorph do not hold (33.3% and 51.9%).
  - On H1 it gives `orig` 0.872 and `pp` 0.821, both point estimates.
- **GAN.**
  - It ranks single-person StyleGAN3 renders above two-person morphs by the widest margin of any row (H3 0.353 [95% pair 0.326, 0.379]).
  - Spread-matched renders: X4 0.447. StyleGAN v1: H4b 0.405, against the 0.912 bytes floor.
  - Its 0.5% MIPGAN-I EER is measured on a set that compares generator output with camera photos (C4).
- **Diffusion (C1).** "Against FRLL photos downsampled to the morphs' face size, the SelfMAD release scores the genuine photos as more morph-like than Greedy-DiM morphs: EER 8.4% → 90.7% (+82.4 [77.3, 87.4]); MorDIFF 2.5% → 61.3% (+58.8 [54.2, 64.6]). Its published regime reproduces on the raw files with its own crop (6.4% vs 7.6%), where the reversal persists (6.4% → 87.2%) under three downsampling kernels (descriptive). It ranks DiffAE reconstructions (0.33 [0.28, 0.37]) and merely resampled photos (0.09) above the published MorDIFF morphs. MAD22 FaceMorpher stays detected and ViT-L/14 is unchanged. One network; cue not identified."
  - Beside it: the reconstruction test's positive control failed (FE ViT-L/14 0.636 ≤ 0.65: assay sensitivity not shown).
  - The earlier registered test (A32 H1) said "neither".
  - A border or alignment artefact of our control pool is not formally excluded.
  - On the other diffusion generators it gives H2 0.510 and Arc2Face 0.510.
- **Mechanism note.**
  - Through our pipeline the same checkpoint shows the same pattern (H3 0.360; Greedy-DiM 29.4 → 89.1), so the pattern does not depend on its own crop.
  - SelfMAD's released training code builds every self-morph fake by blending a photo with a Lanczos-resampled zoom of itself, and never resamples the genuine partner. This is our local copy at commit 673d064, not verified to be the code that trained the released weights.
  - Its RandomDownScale augmentation can hit either class.
  - This is consistent with C1; it does not explain it.

### MADation release ViT-B/16

Official CLIP ViT-B/16 + LoRA weights, one network. CLIP is an image model pretrained on image-text pairs. LoRA is a small trained adapter on top of it.

- **Photo-only and generator-vs-camera checks.**
  - Without a threshold, it scores StyleGAN3 single-person renders above FRLL / FFHQ / FEI photos (AUC 0.947 / 0.980 / 0.964; descriptive, one network).
  - Its G-test EER (9.9%) is measured on a set that compares generator output with camera photos. Report it as "synthetic vs camera", with H3 (0.554) beside it.
  - Its score reacts to shrunk photos: photo-only AUC 0.622 at 1.47x and 0.906 at 3.30x (S7 "neither").
- **Reproduction on our frames.**
  - MorDIFF is within 5 points of its published number (4.9% against 1.1%).
  - Greedy-DiM (54.0%) is not reproduced.
  - MIPGAN-I and MIPGAN-II are not reproduced (18.4 / 13.5 against the published 33.37 / 22.21; DC-8).
- **Regular.**
  - FaceMorpher and OpenCV morphs hold under E7 (4.4%). AMSL doubles (15.1 → 28.9), and WebMorph goes from 4.9 to 10.8.
  - On H1 `orig` it is above the floor (0.770, registered). On `pp` it is +0.045 [+0.029, +0.061] over the floor, so it is not labelled above.
  - At its native threshold it would flag 71.9% of photos shrunk to MAD22 FaceMorpher's face size. Yet the morphs still rank above them (EER 5.94% [3.25, 10.62]).
- **GAN.** H3 0.554. On spread-matched renders it gives 0.423, the lowest row (X4 has little power by construction). H4b 0.716.
- **Diffusion (C2, a descriptive row).** "EER 4.9% → 19.6% (+14.7 [10.3, 18.9]), in all five crops (+13.2 to +21.0); it also separates the published MorDIFF morphs from DiffAE reconstructions (0.85 [0.80, 0.89]), a registered refuter. Identity evidence or a file/frame property: open."
  - Less than half the separation is removed (d′ share 0.46). So by A41's rule it is not called a shortcut. Never write "inflated", "partly carried" or "resolution".
  - The earlier registered test (A36 H-new-75) said "neither".
  - The DiM families do not hold under E7: DiM-C 6.4 → 29.5, Greedy-DiM-S 6.9 → 29.4, DiM-A 20.6 → 56.4.
  - On DiM-A and Greedy-DiM it ranks reconstructions above the morphs (X3 0.361 and 0.024).
  - H2 0.497, Arc2Face 0.485.
- **Caveat.** One released network. C2 is about these weights only, not the MADation method. Its cue wording is "fine-detail softness".

### MADation release ViT-L/14

Official weights, one network. It is A41's negative control.

- **Photo-only checks.**
  - It ignores photo shrinking: shrunk copies against originals give AUC 0.494 → 0.455 (S7 "none").
  - It does react to other processing: at its native threshold it flags 52.9% of JPEG-50 genuine photos (thresholded).
- **Reproduction.**
  - MorDIFF is not reproduced (28.9% against 19.3%).
  - MIPGAN-I is not reproduced (11.9 against 20.32). MIPGAN-II is reproduced (9.9 against 9.06).
- **Regular.**
  - Its benchmark numbers are unchanged under E7 (FaceMorpher and OpenCV 1.0%; AMSL 17.7 → 14.7).
  - It is above the H1 floor on `orig` (0.718, registered) but at the floor on `pp` (0.684 against 0.681, D +0.002).
- **GAN.**
  - It is inverted on FRLL StyleGAN (52.4%) and on the G-test (69.5%).
  - It ranks single-person StyleGAN3 renders above morphs (H3 0.427, reversed).
  - H4b 0.902, against the 0.912 bytes floor.
- **Diffusion.**
  - DiM detection is unchanged against shrunk photos: Greedy-DiM 9.8 → 9.8, Δ 0.00 [−3.15, 3.41] (registered F4 (iii)).
  - Against DiffAE reconstructions it gives 0.749 on Greedy-DiM. File bytes alone already separate that comparison, so the result is uninformative either way.
  - It ranks same-person DiffAE "morphs" above Greedy-DiM morphs (0.386).
  - The same MorDIFF control raises its EER by +10.7 [7.2, 14.2], so the MorDIFF control's specificity is not shown.
  - H2 0.466, Arc2Face 0.491.

### MADation baselines FE ViT-B/16 and FE ViT-L/14

Frozen CLIP encoder + trained head, one network each.

- **Generator-vs-camera check.**
  - The registered test of whether CLIP carries the render cue (H-new-84) was "neither" (G +0.062 [+0.043, +0.078]).
  - Descriptively, the frozen-encoder FE ViT-B/16 release scores single-person renders above FRLL / FFHQ photos at 0.922 / 0.892 (one network).
  - Both FE releases are near 0.5 on morph versus render (H3 0.514 / 0.505).
- **FE ViT-L/14.**
  - **Regular:** it holds. Its landmark numbers move by +0.5 to +1.5 under E7 (AMSL 23.0%). Its H1 `orig` 0.735 and `pp` 0.745 are both labelled above the floor (descriptive).
  - **Diffusion:** it moves by +2 to +6 on DiM under E7 and by −2.4 on MorDIFF. It holds on Greedy-DiM-S: 11.8 → 13.8, +1.98 [0.25, 4.72].
  - **X3:** against reconstructions it gives 0.772 on DiM-A and 0.742 [0.689, 0.792] on MorDIFF, above 0.5 (descriptive).
  - **Positive control:** as the registered positive control it gave 0.636 [0.579, 0.693] ≤ 0.65 on Greedy-DiM. So it is not shown that the reconstruction test could detect identity mixing at all (assay sensitivity not shown).
  - **Reproduction:** MorDIFF is not reproduced (34.8% against 22.85%).
- **FE ViT-B/16.** It is weak everywhere.
  - Under E7 it loses 6–13 points on the FRLL landmark families and 21–29 on DiM.
  - Its H1 `orig` 0.681 is labelled above the 0.620 floor (D +0.061, descriptive). Its `pp` 0.681 sits at its floor.
  - MorDIFF is not reproduced (39.7% against 17.86%).

### MADation baselines FS ViT-B/16 and FS ViT-L/14

Vision transformer trained from scratch + head, one network each. Both are weak on every morph type.

- **FS ViT-B/16.**
  - It is below 0.5 on H1 (`orig` 0.472, `pp` 0.422).
  - Its moderate DiM numbers move to near 0.5 against shrunk photos (16–24% → 42–46%).
  - MorDIFF is inverted either way (67.6% natively, against a published 28.14%).
- **FS ViT-L/14.**
  - It sits at 27.6–49.0% EER on the landmark and diffusion sets, with or without a control.
  - On the G-test it is inverted (67.4%).
- **GAN.** H3 0.511 / 0.540; X4 0.466 / 0.470.

### MixFaceNet-MAD, the official release

On our frames (loader checked on its own training files); one network.

- **Domain.**
  - Our MAD22-5 / FRLL-5 values are 41.7 / 76.5, against the published 13.69 / 8.96. The MAD22 value is on our 185 + 4,069 MAD22 files, against the published 204 + 4,483.
  - Its loader is verified: 0.45% EER on its own SMDD training files. So the miss comes from our frames or from the genuine-photo source, and the two causes are not separated.
- **Regular.**
  - It ranks FRLL genuine photos above FRLL landmark morphs, with or without the control.
  - It detects only MAD22 OpenCV and Webmorph (12–21%), where E7 changes nothing (~1.0x).
- **GAN.**
  - MIPGAN-I EER 47.0%.
  - H3 0.581 [pair 90% 0.559, 0.603]: at the eye-geometry floor (0.560), below the combined floor (0.607–0.617).
  - X4 was not scored.
- **Diffusion.** It is weak natively (27–50%) and at 40–67% against shrunk photos. X3 was not run. H2 0.536.
- **Caveat.** This says nothing about the method on its own crops. Per the drop list, no sentence may tie its numbers to image size.

### M1 Inception-MAD

Our re-implementation, Inception-v3 from scratch, SMDD only, 5 seeds.

- **Reproduction.** Like the other CNN recipes here, it did not reproduce the published numbers (A12-BR equivalence test: falsified).
- **Rankings follow the morph files.**
  - Natively, against byte-copy genuine photos, OpenCV-tool morphs score 3.3% from MAD22 (1351-px files) and 53.6% from FRLL (431-px files).
  - Under E7 they score 4.0% against 72.2%.
  - So these CNN rankings follow the benchmark's morph files.
- **Regular.** MAD22 FaceMorpher goes from 6.4% to 39.0% once the photos are shrunk. H1 is below the floor (`orig` 0.564, `pp` 0.603).
- **GAN.**
  - It scores StyleGAN3 renders above FRLL / FFHQ photos (AUC 0.969 / 0.977, against 0.990 for morphs).
  - H3 0.555, at the eye-geometry floor. X4 0.441.
  - MIPGAN-I 19.8% (descriptive).
- **Diffusion.** Its fair native diffusion numbers do not survive E7 (UA8c 14.4 → 49.4). Uncapped, UA8 under E7 is 63.0 (e.g. Greedy-DiM 9.0 → 60.7), so it is inverted in most families.

### M2 MorphHRNet-style

HRNet-W48 from scratch, 5 seeds.

- **Regular.** It ranks FRLL genuine photos above FRLL landmark morphs (67–91% EER). Degrading both classes (half size, JPEG 50) does not remove the inversion (A12.4 H-new-B: falsified).
- **GAN.**
  - It is weak even on the native GAN sets (MIPGAN-I 43.0%, G-test 38.2%).
  - Its H3 of 0.591 is the highest of any row, but stays below the combined file-size + eye-geometry floor (0.607–0.617).
  - On spread-matched renders it gives 0.469 (X4 has little power by construction).
  - Single M2 networks reach a within-pair θ of 0.66, and simple image properties alone give 0.62. Never write "no network".
- **Diffusion.** UA8c 41.7 → 48.5; uncapped UA8 under E7 is 66.4.

### M3 and M3L, the MADation recipe

CLIP ViT-B/16 or ViT-L/14 + LoRA, SMDD only; 8 and 5 seeds.

- **Where the skill sits.**
  - In our re-implementation (d0, diffusion), a linear head on frozen CLIP ViT-B/16 reaches UA8c 15.2, against M3's 12.1. That is consistent with most of the recipe's diffusion skill sitting in the frozen features.
  - The official FE ViT-B/16 release does not behave this way.
- **Regular.** They hold.
  - Their landmark EERs move by at most 0.6 under E7.
  - On H1 they are labelled above the floor on `orig` (0.805 and 0.833) and on `pp` (0.750 [pair 90% 0.735, 0.765] and 0.810 [0.793, 0.826]).
  - M3 flags 5.9% of half-size photos at its native threshold, against a native rate of 5.4%.
- **GAN.**
  - They score single-person renders above FRLL / FFHQ / FEI photos (M3 0.951 / 0.956 / 0.967; threshold-free, descriptive).
  - They rank single-person StyleGAN3 renders above morphs (H3 0.448 and 0.401, reversed).
  - M3L's H4b of 0.923 is only +0.010 over the file-size floor (Bonferroni lower bound −0.031).
  - Their low MIPGAN-I EERs (7.0% and 0.8%) are measured on synthetic vs camera.
- **Diffusion.**
  - Held-out diffusion detection is unchanged against shrunk photos (UA8c 12.6 → 12.1 and 17.7 → 16.1).
  - It holds on several DiM families; for example, M3 DiM-A goes 7.0 → 7.3 and M3L DiM-A 5.6 → 5.0.
  - MorDIFF stays weak (35.1 → 28.6 and 45.7 → 41.5).
  - They were never tested against DiffAE reconstructions.
  - On H2 they are near 0.5, slightly below (0.483 ± 0.003 and 0.474 ± 0.004, seed t95).
  - M3's number is at its validation-selected checkpoint; the last checkpoint gives 25.4.

### M4 SelfMAD-style

HRNet-W18, self-blended fakes built from SMDD genuine photos only, 5 seeds.

- **Regular.**
  - It scores genuine studio photos as more morph-like than the benchmark morphs. Its EER is 100% on AMSL, WebMorph and all seven diffusion families, and 90.9% on FaceMorpher. OpenCV is at 38.3% and is not inverted.
  - Shrinking the photos makes them look genuine to it (MAD22 FaceMorpher 99.8% → 0.8%). That is the opposite direction from the SelfMAD release.
  - On H1 it is labelled above the floor (0.761 on both variants), so some landmark separation exists. On the benchmarks it is inverted.
- **GAN.**
  - It does not read generator output consistently. It scores FRLL and FFHQ photos above StyleGAN3 renders (0.314 / 0.394), and FEI photos below them (0.999).
  - H3 0.551 [pair 90% 0.531, 0.573]: at the eye-geometry floor (0.560), below the combined floor.
  - X4 0.517 [95% 0.493, 0.541]: the only primary row whose X4 upper bound exceeds 0.5.
- **Diffusion.** UA8c is 50 (capped; 100 uncapped in all 7) → 42.8. Uncapped, UA8 under E7 is 49.3, with families ranging from 21.5 to 60.1.

### M5 PW-MAD

DenseNet-121 with pixel-wise labels, 8 seeds.

- **Regular.**
  - It is fair natively (WebMorph 4.2%), but with seed SD up to ±17 on other families.
  - Under E7 it loses 10–20 points on every FRLL landmark family and on MAD22 FaceMorpher. MAD22 OpenCV and Webmorph, at ~1.0x, are unchanged.
  - H1 is below the floor (`orig` 0.533, `pp` 0.547).
- **GAN.**
  - It is inverted on the StyleGAN2 G-test (56.0%), and on StyleGAN v1 morphs against camera photos (H4 0.338).
  - H3 0.564: between the eye-geometry floor and the combined floor.
- **Diffusion.** It goes from fair to near chance or inverted: UA8c 28.0 → 49.5, with uncapped UA8 under E7 at 72.3 (Greedy-DiM 33.6 → 83.3).

### M6 OrthoMAD

ResNet-18 from scratch, 5 seeds.

- **Regular.**
  - It is inverted on the FRLL landmark families (60–81%). Degrading both classes (half size, JPEG 50) does not remove the inversion (H-new-B: falsified).
  - MAD22 FaceMorpher goes from 24.4% to 47.5% under E7.
- **GAN.**
  - Whether StyleGAN3 renders look morph-like to it depends on the camera pool: 0.525 against FRLL, 0.913 against FFHQ.
  - H3 0.574: between the eye-geometry floor (0.560) and the combined floor (0.607–0.617).
- **Diffusion.** UA8c 36.8 → 48.2; uncapped UA8 under E7 is 60.9.

### M8 and M8O MixFaceNet-MAD

MixFaceNet-S from scratch: our port of the recipe, and the authors' official training code; 5 seeds each.

- **Reproduction.** Neither version reproduced the published numbers; the official-code reproduction was also falsified.
- **Regular.**
  - Both are inverted on FRLL FaceMorpher and OpenCV natively. M8O is inverted on all four FRLL landmark families.
  - MAD22 FaceMorpher collapses under E7 (+38.2 and +39.5).
  - Both are below the H1 floor (`orig` 0.588 / 0.580; `pp` 0.648 / 0.631).
  - At its native 5% threshold, M8O flags 26.7% of half-size genuine photos and 57.3% of the DiM E7 photo pool.
- **GAN.** H3 0.560 / 0.556 ([pair 90% 0.540, 0.578] / [0.537, 0.574]): at the eye-geometry floor (0.560), below the combined floor (0.607–0.617).
- **Diffusion.** UA8c ~49. Uncapped, UA8 under E7 is 63.8 / 66.0, so near chance or inverted; the cap hides the inversion.

### Across rows

**Regular morphs.**
- Only CLIP-based rows hold against photos shrunk to the morphs' face size and on H1: the MADation recipe (M3, M3L), the ViT-L/14 release and the FE ViT-L/14 release. The ViT-L/14 release is at the floor on H1 `pp`.
- Not every CLIP row holds. FE ViT-B/16 loses 6–13 points, and the ViT-B/16 release's AMSL doubles.
- The SelfMAD release keeps FaceMorpher- and OpenCV-type morphs but loses AMSL and WebMorph.
- These rows do not hold: every SMDD-trained CNN recipe except M4 (which is inverted on the benchmarks but above the H1 floor), and the MixFaceNet-MAD release.

**GAN morphs.**
- No published detector we analysed (3 releases and 9 re-implemented published recipes) ranks StyleGAN3 morphs above single-person StyleGAN3 renders by a useful margin, and several rank them the other way round (C3).
- Their low MIPGAN EERs are on sets that compare generator output with camera photos (C4). We report them as "synthetic vs camera", with H3 beside them.

**Diffusion morphs.**
- The SelfMAD release reverses against shrunk photos (C1).
- The SMDD CNN recipes fall to near chance or are inverted (the cap hides the inversion).
- Some rows change little on DiM: M3, M3L, the frozen-CLIP head, and the ViT-L/14 and FE ViT-L/14 releases. The ViT-B/16 and FE ViT-B/16 releases do not.
- On H2 and Arc2Face every row is within about 0.02 of 0.5 or of the simple-cue floors (0.466–0.539). These columns are descriptive, with no hypothesis, potency check or positive control. So they are not evidence that detectors are blind to identity.

## 4. What this does not show

- **It does not grade the methods.** The verdict words are post hoc descriptive labels. The only grades are CONCLUSIONS':
  - C1 "strong (final)";
  - C2 "descriptive row (final)";
  - C3 "strong (narrow)";
  - B "meets its registered criterion";
  - C4 "construction sentence".

  The regular (landmark) column has no shortcut grade at all.
- **The release results are not about the methods.**
  - Each release is one network. C1 and C2 are about those checkpoints, not about the SelfMAD or MADation methods.
  - Never write "published detectors rely on shortcuts", "for every method" or "MADation carries the shortcut".
- **Most results are on our frames, not the authors' pipelines.**
  - The releases were scored on our 512-px eye-aligned frames. Only the SelfMAD release was also scored with its own crop and on raw files, and its raw-file E7 covers three diffusion families only.
  - Several release numbers do not reproduce on our frames (§3).
  - The MixFaceNet-MAD release is out of its input domain on our frames.
- **The recipes are re-implementations that mostly did not reproduce.**
  - Most CNN recipes failed the reproduction check.
  - Their benchmark pool is an eval-pipeline diagnostic (A12.4).
  - A12 numbers must not be set against published tables in the paper.
  - The same architectures trained with our protocol and data (P × d1) are not competing methods. They are in `gather_regular.md` §5 and `gather_diffusion.md` §3e.
- **The data are narrow.**
  - FRLL and MAD22 share one pool of 204 or 185 genuine photos from 102 persons, so the families are not independent.
  - The controlled Poisson set is CASIA-WebFace at 112 px.
  - GAN evidence is one generator per test: StyleGAN3 for H3 and X4, StyleGAN v1 for H4b.
  - The generator-matched diffusion evidence is DiffAE (X3, releases only, with a failed positive control). H2 and Arc2Face are other generators.
  - FFHQ-Morphs is left out of the verdicts. File size alone separates its DiffAE pool (1.000), and its own README calls it "unfit to be used for evaluation purposes".
- **It does not show which cue a network reads, or anything causal.**
  - SelfMAD release: "cue not identified". Never write "resolution", "aliasing", "fine-detail loss", "interpolation trace" or "spectral cue".
  - GANs: no row reached the registered "storage-format cue" label (H-new-142).
  - MixFaceNet-MAD: no image-size sentence.
- **It does not show that detectors are blind to identity.**
  - H3's classes differ in latent spread by construction, and X4 has little power against a two-identity signal by construction.
  - H2 is low-potency.
  - X3's positive control failed (0.636 ≤ 0.65): "assay sensitivity not shown".
  - Never write "does not separate", "no signal" or "no network" for C3.
- **Control-pool artefacts are not excluded.**
  - E7 leaves the alignment borders on landmark families (E07 README).
  - A border or alignment artefact of our E7 pool is not formally excluded: the border test ran but could not be evaluated.
  - The MorDIFF E7 pool is the weaker control. Almost half (0.471) of that pool's difference from the native photos sits in the warped border (H-new-152 W-c). That is a pool property, not a border-test reading of any network. The pool also raises the ViT-L/14 negative control by +10.7.
- **The reruns are not replications.** The crop test and the kernel ladder re-use the same persons and images.
- **It says nothing about MADMamba, W3, E10 or the FST.**
  - CONCLUSIONS requires three things printed beside every shortcut claim: "MADMamba not evaluated on H3 (sealed)", the positive controls, and our own networks' history with the same control.
  - That history concerns our own networks, so it is not repeated here. Take it from CONCLUSIONS when writing the paper.
- **It makes no generalisation claim.** Nothing here supports a "GAN or diffusion generalisation" sentence for any method.

## 5. Flags for the author

1. **C4 wording.**
   - A41 DC-A (`a41_files.json`) records the FRLL StyleGAN morphs as JPEG (quality 74.7, 1024 px), not PNG. MAD22 MIPGAN-I/II are PNG against JPEG.
   - The G-test's file containers are not in DC-A, so "(PNG) … (JPEG)" is unlogged for the G-test, not false.
   - Your sign-off can only weaken the wording. A possible version: "generator output (PNG, or JPEG q≈75 for FRLL StyleGAN) with camera photos (JPEG)".
2. **H1 primary variant.**
   - This note uses `orig` as primary, as both A27 (PROTOCOL l.7751) and the A36 amendment 1 rule (l.9929) register it. `pp` is printed beside it.
   - The "claims on pp" phrase at l.8649 belongs to the A30 registration amendment 2 and covers A30's own networks only.
   - Three releases change label between `orig` and `pp`:
     - ViT-B/16: 0.770 above / 0.727 not above.
     - ViT-L/14: 0.718 above / 0.684 not above.
     - FE ViT-B/16: 0.681 above / 0.681 not above.
3. **Diffusion verdicts exclude X3.** If X3 were counted as a same-generator control:
   - FE ViT-L/14 would meet the old "works" rule (E7 kept on Greedy-DiM-S; X3 MorDIFF 0.742).
   - The ViT-B/16 release would be "partly" on X3 MorDIFF 0.847 alone.

   We left X3 out because its positive control failed and C2 calls the MorDIFF separation "open".
4. **Verdict cut-offs are post hoc.** The cut-offs (10% on two families, 3 points, 5 points and 25% for diffusion) were set after seeing the numbers. Different cut-offs would move a few labels.
5. **Border evidence.** Per-family border results are only in E07 `raw/data-shortcut.md`, which is outside this note's allowed sources. That file says border fraction alone separates FRLL FaceMorpher / OpenCV / WebMorph morphs from E7 photos at AUC 1.00 and MAD22 landmark morphs at 0.69, and that AMSL is not in that check. Only the README's general statement is used above.
6. **Mixed CI levels.** Keep the level next to each number:
   - A41 S2 / S3 / DC-8: person-clustered 95%.
   - A41 H3 bounds: one-sided 95% pair.
   - X4: two-sided pair 95%.
   - A36 H1 and H3: pair 90%.
   - A36 RSX: image bootstrap 95%.
   - Recipes: seed SD, or seed t95 for UA8c and H2.
7. **Cells with no controlled number.**
   - X4 for the MixFaceNet-MAD release.
   - X3 for every recipe, for the FE ViT-B/16 and FS releases, and for the MixFaceNet-MAD release.
   - The SelfMAD own-crop G-test.
   - A raw-file E7 for any landmark family.
   - Any header comparison of morphs against the E7 pool.

## 6. Sources

Paths are under `/home/narolski/mambamorph-code/` unless absolute.

**Scratch gathers** (per-number keys, SDs and CIs):
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_regular.md`
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_gan.md`
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_diffusion.md`

**Grades and wording**
- `experiments/CONCLUSIONS.md`, §"What we can claim about shortcuts" (l.164 onwards): C1, C2, C3, B, C4, the scope, the mechanism note, the drop list, and what is printed beside each claim.
- The same file:
  - l.155: H3 latent spread; X4 "almost the same kind of image by construction".
  - l.241: "synthetic vs camera"; the MAD22 185 + 4,069 caveat; the MixFaceNet-MAD row wording.
  - §"What this means for the paper": no A12 numbers against published tables, and no generalisation claim.

**Regular column**
- **SelfMAD release.** Native and E7 per family: `smadcvpr/results/RSX/rsx_read.json` `networks[].summary` (byte-identical to the A32 `raw/` copy). Half-size flag rates: `smadcvpr/results/RSX/rsx_read.md` "Mechanism". H1 `orig` / `pp` points: `smadcvpr/results/A36/a36_read_own.md` l.42.
- **MADation and FE / FS releases.** `smadcvpr/results/A36/a36_read.json` `RSX.rows` (`fam`, `boot95`, `mech`, `e7_bpcer_at_native_t5`).
- **MixFaceNet-MAD release.** `smadcvpr/results/A36/a36_a2.json` `row_a36.RSX.fam` / `.boot95`.
- **Recipes.** `smadcvpr/results/A12/a12_4_read_stage1.json` `arms["M1:r:d0" … "M8O:ocode:d0", "M4:r:d0b"].family_eer_orig / family_eer_e7`. The inversion test is in `a12_4_read_stage1.md` §(ii) (H-new-B).
- **Registered E7 cells and dose ladder.** `smadcvpr/results/A41/a41_eval.json`:
  - `S3.components.i`: SelfMAD MAD22 FaceMorpher 0.11 [0.00, 0.89].
  - `S3.positive_controls_beside`: ViT-B/16 MAD22 FaceMorpher 5.94 [3.25, 10.62].
  - `S7.rows`: dose ladder.
- **H1 AUCs and labels.** `smadcvpr/results/A36/a36_a1.md` §(5): `orig` table (registered label) and `pp` table (beside).
- **H1 rules.**
  - `smadcvpr/PROTOCOL.md` A27 (l.7751: "Primary: `orig`"; registration ~l.7715).
  - A36 amendment 1 label rule (l.9924–9929).
  - A30 registration amendment 2 (l.8642–8649) for the `pp` note in flag 2.
- **Borders.** `experiments/E07_shortcut_controls/README.md` l.70–73.
- **Construction attributes.** `smadcvpr/results/A41/a41_files.md` / `.json` (DC-A).
- **OpenCV cross-benchmark check and reproduction tests.** `experiments/A12-BR_benchmark_recipes/README.md` (l.140–146).

**GAN column**
- **H3, H4b, H4 and renders vs camera.** `smadcvpr/results/A36/a36_read_own.md` §(C) and `smadcvpr/results/A36/a36_a1.md` §(1). H-new-83 and H-new-84 verdicts: `a36_a1.md` l.7. MixFaceNet-MAD release: `a36_a2.md`.
- **H3 bounds and reversed cells.** `smadcvpr/results/A41/a41_h3.md`.
- **X4.** `smadcvpr/results/A41/a41g_x4.md` / `.json` (H-new-146).
- **Native MIPGAN-I.**
  - SelfMAD: `smadcvpr/results/RSX/rsx_read.md`.
  - ViT-B/16, ViT-L/14: `a41_eval.json` DC-8.
  - FE / FS: `a36_read_own.md` "RSX".
  - MixFaceNet-MAD release: `a36_a2.md`.
  - Recipes: `smadcvpr/results/A12/a12_4_read_stage1.json` `arms[…].family_eer_orig["MAD22/MIPGAN_I"]`.
- **G-test.**
  - Recipes and the SelfMAD our-pipeline row: `smadcvpr/results/A12/a12_5_read_stage1.md` (i).
  - MADation and FE / FS releases: `a36_read_own.md` "G-test".
  - MixFaceNet-MAD release: `a36_a2.md`.
  - Definition: `smadcvpr/PROTOCOL.md` l.122–126.
- **Storage-format label.** `a41_eval.json` `H-new-142`.
- **Registrations.** `smadcvpr/PROTOCOL.md` A34 (H4b, l.8517–8545) and A35 (H3).
- **M2 within-pair θ.** `experiments/A41_shortcut-proof-zero-gpu/README.md` (l.230) and `meta.json`.
- **MixFaceNet-MAD loader check.** `experiments/A39_batch-before-window-close/README.md` (S2).

**Diffusion column**
- **Release E7 per family.** `smadcvpr/results/A41/a41_eval.json` `S2.cells["<row> | dim/<family>"]` and `["<row> | mordiff/mordiff"]` (`native`, `e7`, `delta`, `delta_ci95`).
- **Raw-file E7 and kernels.** `smadcvpr/results/A41/a41g_x7.md`, `a41g_s12.json` `detail.a`, `a41g2_s12k.json`.
- **X3.** `smadcvpr/results/A41/a41g_x3.md` / `.json`. Floor-limited Greedy-DiM vs rec: l.11 and l.51.
- **Five crops.** `smadcvpr/results/A41/a41g_x14b.md`.
- **Border-matched X3.** `smadcvpr/results/A42/a42_border.md`.
- **FE / FS releases, H2 and Arc2Face.** `smadcvpr/results/A36/a36_read_own.md` "RSX: MADation official" and §(C). MixFaceNet-MAD release: `smadcvpr/results/A36/a36_a2.md` "RSX, UA8c and MAD22" and "held-out comparisons".
- **H2 and Arc2Face potency.** `smadcvpr/PROTOCOL.md` A29 (l.8087–8090) and A23 (l.7376).
- **Recipe per-family E7 and uncapped UA8.** `smadcvpr/results/A12/a12_4_read_stage1.json` `arms[*].family_eer_orig / family_eer_e7` and `endpoints_e7.UA8`.
- **Recipe UA8c with t95.** `smadcvpr/results/A36/a36_a2.md` "UA8c per row".
- **Frozen-CLIP head.** `smadcvpr/results/A12/a12_4_read_stage2.json` `arms["M3:a124lp:d0"]`.
- **UA8c definition and the last-checkpoint value.** `experiments/A12-BR_benchmark_recipes/README.md` (l.52–53, 117, 138–139).
- **Diffusion flag rates.** `smadcvpr/results/RSX/rsx_read.md` "Mechanism".

**Not read or not used**
- No `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- No MADMamba, W3, E10 or FST result was used.
- The league (L0–L2) and W3 rows that share `rsx_read.md` / `rsx_read.json` were not used.
