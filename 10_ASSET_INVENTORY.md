# Asset inventory for the twin-controlled audit (TwinMAD)

Prepared 2026-11-11 for Paweł Narolski. This is a read-only inventory. Nothing was downloaded, run, scored or moved. No file whose name contains `fst`, `valx` or `A12SP` was opened. Web facts come from README pages only; LICENSE files and Google Drive folders were not opened.

**Marks.** "checked" means I looked at the file, directory listing or web page in this session. "not verified" means the item comes from memory, a secondary note, or was not looked at.

**Abbreviations.** P = `/home/narolski/mambamorph-code/smadcvpr/PROTOCOL.md`. C = `/home/narolski/mambamorph-code/experiments/CONCLUSIONS.md`. BK = `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/` (local backup of the WCSS run dirs). PAY = `/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/` (staged weights, named by sha256). L = `/lustre/pd03/hpc-narolski-1790461090/smadcvpr/runs/` on WCSS (not opened; named in the plan lists).

---

## A. Detectors

### A.1 Published releases (web search, 2026-11-11)

| Method | Official repo | Weights | Code | Licence (from README) | Status |
|---|---|---|---|---|---|
| MixFaceNet-MAD (SMDD, CVPRW 2022) | github.com/naserdamer/SMDD-Synthetic-Face-Morphing-Attack-Detection-Development-dataset | Yes. Google Drive, behind a request form. SMDD-trained | Yes | CC BY-NC-SA 4.0 | checked |
| PW-MAD (ISVC 2021) | none found | none | none | n/a | not found |
| Inception-MAD (SYN-MAD 2022 entry) | none found | none | none | n/a | not found |
| MorphHRNet | none found | none | none | n/a | not found |
| OrthoMAD (BIOSIG 2022) | github.com/NetoPedro/OrthoMAD | none released | Training code | No LICENSE file | checked |
| IDistill (2023) | github.com/netopedro/idistill | none released | Yes | No LICENSE file | checked |
| MorDeephy (2023) | none found | none | none | n/a | not found |
| SPL-MAD (IJCB 2022) | github.com/meilfang/SPL-MAD | Yes. Google Drive `casia_smdd.pth`, trained on CASIA-WebFace + SMDD, no form mentioned | Yes | CC BY-NC-SA 4.0 per README (a third-party listing says no licence; check the LICENSE file) | checked |
| MADation ViT-B/16, ViT-L/14 (WACVW 2025) | github.com/gurayozgur/MADation | Yes. Google Drive folder, behind a request form | Yes | CC BY-NC-SA 4.0 (also checked in the local mirror `baselines/MADation/LICENSE`) | checked |
| MADPromptS (2025) | github.com/EduardaCaldeira/MADPromptS | None needed: zero-shot CLIP prompts | Yes | CC BY-NC 4.0 | checked |
| SelfMAD (FG 2025) | github.com/LeonTodorov/SelfMAD | Yes. University SharePoint: HRNet-W18 (the paper's model), EfficientNet-B4/B7, Swin-B, ResNet-152 | Yes | Apache-2.0 | checked |
| FD-MAD (arXiv 2601.20656, 2026) | none found | none | none | n/a | not found (abstract page only; the PDF was not checked for a code link) |
| SRL-MAD (arXiv 2603.15050, 2026, one-class) | none found | none | none | n/a | not found (abstract only) |
| R-FLoRA (arXiv 2604.17321, 2026, CLIP ViT-L/14 + LoRA) | none found | none | none | n/a | not found (abstract only) |
| SYN-MAD 2022, MorDIFF, Greedy-DiM pages | github.com/marcohuber/SYN-MAD-2022; github.com/naserdamer/MorDIFF; github.com/zblasingame/Greedy-DiM | No detector weights on any of them | Generation code only (MorDIFF, Greedy-DiM) | MorDIFF CC BY-NC-SA 4.0; DiM-FRLL-Morphs on HF CC BY-SA 4.0 | checked (Greedy-DiM repo not opened directly) |

Released weights exist for MixFaceNet-MAD, SPL-MAD, MADation and SelfMAD. MADPromptS needs no weights.

### A.2 What we hold locally, whether it reproduced, and its input pipeline

Our re-implementations are the A12-BR recipes. In the arm names, R = published recipe in our pipeline, P = our recipe, O = official code, d0 = SMDD only, d1 = our FERET/FRGC data. Primary networks are R x d0 (list: `experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv`, checked).

| Method | Official release held locally | Our re-implementation (primary R x d0, seeds) | Local copy (checked unless marked) | Reproduced the published number? | Input pipeline |
|---|---|---|---|---|---|
| MixFaceNet-MAD | **Yes.** `/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth` (sha 3d507c8b…); also in PAY | M8 (5 seeds, scratch); M8O = official code retrained (5 seeds) | M8 / M8O es.pt + last.pt in BK (`a12_mixfacenet_s_scratch_r224_d0_*`, `a12_mixfacenet_s_official_r224_d0_*_ocode`) | **Release:** 13.61 vs 13.69 MAD22 on the old 185/4,069 subset, and 9.02 vs 8.96 FRLL. This is "conditional numerical agreement" only, and the end-to-end reproduction claim was withdrawn (P l.20295, A46 F1). **M8 / M8O:** falsified, O x d0 MAD22-5 35.78 vs 13.69 (A12-BR) | Official: MTCNN crop, cv2 BGR, 224, (x−0.5)/0.5, class 0 = attack (A36 amendment 2). Our scoring used 512 eye-aligned frames resized to 224. The MTCNN crop branch is **suspended** for a crop defect (A46) |
| PW-MAD | No (none published) | M5 (8 seeds, DenseNet-121) | BK `a12_pwmad_densenet121_r224_d0_*` (8) | Falsified (A12-BR TOST) | 224 from our 512 aligned frame |
| Inception-MAD | No (none published) | M1 (5 seeds, Inception-v3, 299); A45 `incep_ofc` (5 seeds, 224) | M1 in BK (`a12_inception_v3_scratch_r299_d0_*`). A45 nets are on WCSS only (not verified locally) | Falsified. A12-BR TOST; A45 MAD22-5 32.72 vs 10.53 | 299 (M1) or 224 (A45) from the 512 frame |
| MorphHRNet | No (none published) | M2 (5 seeds, HRNet-W48, 256); A45 `hrnet_w18` (5) | M2 in BK (`a12_hrnet_w48_scratch_r256_d0_*`). A45 W18 on WCSS only (not verified) | Falsified. A45 HRNet-W18 40.91 vs 9.42; W48 34.93 vs 9.42 | 256 from the 512 frame |
| OrthoMAD | No (no weights published) | M6 (5 seeds, ResNet-18) | BK `a12_resnet18_orthomad_scratch_r224_d0_*` (5) | Falsified (A12-BR) | 224 |
| IDistill | No | none | — | — | — |
| MorDeephy | No | none | — | — | — |
| SPL-MAD | No (released, not downloaded) | none | — | — | not verified (README silent) |
| MADation ViT-B/16 | **Yes.** `/mnt/t7/wcss_backups/madation_official_upload/madation_official.tar` holds `madation_vitb16` plus FE/FS variants and the dnorm/dscale diagnostics as safetensors. Also in PAY (ddb1455b…, 6a4d93ba…, a7cacd47…) | M3 (8 seeds) | BK `a12_clip_vitb16_madation_r224_d0_*` (8; es.pt + last.pt, so R-last is available) | **Release:** sanity S met: MorDIFF native 4.9 on our frames, 0.99 on own-crop RGB, vs 1.10 published (A36, A46 RGB-only). **M3:** MAD22 reproduced on the mean only; FRLL inconclusive (A12-BR). M3 R-last reaches MorDIFF 4.44 vs 4.9 (A44 amendment 1) | 224 CLIP from the 512 frame (`a12_released.py` adapters). Trained on SMDD per `src/config.py` (checked in the local mirror) |
| MADation ViT-L/14 | **Yes.** Same tar (`madation_vitl14`, FE, FS); PAY bb452ded…, 74dd7fbc…, 6071ec7b… | M3L (5 seeds) | BK `a12_clip_vitl14_madation_r224_d0_*` (5) | M3L MAD22 better than published (A12-BR). Release: not separately gated (not verified) | 224 CLIP |
| MADPromptS | No (zero-shot; code not mirrored locally) | none | — | — | CLIP; not verified |
| SelfMAD | **Not held locally.** The release (`hrnet_w18_checkpoint.model.safetensors`, sha 0ad8db6f…) is listed only at `L/A12REL/selfmad_hrnet_w18`. Copies under the scratchpad are 61-byte mocks. Code mirror at `baselines/SelfMAD` (`weights/` is empty) | M4 "SelfMAD-style" (5 seeds, HRNet-W18 IN1k, 384, d0b) | BK `a12_hrnet_w18_in1k_r384_d0b_*` (8 dirs) | **Release:** Greedy-DiM 6.4 vs 7.6 published on raw files with its own crop (A41 amendment G). On our frames FRLL-5 gave 24.13 (eval-pipeline gap). **M4:** falsified | Own pipeline (`smadcvpr/rsx_selfmad_own.py`): dlib frontal detector + 81 landmarks, landmark bbox + 6.25% margin, 384×384 bilinear, /255, no mean/std, softmax[:,1]. Training data of the release: not verified |
| FD-MAD | No (none published) | A45 `fdmad_g` global branch only (3 seeds at 256 px, 3 at 512 px; CPU RBF-SVM). The fused branch was built but not run | `/mnt/t7/smad_heldout/a45/fdmad/fdmad_global_r{256,512}_s{1,2,3}` | Partial: "R-a reproduced on both global-only means", non-comparable to the full method (A45) | 256 / 512 |
| SRL-MAD, R-FLoRA | No | none | — | — | — |

Other holdings: PAY holds 157 .pt files, 6 safetensors and the MixFaceNet .pth. These are the 164 canonical164 tasks: A36 primaries M1–M8O (51), A49 P0–P3 × 5 seeds × best/last (40), A50 M1/M2/M5/M6 × A/B/C (66), and 7 releases (`ls …/mad22_canonical164_production_v1/plans`, checked). BK holds 89 GB of A12BR run dirs, including the d1, P and screen arms (checked).

**Detectors we can audit as released:** MADation ViT-B/16 and ViT-L/14 (plus FE and FS variants) and MixFaceNet-MAD, all local. SelfMAD's release is on WCSS only. SPL-MAD would need a download. MADPromptS needs only CLIP. Every CNN row (Inception, MorphHRNet, PW-MAD, OrthoMAD, MixFaceNet retrains) is a re-implementation that did not reproduce.

---

## B. The corrected ("fixed") MAD22

| Item | Value | Mark |
|---|---|---|
| Raw fixed copy (author re-upload, ownCloud, acquired 2026-11-09 10:38–10:49 UTC) | `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/{BonaFide,FaceMorpher,MIPGAN_I,MIPGAN_II,OpenCV,Webmorph}/` plus 6 bbox txt files | checked (ls counts) |
| Counts | BonaFide **204**, FaceMorpher **1,000**, MIPGAN-I **1,000**, MIPGAN-II **999**, OpenCV **984**, Webmorph **500**. That is 4,687 images (204 + 4,483), 102 persons; all files decode | checked |
| Earlier subset | 185 + 4,069 (FaceMorpher 893, MIPGAN-I 895, MIPGAN-II 892, OpenCV 889, Webmorph 500) from two Mac ZIPs (`mad22_incoming/*.zip`, merged at `merged_audit_20261108T142102`). The **old copy at `/mnt/t7/Datasety/downloads/MAD22/original_sorted` is this subset** (185 / 893 / 895 / 892 / 889 / 500) and must not be used | checked |
| Differences | The 4,258 old paths are all present and **byte-identical** (0 conflicts). 433 recovered files: 19 bona fide, 107 FaceMorpher, 105 MIPGAN-I, 107 MIPGAN-II, 95 OpenCV, 0 Webmorph (derived by subtraction). The new set also contains 5 duplicate-SHA groups, all Webmorph (e.g. `021_03-vs-029_03` = `021_03-vs-037_03`) and retained by policy, plus an inherited OpenCV bona-copy defect, flagged and retained | checked (`old_comparison.json`, `identity_label_exclusion_audit.json`) |
| Bona fide identity | Filenames `NNN_03` / `NNN_08` are the 102 FRLL persons (neutral / smiling), 1350×1350. These are the same people as the FRLL-Morphs, MorDIFF and DiM bona fide | checked (raw manifest) |
| Manifests | Raw: `/tmp/opencode/mambamorph-mad22-full-reeval-v1/experiments/MAD22_corrected_v1/inputs_v3/raw_manifest.json` (4,687 rows, sha d256281e…; **in /tmp, volatile**). Committed copy of the file list with hashes: `mambamorph-code/experiments/dataaudit/marco_owncloud_20261109T103840Z/verified_inventory.json` (commit 408e50e) | checked |
| Processed (canonical512 two-eye alignment, CPU backend) | `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/<family>/` (4,687 PNG) and `e7/<family>/` (204 per morph family = 1,020). Hashes in `PROCESSED_SHA256SUMS` (5,707). The E7 cell definitions are `canonical_E7_panel.json` (sha 9e174bf1…); new family IED medians are in `family_native_ied_targets.json` | checked |
| Caution | The processed native PNGs **differ in bytes from the old registered inputs for 4,209 of the 4,254 shared rows** (E7: 906 of 925). Old-subset scores therefore cannot be merged with new-input scores | checked (`materialization_receipt.json`) |
| Registration | PROTOCOL "Corrected MAD22 input admission v3" (P l.20449), then the input review "CPU_INPUTS_ADMITTED_QUALIFIED" (C, 2026-11-11 morning integration) | checked |
| Scores on the fixed set | **None.** canonical164 production (164 tasks, 42,046 calls; P l.20545) job 6298965 was **CANCELLED, 0 s**. The only completed jobs are synthetic-pixel technical smokes (6287896 failed; 6288545, 6294852 and 6297451 completed) and CPU plan compiles (6295412 failed, 6295571 partial, 6296447 continuation). None of these produced a real-image score | checked (C morning table; P) |

**What a new experiment must point at to be "on the fixed MAD22":** the 4,687-row population from `raw_manifest.json` / `verified_inventory.json`, with images from `marco_owncloud_20261109T103840Z/author_files/original_sorted/`. If our alignment is used, read `mad22_canonical_E7_inputs_v3_20261109T113746Z/native` (and `e7` for E7 cells) and check it against `PROCESSED_SHA256SUMS`. Never use `/mnt/t7/Datasety/downloads/MAD22`, `smadcvpr_data/manifests/eval.csv` (set = mad22: 185 + 4,069, old inputs) or `merged_audit_20261108T142102`. Results must be labelled as on the corrected population and must not be pooled with old-subset numbers. Before scoring: copy `raw_manifest.json` out of `/tmp` into the repository (not verified whether a committed copy already exists).

---

## C. Generators and matched sets

Here "twin" means a same-person construction: two different photos of one person fed through the morph or generator pipeline.

| Asset | What it is | Images (checked counts) | Where it ran / ARM? | Throughput | Same-person second photo used? |
|---|---|---|---|---|---|
| **GAN32** `/mnt/t7/smad_research/vast-gan32-v1-results/out`, `vast-gan32-trainplus-shard{0,2,3}-results` + `shard1-v2-results` (union list `gan32-trainplus-union-v1/OUTPUTS.json`) | StyleGAN3-T FFHQ-1024 inversion (`payload/models/stylegan3-t-ffhq-1024x1024.pkl`, LPIPS, w600k). Blocks of 2 persons × 2 captures. Roles: **P0/P1** = morph(A,B) per capture; **SA/SB** = self-morph of A's two captures; **RA0/RA1/RB0/RB1** = single-capture reconstructions | 64 blocks (FERET + FRGC, train_fit + diagnostic), 128 + 128 captures, 256 + 256 renders, raw1024 + common512 | Vast, x86, RTX PRO 6000 (96 GB), torch 2.9.1 cu128 | 128 captures in 8,032 s (about 63 s per capture, batch 4); shard0 32 captures in 1,978 s | **Yes** (SA/SB). checked |
| **DiffAE expanded123** `/mnt/t7/smad_research/diffae-expanded123-v1/run/` | DiffAE FFHQ256, same 8-role block design (P0/P1, SA/SB, R*) on FERET/FRGC | 123 blocks attempted, 102 complete, 816 outputs (1,720 PNG incl. aligned/raw sources); `training_admitted=false` | **GB10 (ARM)**, checked in the run events | 7,998 s for 816 outputs (about 9.8 s each; 124,820 denoiser calls) | **Yes** (SA/SB). checked |
| **A41 X3 DiffAE** `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/{rec,self,cross,a256}` | DiffAE (T_enc 250, T_dec 100, DiM-A recipe) on FRLL: reconstructions of 204 photos, **102 self-morphs (p_03 + p_08)**, 100 cross morphs | 204 / 102 / 100 (plus mdcrop/orig variants; 1,940 files) | **GB10**, torch cu130 (`logs/x3_gen.log`) | 4,795 GPU-s total | **Yes**, neutral + smiling of one FRLL person. Expression mixing confounds it (A43). checked |
| **A43** `/mnt/t7/smad_heldout/a43/data/a43/stored/{A,B,B20,C,C20,D,D20,E}` | A = 200 published MorDIFF; B/B20 = our two-person morphs at 100/20 steps; **C/C20 = one-identity self-morphs**; D/D20 = reconstructions; E = 204 photos | A 200, B 200, B20 200, C 102, C20 102, D 204, D20 204, E 204 | **GB10** (`gen/gen_log.json`) | encode 13.1 s per image; decode 5.1 s per image at 100 steps, 1.0 s at 20 steps (bs 16) | **Yes** (C, C20). Expression-matched Bx (R2x) was **not built** (0). checked |
| DiffAE install `/mnt/t7/thirdparty/diffae_00c57d3f…` + `diffae_venv` | Pinned DiffAE repo + FFHQ256 checkpoint (sha 9bd2ba9e…) | — | **Runs on GB10** (A41, A43 and expanded123 all ran here, torch 2.12.1+cu130). The plan's "DGX build not ready" conflicts with this; the x86 failure was A139's, which is "Runtime NOTBUILT" | as above | — checked |
| **H3** `/mnt/t7/smad_heldout/h3_sg3` (A35) | StyleGAN3-T: morph = G((w+_A + w+_B)/2) vs reconstruction G(w+_C) of a **third** CASIA contributor | 600 raw pairs; 423 + 423 final (orig + pp) | WCSS H100, x86 container | about 2 h 40 min per 50 pairs (P A35) | No (C is a different person). checked |
| **A37 sg3ctl** `/mnt/t7/smad_heldout/a37_sg3ctl` | H3 re-decodes: spread-matched, trunc50, trunc70, redec, h3copy pools | 19,570 files; 423 renders per pool | WCSS H100 (decode only) | about 228–249 s per task | No. checked |
| **H4** `/mnt/t7/smad_heldout/h4_mipgan1` (A33) | "MIPGAN-I-style reimplementation" (StyleGAN v1 FFHQ, MIPGAN loss, 150 Adam steps) on CASIA look-alike pairs vs CASIA camera crops | 326 + 326 (of 500 planned); 1,000 CASIA crops in `work/inputs` | WCSS H100 job 6237081 | not verified | No. checked |
| **H4b** `/mnt/t7/smad_heldout/h4b_mipgan1` (A34) | H4 morphs vs the same StyleGAN v1 render of the **host contributor**, from the same photo | 338 + 338 | WCSS H100 job 6237487 | not verified | No: same person but the same photo. checked |
| **MIPGAN-II-style + StyleGAN2 morphs** (training GAN arm) | `experiments/own_generation_v1/receipts/A28_generate_65ee792.py`: e4e + StyleGAN2 FFHQ config-f; `--gen stylegan` and `--gen mipgan2` ("one StyleGAN2 backbone, not an official MIPGAN-II reproduction") | 3,000 PNG on FERET/FRGC (README; files not located in this session) | WCSS container (pure-PyTorch ops, no nvcc) | not verified | No: two-person only. "No self-subject pairs". not verified for location |
| **H2** `/mnt/t7/smad_heldout/h2_embmid` (A29) | IP-Adapter-FaceID SD1.5 (Realistic Vision 4.0): render of normalised(t_A + t_B) vs render of t_C | 992 + 992 | WCSS, x86 pylib | not verified | No. checked |
| **Arc2Face** `/mnt/t7/smad_heldout/arc2face` (A23) | Arc2Face render of a mixed ArcFace embedding vs render of a third identity | 548 + 548 (+ 247/238 excluded) | **GB10** (P A23) | not verified | No. checked |
| **H1** `/mnt/t7/smad_heldout/h1_poisson` (A27) | MediaPipe-478 Delaunay warp + Poisson blend landmark morphs on CASIA look-alike pairs | 598 + 598 (orig + pp) | local CPU (DGX) | not verified | No. checked |
| **R8 landmark self-morphs** `/dev/shm/smad_arms/r8_cv`, `r8_fm` (`smadcvpr/build_arms.py`) | OpenCV (`scripts/78_tool_morph.py`) and FaceMorpher (`scripts/96_facemorpher_tool.py`) morphs of **two distinct captures of one train90 subject** | 2,500 per tool (FERET 896, FRGC 1,604); FERET 518 and FRGC 495 subjects; `r8_pairs.csv` lists the pairs | local CPU (ARM) | not verified | **Yes.** This is a ready landmark twin set, but it is **in RAM (`/dev/shm`) and lost on reboot**, and its subjects were used in A8-W1F training with label 1. checked |
| R6 extra FRGC stills `/dev/shm/smad_arms/r6_frgc` | Controlled FRGC stills of train90 subjects | 4,223 (490 subjects) | — | — | n/a (bona fide pool). checked |
| Landmark tools in code | OpenCV (78), FaceMorpher (`baselines/face_morpher`, 96), WebMorph (`baselines/webmorph`, PHP, + `72_align_morph.R`), MediaPipe + Poisson (`h1_build.py`), dlib-68 (`baselines/dlib68`), SBI-int self-blends (A8-W1F), AMSL outputs only (`baselines/amsl_out`) | — | OpenCV, FaceMorpher, MediaPipe: CPU, ran locally. WebMorph: not verified | not logged | The R8 pairs came from 78 + 96. checked (listings) |
| own_generation_v1 | Planned full matched GAN/DiffAE pool builder (1,500 FERET/FRGC pairs) | not built | — | — | Status **BLOCKED** pending review (README). checked |

---

## D. Genuine-photo pools with at least two photos per person

| Pool | Path | Identities / images (directory counts) | Frontal / studio | Use so far (identity-overlap risk) | Mark |
|---|---|---|---|---|---|
| **FRGC 2.0** stills | `/mnt/t7/Datasety/FRGC-2.0/FRGC-2.0-dist/nd1/{Fall2002,Fall2003,Spring2003,Spring2004}` | **568 subjects, 39,328 JPG**, all with ≥2 images (multiple sessions) | Mix of controlled studio and uncontrolled stills. The split is in BEE signature sets (`BEE_DIST/FRGC2.0/signature_sets`), not counted here | **Training:** train90 subjects in `train.csv` (bona_frgc 1,686 + FRGC morph arms), R6 (490 subjects), R8 (495), GAN32 / expanded123 train_fit blocks, ABC60 data. **val10 subjects** (sha1 rule, `prep_train.is_val`) feed VAL-X (sealed). There is no unused FRGC identity outside val10 | checked (counts); not verified (controlled count) |
| **colorFERET** | `/mnt/t7/Datasety/colorferet/dvd{1,2}/data/images` | **994 subjects, 11,338 images**; fa 1,364, fb 1,358; 993 subjects with ≥2 frontal (fa + fb, same session, expression change); **250 with ≥2 fa (different sessions)** | fa/fb frontal studio; the other codes are poses | Training as FRGC: train90 (`bona_feret` 2,400 + morph arms), R8 (518 subjects), GAN32 / expanded123. Subset copy at `downloads/feret_bonafide` (166 subjects, 356 JPG) | checked |
| **FRLL** | `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front` | **102 persons × 2 = 204 frontal**, plus 8 profile/3-quarter folders × 102 | Studio, 1350², frontal neutral + smiling | **Bona fide of every test benchmark** (MAD22, FRLL-Morphs, MorDIFF, DiM). Already used for A41 self-morphs and A43 C/C20, and for the E7 photos. Test-only; never a training identity | checked |
| **FEI** | `/mnt/t7/Datasety/downloads/FEI/extracted` | **200 subjects, 2,800 JPG** (14 each: pose series plus frontal neutral / smiling) | Studio; frontal neutral + smiling | **Test:** `gtest.csv` (FEI bona neutral 198 / smiling 187 + 1,000 StyleGAN W+ morphs) and the A36 render-vs-camera FEI pool. Disjoint from FERET/FRGC by construction | checked |
| **Multi-PIE** (third-party crop release, not the official distribution) | `/mnt/t7/Datasety/downloads/multipie/multipie.zip` (+ `probe/`) | **249 subjects**, 129,480 HR 128×128 crops (+ the same count of 4× nearest-neighbour LR copies); 13 cameras, frontal camera 051: 9,960 | Studio, but **128 px only** (too small for 512-frame morphs) | Unused; rejected in A23 (P l.7357) | checked |
| **CASIA-WebFace** | `/mnt/t7/Datasety/downloads/CASIA-Webface/train.rec` (insightface 112×112 RecordIO) | **10,572 identities**, about 501k index entries | In the wild, 112² | **Test:** source identities of H1, H2, H3, H4/H4b and Arc2Face (8,488-identity table, sets disjoint from each other). **SPL-MAD's release was trained on CASIA-WebFace**, so CASIA-based sets overlap with that release | checked |
| FFHQ-1024 | `/mnt/t7/Datasety/downloads/FFHQ-1024` | 70,000 images, **no identity labels** (one photo per person) | In the wild | Unsuitable for same-person pairs. StyleGAN and SMDD generators were trained on FFHQ; test via `ffhqm` | checked |
| FLUXSynID | `/mnt/t7/Datasety/downloads/FLUXSynID/FLUXSynID.zip` | 89,361 files; synthetic identities with multiple images (per-identity count not verified) | Synthetic | Rejected in A23 | partly checked |

**Identity-overlap summary.** For the SMDD-trained releases (MADation, MixFaceNet, SelfMAD is not verified), FERET, FRGC and FEI are unseen identities. For our d1, R8 and ABC networks, nearly every multi-capture FERET/FRGC subject is a training identity. The only held-out FERET/FRGC subjects are val10, which belong to sealed VAL-X. FRLL's 102 persons are the benchmark's bona fide.

---

## Blockers found

1. **No score exists on the fixed MAD22.** canonical164 was cancelled. The processed inputs differ in bytes from the old inputs, so nothing can be merged. The raw manifest sits in `/tmp/opencode`.
2. **The SelfMAD release is not on this machine** (WCSS `A12REL` only). SPL-MAD would need a download.
3. **No CNN method reproduced** (Inception, MorphHRNet, PW-MAD, OrthoMAD, MixFaceNet retrains). MixFaceNet release agreement is conditional, and its MTCNN crop branch is suspended.
4. **The R8 landmark twin set (5,000 images) is only in `/dev/shm`.** Its subjects are training identities.
5. **There is no identity-disjoint FERET/FRGC pool for our own networks** outside sealed val10. FEI (200), FRLL (102, benchmark) and Multi-PIE (128 px) are the alternatives.
6. **StyleGAN3 inversion has only run on x86** (WCSS, Vast). It is not verified on the GB10. DiffAE does run on the GB10, which contradicts plan item D4.
