# Evidence dossier: do existing S-MAD methods score well because of benchmark cues?

Prepared 2026-11-11 for Paweł Narolski. Read-only compilation; no number was computed here.

**The claim under test.** "Existing S-MAD methods score well on regular (landmark), GAN and diffusion morphs because of cues available in the benchmark data (bona fide photo resolution/processing history, generator-vs-camera construction, rendering settings, file construction), not because they detect the morphing signal (two blended identities)."

**Short verdict.** The logged evidence supports a narrower claim than this one. It is strong for diffusion morphs on specific networks, an absence result for GAN morphs, and mostly descriptive (with counter-evidence) for regular morphs. `CONCLUSIONS.md` explicitly drops the general sentence "Published S-MAD detectors rely on shortcuts" and "for every method" (drop list, l.214-215).

**Path abbreviations** (all under `/home/narolski/mambamorph-code/` unless absolute):
- **C** = `experiments/CONCLUSIONS.md`
- **P** = `smadcvpr/PROTOCOL.md` (line numbers as of 2026-11-11)
- **R/** = `smadcvpr/results/`
- **S1** = `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/methods_table_final.md`
- **S2** = `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/shortcut_per_method_final.md`

**Verification marks.** "[primary]" = I opened the result file or the PROTOCOL / CONCLUSIONS text for this number in this session. "[via S1/S2]" = taken from the earlier verified summaries (7 Nov), primary file not re-opened today. Nothing below comes from `fst*`, `manifests/valx.csv`, A12SP, MADMamba, W3 or E10 files.

**Terms.** E7 = the same genuine photos shrunk to the morphs' median face size before the same alignment. X3 = published morphs against DiffAE reconstructions of genuine photos (no morphing). H3 = StyleGAN3 two-person morphs against single-person renders of the same generator. X4 = the same morphs against renders matched to the morphs' latent spread. M1 = Inception-MAD recipe, M3 = MADation ViT-B/16 recipe (our SMDD-only retrains). EER in %, AUC 0-1. Brackets are person-clustered 95% intervals unless marked.

---

## 1. One-page summary

**What the evidence shows, in plain words.**

- **Diffusion morphs: the best-supported part.** Two official releases and two re-implemented recipes lose most of their FRLL diffusion-morph performance when only the genuine photos' processing history is changed. A network that never saw a morph reaches near-zero error on the same cells. One release's "morph vs reconstruction" separation disappears when the reconstructions are rendered with the published step count.
- **GAN morphs: an absence, not a shown shortcut.** No analysed detector ranks StyleGAN3 morphs above single-person StyleGAN3 renders by a useful margin, and the GAN benchmarks compare generator PNGs with camera JPEGs. No causal test on the MIPGAN benchmark cells has run.
- **Regular morphs: mostly descriptive, with counter-evidence.** Several detectors fall under E7, and a morph-free network solves some landmark cells. But four rows hold under E7 and score above the file-size floor on a controlled landmark set, so "not because they detect the morphing signal" is not supported for them.
- **Benchmark construction: shown.** File attributes alone separate the classes in every registered cell.

**The strongest numbers.**

| # | Number | Meaning | ID | Source |
|---|---|---|---|---|
| 1 | EER 8.4 → 90.7 (+82.4 [77.3, 87.4]) | SelfMAD release, FRLL Greedy-DiM, native vs E7 photos; ranking reverses. Claim C1, grade "strong (final)" | A32, A41 | C l.182 [primary] |
| 2 | EER 6.4 → 87.2 | Same release on the raw files with its own crop; published regime reproduces (6.4 vs 7.6). Descriptive | A41 amendment G (X7') | C l.182 [primary] |
| 3 | EER 0.00 on MorDIFF, 0.00-1.17 on six DiM families | M3 network trained on SMDD renders vs their shrunk copies; never saw a morph; last checkpoint, 3 seeds. Other checkpoint: 2.46 / 14.54-20.41 | A47 I-3 (H-new-331) | R/A47/a47_read.md [primary] |
| 4 | AUC 0.833 [0.766, 0.896] → 0.487 [0.381, 0.594] | MADation ViT-B/16 release: published MorDIFF morphs vs one-identity reconstructions at 100 vs 20 decoding steps | A43 (R0, R0m) | R/A43/a43_read.md [primary] |
| 5 | AUC 0.505 [0.473, 0.539] | Same release: published MorDIFF morphs vs our same-pair 20-step morphs (label "absent") | A43 (R1m) | R/A43/a43_read.md [primary] |
| 6 | EER 4.44 [2.35, 6.52] vs 34.68 | 8 M3 retrains at the last checkpoint reach the release's MorDIFF regime (4.9); the selected checkpoint sits at 34.68. Their E7 rise is +11.39 [8.00, 14.78] | A44 amendment 1 (R-last), A44 m4c | P l.19973 [primary]; experiments/A44_madation-mechanism/meta.json [primary] |
| 7 | EER 6.39 → 29.51 (+23.12 [18.93, 29.39]) and 6.93 → 29.41 (+22.47 [18.11, 27.37]) | MADation ViT-B/16 release, DiM-C and Greedy-DiM-S (C2b). N1, N2 met post hoc; the N3 refuter fired (0.724, 0.745) | A46 d0, d1 | P l.19870, l.20275 [primary] |
| 8 | EER 9.36 → 60.79 (+51.4 [45.2, 58.5]), one network; 4 of 4 / 5 of 5 / 4 of 4 eligible networks | M1 Inception recipe on Greedy-DiM / Greedy-DiM-S / DiM-C under E7 (H-new-315 supported) | A46 d0 | R/A46/a46_d0.md [primary] |
| 9 | No row at AUC ≥ 0.65; 15 row-cells at 0.35-0.45; X4 0.42-0.52 | 12 published-method rows (51 networks), StyleGAN3 morphs vs renders. Claim C3, "strong (narrow)" | A36, A37, A41 | C l.184 [primary] |
| 10 | O = 1.000 per decision cell | File attributes alone separate classes in 10 cells (15,518 files). Claim B | A41 (H-new-155) | R/A41/a41_files.md [primary] |
| 11 | Δ 0.00 [-3.15, 3.41] | Counter-example: MADation ViT-L/14 release on Greedy-DiM does not move under E7 | A41 F4 (iii) | S2 l.99 [via S2] |
| 12 | MAD22-5 32.72 vs 10.53; 40.91 vs 9.42 | Our SMDD retrains of Inception-MAD and MorphHRNet do not reproduce the published numbers | A45 | R/A45/a45_read.md [primary] |

**Status of the three newest experiments** (details in section 2.4):
- **A45: read** on 2026-11-08 13:28 CET. All five available arms fail the reproduction gate.
- **A46: read** on 2026-11-08 (00:18 and 14:30 CET). Part of it is suspended for a crop defect.
- **A47: read** on 2026-11-08 14:16 CET and independently reviewed (accept-qualified). It has **no results bullet in PROTOCOL.md** and is not in the CONCLUSIONS claims section; its ledger still says "running".

---

## 2. Evidence by morph type

### 2.1 Regular (landmark) morphs

No landmark cell has a registered shortcut grade (S2 l.123). Every E7 fall below is descriptive unless marked.

| Detector (release or re-implementation, #networks) | Benchmark → controlled | Control | CI | Registered verdict / grade | ID | Source |
|---|---|---|---|---|---|---|
| SelfMAD release, own crop (official, 1) | AMSL 2.9 → 33.3; WebMorph 5.9 → 51.9; FaceMorpher 0.4 → 4.8; OpenCV 0.1 → 3.9 | E7 | FM 4.8 [1.95, 7.34]; OCV 3.9 [1.41, 5.85]; none for AMSL, WM | Not tested under a registered rule | A32, A41 S3 | S1 l.108, l.143 [via S1] |
| SelfMAD release (official, 1) | MAD22 FaceMorpher 0.0 → 0.11 | E7 | [0.00, 0.89] | A41 F4 (i) supported: morphs stay detected (counter-evidence) | A41 | S1 l.145 [via S1] |
| MADation ViT-B/16 release (official, 1) | 2.8/2.9/15.1/4.9 → 4.4/4.4/28.9/10.8 (FM/OCV/AMSL/WM) | E7 | FM 4.42 [2.12, 6.93] | Descriptive; FM cell is F4 (ii) supported | A36, A41 | S1 l.109 [via S1] |
| MADation ViT-L/14 release (official, 1) | 1.0/1.0/17.7/4.9 → 1.0/1.0/14.7/4.4 | E7 | none | Descriptive: holds (counter-evidence) | A36 | S1 l.110 [via S1] |
| M1 Inception-MAD (ours, 5) | MAD22 FaceMorpher 6.4 → 39.0; FRLL families inverted natively (53.6/53.6) | E7 | seed means, no person CI | Descriptive; reproduction falsified | A12-BR, A12.4 | S1 l.117 [via S1] |
| M1 Inception-MAD (ours, 5) | OpenCV-tool morphs 3.3% from MAD22 1351-px files vs 53.6% from FRLL 431-px files | Same tool, different file size | none | Descriptive | A12-BR | S2 l.106 [via S2] |
| M5 PW-MAD (ours, 8) | WebMorph 4.2 → 14.3; AMSL 8.9 → 25.7; MAD22 FM 1.2 → 20.7 | E7 | seed means, SD up to ±17 | Descriptive; reproduction falsified | A12-BR | S1 l.122 [via S1] |
| M3 MADation recipe ViT-B/16 (ours, 8) | 3.3/5.7/10.8/8.6 → 3.6/5.8/11.4/8.8 | E7 | seed means | Descriptive: holds (counter-evidence) | A12-BR | S1 l.119 [via S1] |
| M3L MADation recipe ViT-L/14 (ours, 5) | 0.4/0.3/15.0/7.8 → 0.4/0.3/14.5/7.6 | E7 | seed means | Descriptive: holds (counter-evidence) | A12-BR | S1 l.120 [via S1] |
| Morph-free M3 (ours, 3 seeds, last.pt) | MAD22 FaceMorpher 0.00; FRLL facemorpher 2.62 [1.28, 3.78]; webmorph 0.65; amsl 0.82. But MAD22 OpenCV 31.35, Webmorph 23.64, FRLL opencv 18.66 | Trained without any morph (renders vs shrunk copies) | as printed | Per-cell label "solvable by processing history alone" on 5 landmark cells; "not solvable" / "indeterminate" on 3 | A47 I-3 | R/A47/a47_read.md [primary] |
| Morph-free M1 (ours, 3 seeds, last.pt) | MAD22 FaceMorpher 2.14 [0.73, 3.50]; other landmark cells 14.85-29.17 | Same | as printed | "solvable" on 1 cell; others "indeterminate" | A47 I-3 | R/A47/a47_read.md [primary] |
| Controlled Poisson set H1 (clean landmark test) | AUC: SelfMAD 0.872 (point), M3L 0.833, M3 0.805, ViT-B/16 0.770, ViT-L/14 0.718; file-size floor 0.620 | Both classes same source, size, border | pair 90% only | Registered label "above the floor" for ViT-B/16, ViT-L/14, M3, M3L (no grade). M1, M2, M5, M6, M8, M8O "not above" | A36 amendment 1 | S1 l.108-125, l.146-156 [via S1] |

**Reading.** Landmark results of the CNN recipes and the SelfMAD release move with photo size. The CLIP-based rows hold under E7 and are above the floor on the clean set, which is evidence that they do read a landmark-morph signal. E7 leaves alignment borders in place, and border fraction alone separates several families at AUC 0.99-1.00 (`experiments/E07_shortcut_controls/README.md` l.70 [primary]).

### 2.2 GAN morphs

| Detector (#networks) | Benchmark → controlled | Control | CI | Registered verdict / grade | ID | Source |
|---|---|---|---|---|---|---|
| 12 primary rows, 51 networks (ViT-B/16 and ViT-L/14 releases, SelfMAD release, M1-M8O) | Benchmark MIPGAN-I EER, e.g. M3L 0.8, M3 7.0, SelfMAD 0.5 → H3 AUC 0.35-0.59 | Both classes from StyleGAN3 | one-sided pair and seed bounds | **C3 "strong (narrow)"**: no primary row at AUC ≥ 0.65; 15 row-cells rank renders higher (0.35-0.45) | A36, A41 | C l.184 [primary]; S1 l.108-125 [via S1] |
| Same 12 rows | X4 AUC 0.42-0.52; 11 of 12 with upper bound below 0.5 | Renders matched to the morphs' latent spread | pair 95% | Part of C3 | A37, A41 amendment G | C l.184 [primary] |
| M3 recipe (ours, 8) | MIPGAN-I EER 7.0 vs H3 0.448 (reversed); renders vs camera AUC 0.951 / 0.956 / 0.967 (FRLL / FFHQ / FEI) | Renders vs camera photos | none | H-new-83 "neither" (FRLL pool registered; others descriptive) | A36 amendment 1 | S2 l.108 [via S2] |
| M3L recipe (ours, 5) | MIPGAN-I 0.8; H3 0.401 (reversed); H4b 0.923 vs file-size floor 0.912 | StyleGAN v1 morphs vs host renders | Bonferroni lower bound -0.031 | Not above the floor | A36 | S2 l.109 [via S2] |
| M3 R-last (ours, 8) | H3 orig AUC 0.5295 [0.5124, 0.5467]; pp 0.4827 | H3 | seed 95% | H-new-307 "absence" | A44 amendment 1 | P l.19973 [primary] |
| MixFaceNet-MAD release (official, 1) | X4 orig AUC 0.446 [0.419, 0.472] | X4 | pair | H-new-324 supported descriptively; not a primary C3 row | A46 | P l.20275 [primary] |
| Morph-free M3 (ours, 3 seeds, last.pt) | MIPGAN-I 75.51; MIPGAN-II 73.01; FRLL StyleGAN 27.47 | Trained without any morph | as printed | "not solvable at this dose" (MIPGAN). The shrink cue does not explain GAN cells | A47 I-3 | R/A47/a47_read.md [primary] |
| Frozen CLIP ViT-B/16 with fixed head | Render vs camera AUC 0.922 (person lower bound 0.903) | Fixed-head ladder | person | Descriptive H-new-282: "pretraining supplies render-ness"; independent review of this read pending | A44 M3 follow-up | P l.20250 [primary] |
| MAD22 MIPGAN-I/II, FRLL StyleGAN, G-test | "These sets compare generator output (PNG) with camera photos (JPEG)" | File construction | n/a | **C4 "construction sentence"**. No row reads a storage-format cue (H-new-142) | A41 | C l.186 [primary] |
| Published-recipe networks vs our protocol | Our protocol lowers H3 AUC in 14 of 14 method x data cells (-0.008 to -0.197) | H3 | none | Post hoc | A36, A38 | experiments/A36_published-detector-shortcuts/meta.json [primary] |

**Reading.** The GAN benchmark numbers are not evidence of morph detection. That detectors *use* the generator-vs-camera difference on MIPGAN is not shown: the causal test (X6) has not run, and H3 / X4 have little power against a two-identity signal (A39 P, H-new-101: the H3 separation carries over to spread-matched renders; `experiments/A39_batch-before-window-close/meta.json` [primary]).

### 2.3 Diffusion morphs

| Detector (#networks) | Benchmark → controlled | Control | CI | Registered verdict / grade | ID | Source |
|---|---|---|---|---|---|---|
| SelfMAD release, own crop (official, 1) | Greedy-DiM 8.4 → 90.7; MorDIFF 2.5 → 61.3 | E7 | +82.4 [77.3, 87.4]; +58.8 [54.2, 64.6] | **C1 "strong (final)"**. Earlier registered test (A32 H1): "neither" | A32, A41 | C l.182 [primary] |
| SelfMAD release, raw files | Greedy-DiM 6.4 → 87.2 (published 7.6) | E7 on raw files, three kernels | 6.39 [3.35, 9.42] native | N4 met; reversal descriptive | A41 amendment G, G2 | C l.182 [primary]; S2 l.97 [via S2] |
| SelfMAD release | X3 AUC: reconstructions above MorDIFF morphs 0.33 [0.28, 0.37]; resampled-only photos 0.09 | X3 | person | F3 supported; N3 not met (positive control 0.636 ≤ 0.65) | A41 amendment G | C l.182 [primary] |
| MADation ViT-B/16 release (official, 1) | MorDIFF 4.9 → 19.6 | E7, five crops | +14.7 [10.3, 18.9]; d' share 0.463 | **C2 "descriptive row (final)"**; tier 2 not reached (p10 0.0170 > 0.00833) | A36, A41 | C l.183 [primary]; S2 l.98 [via S2] |
| MADation ViT-B/16 release | Published MorDIFF vs reconstructions: 0.833 (100 steps) → 0.487 (20 steps); vs same-pair 20-step morphs 0.505 | Decoding step count matched to published pixels | [0.766, 0.896]; [0.381, 0.594]; [0.473, 0.539] | Registered cell "shortcut (processing history: the decoding step count) shown for MorDIFF". Two- vs one-identity 20-step morphs 0.706 [0.625, 0.785] "undetermined" | A43 | R/A43/a43_read.md [primary] |
| MADation ViT-B/16 release | DiM-C 6.39 → 29.51; Greedy-DiM-S 6.93 → 29.41 | E7 | +23.12 [18.93, 29.39]; +22.47 [18.11, 27.37]; d' share 0.671 / 0.628 | C2b: "N1, N2 met (post hoc registration, outcome forecast)". Then H-new-313 falsified: N3 refuters fired, DiM-C 0.724 [0.664, 0.780], Greedy-DiM-S 0.745 [0.684, 0.804]; label "identity evidence or a file / frame property: open" | A46 d0, d1 | P l.19870, l.20275, l.20293 [primary] |
| MADation ViT-B/16 release, own-crop RGB acquisition | MorDIFF native 0.99 (published 1.10) → +12.72 points (area kernel) | E7 | none | Descriptive only; `published_reproduction_admitted=false` | A46_RGB_ONLY_20261108 | experiments/A46_diffusion-register-raw-files/RGB_ONLY_RESULTS_20261108.md l.113, l.149 [primary] |
| MADation ViT-B/16 release | Photo-only logit rises +1.45 at dose 3.30; Spearman 1.0 over six rungs | Dose ladder on 185 genuine photos | Page p < 1e-6 | F5 / H-new-274 supported (dose response) | A44 | experiments/A44_madation-mechanism/meta.json [primary] |
| MADation ViT-L/14 release (official, 1) | Greedy-DiM 9.8 → 9.8 | E7 | Δ 0.00 [-3.15, 3.41] | F4 (iii) supported: negative control (counter-evidence) | A41 | S2 l.99 [via S2] |
| M3 recipe at last checkpoint (ours, 8) | MorDIFF 4.44 (release 4.9) vs 34.68 ± 3.47 at the selected checkpoint | Training length | [2.35, 6.52] | Regime gate holds | A44 amendment 1 | P l.19973 [primary] |
| M3 R-last (ours, 8) | E7 rise +11.39; MorDIFF vs reconstructions 0.476 with native 0.989 | E7; X3 | [8.00, 14.78]; [0.386, 0.566] | H-new-306 "present"; H-new-305 "refuted" (no release-like separation). Review: accept-qualified | A44 amendment 1 | P l.19973 [primary]; experiments/INDEPENDENT_REVIEW_A44R_A45_20261108.md [primary] |
| M1 Inception recipe (ours, 5) | Greedy-DiM e.g. 9.36 → 60.79; 4 of 4 / 5 of 5 / 4 of 4 eligible networks meet N1 + N2 | E7, ViT-L/14 as negative control | +51.4 [45.2, 58.5] (one network) | H-new-315 supported: "our re-implementation of the Inception-MAD recipe carries its DiM results on the cue". Recipe did not reproduce the published numbers | A46 d0 | R/A46/a46_d0.md [primary] |
| M3 / M3L recipes (ours, 8 / 5) | "Not robust" 0 everywhere; UA8c 12.6 → 12.1 | E7 | seed means | H-new-314 supported: robust (counter-evidence) | A46 d0 | P l.19870 [primary] |
| Morph-free M3 (ours, 3 seeds) | MorDIFF 0.00; DiM 0.00-1.17 (last.pt). es.pt: 2.46; 14.54-20.41 | Trained on SMDD renders vs shrunk copies; no morph seen | [0.00, 0.00] to [0.18, 2.15] | **H-new-331 M3 "held"** at the registered checkpoint; sensitivity "partial (DIFFERS)" | A47 I-3 | R/A47/a47_read.md [primary] |
| Morph-free M1 (ours, 3 seeds) | MorDIFF 14.88; DiM 11.75-44.80 (last.pt) | Same | as printed | H-new-331 M1 "partial" | A47 I-3 | R/A47/a47_read.md [primary] |
| Morph-free M3 | Reconstructions vs aligner-only copies AUC 0.951 [0.933, 0.967] (last); 0.777 (es) | X3 | person | H-new-333 M3 "held"; M1 "falsified" (0.635) | A47 I-3 | R/A47/a47_read.md [primary] |
| M1 with class-symmetric augmentation (ours, 3 seeds) | E7 rise 48.53 → 5.24 (89% removed); native EER +52.45 [47.00, 58.20] on diffusion cells; +13.05 on the landmark specificity cell | I-1 augmentation | as printed | H-new-332 M1 "augmentation costs accuracy generally"; "the shortcut was the performance" **not established** | A47 I-1 | R/A47/a47_read.md [primary] |
| M3 with class-symmetric augmentation | Reference rise only 0.49 | I-1 | n/a | H-new-332 M3 "not applicable" | A47 I-1 | R/A47/a47_read.md [primary] |
| Label-permuted M1, M3 (ours, 2 seeds) | 6 of 17 and 11 of 17 cells off chance | I-4 | n/a | H-new-330 "not chance-level": the negative control is not interpretable | A47 I-4 | R/A47/a47_read.md [primary] |
| MixFaceNet-MAD release (official, 1) | MorDIFF 5.89 → 47.04 (+41.14 [34.64, 46.86]) | E7, MTCNN crop | person | **Suspended** (crop defect; 853 retained MorDIFF edge strips). RGB-only redo: 8.91 → +20.54 points, descriptive | A46 a2; A46_RGB_ONLY | C l.342-366 [primary]; RGB_ONLY_RESULTS_20261108.md l.113, l.149 [primary] |
| FFHQ-based check, 13 rows | No row is "general beyond FRLL" (ViT-B/16 36.38 → 51.10 "neither") | E7 on FFHQ photos | image bootstrap | H-new-322 not supported | A46 ffhqm | P l.19870 [primary] |

### 2.4 A45 / A46 / A47: were they read after 8 Nov?

All three were read on 8 Nov. Nothing new on them has been read since (9-11 Nov work is ABC60, MAD22 canonical input, A49, A50 and the 11 Nov research loop).

| Experiment | Read? | When | Review | Where integrated | Outcome |
|---|---|---|---|---|---|
| A45 reproduction retrains | Yes | 2026-11-08 13:28 CET (P l.19991) | "Corrections required" (JSON exposes control p-values after a failed gate; exclude them) | PROTOCOL only. Ledger README still says "None (not run)" | All five available arms fail. Inception retrain MAD22-5 32.72 vs 10.53; HRNet-W18 40.91 vs 9.42; W48 comparator 34.93 vs 9.42. FD-MAD global arms partial and non-comparable; full FD-MAD has no scores |
| A46 zero-GPU parts (d0, l1, ffhqm, i2, register, d2) | Yes | 2026-11-08 00:18 CET (P l.19870) | Independent review 14:44: corrections required | PROTOCOL, CONCLUSIONS l.335-366 | C2b N1+N2 met; H-new-315 supported; H-new-314 supported; H-new-320 falsified; H-new-322 not supported; D2 oracle H-new-317 supported |
| A46 remaining parts (d1, a2, d6, register_raw, X4) | Yes | 2026-11-08 14:30 CET (P l.20275) | Same review; then crop-validity suspension 14:57; corrective study blocked 15:25; RGB-only redo accepted-qualified 16:19 | PROTOCOL, CONCLUSIONS | H-new-313 falsified (both N3 refuters fired). MTCNN-branch results (raw register, A2, D6 kernel) suspended. H-new-310 support and H-new-323 falsification withdrawn |
| A47 training interventions | Yes | 2026-11-08 14:16 CET (commit e97e143; `experiments/A47_training-interventions/raw/a47_read_completed.log`) | Independent review 14:18: accept-qualified (`experiments/INDEPENDENT_REVIEW_A47_20261108.md`) | **Not in PROTOCOL** (last A47 entry is the copy-back at l.19995). Not in the CONCLUSIONS claims section (only the registration paragraph, l.298). Ledger meta "running" | I-3 M3 "held", M1 "partial"; I-1 M1 "augmentation costs accuracy generally", M3 "not applicable"; I-4 "not chance-level" for both (uninterpretable); H-new-333 M3 "held", M1 "falsified" |

A44 part 1 and amendment 1 (R-last) were read on 2026-11-07 23:22 and 2026-11-08 13:00 CET. The later A44 follow-up reads (M2, M3, M5, family; 14:23-14:26 CET) still await an independent review (P l.20245-20270).

---

## 3. Benchmark-construction evidence (claims B and C4, cue-only floors)

| Finding | Number | Grade / status | ID | Source |
|---|---|---|---|---|
| Documented file attributes alone separate the classes | O = 1.000 per decision cell, 10 cells (7 FRLL diffusion, MAD22 MIPGAN-I/II, MAD22 FaceMorpher); 15,518 files | **B: meets its registered criterion** (H-new-155 supported). Files listed, not hashed | A41 | R/A41/a41_files.md [primary]; C l.185 |
| Which attributes | Diffusion and MIPGAN cells: container, width, bytes per pixel, inter-eye distance. MAD22 FaceMorpher: width, bytes per pixel, inter-eye distance | Confirmed = documented | A41 | R/A41/a41_files.md [primary] |
| FRLL landmark families | Width, height and JPEG quality each at O = 1.000 for amsl, facemorpher, opencv, webmorph | Printed, not registered decision cells | A41 | R/A41/a41_files.md [primary] |
| MAD22 OpenCV / Webmorph | Mostly not separable by these attributes (Webmorph w 0.500, bpp 0.798) | Printed | A41 | R/A41/a41_files.md [primary] |
| GAN sets | Generator PNG against camera JPEG | **C4: construction sentence** | A41 | C l.186 [primary] |
| Border fraction alone | AUC 0.99-1.00 on several evaluation families | Descriptive | E07 | experiments/E07_shortcut_controls/README.md l.70 [primary] |
| X3 Greedy-DiM vs reconstructions | File bytes alone 0.987-0.998 (floor-limited) | Print-only floor | A41 amendment G | S1 l.195 [via S1] |
| H4b | File size alone 0.912 | Floor | A34, A36 | S1 l.76 [via S1] |
| H1 | File size alone 0.620 (orig), 0.681 (pp) | Floor | A27, A36 amendment 1 | S1 l.70 [via S1] |
| H3 | Bytes 0.526; eye geometry 0.560; combined 0.607-0.617 | Floor | A36, A41 | S1 l.172 [via S1] |
| Cue-only network | A network trained only on "render vs shrunk copy" reaches 0.00-1.17 on seven diffusion cells (M3, last.pt) | H-new-331 M3 "held"; not yet in PROTOCOL | A47 I-3 | R/A47/a47_read.md [primary] |
| Missing benchmark files | 185 + 4,069 of 204 + 4,483 MAD22 files held | Qualification on every MAD22 number | A46 register R-g | P l.19870 [primary] |

Claims B and C4 show that a shortcut is possible. They do not show that any detector uses one (C l.185-186). CONCLUSIONS also drops "any cue-floor sentence from A41's frame cues" (drop list).

---

## 4. What the evidence does NOT show

1. **No claim reached the top registered grade.** C1 is "strong (final)", not "meets registered criteria N1-N4": its reconstruction test's positive control failed (0.636 ≤ 0.65) and a border or alignment artefact of the control pool is not formally excluded (C l.182; S2 l.43-48).
2. **C2 is a descriptive row, not a shortcut.** The ViT-B/16 release's rise removes less than half of the separation, and a registered refuter fired. Allowed wording: "identity blending is not needed to explain it and is not separately shown" (C l.183). Never "MADation carries the shortcut".
3. **C3 is a narrow absence.** One generator (StyleGAN3). Not "does not separate", not "blind to identity", nothing causal (C l.184).
4. **The cue is not identified.** C1's cue word is "bona fide processing history; cue not identified". "Resolution", "aliasing", "interpolation trace" are forbidden words (C l.211). The claim's list of four named cues goes beyond this.
5. **"Not because they detect the morphing signal" is not shown.** No test here has demonstrated power to detect identity mixing together with a detector failing it. In A43 the two- vs one-identity contrast is "undetermined" (0.706). In A46 the two B/16 refuters leave "identity evidence or a file / frame property: open". The D2 oracle shows identity information is present in the contrast (H-new-317), but image-only probes do not read it (H-new-318 falsified).
6. **Counter-examples exist.** The ViT-L/14 release does not move on Greedy-DiM; the M3 / M3L recipes are robust under E7 (H-new-314); four rows are above the H1 floor on clean landmark morphs; SelfMAD keeps detecting MAD22 FaceMorpher under E7.
7. **CNN methods were not reproduced.** A45: all arms fail the gate; A12-BR reproduction (TOST) falsified for M1, M2, M4, M5, M6, M8; the official MixFaceNet code did not reproduce (35.78 / 67.59 vs 13.69 / 8.96). So no sentence about Inception-MAD, MorphHRNet, PW-MAD, OrthoMAD, MixFaceNet-MAD or FD-MAD as published methods follows. The MixFaceNet raw-file reproduction (H-new-310) was withdrawn.
8. **One network per release.** C1 and C2 each concern a single checkpoint. Nothing is shown about the SelfMAD or MADation *methods*.
9. **FRLL-only scope.** Every decision cell sits on the same 204 FRLL photos of 102 persons; crop and kernel re-runs are not replications. On FFHQ photos no row was "general beyond FRLL" (A46 ffhqm).
10. **Post hoc rules.** A41's rules were written after earlier estimates had been seen; the earlier registered tests said "neither" (A32 H1, A36 H-new-75, H-new-72). A43, A46 C2b and A42 are post hoc with outcomes partly forecast.
11. **A47 is checkpoint-sensitive and narrowly scoped.** M3 "held" at last.pt becomes "partial" at es.pt. The label-permuted control failed its chance gate, so the pool question stays open. The review limits the reading to: "morph training is not necessary to attain those results in this setup"; it does not show which feature released networks use.
12. **"The shortcut was the performance" is not established.** A47 I-1: the augmentation also costs +13.05 points on the landmark specificity cell (M1) and is not applicable for M3.
13. **Suspended or withdrawn A46 parts.** Raw-register MTCNN cells, A2 (including MixFaceNet MorDIFF 5.89 → 47.04) and the D6 kernel interpretation are suspended for the crop defect. The RGB-only numbers are descriptive without intervals.
14. **MAD22 is incomplete.** 185 + 4,069 of 204 + 4,483 files; the corrected full run (canonical164) was cancelled and has not run (C l.447-500).
15. **MADMamba is sealed.** "MADMamba not evaluated on H3 (sealed)". Nothing here says our method avoids these cues; our own networks show the same history (E07 10.53 → 32.63%; C l.232).
16. **A49 / A50 / ABC60 (9-11 Nov) add no support.** They test mitigation, and none demonstrates removal of processing shortcuts (C l.371-470).

---

## 5. Gaps to close for a CVPR-publishable claim, ranked

1. **Narrow the claim sentence to what is graded.** As worded it is on the paper's own drop list. A defensible version: "On FRLL-based diffusion benchmarks, the analysed releases' and recipes' numbers follow the genuine photos' processing history and how the images were rendered; a network that never saw a morph reaches the same regime; on GAN benchmarks no analysed detector ranks morphs above same-generator renders." Regular morphs need separate, weaker wording.
2. **Register A47 properly and replicate I-3.** Add the PROTOCOL results bullet, adopt the review, update the ledger and CONCLUSIONS. Then replicate with more seeds and a checkpoint rule fixed in advance (last vs es flips the M3 verdict), and repair or replace the failed label-permuted control.
3. **A second bona fide pool and fresh persons (X8).** Everything decisive sits on 204 FRLL photos. Reviewers will ask for a non-FRLL studio pool under rules fixed before the data are seen.
4. **A working identity positive control (N3).** A same-generator test where a known identity-sensitive detector clears its bar, so that "does not detect two blended identities" becomes testable. Expression-matched one-identity morphs (A43 R2x, not run) belong here.
5. **A morph-free arm for the GAN cue and the causal C4 test (X6).** Train "render vs camera" without morphs and score MIPGAN-I/II; replace the camera bona fide by same-generator output on the benchmark cells. Today the GAN part is an absence only.
6. **Reproduce the CNN methods or drop them.** Obtain the authors' checkpoints, or reach the published regime with their selection procedure. Complete the paired corrective crop evaluation (blocked on one mis-detected native photo) to restore a valid MixFaceNet raw-file row.
7. **More than one network per release.** A second checkpoint or seed retrains at the published regime, as A44 R-last did for MADation (8 networks). For SelfMAD, the retrain without the interpolated zoom (H-new-242) would also test the mechanism note.
8. **A registered rule for regular morphs with a border-matched control**, with person-clustered intervals for the SelfMAD AMSL / WebMorph and recipe collapses.
9. **Run on the complete MAD22** (204 + 4,483); canonical164 production has not run.
10. **Close open reviews and housekeeping.** Independent review of the A44 follow-up reads; exclude A45's exposed p-values; hash the 15,518 files behind claim B; update the stale A45 / A46 / A47 ledger entries.
11. **Identify the cue, or keep saying it is not identified.** A43 names one (decoding step count, one network, MorDIFF). For C1 nothing is identified; the border test could not be evaluated.

---

## 6. Not verified in this session

- The full PROTOCOL bullets of A32, A36 (+ amendments), A37 (+ reproduction amendment, H101), A38, A39, A40, A41 (+ G, G2) and A42 (+ amendment 1) were not re-read line by line. Their numbers come from CONCLUSIONS (final claims section), the ledger `meta.json` headlines and S1 / S2. Rows marked [via S1/S2] carry that status.
- The A47 results were read from `smadcvpr/results/A47/a47_read.md`; its sha256 prefix (e78ffb97...) and the JSON's (7ec70c69...) match the independent review. There is no PROTOCOL results bullet to cross-check against.
- The 34.68 ± 3.47 selected-checkpoint MorDIFF value is from the A44 ledger `meta.json` headline (m4c), not from `a44_m4c.md` directly.
- The A46 d0 per-network Inception numbers are from one network's entry in `a46_d0.md`; the seed-level summary was taken from the PROTOCOL bullet.
- `experiments/research_loop_20261111/` (11 Nov) was only skimmed at README level; its findings concern mitigation and are not used as evidence here.
