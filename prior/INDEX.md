# Experiments before 11 Nov 2026

One row per experiment, grouped by theme. Written 11 Nov 2026 from `mambamorph-code/experiments/*/meta.json` and `README.md`
(the "headline" fields), from `experiments/CONCLUSIONS.md` (snapshot in `CONCLUSIONS_snapshot.md`), and from the independent
review files `experiments/INDEPENDENT_*.md`. Nothing is copied beyond short quotes of numbers. Source folders are relative to
`mambamorph-code/experiments/` unless a full path is given. Registered results live in `mambamorph-code/smadcvpr/PROTOCOL.md`.

Related: `summaries/` (one page per experiment from A32 on), `LOOSE_DOCUMENTS.md`, `DATA_LOCATIONS.md`.

## How to read the table

- **Status.** finished = a result was read and recorded. partial = some registered parts were read, others not run or withdrawn.
  not run = registered or planned, no result exists. retired = no row uses this value; a part that was withdrawn is described in
  the outcome instead. Where the ledger entry is stale, the status here follows `CONCLUSIONS.md` and the independent reviews, and
  the row says so.
- **Stale ledger entries.** A44, A45, A46 and A47 still say "running" or give a partial headline in `meta.json`, but all were read
  on 7 and 8 Nov (`INDEPENDENT_REVIEW_A44R_A45_20261108.md`, `INDEPENDENT_REVIEW_A46_20261108.md`,
  `INDEPENDENT_REVIEW_A47_20261108.md`). The ledger entry of A16 and A20 says "registered"; no result exists for either.
- **Sealed data.** Experiments whose folder names carry a sealed-data marker (the final sequestered test and one special-tool set)
  were not opened for this index. They are listed as "not opened".
- **Early numbers are flawed.** `CONCLUSIONS.md` says the E-series numbers (E01 to E11) were affected by resolution shortcuts,
  score ensembles and a contaminated development set. They are kept for the record, not as evidence.
- **Numbers.** "Selection set" means the development set used to choose configurations (not a final test). n is the number of
  training seeds unless said otherwise. 90% or 95% intervals are as printed in the sources.

## Glossary (each term explained once)

- **S-MAD**: single-image morphing attack detection, deciding from one face image whether it blends two people.
- **EER**: equal error rate, the error at the threshold where false alarms equal misses. Lower is better; about 50% is chance.
- **AUC**: area under the ROC curve, the chance that a random morph scores above a random genuine photo. 0.5 is chance, 1.0 is perfect.
- **APCER / BPCER**: share of morphs missed / share of genuine photos wrongly flagged, at a fixed threshold.
- **E7**: the resolution-matched control, where genuine photos are shrunk and enlarged like the morphs, so file history cannot separate classes.
- **Native pool**: the benchmark's genuine photos as published, without that control.
- **SBI**: self-blended images, fake training morphs made by blending a photo with a warped copy of itself.
- **SMDD**: the synthetic face training set used as the base training data (25,000 genuine, 15,000 morphs per `INDEPENDENT_REVIEW_A47_20261108.md`).
- **FRLL, FERET, FRGC, FEI, FFHQ**: public face photo sets (studio or in the wild). **MAD22**: the SYN-MAD 2022 benchmark, 204 genuine and 4,483 morphs published; our copy has 185 and 4,069.
- **MorDIFF, DiM, Greedy-DiM**: diffusion morph sets or generators. **MIPGAN**: a GAN morph generator. **StyleGAN3, DiffAE**: generators used to render faces.
- **H3**: our test of StyleGAN3 morphs against single-person StyleGAN3 renders. **G-test**: GAN morphs against FEI camera photos.
- **MADMamba**: our selective-state-space detector. **E10**: its frozen configuration. **MADation, SelfMAD, MixFaceNet-MAD, Inception-MAD, PW-MAD, MorphHRNet, OrthoMAD, FD-MAD**: published detectors.
- **LoRA**: low-rank adaptation, a light fine-tuning method. **SWA**: stochastic weight averaging. **CLIP**: a large image-text pretrained encoder. **ViT**: vision transformer.
- **W3**: the final run of frozen configurations with 10 fresh seeds. **WCSS**: the Wroclaw supercomputer. **GB10**: the local DGX Spark GPU.
- **Holm**: a correction for many tests. **Seed**: one training run with a fixed random start.

## 1. Architecture and training studies

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| E00 | Which learning rate (2e-4 or 5e-5) suits each architecture, judged on a simple validation split? | 11 of 19 architectures tied, so 2e-4 was used for ties; MADMamba-T validation EER 0.94% at 2e-4 against 1.88% at 5e-5 (1 seed). | finished | `E00_lr_selection` |
| E01 | Under one pipeline, does MADMamba-T beat CNN, ViT and CLIP baselines? | No: MADMamba-T 32.63% EER (n 3) against 26.98% for the best baseline, CLIP-LoRA. Flawed early numbers. | finished | `E01_controlled_comparison` |
| E02 | Which MADMamba components earn their place? | Full model 32.63% against plain Mamba 34.37% EER (n 3; spread 0.22 against 5.06). | finished | `E02_component_ladder` |
| E03 | What happens when each threshold is fixed in advance on the development genuine photos? | MADMamba-T misses 61.97% of development morphs at the 5% false-alarm threshold; thresholds set on each benchmark's own genuine photos would miss 20.39%. | finished | `E03_fixed_thresholds` |
| E04 | How do single networks do on unseen tools and families? | MADMamba-T unseen families 44.18% EER (n 3); leaving out WebMorph raises that family from 27.77% to 37.10%. | finished | `E04_unseen_attacks` |
| E05 | How much does image degradation hurt? | MADMamba-T on FRLL: 13.09% clean, 25.31% after resampling to half size (n 3). | finished | `E05_robustness` |
| E06 | What does each model cost on one H100? | MADMamba-T: 3.49 GFLOPs at 512 px, 16.21 ms latency (batch 1), 1,045 images/s (batch 32). | finished | `E06_cost` |
| E08 | How do width and input size change MADMamba? | Lowest cell N at 384 px: 26.25% EER development (n 3); the fused 23.97% is a score ensemble, not one network. | finished | `E08_width_input_size` |
| E09 | Do frequency dropout, no face scans, 256 px, no SMDD or a pretrained VMamba-T help GAN morphs? | G-test EER: MADMamba-T 46.23%, pretrained VMamba-T+frequency 23.58%, scratch twin 44.22% (n 3). | finished | `E09_gan_interventions_vmamba` |
| E10 | Do the E08 and E09 levers combine? | VMamba-T+frequency at 256 px: 24.39% development EER (n 3); the fused 17.87% is an ensemble, not one network. | finished | `E10_wave3_combined_levers` |
| E11 | Is the 256 px advantage an architecture effect or an input-size effect? | At 256 px: CLIP-LoRA 23.53%, VMamba-T+frequency 24.39%, ResNet-50 29.48% (39.37% at 512). Input size is shared. | finished | `E11_input_size_control` |
| A8-T | Is the seed spread of VMamba-T+frequency from nondeterminism, schedule or basin choice? | Averaged-weight endpoints 38.01% EER (n 3) against 53.96% for the scratch twin; rerunning seed 3 gave 33.49 and 34.00. No cause stated in the headline. | finished | `A8-T_trajectory-determinism` |
| A8-W0 | Diagnosis, selection-set build, test specification freeze, shortcut floor. | Not opened. The earlier index quoted "selection-set span (min) 6.73% EER". | not verified | `A8-W0_*` (name carries a sealed marker) |
| A8-W1A | Do the new SSM core, a conv stem or a new frequency stream help a from-scratch MADMamba-N at 384 px? | None passed the rule; reference 39.26% EER (n 3). New frequency stream was 3.66 points worse than the old [+1.32, +6.01]. | finished | `A8-W1A_madmamba-v2-factorial` |
| A8-W1B | Do width T, larger inputs, 36k steps or a higher learning rate help? | N at 512 px reached 33.3% (12k steps, 5.96 points better than 384 px, failed two guards); no 36k run beat its 12k twin (0 of 8 pairs). | finished | `A8-W1B_scale-length` |
| A8-W1C | What do from-scratch baselines reach? | Near chance: ResNet-50 44.6% (adopted setting); best cell EfficientNet-B4 at 512 px 37.41%. | finished | `A8-W1C_scratch-baselines` |
| A8-W1D | Which fine-tuning recipe helps a pretrained ImageNet network? | DeiT-S with layer-wise learning rates 42.84% against 48.19% full fine-tuning; lowest cell Inception-v3 21.52% was not adopted. | finished | `A8-W1D_finetuning-menu` |
| A8-W1E | Does pretraining beyond ImageNet-1k help at fixed architecture? | No clear gain: CLIP-Mamba-S minus VMamba-S -1.18 points [-5.08, +3.24] (hypothesis falsified); CLIMP-B minus VMamba-B +1.63 [-6.93, +10.49]. | finished | `A8-W1E_pretraining-source` |
| A9-W2L0 | Where does MADMamba stand among from-scratch networks? | MADMamba entry E3 12.56% EER (n 6), rank 4 of 6; EfficientNet-B4 7.85% is first, ResNet-50 9.55% second. | finished | `A9-W2L0_l0-parity-grid` |
| A9-W2L1 | With ImageNet-1k weights, which settings win, and does the frequency stream earn its place? | VMamba-T 0.83%, Swin-T 0.58%, DeiT-S 10.17% EER; the frequency stream was dropped. | finished | `A9-W2L1_imagenet-league` |
| A9-W2L2 | How do large-pretraining backbones score? | MambaVision-B-21K 0.35%, CLIMP VMamba-B 0.38%, CLIP ViT-B/16 LoRA 1.65% (n 6). Scores saturate on this set. | finished | `A9-W2L2_large-pretraining-league` |
| A9-L3 | Does distillation from an ImageNet teacher help the scratch students? | Registered, consent pending. | not run | `A9-L3_kd-students` |
| A9-W3 | After the freeze, how does MADMamba E10 do with 10 fresh seeds? | E10 9.19% EER (n 10), 4th of 6 scratch entries; held-out diffusion 40.17% (near chance); G-test 50.0% (cap, an inversion). | finished | `A9-W3_frozen-list` |
| A10-L | Does 72k steps beat 36k for each scratch family? | Yes for three CNNs: EfficientNet-B4 3.07%, ResNet-50 6.06%, HRNet-W18 7.44% EER (n 6). | finished | `A10-L_72k_rung` |
| A10-LR | Do the promoted learning rates survive at 36k steps? | EfficientNet-B4 at LR 0.001 4.79% (-3.06 points [-4.36, -1.73] against its reference; passes the rule, not selected over the 72k rung); ResNet-50 and MADMamba-N at LR 5e-4 (11.2%, 11.32%) kept their reference settings. | finished | `A10-LR_lr_twins` |
| A10-M | Is MADMamba limited by token stride or width, and is the frequency stream still needed? | E10 (T, stride 8) 8.6% EER (n 6), 3.96 points better than the reference; removing the frequency stream costs at least 14.49 points. | finished | `A10-M_madmamba_stride_width` |
| A10-W | Do baselines' narrower siblings beat the main setting at 36k? | Mostly no: DeiT-tiny sibling 35.91%; two other siblings kept the reference. | finished | `A10-W_width_siblings` |
| A13-3 | Does E10's local-convolution core still work when the selective scan is removed? | Scan-free minus with-scan -1.33 points [-2.41, -0.25]; after correcting for training batch, -0.53 [-1.51, +0.49]. | finished | `A13-3_batch-and-scan` |
| A13-5 | Is the scan's gain only its lag-0 gain (memory set to zero)? | Memoryless minus with-memory -0.85 points [-1.96, +0.31]; not falsified within 1 point. | finished | `A13-5_memoryless-scan` |
| A13-6 | Does E10 itself need its scan? | Scan-free minus E10 -0.35 points [-1.32, +0.64], non-inferior; on an unmatched GAN check it was 7.96 points worse (post hoc, resolution-confounded). | finished | `A13-6_mamba-scan` |
| A13-7 | Does the scan matter off the splice data? | Scan-free minus E10 on held-out diffusion +0.19 points [-0.46, +0.84], so no benefit from the scan; G-test untestable (both at the cap). | finished | `A13-7_scan-benchmarks` |
| A13-BA | Does the core-v2 gain come from its Delta setting or its local convolution? | Convolution only: 9.29% EER, tied with E10 (+0.69 [-0.54, +1.90]); Delta only 12.13%, worse (+3.53). | finished | `A13-BA_bundle-attribution` |
| A20 | Can a frozen CLIP readout ladder lower the selection-set error without losing diffusion detection? | Registered only; no result. | not run | `A20_fcr-ladder` |
| STAGE | Can jobs read libraries and images from node-local storage (cluster ticket)? | Planned infrastructure item, no hypothesis, nothing recorded. | not run | `STAGE_tmpdir-staging` |

## 2. Data arms (what training data and recipes change)

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| A8-W1F | Which training-data change makes networks catch the held-out landmark tool? | SBI was the largest lever: MADMamba-N 43.26% to 19.84%, VMamba-T 40.95% to 2.76%, ConvNeXt-T 41.02% to 4.95% (n 3). On splice-type morphs only. | finished | `A8-W1F_data-arms` |
| A9-W2R | Does changing SBI dose, strength or adding R6/R8 data lower the error for every architecture? | Small gains: ImageNet league "all" arm -1.22 points [-1.68, -0.75] (not applied, failed a guard); scratch +R6 -0.94 [-2.30, +0.37]; a "sub" setting was worse (+5.16). | finished | `A9-W2R_sbi-dose-attribution` |
| A10-D | Do networks react to the self-blending seam they were trained on? | Yes: seam probe AUC 0.975 for MADMamba E3 at 36k steps (0.925 at 12k), 0.978 for EfficientNet-B4 (n 6). | finished | `A10-D_probes` |
| A12-BR | Does our training protocol lower the error of published methods relative to their own recipes? | Four CNN methods: -4.5 to -6.5 points on held-out diffusion (chance 48 to 50 down to 42 to 45); MADation 30.68 points worse than its own low-learning-rate recipe (12.08 against 42.76). | finished | `A12-BR_benchmark_recipes` |
| A12-4 | Where does the gap to published tables come from? | MADation published recipe 12.08% EER [9.69, 14.46] (n 8) on held-out diffusion; frozen CLIP with a linear head 15.2% [11.79, 18.61]. | finished | `A12-4_benchmark-followups` |
| A12-5 | What inverts MADation's diffusion detection, and does our data help other methods? | Frozen CLIP head on our data 10.71% (n 5, no inverted family); the SBI+SWA hypothesis for MADation was falsified (-3.55 points [-7.45, +0.35]). | finished | `A12-5_a124-review-followups` |
| A12-6 | Do the real photos or our morphs carry the gain? | Probe: photos carry it (photos only 9.81% against 10.71% with morphs). MADation on the G-test: our morphs carry it (-22.71 points [-32.38, -13.03]). | finished | `A12-6_photos-vs-morphs` |
| A12-7 | Same question for PW-MAD and Inception-MAD, and for MADation's class weight. | MADation: our morph images, not their loss weight, carry the StyleGAN gain. PW-MAD breaks without our morphs; Inception-MAD loses 10 to 12 points on StyleGAN morphs. | finished | `A12-7_photos-share` |
| A12-SP | Specialists as single-network tool-diversity experiments. | Not opened (name carries a sealed marker); the old ledger says "running", no result recorded here. | not verified | `A12-SP_*` |
| A16 | What are the gains of training E10 without the SMDD genuine images? | Registered only; no result. | not run | `A16_d2-control` |
| A30 | Does acquisition-style augmentation plus our GAN morphs help four pretrained backbones? | Not a confirmed gain: "helps" on design-seen sets were flagged or G-test driven; none confirmed on held-out sets (60 H100-hours). | finished | `A30_gan-protocol-training-method` |

## 3. Frequency stream, sharpness and the G-test inversion

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| A14 | Does training E10 without SMDD genuine images, or without the frequency stream or content gate, remove the G-test inversion? | No: still inverted (99.76% of morphs missed); the content gate has no measurable role (-0.59 points [-1.54, +0.18]). | finished | `A14_inversion-gate` |
| A15 | Is the G-test inversion on the morph side or the genuine-photo side? | Morph side: the morphs score more genuine than real photos. Within E10, uncapped AUC 64.4 on SMDD alone against 34.2 with our data. | finished | `A15_morph-side-sharpness` |
| A17 | Is our data's effect on the G-test ranking specific to the G-test? | Yes: within E10 our data raise GAN ranking by +9.7 AUC (MIPGAN-I/II, FRLL StyleGAN) and lower the G-test by 30.1. | finished | `A17_eval-gan-ranking` |
| A18 | Where does the frequency stream raise or lower the morph ranking? | From scratch it lowers the selection-set EER by 16.7 points but costs MIPGAN-I (-11) and MIPGAN-II (-4.7); with an ImageNet backbone it does nothing above 2 points. | finished | `A18_freq-map` |
| A19 | Do the frequencies act at inference (stream switched off)? | E10 falls to near chance on the selection set (8.97% to 43.14% EER, 16 networks); the MIPGAN cost cannot be undone at inference as far as shown. | finished | `A19_freq-knockout` |
| A22 | Does the stream still help once both classes get the same resampling and JPEG augmentation? | Yes: +18.10 points [+16.79, +19.46] against +16.08 without the augmentation (n 6). | finished | `A22_freq-stream-augmentation` |
| A26 | Does the frequency stream help pretrained VMamba-T and MambaVision on GAN morphs? | No detectable effect on GAN morphs or AMSL (Holm-adjusted 90% intervals); no harm on the selection set. | finished | `A26_freq-stream-pretrained-mambas` |

## 4. Shortcut audits (E07 and A32 to A47)

Summaries for every row in this section are in `summaries/`.

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| E07 | Do networks separate morphs from genuine photos by resolution or file size? | MADMamba-T: 10.53% EER on native pools against 32.63% on resolution-matched pools (n 3); 58 of 63 networks broke the correlation limit. | finished | `E07_shortcut_controls` |
| A32-RSX | Do near-perfect published diffusion scores collapse on resolution-matched pools? | The SelfMAD release: MorDIFF 2.5% to 61.3% EER, Greedy-DiM 8.4% to 90.7%. MADation retrain not reproduced (35.1%). | finished | `A32-RSX_resolution-shortcut` |
| A36 | Do published detectors rely on shortcuts rather than morphing evidence? | None of 12 rows tells StyleGAN3 morphs from single-person renders (AUC 0.35 to 0.59). MADation ViT-B/16 MorDIFF 4.9% to 19.6% EER when photos are resolution-matched. | finished | `A36_published-detector-shortcuts` |
| A37 | Which render property do 84 networks read: spread, typicality or stored detail? | On spread-matched renders no network ranks morphs above renders (AUC 42.8 to 49.2); truncated-render and re-store hypotheses not supported. | finished | `A37_stylegan3-render-controls` |
| A38 | Does removing SBI restore H3 AUC, and is the signal linearly readable from frozen features? | Partly: SBI removal raised H3 AUC +0.071 [+0.046, +0.099] (Inception-MAD), +0.040 (PW-MAD); a linear probe reaches 0.91 AUC but follows closeness to the generator's average face. | finished | `A38_twins-and-feature-probe` |
| A39 | Does the MixFaceNet release run correctly through our pipeline, and what lets a detector pass H3? | Release works (EER 0.45% on its own training images); inside H3, latent spread alone separates classes (AUC 1.000), so H3 cannot test identity mixing. S1, S3 and T withdrawn. | partial | `A39_batch-before-window-close` |
| A40 | Is SelfMAD's downsampling response a loss of detail, and does SBI create it? | Not detail: response does not grow with file size (-2.4 points [-6.0, +1.0]). Parts Q and H2 not run (withdrawn). | partial | `A40_selfmad-detail-sbi-replication-h2-probe` |
| A41 | Under one registered rule set, are released detectors' diffusion results shortcut-carried? | Grades final: SelfMAD release strong (Greedy-DiM 8.37% to 90.74% EER); MADation ViT-B/16 descriptive only; StyleGAN3 absence strong but narrow. | finished | `A41_shortcut-proof-zero-gpu` |
| A42 | Do frame border, zero-fill, kernels or alignment explain the A41 effects? | Border area does not (AUC 0.844); central window drops it to 0.61 [0.56, 0.65]; kernel and gradient readings mixed. No grade changed. | finished | `A42_shortcut-followups-descriptive` |
| A43 | Does MADation ViT-B/16 separate MorDIFF from reconstructions because of the decoding step count? | Yes as far as shown: AUC 0.833 at 100 steps, 0.487 at the matching 20 steps. Identity mixing not needed and not separately shown. | finished | `A43_mordiff-two-by-two` |
| A44 | Why does the released MADation ViT-B/16 behave this way? | Score rises with shrink dose (Spearman 1.0); our retrain trained to the last step reaches the authors' regime (MorDIFF 4.44% against their 4.9%). Ledger is stale: R-last read 8 Nov. LoRA-removal tests not run. | partial | `A44_madation-mechanism` |
| A45 | Do our SMDD-only retrains of Inception-MAD, MorphHRNet and FD-MAD reproduce published MAD22 numbers? | No: all arms FAIL (Inception 32.72% against 10.53%; HRNet-W18 40.91% against 9.42%). Ledger says "running"; read 8 Nov per the independent review. | finished | `A45_smdd-reproduction-retrains` |
| A46 | Does any published regime reproduce on raw files with the authors' crop, and do diffusion cells hold? | Mixed and heavily qualified: MixFaceNet release 13.61% on held MAD22 against 13.69% published; crop defect suspended the MTCNN branch; RGB-only secondary accepted with qualifications. Ledger says "running"; stale. | partial | `A46_diffusion-register-raw-files` |
| A47 | What do networks learn when trained with a label-permuted set, no morphs, or symmetric augmentation? | The morph-free arm of the ViT-B/16 (MADation-style) recipe reaches 0.00% EER on MorDIFF without ever seeing a morph; the label-permuted negative control was not at chance, so that result lacks its control. Ledger says "running"; read 8 Nov. | finished | `A47_training-interventions` |

## 5. Mitigation attempts (A49, A50, ABC60, A138)

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| A49 | Does adding a processing-consistency loss to DINOv3 adaptation reduce processing sensitivity? | No: registered joint criterion failed in all 5 seeds; sensitivity +0.0029 [-0.0049, +0.0106]; native EER +0.25 points [-0.23, +0.73]. | finished | `A49_dinov3` |
| A50 | Does replacing some SMDD morphs with our classical morphs help under our recipe? | Small and family-specific: capped diffusion EER -2.11 (MorphHRNet-style) and -2.20 points (OrthoMAD); uncapped worse for three of four carriers. | finished | `A50_*.md` (no folder; three files) |
| ABC60 | Do photos and our morphs (arms B, C) beat SMDD alone (A) on four backbones? | Every interval includes zero; no Mamba advantage; 412 inverted and 152 near-constant family fits among 2,400. | finished | `primary120fit/` |
| A138 | Do algorithmic training fixes (head-only, LayerNorm, consistency, anchoring) reduce the shortcut? | No scientific run; only a timing pilot (D3-N, D3-P) completed. Not in the ledger. | not run (science) | `/tmp/opencode/mambamorph-a138-algorithmic/` (volatile) |

## 6. MAD22 work

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| MAD22-WD | How to treat our incomplete MAD22 copy? | Author decision 8 Nov: use the verified 185 genuine and 4,069 morph subset as best confirmed, keep the published 204 and 4,483 explicit. | finished | `MAD22_WORKING_DECISION_20261108.md` |
| MAD22-MISS | Which MAD22 files are missing? | 433 files missing (19 genuine, 95 OpenCV, 107 FaceMorpher, 105 MIPGAN-I, 107 MIPGAN-II); a reply from the MAD22 authors is pending. | finished | `MAD22_missing_from_both_downloaded_ZIPs_20261108.txt` |
| MV-AA | Does the MambaVision-B-21K training step repeat itself? | Tolerance-close, not bitwise repeatable (job 6297832, 66 H100 seconds). A trajectory-contract test remains open. | partial | `/home/narolski/mambamorph/research_notes/MAMBAVISION_AA6297832_QUALIFIED_PROTOCOL_ADDENDUM_20261110.md` |
| A139 | Engineering build and admission for the next MAD22-related job. | No result recorded in the files read; purpose not verified. | not verified | `/tmp/opencode/a139-*` (volatile) |

Other MAD22 results appear in A45, A46, A49, A50 and ABC60 above.

## 7. Research loop of 11 Nov

Source: `experiments/research_loop_20261111/README.md` (evidence snapshot written 11 Nov). Outputs are under `/mnt/t7/smad_research/`.
None of these rows has a CONCLUSIONS entry yet.

| ID | Question in plain words | Outcome in plain words | Status | Source folder |
|---|---|---|---|---|
| Astra E2 | Does a resolution signal remain after the proposed normalisation (CLIP views)? | Yes: all four primary kappas exceed 0.5, so the planned mechanism is not admitted. | finished | `research_loop_20261111/results/astra_e2` |
| DiffAE102 ROI | Do inner-face heads help on 102 generated cases? | Apparent improvement on ordinary H3 negatives is exploratory only. | finished | `research_loop_20261111/results/diffae_roi102` |
| A37 ROI | Does that improvement survive spread-matched negatives? | No: inner ROI AUC 0.461 and 0.467 against full image 0.487 and 0.489 (original and post-processed). | finished | `research_loop_20261111/results/a37_roi` |
| DiffAE generation | Generate expanded DiffAE morphs. | 123 attempted, 102 complete, 816 images; quality and potency not established. | finished | `research_loop_20261111/results/diffae123` |
| GAN32 generation | Generate 32 GAN dyads. | 128 inversions, 256 images; 698 copy-back members rehashed. | finished | `research_loop_20261111/results/gan32` |
| Frozen 150-head scoring | Score GAN32 with 150 frozen heads. | Scoring complete; numbers pending independent check, not included. | partial | `research_loop_20261111/results/gan32` |
| Astra core fit | Train the CLIP core arms (20 planned fits). | Started: one of 20 fits running; no result. | partial | `research_loop_20261111/state` |
| GAN TRAINplus | Add 32 GAN training dyads in four shards. | Under way; some rented hosts failed; no result. | partial | `research_loop_20261111/protocols` |
| Fresh confirmation64 | Build a fresh 64-case confirmation set. | Selection stopped: documented metadata cell too small; no generation. | not run | `research_loop_20261111/README.md` |
