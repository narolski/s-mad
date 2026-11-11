# Shortcuts per method: what was found, and how far the proof goes

Prepared for Paweł Narolski, 2026-11-07, as a companion to `methods_table_final.md` in this folder. The rows, their order and their names are the same as in that table, and its numbers and verdict words are used unchanged. No new number was computed.

**Sources**
- Grades and allowed wording: the final section of `experiments/CONCLUSIONS.md`, "What we can claim about shortcuts".
- The four conditions N1–N4: PROTOCOL, A41 registration (2), and the A41 ledger README.
- A42: the PROTOCOL A42 blocks and `smadcvpr/results/A42/a42_border.md`.
- Recipe reproduction tests: `experiments/A12-BR_benchmark_recipes/README.md`.
- Per-row numbers: the three gathers in this folder.

**Scope**
- MADMamba, W3, E10 and the FST are not in this note: "MADMamba not evaluated on H3 (sealed)".
- No `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- The wording still awaits the author's sign-off (Sun 8 Nov 12:00). That sign-off can only drop or weaken it.

**Pending (no reading used, nothing predicted)**
- **A42 amendment 1**, the window test for the ViT-B/16 release on MorDIFF. It was scored and copied back (PROTOCOL "A42 copy-back", 18:07 CET). No results bullet and no post-result review are logged yet.
- **A43**, the MorDIFF two-by-two. It compares the published morphs with our same-pair morphs, and our two-identity morphs with our one-identity morphs. PROTOCOL had no registration block for it when this note was written.

## 1. What "prove beyond doubt" would take, and why nothing here reaches it

The program's registered bar is A41's. The highest grade a shortcut claim can earn is "meets registered criteria N1–N4", and all four conditions are required. A41 does not use the word "proven".
- **N1, reliance.** A control removes the construction difference while everything else stays fixed, and the result is destroyed. In numbers:
  - the benchmark error rate (EER) is at most 10%;
  - the lower end of the person-clustered 95% interval of its rise under the control is at least +10 points;
  - at least half of the separation is gone (d′ share ≥ 0.5).
- **N2, specificity.** The same control leaves real morph evidence detectable: MAD22 FaceMorpher morphs stay detected under it. It also does not move a detector that does not use the cue: the ViT-L/14 release on Greedy-DiM.
- **N3, validity in kind.** Genuine photos passed through the morphs' own generator family, without any morphing, behave like morphs for the detector. Here these are DiffAE reconstructions (X3). The test must also show that it could catch identity mixing at all: its positive-control detector, FE ViT-L/14, must score above 0.65.
- **N4, reproduction.** The published result reproduces on the raw files with the authors' own pipeline, so our frames did not create it (X7′).

**No claim meets this bar.** The closest is C1, the SelfMAD release on diffusion morphs:
- It meets N1, N2 and N4.
- It does not meet N3: the positive control reached only 0.636.
- A border or alignment artefact of our control photos is not formally excluded.
- So its grade is "strong", and the top grade cannot be reached.

**Even the top grade would not be "beyond doubt":**
- Each claim concerns one released network.
- It is scored on one pool of 204 FRLL photos of 102 persons, and the re-runs re-use the same persons and images.
- A41's rules were written after earlier estimates of the same questions had been seen. Those earlier registered tests said "neither".
- The cue itself is not identified.

"Beyond doubt" would need the top grade plus replication: another checkpoint or retrain, fresh data and another studio pool, all under rules fixed before the data are seen.

**Three statements that are easy to confuse.**
- **"A shortcut was shown."** This is about what carries one detector's result on one benchmark cell. A41's definition holds in numbers:
  1. a construction difference separates morphs from genuine photos;
  2. the same difference can be put into genuine photos without any morphing;
  3. removing it removes at least half of the separation, at the thresholds above.

  Only C1 reaches this.
- **"The benchmark number is inflated."** The benchmark figure is better than what the same detector achieves once a known construction difference is removed. So the number overstates performance. It does not say that the detector relies on that difference: less than half of the separation may go, or the control may also move a detector that does not use the cue.
  - A41's "inflated" label (tier 1) needs a native EER of at most 10% and a person-clustered rise clearly above +5 points. It was first printed for the ViT-B/16 release on MorDIFF. It was superseded by "descriptive row" when a registered refuter fired, so this note does not use the word for that row.
  - Every other rise under a control below is descriptive. That covers the FE, FS and MixFaceNet-MAD releases and all recipes: no registered rule was applied, and there are no person-clustered intervals.
- **"The detector fails a clean test."** This is an absence. On a set where both classes are made the same way and only the number of identities differs (H1, H3, X4, H4b, H2, Arc2Face), the detector does not rank morphs above non-morphs by a useful margin.
  - What it shows: the detector's benchmark number for that morph type is not evidence that it detects identity mixing.
  - What it does not show: a shortcut, because it says nothing about which cue the detector uses on the benchmark. Nor does it show that the detector is blind to identity, unless the test has power and a passing positive control. X4 sits near 0.5 by construction, H2 is low-potency, and X3's positive control failed.
  - The registered example is C3, "strong (narrow)", for GAN morphs.

Claims B and C4 describe the benchmarks, not the detectors:
- B: morph and genuine files differ in construction attributes.
- C4: the GAN sets compare generator output with camera photos.

They make a shortcut possible. They do not show that any detector uses one.

## 2. Table: the shortcut found for each method, against the registered bar

**Key**
- **E7.** Genuine photos shrunk to the morphs' median face size before the same alignment. Cells give EER in %, native → E7.
- **Brackets.** [ ] is a person-clustered 95% interval unless marked otherwise.
- **X3 AUC.** Published morphs against DiffAE reconstructions of the genuine photos. Below 0.5 means the reconstructions look more morph-like than the morphs.
- **"GAN analogue".** AUC of single-person StyleGAN3 renders against FRLL / FFHQ / FEI camera photos (A36 amendment 1, H-new-83, registered verdict "neither"; per-pool values descriptive).
  - It is the nearest GAN counterpart of N3: generator output without morphing, scored against camera photos.
  - It is not A41's N3 (A41: "X3 only"). The renders are not re-rendered genuine photos, and StyleGAN3 is not the MIPGAN generator.
- **"‡".** One of the 12 primary rows of C3.
- **"Met / not met".** Used only where A41 registered that condition for that cell. Everything else is a logged number with its status.

| # | Method (networks) | Shortcut / cue found (plain words; or "none shown") | Which morph type | N1 reliance (number) | N2 specificity (number) | N3 validity in kind (number) | N4 reproduction (number) | Status (registered grade if any) | Missing for beyond doubt / next test |
|---|---|---|---|---|---|---|---|---|---|
| **Official releases** | | | | | | | | | |
| 1 | SelfMAD release, HRNet-W18, its own dlib crop and resize on our frames (1) ‡ | **Diffusion:** genuine photos that were only shrunk to the morphs' face size score as more morph-like than published Greedy-DiM and MorDIFF morphs. Photos only resampled by DiffAE's aligner, and DiffAE reconstructions, also score above MorDIFF morphs. Cue word: "bona fide processing history; cue not identified". Its score rises with the shrinking alone: photo-only AUC 0.584 at ~1.0x → 0.998 at 3.30x ("dose response", registered secondary rule). **Regular:** none shown (AMSL 2.9 → 33.3, WebMorph 5.9 → 51.9; descriptive). **GAN:** none shown. | Diffusion: FRLL Greedy-DiM (main cell), MorDIFF (supporting) | Greedy-DiM 8.4 → 90.7, +82.4 [77.3, 87.4], d′ share 2.11. MorDIFF 2.5 → 61.3, +58.8 [54.2, 64.6], d′ share 1.19 (F1, F2 supported). **Met.** The ranking reverses, so "at least half" holds only in the letter. | MAD22 FaceMorpher against its own E7 pool 0.11 [0.00, 0.89]. ViT-L/14 release on Greedy-DiM Δ 0.00 [−3.15, 3.41] (F4 supported). **Met for Greedy-DiM.** On MorDIFF the same control moves ViT-L/14 by +10.74 [7.22, 14.19], so not shown there. | Reconstructions ranked above published morphs: Greedy-DiM 0.024 [0.011, 0.042] (floor-limited), MorDIFF 0.330 [0.284, 0.374]. Resampled-only photos 0.004 / 0.092 (F3 supported). The binding positive control failed: FE ViT-L/14 0.636 [0.579, 0.693] ≤ 0.65. **Not met** ("assay sensitivity not shown"). | Raw files with its own crop: Greedy-DiM 6.39 [3.35, 9.42] against a published 7.60. "Our frames do not change the native regime" (X7′, H-new-145). **Met** (5-point tolerance; FRLL-5 5.55 against 2.96). The reversal persists on the raw files, 6.4 → 87.2 (descriptive). | **C1 "strong (final)"**; top grade unreachable. Pool artefact not formally excluded (XA3c not evaluable). Earlier registered test (A32 H1): "neither". GAN: C3 "strong (narrow)". | N3 with a positive control that passes. A successor border/alignment test. A second checkpoint or a retrain over seeds (H-new-242). Fresh data and another studio pool (X8). |
| 2 | MADation release, CLIP ViT-B/16 + LoRA (1) ‡ | **None shown.** Diffusion: its MorDIFF EER rises against shrunk photos (cue word "fine-detail softness"). But it separates the published MorDIFF morphs from DiffAE reconstructions, a registered refuter: "Identity evidence or a file/frame property: open." Regular, GAN: none shown. | Diffusion: MorDIFF | 4.9 → 19.6, +14.7 [10.3, 18.9]; d′ share 0.463 < 0.5. Tier 2 not reached (p10 0.0170 > 0.00833). Same rise in all five crops (+13.2 to +21.0). **Not met.** | FRLL FaceMorpher under E7 4.42 [2.12, 6.93] (F4 (ii) supported). But the MorDIFF control moves the ViT-L/14 release by +10.74 [7.22, 14.19]. **Not shown for MorDIFF.** | **Refuted:** MorDIFF morphs vs reconstructions 0.847 [0.803, 0.891] (F7's kill fired). With border area matched: 0.844 [0.787, 0.895] (A42, post hoc). DiM-A 0.361 the other way (descriptive). GAN analogue 0.947 / 0.980 / 0.964. | A41's N4 for C2 is the five-crop check (F6 supported), run on our frames. No raw-file run with MADation's pipeline. On our frames MorDIFF 4.9 against a published 1.1. | **C2 "descriptive row (final)"** (a registered refuter fired). Earlier registered test (A36 H-new-75): "neither". GAN: C3 "strong (narrow)". H1 `orig` "above" (registered label, no grade). | **A42 amendment 1 window test: pending.** **A43 MorDIFF two-by-two: pending.** Then a MorDIFF fidelity check and a fresh-data replication (H-new-234). |
| 3 | MADation release, CLIP ViT-L/14 + LoRA (1) ‡ | **None shown.** It is A41's negative control: shrinking photos does not move it (photo-only AUC 0.494 → 0.455, "none"). It does react to other processing: 52.9% of JPEG-50 genuine photos flagged at its native threshold (descriptive). | — | Greedy-DiM 9.8 → 9.8, Δ 0.00 [−3.15, 3.41]. MorDIFF 28.9 → 39.7, +10.74 [7.22, 14.19], but native above 10, so not a decision cell. | It is C1's N2 control (F4 (iii) supported). | Greedy-DiM vs reconstructions 0.749 [0.696, 0.802]. Floor-limited (simple image properties alone 0.993), so uninformative. Same-person DiffAE "morphs" score above Greedy-DiM morphs (0.386, descriptive). GAN analogue 0.904 / 0.808 / 0.924. | Our frames only. MorDIFF 28.9 against 19.3: not reproduced. MIPGAN-I 11.9 against 20.32: not reproduced. MIPGAN-II 9.9 against 9.06: reproduced. | F4 (iii) supported (as control). GAN: C3 "strong (narrow)". H1 `orig` "above" (registered label). | Nothing to prove for a shortcut. Its MorDIFF rise is untested (native above 10). |
| 4 | MADation baseline FE ViT-B/16, frozen CLIP + head (1) | **None shown.** Descriptive: its numbers fall under E7 (FRLL landmark 16.7–26.0 → 22.6–38.7; DiM 21.0–47.0 → 41.6–73.6). | — | No person interval and no rule. Most native EERs are above 10, outside A41's definition. MAD22 FaceMorpher 1.0 → 7.2. | not tested | X3 not run. GAN analogue 0.922 / 0.892 / 0.656. Registered "CLIP carries the render cue" (H-new-84): "neither". | Our frames only: MorDIFF 39.7 against 17.86, not reproduced. | descriptive only (outside C3) | E7 cells with person intervals under a registered rule; X3; a raw-file run. |
| 5 | MADation baseline FE ViT-L/14, frozen CLIP + head (1) | **None shown.** It barely moves under E7: landmark +0.5 to +1.5; Greedy-DiM-S holds. | — | Greedy-DiM-S 11.8 → 13.8, +1.98 [0.25, 4.72] (descriptive; native above 10). | not tested | MorDIFF vs reconstructions 0.742 [0.689, 0.792], DiM-A 0.772 (descriptive). As the registered X3 positive control on Greedy-DiM: 0.636 [0.579, 0.693] ≤ 0.65, gate failed. GAN analogue 0.887 / 0.903 / 0.861. | Our frames only: MorDIFF 34.8 against 22.85, not reproduced. | descriptive only. Its failed gate is what blocks N3 for C1. | For C1, a positive-control detector that clears 0.65 on a same-generator test. |
| 6 | MADation baseline FS ViT-B/16, from scratch + head (1) | **None shown.** Weak natively. Its moderate DiM numbers go to near chance against shrunk photos (16.1–24.0 → 41.6–45.6; descriptive). | — | No person interval. DiM native 16–24, above A41's 10% entry bar. FRLL OpenCV 3.9 → 5.4 holds. | not tested | X3 not run. GAN analogue 0.877 / 0.509 / 0.569. | Our frames: MorDIFF 67.6 against 28.14, not reproduced. | descriptive only | Nothing to prove: no native result at or below 10% falls under the control. |
| 7 | MADation baseline FS ViT-L/14, from scratch + head (1) | **None shown.** Weak natively everywhere (27.6–49.0% with or without a control). G-test inverted (67.4). | — | — (no native cell at or below 10%) | not tested | X3 not run. GAN analogue 0.594 / 0.611 / 0.465. | not logged in this note's sources | descriptive only | Nothing to prove. |
| 8 | MixFaceNet-MAD, the official release, on our frames (loader checked on its own training files) (1) | **None shown.** Out of its input domain on our frames. It ranks FRLL genuine photos above FRLL landmark morphs with or without the control. No sentence may tie its numbers to image size (drop list). | — | — (FRLL landmark families inverted natively, 75.5–98.0) | not tested | X3 not run. GAN analogue 0.588 / 0.875 / 0.651. | Not reproduced on our frames: MAD22-5 / FRLL-5 41.7 / 76.5 against 13.69 / 8.96. The loader is verified (0.45% on its own SMDD training files), so the cause is our frames or the genuine-photo source; the two are not separated. | descriptive only (outside C3; X4 not scored) | Scoring on its own crops and raw files before any reading. |
| **Published recipes, our re-implementation, SMDD only** | | | | | | | | | |
| 9 | M1 Inception-MAD, Inception-v3 from scratch (5) ‡ | **No registered shortcut.** Descriptive: its rankings follow the benchmark's morph files. Against byte-copy genuine photos, OpenCV-tool morphs score 3.3% from MAD22's 1351-px files and 53.6% from FRLL's 431-px files. Its fair results collapse once the photos are shrunk. GAN: none shown. | Regular (MAD22 FaceMorpher) and diffusion (DiM); descriptive | Seed means; no person interval, no d′ share. MAD22 FaceMorpher 6.4 → 39.0. Greedy-DiM 9.0 → 60.7. UA8c 14.4 → 49.4 (uncapped 63.0). | not tested | X3 not run. GAN analogue 0.969 / 0.977 / 0.644 (morphs vs FRLL 0.990). | Re-implementation, not the authors' pipeline. Reproduction test (TOST): falsified. | descriptive only (no registered shortcut rule applied to recipes). GAN: C3 "strong (narrow)". H1 `orig` "not above" (registered label). | A registered E7 rule with person intervals over its networks, a negative control and X3. A re-implementation that reproduces. |
| 10 | M2 MorphHRNet-style, HRNet-W48 from scratch (5) ‡ | **None shown.** Inverted natively on FRLL landmark families (67.5–90.7%). Degrading both classes does not remove the inversion (H-new-B falsified). | — | — (no FRLL landmark, MAD22 FaceMorpher or diffusion cell at or below 10% natively) | not tested | X3 not run. GAN analogue 0.440 / 0.886 / 0.587. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 "strong (narrow)"; it is the highest H3 row (0.591 [pair 90% 0.572, 0.610]), still below the combined floor; single networks reach a within-pair θ of 0.66. H1 "not above". | Nothing to prove for a shortcut: no good benchmark result to carry. |
| 11 | M3 MADation recipe, CLIP ViT-B/16 + LoRA (8) ‡ | **None shown.** Regular, diffusion: it holds. GAN: its MIPGAN-I EER (7.0%) is measured on generator output against camera photos (C4). On the clean test it ranks single-person renders above morphs (H3 0.448). | GAN (descriptive) | Regular and diffusion: no reliance on shrinking. Landmark moves ≤ 0.6; MAD22 FaceMorpher 5.0 → 5.3; UA8c 12.6 → 12.1 (seed means). GAN: no control on the benchmark cell. | Flags 5.9% of half-size photos at its native threshold, against 5.4% native (descriptive). | X3 not run. GAN analogue 0.951 / 0.956 / 0.967. | Re-implementation. MAD22 reproduced on the mean only (MIPGAN-I 7.0 against 33.37). FRLL inconclusive (+2.17 [0.86, 3.47], margin 1.73). | GAN: C3 "strong (narrow)" (absence). H1 `orig` "above" (registered label). Otherwise descriptive. | GAN: X6 (the causal C4 test); a same-generator clean set with a passing positive control. X3 for the recipes. |
| 12 | M3L MADation recipe, CLIP ViT-L/14 + LoRA (5) ‡ | **None shown.** Regular, diffusion: it holds; MorDIFF stays weak (45.7 → 41.5). GAN: MIPGAN-I 0.8% is synthetic vs camera. H3 0.401 (reversed). H4b 0.923, only +0.010 over the file-size floor of 0.912 (Bonferroni lower bound −0.031). | GAN (descriptive) | Landmark ≤ 0.6 change (FaceMorpher 0.4 → 0.4; MAD22 FaceMorpher 0.6 → 0.5). UA8c 17.7 → 16.1. | not tested | X3 not run. GAN analogue 0.934 / 0.940 / 0.957. | Re-implementation. MAD22 better than published (TOST). | GAN: C3 "strong (narrow)". H1 `orig` "above". Otherwise descriptive. | As M3. |
| 13 | M4 SelfMAD-style, HRNet-W18 + self-blended fakes from SMDD genuine photos only (5) ‡ | **None shown.** Inverted on the benchmarks: 100% EER on AMSL, WebMorph and all seven diffusion families, 90.9% on FaceMorpher. Shrinking makes photos look genuine to it (MAD22 FaceMorpher 99.8 → 0.8), the opposite direction from the SelfMAD release. Above the floor on the clean landmark set (H1 0.761). | — | — (no native cell at or below 10%; the control improves it) | not tested | X3 not run. GAN analogue 0.314 / 0.394 / 0.999. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 "strong (narrow)". H1 `orig` "above". | Nothing to prove for a shortcut. Its opposite-direction response is descriptive. |
| 14 | M5 PW-MAD, DenseNet-121 with pixel-wise labels (8) ‡ | **No registered shortcut.** Descriptive: fair native results fall once the photos are shrunk. MAD22 OpenCV and Webmorph, shrunk only ~1.0x, do not change. GAN: none shown. | Regular and diffusion (descriptive) | Seed means, no person interval; seed SD up to ±17 on some families. WebMorph 4.2 → 14.3; AMSL 8.9 → 25.7; MAD22 FaceMorpher 1.2 → 20.7; UA8c 28.0 → 49.5 (uncapped 72.3). | not tested (the ~1.0x families' stability is a no-dose check, descriptive) | X3 not run. GAN analogue 0.881 / 0.845 / 0.801. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 "strong (narrow)". H1 `orig` "not above". | As M1. |
| 15 | M6 OrthoMAD, ResNet-18 from scratch (5) ‡ | **None shown.** Inverted natively on FRLL landmark families (59.8–81.4%), and not removed by degrading both classes (H-new-B falsified). MAD22 FaceMorpher 24.4 → 47.5 (descriptive). | — | — (no native cell at or below 10%) | not tested | X3 not run. GAN analogue 0.525 / 0.913 / 0.572. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 "strong (narrow)". H1 `orig` "not above". | Nothing to prove. |
| 16 | M8 MixFaceNet-MAD recipe, MixFaceNet-S from scratch (5) ‡ | **None shown.** Weak or inverted natively (FRLL FaceMorpher and OpenCV inverted). MAD22 FaceMorpher 27.6 → 65.7 under E7 (descriptive). | — | — (no native cell at or below 10%) | not tested | X3 not run. GAN analogue 0.763 / 0.963 / 0.662. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 "strong (narrow)". H1 `orig` "not above". | Nothing to prove. |
| 17 | M8O MixFaceNet-MAD, official training code (5) ‡ | **None shown.** Inverted natively on all four FRLL landmark families. At its native 5% threshold it flags 26.7% of half-size genuine photos and 57.3% of the DiM E7 photo pool (descriptive): shrinking alone moves photos toward "morph" for it. But it has no good native result for that to carry. | — | — (no native cell at or below 10%) | not tested | X3 not run. GAN analogue 0.697 / 0.954 / 0.629. | Official-code reproduction (O-Repro): falsified. | descriptive only. GAN: C3 "strong (narrow)". H1 `orig` "not above". | Nothing to prove. |

**Notes to the table**
- **Confidence-interval levels.** Person-clustered 95% for the A41 cells (S2, S3, DC-8, X3, X7′). Pair 90% for the A36 H1 and H3 values. Seed means for the recipes.
- **H1 labels.** Registered for the 11 primary rows (M1–M8O and the ViT-B/16 and ViT-L/14 releases), with no grade and set post-freeze. The SelfMAD own-crop H1 (`orig` 0.872) is a point estimate, counted "above" only in A39's sensitivity read.
- **No landmark (regular) cell has a shortcut grade.** E7 leaves the alignment borders in place, and border fraction alone separates several evaluation families almost perfectly (AUC 0.99–1.00; E07 README). So E7 is a weaker control on landmark morphs than on diffusion morphs.
- **Recipes.** No registered shortcut rule was applied to them. A12.4 calls their benchmark pool "an eval-pipeline diagnostic, never a detection result".
- **Printed beside every claim in the paper** (CONCLUSIONS):
  - the positive controls: the X3 gate failed (0.636 ≤ 0.65), and the ViT-L/14 release is unchanged on Greedy-DiM (Δ 0.00 [−3.15, 3.41]);
  - our own networks' history with the same shortcut (take it from CONCLUSIONS);
  - "MADMamba not evaluated on H3 (sealed)".

## 3. Method by method: what shortcut, how we know, how sure

**1. SelfMAD release.**
- *What:* on diffusion morphs, it treats genuine photos that were only shrunk to the morphs' face size as more morph-like than real Greedy-DiM and MorDIFF morphs. Cue: "bona fide processing history; cue not identified".
- *How we know:*
  - Shrinking alone takes its Greedy-DiM EER from 8.4% to 90.7% (+82.4 [77.3, 87.4]).
  - The same control leaves MAD22 FaceMorpher morphs detected (0.11%) and leaves the ViT-L/14 release unchanged (Δ 0.00).
  - Its published number reproduces on the raw files with its own crop (6.4% against 7.6%), and there the reversal persists (6.4% → 87.2%, descriptive).
- *How sure:* this is C1, graded "strong (final)", the highest grade any shortcut claim reached here, but not the top grade.
  - The reconstruction test's positive control failed (0.636 ≤ 0.65).
  - A border or alignment artefact of our control photos is not formally excluded.
  - It is one checkpoint on 204 photos of 102 persons, the earlier registered test said "neither", and it says nothing about the SelfMAD method.

**2. MADation release ViT-B/16.**
- *What:* no shortcut is shown. On MorDIFF its EER rises against shrunk photos (cue word "fine-detail softness"), but our rules do not let us call this a shortcut.
- *How we know:*
  - The rise, 4.9% → 19.6% (+14.7 [10.3, 18.9]), appears in all five crops.
  - It removes less than half of the separation (d′ share 0.46), and the same control also moves the ViT-L/14 release (+10.7).
  - The release separates the published MorDIFF morphs from DiffAE reconstructions (0.85 [0.80, 0.89]), a registered refuter.
- *How sure:* this is C2, a "descriptive row (final)": "Identity evidence or a file/frame property: open." A42 amendment 1 and A43, which bear directly on this question, are pending.

**3. MADation release ViT-L/14.**
- *What:* none shown. It is the detector that ignores shrinking, used as the negative control.
- *How we know:* its Greedy-DiM EER is unchanged under the control (9.8 → 9.8, Δ 0.00 [−3.15, 3.41]), and shrunk photos do not look more morph-like to it (0.494 → 0.455). It does react to JPEG-50 photos (52.9% flagged).
- *How sure:* it is registered as a control component (F4 (iii) supported), not as a claim about the detector. On GAN morphs it fails the clean test (H3 0.427, reversed; C3).

**4. FE ViT-B/16.**
- *What:* none shown.
- *How we know:* its numbers fall under E7 on landmark and DiM morphs, but most of them start above 10%. No registered rule or person interval was applied, and X3 was not run.
- *How sure:* descriptive only, one network.

**5. FE ViT-L/14.**
- *What:* none shown.
- *How we know:* it barely moves under E7 (Greedy-DiM-S +1.98 [0.25, 4.72]), and it separates published MorDIFF morphs from reconstructions (0.742 [0.689, 0.792]).
- *How sure:* descriptive. As the registered positive control on Greedy-DiM it reached only 0.636 ≤ 0.65. That failure is why no reconstruction result in this program counts as N3.

**6. FS ViT-B/16.**
- *What:* none shown.
- *How we know:* it is weak natively. Its DiM numbers (16–24%) go to 42–46% against shrunk photos, but they start above A41's 10% entry bar.
- *How sure:* descriptive only, one network.

**7. FS ViT-L/14.**
- *What:* none shown.
- *How we know:* it sits at 27.6–49.0% with or without the control, so there is no good result for a cue to carry.
- *How sure:* descriptive only.

**8. MixFaceNet-MAD release.**
- *What:* none shown.
- *How we know:* on our frames it is out of its input domain (41.7 / 76.5 against the published 13.69 / 8.96). Its loader is verified on its own training files (0.45%), so the cause is our frames or the genuine-photo source, and these are not separated.
- *How sure:* descriptive only. No sentence may tie its numbers to image size.

**9. M1 Inception-MAD.**
- *What:* no registered shortcut. Descriptively, its rankings follow the benchmark's morph files, and its fair results collapse once the photos are shrunk.
- *How we know:* OpenCV-tool morphs score 3.3% from MAD22's 1351-px files and 53.6% from FRLL's 431-px files. Under E7, MAD22 FaceMorpher goes 6.4% → 39.0% and UA8c 14.4 → 49.4.
- *How sure:* descriptive only. These are seed means of a re-implementation that did not reproduce, with no person interval, no negative control and no X3.

**10. M2 MorphHRNet-style.**
- *What:* none shown.
- *How we know:* it is inverted natively on FRLL landmark morphs (67–91%), and degrading both classes does not remove that, so there is no good result to carry.
- *How sure:* descriptive. On GAN morphs its 0.591 is the best H3 row and still below the combined file-size and eye-geometry floor (C3).

**11. M3 MADation recipe ViT-B/16.**
- *What:* none shown. On regular and diffusion morphs it holds.
- *How we know:* on GAN morphs:
  - its 7.0% MIPGAN-I EER compares generator output with camera photos;
  - it scores single-person renders above camera photos (0.951 / 0.956 / 0.967);
  - with both classes from the generator, it ranks renders above morphs (H3 0.448).
- *How sure:* the GAN absence is C3, "strong (narrow)". The renders-vs-camera numbers are descriptive, and no causal GAN test has run (X6).
  - Allowed: "its GAN benchmark number is not evidence of morph detection".
  - Not allowed: "it uses a GAN shortcut".

**12. M3L MADation recipe ViT-L/14.**
- *What:* none shown; the pattern is the same as M3.
- *How we know:* MIPGAN-I is 0.8% on synthetic vs camera, H3 is 0.401 (reversed), and H4b gives only what file size gives (0.923 against 0.912).
- *How sure:* C3 "strong (narrow)" for the absence; the rest is descriptive.

**13. M4 SelfMAD-style.**
- *What:* none shown.
- *How we know:* it is inverted on the benchmarks. Shrinking makes photos look genuine to it (MAD22 FaceMorpher 99.8 → 0.8), the opposite of the SelfMAD release. It is above the floor on the clean landmark set (H1 0.761).
- *How sure:* descriptive only.

**14. M5 PW-MAD.**
- *What:* no registered shortcut. Descriptively, its fair native results fall once the photos are shrunk.
- *How we know:* WebMorph goes 4.2 → 14.3, MAD22 FaceMorpher 1.2 → 20.7 and UA8c 28.0 → 49.5, while the families shrunk only ~1.0x do not change.
- *How sure:* descriptive only. These are seed means with seed SD up to ±17, from a re-implementation that did not reproduce.

**15. M6 OrthoMAD.**
- *What:* none shown.
- *How we know:* it is inverted natively on FRLL landmark morphs (59.8–81.4%), and degrading both classes does not remove that.
- *How sure:* descriptive only.

**16. M8 MixFaceNet-MAD recipe.**
- *What:* none shown.
- *How we know:* it is weak or inverted natively. Its MAD22 FaceMorpher fall (27.6 → 65.7) starts above 10%.
- *How sure:* descriptive only.

**17. M8O MixFaceNet-MAD, official code.**
- *What:* none shown.
- *How we know:* it is inverted natively on all four FRLL landmark families. Shrinking alone pushes genuine photos toward "morph" for it (26.7% of half-size photos flagged at its native threshold), but there is no good native result for that to carry.
- *How sure:* descriptive only. The official-code reproduction was falsified.

**Across rows.**
- Exactly one shortcut is shown: C1, the SelfMAD release on diffusion morphs, graded "strong".
- Everything else falls into one of two groups:
  - a descriptive move under a control, with no registered rule;
  - an absence on a clean test: C3 for GAN morphs, and the H1 labels for landmark morphs.
- Never write "published detectors rely on shortcuts", "for every method" or "MADation carries the shortcut".

## 4. What would make it beyond doubt (cheapest decisive additions per claim)

A41's grades are final. Nothing below can change C1, C2 or C3. Each item can only change an explanation sentence, or support a new claim registered separately before its data are seen.

**C1 (SelfMAD release, diffusion morphs)**
1. **N3 with a working positive control.** This is the one registered condition still missing. It needs a same-generator test whose positive-control detector clears its bar. On X3, FE ViT-L/14 reached only 0.636 ≤ 0.65, where simple image properties alone give 0.993. This note's sources name no scheduled item for it.
2. **Exclude the control-pool artefact.**
   - A successor border test, with its cut set relative to the untrained-network baseline (A41's calibration note).
   - Path attribution (H-new-261, about 0.05 GPU-h, after the window).
   - The best-aligned-third check (H-new-260, zero GPU, proposed) can add a sentence. It cannot remove the qualifier.
3. **A second checkpoint, or a retrain over seeds** (after the window). This is the SelfMAD retrain whose self-morphs use an integer shift instead of an interpolated zoom (H-new-242; 2 seeds per arm, 40–80 GPU-h). It would turn one checkpoint into several networks and test the mechanism note, which is "consistent with" C1 and does not explain it.
4. **Fresh data and another studio pool (X8)** (after the window). Every C1 number sits on the same 204 FRLL photos of 102 persons.

**C2 (ViT-B/16 release, MorDIFF)**
1. **A42 amendment 1, the window test** (H-new-240 (b), H-new-255): pending. It can add a C2 sentence only, and the zoom confound stays.
2. **A43, the MorDIFF two-by-two:** pending.
   - It compares the published morphs with our same-pair morphs (the file-construction cue).
   - It also compares our two-identity morphs with our one-identity morphs (identity evidence).
   - It is the only logged test that separates identity evidence from the morphs' pipeline for C2.
3. **Zero-GPU matching checks** (H-new-257, H-new-258; proposed, not registered): is the border slope a property of the control photos, and does matching on border area and on file size per content pixel remove the separation?
4. **After the window:**
   - a fresh-data replication of the ViT-B/16 rise (H-new-234);
   - a same-scale window that keeps the zero-fill;
   - another studio pool (X8).

**C3 (GAN morphs, absence)**
1. **A clean set with power against a two-identity signal and a positive control that passes.** X4 sits near 0.5 by construction, and H3's classes differ in latent spread.
2. **Other generators.** C3 covers StyleGAN3 only.
3. **X6, the causal test of C4** (3–5 H100-h or 8–16 GB10-h, after the window). It is the only planned item that could turn "these sets compare generator output with camera photos" into a statement about what a detector uses on MIPGAN-I/II.

**Regular (landmark) morphs (no grade yet)**
1. **A registered landmark rule with a border-matched control.** E7 leaves the alignment borders in place. It also needs person-clustered intervals for the descriptive falls: SelfMAD AMSL and WebMorph, and the recipes' collapses (M1, M5, M8, M8O).
2. **Per-network registered rules for the recipes, with a negative control.** None has been applied so far.

**B and C4 (benchmark construction)**
- Hash the 15,518 enumerated files. They were listed, not hashed; a hash-only manifest is proposed.
- C4 stays a construction sentence until a row reads a storage-format cue (none did, H-new-142) or X6 runs.
