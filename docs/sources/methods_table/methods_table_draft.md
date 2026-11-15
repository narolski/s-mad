# Competing detectors with the shortcuts removed: regular, GAN and diffusion morphs (draft)

Draft for Paweł Narolski, 2026-11-07. It is built only from the three read-only gathers in this folder (`gather_regular.md`, `gather_gan.md`, `gather_diffusion.md`), which copy values out of logged reader outputs. No new number was computed for this draft.

- **MADMamba is not in this table.** Its results are sealed, and it was not scored on these controls ("MADMamba not evaluated on H3 (sealed)").
- No W3, E10 or FST number is used.
- Grades and allowed wording follow the final section of `experiments/CONCLUSIONS.md`, "What we can claim about shortcuts".

## 1. What "once shortcuts are not available" means, and how we tested it

**What it means.** A morph detector has to tell morphs (one face image built from two people) apart from genuine photos of one person. On the standard benchmarks, the two classes were also made in different ways:

- The genuine photos are large, high-quality camera JPEG files.
- The morphs are files of other sizes and formats, with smaller faces.
- Morphs from the landmark tools also carry black borders left by face alignment.
- In each of the ten registered cells (the seven FRLL diffusion families and three MAD22 families), one documented file attribute alone (file format, width, bits per pixel or face size) separates morphs from genuine photos perfectly (claim B); the other landmark families show the same in descriptive header checks. FRLL is the Face Research Lab London set; MAD22 is the SYN-MAD 2022 benchmark.
- GAN morphs (GAN: generative adversarial network) and diffusion morphs are also the output of an image generator, while the genuine photos come from a camera.

A detector can therefore score well just by noticing how the file or picture was made, without noticing that two identities were blended. We call such a difference a "shortcut". To see what a detector does without it, we keep the morphs fixed and replace the genuine side with images made the same way as the morphs but showing only one person. Then we score the same networks again.

We report two kinds of number:
- **Equal error rate (EER, in %).** The error rate when the decision threshold is set so that missed morphs and false alarms on genuine images are equally frequent. 0 is perfect and 50 is chance. Above 50 means the detector rates the genuine images as more morph-like than the morphs ("inverted"). It depends on a threshold.
- **Area under the curve (AUC).** The chance that a random morph scores above a random comparison image. 0.5 is chance, and below 0.5 means the comparison images look more morph-like. It needs no threshold.

Each control also has a "floor": the AUC that a simple statistic, such as file size or eye position, reaches on the same comparison. A detector shows something beyond that statistic only if it clearly beats the floor.

**How we tested it.** The tests differ by morph type.

**Regular morphs.** These are made by warping two faces onto shared facial landmarks and blending them, with the AMSL, FaceMorpher, OpenCV and WebMorph tools. There are two tests:
- **Shrunk genuine photos (labelled E7 in the logs).** Each genuine photo is shrunk to the morphs' face size before the same alignment, by 1.47x to 3.3x depending on the family. This removes the size and processing difference. It leaves the black borders and file headers, and those alone still separate FRLL landmark morphs from the shrunk photos.
- **The clean Poisson test (H1).** A separately built set of 598 pairs of Poisson-blended landmark morphs and genuine images. Both classes come from the same source photos, at the same size, with the same border and the same post-processing. Only a file-size difference is left, and it alone gives AUC 0.681.

**GAN morphs.** The genuine side is replaced by output of the same generator:
- StyleGAN3 renders of a single person (H3).
- The same kind of renders, matched to how spread out the morphs' latent codes are (X4).
- Single-person StyleGAN v1 renders, compared with MIPGAN-style morphs (H4b). File size alone gives 0.912 here.

A latent-average morph and a single-person render are almost the same kind of image by construction. So these tests can show that a detector reads "generator output", but they have little power to show a two-identity signal.

**Diffusion morphs** (FRLL's DiM variants and MorDIFF). There are three tests:
- **Shrunk genuine photos.** The same shrinking as for regular morphs. For the SelfMAD release it was also run on the raw files with its own face crop, and with three different shrinking methods.
- **Genuine photos passed through the morphs' generator family (X3).** The generator family is DiffAE, a diffusion autoencoder. Three pools: its reconstructions of genuine photos, photos that were only resized by its aligner, and one-person "morphs" made from a person's own two photos. Official releases only.
- **Same-generator renders (H2, Arc2Face).** Morphs from two other diffusion generators, compared with single-person renders from the same generator.

## 2. Comparison table

Each cell gives the benchmark number → the controlled number, then a verdict. The controlled numbers are defined in notes [a]-[f] below the table. "Releases" are the authors' official weights, one network each, scored on our 512-px eye-aligned frames unless the row says otherwise. "Recipes" are our re-implementation of the published training recipe, trained on SMDD only (d0; SMDD is the synthetic morph training set of the SYN-MAD 2022 competition). Recipe numbers are means over the stated number of networks (seeds). ‡ marks the 12 primary rows of the registered GAN test (claim C3).

| # | Method (networks) | Regular (landmark) morphs [a][b] | GAN morphs [c][d] | Diffusion morphs [e][f] |
|---|---|---|---|---|
| **Official releases** | | | | |
| 1 | SelfMAD release, HRNet-W18, its own crop (1) ‡ | EER FM/OCV/AMSL/WM 0.4/0.1/2.9/5.9 → 4.8/3.9/33.3/51.9; MAD22 FM 0.0 → 0.11; H1 AUC 0.821. **partly** | EER MIPGAN-I 0.5 → H3 AUC 0.353 (reversed), X4 0.447; H4b 0.405. **fails** | EER Greedy-DiM 8.4 → 90.7, MorDIFF 2.5 → 61.3 (C1); X3 AUC 0.024 / 0.330; H2 0.510. **fails** |
| 2 | MADation release, CLIP ViT-B/16 + LoRA (1) ‡ | EER 2.8/2.9/15.1/4.9 → 4.4/4.4/28.9/10.8; MAD22 FM 0.6 → 5.9; H1 0.727 (not above floor). **partly** | EER MIPGAN-I 18.4, G-test 9.9 → H3 0.554, X4 0.423; H4b 0.716. **fails** | EER MorDIFF 4.9 → 19.6 (C2), DiM-A 20.6 → 56.4, Greedy-DiM 54.0 → 84.9; X3 MorDIFF 0.847, DiM-A 0.361; H2 0.497. **partly** |
| 3 | MADation release, CLIP ViT-L/14 + LoRA (1) ‡ | EER 1.0/1.0/17.7/4.9 → 1.0/1.0/14.7/4.4; MAD22 FM 0.0 → 0.55; H1 0.684 (at floor). **partly** | EER MIPGAN-I 11.9, G-test 69.5 → H3 0.427 (reversed), X4 0.445; H4b 0.902. **fails** | EER Greedy-DiM 9.8 → 9.8, DiM-A 22.0 → 16.7, MorDIFF 28.9 → 39.7; X3 Greedy-DiM 0.749 (floor 0.993); H2 0.466. **partly** |
| 4 | MADation baseline FE ViT-B/16 (frozen CLIP + head) (1) | EER 16.7/18.6/26.0/22.5 → 22.6/26.0/38.7/31.9; MAD22 FM 1.0 → 7.2; H1 0.681 (= floor). **fails** | EER MIPGAN-I 35.1, G-test 35.1 → H3 0.514, X4 0.451; H4b 0.661. **fails** | EER DiM 21.0-47.0 → 41.6-73.6, MorDIFF 39.7 → 53.5; X3 untested; H2 0.498. **fails** |
| 5 | MADation baseline FE ViT-L/14 (frozen CLIP + head) (1) | EER 3.9/4.4/21.6/9.8 → 4.4/4.9/23.0/10.3; MAD22 FM 1.6 → 2.7; H1 0.745 (above). **works** | EER MIPGAN-I 8.5, G-test 29.1 → H3 0.505, X4 0.475; H4b 0.804. **fails** | EER Greedy-DiM 22.0 → 28.0, MorDIFF 34.8 → 32.4; X3 Greedy-DiM 0.636, MorDIFF 0.742; H2 0.502. **partly** |
| 6 | MADation baseline FS ViT-B/16 (from scratch + head) (1) | EER 16.7/3.9/40.6/32.1 → 17.3/5.4/40.7/34.8; MAD22 FM 30.3 → 47.6; H1 0.422. **fails** | EER MIPGAN-I 17.8, G-test 46.4 → H3 0.511, X4 0.466; H4b 0.546. **fails** | EER DiM 16.1-24.0 → 41.6-45.6, MorDIFF 67.6 → 62.2; X3 untested; H2 0.476. **fails** |
| 7 | MADation baseline FS ViT-L/14 (from scratch + head) (1) | EER 38.2/31.9/39.2/32.9 → 37.7/32.8/39.7/32.8; MAD22 FM 32.9 → 35.7; H1 0.536. **fails** | EER MIPGAN-I 32.5, G-test 67.4 → H3 0.540, X4 0.470; H4b 0.641. **fails** | EER DiM 38.1-47.0 → 40.2-49.0, MorDIFF 43.0 → 42.1; X3 untested; H2 0.502. **fails** |
| 8 | MixFaceNet-MAD release, official SMDD weights (1) | EER 98.0/98.0/82.8/75.5 → 98.0/98.1/86.8/80.4 (inverted); MAD22 FM 85.4 → 91.9; H1 0.598. **fails** | EER MIPGAN-I 47.0, G-test 39.5 → H3 0.581, X4 not scored; H4b 0.695. **fails** | EER DiM 27.1-50.1 → 43.6-66.7, MorDIFF 27.5 → 40.1; X3 untested; H2 0.536. **fails** |
| **Published recipes, our re-implementation, SMDD only** | | | | |
| 9 | M1 Inception-MAD, Inception-v3 from scratch (5) ‡ | EER 53.6/53.6/27.5/24.9 → 71.5/72.2/46.3/42.1; MAD22 FM 6.4 → 39.0; H1 0.603. **fails** | EER G-test 37.5 → H3 0.555, X4 0.441; H4b 0.672. **fails** | UA8c EER 14.4 → 49.4; X3 untested; H2 0.534. **fails** |
| 10 | M2 MorphHRNet-style, HRNet-W48 from scratch (5) ‡ | EER 90.7/87.1/73.2/67.5 → 92.5/90.0/79.7/73.7 (inverted); MAD22 FM 51.6 → 73.8; H1 0.594. **fails** | EER G-test 38.2 → H3 0.591, X4 0.469; H4b 0.678. **fails** | UA8c 41.7 → 48.5; X3 untested; H2 0.532. **fails** |
| 11 | M3 MADation recipe, CLIP ViT-B/16 + LoRA (8) ‡ | EER 3.3/5.7/10.8/8.6 → 3.6/5.8/11.4/8.8; MAD22 FM 5.0 → 5.3; H1 0.750 (above). **works** | EER MIPGAN-I 7.0, G-test 35.6 → H3 0.448 (reversed), X4 0.458; H4b 0.847. **fails** | UA8c 12.6 → 12.1, MorDIFF 35.1 → 28.6; X3 untested; H2 0.483. **partly** |
| 12 | M3L MADation recipe, CLIP ViT-L/14 + LoRA (5) ‡ | EER 0.4/0.3/15.0/7.8 → 0.4/0.3/14.5/7.6; MAD22 FM 0.6 → 0.5; H1 0.810 (above). **works** | EER MIPGAN-I 0.8, G-test 37.6 → H3 0.401 (reversed), X4 0.442; H4b 0.923 (floor 0.912). **fails** | UA8c 17.7 → 16.1, MorDIFF 45.7 → 41.5; X3 untested; H2 0.474. **partly** |
| 13 | M4 SelfMAD-style, HRNet-W18 + self-blended fakes from SMDD genuine photos only (5) ‡ | EER 90.9/38.3/100/100 → 82.0/24.5/100/100 (inverted); MAD22 FM 99.8 → 0.8; H1 0.761 (above). **partly** | EER G-test 24.3 → H3 0.551, X4 0.517; H4b 0.403. **fails** | EER 100 in all 7 families (inverted) → UA8c 42.8; X3 untested; H2 0.475. **fails** |
| 14 | M5 PW-MAD, DenseNet-121 with pixel-wise labels (8) ‡ | EER 14.4/15.8/8.9/4.2 → 24.5/28.8/25.7/14.3; MAD22 FM 1.2 → 20.7; H1 0.547. **fails** | EER G-test 56.0 (inverted) → H3 0.564, X4 0.460; H4b 0.455. **fails** | UA8c 28.0 → 49.5; X3 untested; H2 0.491. **fails** |
| 15 | M6 OrthoMAD, ResNet-18 from scratch (5) ‡ | EER 61.3/81.4/66.8/59.8 → 67.7/85.8/74.6/69.3 (inverted); MAD22 FM 24.4 → 47.5; H1 0.653. **fails** | EER G-test 33.7 → H3 0.574, X4 0.469; H4b 0.647. **fails** | UA8c 36.8 → 48.2; X3 untested; H2 0.525. **fails** |
| 16 | M8 MixFaceNet-MAD recipe, MixFaceNet-S from scratch (5) ‡ | EER 66.5/57.4/46.9/44.8 → 75.2/70.1/63.6/61.7; MAD22 FM 27.6 → 65.7; H1 0.648. **fails** | EER G-test 37.3 → H3 0.560, X4 0.448; H4b 0.623. **fails** | UA8c 28.1 → 48.9; X3 untested; H2 0.533. **fails** |
| 17 | M8O MixFaceNet-MAD, official training code (5) ‡ | EER 85.1/78.4/55.8/54.1 → 88.5/84.1/66.4/65.2; MAD22 FM 30.8 → 70.3; H1 0.631. **fails** | EER MIPGAN-I 45.8, G-test 36.8 → H3 0.556, X4 0.453; H4b 0.630. **fails** | UA8c 36.3 → 49.0; X3 untested; H2 0.534. **fails** |

**Notes to the table.**

**[a] Regular, benchmark.**
- EER in % (thresholded). FRLL families in the order FaceMorpher / OpenCV / AMSL / WebMorph, each scored against the 204 FRLL genuine photos (102 persons). MAD22 FaceMorpher is scored against the 185 MAD22 genuine photos, which are byte copies of FRLL photos.
- Releases: one network, no seed spread, image-bootstrap 95% CIs in A36 RSX.
- Recipes: seed means; SDs are in `gather_regular.md` §2-3.
- The recipes' benchmark pool is labelled by A12.4 as "an eval-pipeline diagnostic, never a detection result".

**[b] Regular, controlled.**
- **E7 EER (thresholded).** The same genuine photos, shrunk (area averaging) to each family's median morph face size before alignment. Shrinking factors: FRLL FM 1.47x, OCV 1.56x, AMSL and WebMorph 1.80x, MAD22 FaceMorpher 3.30x.
- MAD22 OpenCV and Webmorph are left out of the table because E7 shrinks those photos by only ~1.0x, so it tests nothing there.
- E7 still leaves the alignment borders and file headers. Border fraction alone separates FRLL landmark morphs from E7 photos at AUC 1.00 (E07 `raw/data-shortcut.md`).
- **H1 AUC (threshold-free).** The clean Poisson set, `pp` variant (the A27 registration puts claims on `pp`): 598 pairs, both classes from the same source at the same size, with the same border and post-processing. The file-size floor is **0.681** (0.620 on `orig`).
- "Above / not above" is the A36 amendment 1 reader's label against the floors, with pair-clustered 90% CIs. It is exploratory and post-freeze. The SelfMAD own-crop `pp` value is a point estimate with no CI.

**[c] GAN, benchmark.**
- EER % on MAD22 MIPGAN-I (generator PNG vs camera JPEG) where a registered reader prints the arm value.
- G-test: held-out StyleGAN2 latent-average morphs of FEI face-database pairs vs FEI camera captures. For the recipes it is the mean of the neutral and smiling families.
- For M1, M2, M4, M5, M6 and M8 no reader prints a MIPGAN-I arm mean (see flag 2), so only the G-test is shown.
- The SelfMAD own-crop G-test is not logged.
- M8O MIPGAN-I 45.8 is the value with test-time augmentation in `rsx_read.md`; 44.9 without it is in `a36_a2.md`.

**[d] GAN, controlled** (all threshold-free AUC).
- **H3.** 423 StyleGAN3 two-person latent-average morphs against single-person renders of the same generator, `orig`, full pairs. Floors: bytes 0.526, eye geometry 0.560, combined covariates 0.607-0.617. Values below 0.5 mean the renders score as more morph-like. "Reversed" means the 95% pair CI lies below 0.5 (`a41_h3.md`).
- **X4.** The same morphs against renders matched to the morphs' latent spread, with a pair-clustered 95% CI in `a41g_x4.md`.
- **H4b.** StyleGAN v1 MIPGAN-I-style morphs against single-identity renders of the host. File-size floor **0.912**.

**[e] Diffusion, benchmark.**
- EER % on FRLL diffusion families against the original genuine photos.
- Releases are shown per family.
- Recipes show UA8c: the mean EER over the seven held-out diffusion families (six DiM variants plus MorDIFF), each capped at 50, with the t-based 95% half-width over seeds in `a36_a2.md`.
- The recipes' benchmark (orig) pool is the A12.4 eval-pipeline diagnostic.

**[f] Diffusion, controlled.**
- **E7 EER.** The same shrinking as [b], per diffusion family. Person-clustered 95% CIs for the releases are in `a41_eval.json` S2.
- **X3 AUC.** Published morphs against DiffAE reconstructions of the genuine photos (the "rec" pool). Listed in the order Greedy-DiM / MorDIFF unless a family is named. Releases only; the recipes were never scored on X3.
- **H2 AUC.** IP-Adapter-FaceID Stable Diffusion 1.5 embedding-midpoint morphs against single-identity renders of the same generator. Floors: bytes 0.522, eye geometry 0.518.
- Arc2Face (548 + 548 images, both generated) gives the same picture: every row is at 0.482-0.539 (`gather_diffusion.md` §3h).

**Verdict words.** These are this draft's descriptive labels. They are **not** A41 grades, and "partly" is not the dropped phrase "partly carried".

- **Regular**
  - **works:** under E7 the EER stays ≤ 10% on at least two FRLL landmark families, no family rises by more than ~3 points, and H1 `pp` is above its floor.
  - **fails:** neither condition holds (no two FRLL families at ≤ 10% under E7, and H1 `pp` not above floor).
  - **partly:** anything in between.
- **GAN**
  - **works:** both H3 and X4 are clearly above their floors.
  - **partly:** one of them is.
  - **fails:** neither is. Every row fails. In C3's terms this means no detection beyond generator output is shown. It does **not** mean that the detector is blind to two identities, because the test has little power for that.
- **Diffusion**
  - **works:** E7 keeps the benchmark error rate (within a few points and well below 50), and a same-generator control (X3, H2, Arc2Face) is clearly above its floor. No row works, because every row sits at 0.466-0.539 on H2 and Arc2Face.
  - **partly:** one of the two holds, on at least one family.
  - **fails:** neither holds.
- **untested:** no controlled number is logged. No cell of the table needs this verdict; single untested controls are marked inside the cells.

**Counts.**

| Morph type | works | partly | fails |
|---|---|---|---|
| Regular | 3 (FE ViT-L/14, M3, M3L) | 4 (SelfMAD release, ViT-B/16, ViT-L/14, M4) | 10 |
| GAN | 0 | 0 | 17 |
| Diffusion | 0 | 5 (ViT-B/16, ViT-L/14, FE ViT-L/14, M3, M3L) | 12 |

**Status of the numbers.**
- **Registered decision cells.** SelfMAD release, MAD22 FaceMorpher under E7 (A41 F4 (i), supported). MADation ViT-B/16 FRLL FaceMorpher under E7 (F4 (ii)). SelfMAD release Greedy-DiM and MorDIFF (C1: F1, F2, F3, grade "strong (final)"). ViT-B/16 MorDIFF (C2: F5, F6, F7, "descriptive row (final)"). ViT-L/14 Greedy-DiM as the negative control (F4 (iii)). FE ViT-L/14 as the X3 positive-control gate.
- **H3 and X4 on the ‡ rows** (C3, "strong (narrow)").
- **Registered labels without a grade.** The H1 labels (A36 amendment 1) and H4b (the A36 H-new-72 route, "neither").
- **Everything else is descriptive.** In particular, no landmark (regular) cell has a shortcut grade, and no registered shortcut rule was applied to the recipes.

## 3. Method by method

**SelfMAD release** (official HRNet-W18 checkpoint, one network, its own dlib crop and resize).
- **What it responds to.** In a test with no morphs at all, its score climbs with how much a genuine photo was shrunk. Shrunk copies against the same photos give AUC 0.584 at ~1.0x, 0.968 at 1.80x and 0.998 at 3.30x. At its own 5% false-alarm threshold it flags 95.1% of half-size genuine photos. The allowed cue wording is "bona fide processing history; cue not identified".
- **Regular.** FaceMorpher- and OpenCV-tool morphs stay detected against shrunk photos: FRLL FaceMorpher 4.8% [person 95% 1.95, 7.34]; MAD22 FaceMorpher 0.11% [0.00, 0.89], registered. The clean Poisson morphs score above the file-size floor (0.821). AMSL and FRLL WebMorph do not hold (33.3% and 51.9%).
- **GAN.** It separates StyleGAN3 renders from FRLL camera photos almost perfectly (AUC 1.000). Yet it ranks single-person renders above two-person morphs by the widest margin of any row (H3 0.353 [95% pair 0.326, 0.379]).
- **Diffusion (C1).** Against FRLL photos shrunk to the morphs' face size, it scores the genuine photos as more morph-like than Greedy-DiM morphs: 8.4% → 90.7% (+82.4 [77.3, 87.4]). It does the same on the raw files with its own crop (6.4% → 87.2%, descriptive). It also ranks DiffAE reconstructions (0.33 [0.28, 0.37]) and merely resized photos (0.09) above the published MorDIFF morphs.
- **Caveat.** Through our pipeline the same checkpoint shows the same pattern (H3 0.360; Greedy-DiM 29.4 → 89.1), so its crop is not the cause. Its released training code blends each photo with a resampled zoom of itself and never resamples the genuine partner. That is consistent with this behaviour but does not explain it.

**MADation release ViT-B/16** (official CLIP ViT-B/16 + LoRA weights, one network). CLIP is an image model pretrained on image-text pairs; LoRA is a small trained adapter on top of it.
- **What it responds to.** It reads "generator output versus camera photo" reliably. It scores StyleGAN3 single-person renders above FRLL, FFHQ (Flickr-Faces-HQ) and FEI photos at AUC 0.947 / 0.980 / 0.964. Its 9.9% G-test, the best of any published row, is a generator-versus-camera result.
- **Regular.** FaceMorpher and OpenCV morphs hold under E7 (4.4%). AMSL doubles (15.1 → 28.9). On the clean Poisson test it is above the file-size floor on `orig` (0.770) but not on `pp` (0.727). At its native threshold it would flag 71.9% of photos shrunk to MAD22 FaceMorpher's face size, yet the morphs still rank above them (5.94% [3.25, 10.62]).
- **Diffusion (C2, a descriptive row).** MorDIFF goes from 4.9% to 19.6% (+14.7 [10.3, 18.9]) in all five crops (+13.2 to +21.0). It also separates the published MorDIFF morphs from DiffAE reconstructions (0.85 [0.80, 0.89]), a registered refuter. Whether that is identity evidence or a file or frame property is open. Its DiM detection mostly collapses (DiM-A 20.6 → 56.4; X3 0.361).
- **Caveat.** One released network. C2 is about these weights only, not the MADation method, and its cue wording is "fine-detail softness".

**MADation release ViT-L/14** (official weights, one network; A41's negative control).
- **What it responds to.** It ignores photo shrinking: shrunk copies against originals give AUC 0.494 → 0.455. It does react to other processing: at its native threshold it flags 52.9% of JPEG-50 genuine photos.
- **Regular.** Benchmark numbers are unchanged under E7 (FaceMorpher and OpenCV 1.0%). It sits at the file-size floor on clean Poisson morphs (0.684 against 0.681).
- **GAN.** It is inverted on FRLL StyleGAN (52.4%) and the G-test (69.5%), and it ranks single-person StyleGAN3 renders above morphs (0.427).
- **Diffusion.** DiM detection is unchanged against shrunk photos (Greedy-DiM 9.8 → 9.8, Δ 0.00 [−3.15, 3.41]). But it stays below the cue floor against DiffAE reconstructions (0.749 against 0.993), and ranks same-person DiffAE "morphs" above Greedy-DiM morphs (0.386). Its +10.7 MorDIFF rise shows that the MorDIFF control pool is not specific.

**MADation baselines FE ViT-B/16 and FE ViT-L/14** (frozen CLIP encoder + trained head, one network each).
- **Where the pattern sits.** These two show that the "generator versus camera" pattern is largely in the pretrained features: renders against FRLL / FFHQ score 0.922 / 0.892 for FE ViT-B/16 (descriptive, one network each). Both are at chance on morph versus render (H3 0.514 / 0.505).
- **FE ViT-L/14** keeps its landmark numbers under E7 (+0.5 to +1.5) and beats the clean-test floor (0.745). On diffusion it moves little under E7 (+2 to +6). It separates morphs from reconstructions on DiM-A and MorDIFF (0.772, 0.742). As the registered positive control it failed on Greedy-DiM (0.636 ≤ 0.65), so X3 could not show that it is sensitive to identity mixing at all.
- **FE ViT-B/16** is weak everywhere and loses 6-13 points on landmark families and 21-29 on DiM under E7.

**MADation baselines FS ViT-B/16 and FS ViT-L/14** (vision transformer trained from scratch + head, one network each).
- They are weak on every morph type.
- On the clean Poisson test FS ViT-B/16 is below chance (0.422).
- Its moderate DiM numbers drop to near chance against shrunk photos (16-24% → 42-46%).
- FS ViT-L/14 sits at 28-49% EER with or without any control.

**MixFaceNet-MAD release** (official SMDD weights, one network).
- **Domain.** On our frames it is outside its input domain. Our MAD22-5 / FRLL-5 values are 41.7 / 76.5, against published 13.69 / 8.96. Its loader is verified: 0.45% EER on its own SMDD training files. So the miss comes from our frames or the genuine-photo source, and the two causes are not separated.
- **Regular.** It ranks FRLL genuine photos above FRLL landmark morphs, with or without control. It detects only MAD22 OpenCV and Webmorph (12-21%), where E7 changes nothing.
- **GAN and diffusion.** It is near chance on GAN morphs (H3 0.581, MIPGAN-I 47%). On diffusion it is weak natively (27-50%) and at 40-67% against shrunk photos.
- **Caveat.** This says nothing about the method on its own crops. Per the drop list, no sentence may tie its numbers to image size.

**M1 Inception-MAD** (our re-implementation, Inception-v3 from scratch, SMDD only, 5 seeds).
- **Reproduction.** Like the other CNN recipes here, it did not reproduce the published numbers (A12-BR equivalence test: falsified).
- **Rankings.** They follow which benchmark the morph file comes from. OpenCV-tool morphs from MAD22 score 4.0% and those from FRLL 72.2% under E7, although MAD22's 185 genuine photos are byte copies of FRLL photos.
- **Regular.** MAD22 FaceMorpher goes from 6.4% to 39.0% once the photos are shrunk. The clean test is below the file-size floor (0.603).
- **GAN and diffusion.** It flags StyleGAN3 renders against FRLL and FFHQ photos about as much as morphs, and sits at the eye-geometry floor on H3 (0.555). Its fair native diffusion numbers collapse to chance (UA8c 14.4 → 49.4).

**M2 MorphHRNet-style** (HRNet-W48 from scratch, 5 seeds).
- **Regular.** It ranks FRLL genuine photos above FRLL landmark morphs (67-91% EER). The inversion is not caused by the photo pool or JPEG compression (A12.4 H-new-B, falsified).
- **GAN.** It is weak even on the native GAN sets (G-test 38.2%). Its H3 value of 0.591 is the highest row, but it stays below the combined file-size + eye-geometry floor (0.607-0.617) and is gone on spread-matched renders (0.469). Single M2 networks reach a within-pair AUC of 0.66, so "no network" must not be written.
- **Diffusion.** Near chance (UA8c 41.7 → 48.5).

**M3 and M3L, the MADation recipe** (CLIP ViT-B/16 or ViT-L/14 + LoRA, SMDD only; 8 and 5 seeds).
- **Where the skill sits.** Mostly in the frozen CLIP features: a linear head alone on frozen CLIP ViT-B/16 gives UA8c 15.2%.
- **Regular.** They are the retrained rows that keep landmark detection on both tests. Their landmark EERs move by at most 0.6 under E7, and they score above the clean-test floor (0.750 [pair 90% 0.735, 0.765] and 0.810 [0.793, 0.826]). M3 flags 5.9% of half-size photos, against a native rate of 5.4%.
- **GAN.** They act as generator-output detectors: renders against FRLL / FFHQ / FEI photos give M3 0.951 / 0.956 / 0.967. They rank single-person StyleGAN3 renders above morphs (H3 0.448 and 0.401, reversed). M3L's H4b 0.923 is only +0.010 over the file-size floor (Bonferroni lower bound −0.031).
- **Diffusion.** Held-out diffusion detection is unchanged against shrunk photos (UA8c 12.6 → 12.1 and 17.7 → 16.1). They were never tested against DiffAE reconstructions, and they are at chance on same-generator renders (H2 0.483 and 0.474). M3's number is at its validation-selected checkpoint; the last checkpoint gives 25.4.

**M4 SelfMAD-style** (HRNet-W18, self-blended fakes built from SMDD genuine photos only, 5 seeds).
- **Regular.** It scores genuine studio photos as more morph-like than the benchmark morphs (EER 100% on AMSL, WebMorph and all seven diffusion families; 90.9% on FaceMorpher). Shrinking the photos makes them look genuine to it (MAD22 FaceMorpher 99.8% → 0.8%), the opposite direction from the SelfMAD release. On clean Poisson morphs it is above the file-size floor (0.761), so some landmark separation exists, but on the benchmarks the photos swamp it.
- **GAN.** It does not read generator output consistently. It scores FRLL and FFHQ photos above StyleGAN3 renders, and FEI photos below them. On morph versus render it is at chance (H3 0.551, X4 0.517).

**M5 PW-MAD** (DenseNet-121 with pixel-wise labels, 8 seeds).
- **Regular.** It is fair natively (WebMorph 4.2%, but with seed SD up to ±17 on other families). It loses 10-20 points on every landmark family once the photos are shrunk, and it is below the clean-test floor (0.547).
- **GAN.** It is inverted on the StyleGAN2 G-test (56.0%) and on StyleGAN v1 against camera photos (0.338).
- **Diffusion.** It goes from fair (UA8c 28.0) to chance, and is inverted per family (Greedy-DiM 33.6 → 83.3).

**M6 OrthoMAD** (ResNet-18 from scratch, 5 seeds).
- **Regular.** It is inverted on FRLL landmark families (60-81%), and the inversion is not a pool or JPEG effect (H-new-B, falsified). MAD22 FaceMorpher goes from 24.4% to 47.5% under E7.
- **GAN.** Whether StyleGAN3 renders look morph-like to it depends on the camera pool: 0.525 against FRLL, 0.913 against FFHQ. On morph versus render it is at the image-property floor (H3 0.574).
- **Diffusion.** Chance under E7 (UA8c 36.8 → 48.2).

**M8 and M8O MixFaceNet-MAD** (MixFaceNet-S from scratch: our port of the recipe, and the authors' official training code; 5 seeds each).
- **Reproduction.** Neither version reproduced the published numbers (the official-code reproduction was also falsified).
- **Regular.** Both are near chance or inverted on FRLL landmark families. MAD22 FaceMorpher collapses under E7 (+38.2 and +39.5), and both are below the clean-test floor (0.648, 0.631). M8O flags 26.7% of half-size genuine photos and 57.3% of the DiM shrunk-photo pool at its native 5% threshold.
- **GAN and diffusion.** At chance on both (H3 0.560 / 0.556; UA8c ~49).

**Across rows.**
- **Regular morphs.** Only CLIP-based rows keep landmark detection once the photo-processing difference is gone and on the clean test: the MADation recipe (M3, M3L) and the FE ViT-L/14 release. The SelfMAD release keeps FaceMorpher- and OpenCV-type morphs but loses AMSL and WebMorph. Every SMDD-trained CNN recipe and the MixFaceNet-MAD release fail.
- **GAN morphs.** No published detector we analysed ranks StyleGAN3 morphs above single-person StyleGAN3 renders by a useful margin, and several rank them the other way round (C3). Their good MIPGAN numbers come from sets that compare generator output with camera photos (C4).
- **Diffusion morphs.** The SelfMAD release reverses against shrunk photos (C1). The SMDD CNN recipes fall to chance or below. The CLIP rows hold against shrunk photos on DiM. No row scores two-person diffusion morphs above one-person renders of the same generator beyond chance (H2, Arc2Face: 0.466-0.539; descriptive).

## 4. What this does not show

- **It does not grade the methods.** The verdict words are descriptive labels for this draft. The only grades are CONCLUSIONS' C1 "strong (final)", C2 "descriptive row (final)", C3 "strong (narrow)", B ("meets its registered criterion") and C4 ("construction sentence"). The regular (landmark) column has no shortcut grade at all.
- **The release results are not about the methods.** Each release is one network. C1 and C2 are about those checkpoints, not about the SelfMAD or MADation methods. Never "published detectors rely on shortcuts", "for every method" or "MADation carries the shortcut".
- **Most results are on our frames, not the authors' pipelines.** Releases were scored on our 512-px eye-aligned frames; only the SelfMAD release was also scored with its own crop and on raw files. The MixFaceNet-MAD release is out of its input domain on our frames.
- **The recipes are re-implementations that mostly did not reproduce.** Most CNN recipes failed the reproduction check. Their benchmark pool is an eval-pipeline diagnostic (A12.4), and A12 numbers must not be set against published tables in the paper. The same architectures trained with our protocol and data (P × d1) are not competing methods. They are in `gather_regular.md` §5 and `gather_diffusion.md` §3e.
- **The data are narrow.**
  - FRLL and MAD22 share one pool of 204 or 185 genuine photos from 102 persons, so the families are not independent.
  - The clean Poisson set is CASIA-WebFace at 112 px.
  - GAN evidence is one generator per test: StyleGAN3 for H3 and X4, StyleGAN v1 for H4b.
  - Diffusion generator-matched evidence is DiffAE (X3, releases only) plus two other generators (H2, Arc2Face).
  - FFHQ-Morphs is left out of the verdicts. File size alone separates its DiffAE pool (1.000), and its own README calls it "unfit to be used for evaluation purposes".
- **It does not show which cue a network reads, or anything causal.**
  - Not for the SelfMAD release: "cue not identified". Never "resolution", "aliasing", "fine-detail loss", "interpolation trace" or "spectral cue".
  - Not for GANs: no storage-format cue was found.
  - Not for MixFaceNet-MAD: no image-size sentence.
- **It does not show that detectors are blind to identity.** H3 and X4 have little power against a two-identity signal by construction. X3's positive control failed (0.636 ≤ 0.65), so "assay sensitivity not shown". Never "does not separate", "no signal" or "no network" for C3.
- **Control-pool artefacts are not excluded.** A border or alignment artefact of our E7 pool is not formally excluded, because the border test could not be evaluated. The MorDIFF E7 pool is the weaker control: 47% of its difference from the native photos sits in the warped border, and it raises even the ViT-L/14 negative control by +10.7. E7 also leaves borders and headers on landmark families.
- **The reruns are not replications.** The crop test and the kernel ladder re-use the same persons and images.
- **It says nothing about MADMamba, W3, E10 or the FST.** CONCLUSIONS requires "MADMamba not evaluated on H3 (sealed)", the positive controls and our own networks' history with the same control to be printed beside every shortcut claim. That history is deliberately not repeated here, so take it from CONCLUSIONS when writing the paper.
- **It makes no generalisation claim.** Nothing here supports a "GAN or diffusion generalisation" sentence for any method.

## 5. Flags for the author

1. **C4 wording.** A41 DC-A records the FRLL StyleGAN morphs as JPEG (quality ~75, 1024 px), not PNG. So C4's "(PNG) ... (JPEG)" is literally true only for MAD22 MIPGAN-I/II. Your sign-off can only weaken the wording. A possible version: "generator output (PNG, or JPEG q≈75 for FRLL StyleGAN) with camera photos (JPEG)".
2. **Missing MIPGAN arm means.** No registered reader prints MIPGAN-I/II or FRLL StyleGAN arm means for M1, M2, M4, M5, M6 and M8. `gather_gan.md` computed them (marked †) from logged per-network values, but they are not used here. Re-derive them with a registered reader if the paper needs them.
3. **H1 primary variant.** For H1, A27 puts claims on `pp` while the A36 amendment 1 label uses `orig` as primary. Three releases change label between the two: ViT-B/16 (0.770 / 0.727), ViT-L/14 (0.718 / 0.684) and FE ViT-B/16 (0.681 / 0.681). This draft uses `pp`.
4. **Mixed CI levels.** Keep the level next to each number:
   - A41: person-clustered 95%.
   - A36: pair 90%.
   - A41 H3 bounds: one-sided 95%.
   - X4: pair 95%.
   - A36 RSX: image bootstrap 95%.
5. **Cells with no controlled number.**
   - X4 for the MixFaceNet-MAD release.
   - X3 for every recipe and for the FE ViT-B/16 and FS releases.
   - The SelfMAD own-crop G-test.
   - A raw-file E7 for any landmark family.

## 6. Sources

All paths are under `/home/narolski/mambamorph-code/`. The scratch gathers, which carry the per-number keys, SDs and CIs, are:
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_regular.md`
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_gan.md`
- `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/gather_diffusion.md`

**Grades and wording**
- `experiments/CONCLUSIONS.md`, §"What we can claim about shortcuts": C1, C2, C3, B, C4, the drop list and what is printed beside each claim.
- The same file, §"What this means for the paper": no A12 numbers against published tables, and no generalisation claim.

**Regular column**
- **SelfMAD release.** Native and E7 per family: `experiments/A32-RSX_resolution-shortcut/raw/rsx_read.json` `networks[].summary`. Half-size flag rates: `smadcvpr/results/RSX/rsx_read.md` "Mechanism".
- **MADation releases.** `experiments/A36_published-detector-shortcuts/raw/results/a36_read.json` `RSX.rows` (`fam`, `boot95`, `mech`, `e7_bpcer_at_native_t5`).
- **MixFaceNet-MAD release.** `a36_a2.json` `row_a36.RSX.fam`.
- **Recipes.** `experiments/A12-4_benchmark-followups/raw/a12_4_read_stage1.json` `arms["M1:r:d0"…"M8O:ocode:d0", "M4:r:d0b"].family_eer_orig / family_eer_e7`. The inversion test is in `a12_4_read_stage1.md` §(ii) (H-new-B).
- **Registered E7 cells and dose ladder.** `smadcvpr/results/A41/a41_eval.json`:
  - `S3.components.i`: SelfMAD MAD22 FaceMorpher 0.11 [0.00, 0.89].
  - `S3.positive_controls_beside`: ViT-B/16 MAD22 FaceMorpher 5.94 [3.25, 10.62].
  - `S7.rows`: dose ladder.
- **H1 clean Poisson AUC and labels.** `smadcvpr/results/A36/a36_a1.md` §(5); SelfMAD own `pp`: `a36_read_own.json`. Registration: `smadcvpr/PROTOCOL.md` A27 (~l.7715, "claims on pp", l.8649).
- **Border floor.** `experiments/E07_shortcut_controls/raw/data-shortcut.md` §2.
- **Construction attributes.** `smadcvpr/results/A41/a41_files.md` (DC-A).
- **OpenCV cross-benchmark check and reproduction tests.** `experiments/A12-BR_benchmark_recipes/README.md` (l.140-146).

**GAN column**
- **H3, H4b and renders against camera photos.** `smadcvpr/results/A36/a36_read_own.md` §(C) and `smadcvpr/results/A36/a36_a1.md` §(1). The MixFaceNet-MAD release is in `a36_a2.md`.
- **H3 bounds and reversed cells.** `smadcvpr/results/A41/a41_h3.md`.
- **X4.** `smadcvpr/results/A41/a41g_x4.md` / `.json` (H-new-146).
- **Native MIPGAN.**
  - Releases: `a41_eval.json` DC-8 (ViT-B/16, ViT-L/14) and `rsx_read.md` (SelfMAD).
  - FE/FS rows: `a36_read_own.md` "RSX".
  - M3 and M8O: `rsx_read.md`.
  - M3L: `a36_read_own.md` (B).
- **G-test.** `smadcvpr/results/A12/a12_5_read_stage1.md` (i) for the recipes and the SelfMAD our-pipeline row; `a36_read_own.md` "G-test" for the MADation releases; `a36_a2.md` for MixFaceNet-MAD. The G-test definition is at `smadcvpr/PROTOCOL.md` l.122-126.
- **Registrations.** `smadcvpr/PROTOCOL.md` A34 (H4b), A35 (H3).
- **MixFaceNet-MAD loader check.** `experiments/A39_batch-before-window-close/README.md` (S2).

**Diffusion column**
- **Release E7 per family.** `smadcvpr/results/A41/a41_eval.json` `S2.cells["<row> | dim/<family>"]`, `["<row> | mordiff/mordiff"]` (`native`, `e7`, `delta`, `delta_ci95`). Spot-checked for this draft: SelfMAD own Greedy-DiM 8.37 → 90.74 [77.32, 87.35]; ViT-B/16 MorDIFF 4.90 → 19.60 [10.32, 18.92]; ViT-L/14 Greedy-DiM Δ 0.00 [−3.15, 3.41].
- **Raw-file E7 and kernels.** `smadcvpr/results/A41/a41g_x7.md`, `a41g_s12.json` `detail.a`, `a41g2_s12k.json`.
- **X3 and its cue floors.** `smadcvpr/results/A41/a41g_x3.md` / `.json`.
- **Five crops.** `smadcvpr/results/A41/a41g_x14b.md`.
- **Border-matched X3.** `smadcvpr/results/A42/a42_border.md`.
- **FE/FS releases, H2, Arc2Face.** `smadcvpr/results/A36/a36_read_own.md` "RSX: MADation official" and §(C). The MixFaceNet-MAD release is in `smadcvpr/results/A36/a36_a2.md` "RSX, UA8c and MAD22" and "held-out comparisons".
- **Recipe per-family E7.** `smadcvpr/results/A12/a12_4_read_stage1.json` `arms[*].family_eer_orig / family_eer_e7`.
- **Recipe UA8c with t95.** `a36_a2.md` "UA8c per row".
- **Frozen-CLIP head.** `smadcvpr/results/A12/a12_4_read_stage2.json` `arms["M3:a124lp:d0"]`.
- **UA8c definition and the last-checkpoint value.** `experiments/A12-BR_benchmark_recipes/README.md` (l.52-53, 117, 138-139).
- **Diffusion flag rates.** `smadcvpr/results/RSX/rsx_read.md` "Mechanism".

**Not read or not used**
- No `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- League (L0-L2) and W3 rows that share `rsx_read.md` / `rsx_read.json` were not used.
