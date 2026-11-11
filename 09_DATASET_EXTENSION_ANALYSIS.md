# Dataset extension: what we know, what the plan covers, what to add

Date: 11 Nov 2026. Read-only analysis. No GPU job, no SSH, nothing sealed opened (no `fst*`, `valx*`, A12SP).
Author question: "Impact of dataset extension on generalisation and on eliminating usage of benchmark cues in
training: are we covered there with our planned experiments? Should we do some more work?"

## Terms

- **S-MAD**: single-image morphing attack detection. **EER**: equal error rate (50% = chance). **AUC**: area under
  the ROC curve (0.5 = chance; below 0.5 = the ranking is reversed, "inverted").
- **SMDD**: the standard synthetic training set (25,000 synthetic bona fide renders + 15,000 morphs).
- **Dataset extension**: training on more than SMDD. In our record: genuine FERET/FRGC photos ("photos"), our
  classical landmark morphs from those photos ("classical morphs", three landmark tool families), our GAN morphs
  (A28, 3,000 StyleGAN2/e4e and MIPGAN-II-style), and planned own DiffAE morphs.
- **d0 / d1** (A12 names): d0 = SMDD only. d1 = SMDD + photos + classical morphs ("our data", our whole training
  protocol). **photos-only** = d1 without our morphs.
- **A / B / C** (ABC60 and A50 names): A = SMDD; B = A + genuine FERET/FRGC photos; C = B + classical morphs.
  CG / CD / CGD = C + our GAN morphs / + our DiffAE morphs / + both (never run).
- **R / P**: a published method's own recipe (R) vs our training recipe (P).
- **E7**: the control where the genuine test photos get the same shrink-and-enlarge history as the morphs. The
  **E7 rise** = EER under E7 minus EER on the native photos. A large rise means the score follows processing
  history, not morphing.
- **UA8c**: mean EER over the seven held-out FRLL diffusion families (six DiM variants + MorDIFF), E7 pool, each
  family capped at 50. **native17**: mean EER over the 17 native benchmark families (MAD22, FRLL-Morphs, DiM, MorDIFF).
- **Held-out matched sets**: **H1** = CASIA-WebFace landmark morphs (MediaPipe warp + Poisson blend, unseen tool and
  unseen source) vs the host's own unmodified photo, 598 pairs, `orig` and identically post-processed `pp`; bytes-only
  floor AUC 0.620 / 0.681. **H2** = IP-Adapter-FaceID diffusion morphs vs single-identity renders of the same pipeline
  (992 + 992, CASIA, low potency). **H3** = StyleGAN3 two-person morphs vs single-person renders (423 + 423);
  **H3_spread / X4** = the same morphs vs renders matched to the morphs' latent spread. **Q** = mean EER of H2 and H3
  orig (the ABC60 primary). **X3** = MorDIFF morphs vs FRLL aligner-only copies (a256), DiffAE reconstructions (rec)
  and DiffAE self-morphs (self).
- **G-test**: FEI StyleGAN morphs; a selection-seen generator, not a clean held-out test. **VALX-A\***: the selection
  set (FERET/FRGC people, one held-out splice tool).
- **Twin**: a one-identity image made by the same pipeline as a morph, with the same post-processing.

## 0. Short answer

- **Generalisation.** Extension helps on tests built like our training data (in-tool benchmarks, selection set,
  StyleGAN G-test) and, descriptively, on one unseen-source landmark set (H1, where "our data" raise AUC by
  +0.06 to +0.17 under our recipe in 7 of 7 methods). It does **not** help on any test where both classes come from
  one pipeline (H2, H3, X4, Q: all at 45-53% EER, unchanged or worse). On held-out FRLL diffusion it moves broken
  CNNs from chance to 42-45%, which is near floor.
- **Cue usage.** No experiment was designed to show that extension removes a cue, and none shows it on a
  matched test. One derived reading in this note (Section 2.2) is new: in ABC60, adding genuine photos (B-A) cuts the
  diffusion E7 rise by 13-29 points in all four architectures, and adding classical morphs (C-B) gives most of it back
  in two of four. Adding photos also makes every architecture flag single-identity renders more (Q worse, 4 of 4).
  So extension **moves** which cues are available; it does not remove them.
- **Coverage.** The new plan (TwinSet) answers "does matched data give a detector that responds to identity
  blending". It does not answer "did our earlier, unmatched extension help or hurt", "is it matching or just more
  data", or "does anything hold on a source never used in training". Four cheap additions close this, three of them
  by re-scoring existing checkpoints (about 1 H100-hour in total). Section 4.

## 1. Every dataset-extension experiment run so far

Author ruling (PROTOCOL A12.5 (14), 1 Nov): "our data help" refers to the whole training protocol (photos + morphs);
attribution to the morphs alone is not required. The A12.6/A12.7/A50/ABC60 decompositions are descriptive splits
inside it and do not gate that claim.

Columns: (i) = tells us something about generalisation beyond the training construction; (ii) = tells us
something about reduced cue usage. "In-tool" = the test family was made with a tool used in training.

| # | Experiment | What was added | Architectures | Seeds | Measured | Result (numbers) | (i) | (ii) | Source |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A8-W1F data arms | R6: 4,223 more real FRGC photos; R8: 2,500 same-person self-morphs labelled morph; d1-real: SMDD bona fide replaced by real photos; "all" = R6+R8+SBI | MADMamba-N (scratch), VMamba-T, ConvNeXt-T | 3 | VALX-A (selection set); unmatched V-GAN | R6, d1-real: no arm passes the decision rule in any architecture. R8 helps the pretrained nets but fails guard G2 (VMamba 22.60, ConvNeXt 32.39). d1-real lowers unmatched V-GAN EER (MADMamba 21.57 to 17.55, VMamba 11.92 to 6.47, ConvNeXt 11.44 to 4.54), resolution-confounded. SBI (not data extension) is the only lever. | No: selection set from training sources; V-GAN unmatched | No: H4 ("SMDD teaches StyleGAN render = bona fide") left open | `experiments/A8-W1F_data-arms/README.md` |
| 2 | A12-BR | d0 to d1, crossed with R vs P | M1 Inception-MAD, M2 MorphHRNet-style, M3 MADation ViT-B/16, M4 SelfMAD-style, M5 PW-MAD, M6 OrthoMAD, M8 MixFaceNet | 3-8 | UA8c (E7 pool, capped), BENCH (in-tool) | P x d1 - R x d0 on UA8c: M1 -4.50, M2 -6.45, M5 -4.79, M6 -5.31 (confirmatory, Holm), to 42.0-44.9% (from 48-50). MADation +30.68 worse. 75-98% of each CNN gain sits in two of six DiM variants. For M1 and M5, R x d1 already matches P x d1 (44.7 vs 44.9; 44.1 vs 44.8). | Weak: held-out, but near chance and two families | In-tool only: d1 removes a cross-format cue (OpenCV 4% at 1351 px vs 72% at 431 px for M1 R x d0) inside the training tools | `A12-BR_benchmark_recipes/README.md` |
| 3 | A12-4 | R x d1, fresh seeds 4-8 | M1, M5 | 5 | UA8c | M1: P x d1 - R x d1 +0.48 [-2.49, +3.45] (data carries about 90% of the gain); M5 +1.64 [-0.26, +3.54] (about two thirds) | Weak | No | `A12-4_benchmark-followups/README.md` |
| 4 | A12-5 | frozen-CLIP linear probe d0 vs d1; OrthoMAD R x d1 | CLIP ViT-B/16 frozen + head; M6 | 5 | UA8c, G-test, BENCH | Probe UA8c 15.20 to 10.71 (-4.49 [-7.95, -1.02]), no inverted family; G-test -11.97 (neutral family only). OrthoMAD R x d1 -0.57 [-2.45, +1.30] (null); needs data and recipe together (-5.31). | Weak-moderate: held-out diffusion, but the E7 rise of this probe is already about 0 (Section 2.2) | No | `A12-5_a124-review-followups/README.md` |
| 5 | A12-6 | photos-only arm (d1 minus our 62,112 morph items) | probe; MADation R | 5 (R d1: 8) | UA8c, G-test | Probe UA8c: photos-only 9.81, -5.39 [-8.82, -1.96] vs d0; adding morphs +0.90 [-0.93, +2.73]. MADation G-test: morphs carry it (d1 - photos-only -22.71 [-32.38, -13.03]); MADation UA8c unresolvable (-2.37 [-5.67, +0.93]). | Photos help the probe on held-out diffusion; morphs only on the selection-seen StyleGAN | No; photos-only adds a real-photo = bona fide cue (disclosed) | `A12-6_photos-vs-morphs/README.md` |
| 6 | A12-7 | photos-only for M1, M5; loss-weight controls for MADation | M1, M5, MADation R | 5 | UA8c, G-test, BENCH | PW-MAD photos-only breaks training (MAD22-5 52.4). Inception photos-only costs 10-12 points on StyleGAN; morphs do not repair it. MADation: morph images, not their loss weight, carry the G-test gain; checkpoint-dependent. | No | No | `A12-7_photos-share/README.md` |
| 7 | A36 held-out scoring of A12 rows (descriptive rows) | the A12 d0 and d1 networks, scored on H1, H2, H3, Arc2Face, FFHQ-Morphs | 7 methods, R and P recipes | 3-8 | AUC on H1 orig/pp, H2, H3 | **H1 orig, P x d0 to P x d1**: M1 0.552 to 0.700, M2 0.604 to 0.688, M3 0.699 to 0.859, M4 0.747 to 0.802, M5 0.458 to 0.623, M6 0.482 to 0.649, M8 0.614 to 0.689 (7 of 7 up; bytes floor 0.620). **H1 pp** (same processing both classes, floor 0.681): 6 of 7 up (M4 0.799 to 0.750 down). R x d0 to R x d1: +0.004 to +0.12. **H3**: P x d0 to P x d1 -0.02 to +0.03, all below 0.55. **H2**: 0.47-0.53 everywhere. FFHQ-Morphs: bytes floor 1.000, uninformative. | **Yes, the only unseen-source evidence**, but morph vs untouched host, not a twin | Partly: pp removes JPEG grid differences; blending smoothness (an attack property) remains | `A36_published-detector-shortcuts/raw/results/a36_read.md`; PROTOCOL l.10130 |
| 8 | A14 / A16 | E10 without SMDD bona fide (N); E10 on our data only, no SMDD image (D2) | MADMamba E10 | 6-10 | VALX-A\*, UA8c, G-test | N: VALX-A\* 7.21 vs 9.19, UA8c 36.6 vs 40.2, worse on own tools, 2x false alarms. D2: VALX-A\* 6.65 vs 8.71 (-2.06 [-3.21, -0.97]); G-test inverted (AUC 31.9; SMDD alone 64.4); 3x false alarms at fixed thresholds. | No (selection set, selection-seen GAN) | No: "a data-composition effect, not a better detector"; our data alone produce the G-test inversion | CONCLUSIONS l.17, l.83 |
| 9 | A30 GAN-protocol training | our 3,000 A28 GAN morphs, with (arm c) or without (arm g) a22n augmentation | CLIP LoRA, ConvNeXt, HRNet, MambaVision | 6 | G-test, H3, H4/H4b, FFHQM, FFHQ photos | GAN gains only on the selection-seen G-test and in-tool StyleGAN2. H3: every arm at or below chance on pp (best 0.489). No held-out "helps" confirmed; no network beats the bytes floors. Arm g raises false alarms on FFHQ camera photos by +13.9 / +16.4 points. Eye-geometry-only classifier on our GAN morphs: AUC 0.969. | No | **Adds a cue**: known alignment-geometry trace; render flag | `A30_gan-protocol-training-method/README.md` |
| 10 | A50 (P recipe, A/B/C) | B = + photos; C = B + classical morphs replacing 60% of SMDD-morph draws | M1, M2, M5, M6 | 5-8 | UA8c capped and uncapped, BENCH | C-B capped: M2 -2.11 [-3.46, -0.75], M6 -2.20 [-3.56, -0.83] (Holm p .028); M1 -1.19, M5 -0.80 (null). Uncapped worse on the point estimate in 3 of 4 (M1 +1.66, M2 +1.82, M5 +3.98); M2's Greedy-DiM 50.99 to 68.92. B-A capped -0.10 / -4.37 / -2.55 / -3.42. BENCH B to C in-tool 22.8 to 12.3 etc. All means 42-48%. | Weak, near floor; the cap hides inversions | No | `A50_RESULTS_20261108.md`; CONCLUSIONS l.377 |
| 11 | ABC60 | A / B / C, uniform sampler, no SBI, 10,060 updates, final checkpoint | ConvNeXt-T, VMamba-T, DeiT-S (all IN1k, full), DINOv3-L/16 (LayerNorm + head) | 5 paired (201-205) | Q (H2 + H3 orig), native17, E7 families, X3, H3_spread | Q C-A: CN +1.49, VM +2.45, DeiT -0.87, D3 +0.46, all CIs include 0. native17 C-A: -6.7, -12.4, +1.0, -6.2, all CIs include 0. **B-A worsens Q in 4 of 4** (+3.69, +5.80, +3.87, +1.47, CIs exclude 0; Section 2.2). Cell means 45.1-52.9%. 412 inverted and 152 near-constant family flags. | No on matched tests (floor) | Yes, derived (Section 2.2): history cue on diffusion moves with the bona fide composition | CONCLUSIONS l.385-470; analysis JSON (Section 2.2) |
| 12 | A49 | not a data arm: JS consistency loss on fixed C data | DINOv3 | 5 | processing instability, native17 | Joint criterion failed (+0.0029 [-0.0049, +0.0106]) | No | No | CONCLUSIONS l.371 |
| 13 | A47 I-3 (context, not extension) | morph-free net: SMDD renders vs their shrunk copies | M1, M3 | 3 | native DIFF cells, X3 | M3: MorDIFF 0.00, DiM 0.00-1.17 at last.pt; es.pt 2.46 / 14.54-20.41. M1 partial. Label-permuted control not at chance. | n/a | Shows the diffusion cells can be passed by history alone; any extension that leaves that history asymmetry in place can still pass them | `01_EVIDENCE_DOSSIER.md` rows 37, 112-117 |
| - | CG / CD / CGD (ABC generated arms) | + 3,000 A28 GAN; + 1,500 own DiffAE; both | the four ABC models | planned 5 | Q, native17 | **Never run.** D pool never built (`own_generation_v1` blocked, no outputs). The four registered CGD-C joint tests and two moderation tests are "unevaluable", not failed. | - | - | `primary120fit/SCOPE_CHANGE.md`; CONCLUSIONS l.411, l.469 |
| - | Narrow vs diverse pilot | 1,500 W+ vs 500 W+ / 500 MIPGAN-style / 500 DiffAE, same dyads | CN, VM | planned 301-305 | - | **Never run** (deferred last, no release). Note: it reserves seeds 301-305, the same seeds the new plan uses. | - | - | `NARROW_DIVERSE_PILOT_*/READINESS.md` |
| - | Research loop 11 Nov (DiffAE102, GAN32, Astra) | small own-generated sets for frozen heads | frozen heads | - | H3, spread controls | Apparent inner-ROI gain on H3 removed by spread-matched controls (0.461 / 0.467 vs 0.487 / 0.489). Generation counts only; no detector efficacy. | No | No mitigation shown | `research_loop_20261111/README.md` |

## 2. What is established, null, never tested

### 2.1 Established (within our pipeline; all exploratory unless noted)

1. **Our whole protocol repairs broken baselines on held-out FRLL diffusion, a little** (A12-BR, confirmatory for
   four CNNs): chance to 42-45% capped. For Inception-MAD and PW-MAD the data, not the recipe, carries it. This is the
   claim the author's ruling covers.
2. **Real photos carry the frozen-CLIP probe's diffusion gain** (A12-6: -5.39); our classical morphs add nothing
   detectable there. Our classical morphs carry MADation's StyleGAN G-test gain (-22.71), on a selection-seen generator.
3. **On the only unseen-source, source-matched landmark set (H1, CASIA, unseen tool), d1 raises AUC under our recipe
   in 7 of 7 methods** (+0.06 to +0.17, A36, descriptive rows, seed mean only). On the identically processed `pp`
   variant 6 of 7 rise and five P x d1 rows exceed the bytes floor (0.681). This is the best existing evidence that
   extension generalises, and it is not registered as a contrast.
4. **Extension does not help on any twin-type test.** H3: P x d1 vs P x d0 within -0.02 to +0.03, all below 0.55;
   H2 0.47-0.53 for all rows; ABC60 Q unchanged (C-A CIs include 0); A30 H3 at chance after our GAN morphs.
5. **Adding genuine photos makes networks rank single-identity renders as more morph-like** (ABC60 B-A on Q, 4 of 4
   architectures, CIs exclude 0; H3 orig B-A +1.35 to +8.13). Consistent with a new "camera photo = bona fide" cue,
   and with A30/A36 (render flags).
6. **Our GAN morphs add a known geometry cue** (eye-geometry-only AUC 0.969) and raise false alarms on camera photos.

### 2.2 New derived reading: extension moves the history cue (exploratory, post hoc, not registered)

Computed here from the frozen ABC60 analysis (`ABC60_FROZEN_ANALYSIS.json`, branch
`recovery/final-gpu-boundary-v1`, `family_metrics`), with the same paired five-seed t intervals (df 4) as the
registered reader. Check: the Q contrasts reproduce the registered ones exactly (CN C-A +1.490, VM +2.450,
DeiT -0.866, D3 +0.455). Scripts (session scratchpad, not in any repo):
`/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/abc_rise.py` and
`.../scratchpad/a12_rise.py`; rerun them before registering (X0).

E7 rise on the seven diffusion families (E7 EER minus native EER, mean over families, EER points):

| Arch | A | B | C | B-A [95% CI] | C-B [95% CI] | C-A [95% CI] |
|---|---|---|---|---|---|---|
| CN | 30.50 | 6.06 | 28.33 | -24.44 [-36.63, -12.26] | +22.28 [+12.17, +32.38] | -2.17 [-11.40, +7.07] |
| VM | 28.95 | 7.42 | 25.81 | -21.53 [-30.60, -12.46] | +18.39 [-5.92, +42.71] | -3.14 [-20.11, +13.84] |
| DeiT | 31.16 | 17.96 | 28.56 | -13.20 [-21.61, -4.78] | +10.59 [+3.67, +17.52] | -2.60 [-13.12, +7.92] |
| D3 | 44.97 | 16.22 | 24.77 | -28.75 [-41.38, -16.13] | +8.55 [-3.73, +20.82] | -20.21 [-32.44, -7.97] |

E7 rise on the seven landmark families: C-A -8.64 (CN), -8.65 (VM), -3.43 (DeiT), -7.58 (D3), all CIs exclude 0; most
of it is B-A in CN and VM. Absolute E7 diffusion EER: A 52-67%, B 29-46%, C 29-55% (D3 C best at 29.1%).

The same reading on the A12 R-recipe triplets (local score files `smadcvpr_runs/A12_scored/A12BR/`, R-es checkpoint,
uncapped, d0 / photos-only / d1): frozen-CLIP probe -0.2 / -3.2 / -0.5 (no history cue to remove); MADation R
-0.5 / -2.8 / +2.0 (at R-last 22.0 / 17.4 / 12.8); Inception R 48.6 / 42.7 / 40.5; PW-MAD photos-only failed
training. So the large photo effect is specific to the ABC sampler and recipe; it does not replicate in Inception's
own recipe.

What this means, carefully:
- Under the ABC recipe, the bona fide composition decides how much a network relies on resampling history. Real
  photos of mixed capture history in the bona fide class make "looks resampled" a weaker cue; classical morphs, which
  carry warp/blend/alignment history that the bona fide class lacks, re-create a history asymmetry.
- It is measured on the same 204 FRLL photos used for every other E7 reading, on already-seen families, five seeds.
- A smaller E7 rise with an unchanged Q (45-53%) is not a detector of morphing; it is a detector that uses a
  different cue. The C-A net change is null in three of four architectures.

### 2.3 Null (no detectable effect)

- ABC60: Q and native17 C-A in all four architectures.
- A50: incremental classical-morph effect for Inception-MAD and PW-MAD; uncapped harm not resolved either way.
- A8-W1F: R6 (more photos) and d1-real on the selection metric.
- A12-5: OrthoMAD data only; A12-6: MADation UA8c data gain; A12-4: M5 data-only label "neither".
- A30: no held-out confirmation of any GAN-morph gain.
- A49: consistency loss on the C data.

### 2.4 Never tested

1. **Any unseen-source test for the decomposition arms.** H1 was never scored on the ABC60 fits, the A50 fits or the
   A12 probe/MADation photos-only arms. So "photos vs morphs" is known only on FRLL-based sets.
2. **Landmark morph vs landmark twin.** No landmark twins exist (also listed in `04_HYPOTHESES.md` A2). H1's
   bona fide is the untouched host photo, so a network can pass H1 by detecting warp/blend/clone history.
3. **An E7-type control on a non-FRLL photo pool for extension arms.** A46 built FFHQ E7 pools but scored only
   released/A12 rows.
4. **Count-matched addition.** Every contrast (A50, ABC60, A12-6) replaces draws at fixed compute; none adds data
   at fixed SMDD exposure. "More data" and "different mix" are confounded.
5. **Generated-morph extension at scale** (CG/CD/CGD, narrow vs diverse); a morphs-only arm; any dose (how many
   photos or morphs).
6. **Matched vs unmatched extension at fixed count**: is it the matching (twins) or just more varied data?
7. **A fresh identity-leakage audit** of train90 against the newer held-out sets (A50/ABC60 inherited it).

### 2.5 Confounds that limit every reading above

- **Added data come from other pipelines than SMDD.** Photos: real FERET/FRGC captures (studio, own resolutions and
  codecs) next to synthetic SMDD bona fide. Classical morphs: warp + blend + alignment history that only the morph
  class has (A8 already flagged R8 for this). GAN morphs: eye-geometry trace. Each arm therefore adds new cues while
  it may weaken old ones; Section 2.2 shows this happening.
- **Replacement, not addition.** A50 replaces 60% of SMDD-morph draws; ABC B replaces synthetic bona draws. Exposure,
  class mass, repetition (A50 repeats each image three times) and BN state move together.
- **Near-floor endpoints.** Q 45-53%, UA8c 42-48%, H2/H3 0.45-0.55 AUC. Small differences there say little; capping
  at 50 hides inversions (A50 M2 Greedy-DiM 68.92).
- **One genuine-photo pool.** UA8c, native17, E7 and X3 all rest on 204 FRLL photos of 102 people.
- **Seen tests, chosen carriers.** All families were seen before the arms were designed; A50's four carriers were
  chosen after A12. VALX-A\* is built from the same FERET/FRGC sources as the added data, so it is in-distribution.
- **H1 is not a twin set.** Morphs are 3-5% smaller files (bytes floor 0.620); averaging two faces smooths texture.
  This is an attack property, but it is also what classical morphs in d1 carry, so H1 gains cannot separate
  "detects blending" from "detects our training morphs' processing".
- **Few seeds.** 3 (A8, early A12) to 5-8; SDs of 1-6 points; several 3-seed A12 effects shrank on fresh seeds.

## 3. Coverage check against `05_RESEARCH_PLAN.md`

| Dataset-extension question | Plan item that answers it | Covered? |
|---|---|---|
| Does data in which both classes share one pipeline (TwinSet) give a detector that responds to identity blending? | T4 (M1, M2), T6 (M6), G guards | Yes |
| Does twin-trained data cost benchmark accuracy, and does the E7 rise stop? | T4 + B (M5) | Partly: M5's reference is "the same backbone trained the usual way", but for frozen CLIP-L no "usual extension" (C-like) reference exists |
| Do released detectors fail on twins? | T1, T2 (A2, A3) | Yes for released weights; **not for our extension checkpoints** (ABC60, A12, A50) |
| Did our earlier, unmatched extension (photos, classical morphs) teach blending or a pipeline? | none | **No.** Needs our checkpoints scored on TwinSet and H1 twins (X1, X2 below) |
| Photos vs morphs on an unseen source | none | **No** (X1) |
| Is it matching or just more data, at fixed count? | none | **No** (X4) |
| Second genuine-photo pool for the E7 control | "Evidence still to add" item 3: FRGC, colorFERET | **Flawed**: FRGC/FERET photos and people are training data of every d1/B/C network and of TwinSet; use a pool never trained on (FFHQ via A46, Multi-PIE or CASIA) (X3) |
| Unseen-source test | TwinSet held-out tools and generators; identity-disjoint splits | **Partly**: TwinSet test shares its sources (FRGC, colorFERET, Multi-PIE, FRLL) with TwinSet training. No held-out source is reserved. |
| Benchmark contamination | B (MAD22, FRLL with/without E7) | **Risk**: FRLL is a TwinSet source; if FRLL people enter TwinSet training, FRLL benchmark numbers (FRLL-Morphs, DiM, MorDIFF, E7) are no longer held out. MAD22 bona fide are FRLL people too (CONCLUSIONS l.157). |
| CG / CD / CGD (registered, unevaluable) | not mentioned | **Open**: needs an explicit disposition |
| MADMamba under extension | T4 arm only | Covered as far as the plan intends |
| Seeds | 301-305 | Collides with the never-run narrow/diverse pilot's registered 301-305; harmless if that pilot is retired, but say so |

## 4. Proposal: minimum additional work

Basis for GPU estimates: ABC60 scoring used 5,672 single-GPU seconds for 2,651,400 scores (about 470 images per
second per H100 including start-up); ABC60 training was about 1.1 H100-hours per fit; A50 about 0.64. DGX GB10 is
assumed about one third of an H100 for inference.

### X0. Register what is already computed (0 GPU, about 2 hours CPU and writing)

- **What:** add three exploratory readouts to `PROTOCOL.md` before any new score exists: (a) the ABC60 E7-rise
  table (Section 2.2) for diffusion and landmark families; (b) the A12 R-triplet E7-rise table; (c) the A36 H1
  P x d0 vs P x d1 table as a paired contrast with the bytes and eye-geometry floors. Write the X1-X3 predictions
  next to them.
- **Data:** frozen ABC60 analysis JSON (branch `recovery/final-gpu-boundary-v1`), `smadcvpr_runs/A12_scored/A12BR/`
  (285 scored networks, eval and G-test, es and last), `experiments/A36_published-detector-shortcuts/raw/results/`.
- **Falsifier:** none (descriptive); it fixes the predictions that X1-X3 can falsify.

### X1. Re-score existing extension checkpoints on H1 and the twin sets (no training; about 0.5 H100-h)

- **Arms (reused networks):** ABC60 A/B/C x CN/VM/DeiT/D3 x 5 seeds (60); A12 frozen-CLIP probe d0 / photos-only /
  d1 (5/5/5); MADation R d0 / photos-only / d1 (8/5/8); Inception R and PW-MAD R triplets; A50 C (23 local) and, if
  copied from WCSS, A50 A/B (about 20).
- **Data (all on disk):** H1 orig and pp (`/mnt/t7/smad_heldout/h1_poisson`), Arc2Face (`arc2face`), A43 20-step
  DiffAE same-pair morphs vs twins (`a43`), and later the TwinSet test split. H2, H3, X3, X4 are already scored for
  ABC60 and need no rerun.
- **Metric:** AUC with pair-clustered bootstrap, EER, paired seed contrasts B-A, C-B, C-A; bytes and eye-geometry
  floors printed beside every cell.
- **Falsifiers (fixed before scoring):** "extension generalises to an unseen source" fails if C-A on H1 pp is below
  +0.02 AUC or its CI includes 0 in at least 3 of 4 ABC architectures, or if C is not above the 0.681 floor.
  "Photos carry it" vs "morphs carry it": the A12-6 outcome rule, applied to H1.
- **Prediction from A36:** C above A on H1 by +0.05 or more; B near A.
- **Cost:** about 150 networks x about 3,500 images = 0.5 M forwards, about 0.3-0.5 H100-h; about 1-2 h wall on the
  DGX for CN, DeiT, D3 and the A12/A50 CNNs. VMamba needs its selective-scan kernel: run the 15 VM fits on WCSS
  unless the Spark environment is verified for it.
- **Checkpoints on disk:** ABC60 `/mnt/t7/primaryABC60-analysis-inputs-20261110-v1/training/<task>/final.pt` (60, 23 GB);
  A12 `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/<run>/{es,last}.pt` (216 runs); A50 C
  `/mnt/t7/smad_heldout/a50/runs/A12BR/` (23). A50 A/B were not found locally (WCSS only).

### X2. Landmark twins on an unseen source (CPU build; about 0.2 H100-h to score)

- **What:** with the unchanged H1 build script, make self-morph twins for the H1 hosts: host photo warped and
  Poisson-blended with a **second photo of the same CASIA identity**, same mask, same `pp` chain for both classes,
  pose-matched as in the plan's G1. Output: H1 morph vs H1 twin (and twin vs untouched host as a pure
  "processing" control).
- **Arms:** the X1 network set, plus the plan's T1 released detectors and later T4 models.
- **Metric:** morph-vs-twin AUC, pair-clustered; twin-vs-host AUC.
- **Falsifier:** if C-A morph-vs-twin AUC is below +0.02 (CI includes 0) while C-A morph-vs-host AUC rises, our
  classical morphs taught warp/blend history, not two-identity blending. That is the decisive sentence for the
  "eliminating cue usage" half of the question.
- **Why here and not only in TwinSet:** CASIA was never used in training (no CASIA or Multi-PIE row in
  `train.csv`), so this is the only landmark twin test that is source-held-out for every network we own.
- **Data:** CASIA-WebFace at `/home/narolski/mambamorph/Datasety/downloads/CASIA-Webface`; H1 scripts and identity
  table in `/mnt/t7/smad_heldout/h1_poisson/{scripts,raw}`. CPU only, a few hours. No new processing code: the H1
  script and `prep_eval.align` are reused unchanged.

### X3. E7 control on a photo pool never used in training (no training; about 0.3 H100-h)

- **What:** score the X1 network set on the A46 FFHQ pools (FFHQ-Morphs diffae vs FFHQ bona fide, native and
  resolution-matched). If a studio pool is wanted, keep **Multi-PIE out of TwinSet training** and build its E7 copies
  with the existing registered E7 call (CPU).
- **Metric:** E7 rise per arm; B-A and C-B paired contrasts.
- **Falsifier:** the Section 2.2 reading ("photos reduce, classical morphs restore the history cue") fails on a new
  pool if B-A reduces the FFHQ diffusion E7 rise by less than 5 points, or its CI includes 0, in at least 3 of 4
  architectures.
- **Data:** `/mnt/t7/smad_heldout/ffhq_morphs/eval/ffhqm/{diffae,ffhq_bona,landmark_*,stylegan_*}` and the A46
  outputs under `/mnt/t7/smad_heldout/a46`. Native FFHQ-Morphs has a bytes floor of 1.000, so only the matched pool
  is a valid read. Multi-PIE raw: `/home/narolski/mambamorph/Datasety/downloads/multipie`.

### X4. Matched vs unmatched extension at fixed count, inside T4 (new training, frozen heads; about 1 H100-h)

- **Arms (one backbone, the plan's frozen CLIP ViT-L/14 + head; seeds 301-305):** (i) C data (SMDD + photos +
  classical morphs: the unmatched extension); (ii) C + TwinSet, with twins as bona fide; (iii) TwinSet only. Equal
  updates and equal morph draws in (i) and (ii); same head and schedule as T4.
- **Metric:** held-out-tool twin AUC (landmark, GAN, DiffAE), H1 and H1-twin AUC (X2), E7 rise on FRLL and FFHQ,
  MAD22 and FRLL EER.
- **Falsifier:** if (ii) - (i) twin AUC is below +0.05 and the E7 rise is not at least halved, matching adds nothing
  over plain extension, and the paper cannot say "the data, not the loss" for the matched design.
- **Cost:** CLIP-L features for C (64,363 images) and TwinSet (about 50,000) once, about 0.3-0.5 H100-h equivalent on
  the DGX; heads take minutes. An optional LoRA version (3 arms x 5 seeds) is about 15 H100-h and should run only if
  the head version shows a difference.
- **Data:** C pool from the A49 train90 C lineage (64,363 unique rows; `smadcvpr_data/manifests/train.csv`); TwinSet
  from D1-D4.

### X5. Guards (0 GPU)

- **Identity and source split for TwinSet:** no FRGC/FERET person from train90 in any TwinSet test split; no FRLL
  person in TwinSet training if FRLL or MAD22 benchmark numbers are reported (B); reserve one source (Multi-PIE or
  CASIA) as never-trained.
- **Copy the A28 GAN pool off `/tmp`:** the 3,000 GAN morphs and their canonical copies live under
  `/tmp/opencode/gan_protocol/final` and `/tmp/opencode/own-generation-GAN-canonical256-v1`; a reboot loses them.
  (Requires the author's yes for the T7 folder, per standing rule.)
- **Seeds:** declare that the narrow/diverse pilot is retired before reusing 301-305.

### X6. Disposition of CG / CD / CGD (decision; 0 or about 11 H100-h)

- **Recommendation:** retire as registered and record them as "superseded, not run". Reasons: Q sits at 45-53%,
  so the CGD-C Q-superiority test has almost no room; the G pool carries a known geometry trace (0.969); the D pool
  does not exist; A30 already showed our GAN morphs do not move H3. Their scientific question (does generated-morph
  extension help on matched tests) is answered better by TwinSet's GAN and DiffAE families, which carry their own
  twins.
- **If the author wants the registered answer anyway:** CG only, CN and D3, 5 seeds (10 fits, about 11 H100-h),
  scored on the ABC60 contract plus X1-X3 sets. Falsifier: CG-C Q change within +-1 point and H3/X4 unchanged means
  generated-morph extension adds nothing on matched tests.

## 5. Ranking by information per GPU-hour

| Rank | Item | GPU (H100-h) | What it decides |
|---|---|---|---|
| 1 | X0 register derived readouts and predictions | 0 | Turns two unregistered findings (ABC E7-rise shift, A36 H1 gain) into testable predictions |
| 2 | X5 guards (splits, held-out source, /tmp copy, seeds) | 0 | Keeps TwinSet and benchmark numbers interpretable |
| 3 | X1 re-score ABC60 / A12 / A50 on H1 and twin sets | 0.3-0.5 | Photos vs morphs on an unseen source; extension vs twins for networks we already have |
| 4 | X3 E7 on FFHQ (and Multi-PIE) pools | 0.3 | Whether the history-cue shift is general beyond the 204 FRLL photos |
| 5 | X2 CASIA landmark twins | 0.2 (+ CPU build) | Whether classical-morph extension taught blending or processing |
| 6 | X4 matched vs unmatched at fixed count (frozen heads) | about 1 (LoRA +15 optional) | Whether matching, not more data, is what helps |
| 7 | X6 CG only, if wanted | about 11 | The registered generated-arm question, mostly already answered by A30 |

Total for ranks 1-6: about 2 H100-hours plus CPU builds, almost all of it re-scoring checkpoints that are already on
`/mnt/t7`.
