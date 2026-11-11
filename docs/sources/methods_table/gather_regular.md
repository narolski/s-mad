# Column "REGULAR (landmark-based) morphs": published methods, native vs. with the shortcuts removed

File: /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_regular.md
Built read-only from logged outputs on 2026-11-07. No new number was computed. The only processing was copying values out of the logged JSON and MD files and taking E7 minus native.

**MADMamba is not in this table.** MADMamba, W3, E10 and FST results are sealed. The A32 RSX file also holds W3 / L0-L2 rows, and those rows were left out. Our own networks' E07 history is printed beside shortcut claims in the paper. It consists of MADMamba-family numbers, so it is not repeated here.

**No shortcut grade exists for any landmark family.** The final section of CONCLUSIONS.md, "What we can claim about shortcuts", grades C1 and C2 on diffusion cells and C3 on StyleGAN3 cells. Landmark families appear in only two places:
- as specificity / positive-control cells (A41 S3 = F4, H-new-150);
- in claim B's construction statement, through MAD22 FaceMorpher.

Everything else below is descriptive. The wording follows the drop list in that section:
- No "resolution shortcut" for either release.
- No MixFaceNet-MAD resolution sentence.
- Never "the same OpenCV morphs".
- No "proven", and "strong" is not used as ordinary prose.

---

## 0. Conventions (read once)

**Families.**
- FRLL-Morphs: AMSL, FaceMorpher (FM), OpenCV (OCV), WebMorph (WM). Each is scored against the 204 FRLL photos.
- MAD22: FaceMorpher, OpenCV, Webmorph. Each is scored against 185 photos, which are byte copies of FRLL photos. MAD22 numbers carry the 185 + 4,069 subset caveat.
- Also covered:
  - H1 Poisson: 598 pairs, MediaPipe-478 Delaunay warp plus Poisson blending, CASIA-WebFace identities.
  - FFHQ-Morphs landmark_complete and landmark_combined.

**Networks.**
- "Release" means the authors' weights scored on our 512-px eye-aligned frames. One network each, so there is no seed spread. The SelfMAD release is also scored with its own dlib crop and cv2.resize ("own preprocessing").
- "Retrain" means the published recipe re-implemented in our trainer (A12BR). Variants:
  - R = the published recipe.
  - O = the official MixFaceNet-MAD training procedure, re-implemented.
  - P = our protocol.
- Training data:
  - d0 = SMDD only (the SYN-MAD 2022 setting).
  - d0b = SMDD bona fide only, with self-blended fakes (the SelfMAD-style recipe).
  - d1 = our data. The FM, OCV and WM benchmark families are "in-tool" for d1 (A12 plan, finding S5).
- Leagues: L0 = from scratch, L1 = ImageNet, L2 = CLIP.

**The controls and what each one removes.**

| control | what it does | what it leaves in place |
|---|---|---|
| **E7 (resolution-matched bona fide pool)** | The same genuine photos, downsampled (INTER_AREA) to the family's median morph inter-eye distance (IED) before alignment (PROTOCOL §3). Downsampling factor ("dose"), from the A41 registration (H-new-136): MAD22 OCV and WM **~1.0x** (almost no change), FRLL FM **1.47x**, FRLL OCV **1.56x**, FRLL AMSL and WM **1.80x**, MAD22 FM **3.30x**. | Alignment borders: the morphs of FRLL FM/OCV/WM and MAD22 FM have zero-padded borders in 96-100% of images and the photos have none. Border fraction alone gives AUC 0.99-1.00 (A8 diagnosis, E07 raw/data-shortcut.md, Verdict item 4). File-header differences: one header attribute alone separates morphs from photos at O = 1.000 for every landmark family, by width and JPEG quality; MAD22 Webmorph only by chroma subsampling (O 1.000) and bytes per pixel (O 0.798) (A41 DC-A). |
| **Photo-only dose ladder (A41 S7, H-new-136)** | Threshold-free AUC of the shrunk copies against the same 185 photos at native size, at each family's dose. No morph is involved. | n/a (it measures how much a detector's score reacts to shrinking a genuine photo) |
| **resample50 / jpeg50 BPCER (A32 M, A36 RSX "mech")** | Share of half-size (or JPEG-50) genuine photos flagged as morphs at the network's native BPCER-5% threshold. Thresholded. | n/a (photo side only) |
| **H1 Poisson, `pp` variant** | The cleanest landmark test. Both classes share source, native size (112² both, IED within 0.7%), a ~40% black border and identical post-processing (unsharp mask, colour transfer, JPEG q85-95). | Morphs are 3-5% smaller PNG files, an attack property. Floors: bytes-only 0.620 (orig) / 0.681 (pp), eye geometry 0.526 / 0.522. Low native IED (~37 px, upscaled ~3.6x). Claims rest on `pp`. |
| **FFHQ-Morphs landmark families vs their E7 pool** | Photos downsampled to the morphs' 64.6 px IED; both classes lossless PNG (A24 registration). | The dataset's own README calls it "unfit to be used for evaluation purposes". A 26-cue cue-only diagnostic reaches AUC 0.93 on landmark_complete (A24 caveat 2). The bytes floor of 1.000 reflects the 1024-px source, not the resmatched images (PROTOCOL A30 (e)). Within-set eye-geometry floor 0.596 (complete) / 0.589 (combined). |
| **26-scalar cue-only detector (A8)** | Logistic regression on 26 low-level image statistics, trained on our D1 training sample, scored on the landmark families. A floor for "how far simple image statistics get". | n/a |

**Metric labels.**
- EER (%) and flag / BPCER rates are **thresholded**. EER uses the per-family equal-error threshold. Flag rates use the stated fixed threshold.
- AUC is **threshold-free**.
- "native → E7 (Δ)" means EER against the original photos, then EER against the E7 pool.

**Spread and CI labels.**
- ±SD = SD over seeds.
- ±t95 = seed t half-width.
- [person 95%] = A41 person-clustered dyadic bootstrap (102 FRLL persons, B = 10,000).
- [pair 90%] = A36 pair-clustered bootstrap (598 H1 pairs).
- [boot95] = A36 RSX bootstrap (B = 2,000; clustering not stated in the output).

**Status labels.**
- R = number from a registered decision cell or registered label.
- D = descriptive or post hoc (printed by a registered reader, but no landmark hypothesis was registered).

---

## 1. Summary table (one row per method)

"Clean test" = H1 Poisson `pp` AUC (threshold-free; floor 0.681, pair-clustered; registered label from the A36 amendment 1 reader).

| # | Method (what it is) | Networks | Native landmark EER (benchmark pools) | Under E7 (photos shrunk to the morphs' face size) | Clean test H1 pp AUC (floor 0.681) | Still detects landmark morphs once the photo-processing cue is gone? Plain words |
|---|---|---|---|---|---|---|
| 1 | **SelfMAD release, own preprocessing** (HRNet-W18, trained on self-morphed photos; official weights, own crop) | 1 release | FRLL AMSL 2.9, FM 0.4, OCV 0.1, WM 5.9; MAD22 FM 0.0, OCV 0.6, WM 13.6. On the raw files with its own crop: AMSL 2.44, FM 0.98, OCV 0.37, WM 7.36 | FM 4.8 [person 1.95, 7.34], OCV 3.9 [1.41, 5.85], MAD22 FM 0.11 [0.00, 0.89] (R, F4 (i)), MAD22 OCV 1.1, MAD22 WM 19.0. **AMSL 33.3 (+30.4), FRLL WM 51.9 (+46.1)** | 0.821 (point; above floor; orig 0.872) | **Partly.** FaceMorpher- and OpenCV-type morphs and the clean Poisson morphs stay detected. Its near-perfect AMSL and WebMorph numbers do not hold: against photos shrunk to those morphs' face size it misses a third of AMSL morphs and is at chance on FRLL WebMorph. Its score climbs with how much a genuine photo was shrunk (photo-only AUC 0.58 at ~1.0x → 0.97 at 1.80x → 0.998 at 3.30x). At its native threshold it flags 95% of half-size photos. |
| 2 | **SelfMAD release, our pipeline** (same weights, our loader) | 1 release, D | AMSL 9.8, FM 1.0, OCV 0.4, WM 11.3; MAD22 FM 0.0, OCV 2.0, WM 19.0 | AMSL 41.8, FM 5.8, OCV 3.4, WM 41.2; MAD22 FM 5.9, OCV 2.7, WM 20.0 | 0.774 [pair 0.756, 0.792], above | Same pattern as row 1. FM/OCV kept (≤ 6%); AMSL and WM fall to ~41%; flags 71% of half-size photos. |
| 3 | **MADation release ViT-B/16** (CLIP ViT-B/16 with LoRA, SMDD) | 1 release (A36 primary) | AMSL 15.1, FM 2.8, OCV 2.9, WM 4.9; MAD22 FM 0.6, OCV 2.7, WM 6.4 | FM 4.42 [person 2.12, 6.93] (R, F4 (ii)), OCV 4.42 [2.08, 7.37], WM 10.8, **AMSL 28.9 (+13.8)**; MAD22 FM 5.94 [3.25, 10.62], OCV 3.7, WM 7.0 | 0.727 [0.712, 0.742]; D +0.045, **label "not above the floor"** (orig 0.770, above) | **Mostly yes.** FM, OCV and WM-type morphs stay at 4-11% and MAD22 families at ≤ 7%; AMSL doubles. The detector does react to shrunk photos (photo-only AUC 0.62 → 0.91), and at its native threshold it would flag 72% of photos shrunk to MAD22 FaceMorpher's face size. The morphs still rank above them. On clean Poisson morphs it beats the file-size floor on orig, but not by the registered label on pp. |
| 4 | **MADation release ViT-L/14** | 1 release (A36 primary; A41's negative-control detector) | AMSL 17.7, FM 1.0, OCV 1.0, WM 4.9; MAD22 FM 0.0, OCV 0.6, WM 10.2 | Unchanged: AMSL 14.7, FM 1.0, OCV 1.0, WM 4.4; MAD22 FM 0.55, OCV 0.6, WM 10.2 | 0.684 [0.667, 0.701]; D +0.002, not above (orig 0.718, above) | **Yes on the benchmarks, but the clean test sits at the floor.** Its landmark results do not depend on photo downsampling (photo-only AUC 0.45-0.49, "none"). It flags 45-53% of JPEG-50 photos at its native threshold, so it reads other processing, and on clean Poisson morphs it does no better than file size. |
| 5 | **MADation release FE ViT-B/16** (frozen CLIP + head) | 1 release, D | AMSL 26.0, FM 16.7, OCV 18.6, WM 22.5; MAD22 FM 1.0, OCV 21.1, WM 40.1 | AMSL 38.7, FM 22.6, OCV 26.0, WM 31.9; MAD22 FM 7.2, OCV 21.5, WM 41.1 | 0.681 [0.668, 0.695], at floor (orig 0.681, above) | **Weak, and weaker under E7** (+6 to +13 on FRLL). |
| 6 | **MADation release FE ViT-L/14** (frozen CLIP + head) | 1 release, D | AMSL 21.6, FM 3.9, OCV 4.4, WM 9.8; MAD22 FM 1.6, OCV 5.5, WM 11.9 | AMSL 23.0, FM 4.4, OCV 4.9, WM 10.3; MAD22 FM 2.7, OCV 5.5, WM 11.9 | 0.745 [0.731, 0.760], above | **Yes, nearly unchanged**, and above floor on the clean test. |
| 7 | **MADation release FS ViT-B/16** (ViT from scratch + head) | 1 release, D | AMSL 40.6, FM 16.7, OCV 3.9, WM 32.1; MAD22 FM 30.3, OCV 4.3, WM 8.6 | AMSL 40.7, FM 17.3, OCV 5.4, WM 34.8; MAD22 FM 47.6, OCV 4.3, WM 9.1 | 0.422 [0.400, 0.443], below chance | **No** on the clean test. Benchmark detection is uneven, and MAD22 FM falls to chance under E7. |
| 8 | **MADation release FS ViT-L/14** | 1 release, D | 28-39 on every landmark family | Unchanged (27.6-39.7) | 0.536 [0.516, 0.556] | **No** (weak everywhere). |
| 9 | **MixFaceNet-MAD release** (official SMDD weights, "on our frames (loader checked on its own training files)") | 1 release, D (A36 amendment 2) | AMSL 82.8, FM 98.0, OCV 98.0, WM 75.5; MAD22 FM 85.4, OCV 12.5, WM 20.6 (published MAD22-5 13.69 / FRLL-5 8.96; ours 41.7 / 76.5) | AMSL 86.8, FM 98.0, OCV 98.1, WM 80.4; MAD22 FM 91.9, OCV 13.0, WM 21.1 | 0.598 (point), below floor | **No.** On our frames it ranks the FRLL photos above FRLL landmark morphs, with or without the control. It detects only MAD22 OpenCV and Webmorph (12-21%), where E7 changes nothing. On clean Poisson morphs it is below the file-size floor. FFHQ landmark_complete AUC 0.859. |
| 10 | **M1 Inception-MAD R × d0** (Inception-v3 from scratch @299) | 5 seeds | AMSL 27.5±10.3, FM 53.6±10.6, OCV 53.6±19.5, WM 24.9±10.6; MAD22 FM 6.4±1.2, OCV 3.3±1.4, WM 12.4±2.2 | AMSL 46.3, FM 71.5, OCV 72.2, WM 42.1; **MAD22 FM 39.0±18.1 (+32.6)**; OCV 4.0, WM 13.7 | 0.603 [0.594, 0.613], below | **No.** FRLL landmark morphs sit at or below the photos natively and fall further under the control. MAD22 FaceMorpher goes from 6% to 39% once photos are shrunk to its face size. The two MAD22 families it does detect are the ones where E7 changes almost nothing. Clean Poisson morphs: below the file-size floor. |
| 11 | **M2 MorphHRNet-style R × d0** (HRNet-W48 from scratch @256) | 5 seeds | FRLL 67.5-90.7 (inverted); MAD22 FM 51.6±17.2, OCV 12.0, WM 19.2 | FRLL 73.7-92.5; MAD22 FM 73.8 (+22.2), OCV 12.6, WM 19.6 | 0.594 [0.587, 0.602], below | **No.** It ranks FRLL photos above FRLL landmark morphs, and the inversion is not caused by the photo pool or JPEG (A12-4 H-new-B "falsified"). |
| 12 | **M3 MADation ViT-B/16 R × d0** (CLIP ViT-B/16 + LoRA r2, low LR, early stop) | 8 seeds | AMSL 10.8±3.1, FM 3.3±0.8, OCV 5.7±1.4, WM 8.6±2.4; MAD22 FM 5.0±1.7, **OCV 23.6±2.9, WM 22.4±3.5** | Unchanged (+0.1 to +0.6): 11.4, 3.6, 5.8, 8.8; MAD22 5.3, 23.7, 22.5 | 0.750 [0.735, 0.765], above (orig 0.805) | **Yes, unaffected by the control.** It flags only 5.9% of half-size photos, close to the 5.4% native rate. MAD22 OpenCV/Webmorph stay weak (published OpenCV 3.85). |
| 13 | **M3L MADation ViT-L/14 R × d0** | 5 seeds | AMSL 15.0±2.0, FM 0.4, OCV 0.3, WM 7.8; MAD22 FM 0.6, OCV 8.6±3.5, WM 15.8±3.1 | Unchanged: 14.5, 0.4, 0.3, 7.6; MAD22 0.5, 8.6, 15.8 | 0.810 [0.793, 0.826], above (orig 0.833) | **Yes, unaffected**, and the best clean-test AUC among the R × d0 rows. |
| 14 | **M4 SelfMAD-style R × d0b** (HRNet-W18 IN-1k, SAM, self-blended fakes from SMDD photos only @384) | 5 seeds | **Inverted:** AMSL 100.0, FM 90.9±4.8, OCV 38.3±6.8, WM 100.0; MAD22 FM 99.8±0.5, OCV 32.9, WM 48.3 | AMSL 100.0, FM 82.0, OCV 24.5; **MAD22 FM 0.8±0.7 (−98.9)**, OCV 31.6, WM 47.0 | 0.761 [0.744, 0.779], above | **Not on the benchmarks.** It scores genuine studio photos as more morph-like than landmark morphs. Shrinking the photos makes them look genuine to it (MAD22 FM 99.8% → 0.8%), the opposite direction from the SelfMAD release. On clean Poisson morphs it is above the file-size floor, so some landmark signal exists, but the benchmark photos swamp it. |
| 15 | **M5 PW-MAD R × d0** (DenseNet-121 to transition 2 + pixel map @224) | 8 seeds | AMSL 8.9±8.6, FM 14.4±14.3, OCV 15.8±16.7, WM 4.2±2.4; MAD22 FM 1.2±1.5, OCV 7.7, WM 20.9 | AMSL 25.7, FM 24.5, OCV 28.8, WM 14.3 (+10 to +17); **MAD22 FM 20.7 (+19.5)**; OCV 7.9, WM 21.2 | 0.547 [0.538, 0.555], below | **No.** Fair natively, but it loses 10-20 points on every family with a real dose. Clean Poisson morphs: below the floor. |
| 16 | **M6 OrthoMAD R × d0** (ResNet-18 from scratch, orthogonal heads @224) | 5 seeds | FRLL 59.8-81.4 (inverted); MAD22 FM 24.4, OCV 9.4, WM 16.9 | FRLL 67.7-85.8; MAD22 FM 47.5 (+23.1), OCV 10.0, WM 17.6 | 0.653 [0.641, 0.665], not above | **No.** Inverted on FRLL, and the inversion is not caused by the photo pool or JPEG (H-new-B "falsified"). |
| 17 | **M8 MixFaceNet-MAD R × d0** (MixFaceNet-S port, from scratch) | 5 seeds | FRLL 44.8-66.5; MAD22 FM 27.6±26.8, OCV 6.4, WM 14.0 | FRLL 61.7-75.2; MAD22 FM 65.7 (+38.2), OCV 6.8, WM 14.9 | 0.648 [0.637, 0.659], below | **No** (only MAD22 OpenCV/Webmorph, where E7 is ~1.0x). |
| 18 | **M8O MixFaceNet-MAD official code O × d0** | 5 seeds | FRLL 54.1-85.1; MAD22 FM 30.8, OCV 6.1, WM 14.7 | FRLL 65.2-88.5; MAD22 FM 70.3 (+39.5 ±t95 9.9) | 0.631 [0.621, 0.642], below | **No.** Same as M8; at its native threshold it flags 26.7% of half-size photos. |

**Bottom line for the landmark column.**
- **Keep their landmark detection under E7 and on the clean test:** only CLIP-based rows. These are the MADation recipe retrains (M3, M3L R × d0; 8 + 5 seeds) and the FE ViT-L/14 release (1 network). The ViT-B/16 and ViT-L/14 releases keep most of their benchmark numbers (ViT-B/16's AMSL doubles) but sit at the clean-test floor on `pp`.
- **The SelfMAD release keeps FaceMorpher/OpenCV-type morphs and the clean Poisson morphs.** It loses AMSL and WebMorph once the photos are shrunk to those morphs' face size. That is numerically C1's pattern, but no registered test covers landmark cells, so no grade or "shortcut" word applies.
- **Every SMDD-trained CNN recipe (M1, M2, M4, M5, M6, M8, M8O) and the MixFaceNet-MAD release fail.** They are inverted on FRLL natively, or they collapse on MAD22 FaceMorpher under E7, and they sit at or below the file-size floor on H1 (M4 is the exception on H1).
- **Their "good" MAD22 OpenCV/Webmorph numbers do not test the cue:** E7 there is ~1.0x.
- **Reviewer's count** (A36 amendment 2 post-result review; not blind, not recounted): an FRLL FM or OCV native EER above 50 occurs in 28 of 38 published-recipe SMDD CNN networks, 3 of 33 our-protocol P × d0 CNNs (M4 only), 0 of 46 CLIP networks, and the MixFaceNet-MAD release (98%).
- **How the methods work, as far as the logs show.**
  - SelfMAD: CONCLUSIONS mechanism note, consistent with C1, not tested. Its released training code builds every fake from a photo blended with a Lanczos-resampled zoom of itself, and never resamples the genuine partner. A network trained that way could treat traces of resampling as a sign of a morph. That fits its landmark pattern here, where the score rises with how much a genuine photo was shrunk. It does not explain it (and never "learned from RandomDownScale").
  - MADation: the skill sits mostly in the frozen CLIP features (A12-4: a linear head alone gives UA8c 15.2%). That is consistent with the CLIP rows' insensitivity to E7 here.
  - SMDD-trained CNN recipes: no reproduction (A12-BR, falsified for M1, M2, M4, M5, M6, M8). Their benchmark rankings follow which benchmark the morph file comes from (the OpenCV cross-benchmark check in §3), not the landmark warp-and-blend.

---

## 2. Detail: FRLL-Morphs landmark families, EER % native → E7 (Δ)

Thresholded. Doses: FM 1.47x, OCV 1.56x, AMSL/WM 1.80x.

| method | n | AMSL | FaceMorpher | OpenCV | WebMorph | source / status |
|---|---|---|---|---|---|---|
| SelfMAD release, own preprocessing | 1 | 2.9 → 33.3 (+30.4) | 0.4 → 4.8 (+4.4) | 0.1 → 3.9 (+3.8) | 5.9 → 51.9 (+46.1) | A32 `rsx_read.json` networks[].summary; D (A32 registered H1 covers MorDIFF/Greedy-DiM only) |
| SelfMAD release, our pipeline | 1 | 9.8 → 41.8 (+32.0) | 1.0 → 5.8 (+4.8) | 0.4 → 3.4 (+3.0) | 11.3 → 41.2 (+29.9) | same; D. Also A12-4 stage 1 H-new-A (no-TTA): FRLL-5 E7 24.03 vs orig 10.09 |
| MADation release ViT-B/16 | 1 | 15.1 [boot95 12.2, 17.2] → 28.9 [25.4, 31.5] | 2.8 → 4.4 [2.9, 6.4] | 2.9 → 4.4 [3.3, 6.4] | 4.9 → 10.8 [8.5, 13.3] | A36 `a36_read.json` RSX.rows (fam, boot95); D (H-new-75 is MorDIFF/Greedy-DiM) |
| MADation release ViT-L/14 | 1 | 17.7 → 14.7 (−2.9) | 1.0 → 1.0 | 1.0 → 1.0 | 4.9 → 4.4 (−0.5) | same; D |
| MADation release FE ViT-B/16 | 1 | 26.0 → 38.7 (+12.7) | 16.7 → 22.6 (+5.9) | 18.6 → 26.0 (+7.4) | 22.5 → 31.9 (+9.4) | same; D |
| MADation release FE ViT-L/14 | 1 | 21.6 → 23.0 (+1.5) | 3.9 → 4.4 (+0.5) | 4.4 → 4.9 (+0.5) | 9.8 → 10.3 (+0.5) | same; D |
| MADation release FS ViT-B/16 | 1 | 40.6 → 40.7 | 16.7 → 17.3 | 3.9 → 5.4 (+1.5) | 32.1 → 34.8 (+2.7) | same; D |
| MADation release FS ViT-L/14 | 1 | 39.2 → 39.7 | 38.2 → 37.7 | 31.9 → 32.8 | 32.9 → 32.8 | same; D |
| MixFaceNet-MAD release | 1 | 82.8 → 86.8 (+4.0) | 98.0 → 98.0 | 98.0 → 98.1 | 75.5 → 80.4 (+4.9) | A36 `a36_a2.json` row_a36.RSX.fam; D |
| M1 Inception-MAD R × d0 | 5 | 27.5±10.3 → 46.3±8.1 (+18.8) | 53.6±10.6 → 71.5±9.3 (+17.9) | 53.6±19.5 → 72.2±13.8 (+18.7) | 24.9±10.6 → 42.1±8.6 (+17.1) | A12-4 `a12_4_read_stage1.json` arms["M1:r:d0"]; D (orig pool = A12.4 diagnostic; E7 per-family feeds the registered BENCH endpoint) |
| M2 MorphHRNet-style R × d0 | 5 | 73.2±8.8 → 79.7±6.1 (+6.6) | 90.7±3.3 → 92.5±2.6 (+1.8) | 87.1±2.7 → 90.0±2.5 (+2.9) | 67.5±8.7 → 73.7±6.4 (+6.3) | arms["M2:r:d0"]; D |
| M3 MADation ViT-B/16 R × d0 | 8 | 10.8±3.1 → 11.4±3.3 (+0.6) | 3.3±0.8 → 3.6±0.8 (+0.3) | 5.7±1.4 → 5.8±1.4 (+0.1) | 8.6±2.4 → 8.8±2.5 (+0.2) | arms["M3:r:d0"]; also A32 RSX with ±t95 (e.g. AMSL Δ +0.59 ± 0.66); D |
| M3L MADation ViT-L/14 R × d0 | 5 | 15.0±2.0 → 14.5±1.9 (−0.5) | 0.4±0.0 → 0.4±0.0 | 0.3±0.2 → 0.3±0.2 | 7.8±1.7 → 7.6±1.7 (−0.3) | arms["M3L:r:d0"]; D |
| M4 SelfMAD-style R × d0b | 5 | 100.0 → 100.0 | 90.9±4.8 → 82.0±4.3 (−8.9) | 38.3±6.8 → 24.5±4.3 (−13.8) | 100.0 → 100.0 | arms["M4:r:d0b"]; D |
| M5 PW-MAD R × d0 | 8 | 8.9±8.6 → 25.7±8.2 (+16.8) | 14.4±14.3 → 24.5±11.3 (+10.2) | 15.8±16.7 → 28.8±12.1 (+13.0) | 4.2±2.4 → 14.3±6.0 (+10.1) | arms["M5:r:d0"]; D |
| M6 OrthoMAD R × d0 | 5 | 66.8±7.7 → 74.6±6.7 (+7.9) | 61.3±9.4 → 67.7±9.1 (+6.5) | 81.4±15.3 → 85.8±12.8 (+4.4) | 59.8±9.9 → 69.3±8.5 (+9.4) | arms["M6:r:d0"]; D |
| M8 MixFaceNet-MAD R × d0 | 5 | 46.9±5.7 → 63.6±3.5 (+16.7) | 66.5±18.6 → 75.2±14.8 (+8.7) | 57.4±20.8 → 70.1±15.5 (+12.6) | 44.8±4.0 → 61.7±3.6 (+16.8) | arms["M8:r:d0"]; D |
| M8O MixFaceNet-MAD official code O × d0 | 5 | 55.8±11.4 → 66.4±10.1 (+10.6) | 85.1±10.7 → 88.5±9.0 (+3.4) | 78.4±14.3 → 84.1±11.4 (+5.8) | 54.1±12.0 → 65.2±10.0 (+11.1) | arms["M8O:ocode:d0"]; A32 RSX ±t95 (AMSL Δ +10.61 ± 3.46); D |

**Raw files, SelfMAD's own crop, native pool** (A41 X7', `a41g_x7.json` raw_eer.score; [95%]): AMSL 2.44 [0.95, 4.57], FM 0.98 [0.05, 1.69], OCV 0.37 [0.00, 0.60], StyleGAN 16.60, WM 7.36 [4.96, 10.61], FRLL-5 mean 5.55 (published 2.96).
- Registered: H-new-145 says "published regime reproduced on raw files". The per-family values are D.
- No raw-file E7 exists for any landmark family. S12's raw-file E7 covers Greedy-DiM, DiM-A and MorDIFF only.

## 3. Detail: MAD22 landmark families, EER % native → E7 (Δ)

Thresholded. Doses: OCV/WM ~1.0x (E7 is almost a no-op), FM 3.30x. The MAD22 FM files are 256-px JPEGs and so carry cues of their own (A41 S3 caveat).

| method | n | FaceMorpher | OpenCV | Webmorph | source / status |
|---|---|---|---|---|---|
| SelfMAD release, own preprocessing | 1 | 0.0 → **0.11 [person 0.00, 0.89]** | 0.6 → 1.1 | 13.6 → 19.0 (+5.4) | A32 RSX; FM cell = A41 S3 (i) `a41_eval.json` S3.components.i, **R** (F4 / H-new-150 supported, IUT p = 0.0001 at Holm level 0.01) |
| SelfMAD release, our pipeline | 1 | 0.0 → 5.9 | 2.0 → 2.7 | 19.0 → 20.0 | A32 RSX; D |
| MADation release ViT-B/16 | 1 | 0.6 [boot95 0.0, 1.65] → **5.94 [person 3.25, 10.62]** | 2.7 → 3.7 | 6.4 → 7.0 | A36 RSX; FM E7 CI from A41 S3 positive_controls_beside; D |
| MADation release ViT-L/14 | 1 | 0.0 → 0.55 | 0.6 → 0.6 | 10.2 → 10.2 | A36 RSX; D |
| MADation release FE ViT-B/16 | 1 | 1.0 → 7.2 (+6.1) | 21.1 → 21.5 | 40.1 → 41.1 | A36 RSX; D |
| MADation release FE ViT-L/14 | 1 | 1.6 → 2.7 | 5.5 → 5.5 | 11.8 → 11.8 | A36 RSX; D |
| MADation release FS ViT-B/16 | 1 | 30.3 → 47.6 (+17.3) | 4.3 → 4.3 | 8.6 → 9.1 | A36 RSX; D |
| MADation release FS ViT-L/14 | 1 | 32.9 → 35.7 | 28.1 → 27.6 | 32.4 → 31.9 | A36 RSX; D |
| MixFaceNet-MAD release | 1 | 85.4 → 91.9 (+6.5) | 12.5 → 13.0 | 20.6 → 21.1 | A36 a2 RSX; D |
| M1 R × d0 | 5 | 6.4±1.2 → 39.0±18.1 (+32.6) | 3.3±1.4 → 4.0±1.2 | 12.4±2.2 → 13.7±2.4 | A12-4 stage 1; D |
| M2 R × d0 | 5 | 51.6±17.2 → 73.8±16.7 (+22.2) | 12.0±2.4 → 12.6±2.5 | 19.2±2.4 → 19.6±2.1 | same; D |
| M3 R × d0 | 8 | 5.0±1.7 → 5.3±1.9 | 23.6±2.9 → 23.7±3.0 | 22.4±3.5 → 22.5±3.4 | same; D (A12-BR reproduction: per family OpenCV 23.7 vs published 3.85) |
| M3L R × d0 | 5 | 0.6±0.2 → 0.5±0.1 | 8.6±3.5 → 8.6±3.5 | 15.8±3.1 → 15.8±3.1 | same; D |
| M4 R × d0b | 5 | 99.8±0.5 → 0.8±0.7 (−98.9) | 32.9±10.3 → 31.6±10.5 | 48.3±4.4 → 47.0±4.0 | same; D |
| M5 R × d0 | 8 | 1.2±1.5 → 20.7±7.7 (+19.5) | 7.7±4.0 → 7.9±3.8 | 20.9±8.8 → 21.2±8.1 | same; D |
| M6 R × d0 | 5 | 24.4±8.2 → 47.5±12.7 (+23.1) | 9.4±2.5 → 10.0±2.6 | 16.9±2.7 → 17.6±2.6 | same; D |
| M8 R × d0 | 5 | 27.6±26.8 → 65.7±14.6 (+38.2) | 6.4±1.2 → 6.8±1.1 | 14.0±1.0 → 14.9±1.4 | same; D |
| M8O O × d0 | 5 | 30.8±11.2 → 70.3±9.3 (+39.5; t95 ±9.89 in A32) | 6.1±1.6 → 6.7±1.9 | 14.7±1.7 → 15.2±2.1 | same + A32 RSX; D |

**Cross-benchmark check with the same genuine photos** (A12-BR README, post-result review, E7 numbers; D). The 185 MAD22 photos are byte copies of FRLL photos. OpenCV-tool morphs at 1351 px (MAD22) and at 431 px (FRLL), R × d0:
- M1: 4.0 vs 72.2
- M2: 12.6 vs 90.0
- M6: 10.0 vs 85.8
- M8: 6.8 vs 70.1
- P × d0 flips the sign (M1: 25.8 vs 10.7).

The same tool is detected in one benchmark and inverted in the other against the same photos. So these CNN rankings follow the benchmark's morph files, not the OpenCV warp-and-blend.

## 4. Detail: other controls

### 4a. Photo-only dose ladder (A41 S7, H-new-136)

AUC of shrunk copies vs the same 185 photos at native size. Threshold-free, [person 95%]. Registered secondary rule; reader labels stored as open. Source: `a41_eval.json` S7.rows.

| release | ~1.0x (MAD22 OCV/WM) | 1.47x (FRLL FM) | 1.56x (FRLL OCV) | 1.80x (FRLL AMSL/WM) | 3.30x (MAD22 FM) | label |
|---|---|---|---|---|---|---|
| SelfMAD, own preprocessing | 0.584 [0.564, 0.609] | 0.896 [0.869, 0.925] | 0.927 [0.902, 0.952] | 0.968 [0.950, 0.984] | 0.998 [0.995, 1.000] | dose response |
| SelfMAD, our pipeline | 0.555 [0.542, 0.573] | 0.788 [0.760, 0.823] | 0.823 [0.794, 0.857] | 0.889 [0.860, 0.919] | 0.983 [0.971, 0.993] | dose response |
| MADation ViT-B/16 | 0.524 [0.518, 0.532] | 0.622 [0.608, 0.644] | 0.638 [0.622, 0.663] | 0.682 [0.660, 0.711] | 0.906 [0.875, 0.937] | neither |
| MADation ViT-L/14 | 0.494 [0.489, 0.497] | 0.479 [0.469, 0.486] | 0.477 [0.467, 0.486] | 0.469 [0.456, 0.479] | 0.455 [0.422, 0.488] | none (calibration check passed) |

Reading (gatherer's, post hoc): these AUCs measure how much the release's score reacts to nothing but shrinking a genuine photo to each landmark family's face size. For SelfMAD that reaction is almost as large as its native separation of AMSL/WM morphs, which is why those two families fall apart under E7. It is not as large for FM/OCV, where the morphs score higher still.

### 4b. Fixed-threshold view: % of genuine photos flagged at the network's native BPCER-5% threshold

Thresholded; D. Native rate 5.4 by construction.

| network | FRLL half-size (resample50) | FRLL JPEG-50 | FRLL E7 pools (pooled) | MAD22 half-size | MAD22 E7 pools | source |
|---|---|---|---|---|---|---|
| SelfMAD release, own | 95.1 | 1.5 | 58.9 | 95.1 | 26.5 | A32 rsx_read.md "Mechanism" (M: registered, "supported" for this row) |
| SelfMAD release, our pipeline | 71.1 | 1.5 | 37.4 | 71.9 | 24.1 | same; D |
| MADation release ViT-B/16 | 28.9 | 4.4 | 16.4 (per family: AMSL/WM 22.5, FM 14.7, OCV 16.7) | 28.1 | 18.9 (**MAD22 FM pool 71.9**, OCV/WM 5.9) | A36 RSX mech / e7_bpcer_at_native_t5; D |
| MADation release ViT-L/14 | 4.9 | **52.9** | 4.9 | 4.9 | 5.5 | same; D (H-new-87: BPCER rises with JPEG compression) |
| MADation FE ViT-B/16 / FE ViT-L/14 | 23.5 / 7.4 | 6.4 / 6.4 | 14.4 / 6.7 | 22.7 / 7.0 | 13.2 / 6.4 | same; D |
| MADation FS ViT-B/16 / FS ViT-L/14 | 20.6 / 5.9 | 5.9 / 5.4 | 11.8 / 5.9 | 20.5 / 5.4 | 12.8 / 5.5 | same; D |
| MixFaceNet-MAD release | 18.1 | 4.9 | 11.8 (per family 11.3-15.2) | 18.9 | 12.5 (MAD22 FM pool 38.9) | A36 a2 RSX; D. Not a resolution sentence (drop list) |
| M3 MADation R × d0 (8) | 5.9 ± 0.8 | 9.3 ± 2.8 | 5.7 ± 0.3 | 5.9 ± 1.0 | 5.5 ± 0.2 | A32 rsx_read.md (M: registered, "not supported" for this row) |
| M8O MixFaceNet-MAD O × d0 (5) | 26.7 ± 5.6 | 4.7 ± 0.8 | 15.1 ± 3.1 | 27.4 ± 5.3 | 16.8 ± 2.0 | A32; D |

Do not quote the MixFaceNet-MAD release's flag rates at the VALX-A* threshold. That threshold sits far below its own operating point (CONCLUSIONS).

### 4c. Effect of degrading both classes on the inverted FRLL families (A12-4 H-new-B)

Shift vs the orig pool, R × d0; D. Source: `a12_4_read_stage1.md` §(ii).

| arm | resample50 shift on OCV / FM | jpeg50 shift on OCV / FM | verdict |
|---|---|---|---|
| M1 | +13.6 ±10.0 / +20.8 ±6.3 | −0.9 / +4.8 | mixed |
| M8 | +8.7 / +8.8 | −0.9 / +5.3 | mixed |
| M2 | +3.6 / +3.3 | −0.5 / +0.3 | falsified (the inversion is no pool or JPEG effect) |
| M6 | −2.2 / +0.0 | −0.2 / +4.6 | falsified (the inversion is no pool or JPEG effect) |

M3, M3L and M5 were not tested (no inversion).

### 4d. H1 Poisson (clean landmark set), AUC [pair 90%]

Threshold-free. A36 amendment 1 reader `a36_a1.md` §(5), registered label (orig primary, pp beside). Exploratory, post-freeze. Floors: orig 0.620, pp 0.681.

| row | n | H1 orig | label | H1 pp | label |
|---|---|---|---|---|---|
| SelfMAD release, own preprocessing | 1 | 0.872 | above (A39 sensitivity: rows above 5 → 6) | 0.821 | point only (`a36_read_own.json`; EER pp 26.9%) |
| SelfMAD release, our pipeline | 1 | 0.844 [0.828, 0.859] | above | 0.774 [0.756, 0.792] | above |
| MADation release ViT-B/16 | 1 | 0.770 [0.754, 0.785] | above | 0.727 [0.712, 0.742] | not above (D +0.045) |
| MADation release ViT-L/14 | 1 | 0.718 [0.702, 0.736] | above | 0.684 [0.667, 0.701] | not above (D +0.002) |
| FE ViT-B/16 / FE ViT-L/14 | 1 / 1 | 0.681 / 0.735 | above / above | 0.681 / 0.745 | not above / above |
| FS ViT-B/16 / FS ViT-L/14 | 1 / 1 | 0.472 / 0.554 | not above | 0.422 / 0.536 | not above |
| MixFaceNet-MAD release | 1 | 0.572 | (A36 a2 row; below floor) | 0.598 | below floor |
| M1 R × d0 | 5 | 0.564 [0.557, 0.572] | not above | 0.603 [0.594, 0.613] | not above |
| M2 R × d0 | 5 | 0.570 | not above | 0.594 | not above |
| M3 R × d0 | 8 | 0.805 [0.791, 0.818] | above | 0.750 [0.735, 0.765] | above |
| M3L R × d0 | 5 | 0.833 [0.816, 0.849] | above | 0.810 [0.793, 0.826] | above |
| M4 R × d0b | 5 | 0.761 [0.741, 0.780] | above | 0.761 [0.744, 0.779] | above |
| M5 R × d0 | 8 | 0.533 | not above | 0.547 | not above |
| M6 R × d0 | 5 | 0.623 (D +0.002) | not above | 0.653 | not above |
| M8 R × d0 | 5 | 0.588 | not above | 0.648 | not above |
| M8O O × d0 | 5 | 0.580 | not above | 0.631 | not above |

PROTOCOL bullet (A36 amendment 1 results, item (5), ~line 10130): "orig, 5 of the 11 primary rows above the bytes-only (0.620) and eye-geometry floors: M3 0.805, M3L 0.833, M4 0.761, MADation official ViT-B/16 0.770 and ViT-L/14 0.718; the CNN rows are 0.533 to 0.623."

### 4e. FFHQ-Morphs landmark families vs their E7 pool, AUC

Threshold-free. A36 (C) table in `a36_read.md` / `a36_read_own.md`; seed mean; D. See the caveats in §0 (README "unfit", cue-only AUC 0.93).

| row | landmark_complete | landmark_combined |
|---|---|---|
| SelfMAD own / our pipeline | 0.959 / 0.932 | 0.918 / 0.828 |
| MADation ViT-B/16 / ViT-L/14 | 0.996 / 1.000 | 0.700 / 0.539 |
| FE B/16 / FE L/14 / FS B/16 / FS L/14 | 0.975 / 0.992 / 0.874 / 0.832 | 0.757 / 0.820 / 0.509 / 0.541 |
| MixFaceNet-MAD release | 0.859 (EER 23.9) | 0.579 |
| M1 / M2 / M3 / M3L / M4 | 0.973 / 0.921 / 0.989 / 0.996 / 0.841 | 0.666 / 0.615 / 0.881 / 0.818 / 0.788 |
| M5 / M6 / M8 / M8O | 0.981 / 0.937 / 0.937 / 0.945 | 0.700 / 0.667 / 0.689 / 0.683 |

Reading (gatherer's, post hoc): almost every row reaches AUC above 0.92 on landmark_complete. This includes rows that fail H1 and invert on FRLL. Because a cue-only detector already reaches 0.93 there, landmark_complete does not show morph-artefact reading. landmark_combined separates the rows more, and broadly follows H1.

**A39 R3, photo side on FFHQ** (SelfMAD own; H-new-95 registered, verdict "neither"). At its VALX-A* threshold it flags these shares of FFHQ photos shrunk to the 64.6 px landmark-family face size:
- landmark_complete pool: 14.9% vs 7.8% native (+7.1 [+5.6, +8.6]).
- landmark_combined pool: 15.2% (+7.3 [+5.9, +8.8]).

Without a threshold, the score rise is a median +0.23 to +0.28 on 0-1 (A40, D).

### 4f. Cue-only floor (A8 26-scalar detector)

EER %, trained on our D1 sample, scored on our 512-px frames. Source: E07 raw/data-shortcut.md §2; D.

| family | vs original photos | vs E7 photos |
|---|---|---|
| FRLL FM | 4.4 | 9.4 |
| FRLL OCV | 11.2 | 29.9 |
| FRLL WM | 9.4 | 38.7 |
| MAD22 FM | 6.9 | 21.1 |
| MAD22 OCV | 10.9 | 15.2 |
| MAD22 WM | 22.1 | 29.8 |

Simple image statistics alone get within a few points of several published methods under E7. For example, SelfMAD's FRLL FM is 4.8 against the floor's 9.4. In the same document:
- Zero-border fraction alone separates FRLL landmark morphs from E7 photos at AUC 1.00, and MAD22 landmark morphs at 0.69.
- MAD22 FM morphs have more Haar-HH energy than their E7 photos (AUC 0.95).

### 4g. Construction attributes in the raw files (A41 DC-A, H-new-155 "supported")

One-feature O = max(AUC, 1 − AUC), header only. Source: `a41_files.md`.
- **MAD22 FM is a registered decision cell.** Width, bpp and IED are documented and confirmed, with O = 1.000, so claim B applies to it: "Morph and bona fide files differ in documented construction attributes that alone separate the classes."
- **Other landmark cells (D).**
  - MAD22 OCV: width 1.000, JPEG quality 1.000.
  - MAD22 WM: chroma subsampling 1.000, bpp 0.798.
  - FRLL AMSL / FM / OCV / WM: width 1.000 and JPEG quality 1.000 each.

---

## 5. Appendix (descriptive): the same recipes trained with our protocol and our data (P × d1)

These are not the published methods. FM, OCV and WM are in-tool for d1. Source: A12-4 stage 1 arms["M*:p:d1"]; H1 from `a36_a1.md`.

| row | n | FRLL AMSL / FM / OCV / WM, native → E7 | MAD22 FM, native → E7 | H1 pp [pair 90%] |
|---|---|---|---|---|
| M1 P × d1 | 5 | 7.1→13.0 / 0.6→0.7 / 0.2→0.5 / 3.4→5.1 | 0.0→7.2 | 0.759, above |
| M2 P × d1 | 5 | 20.1→25.8 / 2.7→3.4 / 2.4→3.0 / 5.5→7.2 | 1.7→7.0 | 0.741, above |
| M3 P × d1 | 8 | 32.4→37.0 / 0.9→1.1 / 1.1→1.4 / 15.7→18.5 | 1.0→3.0 | 0.838, above |
| M4 P × d1 | 5 | 31.4→45.7 / 0.8→2.1 / 0.4→1.6 / 23.2→35.7 | 3.1→3.9 | 0.750, above |
| M5 P × d1 | 8 | 6.7→14.2 / 0.4→0.5 / 0.1→0.5 / 2.3→5.0 | 0.0→9.5 | 0.699, not above |
| M6 P × d1 | 5 | 16.2→21.0 / 1.0→1.9 / 1.5→2.5 / 7.1→10.1 | 1.0→13.1 | 0.756, above |
| M8 P × d1 | 5 | 8.7→15.7 / 1.1→2.6 / 0.8→1.8 / 3.7→6.0 | 0.5→18.7 | 0.768, above |
| M8O O × d1 (official code, our data) | 3 | 42.1→53.8 / 47.7→55.7 / 35.2→43.7 / 19.3→28.9 | 19.1→48.0 | 0.626, not above |

Reading (gatherer's, post hoc): with our training protocol, the same architectures detect in-tool FM/OCV morphs under E7 at 0.5-3.4%. Most of them also clear the H1 pp floor. In CONCLUSIONS terms this is "our training protocol as a whole"; it is not attributed to the morphs alone. AMSL, which is not one of our tools, still rises by 5-14 points under E7.

---

## 6. Sources (all read-only)

- `/home/narolski/mambamorph-code/experiments/CONCLUSIONS.md`, §"What we can claim about shortcuts": grades, wording, drop list. Also the §"Published methods in our pipeline (A12)" bullets used above: MixFaceNet-MAD release wording, the FRLL FM/OCV inversion count, the OpenCV cross-benchmark check.
- `/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/rsx_read.json` (networks[].summary, SelfMAD rows only) and `rsx_read.md` (Mechanism table). PROTOCOL "A32 results" (~line 8277).
- `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/raw/results/a36_read.json` (RSX.rows: fam, boot95, mech, e7_bpcer_at_native_t5), `a36_read.md` and `a36_read_own.md` (§(C) H1 / FFHQM), `a36_read_own.json` (heldout, SelfMAD own), `a36_a1.md` §(5) (H1 pair CIs and labels), `a36_a2.json` (row_a36.RSX, heldout; MixFaceNet-MAD release). PROTOCOL "A36 amendment 1 results" (~line 10110-10130) and "A36 amendment 2 results / post-result review" (~lines 11482, 11522).
- `/home/narolski/mambamorph-code/experiments/A12-4_benchmark-followups/raw/a12_4_read_stage1.json` (arms[*].family_eer_orig / family_eer_e7; mean, sd, n) and `a12_4_read_stage1.md` §(ii) (H-new-B). PROTOCOL "A12.4 read, stage 1" (~line 1943).
- `/home/narolski/mambamorph-code/experiments/A12-BR_benchmark_recipes/README.md`: methods M1-M8O, recipes, OpenCV cross-benchmark numbers, reproduction failures.
- `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv`: primary rows = 51 networks. M1 5, M2 5, M3 8, M3L 5, M4 5, M5 8, M6 5, M8 5, M8O 5. No M7 exists in the list.
- `/home/narolski/mambamorph-code/experiments/A41_shortcut-proof-zero-gpu/raw/results/a41_eval.json` (S3 = F4 components and positive_controls_beside; S7 rows), `a41g_x7.json` (raw-file native), `a41_files.md` (DC-A). A41 registration `raw/entry/A41_entry.md` (S7 dose levels, lines ~132-140). PROTOCOL F4 text (~line 14240).
- `/home/narolski/mambamorph-code/experiments/A39_batch-before-window-close/README.md` (R3) and `/home/narolski/mambamorph-code/experiments/A40_selfmad-detail-sbi-replication-h2-probe/README.md` (Part F): SelfMAD on FFHQ photos.
- `/home/narolski/mambamorph-code/experiments/E07_shortcut_controls/README.md` (E7 definition, pool sizes MAD22 925 / FRLL 1,020) and `raw/data-shortcut.md` (A8: borders, 26-cue floor).
- `/home/narolski/mambamorph-code/smadcvpr/PROTOCOL.md`: §3 (E7 rule), A27 (H1 registration, ~line 7715), A24 (FFHQ-Morphs registration, ~line 7399).
