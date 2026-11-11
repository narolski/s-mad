# Experiments before 11 Nov 2026

Generated from `mambamorph-code/experiments/*/meta.json` (commit 1714b11). Nothing was copied; paths are relative to `mambamorph-code/experiments/`.
Status values are the ledger's own and some are stale: A44, A45 and A47 were read on 8 Nov although their entries say otherwise (see `../02_REVIEW_AND_SHORTCOMINGS.md`).

| ID | Title | Status | Updated | GPU-h | First headline line | Folder |
|---|---|---|---|---|---|---|
| A10-D | SBI-cue probes (zero-training diagnostics) | analysed | 2026-10-31 | 0.5 | P-seam MADMamba E3 36k: 0.975 AUC | `A10-D_probes` |
| A10-LR | LR parity: 36k twins of every A9-promoted LR | decided | 2026-10-31 | None | EfficientNet-B4 r384 LR 0.001 36k: 4.79 EER % | `A10-LR_lr_twins` |
| A10-L | 72k length rung of every L0 family's D3 configuration | decided | 2026-10-31 | None | EfficientNet-B4 72k (efficientnet_b4_scratch): 3.07 EER % | `A10-L_72k_rung` |
| A10-M | MADMamba token stride x width at 36k (M1-M5) and pruning twins | decided | 2026-10-31 | None | E10 = M3: T p8 36k (mm2_t_v2_conv_v2_p8), the MADMamba entry: 8.6 EER % | `A10-M_madmamba_stride_width` |
| A10-W | Width parity: 36k twins of the baselines' registered siblings | decided | 2026-10-31 | None | DeiT-tiny sibling 36k (DeiT-S family): 35.91 EER % | `A10-W_width_siblings` |
| A12-4 | A12.3e follow-ups: eval pool, format cue, CLIP adaptation, data vs recipe | analysed | 2026-11-01 | 10.14 | MADation, published recipe R x d0: 12.08 EER % | `A12-4_benchmark-followups` |
| A12-5 | A12.4 follow-ups: what inverts MADation's DiM detection, OrthoMAD and frozen CLIP on our data, G-test | analysed | 2026-11-01 | 6.8 | Frozen-CLIP head on our data (H-new-J), UA8c: 10.71 EER % | `A12-5_a124-review-followups` |
| A12-6 | Real photos vs our morphs (frozen CLIP and MADation photos-only arms), MADation R x d1 fresh seeds, W3 predict | analysed | 2026-11-01 | 6.9 | MADation R, our data - photos only, G-test (selection-seen generator): -22.71 EER points | `A12-6_photos-vs-morphs` |
| A12-7 | Photos-only arms for PW-MAD and Inception-MAD, and the morph-class weight of MADation's recipe | analysed | 2026-11-02 | 9.1 | MADation: our morph images, not their weight in the loss, carry the StyleGAN gain (neutral family, both checkpoints; selection-seen generator). | `A12-7_photos-share` |
| A12-BR | Published benchmark methods: own recipe vs our protocol | analysed | 2026-11-01 | None | H-full, UA8c (held-out): P x d1 - R x d0, four CNN methods (M1, M2, M5, M6): '-4.5 to -6.5' EER points | `A12-BR_benchmark_recipes` |
| A12-SP | Specialists as single-network tool-diversity experiments | running | 2026-10-31 | None |  | `A12-SP_tool_diversity` |
| A13-3 | Batch shift and scan removal (core c2) | analysed | 2026-11-01 | 17.8 | N (no scan state term) - K, unadjusted: -1.33 EER points | `A13-3_batch-and-scan` |
| A13-5 | The memoryless scan (core c2, Abar = 0) | analysed | 2026-11-01 | 9.2 | M (memoryless scan, Abar = 0) - K: -0.85 EER points | `A13-5_memoryless-scan` |
| A13-6 | E10's own scan and the lag-0 gain on FRGC (H-new-13, H-new-14) | analysed | 2026-11-01 | 33.4 | P (E10, scan -> skip) - E10 pooled: -0.35 EER points | `A13-6_mamba-scan` |
| A13-7 | The benchmark test of the scan-free E10 (P-W3; H-new-16, H-new-18) | analysed | 2026-11-02 | 10.5 | UA8c, scan-free E10 - E10 (paired by seed): 0.19 EER points | `A13-7_scan-benchmarks` |
| A13-BA | Core-v2 bundle attribution at token stride 8 | analysed | 2026-11-01 | 21.5 | : 9.29 EER % | `A13-BA_bundle-attribution` |
| A14 | Post-freeze MADMamba follow-ups: the G-test inversion fixed in training, the frequency stream, the content gat | analysed | 2026-11-02 | 28 | H-new-21 falsified: E10 trained without the SMDD bona fide is still inverted on the G-test (oracle APCER 99.76%). At the operating point every from-scratch W3 row fails the G-test; in ranking (A15, uncapped AUC) E10 on d | `A14_inversion-gate` |
| A15 | Two zero-GPU diagnosis reads of the G-test inversion: the morph side (H-new-29) and relative sharpness via E5  | analysed | 2026-11-02 | 0 | H-new-29 supported: the G-test inversion is on the morph side (the morphs score more genuine than real FERET / FRGC photos; the FEI pool is not the cause). | `A15_morph-side-sharpness` |
| A16 | What N's gains are: E10 without any SMDD (d2) against a same-batch E10 control (H-new-30; amended: H-new-31 /  | registered | 2026-11-02 | None |  | `A16_d2-control` |
| A17 | Is our data's effect on E10's G-test ranking specific to the G-test? The uncapped eval-GAN AUC read (H-new-34) | analysed | 2026-11-02 | 0 | Within E10 our data improve the eval GAN ranking (+9.7 AUC on MIPGAN-I / II and FRLL StyleGAN) and invert the G-test ranking (-30.1): the inversion is specific to the G-test set (near-determined, descriptive). | `A17_eval-gan-ranking` |
| A18 | The frequency-stream map: where the stream raises or lowers the morph ranking, per eval and G-test family (H-n | analysed | 2026-11-02 | 0 | From scratch the frequency stream lifts the selection metric (-16.7 EER) and AMSL (+10.5 AUC); its diffusion gain sits on the bona fide side (it penalises downsampled bona fide less; native pool -1.6); it costs MIPGAN-I  | `A18_freq-map` |
| A19 | When do the frequencies help? The stream knocked out at inference in E10 (zero state; bias-kept state as a sen | analysed | 2026-11-02 | 1.9 | Without its frequency input at inference, E10 is near chance on the selection set (VALX-A* 8.97 -> 43.14% EER, 16 networks), so whether its MIPGAN-I cost could be undone at inference is not determined (descriptive; the r | `A19_freq-knockout` |
| A20 | The frozen-CLIP readout ladder FCR: C0, C0-hi, ML, RP, RC, RD on a frozen CLIP ViT-B/16 against a same-batch M | registered | 2026-11-02 | 12.0 |  | `A20_fcr-ladder` |
| A22 | Frequency stream x class-symmetric acquisition augmentation a22n: does MADMamba's spectral stream carry morph  | analysed | 2026-11-03 | None | Under class-symmetric train-time acquisition augmentation (a22n), the frequency stream keeps its full selection-set advantage: +18.10 [+16.79, +19.46] vs +16.08 EER points without it (6 paired seeds; H-new-53 and H-new-5 | `A22_freq-stream-augmentation` |
| A26 | MADMamba's v2 frequency stream on pretrained VMamba-T and MambaVision-B-21K: does Haar / DCT help on GAN morph | analysed | 2026-11-03 | None | On pretrained VMamba-T (n 6) and MambaVision-B-21K (n 10), the frequency stream had no detectable effect on GAN morphs or AMSL (Holm-adjusted 90% CIs; MambaVision AMSL uninformative), and no harm on the selection set, wh | `A26_freq-stream-pretrained-mambas` |
| A30 | Training method a22n + GAN-protocol morphs on four pretrained backbones (H-new-64 ... H-new-69; held-out, arm  | analysed | 2026-11-06 | 60 | The method (a22n + our GAN morphs) is not a confirmed gain: design-seen diffusion / GAN 'helps' are geometry-flagged or G-test-driven and none is confirmed on held-out sets. | `A30_gan-protocol-training-method` |
| A32-RSX | Resolution / compression shortcut in published S-MAD diffusion-morph results | analysed | 2026-11-07 | 0.1 | The official SelfMAD release (its own preprocessing) is near-perfect on MorDIFF and Greedy-DiM only against the native high-resolution bona fide pool (EER 2.5 / 8.4); against a resolution-matched pool it fails (61.3 / 90 | `A32-RSX_resolution-shortcut` |
| A36 | Published detectors and shortcuts on the held-out sets (A12BR retrains, SelfMAD and MADation releases) | analysed | 2026-11-06 | 7.588 | No published S-MAD method we analyse tells a StyleGAN3 morph from a single-person StyleGAN3 render beyond simple image properties (H3 orig AUC 0.35-0.59 over 12 primary rows with the SelfMAD own row; H-new-72 neither); b | `A36_published-detector-shortcuts` |
| A37 | StyleGAN3 render controls (spread-matched, truncated, re-stored renders) | analysed | 2026-11-07 | 2.628 | On renders matched to the morphs' latent spread, no network in any of the 14 arms ranks the StyleGAN3 morphs above the renders (AUC 42.8-49.2; descriptive, outside the rule); the two arms above chance on H3 fall to chanc | `A37_stylegan3-render-controls` |
| A38 | A12 twins on H3 and FFHQM (which part of our protocol lowers H3 AUC) and a frozen-feature probe on H3 | analysed | 2026-11-06 | 0.625 | H-new-86 (does removing SBI restore H3 AUC?): neither by the registered rule in both pools; removing SBI raised H3 orig AUC by +0.071 [+0.046, +0.099] (Inception-MAD, meets the +0.05 bar) and +0.040 [+0.014, +0.068] (PW- | `A38_twins-and-feature-probe` |
| A39 | The batch before the run window closes: release adapter check on SMDD, skill-vs-inversion line, SelfMAD own-ro | analysed | 2026-11-07 | 0.278 | Partial: R1-R4 read on CPU (2026-11-06); S2 and P read on 2026-11-07; S1, S3 and T withdrawn by the author (not run). | `A39_batch-before-window-close` |
| A40 | SelfMAD downsampling response by native detail, a fresh SBI distinctiveness replication on A39 S1, and the A38 | analysed | 2026-11-07 | 0.0 | Part F read (zero GPU); Q (H-new-133) and H2 (H-new-134) not run, withdrawn by the author. | `A40_selfmad-detail-sbi-replication-h2-probe` |
| A41 | Shortcut proof: person-clustered E7 contrasts, specificity, dose ladder, H3 absence, spectra, construction tab | analysed | 2026-11-07 | 1.037 | A41 amendment G2 read 2026-11-07 13:48:41-13:48:57 CET (xa3c, s12k and the full decide; REAL, local CPU, every part exit 0, nothing refused; 3 WCSS H100 job lines and 2 smokes, 0.043 GPU-h; A41 in total 1.037). Every gat | `A41_shortcut-proof-zero-gpu` |
| A42 | Six descriptive follow-ups of the A41 amendment G / G2 post-result reviews: the ViT-B/16 frame border (border- | analysed | 2026-11-07 | 0.074 | A42 read in full on 2026-11-07: the zero-GPU parts 16:42:51-16:43:23 CET, the window part (through A42 amendment 1) 18:08:39-18:08:49 CET and the write-once summary 18:08:58 CET (REAL, local CPU, every part exit 0, nothi | `A42_shortcut-followups-descriptive` |
| A43 | The MorDIFF two-by-two: published vs our same-pair DiffAE morphs at 100 and 20 decoding steps, two- vs one-ide | analysed | 2026-11-07 | 0.108 | A43 read in full on 2026-11-07 22:02:21-22:02:35 CET by the registered a43_read.py (REAL, local CPU, exit 0, nothing refused; every binding gate passed, the re-score gate exact in all 8 releases). Registered joint cell ` | `A43_mordiff-two-by-two` |
| A44 | The MADation mechanism block: component ladder, in-memory LoRA removal and dose, head-direction decomposition, | analysed | 2026-11-07 | 0.096 | A44 partial (2026-11-07 23:22 CET): the 11 gate-first M2 platform gates all pass (/dAUC/ <= 0.00027, tau >= 0.995); F5 / H-new-274 supported: the released ViT-B/16's logit on 185 genuine photos (102 persons) rises monoto | `A44_madation-mechanism` |
| A45 | SMDD-only reproduction retrains (Inception-MAD, MorphHRNet) and the FD-MAD re-implementation | running | 2026-11-07 | None | reproduction gate per arm (incep_ofc, hrnet_w18, hrnet_w48_m2, fdmad_g; fdmad_g512 descriptive): None PASS / FAIL | `A45_smdd-reproduction-retrains` |
| A46 | The zero-GPU diffusion family, the reproduction register and the raw-file runs (A-1 official boxes, A-2 releas | running | 2026-11-08 | None |  | `A46_diffusion-register-raw-files` |
| A47 | The training interventions: I-4 label-permuted negative control, I-3 morph-free positive control, I-1 class-sy | running | 2026-11-07 | None |  | `A47_training-interventions` |
| A8-T | Determinism and snapshot trajectories of VMamba-T + frequency stream (T1, T2, T2-s) | final | 2026-10-30 | 2.7 | T2 SWA endpoints (VMamba-T+freq v1 @256): 38.01 EER % | `A8-T_trajectory-determinism` |
| A8-W0 | Diagnosis, VAL-X-A, FST specification freeze and the shortcut floor | decided | 2026-10-30 | None | E0 VALX-A span (min): 6.73 EER % | `A8-W0_infrastructure-valx-fst` |
| A8-W1A | MADMamba-v2 from scratch: core x stem x frequency factorial | final | 2026-10-30 | 13.4 | Reference v1_lin_v1 N@384: 39.26 EER % | `A8-W1A_madmamba-v2-factorial` |
| A8-W1B | MADMamba-v2 width, input size and training length (from scratch) | final | 2026-10-30 | 29.9 | N@512 v1_lin_v1 (12k): 33.3 EER % | `A8-W1B_scale-length` |
| A8-W1C | L0 scratch baselines (ResNet-50, ConvNeXt-T, DeiT-S, EfficientNet-B4, HRNet-W18), incl. W1-C2 | final | 2026-10-30 | 52.1 | ResNet-50 384, LR 5e-4 (adopted): 44.6 EER % | `A8-W1C_scratch-baselines` |
| A8-W1D | Fine-tuning strategy for the ImageNet-1k league (L1), with WiSE-FT | final | 2026-10-30 | 24.0 | DeiT-S llrd (adopted): 42.84 EER % | `A8-W1D_finetuning-menu` |
| A8-W1E | Pretraining source at a fixed architecture (IN-22k, CLIP, DINOv3, MambaVision) | final | 2026-10-30 | 12.9 | H6a: CLIP-Mamba-S − VMamba-S: -1.18 Δ EER points | `A8-W1E_pretraining-source` |
| A8-W1F | Data-pipeline arms (−balance, R6, R8, SBI-int, d1-real, all) on three reference configurations | decided | 2026-10-30 | 14.8 | MADMamba-v2 N@384 + SBI-int: 19.84 EER % | `A8-W1F_data-arms` |
| A9-L3 | W2-L3: knowledge-distilled scratch students (registered, consent pending) | registered | 2026-10-30 | None |  | `A9-L3_kd-students` |
| A9-W2L0 | W2-L0: scratch parity grid (MADMamba factorial and pruning, baselines, D1-D4 standings) | decided | 2026-10-30 | 130.0 | MADMamba L0 entry E3 (N, v2_conv_v2, 384, 36k): 12.56 EER % | `A9-W2L0_l0-parity-grid` |
| A9-W2L1 | W2-L1: ImageNet-1k league (strategy, VMamba-T frequency pruning, resolution) | decided | 2026-10-30 | 51.1 | VMamba-T L1 entry (plain, freq none, 384, full): 0.83 EER % | `A9-W2L1_imagenet-league` |
| A9-W2L2 | W2-L2: large-scale pretraining league (inheritors, 384 adoptions, CLIP ViT-B/16) | decided | 2026-10-30 | 100.3 | MambaVision-B-21K (384, freq none): 0.35 EER % | `A9-W2L2_large-pretraining-league` |
| A9-W2R | W2-R: SBI dose, strength and R6/R8 attribution (both leagues) | analysed | 2026-10-30 | 87.4 | L1 "all" (R6+R8+SBI), Δ_pool: -1.22 Δ EER points | `A9-W2R_sbi-dose-attribution` |
| A9-W3 | W3: frozen configurations, 10 fresh seeds each, FST claims (registered) | analysed | 2026-11-02 | None | MADMamba E10 VALX-A* (W3, 10 fresh seeds): 9.19 EER % | `A9-W3_frozen-list` |
| E00 | Learning-rate selection on val10 (E0) | final | 2026-10-30 | 23.4 | architectures with tied val10 EER: 11 of 19 | `E00_lr_selection` |
| E01 | Controlled architecture comparison x data regime (E1) | final | 2026-10-30 | 26.6 | MADMamba-T D1 dev: 32.63 EER % | `E01_controlled_comparison` |
| E02 | MADMamba component ladder (E2) | final | 2026-10-30 | 3.1 | plain Mamba D1 dev: 34.37 EER % | `E02_component_ladder` |
| E03 | Per-image thresholds fixed in advance (E3) | final | 2026-10-30 | None | MADMamba-T D1 APCER dev @ BPCER-5% threshold: 61.97 APCER % | `E03_fixed_thresholds` |
| E04 | Unseen attacks: leave-one-tool-out and absent families (E4) | final | 2026-10-30 | 9.6 | MADMamba-T D1 unseen: 44.18 EER % | `E04_unseen_attacks` |
| E05 | Robustness to image degradation (E5) | final | 2026-10-30 | None | MADMamba-T D1 FRLL, clean (native): 13.09 EER % | `E05_robustness` |
| E06 | Inference and training cost on one H100 (E6) | final | 2026-10-30 | None | MADMamba-T GFLOPs @512: 3.49 GFLOPs | `E06_cost` |
| E07 | Shortcut controls: resolution matching and nuisance correlations (E7) | final | 2026-10-30 | None | MADMamba-T D1 dev, native pools: 10.53 EER % | `E07_shortcut_controls` |
| E08 | MADMamba width x input size grid (E8, A3) | final | 2026-10-30 | 14.5 | MADMamba-N@384 dev (lowest cell): 26.25 EER % | `E08_width_input_size` |
| E09 | GAN-morph and shortcut interventions; VMamba-T pretrained vs scratch; G-test (E9) | final | 2026-10-30 | 58.0 | MADMamba-T D1 G-test: 46.23 EER % | `E09_gan_interventions_vmamba` |
| E10 | Wave 3: combining the E8/E9 levers (E10, A6) | final | 2026-10-30 | 21.7 | VMamba-T+freq@256 D1 dev: 24.39 EER % | `E10_wave3_combined_levers` |
| E11 | Input-size control: every baseline at 256 (E11, A7) | final | 2026-10-30 | 6.1 | CLIP-LoRA@256 D1 dev: 23.53 EER % | `E11_input_size_control` |
| STAGE | Node-local staging of the train and score arrays (KDM ticket #26133735) | planned | 2026-11-02 | None |  | `STAGE_tmpdir-staging` |
| <ID> | <short title> | planned | YYYY-MM-DD | None | <what>: None EER % | `_template` |

## Studies and documents without a ledger entry

- `A49_dinov3`
- `A50_ABC_PROSPECTIVE_PLAN_20261108.md`
- `A50_EXECUTION_20261108.md`
- `A50_RESULTS_20261108.md`
- `ABC_COVERAGE_AUDIT_20261108.md`
- `AUTONOMOUS_CONTINUATION_20261108.md`
- `CONCLUSIONS.md`
- `DATA_EXPANSION_ASSET_INVENTORY_20261108T214911_CET.md`
- `DATA_EXPANSION_FOUR_MODEL_PILOT_20261108T214911_CET.md`
- `DINOv3_P1_PLAN_20261108.md`
- `INDEPENDENT_ABC60_OPERATIONAL_DELTA_REVIEW_20261108T225844_CET.md`
- `INDEPENDENT_FINAL_EXECUTABLE_REVIEW_PRIMARY120FIT_20261108T223402_CET.md`
- `INDEPENDENT_OPERATIONS_V2_REVIEW_20261108T232656_CET.md`
- `INDEPENDENT_OPERATIONS_V3_NARROW_REVIEW_20261108T234122_CET.md`
- `INDEPENDENT_PHYSICAL_RELEASE_REVIEW_20261109T000655_CET.md`
- `INDEPENDENT_POSTRESULT_REVIEW_A46_RGB_ONLY_20261108T161539_CET.md`
- `INDEPENDENT_POSTRESULT_REVIEW_A49_20261108T203455Z.md`
- `INDEPENDENT_POSTRESULT_REVIEW_A50_20261108T213134_CET.md`
- `INDEPENDENT_PREREVIEW_A50_20261108.md`
- `INDEPENDENT_PREREVIEW_PRIMARY120FIT_514c7d1_20261108T220512_CET.md`
- `INDEPENDENT_PREREVIEW_SHORTCUT_MITIGATION_20261108T214152_CET.md`
- `INDEPENDENT_REVIEW_A44R_A45_20261108.md`
- `INDEPENDENT_REVIEW_A46_20261108.md`
- `INDEPENDENT_REVIEW_A46_CORRECTIVE_20261108T152840_CET.md`
- `INDEPENDENT_REVIEW_A47_20261108.md`
- `INDEPENDENT_TMPDIR_AUDIT_20261108T224038_CET.md`
- `LITERATURE_TO_DESIGN_ADDENDUM_20261108T214710_CET.md`
- `MAD22_WORKING_DECISION_20261108.md`
- `MAD22_missing_from_both_downloaded_ZIPs_20261108.txt`
- `NARROW_DIVERSE_PILOT_20261108T215424_CET`
- `OWN_DIFFUSION_GENERATION_READINESS_20261108T215848_CET.md`
- `PRIMARY80FIT_EXECUTION_READINESS_20261108.md`
- `README.md`
- `SHORTCUT_MITIGATION_COVERAGE_AUDIT_20261108T213558_CET.md`
- `SHORTCUT_MITIGATION_PROSPECTIVE_PLAN_20261108T213558_CET.md`
- `TMPDIR_AUDIT_EVIDENCE_20261108T224038_CET.txt`
- `WCSS_CONCURRENCY_AUTHORIZATION_20261108.md`
- `build_site.py`
- `dataaudit`
- `dates.json`
- `own_diffusion_readiness_20261108`
- `own_generation_v1`
- `plan_dla_Kamila_2026-11-08.html`
- `primary120fit`
- `primary80fit`
- `research_loop_20261111`
- `site`

## Other locations

- Registered results: `mambamorph-code/smadcvpr/PROTOCOL.md`
- Conclusions: `mambamorph-code/experiments/CONCLUSIONS.md`
- Held-out and matched image sets: `/mnt/t7/smad_heldout/`
- Research loop of 11 Nov: `mambamorph-code/experiments/research_loop_20261111/`, outputs in `/mnt/t7/smad_research/`
- A138 and A139 (not in the ledger): `/tmp/opencode/mambamorph-a138-algorithmic/`, `~/.local/state/smad-orchestrator-v1/` (volatile; copy before reboot)
