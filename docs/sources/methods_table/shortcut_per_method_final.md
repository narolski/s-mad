# Shortcuts per method: what was found, and how far the evidence goes

Prepared for Paweł Narolski, 2026-11-07 (sources as of 18:47 CET), as a companion to `methods_table_final.md` in this folder. The rows, their order and their names are the same as in that table, and its numbers and verdict words are used unchanged. Two checkers' corrections are applied. A few values were re-read from logged outputs (`a41_eval.json` S2 for the ViT-B/16 release's DiM-C and Greedy-DiM-S cells; `a41g_x7.md`; the MAD22 OpenCV recipe cells in `a12_4_read_stage1.json`; A12-BR README l.140–147). No new number was computed.

**Sources**
- Grades and allowed wording: `experiments/CONCLUSIONS.md`, the section "What we can claim about shortcuts" (marked Final), l.164 onward. It is not the last section of the file.
- The four conditions N1–N4: PROTOCOL, A41 registration (2), (3) and (9), and the A41 ledger README.
- A42: the PROTOCOL A42 blocks, including the amendment 1 results (l.17322) and post-result review (l.17398), and the author's answer on question (i); `smadcvpr/results/A42/a42_border.md`; CONCLUSIONS "Beside C2".
- Recipe reproduction tests: `experiments/A12-BR_benchmark_recipes/README.md`.
- Per-row numbers: the three gathers in this folder.

**Scope**
- MADMamba, W3, E10 and the FST are not in this note: "MADMamba not evaluated on H3 (sealed)".
- No `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- The wording still awaits the author's sign-off (Sun 8 Nov 12:00). That sign-off can only drop or weaken it.

**A42 amendment 1 and A43: status**
- **A42 amendment 1** (the window test; the ViT-B/16 release; MorDIFF).
  - The window was read at 18:08 CET. Its results bullet and post-result review were logged at 18:30 CET (PROTOCOL l.17322 and l.17398, commit d03dfe7), after this note's first sources were read.
  - The author answered question (i) at about 18:35 CET (logged 18:39 CET, 756dfad): his crop-slicing approval covers the central 256-px window. Under amendment 1's timing rule this changes no label.
  - A42 is post hoc and descriptive. It changes no A41 verdict, kill or grade.
  - This note uses only CONCLUSIONS' "Beside C2" sentence (quoted in §4, C2 item 1). It does not use the registered H-new-240 (b) label "held": the post-result review says "held" means the separation does not survive the central window, not that the border explains it.
- **A43 (the MorDIFF two-by-two, H-new-241; staged, not registered): pending.**
  - It compares the published MorDIFF morphs with our same-pair morphs, and our two-identity morphs with our one-identity morphs.
  - It is staged on branch a43 (code 8a6219e, ledger 58c5b82, 18:30 CET). No image has been generated and nothing has been scored. Nothing is predicted here.
  - **Name clash.** Main PROTOCOL (l.17047, l.17469) and CONCLUSIONS (l.283) use "A43" for a different item: one zero-GPU registration of H-new-257, 258, 260 and 264–266. CONCLUSIONS lists the same-pair morphs (H-new-241) as "after the deadline".

## 1. What the registered bar requires, and why no claim meets it

The program's registered bar is A41's. The top grade a shortcut claim can earn is "meets registered criteria N1–N4", and all four conditions are required. A grade is the label A41's registered rules assign, not a level of certainty (CONCLUSIONS).

- **N1, reliance.** A control removes the construction difference while everything else stays fixed, and at least half of the separation goes.
  - In numbers (CONCLUSIONS' summary): the benchmark error rate (EER) is at most 10%; the person-clustered lower bound of its rise under the control is at least +10 points; at least half of the separation is gone (d′ share ≥ 0.5).
  - Operationally (F1, F2, F5): the rise is decided by a one-sided person-clustered test that it exceeds +10, at its Holm level (p10 ≤ level), not by the printed two-sided interval. C2's printed interval starts at 10.3 (one-sided lower bound 10.97), but p10 0.0170 > 0.00833, so tier 2 was not reached.
- **N2, specificity (F4).** The same control leaves real morph evidence detectable: MAD22 FaceMorpher morphs stay detected under it. It also does not move a detector that ignores downsampling: the ViT-L/14 release, on Greedy-DiM. This shows only that E7 does not mechanically destroy a detector that is good on DiM (A41's printed caveat).
- **N3, validity in kind (F3, X3 only).** Genuine photos passed through the morphs' own generator family, without any morphing, behave like morphs for the detector. Here these are DiffAE reconstructions (X3). The test must also show that it could catch identity mixing at all: its positive-control detector, FE ViT-L/14, must score above 0.65 on the reconstructions.
- **N4, reproduction.** For C1, with the release's own crop on the raw files (X7′, H-new-145), both components:
  - "published regime reproduced on raw files": raw Greedy-DiM within 5 points of the published 7.60, and the FRLL-5 mean within 5 of 2.96;
  - "our frames do not change the native regime": |raw − frame| ≤ 3 points for Greedy-DiM and MorDIFF.

  The raw-file reversal is descriptive. For C2, N4 is the five-crop check (X14b, F6).

**No claim meets this bar.** The closest is C1, the SelfMAD release on diffusion morphs:
- It meets N1 (F1, F2), N2 (F4, Greedy-DiM; not shown on MorDIFF) and N4 (X7′, both components).
- It does not meet N3: the positive control reached only 0.636.
- A border or alignment artefact of our control photos is not formally excluded.
- The top grade would also need no fired C1 kill and W-c resolved (PROTOCOL l.14441).
- So its grade is "strong (final)", and the top grade cannot be reached.

**Even the top grade would not be "beyond doubt":**
- Each claim concerns one released network.
- It is scored on one pool of 204 FRLL photos of 102 persons, and the re-runs re-use the same persons and images.
- A41's rules were written after earlier estimates of the same questions had been seen. Those earlier registered tests said "neither".
- The cue itself is not identified.

"Beyond doubt" would need the top grade plus replication: another checkpoint or retrain, fresh data and another studio pool, all under rules fixed before the data are seen.

**Three statements that are easy to confuse.**
- **"The result meets A41's shortcut definition."** This is about what carries one detector's result on one benchmark cell. A41's definition requires, in numbers:
  1. a construction difference separates morphs from genuine photos;
  2. the same difference can be put into genuine photos without any morphing;
  3. removing it removes at least half of the separation, at the thresholds above.

  C1 is the only claim whose numbers meet A41's shortcut definition. It is graded "strong (final)", and two registered conditions are open: the assay sensitivity of X3, and a pool artefact that is not formally excluded. In plain words (CONCLUSIONS): the SelfMAD release treats genuine photos that were merely shrunk to the morphs' face size as more morph-like than real Greedy-DiM morphs.
- **"The benchmark number changes under a control."** The benchmark number changes when a control alters a construction difference. This says neither by how much deployed performance is overstated nor that the detector relies on that difference.
  - A41's "inflated" label (tier 1) needs a native EER of at most 10% and a one-sided person-clustered test that the rise exceeds +5 passing at its Holm level (p5). It was first printed for the ViT-B/16 release on MorDIFF. It was superseded by "descriptive row" when a registered refuter fired, so this note does not use the word for that row.
  - Every other rise under a control below is descriptive. No registered rule was applied to it. Person intervals exist only for the A41 S2 and S3 release cells, not for FE ViT-B/16, FS, MixFaceNet-MAD or the recipes.
- **"The detector fails a clean test."** This is an absence. On a set where both classes come from the same tool or generator, and the known remaining differences are named (H1 file size, floor 0.620; H3 latent spread, by construction; H4b file size, floor 0.912), the detector does not rank morphs above non-morphs by a useful margin.
  - What it shows (C3 only, StyleGAN3): the detector's GAN benchmark number is not evidence of morph detection. The H1 labels are registered without a grade; H2 and Arc2Face are descriptive.
  - What it does not show: a shortcut, because it says nothing about which cue the detector uses on the benchmark. Nor does it show that the detector is blind to identity, unless the test has power and a passing positive control. X4 sits near 0.5 by construction, H2 is low-potency, and X3's positive control failed.
  - The registered example is C3, "strong (narrow)", for GAN morphs.

Claims B and C4 describe the benchmarks, not the detectors:
- B: morph and genuine files differ in construction attributes.
- C4: the GAN sets compare generator output with camera photos.

They make a shortcut possible. They do not show that any detector uses one.

## 2. Table: the shortcut test outcome for each method, against the registered bar

**Key**
- **E7.** Genuine photos shrunk to the morphs' median face size before the same alignment. Cells give EER in %, native → E7.
- **Brackets.** [ ] is a person-clustered 95% interval unless marked otherwise. "pair 90%" marks the A36 H1 and H3 intervals. Row 11's FRLL reproduction interval is marked "TOST": the A12-BR TOST interval (90%) over seeds plus the image bootstrap.
- **X3 AUC.** Published morphs against DiffAE reconstructions of the genuine photos. Below 0.5 means the reconstructions look more morph-like than the morphs.
- **"Renders vs camera"** (in the outcome column, not N3). AUC of the single-person StyleGAN3 renders of H3 against FRLL / FFHQ / FEI camera photos (A36 amendment 1, H-new-83).
  - The registered cell is the FRLL pool on the 11 primary rows (M1–M8O and the ViT-B/16 and ViT-L/14 releases), with verdict "neither". The FFHQ and FEI pools are descriptive, and so are rows 4–8 and the SelfMAD row (A39 R3).
  - It is not A41's N3 (A41: "X3 only"). The renders are not re-rendered genuine photos, and StyleGAN3 is not the MIPGAN generator.
- **"‡".** One of the 12 primary rows of C3.
- **Fixed outcome tags.** "meets A41's shortcut definition" (C1 only); "registered refuter fired" (C2); "negative control"; "not tested under a registered rule (descriptive: …)"; "no native EER ≤ 10% to carry" (rows 15–17: "no native EER ≤ 10% that E7 changes").
- **"Which morph type".** Filled only for cells with a registered grade; "—" otherwise.
- **"Met / not met".** Used only where A41 registered that condition for that cell. Everything else is a logged number with its status.
- **GAN status.** "C3 absence, 'strong (narrow)'; not a shortcut grade" on every ‡ row.

| # | Method (networks) | Shortcut test outcome and construction cue (plain words) | Which morph type | N1 reliance (number) | N2 specificity (number) | N3 validity in kind (number) | N4 reproduction (number) | Status (registered grade if any) | Missing for the top grade or replication / next test |
|---|---|---|---|---|---|---|---|---|---|
| **Official releases** | | | | | | | | | |
| 1 | SelfMAD release, HRNet-W18, its own dlib crop and resize on our frames (1) ‡ | **Diffusion: meets A41's shortcut definition (C1).** Against photos shrunk to the morphs' face size before the same alignment (E7), genuine photos score as more morph-like than published Greedy-DiM and MorDIFF morphs. Photos only resampled by DiffAE's aligner, and DiffAE reconstructions, also score above MorDIFF morphs. Cue word: "bona fide processing history; cue not identified". Its score rises with the shrinking factor: photo-only AUC 0.584 at ~1.0x → 0.998 at 3.30x ("dose response", registered secondary rule). **Regular:** not tested under a registered rule (descriptive: AMSL 2.9 → 33.3, WebMorph 5.9 → 51.9). **GAN:** C3 absence (Status). Renders vs camera 1.000 / 0.952 (FRLL / FFHQ; descriptive, A39 R3). | Diffusion: FRLL Greedy-DiM (main cell), MorDIFF (supporting) | Greedy-DiM 8.4 → 90.7, +82.4 [77.3, 87.4], d′ share 2.11. MorDIFF 2.5 → 61.3, +58.8 [54.2, 64.6], d′ share 1.19 (F1, F2 supported). **Met:** the ranking reverses (share 2.11). The control does more than remove the separation, which the review reads as pointing to the E7 construction (H-new-233, proposed); hence the pool-artefact qualifier. | MAD22 FaceMorpher against its own E7 pool 0.11 [0.00, 0.89]. ViT-L/14 release on Greedy-DiM Δ 0.00 [−3.15, 3.41] (F4 supported). **Met for Greedy-DiM.** On MorDIFF the same control moves ViT-L/14 by +10.74 [7.22, 14.19], so not shown there. | Reconstructions ranked above published morphs: Greedy-DiM 0.024 [0.011, 0.042] (floor-limited), MorDIFF 0.330 [0.284, 0.374]. Resampled-only photos 0.004 / 0.092 (F3 supported). The binding positive control failed: FE ViT-L/14 0.636 [0.579, 0.693] ≤ 0.65. **Not met** ("assay sensitivity not shown"). | Raw files with its own crop (X7′, H-new-145). "Published regime reproduced on raw files" (raw Greedy-DiM within 5 of 7.60; FRLL-5 mean within 5 of 2.96): Greedy-DiM 6.39 [3.35, 9.42]; FRLL-5 5.55. "Our frames do not change the native regime" (\|raw − frame\| ≤ 3): Greedy-DiM 6.39 vs 8.37; MorDIFF 1.49 vs 2.53. **Met** (both components). The reversal persists on the raw files, 6.4 → 87.2 (descriptive). | **C1 "strong (final)"**; top grade unreachable. Pool artefact not formally excluded (the border test, XA3c, ran but could not be evaluated). Earlier registered test (A32 H1): "neither". GAN: C3 absence, "strong (narrow)"; not a shortcut grade. | N3 with a positive control that passes. A successor border/alignment test. A second checkpoint, or a retrain over seeds (H-new-242; retrained networks are ours, not the release). Fresh data and another studio pool (X8). |
| 2 | MADation release, CLIP ViT-B/16 + LoRA (1) ‡ | **Diffusion: registered refuter fired (C2).** Its MorDIFF EER rises against shrunk photos (C2's registered cue word "fine-detail softness"; cue not identified). But it separates the published MorDIFF morphs from DiffAE reconstructions, a registered refuter: "Identity evidence or a file/frame property: open." Also descriptive, not registered decision cells (F5 covers MorDIFF only; no d′ share logged): DiM-C 6.39 → 29.51, +23.12 [19.08, 29.21]; Greedy-DiM-S 6.93 → 29.41, +22.47 [18.00, 27.43]. **Regular:** not tested under a registered rule (descriptive: AMSL 15.1 → 28.9, WebMorph 4.9 → 10.8). **GAN:** C3 absence (Status). Renders vs camera 0.947 / 0.980 / 0.964. | Diffusion: MorDIFF (C2 cell); DiM-C and Greedy-DiM-S (descriptive) | MorDIFF 4.9 → 19.6, +14.7 [10.3, 18.9]; d′ share 0.463 < 0.5. Tier 2 not reached: p10 0.0170 > its Holm level 0.00833 (the printed interval starts at 10.3, but the rule is the one-sided test). A rise in all five crops (+13.2 to +21.0). **Not met.** | FRLL FaceMorpher under E7 4.42 [2.12, 6.93] (F4 (ii) supported). But the MorDIFF control moves the ViT-L/14 release by +10.74 [7.22, 14.19]; in the central 256-px window that rise stays at +12.3 [6.6, 16.2] (A42, post hoc; CONCLUSIONS: the non-specificity "is not a border artefact"). **Not shown for MorDIFF.** | **Not met:** the registered refuter fired (F7, H-new-139b, falsified by its kill): MorDIFF morphs vs reconstructions 0.847 [0.803, 0.891]. With border area matched: 0.844 [0.787, 0.895] (A42, post hoc). Central 256-px window: 0.61 [0.56, 0.65] (A42 amendment 1, post hoc, explanation only; not a border test). DiM-A 0.361 the other way (descriptive). Identity evidence or a file/frame property: open. | **Met as registered** (F6 supported; five crops of our frames, not raw files). No raw-file run with MADation's pipeline. On our frames MorDIFF 4.9 against a published 1.1. | **C2 "descriptive row (final)"** (a registered refuter fired). Earlier registered test (A36 H-new-75): "neither". GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "above" (registered label, no grade). | A42 amendment 1: read (post hoc; see "Beside C2" in §4). A43 (the MorDIFF two-by-two, H-new-241; staged, not registered): pending. Then off-centre same-scale windows (H-new-262/263, proposed, not registered), a MorDIFF fidelity check, a fresh-data replication (H-new-234). |
| 3 | MADation release, CLIP ViT-L/14 + LoRA (1) ‡ | **Negative control** (A41 F4 (iii)). Shrinking photos does not move it on Greedy-DiM and photo-only (photo-only AUC 0.494 → 0.455, "none"); its MorDIFF pool rise is +10.74. It does react to other processing: 52.9% of JPEG-50 genuine photos flagged at its native threshold (descriptive). **GAN:** C3 absence (Status). Renders vs camera 0.904 / 0.808 / 0.924. | — | Greedy-DiM 9.8 → 9.8, Δ 0.00 [−3.15, 3.41]. MorDIFF 28.9 → 39.7, +10.74 [7.22, 14.19], but native above 10, so not a decision cell. | It is C1's N2 control: native 9.80 ≤ 10 and Δ 0.00 [−3.15, 3.41] on Greedy-DiM (F4 (iii) supported). | Greedy-DiM vs reconstructions 0.749 [0.696, 0.802]. Floor-limited (simple image properties alone 0.993), so uninformative. Same-person DiffAE "morphs" score above Greedy-DiM morphs (0.386, descriptive). | Our frames only. MorDIFF 28.9 against 19.3: not reproduced. MIPGAN-I 11.9 against 20.32: not reproduced. MIPGAN-II 9.9 against 9.06: reproduced. | F4 (iii) supported (as control). GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "above" (registered label). | No shortcut test applies: it is the negative control. Its MorDIFF rise is untested (native above 10). |
| 4 | MADation baseline FE ViT-B/16, frozen CLIP + head (1) | **Not tested under a registered rule** (descriptive: its numbers fall under E7; FRLL landmark 16.7–26.0 → 22.6–38.7; DiM 21.0–47.0 → 41.6–73.6). Renders vs camera 0.922 / 0.892 / 0.656 (descriptive). Registered "CLIP carries the render cue" (H-new-84): "neither". | — | No person interval and no rule. Most native EERs are above 10, outside A41's definition. MAD22 FaceMorpher 1.0 → 7.2. | not tested | X3 not run. | Our frames only: MorDIFF 39.7 against 17.86, not reproduced. | descriptive only (outside C3) | E7 cells with person intervals under a registered rule; X3; a raw-file run. |
| 5 | MADation baseline FE ViT-L/14, frozen CLIP + head (1) | **Not tested under a registered rule** (descriptive: it changes little under E7; landmark +0.5 to +1.5; Greedy-DiM-S holds). It is the registered X3 positive control, whose gate failed (N3). Renders vs camera 0.887 / 0.903 / 0.861 (descriptive). | — | Greedy-DiM-S 11.8 → 13.8, +1.98 [0.25, 4.72] (descriptive; native above 10). | not tested | MorDIFF vs reconstructions 0.742 [0.689, 0.792], DiM-A 0.772 (descriptive; not shown to be identity evidence: no fidelity check covered MorDIFF). As the registered X3 positive control on Greedy-DiM: 0.636 [0.579, 0.693] ≤ 0.65, gate failed. | Our frames only: MorDIFF 34.8 against 22.85, not reproduced. | descriptive only. Its failed gate is what blocks N3 for C1. | For C1, a positive-control detector that clears 0.65 on a same-generator test. |
| 6 | MADation baseline FS ViT-B/16, from scratch + head (1) | **Not tested under a registered rule** (descriptive: weak natively; its moderate DiM numbers go to near chance against shrunk photos, 16.1–24.0 → 41.6–45.6). Renders vs camera 0.877 / 0.509 / 0.569 (descriptive). | — | No person interval. DiM native 16–24, above A41's 10% entry bar. FRLL OpenCV 3.9 → 5.4 holds. | not tested | X3 not run. | Our frames: MorDIFF 67.6 against 28.14, not reproduced. | descriptive only | No shortcut test applies: no native EER ≤ 10% falls under the control (FRLL OpenCV 3.9 → 5.4). |
| 7 | MADation baseline FS ViT-L/14, from scratch + head (1) | **No native EER ≤ 10% to carry.** Weak natively everywhere (27.6–49.0% with or without a control). G-test inverted (67.4). Renders vs camera 0.594 / 0.611 / 0.465 (descriptive). | — | — (no native cell at or below 10%) | not tested | X3 not run. | Our frames only: MorDIFF 43.0 against a published 40.92 (no reproduction label logged; near chance either way). | descriptive only | No shortcut test applies (no native EER ≤ 10%). |
| 8 | MixFaceNet-MAD, the official release, on our frames (loader checked on its own training files) (1) | **No native EER ≤ 10% to carry.** It does not reproduce on our frames (cause: our frames or the genuine-photo source, not separated). It ranks FRLL genuine photos above FRLL landmark morphs with or without the control. No sentence may tie its numbers to image size (drop list). Renders vs camera 0.588 / 0.875 / 0.651 (descriptive). | — | — (FRLL landmark families inverted natively, 75.5–98.0) | not tested | X3 not run. | Not reproduced on our frames: MAD22-5 / FRLL-5 41.7 / 76.5 against 13.69 / 8.96. The loader is verified (0.45% on its own SMDD training files), so the cause is our frames or the genuine-photo source; the two are not separated. | descriptive only (outside C3; X4 not scored) | Scoring on its own crops and raw files before any reading. |
| **Published recipes, our re-implementation, SMDD only** | | | | | | | | | |
| 9 | M1 Inception-MAD, Inception-v3 from scratch (5) ‡ | **Not tested under a registered rule** (descriptive: its rankings follow the benchmark's morph files. Against byte-copy genuine photos, OpenCV-tool morphs score 3.3% from MAD22's 1351-px files and 53.6% from FRLL's 431-px files. Its fair results collapse once the photos are shrunk). **GAN:** C3 absence (Status). Renders vs camera 0.969 / 0.977 / 0.644 (morphs vs FRLL 0.990). | — | Seed means; no person interval, no d′ share. MAD22 FaceMorpher 6.4 → 39.0. Greedy-DiM 9.0 → 60.7. UA8c 14.4 → 49.4 (uncapped 63.0). | not tested | X3 not run. | Re-implementation, not the authors' pipeline. Reproduction test (TOST): falsified. | descriptive only (no registered shortcut rule applied to recipes). GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "not above" (registered label). | A registered E7 rule with person intervals over its networks, a negative control and X3. A re-implementation that reproduces. |
| 10 | M2 MorphHRNet-style, HRNet-W48 from scratch (5) ‡ | **No native EER ≤ 10% to carry.** Inverted natively on FRLL landmark families (67.5–90.7%). Degrading both classes does not remove the inversion (H-new-B falsified). Renders vs camera 0.440 / 0.886 / 0.587. | — | — (no FRLL landmark, MAD22 FaceMorpher or diffusion cell at or below 10% natively) | not tested | X3 not run. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. It is the highest H3 row (0.591 [pair 90% 0.572, 0.610]), still below the combined floor; single networks reach a within-pair θ of 0.66, and simple image properties alone reach 0.62. H1 "not above". | No shortcut test applies (no native EER ≤ 10%). |
| 11 | M3 MADation recipe, CLIP ViT-B/16 + LoRA (8) ‡ | **Not tested under a registered rule** (descriptive: on regular and diffusion morphs it changes little under E7. Photo-only, it flags 5.9% of half-size photos at its native threshold, against 5.4% native; A32 hypothesis M, "not supported as registered", read descriptively). **GAN:** its MIPGAN-I EER (7.0%) is measured on generator output against camera photos (C4). On the clean test it ranks single-person renders above morphs (H3 0.448). Renders vs camera 0.951 / 0.956 / 0.967. | — | Regular and diffusion: little change under E7 (seed means, descriptive). Landmark moves ≤ 0.6; MAD22 FaceMorpher 5.0 → 5.3; UA8c 12.6 → 12.1. GAN: no control on the benchmark cell. | not tested | X3 not run. | Re-implementation. MAD22 reproduced on the mean only (per family MIPGAN-I 7.0 against 33.37, OpenCV 23.7 against 3.85). FRLL inconclusive: +2.17 [TOST 0.86, 3.47], margin 1.73. | GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "above" (registered label). Otherwise descriptive. | GAN: X6 (the causal C4 test; it would need its own registered claim); a same-generator clean set with a passing positive control. X3 for the recipes. |
| 12 | M3L MADation recipe, CLIP ViT-L/14 + LoRA (5) ‡ | **Not tested under a registered rule** (descriptive: regular and diffusion change little under E7; MorDIFF stays weak, 45.7 → 41.5). **GAN:** MIPGAN-I 0.8% is synthetic vs camera. H3 0.401 (reversed). H4b 0.923 is not above the file-size floor of 0.912 (+0.010; Bonferroni lower bound −0.031). Renders vs camera 0.934 / 0.940 / 0.957. | — | Landmark ≤ 0.6 change (FaceMorpher 0.4 → 0.4; MAD22 FaceMorpher 0.6 → 0.5). UA8c 17.7 → 16.1 (seed means). | not tested | X3 not run. | Re-implementation. MAD22 better than published (TOST). | GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "above". Otherwise descriptive. | As M3. |
| 13 | M4 SelfMAD-style, HRNet-W18 + self-blended fakes from SMDD genuine photos only (5) ‡ | **No native EER ≤ 10% to carry.** Inverted on the benchmarks: 100% EER on AMSL, WebMorph and all seven diffusion families, 90.9% on FaceMorpher. Shrinking makes photos look genuine to it (MAD22 FaceMorpher 99.8 → 0.8), the opposite direction from the SelfMAD release. Above the floor on the clean landmark set (H1 0.761). Renders vs camera 0.314 / 0.394 / 0.999. | — | — (no native cell at or below 10%; the control improves it) | not tested | X3 not run. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "above". | No shortcut test applies (no native EER ≤ 10%). Its opposite-direction response is descriptive. |
| 14 | M5 PW-MAD, DenseNet-121 with pixel-wise labels (8) ‡ | **Not tested under a registered rule** (descriptive: fair native results fall once the photos are shrunk; MAD22 OpenCV and Webmorph, shrunk only ~1.0x, do not change). Renders vs camera 0.881 / 0.845 / 0.801. | — | Seed means, no person interval; seed SD up to ±17 on some families. WebMorph 4.2 → 14.3; AMSL 8.9 → 25.7; MAD22 FaceMorpher 1.2 → 20.7; UA8c 28.0 → 49.5 (uncapped 72.3). | not tested (the ~1.0x families' stability is a no-dose check, descriptive) | X3 not run. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "not above". | As M1. |
| 15 | M6 OrthoMAD, ResNet-18 from scratch (5) ‡ | **No native EER ≤ 10% that E7 changes.** Inverted natively on FRLL landmark families (59.8–81.4%), and not removed by degrading both classes (H-new-B falsified). MAD22 FaceMorpher 24.4 → 47.5 (collapses under E7, descriptive). Renders vs camera 0.525 / 0.913 / 0.572. | — | — (no native cell at or below 10% that E7 changes: MAD22 OpenCV 9.4 → 10.0, shrunk only ~1.0x) | not tested | X3 not run. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "not above". | No shortcut test applies (no native EER ≤ 10% that E7 changes). |
| 16 | M8 MixFaceNet-MAD recipe, MixFaceNet-S from scratch (5) ‡ | **No native EER ≤ 10% that E7 changes.** Weak or inverted natively (FRLL FaceMorpher and OpenCV inverted). MAD22 FaceMorpher 27.6 → 65.7 under E7 (descriptive). Renders vs camera 0.763 / 0.963 / 0.662. | — | — (no native cell at or below 10% that E7 changes: MAD22 OpenCV 6.4 → 6.8, ~1.0x) | not tested | X3 not run. | Re-implementation; TOST falsified. | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "not above". | No shortcut test applies (no native EER ≤ 10% that E7 changes). |
| 17 | M8O MixFaceNet-MAD, official training code (5) ‡ | **No native EER ≤ 10% that E7 changes.** Inverted natively on all four FRLL landmark families. At its native 5% threshold it flags 26.7% of half-size genuine photos and 57.3% of the DiM E7 photo pool (descriptive): shrunk photos move toward "morph" for it, but it has no good native result for that to carry. Renders vs camera 0.697 / 0.954 / 0.629. | — | — (no native cell at or below 10% that E7 changes: MAD22 OpenCV 6.1 → 6.7, ~1.0x) | not tested | X3 not run. | Official-code reproduction (O-Repro): falsified. O × d0 MAD22-5 35.78 ± 3.66, FRLL-5 67.59 ± 7.31, against the published 13.69 / 8.96 (A12-BR README l.146). | descriptive only. GAN: C3 absence, "strong (narrow)"; not a shortcut grade. H1 `orig` "not above". | No shortcut test applies (no native EER ≤ 10% that E7 changes). |

**Notes to the table**
- **Confidence-interval levels.**
  - Person-clustered 95%: the A41 cells (S2, S3, DC-8, X3, X7′) and A42 (border-matched and central-window X3, the central-window rises).
  - Pair 90%: the A36 H1 and H3 values.
  - TOST (90%, over seeds plus the image bootstrap): the A12-BR reproduction intervals (row 11).
  - Seed means, or mean ± SD: the recipes.
- **H1 labels.** Registered for the 11 primary rows (M1–M8O and the ViT-B/16 and ViT-L/14 releases), with no grade and set post-freeze. The SelfMAD own-crop H1 (`orig` 0.872) is a point estimate, counted "above" only in A39's sensitivity read.
- **No landmark (regular) cell has a shortcut grade.** E7 leaves the alignment borders on landmark families (E07 README), and border fraction alone separates several evaluation families almost perfectly (AUC 0.99–1.00). On MorDIFF, 0.471 of the pool's difference from the native photos sits in the warped border (H-new-152 W-c).
- **Recipes.** No registered shortcut rule was applied to them. A12.4 calls their benchmark pool "an eval-pipeline diagnostic, never a detection result".
- **Printed beside every claim in the paper** (CONCLUSIONS):
  - the positive controls: the X3 gate failed (0.636 ≤ 0.65), and the ViT-L/14 release is unchanged on Greedy-DiM (Δ 0.00 [−3.15, 3.41]);
  - our own networks' history with the same shortcut (take it from CONCLUSIONS);
  - "MADMamba not evaluated on H3 (sealed)".

## 3. Method by method: what was found, how we know, how sure

**1. SelfMAD release.**
- *What:* meets A41's shortcut definition on diffusion morphs (C1). It treats genuine photos that were only shrunk to the morphs' face size as more morph-like than real Greedy-DiM and MorDIFF morphs. Cue: "bona fide processing history; cue not identified".
- *How we know:*
  - Against photos shrunk to the morphs' face size before the same alignment (E7), its Greedy-DiM EER goes 8.4% → 90.7% (+82.4 [77.3, 87.4]).
  - The same control leaves MAD22 FaceMorpher morphs detected (0.11%) and leaves the ViT-L/14 release unchanged on Greedy-DiM (Δ 0.00).
  - With its own crop on the raw files, its published regime reproduces (6.4% against 7.6%) and our frames do not change the native regime. There the reversal persists (6.4% → 87.2%, descriptive).
- *How sure:* this is C1, graded "strong (final)", the highest grade any shortcut claim reached here, but not the top grade. Two registered conditions are open:
  - the reconstruction test's positive control failed (0.636 ≤ 0.65);
  - a border or alignment artefact of our control photos is not formally excluded.

  It is also one checkpoint on 204 photos of 102 persons, the earlier registered test said "neither", and it says nothing about the SelfMAD method.

**2. MADation release ViT-B/16.**
- *What:* no shortcut is shown; a registered refuter fired. On MorDIFF its EER rises against shrunk photos (C2's registered cue word "fine-detail softness"; cue not identified), but our rules do not let us call this a shortcut.
- *How we know:*
  - The rise, 4.9% → 19.6% (+14.7 [10.3, 18.9]), appears in all five crops (+13.2 to +21.0).
  - It removes less than half of the separation (d′ share 0.46). Tier 2 is not reached (p10 0.0170 > 0.00833). The same control also moves the ViT-L/14 release (+10.7).
  - The release separates the published MorDIFF morphs from DiffAE reconstructions (0.85 [0.80, 0.89]), a registered refuter.
  - Two DiM variants also rise, from 6–7% to 29% (DiM-C, Greedy-DiM-S; descriptive, not decision cells).
- *How sure:* this is C2, a "descriptive row (final)": "Identity evidence or a file/frame property: open." A42 amendment 1 adds only the explanation sentence beside C2. A43 (the MorDIFF two-by-two, H-new-241; staged, not registered) is pending.

**3. MADation release ViT-L/14.**
- *What:* the negative control. It is the detector that ignores downsampling on Greedy-DiM and photo-only; its MorDIFF pool rise is +10.7.
- *How we know:* its Greedy-DiM EER is unchanged under the control (9.8 → 9.8, Δ 0.00 [−3.15, 3.41]), and shrunk photos do not look more morph-like to it (0.494 → 0.455). It does react to JPEG-50 photos (52.9% flagged).
- *How sure:* it is registered as a control component (F4 (iii) supported), not as a claim about the detector. On GAN morphs it does not rank morphs above single-person renders by the registered margin (H3 0.427, reversed; C3).

**4. FE ViT-B/16.**
- *What:* not tested under a registered rule.
- *How we know:* its numbers fall under E7 on landmark and DiM morphs, but most of them start above 10%. No registered rule or person interval was applied, and X3 was not run.
- *How sure:* descriptive only, one network.

**5. FE ViT-L/14.**
- *What:* not tested under a registered rule.
- *How we know:* it changes little under E7 (Greedy-DiM-S +1.98 [0.25, 4.72]). It separates published MorDIFF morphs from reconstructions (0.742 [0.689, 0.792]), which is not shown to be identity evidence (no fidelity check covered MorDIFF).
- *How sure:* descriptive. As the registered positive control on Greedy-DiM it reached only 0.636 ≤ 0.65. That failure is why C1 cannot meet N3. It does not void C2's refuter, which fired under its own registered rule.

**6. FS ViT-B/16.**
- *What:* not tested under a registered rule.
- *How we know:* it is weak natively. Its DiM numbers (16–24%) go to 42–46% against shrunk photos, but they start above A41's 10% entry bar.
- *How sure:* descriptive only, one network.

**7. FS ViT-L/14.**
- *What:* no native EER ≤ 10% to carry.
- *How we know:* it sits at 27.6–49.0% with or without the control, so there is no good result for a cue to carry. On our frames its MorDIFF EER is 43.0% against a published 40.92% (no reproduction label logged).
- *How sure:* descriptive only.

**8. MixFaceNet-MAD release.**
- *What:* no native EER ≤ 10% to carry.
- *How we know:* it does not reproduce on our frames (41.7 / 76.5 against the published 13.69 / 8.96). Its loader is verified on its own training files (0.45%), so the cause is our frames or the genuine-photo source, and these are not separated.
- *How sure:* descriptive only. No sentence may tie its numbers to image size.

**9. M1 Inception-MAD.**
- *What:* not tested under a registered rule. Descriptively, its rankings follow the benchmark's morph files, and its fair results collapse once the photos are shrunk.
- *How we know:* OpenCV-tool morphs score 3.3% from MAD22's 1351-px files and 53.6% from FRLL's 431-px files. Under E7, MAD22 FaceMorpher goes 6.4% → 39.0% and UA8c 14.4 → 49.4.
- *How sure:* descriptive only. These are seed means of a re-implementation that did not reproduce, with no person interval, no negative control and no X3.

**10. M2 MorphHRNet-style.**
- *What:* no native EER ≤ 10% to carry.
- *How we know:* it is inverted natively on FRLL landmark morphs (67–91%), and degrading both classes does not remove that.
- *How sure:* descriptive. On GAN morphs its 0.591 is the best H3 row and still below the combined file-size and eye-geometry floor (C3). Single networks reach a within-pair θ of 0.66, and simple image properties alone reach 0.62.

**11. M3 MADation recipe ViT-B/16.**
- *What:* not tested under a registered rule. On regular and diffusion morphs it changes little under E7 (seed means, descriptive).
- *How we know:* on GAN morphs:
  - its 7.0% MIPGAN-I EER compares generator output with camera photos;
  - it scores single-person renders above camera photos (0.951 / 0.956 / 0.967; renders vs camera, registered only for the FRLL pool, H-new-83 "neither");
  - with both classes from the generator, it ranks renders above morphs (H3 0.448).
- *How sure:* the GAN absence is C3, "strong (narrow)". The renders-vs-camera numbers are descriptive, and no causal GAN test has run (X6).
  - Allowed: "its GAN benchmark number is not evidence of morph detection".
  - Not allowed: "it uses a GAN shortcut".

**12. M3L MADation recipe ViT-L/14.**
- *What:* not tested under a registered rule; the pattern is the same as M3.
- *How we know:* MIPGAN-I is 0.8% on synthetic vs camera, H3 is 0.401 (reversed), and H4b is not above the file-size floor (0.923 against 0.912; Bonferroni lower bound −0.031).
- *How sure:* C3 "strong (narrow)" for the absence; the rest is descriptive.

**13. M4 SelfMAD-style.**
- *What:* no native EER ≤ 10% to carry.
- *How we know:* it is inverted on the benchmarks. Shrinking makes photos look genuine to it (MAD22 FaceMorpher 99.8 → 0.8), the opposite of the SelfMAD release. It is above the floor on the clean landmark set (H1 0.761).
- *How sure:* descriptive only.

**14. M5 PW-MAD.**
- *What:* not tested under a registered rule. Descriptively, its fair native results fall once the photos are shrunk.
- *How we know:* WebMorph goes 4.2 → 14.3, MAD22 FaceMorpher 1.2 → 20.7 and UA8c 28.0 → 49.5, while the families shrunk only ~1.0x do not change.
- *How sure:* descriptive only. These are seed means with seed SD up to ±17, from a re-implementation that did not reproduce.

**15. M6 OrthoMAD.**
- *What:* no native EER ≤ 10% that E7 changes.
- *How we know:* it is inverted natively on FRLL landmark morphs (59.8–81.4%), and degrading both classes does not remove that. MAD22 FaceMorpher goes 24.4 → 47.5 under E7 (descriptive). Its only native cell at or below 10%, MAD22 OpenCV (9.4 → 10.0), is shrunk only ~1.0x, so E7 tests nothing there.
- *How sure:* descriptive only.

**16. M8 MixFaceNet-MAD recipe.**
- *What:* no native EER ≤ 10% that E7 changes.
- *How we know:* it is weak or inverted natively. Its MAD22 FaceMorpher fall (27.6 → 65.7) starts above 10%. Its only native cell at or below 10%, MAD22 OpenCV (6.4 → 6.8), is shrunk only ~1.0x.
- *How sure:* descriptive only.

**17. M8O MixFaceNet-MAD, official code.**
- *What:* no native EER ≤ 10% that E7 changes.
- *How we know:* it is inverted natively on all four FRLL landmark families. Shrunk photos move toward "morph" for it (26.7% of half-size photos flagged at its native threshold), but there is no good native result for that to carry. Its MAD22 OpenCV cell (6.1 → 6.7) is shrunk only ~1.0x.
- *How sure:* descriptive only. The official-code reproduction was falsified (MAD22-5 35.78 ± 3.66, FRLL-5 67.59 ± 7.31, against 13.69 / 8.96).

**Across rows.**
- C1 is the only claim whose numbers meet A41's shortcut definition. It is graded "strong (final)"; two registered conditions are open (assay sensitivity of X3; pool artefact not formally excluded). In plain words (CONCLUSIONS): the SelfMAD release treats genuine photos that were merely shrunk to the morphs' face size as more morph-like than real Greedy-DiM morphs.
- Every other row carries one of the fixed tags:
  - registered refuter fired (C2, the ViT-B/16 release on MorDIFF);
  - negative control (the ViT-L/14 release);
  - not tested under a registered rule (descriptive moves under a control);
  - no native EER ≤ 10% to carry.
- Separately, there are absences on clean tests: C3 for GAN morphs, and the H1 labels for landmark morphs (registered, no grade). Neither is a shortcut grade.
- Never write "published detectors rely on shortcuts", "for every method" or "MADation carries the shortcut".

## 4. What would strengthen each claim (what "beyond doubt" would still need)

A41's grades are final. CONCLUSIONS: "What can still change a grade. Nothing". That covers C1–C4 and B. Each item below can only change an explanation sentence, or support a new claim registered separately before its data are seen.

**C1 (SelfMAD release, diffusion morphs)**
1. **N3 with a working positive control.** This is the one registered condition still missing. It needs a same-generator test whose positive-control detector clears its bar. On X3, FE ViT-L/14 reached only 0.636 ≤ 0.65, where simple image properties alone give 0.993. This note's sources name no scheduled item for it.
2. **Exclude the control-pool artefact.**
   - A successor border test, with its cut set relative to the untrained-network baseline (A41's calibration note).
   - Path attribution (H-new-261, about 0.05 GPU-h, after the deadline).
   - The best-aligned-third check (H-new-260, zero GPU, proposed) can add a sentence. It cannot remove the qualifier.
3. **A second checkpoint, or a retrain over seeds** (after the deadline). This is the SelfMAD retrain whose self-morphs use an integer shift instead of an interpolated zoom (H-new-242; 2 seeds per arm, 40–80 GPU-h). It would add retrained networks (ours, not the release) and test the mechanism note, which is "consistent with" C1 and does not explain it.
4. **Fresh data and another studio pool (X8)** (after the deadline). Every C1 number sits on the same 204 FRLL photos of 102 persons.

**C2 (ViT-B/16 release, MorDIFF)**
1. **A42 amendment 1, the window test** (H-new-240 (b), H-new-255): read. It added the Beside-C2 explanation sentence only, and the zoom confound stays (H-new-262/263, proposed). CONCLUSIONS, "Beside C2" (explanation, not part of "What we may write"): "Post hoc (A42; one network, the same 204 photos; the window covered by the author's ruling on (i) of 2026-11-07 about 18:35 CET): matching border area leaves the separation at 0.84. In the central 256-px window, which holds no zero-fill and which the loader enlarges about 2x, it falls to 0.61 [0.56, 0.65], while the rise against downsampled photos grows to +32.9 [28.9, 37.7]. Most of the refuter lies outside the central window or depends on the face's scale (not separated); the rise does not need the zero-filled border. Identity evidence or a file/frame property: open." Never "the kill is spurious"; never call this window a "border test".
2. **Same-pair MorDIFF morphs (H-new-241), staged as A43, the MorDIFF two-by-two:** pending.
   - It compares the published morphs with our same-pair morphs (how the published files were made).
   - It also compares our two-identity morphs with our one-identity morphs (identity evidence).
   - It is a staged test designed to tell identity evidence from how the published MorDIFF files were made; PROTOCOL (l.17049–17050) calls H-new-241 "the only identity-vs-pipeline test for C2". It has not been registered or run, and nothing is predicted.
3. **Zero-GPU matching checks** (H-new-257, H-new-258; proposed, not registered): is the border slope a property of the control photos, and does matching on border area and on file size per content pixel remove the separation? PROTOCOL (l.17047, l.17469) and CONCLUSIONS (l.283) plan these, with H-new-260 and 264–266, as one zero-GPU registration that they also call "A43". That is a different item from the staged MorDIFF two-by-two in item 2.
4. **After the deadline:**
   - a fresh-data replication of the ViT-B/16 rise (H-new-234);
   - a same-scale window that keeps the zero-fill;
   - another studio pool (X8).

**C3 (GAN morphs, absence)**
1. **A clean set with power against a two-identity signal and a positive control that passes.** X4 sits near 0.5 by construction, and H3's classes differ in latent spread.
2. **Other generators.** C3 covers StyleGAN3 only.
3. **X6, the causal test of C4** (3–5 H100-h or 8–16 GB10-h, after the deadline). C4's grade is final; X6 could only support a separately registered causal claim about what a detector uses on MIPGAN-I/II.

**Regular (landmark) morphs (no shortcut grade registered)**
1. **A registered landmark rule with a border-matched control.** E7 leaves the alignment borders in place. It also needs person-clustered intervals for the descriptive falls: SelfMAD AMSL and WebMorph, and the recipes' collapses (M1, M5, M6, M8, M8O).
2. **Per-network registered rules for the recipes, with a negative control.** None has been applied so far.

**B and C4 (benchmark construction)**
- Hash the 15,518 enumerated files. They were listed, not hashed; a hash-only manifest is proposed.
- C4's grade is final; X6 could only support a separately registered causal claim. A storage-format sentence would need a new registered claim (no row read a storage-format cue, H-new-142).

## 5. Flags for the author (outside this note)

1. **CONCLUSIONS l.124 heading.** The bullet's heading still reads "…MorDIFF result is inflated on our frames". Its body and the claims table say "descriptive row". A reviewer will quote the heading.
2. **The name "A43".** Main PROTOCOL and CONCLUSIONS use it for the zero-GPU registration of H-new-257/258/260/264–266; branch a43 uses it for the MorDIFF two-by-two (H-new-241). One of the two needs a new name before either is registered.
3. **Staged A43 interpretation table.** One of its labels uses a word the drop list forbids for any claim, and C2's grade is final. That label must not enter this note or the paper.
