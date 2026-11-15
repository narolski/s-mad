# Diffusion-morph column: how each competing method does once the shortcuts are removed

Gathered 2026-11-07 from logged outputs only (no new computation). **MADMamba is not in this table** (sealed; not evaluated on these controls). No W3, E10 or FST number is used. The authority for grades and wording is the final section of `/home/narolski/mambamorph-code/experiments/CONCLUSIONS.md`, "What we can claim about shortcuts" (section 4 below).

## 0. Conventions

- **EER** = equal error rate in %, at the equal-error threshold of each comparison. Labelled "thresholded (EER)". 50 = chance. **Above 50 = inverted**: the method rates the genuine photos as more morph-like than the morphs.
- **AUC** = threshold-free ranking. 0.5 = chance. Below 0.5 = the control images rank above the morphs.
- **Flag rate / BPCER** = thresholded at a stated threshold.
- **Native** = the benchmark as shipped. The morphs are compared with the original high-resolution FRLL photos (204 photos, 102 persons; 185 for the MAD22 copies).
- **Release** = the authors' official weights. **Retrain** = our re-implementation of the published recipe in our pipeline. "R x d0" means recipe R trained on SMDD only (d0), as in SYN-MAD 2022. "P x d1" means our protocol trained on our data.
- Releases are scored on our 512-px eye-aligned frames unless a row says "own preprocessing" (the SelfMAD release's own dlib crop and resize) or "raw files" (the release's own `crop.py` on the raw benchmark files).
- **Status labels.** "registered" = a pre-specified rule decided the number. For A41 these are rules on previously observed estimates, exploratory and post-freeze; the amendment G/G2 values were blind. "descriptive" = printed by a registered reader, but no rule decides it. "post hoc" = written after the numbers were seen. "confirmatory" = A12's multiplicity-adjusted family.
- **CIs.**
  - A41 / A42: person-clustered dyadic bootstrap 95%, B = 10,000, over the 102 FRLL persons.
  - A36 RSX: image bootstrap 95%, B = 2,000.
  - Retrains: mean ± SD over seeds (A12.4 JSON), or mean ± t95 half-width over seeds (A36 tables).
  - A12-BR confirmatory: 95% CI.

## 1. The controls used for diffusion morphs

| Control | What it takes away | Where |
|---|---|---|
| **B: construction table** | Shows that the shortcut exists. In all 7 FRLL diffusion cells (DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S, MorDIFF), morph and genuine files differ in container, width, bits per pixel and face size, and each attribute alone separates the classes (O = 1.000). Registered (H-new-155 supported); 15,518 files listed, not hashed. | `smadcvpr/results/A41/a41_files.md` |
| **E7 (resolution-matched genuine photos)** | Each genuine FRLL photo is downsampled (INTER_AREA) to the morph family's median face size, then framed the same way. Only the genuine side changes. | A32 RSX, A36 H-new-75, A41 S2, A12.4 |
| **Raw-file E7 + kernel ladder (S12 (a), A41 G2)** | The same downsampling on the raw benchmark files, read through SelfMAD's own `crop.py` (no 512 frames, no warped border). Three kernels: OpenCV INTER_AREA, PIL bicubic, PIL Lanczos. | `a41g_s12.json`, `a41g2_s12k.json` |
| **Dose ladder (S7)** | The same 185 FRLL photos downsampled by 1.0x to 3.3x. AUC compares each copy with its original; 0.5 = the method ignores downsampling. | `a41_eval.json` S7 |
| **resample50 morphs (S12 (b))** | The morphs themselves are halved (INTER_AREA) and scaled back (bilinear). Does resampling make a morph look more or less morph-like? | `a41g_s12.md` |
| **X3 (generator-matched genuine photos)** | Genuine FRLL photos are put through the morphs' generator family (DiffAE) without any identity mixing:<br>• **rec**: DiffAE encode/decode reconstructions (204)<br>• **a256**: only DiffAE's 256-px aligner, i.e. resampled<br>• **self**: DiffAE "morphs" of a person's neutral and smiling photo, one identity (102)<br>A = AUC of the published morphs against that pool. Identity evidence would need A well above 0.5. | `a41g_x3.md/.json` |
| **X14b crops** | ViT-B/16 MorDIFF native vs E7 in five crop windows of the same frames. | `a41g_x14b.md` |
| **S8 cue-matched MorDIFF** | The E7 MorDIFF EER on a subset matched for face geometry and file bytes. | `a41_eval.json` H-new-137 |
| **A42 border matching** | The X3 MorDIFF-vs-rec AUC with the frames' zero-filled border area matched. | `smadcvpr/results/A42/a42_border.md` |
| **Same-generator diffusion renders (A36 (C))** | **H2**: IP-Adapter-FaceID SD1.5 embedding-midpoint morphs vs single-identity renders from the same generator (992 + 992).<br>**Arc2Face**: 548 + 548, both classes generated.<br>Simple-cue floors: bytes 0.522 / eye geometry 0.518 (H2); 0.514 / 0.509 (Arc2Face). | `smadcvpr/results/A36/a36_read_own.md` (C) |
| **Cross-source: FFHQ-Morphs DiffAE** | FFHQ DiffAE morphs vs FFHQ photos downsampled to the morphs' face size (E7 resmatch pool). The bytes-only floor is **1.000**, so file size alone separates the classes here: cue-confounded. | A36 (C) column FFHQM/diffae |

## 2. Summary table: one row per method, diffusion morphs

Native and controlled numbers sit side by side. "Plain words" follows the CONCLUSIONS wording rules.

| Method (networks; training data) | Native benchmark | Once shortcuts are removed | What it means in plain words | Backing | Status, source |
|---|---|---|---|---|---|
| **SelfMAD release**, HRNet-W18, own preprocessing (official checkpoint, SMDD-based self-morph training) | EER: Greedy-DiM 8.37, MorDIFF 2.53, DiM-A 3.86, Fast-DiM 5.84, Fast-DiM-ODE 13.13, DiM-C 1.98, Greedy-DiM-S 1.98. Raw files with its own crop: Greedy-DiM 6.39 [3.35, 9.42] (published 7.60), DiM-A 4.41, MorDIFF 1.49. | **E7 (frames):**<br>• Greedy-DiM 90.74, Δ +82.38 [77.32, 87.35]<br>• MorDIFF 61.29, Δ +58.76 [54.15, 64.55]<br>• DiM-A 66.19<br>• Fast-DiM 77.08<br>• Fast-DiM-ODE 88.31<br>• DiM-C 43.17<br>• Greedy-DiM-S 33.81<br>AUC drops from 0.94-1.00 to 0.03-0.70.<br>**Raw-file E7 (own crop):** Greedy-DiM 87.23 (Δ +80.84 [75.97, 85.70]), DiM-A 69.50, MorDIFF 45.20. With PIL kernels the rise is larger (Greedy-DiM +86.78 / +85.25).<br>**X3 A:**<br>• rec: 0.024 / 0.234 / 0.330 [0.284, 0.374] (Greedy-DiM / DiM-A / MorDIFF)<br>• a256: 0.004 / 0.075 / 0.092<br>• self: 0.018 / 0.113 / 0.212<br>**Same-generator renders:** H2 0.510, Arc2Face 0.510.<br>**FFHQ DiffAE (E7):** 0.382. | Its near-perfect diffusion numbers depend on how the genuine photos were processed. Once genuine photos are merely shrunk to the morphs' face size, it rates them as **more morph-like than real Greedy-DiM morphs**: the ranking reverses. The same happens on the raw files with its own crop, and with three shrinking kernels (descriptive). It also ranks DiffAE reconstructions of genuine photos, and photos that were only resampled, above the published morphs. Same-person DiffAE "morphs" also rank above them. So the reversal already starts at the resampling step. No identity-mixing evidence. Cue: "bona fide processing history; cue not identified". | 1 network | C1 **"strong" (final)**. Registered: A41 F1 / F2 (Holm, p < 1e-4), F3 (X3, blind, supported), X7′ reproduction. Descriptive: S12 (a) and the kernels. Post hoc: FFHQ.<br>`a41_eval.json` S2.cells; `a41g_x3.md`; `a41g_s12.json` detail.a; `a41g2_s12k.json`; `a41g_x7.md`; A36 (C) |
| **SelfMAD release, our pipeline** (same checkpoint on our 512 frames) | Greedy-DiM 29.41, MorDIFF 6.49, DiM-A 15.64, Fast-DiM 17.18 | **E7:** Greedy-DiM 89.11 (Δ +59.70 [52.55, 65.31]), MorDIFF 61.29 (Δ +54.80 [48.48, 59.87]), DiM-A 73.02.<br>**X3 rec:** 0.018 / 0.104 / 0.256.<br>**Same-generator renders:** H2 0.537, Arc2Face 0.499. | Same picture as with its own preprocessing: shrunk or reconstructed genuine photos look more morph-like to it than diffusion morphs. | 1 network | Descriptive. `a41_eval.json` S2.cells; `a41g_x3.md` |
| **MADation official ViT-B/16** (authors' LoRA weights) | MorDIFF 4.90 (published 1.10; reproduction check S met within 5 points). DiM-C 6.39, Greedy-DiM-S 6.93, Fast-DiM 16.09, DiM-A 20.59, Fast-DiM-ODE 25.92. Greedy-DiM 53.96: **not reproduced**, already at chance. | **E7:**<br>• MorDIFF 19.60, Δ +14.70 [10.32, 18.92]; d′ share 0.46, so less than half the separation is removed<br>• DiM-C 29.51<br>• Greedy-DiM-S 29.41<br>• Fast-DiM 51.44<br>• DiM-A 56.39<br>• Fast-DiM-ODE 57.88<br>• Greedy-DiM 84.90<br>**MorDIFF rise in the five crops:** +13.22 to +21.04. Cue-matched E7 MorDIFF: 21.18 (+1.58 [−2.87, 7.61]).<br>**X3 A:**<br>• MorDIFF: rec **0.847 [0.803, 0.891]**, border-matched 0.844 [0.787, 0.895]; a256 0.911; self 0.942 (cue floor 0.956)<br>• DiM-A: rec 0.361<br>• Greedy-DiM: rec 0.024<br>**Same-generator renders:** H2 0.497, Arc2Face 0.485.<br>**FFHQ DiffAE:** 0.505. | Against shrunk genuine photos its MorDIFF error rises from 5% to 20%, in every crop. It still keeps more than half the separation. It also tells the published MorDIFF morphs from DiffAE reconstructions of genuine photos (0.85, above the 0.60 cue floor). The rules count that **against** a shortcut. But on DiM-A and Greedy-DiM it ranks the reconstructions above the morphs. Whether the MorDIFF separation is identity evidence or a property of the MorDIFF files or frames is **open**. Cue word: "fine-detail softness". | 1 network | C2 **"descriptive row" (final)**; the registered refuter F7 fired. Registered: F5 (tier 1), F6 crops. Descriptive / post hoc: A42 border matching. A36 H-new-75: "neither".<br>`a41_eval.json` S2.cells; `a41g_x14b.md`; `a41g_x3.md`; `a42_border.md` |
| **MADation official ViT-L/14** (used as the detector that ignores downsampling) | Greedy-DiM 9.80, Greedy-DiM-S 8.81, Fast-DiM-ODE 15.21, DiM-C 16.19, DiM-A 22.03, Fast-DiM 22.57, MorDIFF 28.91 (published 19.26: not reproduced) | **E7:** Greedy-DiM 9.80 (Δ 0.00 [−3.15, 3.41]); DiM-A 16.73 (−5.30); Fast-DiM 18.61 (−3.96 [−7.55, −0.25]); MorDIFF 39.65 (**+10.74 [7.22, 14.19]**).<br>**Dose ladder:** AUC 0.494 → 0.455 (ignores downsampling).<br>**X3 A:**<br>• Greedy-DiM: rec 0.749 (cue floor 0.993), a256 0.843, self 0.386<br>• DiM-A: rec 0.550, self 0.268<br>• MorDIFF: rec 0.610, self 0.501<br>**Same-generator renders:** H2 0.466, Arc2Face 0.491.<br>**FFHQ DiffAE:** 0.544. | Its DiM detection does not depend on how the genuine photos were processed. It is modest and unchanged against shrunk photos. Against DiffAE reconstructions it separates less well, and it ranks same-person DiffAE "morphs" above published Greedy-DiM morphs, so no identity evidence is shown. Its MorDIFF rise under E7 shows that the MorDIFF control pool is **not specific**: 47% of that pool's difference from the native photos sits in the warped border. | 1 network | Negative control: registered A41 F4 (iii), supported; S7 "none". MorDIFF cell descriptive.<br>`a41_eval.json` S2.cells, S7; `a41g_x3.md` |
| **MADation official FE ViT-L/14** (frozen encoder + head; registered X3 positive control) | DiM 11.78-22.03, MorDIFF 34.80 (published 22.85: not reproduced) | **E7:** DiM +1.98 to +5.94 (e.g. Greedy-DiM 22.03 → 27.97, Δ +5.94 [3.12, 9.03]); MorDIFF 32.38 (−2.43).<br>**X3 rec:** **0.636 [0.579, 0.693]** (Greedy-DiM), 0.772 (DiM-A), 0.742 (MorDIFF).<br>**X3 self:** 0.312 / 0.489 / 0.522.<br>**Same-generator renders:** H2 0.502, Arc2Face 0.493.<br>**FFHQ DiffAE:** 0.838. | Barely affected by shrinking the photos. It separates the morphs from reconstructions on DiM-A and MorDIFF, but as the registered positive control it failed on Greedy-DiM (≤ 0.65). So X3 cannot show that the reconstruction test could detect identity mixing at all ("assay sensitivity not shown"). | 1 network | Descriptive row, with a registered gate role in X3 (it caps C1 at "strong").<br>`a41_eval.json` S2.cells; `a41g_x3.md` |
| **MADation official FE ViT-B/16** | DiM 21.0-47.0, MorDIFF 39.7 (published 17.86) | **E7:** DiM 41.6-73.6 (+20.6 to +29.0), MorDIFF 53.5 (+13.8).<br>No X3.<br>**Same-generator renders:** H2 0.498, Arc2Face 0.482.<br>**FFHQ DiffAE:** 0.690. | Weak on diffusion natively and near or above chance against shrunk photos. | 1 network | Descriptive, no CI. `a36_read_own.md` "RSX: MADation official" and (C) |
| **MADation official FS ViT-B/16** (from scratch) | DiM 16.1-24.0; MorDIFF 67.6 (inverted; published 28.14) | **E7:** DiM 41.6-45.6 (+21.6 to +26.0); MorDIFF 62.2.<br>**Same-generator renders:** H2 0.476, Arc2Face 0.539.<br>**FFHQ DiffAE:** 0.458. | Its moderate native DiM numbers fall to near chance once the photos are shrunk. MorDIFF is inverted either way. | 1 network | Descriptive, no CI. Same source |
| **MADation official FS ViT-L/14** | DiM 38.1-47.0; MorDIFF 43.0 (published 40.92) | **E7:** DiM 40.2-49.0 (+1.5 to +4.0); MorDIFF 42.1.<br>**Same-generator renders:** H2 0.502, Arc2Face 0.511. | Near chance with or without the control. | 1 network | Descriptive. Same source |
| **MixFaceNet-MAD release** (official SMDD weights; outside its input domain on our frames) | DiM 27.1-50.1; MorDIFF 27.5; UA8c native 39.39 | **E7:** DiM 43.6-66.7 (+16.5 to +18.6); MorDIFF 40.1 (+12.6); UA8c (capped) 47.67.<br>At its own native 5% threshold it flags 36.7% / 21.6% of the DiM / MorDIFF E7 photo pools (review-derived, post hoc).<br>**Same-generator renders:** H2 0.536, Arc2Face 0.486.<br>**FFHQ DiffAE:** 0.670. | Weak natively and near chance against shrunk photos, like most SMDD-trained rows. Numbers only: the A41 drop list forbids a "resolution" sentence for this release. | 1 network | Descriptive. A36 amendment 2; H-new-97 (registered) "neither".<br>`a36_a2.md` "RSX, UA8c and MAD22" and "held-out comparisons" |
| **M1 Inception-MAD** retrain R x d0 | Greedy-DiM 9.0±1.6, Greedy-DiM-S 5.5±0.5, DiM-C 8.1±2.5, DiM-A 13.4±2.4, MorDIFF 20.0±7.4; UA8 (uncapped mean) 14.4±2.4; UA8c native 14.40 ± 2.97 (t95) | **E7:** Greedy-DiM 60.7±5.7, DiM-A 70.9±4.1, Fast-DiM-ODE 79.5±3.1, MorDIFF 51.2±3.8; UA8 63.0±4.1; **UA8c 49.38 ± 1.36**.<br>No X3.<br>**Same-generator renders:** H2 0.534 ± 0.006, Arc2Face 0.485.<br>**FFHQ DiffAE:** 0.687. | Its fair native diffusion numbers do not survive. Against shrunk genuine photos it rates them as more morph-like than the morphs in most families (inverted). With our data and protocol it moves from chance to slightly better than chance. | 5 seeds | Descriptive (A12.4; the native "orig" pool is an eval-pipeline diagnostic). P x d1 UA8c 44.88: Δ −4.50 [−6.33, −2.67], **confirmatory**.<br>`a12_4_read_stage1.json` arms["M1:r:d0"]; `a36_a2.md` UA8c table; A12-BR README |
| **M2 MorphHRNet-style** retrain R x d0 | UA8 45.6±10.7 (Greedy-DiM 49.4, MorDIFF 30.0); UA8c native 41.67 | **E7:** UA8 66.4±10.6 (Greedy-DiM 71.7, MorDIFF 43.0); **UA8c 48.50 ± 1.62**.<br>**Same-generator renders:** H2 0.532, Arc2Face 0.492.<br>**FFHQ DiffAE:** 0.720. | Near chance natively; inverted against shrunk photos. | 5 seeds | Descriptive. P x d1 42.05: Δ −6.45 [−8.12, −4.78], confirmatory. Same sources |
| **M3 MADation ViT-B/16 recipe** retrain R x d0 | DiM-A 7.0±2.0, DiM-C 5.4, Fast-DiM 4.7, Greedy-DiM-S 4.2, Fast-DiM-ODE 8.3, Greedy-DiM 23.2±6.4, MorDIFF 35.1±3.6; UA8 12.6±2.2 | **E7:** DiM-A 7.3±3.0, Greedy-DiM 24.5±6.5, MorDIFF 28.6±2.7; UA8 12.1±2.8; **UA8c 12.08 ± 2.33** (95% [9.69, 14.46]). At the native 5% threshold it flags 5.7% / 2.2% of the DiM / MorDIFF E7 photos (native 5.4).<br>No X3.<br>**Same-generator renders:** **H2 0.483 ± 0.003**, Arc2Face 0.485.<br>**FFHQ DiffAE:** 0.815 (bytes floor 1.000). | The only retrained recipe whose DiM detection survives shrinking the photos: its numbers barely move. It is the best held-out recipe in the study, on DiM, not on MorDIFF (29%). Caveats: this is its VALX-A\*-selected checkpoint (the last checkpoint gives 25.4), it was never tested against generator reconstructions, and it is at chance on morph vs single-person renders of other diffusion generators (H2, Arc2Face). Our protocol makes it worse. | 8 seeds | Descriptive (A12.4 / A32 RSX: A32 H1 "neither", because it never reaches a low native MorDIFF / Greedy-DiM EER). H-full +30.68 [+28.17, +33.20] in favour of the published recipe, confirmatory.<br>`a12_4_read_stage1.json` arms["M3:r:d0"]; `rsx_read.md`; A12-BR README |
| **M3L MADation ViT-L/14 recipe** retrain R x d0 | DiM-A 5.6, Greedy-DiM 24.3, MorDIFF 45.7; UA8 17.7±1.9 | **E7:** DiM-A 5.0, Greedy-DiM 22.4, MorDIFF 41.5 (chance); **UA8c 16.11 ± 2.60**.<br>**Same-generator renders:** H2 0.474, Arc2Face 0.505.<br>**FFHQ DiffAE:** 0.724. | Like M3: unaffected by E7 on DiM, chance on MorDIFF and on same-generator renders. | 5 seeds | Descriptive. Same sources |
| **M4 SelfMAD-style** retrain R x d0b (HRNet-W18 IN-1k, SBI-int, SAM) | **100.0** in all 7 families (fully inverted: it rates the original high-resolution photos as more morph-like than every morph); UA8c native 50 (capped) | **E7:** 21.5±6.1 (Greedy-DiM-S) to 60.1±13.3 (MorDIFF); UA8 49.3±12.0; **UA8c 42.77 ± 5.85**.<br>**Same-generator renders:** H2 0.475, Arc2Face 0.495.<br>**FFHQ DiffAE:** 0.444. | Reads the photos' processing history in the opposite direction from the SelfMAD release. Once the photos are shrunk it is near chance. | 5 seeds | Descriptive (outside the confirmatory family). Same sources |
| **M5 PW-MAD** retrain R x d0 | Greedy-DiM 33.6±11.2, Greedy-DiM-S 8.2, MorDIFF 42.8±23.2; UA8 29.0±9.8; UA8c native 27.98 | **E7:** Greedy-DiM 83.3±5.6, DiM-A 82.5, MorDIFF 49.2; UA8 72.3±4.7; **UA8c 49.54 ± 0.52**.<br>**Same-generator renders:** H2 0.491, Arc2Face 0.511.<br>**FFHQ DiffAE:** 0.643. | Moderate natively, strongly inverted against shrunk photos. | 8 seeds | Descriptive. P x d1 44.75: Δ −4.79 [−6.00, −3.58], confirmatory. Same sources |
| **M6 OrthoMAD** retrain R x d0 | UA8 37.0±4.1 (Greedy-DiM 38.2, MorDIFF 32.7); UA8c native 36.80 | **E7:** UA8 60.9±1.7 (Greedy-DiM 64.8, MorDIFF 47.7); **UA8c 48.22 ± 1.26**.<br>**Same-generator renders:** H2 0.525, Arc2Face 0.492.<br>**FFHQ DiffAE:** 0.703. | Weak natively; inverted against shrunk photos. | 5 seeds | Descriptive. P x d1 42.92: Δ −5.31 [−7.03, −3.58], confirmatory. Same sources |
| **M8 MixFaceNet-MAD** retrain R x d0 | UA8 28.1±7.9 (Greedy-DiM 30.7, MorDIFF 15.6); UA8c native 28.05 | **E7:** UA8 63.8±5.5 (Greedy-DiM 69.0, MorDIFF 44.5); **UA8c 48.89 ± 1.22**.<br>**Same-generator renders:** H2 0.533, Arc2Face 0.491.<br>**FFHQ DiffAE:** 0.659. | Moderate natively; inverted or at chance against shrunk photos. | 5 seeds | Descriptive (Tier 2, outside the confirmatory family). Same sources |
| **M8O MixFaceNet-MAD official training code** retrain O x d0 | UA8 36.9±4.5 (Greedy-DiM 38.9, MorDIFF 24.2); UA8c native 36.30 | **E7:** UA8 66.0±6.7 (Greedy-DiM 71.7; MorDIFF 44.7, Δ +20.41 ± 6.78 t95); **UA8c 48.97 ± 0.61**. At the native 5% threshold it flags 57.3% / 33.8% of the DiM / MorDIFF E7 photos.<br>**Same-generator renders:** H2 0.534, Arc2Face 0.486. | As M8: inverted or at chance once the photos are shrunk. | 5 seeds | Descriptive. Same sources + `rsx_read.md` |
| Extra: **frozen CLIP ViT-B/16 + linear head** (MADation backbone, head only; A12.4 arm a124lp, d0) | UA8 15.4 (Greedy-DiM 18.9, MorDIFF 37.0) | **E7:** UA8 15.2 (Greedy-DiM 22.0, MorDIFF 30.8). On our data (a125lp, d1): UA8c 10.71 [9.18, 12.25]. | Unaffected by shrinking the photos, like the MADation recipe. Not tested on reconstructions or renders. | 5 seeds | Descriptive. H-new-J (registered, d1) supported, exploratory.<br>`a12_4_read_stage2.json` arms["M3:a124lp:d0"]; A12-5 README |

**Reading across rows (diffusion only):**
- **The native FRLL diffusion benchmark carries a construction shortcut.** Morph and genuine files differ in container, size and face size, and each separates the classes perfectly (claim B).
- **Once only the genuine photos' processing history is matched (E7), three patterns appear:**
  - **The SelfMAD release reverses.** Shrunk genuine photos rate as more morph-like than the morphs (C1, the one "strong" claim).
  - **Every SMDD-trained CNN recipe is at chance or inverted** on held-out diffusion (UA8c 42.8-49.5). Several looked fair natively (M1 Greedy-DiM 9%).
  - **Some CLIP-based rows hold.** The MADation recipe retrains (M3, M3L), the frozen-CLIP head and the ViT-L/14 / FE ViT-L/14 releases change little under E7. Not all CLIP rows hold: the official ViT-B/16 loses part of its MorDIFF separation (C2, a descriptive row), and the FE / FS ViT-B/16 releases rise +20 to +29 on DiM.
- **Once genuine photos have been through the morphs' generator family (X3, releases only), no release shows identity-mixing evidence:**
  - **SelfMAD** ranks reconstructions, resampled photos and same-person DiffAE "morphs" above the published morphs.
  - **ViT-B/16** separates the published MorDIFF morphs from reconstructions (0.85), but ranks reconstructions above DiM-A and Greedy-DiM morphs.
  - **FE ViT-L/14**, the positive control, failed its gate on Greedy-DiM, so X3 could not have shown identity detection at all.
- **On morph vs single-identity renders of other diffusion generators** (H2, Arc2Face), all 18 rows (12 primary + 6 descriptive) sit at 0.466-0.539: chance, at the simple-cue floors.

## 3. Detail tables (all logged numbers; sources per table)

### 3a. Releases, FRLL diffusion families, native → E7 EER (our 512 frames; SelfMAD row = its own preprocessing)

Source: `/home/narolski/mambamorph-code/smadcvpr/results/A41/a41_eval.json`, key `S2.cells["<row> | dim/<family>"]` and `["<row> | mordiff/mordiff"]`, fields `native`, `e7`, `delta`, `delta_ci95`, `auc_native`, `auc_e7`. Person-clustered 95%, B = 10,000.

**Status:**
- **Registered decision cells:** F1 (SelfMAD own, Greedy-DiM), F2 (SelfMAD own, MorDIFF), F5 (ViT-B/16, MorDIFF) and F4 (iii) (ViT-L/14, Greedy-DiM).
- **Every other cell** is a descriptive print of the same registered reader.
- **Same numbers elsewhere.** A32 RSX `smadcvpr/results/RSX/rsx_read.md` (A32 H1 registered: "neither") and A36 `a36_read_own.md` "RSX: MADation official" (H-new-75 registered: "neither"; image-bootstrap 95% on ViT-B/16 MorDIFF: [+11.2, +18.0]).

| Row | DiM-A | DiM-C | Fast-DiM | Fast-DiM-ODE | Greedy-DiM | Greedy-DiM-S | MorDIFF |
|---|---|---|---|---|---|---|---|
| SelfMAD own | 3.86 → 66.19 (+62.33 [57.26, 67.71]) | 1.98 → 43.17 | 5.84 → 77.08 | 13.13 → 88.31 | **8.37 → 90.74 (+82.38 [77.32, 87.35])** | 1.98 → 33.81 | **2.53 → 61.29 (+58.76 [54.15, 64.55])** |
| SelfMAD our pipeline | 15.64 → 73.02 | 3.96 → 41.73 | 17.18 → 70.69 | 31.76 → 86.32 | 29.41 → 89.11 | 3.96 → 37.23 | 6.49 → 61.29 |
| MADation ViT-B/16 | 20.59 → 56.39 | 6.39 → 29.51 | 16.09 → 51.44 | 25.92 → 57.88 | 53.96 → 84.90 | 6.93 → 29.41 | **4.90 → 19.60 (+14.70 [10.32, 18.92])** |
| MADation ViT-L/14 | 22.03 → 16.73 | 16.19 → 14.21 | 22.57 → 18.61 | 15.21 → 13.68 | **9.80 → 9.80 (0.00 [−3.15, 3.41])** | 8.81 → 8.81 | 28.91 → 39.65 (+10.74 [7.22, 14.19]) |
| MADation FE ViT-L/14 | 14.75 → 19.50 | 17.18 → 22.03 | 20.59 → 25.99 | 15.66 → 19.08 | 22.03 → 27.97 | 11.78 → 13.76 | 34.80 → 32.38 |

AUC native → E7 (same keys):

| Row | DiM-A | Greedy-DiM | MorDIFF |
|---|---|---|---|
| SelfMAD own | 0.990 → 0.256 | 0.959 → 0.027 | 0.993 → 0.321 |
| SelfMAD our pipeline | 0.922 → 0.190 | 0.750 → 0.040 | 0.977 → 0.362 |
| ViT-B/16 | 0.872 → 0.438 | 0.458 → 0.064 | 0.987 → 0.885 |
| ViT-L/14 | 0.863 → 0.885 | 0.947 → 0.939 | 0.803 → 0.682 |
| FE ViT-L/14 | 0.929 → 0.897 | 0.860 → 0.805 | 0.699 → 0.736 |

The d′ share removed (registered rule) is SelfMAD Greedy-DiM 2.110, MorDIFF 1.188 and ViT-B/16 MorDIFF 0.463, so ViT-B/16 is below the 0.5 needed for "shortcut-carried". Tier 2 for ViT-B/16 was not reached (p10 0.017 > 0.00833).

The specificity check for C1 used a regular-morph family: SelfMAD MAD22 FaceMorpher under E7 stays at 0.11 [0.00, 0.89] (registered F4 (i)).

### 3b. SelfMAD release on the raw benchmark files (its own `crop.py` and loader)

Sources: `a41g_x7.md` (X7′, H-new-145, registered: "published regime reproduced on raw files"); `a41g_s12.json` `detail.a.<family>.score` (S12 (a), descriptive); `a41g2_s12k.json` `families.<family>.versions.score` (`auc`, `e7_rise_cross_file`) and `g2r_median_dlogit` (H-new-157 "versions agree", descriptive).

| Family | Raw native EER (published) | Raw E7, INTER_AREA | EER rise: INTER_AREA / PIL bicubic / PIL Lanczos | AUC of the E7 copies vs the originals (same three kernels) |
|---|---|---|---|---|
| Greedy-DiM | 6.39 [3.35, 9.42] (7.60) | 87.23 [82.95, 90.87] | +80.84 [75.97, 85.70] / +86.78 / +85.25 | 0.997 / 0.999 / 0.999 |
| DiM-A | 4.41 [1.75, 6.64] | 69.50 [63.77, 74.45] | +65.10 / +78.96 / +77.97 | 0.997 / 0.999 / 0.999 |
| MorDIFF | 1.49 [0.00, 3.42] | 45.20 [39.72, 50.25] | +43.71 / +64.70 / +61.73 | 0.996 / 0.999 / 0.999 |

- **The PIL kernels push further.** They shift the release's median logit by +0.90 to +0.99 beyond INTER_AREA (every interval excludes 0).
- **The ladder is one result, not three.** It sits at the AUC ceiling and uses the same 204 photos for all three kernels.
- **Words.** Never "kernel-independent"; it is "not specific to INTER_AREA".
- **A42 post hoc.** Lanczos copies keep more top-band energy than INTER_AREA copies, yet push the release as far as bicubic copies. So "less top-band energy" does not explain the PIL push. Which kernel property matters is not shown.

### 3c. X3: published diffusion morphs vs genuine photos passed through DiffAE (releases only; AUC [person 95%])

Source: `/home/narolski/mambamorph-code/smadcvpr/results/A41/a41g_x3.md` (and `.json`).

**Status:**
- **Registered, blind:** F3 (SelfMAD own, rec, Greedy-DiM + MorDIFF): supported, p < 1e-4. F7 (ViT-B/16, rec, MorDIFF): falsified by its kill, i.e. the refuter fired.
- **Identity:** H-new-140 reads "no identity-mixing evidence".
- **Positive-control gate:** FE ViT-L/14 Greedy-DiM rec 0.636 ≤ 0.65, so "assay sensitivity not shown".
- **Other cells:** descriptive.
- **Gates passed:** alignment 1.0, identity 1.0, fidelity 0.5133 (DiM-A only; no MorDIFF fidelity gate was registered).

| Row | Family | native | E7 | a256 | rec | self |
|---|---|---|---|---|---|---|
| SelfMAD own | Greedy-DiM | 0.959 | 0.027 | 0.004 [0.001, 0.010] | **0.024 [0.011, 0.042]** | 0.018 |
| SelfMAD own | DiM-A | 0.990 | 0.256 | 0.075 | 0.234 [0.184, 0.287] | 0.113 |
| SelfMAD own | MorDIFF | 0.993 | 0.321 | 0.092 [0.062, 0.123] | **0.330 [0.284, 0.374]** | 0.212 |
| SelfMAD our pipeline | Greedy-DiM / DiM-A / MorDIFF | 0.750 / 0.922 / 0.977 | 0.040 / 0.190 / 0.362 | 0.010 / 0.060 / 0.150 | 0.018 / 0.104 / 0.256 | 0.022 / 0.095 / 0.295 |
| ViT-B/16 | Greedy-DiM | 0.458 | 0.064 | 0.080 | 0.024 | 0.078 |
| ViT-B/16 | DiM-A | 0.872 | 0.438 | 0.530 | 0.361 [0.297, 0.425] | 0.452 |
| ViT-B/16 | MorDIFF | 0.987 | 0.885 | 0.911 | **0.847 [0.803, 0.891]** | 0.942 [0.913, 0.968] |
| ViT-L/14 | Greedy-DiM | 0.947 | 0.939 | 0.843 | 0.749 [0.696, 0.802] | 0.386 |
| ViT-L/14 | DiM-A | 0.863 | 0.885 | 0.674 | 0.550 | 0.268 |
| ViT-L/14 | MorDIFF | 0.803 | 0.682 | 0.723 | 0.610 | 0.501 |
| FE ViT-L/14 | Greedy-DiM | 0.860 | 0.805 | 0.719 | **0.636 [0.579, 0.693]** | 0.312 |
| FE ViT-L/14 | DiM-A | 0.929 | 0.897 | 0.837 | 0.772 | 0.489 |
| FE ViT-L/14 | MorDIFF | 0.699 | 0.736 | 0.802 | 0.742 | 0.522 |

**Cue-only floors (print-only, Q-G2).** Each is what simple image properties (bytes, border fraction, geometry, logistic regression on cues) reach for the contrast:

| Contrast | Cue floor | Which pool is smoother |
|---|---|---|
| Greedy-DiM vs rec | **0.993** | rec (floor-limited) |
| Greedy-DiM vs a256 | 0.974 | a256 |
| Greedy-DiM vs self | 0.939 | self |
| DiM-A vs rec | 0.775 | rec |
| DiM-A vs a256 | 0.566 | a256 |
| DiM-A vs self | 0.597 | the published morphs |
| MorDIFF vs rec | **0.602** | the published morphs |
| MorDIFF vs a256 | 0.726 | the published morphs |
| MorDIFF vs self | **0.956** | the published morphs |

- **Above its floor:** only ViT-B/16 MorDIFF vs rec (0.847 against a floor of 0.602) clearly exceeds the cue floor.
- **At its floor:** ViT-B/16 MorDIFF vs self (0.942 against 0.956).
- **Below or at their floors:** ViT-L/14 Greedy-DiM vs rec (0.749 against 0.993) and every SelfMAD cell. The SelfMAD cells sit below 0.5, i.e. reversed.
- **Caveat on the self pool.** It carries visible interpolation artefacts (X3 generation report), which favour the "no identity-mixing evidence" wording.

**A42 (descriptive, post hoc).**
- **ViT-B/16 MorDIFF vs rec:** 0.844 [0.787, 0.895] with border area matched (0.847 unmatched). It weakens from 0.890 to 0.755 across border-area fifths.
- **Other rows on rec:** SelfMAD own 0.359, SelfMAD pipeline 0.285, ViT-L/14 0.601, FE ViT-L/14 0.739.
- **Source:** `smadcvpr/results/A42/a42_border.md`, H-new-240 (a).

### 3d. ViT-B/16 release MorDIFF robustness checks

| Check | Native | E7 | Rise [95%] | Status, source |
|---|---|---|---|---|
| X14b crop c0 (registered frame) | 4.90 | 19.60 | +14.70 [+10.26, +19.15] | F6 registered, supported; `a41g_x14b.md` |
| c1 | 3.91 | 19.60 | +15.69 [+11.63, +19.52] | same |
| c2 | 1.49 | 22.52 | +21.04 [+15.63, +26.94] | same |
| c3 | 4.41 | 17.62 | +13.22 [+10.38, +17.85] | same |
| c4 | 3.02 | 17.62 | +14.60 [+10.63, +17.72] | same |
| ViT-L/14, same five crops (beside) | 22.52-29.90 | 36.78-41.73 | +10.74 to +14.26 | same |
| S8 cue-matched (geometry + bytes) | – | 19.60 full / 21.18 matched | +1.58 [−2.87, 7.61] | H-new-137, registered secondary: "not geometry- or bytes-carried"; `a41_eval.json` H-new-137 |
| XA3c border / band attribution | – | – | not evaluable: the summed attribution has the **opposite sign** to the logit change | A41 G2; no share may be shown (drop list) |

These checks re-use the same persons and images, so they are not a replication.

### 3e. Retrained recipes: native → E7 EER per diffusion family (mean ± SD over seeds, uncapped)

**Sources:**
- Per-family values: `/home/narolski/mambamorph-code/smadcvpr/results/A12/a12_4_read_stage1.json`, keys `arms["<arm>"].family_eer_orig` (native) and `.family_eer_e7` (E7), stored as fractions (×100 here), plus `endpoints_orig/e7.UA8`.
- UA8c (capped at 50 per family; seed t95): `smadcvpr/results/A36/a36_a2.md`, "UA8c per row".

**Status:**
- **Descriptive.** The A12.4 read says the orig pool is "an eval-pipeline diagnostic, never a detection result". The E7 number is the one claimed for any method.
- **Checked.** The A12.4 read reproduces 4,607 per-family EERs of the A12.3e report exactly.
- **Not run.** No registered shortcut rule was applied to the retrains, and they were not scored on X3.

| Arm (n) | DiM-A | DiM-C | Fast-DiM | Fast-DiM-ODE | Greedy-DiM | Greedy-DiM-S | MorDIFF | UA8 uncapped | UA8c native → E7 (t95) |
|---|---|---|---|---|---|---|---|---|---|
| M1 Inception-MAD R x d0 (5) | 13.4±2.4 → 70.9±4.1 | 8.1±2.5 → 54.5±5.5 | 19.2±2.6 → 75.5±4.5 | 25.6±2.2 → 79.5±3.1 | 9.0±1.6 → 60.7±5.7 | 5.5±0.5 → 48.5±5.3 | 20.0±7.4 → 51.2±3.8 | 14.4 → 63.0 | 14.40 → 49.38 ± 1.36 |
| M2 MorphHRNet-style R x d0 (5) | 47.8 → 70.6 | 45.0 → 67.4 | 54.4 → 76.7 | 54.2 → 76.4 | 49.4±12.7 → 71.7±11.5 | 38.3 → 59.4 | 30.0±3.4 → 43.0±6.7 | 45.6 → 66.4 | 41.67 → 48.50 ± 1.62 |
| M3 MADation ViT-B/16 R x d0 (8) | 7.0±2.0 → 7.3±3.0 | 5.4 → 5.9 | 4.7 → 5.2 | 8.3 → 8.6 | 23.2±6.4 → 24.5±6.5 | 4.2 → 4.3 | 35.1±3.6 → 28.6±2.7 | 12.6 → 12.1 | 12.56 → 12.08 ± 2.33 |
| M3L MADation ViT-L/14 R x d0 (5) | 5.6 → 5.0 | 13.8 → 12.7 | 17.8 → 16.4 | 9.6 → 8.4 | 24.3±4.4 → 22.4±4.7 | 7.1 → 6.3 | 45.7±1.7 → 41.5±1.7 | 17.7 → 16.1 | 17.71 → 16.11 ± 2.60 |
| M4 SelfMAD-style R x d0b (5) | 100.0 → 57.7±10.9 | 100.0 → 43.1 | 100.0 → 56.3 | 100.0 → 51.5 | 100.0 → 54.9±19.4 | 100.0 → 21.5±6.1 | 100.0 → 60.1±13.3 | 100.0 → 49.3 | 50.00 → 42.77 ± 5.85 |
| M5 PW-MAD R x d0 (8) | 36.1 → 82.5 | 18.2 → 71.2 | 27.6 → 78.3 | 36.7 → 84.6 | 33.6±11.2 → 83.3±5.6 | 8.2±2.5 → 57.2±7.6 | 42.8±23.2 → 49.2±6.0 | 29.0 → 72.3 | 27.98 → 49.54 ± 0.52 |
| M6 OrthoMAD R x d0 (5) | 42.5 → 69.6 | 30.0 → 55.9 | 44.3 → 70.9 | 50.2 → 75.9 | 38.2±3.7 → 64.8±4.1 | 20.8 → 41.5 | 32.7±11.7 → 47.7±7.0 | 37.0 → 60.9 | 36.80 → 48.22 ± 1.26 |
| M8 MixFaceNet-MAD R x d0 (5) | 31.4 → 71.0 | 23.4 → 58.5 | 36.1 → 73.4 | 40.6 → 77.2 | 30.7±10.0 → 69.0±6.4 | 19.3 → 52.8 | 15.6±1.8 → 44.5±4.0 | 28.1 → 63.8 | 28.05 → 48.89 ± 1.22 |
| M8O MixFaceNet official code O x d0 (5) | 41.1 → 72.9 | 31.3 → 62.8 | 46.4 → 76.1 | 50.9 → 78.2 | 38.9±6.3 → 71.7±7.8 | 25.2 → 55.8 | 24.2±6.9 → 44.7±4.9 | 36.9 → 66.0 | 36.30 → 48.97 ± 0.61 |
| Frozen-CLIP head a124lp d0 (5), descriptive | 9.9 → 10.1 | 11.9 → 12.6 | 10.6 → 10.7 | 10.4 → 10.8 | 18.9±2.9 → 22.0±3.9 | 9.1 → 9.5 | 37.0±1.7 → 30.8±1.6 | 15.4 → 15.2 | 15.40 → 15.20 |

**Our data + our protocol (P x d1), the same E7 pool.**
- **UA8c:** M1 44.88, M2 42.05, M5 44.75, M6 42.92, M8 45.66, M3 42.76, M4 47.09.
- **Confirmatory H-full** (`/home/narolski/mambamorph-code/experiments/A12-BR_benchmark_recipes/README.md`):
  - In favour of P x d1: M1 −4.50 [−6.33, −2.67], M2 −6.45 [−8.12, −4.78], M5 −4.79 [−6.00, −3.58], M6 −5.31 [−7.03, −3.58].
  - In favour of the published recipe: M3 MADation +30.68 [+28.17, +33.20].
- **Where the CNN gain sits (descriptive):** 75-98% of it comes from DiM-C + Greedy-DiM-S. The other four DiM variants stay at 48.7-95.3, mostly inverted.

### 3f. Thresholded: genuine-photo flag rate (BPCER, %) at each network's native 5%-BPCER threshold

Source: `smadcvpr/results/RSX/rsx_read.md`, "Mechanism" table (registered A32 reader; M is "not supported as registered", descriptive).

| Network | Native pool | DiM E7 pool | MorDIFF E7 pool | FRLL resample50 photos |
|---|---|---|---|---|
| SelfMAD release, own preprocessing | 5.39 | **100.00** | **99.51** | 95.10 |
| SelfMAD release, our pipeline | 5.39 | 91.01 | 93.63 | 71.08 |
| MADation recipe R x d0 (n 8) | 5.39 | 5.71 ± 0.84 | 2.21 ± 0.90 | 5.88 ± 0.82 |
| MixFaceNet official code O x d0 (n 5) | 5.39 | 57.34 ± 9.50 | 33.82 ± 11.58 | 26.67 ± 5.55 |
| SelfMAD-style M4 P x d0 (n 5), descriptive | 5.39 | 0.00 | 0.00 | 3.53 ± 7.46 |
| MixFaceNet release (A36 amendment 2 post-result review; review-derived, post hoc; `experiments/A36_published-detector-shortcuts/README.md`) | 5 (its own native threshold) | 36.7 | 21.6 | 18.9 / 18.1 (half-resolution camera photos) |

Do not quote MixFaceNet-release flag rates at its VALX-A\* threshold (A39 S2).

### 3g. Dose ladder and resampled morphs (releases)

**Dose ladder (S7):** the AUC of downsampled copies of 185 FRLL photos against their originals. Source: `a41_eval.json` S7.rows. Status: H-new-136, a registered secondary rule; "calibrated".

| Release | ~1.0x | 1.47x | 1.80x | 3.19x | Verdict |
|---|---|---|---|---|---|
| SelfMAD own | 0.584 [0.564, 0.609] | 0.896 | 0.968 | 0.998 | dose response |
| SelfMAD our pipeline | 0.555 | 0.788 | 0.889 | 0.982 | dose response |
| ViT-B/16 | 0.524 | 0.622 | 0.682 | 0.894 | neither |
| ViT-L/14 | 0.494 | 0.479 | 0.469 | 0.456 | none |

**resample50 applied to the morphs (S12 (b)):** paired logit shift [person 95%]. Positive = more morph-like. Source: `a41g_s12.md`; H-new-158, descriptive.

| Release | Greedy-DiM | DiM-A | MorDIFF |
|---|---|---|---|
| SelfMAD own | +0.308 [0.102, 0.503], insensitive, floor-limited | **−1.940** [−2.173, −1.703], responds | −0.592, insensitive |
| ViT-B/16 | +2.937, responds | +9.342, responds | +6.402 [5.072, 7.714], graded |
| ViT-L/14 | −0.012, graded | +0.607, responds | +1.362, responds |

- **SelfMAD.** Resampling a DiM-A morph makes it *less* morph-like to the release, while resampling a genuine photo makes the photo *more* morph-like.
- **ViT-B/16.** Resampling makes diffusion morphs more morph-like.

### 3h. Diffusion morph vs single-identity render of the same generator, and FFHQ DiffAE (AUC)

Source: `smadcvpr/results/A36/a36_read_own.md` section (C) (registered A36 reader; these columns are descriptive, no hypothesis), and `a36_a2.md` for the MixFaceNet release. Retrains: seed mean ± t95. Releases: point only.

**Floors** (bytes / eye geometry transferred / within-set):

| Set | Bytes | Eye geometry, transferred | Eye geometry, within-set |
|---|---|---|---|
| H2 | 0.522 | 0.518 | 0.502 |
| Arc2Face | 0.514 | 0.509 | 0.489 |
| FFHQM/diffae | **1.000** | 0.539 | 0.601 |

| Row | H2 (IP-Adapter-FaceID SD1.5) | Arc2Face | FFHQM DiffAE (E7 pool) |
|---|---|---|---|
| M1 R x d0 | 0.534 ± 0.006 | 0.485 ± 0.014 | 0.687 ± 0.011 |
| M2 R x d0 | 0.532 ± 0.003 | 0.492 ± 0.008 | 0.720 ± 0.038 |
| M3 R x d0 | 0.483 ± 0.003 | 0.485 ± 0.006 | 0.815 ± 0.017 |
| M3L R x d0 | 0.474 ± 0.004 | 0.505 ± 0.007 | 0.724 ± 0.024 |
| M4 R x d0b | 0.475 ± 0.002 | 0.495 ± 0.006 | 0.444 ± 0.056 |
| M5 R x d0 | 0.491 ± 0.011 | 0.511 ± 0.013 | 0.643 ± 0.024 |
| M6 R x d0 | 0.525 ± 0.007 | 0.492 ± 0.008 | 0.703 ± 0.032 |
| M8 R x d0 | 0.533 ± 0.005 | 0.491 ± 0.015 | 0.659 ± 0.044 |
| M8O O x d0 | 0.534 ± 0.004 | 0.486 ± 0.007 | 0.687 ± 0.049 |
| SelfMAD own | 0.510 | 0.510 | 0.382 |
| SelfMAD pipeline | 0.537 | 0.499 | 0.381 |
| MADation ViT-B/16 | 0.497 | 0.485 | 0.505 |
| MADation ViT-L/14 | 0.466 | 0.491 | 0.544 |
| FE ViT-B/16 | 0.498 | 0.482 | 0.690 |
| FE ViT-L/14 | 0.502 | 0.493 | 0.838 |
| FS ViT-B/16 | 0.476 | 0.539 | 0.458 |
| FS ViT-L/14 | 0.502 | 0.511 | 0.660 |
| MixFaceNet release | 0.536 | 0.486 | 0.670 |

- **H2 and Arc2Face.** Every row sits at 0.466-0.539, at the simple-cue floors. No method separates a two-identity diffusion morph from a one-identity render of the same generator.
- **FFHQM DiffAE.** File size alone gives 1.000 here, so no number in that column is evidence of morph detection. The SelfMAD release misses these morphs (0.38, post hoc; CONCLUSIONS).

## 4. Wording rules that bind this column (CONCLUSIONS, "What we can claim about shortcuts")

**Allowed sentences**, as worded by the last post-result review:

- **C1** (SelfMAD release, own preprocessing; FRLL Greedy-DiM main cell, MorDIFF): "Against FRLL photos downsampled to the morphs' face size, the SelfMAD release scores the genuine photos as more morph-like than Greedy-DiM morphs: EER 8.4% → 90.7% (+82.4 [77.3, 87.4]); MorDIFF 2.5% → 61.3% (+58.8 [54.2, 64.6]). Its published regime reproduces on the raw files with its own crop (6.4% vs 7.6%), where the reversal persists (6.4% → 87.2%) under three downsampling kernels (descriptive). It ranks DiffAE reconstructions (0.33 [0.28, 0.37]) and merely resampled photos (0.09) above the published MorDIFF morphs. MAD22 FaceMorpher stays detected and ViT-L/14 is unchanged. One network; cue not identified."
- **C2** (official MADation ViT-B/16, MorDIFF; descriptive row): "EER 4.9% → 19.6% (+14.7 [10.3, 18.9]), in all five crops (+13.2 to +21.0); it also separates the published MorDIFF morphs from DiffAE reconstructions (0.85 [0.80, 0.89]), a registered refuter. Identity evidence or a file/frame property: open."
- **B:** "Morph and bona fide files differ in documented construction attributes that alone separate the classes (O = 1.000 per decision cell)."
- **Cue words:**
  - C1: "bona fide processing history; cue not identified". Never "resolution", "aliasing", "fine-detail loss", "interpolation trace" or "spectral cue".
  - C2: "fine-detail softness". Never "resolution", "partly carried" or "shortcut-carried".

**Dropped, whatever happens** (diffusion-relevant items):

- General shortcut claims:
  - "Published S-MAD detectors rely on shortcuts" (in general), or "for every method".
  - "MADation carries the shortcut": C2 is about the released ViT-B/16 weights only.
  - "Resolution shortcut", for either release.
- Reconstruction (X3) claims:
  - "No analysed detector separates morphs from reconstructions": the ViT-B/16, ViT-L/14 and FE ViT-L/14 releases do on some families.
  - "SelfMAD cannot tell morphs from reconstructions": it reverses them.
  - "ViT-B/16 detects identity mixing", and "the C2 kill is spurious".
- Kernel, border and mechanism claims:
  - "Kernel-independent" and "the kernel does not matter"; the kernel ladder as three replications.
  - "XA3c not run", "the border test excludes a pool artefact", and any border-test share for ViT-B/16.
  - "Learned from RandomDownScale". The mechanism note says only "consistent with", never "explains". (SelfMAD's released training code blends each photo with a Lanczos-resampled zoom of itself and never resamples the genuine partner.)
- Other:
  - The MixFaceNet-MAD resolution sentence.
  - "Proven" or "absolutely sure"; "strong" as ordinary prose.
  - Also from "What this means for the paper": no "GAN or diffusion generalisation" claim, and A12 numbers are never set against published tables.

**Printed beside every claim** (per CONCLUSIONS):
- The positive controls: the FE ViT-L/14 X3 gate 0.636 ≤ 0.65 ("assay sensitivity not shown"), and the ViT-L/14 negative control (Greedy-DiM Δ 0.00).
- "MADMamba not evaluated (sealed)".
- Our own networks' history with the same control. It is left out here because it concerns our networks (sealed W3 / E-series), not a competing method.

## 5. What this column does not show (gaps in the logged evidence)

- **X3 was run on 5 release rows only**, never on the retrained recipes M1-M8O. So for the retrains, "once genuine photos went through the generator" rests only on H2 / Arc2Face. Those are other generators, not the FRLL DiM / MorDIFF generators.
- **The reconstruction test's sensitivity is not shown.** The positive control failed on Greedy-DiM (0.636). No MorDIFF fidelity gate was registered, so the meaning of C2's refuter is open (H-new-240 and H-new-241 proposed; the A42 window part did not run because of a scorer bug).
- **A border or alignment artefact of our E7 control pool is not formally excluded.**
  - XA3c is "not evaluable" for both releases.
  - For C1's main cell the border holds 8% of the pool's difference and covers 0.2% of the input.
  - The MorDIFF E7 pool's border share is 0.471, and it raises even the ViT-L/14 release by +10.7. So the MorDIFF control is the weaker one.
- **Single networks and shared pools.**
  - Each release is one network.
  - All seven FRLL diffusion families share one 204-photo genuine pool (102 persons).
  - The crop test and the kernel ladder re-use the same images, so neither is a replication.
- **Off-FRLL diffusion evidence is weak.** FFHQ DiffAE is cue-confounded (bytes floor 1.000). The proposed off-FRLL replication on FFHQM DiffAE (H-new-174) and A40's H2 probe (H-new-134) did not run.
- **Retrain native numbers are an eval-pipeline diagnostic only** (A12.4), and no registered shortcut rule was applied to any retrain.

Key source files (absolute):
- `/home/narolski/mambamorph-code/experiments/CONCLUSIONS.md`
- `/home/narolski/mambamorph-code/experiments/A41_shortcut-proof-zero-gpu/README.md`
- `/home/narolski/mambamorph-code/smadcvpr/results/A41/` (`a41_eval.json`, `a41g_x3.md`, `a41g_x14b.md`, `a41g_s12.json`, `a41g2_s12k.json`, `a41g_x7.md`, `a41_files.md`)
- `/home/narolski/mambamorph-code/smadcvpr/results/A42/a42_border.md`
- `/home/narolski/mambamorph-code/smadcvpr/results/RSX/rsx_read.md`
- `/home/narolski/mambamorph-code/smadcvpr/results/A36/a36_read_own.md`
- `/home/narolski/mambamorph-code/smadcvpr/results/A36/a36_a2.md`
- `/home/narolski/mambamorph-code/smadcvpr/results/A12/a12_4_read_stage1.json`
- `/home/narolski/mambamorph-code/smadcvpr/results/A12/a12_4_read_stage2.json`
- `/home/narolski/mambamorph-code/experiments/A12-BR_benchmark_recipes/README.md`
- `/home/narolski/mambamorph-code/experiments/A12-5_a124-review-followups/README.md`
- `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/README.md`
- `/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/README.md`
