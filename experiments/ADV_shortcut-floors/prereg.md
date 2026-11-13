# Shortcut floors of the standing adversary (ADV): registration

Written 13 Nov 2026 from about 19:00 CET (machine clock, `date`) by the standing adversary (ADVERSARY role,
OWNER_BRIEF.md "Five standing roles", item 3), before any floor in this folder is computed. Binding at the git commit
that adds this file under this name. Code: `src/adversary/`. Large outputs: `/mnt/t7/smad_next/ADV/`. CPU only, on the
DGX, with the thread caps of OWNER_BRIEF.md; no GPU, no cluster job.

## 0. Stance, authority and what was known at writing

- **Stance.** Every gain a network shows on a contrast is treated as a shortcut until the strongest shortcut-only model
  fitted on the same rows fails to match it. From the release of these floors, a registered gain counts only beside
  its floor (OWNER_BRIEF.md, item 3), and the floor is fixed (committed) before the arm is read.
- **Known at writing (disclosed).** The registrations named in section 4 (read in full: AB1 `prereg_fm.md`,
  `prereg_x.md`; GX1 `prereg.md` with amendments 1 and 1b; RZ1 `prereg.md`; BB2 `prereg.md` sections 5-6 and
  amendments 4-5, `PLAN_DINOV3_PROGRAMME_20261113.md`; SE1 `README.md`; the hand-made statistics code
  `src/PN1/baseline27.py`, `src/SE1/baseline27_se1.py`, `src/PN1/fs_read.py` `fmax`). The reviewed audit table
  `experiments/SA1_shortcut-audit-table/result.md` lines 1-156 and the evening conclusions
  (`18_EVENING_CONCLUSIONS_20261113.md`), which give: Sb's landmark_combined AUC 0.873-0.906 (seeds 408-412) against the
  best single hand-made statistic 0.886 (noise_std_face, in-sample) and the 27-statistic baseline 0.814 (trained on the
  ladder training hosts). **Not opened:** any result, score file or tar of the second-engine arm (SbFM), the
  border-crossed arm (Sbx), GX1, RZ1, the DINOv3 E3/E2 jobs or the SE1 H100 block; AB1 `result.md`; any `*_summary.json`
  or `*_mock*.json` of AB1. Nothing in this folder was computed before this commit except an 8-image smoke of the feature
  code (section 3) and a synthetic-data test of the fitting code (random features; no image).
- **What the adversary cannot do.** It never builds an image, never uses an image operation, never opens a closed or
  sealed set, never edits another owner's file. Attack sets (section 8) are requests to the DATA role through the lead.

## 1. Question

For each contrast that a queued arm will claim, how well does the strongest model that sees only shortcut features
(hand-made image statistics, border, resolution and enlargement proxies, storage, rendering and blend-energy cues)
separate the two sides of the contrast on the same development rows, cross-fitted so that no person is on both sides of
a split? That number is the arm's **shortcut floor**: a gain counts only if the network exceeds it.

## 2. Data (development only)

- Rows come only from the arms' own evaluation manifests, read without change:
  `/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv` (AB1's 21,277 rows + 3,582 border rows; SbFM, Sbx, GX1's guards and
  RZ1 are read on it; E3's landmark_combined and splice rows are the same images in `pn1_eval.csv`) and
  `/mnt/t7/smad_next/PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv` (PR1 GD0/GD1/GD2: FFHQ-Morphs StyleGAN/DiffAE
  families, development by the author's ruling of 12 Nov; DG1 diffusion ladder and AG1 MIPGAN controls on FRGC/FERET
  ladder hosts). Training rows (section 5.3) from the arms' training manifests: `PN1/manifests2/train_Sb.csv`,
  `train_A.csv`, `AB1/x/manifests/train_Sbx.csv`, `AB1/fm/manifests/train_SbFM.csv`. Images are the stored 512 px
  frames of the packs (unpacked trees on `/mnt/t7/smad_next/`, resolved by relative path).
- Never opened: FRLL, FRLL-Morphs, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace, `manifests/valx.csv`, FST, A12SP; no
  file whose name contains `fst`, `valx`, `A12SP`. `contrasts.py` refuses any row whose id or path contains one of
  those names. The PN1 catalogue (`pn1lib.catalog`, which lists benchmark files) is not used; person keys come from the
  split files and the AF0/AR1 lists.
- Person split: a row's persons are its manifest host (FFHQ morph pairs split on `_`, MS1 pairs on `|`), plus the
  partner for two-person rows (ladder `partner_B`; AF0 manifest `pid_A`/`pid_B`, also for halves and stored copies).
  Connected components of the person graph are the units of folds and bootstraps.

## 3. Features (fixed now; `src/adversary/feats.py`)

On the stored 512 x 512 frame as the packs hold it (cv2.imread, RGB), 62 values in six families:

| Family | Values |
|---|---|
| F27 | the 27 hand-made statistics of the reviewed floors: 26 `smadcvpr/cue_floor` statistics + PNG bytes, through `src/AF0/cues_all.one` imported unchanged (sha256 1ab50f30… asserted, as `src/PN1/cues27.py`). Smoke: identical (max abs difference 0.0) to the cached `PN1/cues/a14_lcomb.npz` on 8 landmark_combined frames. |
| BORDER | edge-connected exactly-black fraction (`src/TT1/build_border_ref.edge_mask`, unchanged), black depth of each of the four sides, content bounding-box fraction, mean luma at the content boundary |
| RES | radial-spectrum cut-off frequency at 95 / 99 / 99.9% of the power, face box and whole frame; implied enlargement 0.5 / f99 (face box); content scale |
| STORE | PNG bytes per content pixel; 8x8 blockiness maximised over the 64 grid offsets and its ratio to the median offset (a JPEG grid that survived); DCT quantisation-comb score and step |
| RENDER | spectral peak excess at 1/4 and 1/2 cycles per pixel (up-sampling peaks), high-band tail spread, chroma noise-residual std (Cb, Cr), cross-channel noise-residual correlation R-G and G-B (demosaicing trace), residual kurtosis in the face |
| BLEND | secondary peak and lag of the face-box Laplacian autocorrelation at lags 2-16 px (ghosting), eye-region Laplacian and gradient energy, face / border gradient-spread ratio, left-right mirror difference of the face box, second- to first-derivative energy ratio in the face |

Measurement only: no image is written, no resampling, blur or compression of an image is computed. Native source
resolution and the true enlargement factor are not in the manifests; RES gives image-based proxies (stated as a
limitation). Code pins at this commit (sha256): `feats.py` 34716797…, `floor.py` 4e022c07…, `contrasts.py` c336c732…,
`run_floors.py` 38b56be1…, `check.py` f9019632… (full hashes in `pins.sha256`).

## 4. Contrasts and the rows each floor is fitted on

Positive side first (the side the arm should score higher); counts are rows. "printed" = context for the arm's printed
reads, no rule attached beyond section 6.

| Arm (order of first reads) | Registered read | Floor contrast (`contrasts.py` name) | Rows |
|---|---|---|---|
| Second-engine arm (SbFM, AB1) | H-fm1 (primary) | FFHQ landmark_combined orig vs resmatch (`lcomb`) | 1,000 / 2,000 |
| | H-fm2 | test-ladder FaceMorpher R4 vs FaceMorpher R2w (`test_fm_R4_vs_R2w`) | 191 / 573 |
| | H-fm3 (guard) | test-ladder OpenCV R4 vs OpenCV R2w (`test_cv_R4_vs_R2w`) | 573 / 573 |
| | printed engine table | test and development R4 vs R2w and R4 vs R3, both engines (`test_fm_R4_vs_R3`, `test_cv_R4_vs_R3`, `dev_fm_R4_vs_R2w`, `dev_fm_R4_vs_R3`, `dev_cv_R4_vs_R2w`, `dev_cv_R4_vs_R3`) | 100-573 per side |
| Border-crossed arm (Sbx, AB1) | H-x1 (border flags, a flag-rate read) | separability of the 1,582 border-blanked development camera photos from their 226 unbordered originals (`border_vs_cam`); FFHQ border vs FFHQ native (`border_ffhq_vs_ffhq`); and the same-data shortcut learner's border flag shares (section 5.3) | 1,582 / 226; 2,000 / 2,000 |
| | landmark_combined guard | `lcomb` | as above |
| GAN arms (GX, GXp; GX1) | primary R4 vs R3, held-out development hosts (amendment 1) | `gx1_R4_vs_R3` on the admitted held-out rows of `gx1_eval.csv`, computed when the GX1 owner commits `pins_images.sha256` and the evaluation manifest, and before any GX1 fit tar is fetched (section 7); until then the existing analogue on the AG1 controls `gd2_R4_vs_R3` | 74 / 119 (analogue) |
| | secondary R4 vs R2 (s1) | `gx1_R4_vs_R2` (same timing); analogue `gd2_R4_vs_R2` | 74 / 238 (analogue) |
| | transfer reads | GD0 StyleGAN w / w+ orig vs resmatch (`gd0_sgw_vs_resmatch`, `gd0_sgwp_vs_resmatch`) | 1,000 / 2,000 each |
| | landmark_combined guard | `lcomb` | |
| Resolution and resize study, wave 1 (RZ1) | detection guards (H-mix4d, H-mix5), H-512a later | `lcomb` on the stored frame (the 512 arms see exactly this frame; for the 224 arms RZ1 registers its own floor on the resized input, and this floor is the frame-level companion) | |
| | storage reads (H-mix1-4, C2P rows) | separability of stored from native genuine photos and of stored morphs from stored photos at the same size: `store_photo_fm61_vs_native`, `store_photo_amsl112_vs_native`, `store_morph_vs_photo_fm61`, `store_morph_vs_photo_amsl112`; plus the same-data shortcut learner's flag rise on the stored copies (section 5.3) | 291 / 300, 290 / 300, 150 / 291, 149 / 290 |
| DINOv3 programme (BB2 E3, E2) | E3 contrast 1 | `lcomb` | |
| | E3 contrast 3 | test-ladder face-only S4_bg vs S0_bg (`test_S4bg_vs_S0bg`) | 191 / 191 |
| | E3 splice-fit gate (training AUC lad_S4 vs lad_S3) and E2 linear probe (lad_S4 vs lad_S3, lad_S4 vs lad_S0, StratifiedGroupKFold by person) | the same training rows of `train_Sb.csv`, cross-fitted by person (`train_lad_S4_vs_S3`, `train_lad_S4_vs_S0`) | 124 / 156 each |
| Frozen candidate (Sb), the 20 audit rows (SA1), development data | row 1 storage of genuine photos | `store_photo_*_vs_native` | |
| | row 2 storage of morphs | `store_morph_vs_photo_*`, `ms1_morph_vs_photo_native` | |
| | row 3 JPEG history | not computable: no development JPEG pool exists (SA1 3-A); not built | — |
| | row 4 unseen camera source | not in this registration (the TT1 pack rows are not in ab1x_eval; an amendment may add them); context only: `af0_dev_u50_vs_photo`, `hn2_lcomplete_vs_bona` | |
| | row 5 border | `border_vs_cam`, `border_ffhq_vs_ffhq` | |
| | row 6 warp only | `dev_cv_R4_vs_R2w`, `dev_cv_R4_vs_R2w4` | 300 / 100 each |
| | row 7 same-person morph | `dev_cv_R4_vs_R3`, `dev_cv_R4_vs_R3m` | 300 / 300, 300 / 100 |
| | row 8 same-person splice | `dev_S4_vs_S3`, `test_S4_vs_S3` | 100 / 100, 191 / 191 |
| | row 9 seam only | `dev_S4_vs_S0` | 100 / 100 |
| | row 10 crop path | not computable on these rows (geometry references are TT1 rows); n/a | — |
| | row 11 data volume | n/a (no contrast) | — |
| | row 12 surround blend | `dev_R4face_vs_R2wface` (face blanked: surround only) and `dev_S4bg_vs_S0bg` (face only) | 100 / 100 each |
| | row 13 diffusion render path | `gd1_X_vs_REC` (two-person diffusion morph vs one-photo reconstruction), `gd1_X_vs_SAME`, context `gd0_diffae_vs_resmatch` | 191 / 191 |
| | row 14 GAN one-person render | `gd2_R4_vs_R2`, `gd2_R4_vs_R3` | 74 / 238, 74 / 119 |
| | row 15 SMDD partner trace | n/a for our arms (not SMDD-trained) | — |
| | row 16 FRLL smiling half | not computable: benchmark set | — |
| | row 17 softness | covered by F27/RES on every contrast (Laplacian variance, band powers, cut-offs); no separate contrast | — |
| | row 18 FFHQ landmark_combined | `lcomb` | |
| | row 19 operating point | n/a (no two-class contrast) | — |
| | row 20 morph engine | `test_fm_R4_vs_R2w`, and the same-data shortcut learner trained on OpenCV-only rows (train_Sb) read on FaceMorpher rows | |

## 5. Models (fixed now; `src/adversary/floor.py`)

### 5.1 Cross-fitted floor on the contrast's own rows (the registered floor)

- Folds: `StratifiedGroupKFold(n_splits = 5, shuffle = True, random_state = 20261113)` over person components (fewer
  folds only if a side has fewer than 5 components). Missing or infinite values: training-fold median.
- **single:** on each training fold, the statistic and sign with the highest training AUC; held-out values mapped
  through that fold's empirical CDF so that the five folds pool on one scale.
- **logreg:** StandardScaler + LogisticRegression(C = 1, class_weight balanced, max_iter 3000), all 62 features.
- **gbt:** HistGradientBoostingClassifier(max_iter 200, learning_rate 0.05, max_leaf_nodes 15, min_samples_leaf 20,
  l2_regularization 1.0, class_weight balanced, early_stopping off, random_state 0), all 62 features.
- AUC and EER on the pooled held-out scores; 95% interval by 2,000 draws of person components with replacement
  (numpy default_rng(20261114)), conditional on the fitted folds.
- **The floor** of a contrast = the highest of the three cross-fitted AUCs (the choice of the maximum favours the
  adversary, as intended); its model is named. No tuning beyond these fixed settings.
- Printed with it: the in-sample best single statistic (the reviewed `fs_read.fmax` convention, max over the
  statistics of max(AUC, 1 - AUC) on all rows; optimistic), the same over F27 only, logreg on F27 alone (continuity with
  the 27-statistic baseline), each family alone (gbt and logreg), and leave-one-family-out AUC with the floor's model
  (gbt when the floor is `single`). **Carrying family** = the family with the highest family-alone AUC.

### 5.2 Why cross-fitted on the evaluation rows

The networks never see the evaluation rows; the shortcut model is fitted on them (on other persons). That is an
advantage for the adversary, on purpose: a network gain that does not exceed what shortcut cues reach in-distribution
on the same rows is not evidence of a morph signal. A network that exceeds it has shown something no listed shortcut
explains on these rows; it has not shown that it uses no shortcut.

### 5.3 Same-data shortcut learner (printed; for flag-rate reads)

For reads that are flag rates, not two-class contrasts (border flags, storage rise, same-person placement, engine
transfer), the floor is "what a shortcut-only learner trained on the arm's own training rows does": logreg and gbt
(settings above) fitted on the unique training rows of `train_Sb`, `train_A`, `train_Sbx`, `train_SbFM` (labels from
the manifests, each image once), applied to the evaluation rows; printed per pool: own-rule flag share (logreg decision
> 0; gbt probability > 0.5) and AUC on every contrast of section 4. Pools: border-blanked camera photos and their
originals, FFHQ border and native, MS1 hold-out natives and their fm61 / amsl112 copies (photos and morphs), development
S0 / S3 / S4, R3 (both engines), FaceMorpher R2w / R2w4 / R4, OpenCV R4, development R0 and AF0 photos, landmark_combined
morphs and genuine, GD2 R2 and R4. Printed only; no verdict attaches to it.

## 6. What an arm must exceed (the rule other owners apply)

- **Per network and contrast:** the network **exceeds its shortcut floor** if the 2.5% bound of (network AUC - floor
  AUC), re-taken in the same draw of person components (2,000 draws, numpy default_rng(20261115)), is above 0; scored on
  exactly the rows of `floors/<contrast>_heldout.csv`, against the floor model's held-out scores. Implementation:
  `src/adversary/check.py` `exceeds()`. Quick bar printed in FLOORS.md: the floor's upper 95% bound (a network point
  AUC below it cannot exceed).
- **Per arm:** a registered gain or hypothesis verdict counts as beyond the shortcut floor only if the arm's network
  exceeds the floor on the seeds its own registration requires (its own seed counting: ≥ 4 of 5, 4 of 4, 2 of 3 ...).
  Otherwise the verdict is reported with the words "within the shortcut floor" beside it. A difference between two
  arms (for example SbFM - Sb ≥ +0.02) is reported as a gain beyond the floor only if the better arm exceeds the floor;
  if neither does, it is "a gain within the shortcut floor".
- **The floor does not change an arm's own verdict**: the arm's registered verdict stands as registered; the floor
  verdict is printed beside it.
- For the GX1 primary contrast the GX1 registration already has its own cue floor F (AG1 statistics and a logistic
  on them, trained on GX1 training R3/R4 rows); this floor is printed beside F; GX1's rule uses F.

## 7. Timing: floors fixed before arms are read

- Order of computation: the features (`feats`), then the stage-1 floors (the contrasts of SbFM, Sbx, the GX1 analogues,
  RZ1 wave 1, E3/E2), committed with FLOORS.md lines; then the stage-2 floors (the audit rows); then the same-data
  learner. Each commit is made as soon as its JSON exists. The arms' reads are no earlier than their fits' end
  (SbFM, Sbx, GX1, RZ1: latest 15 Nov 18:00; E3 fetch by 14 Nov 18:00): stage 1 is committed tonight.
- **If an arm is read before its floor is committed,** that floor is still computed and committed, but labelled
  "after the arm's read" in FLOORS.md, and the adversary states whether it had seen the arm's result (it will not
  look).
- GX1's own floor (`gx1_R4_vs_R3`, `gx1_R4_vs_R2`) is an amendment to this file, computed from the admitted frames
  after the GX1 owner commits `pins_images.sha256` and `gx1_eval.csv`, and committed before any GX1 fit tar is
  fetched (the GX1 owner is asked, through the lead, to wait for that commit before fetching).
- The adversary never opens an arm's scores. `check.py` is for the arm owners' readers.

## 8. Attack sets (requests to DATA through the lead; nothing is built here)

Two or three image sets per arm that would break the arm's claim if it rests on a shortcut, using only allowed
operations (approved warp `h1_build.py`, unchanged OpenCV / FaceMorpher morphers, constant-colour region blanking,
existing E7 outputs, lossless PNG). Listed in FLOORS.md, section "Attack sets", for the lead to route.

## 9. Limits stated now

- The floor is a floor of the listed families only; a network can use a shortcut that none of them measures.
- RES gives image proxies for native resolution and enlargement; the true source sizes are not in the manifests.
- The bootstrap is conditional on the fitted folds (no refitting per draw).
- Rows with few persons (GD2 R4: 74 rows) give wide intervals.
- One floor per contrast; no multiplicity correction across contrasts.

## 10. Budget and commands

CPU only: about 32,000 frames at about 0.3 s each with 2 worker processes (about 1.5 h), then the fits (minutes per
contrast). Commands (all `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/adversary/run_floors.py ...`):

```
feats --set ab1x ; feats --set train ; feats --set gd12 ; feats --set gd0     # tested: feats --set ab1x --limit 8
floors --stage 1 ; floors --stage 2 ; transfer ; table
```

## 11. Pre-run check

Requested from the lead before the first floor is computed (task instruction). Result and fixes are recorded below as
an amendment before any floor is committed.
