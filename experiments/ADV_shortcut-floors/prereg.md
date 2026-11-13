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

## Amendment 1 (13 Nov, before any floor is computed): pre-run check fixes, RI1/TB1 floors, relation to RZ1's floor

Pre-run check: experiment-reviewer (Opus), GO WITH FIXES, on 4a0abb0 (findings F1-F10; the lead was told). Applied:

- **F1 (blocker), ladder rows.** `ab1x_eval.csv` holds every ladder rung three times (native, `strength` 61, 112). The
  ladder selectors now require `strength = ""`, as the arms' readers do (`ab1fm_read.py` asserts 191 test / 100
  development rows per rung). Corrected counts in section 4: test R4 vs R2w and R4 vs R3, both engines, 191 / 191;
  development R4 vs R2w, R2w4, R3, R3m, both engines, 100 / 100. The ladder pools of section 5.3 take natives only.
- **F2 (blocker), GD2 persons.** GD2 (AG1 MIPGAN) rows take their persons from `AG1/data/manifests/ag1.csv`
  (`pa`, `pb`, matched by the source file name), not from the ladder partner table: 57 person components, as the
  reviewer counted. GD1's partners match the ladder table (0 mismatches) and are unchanged.
- **F3, both sides genuine.** `border_vs_cam`, `border_ffhq_vs_ffhq`, `store_photo_fm61_vs_native`,
  `store_photo_amsl112_vs_native` are **separability ceilings** (how visible the nuisance is to shortcut features),
  with no "exceeds" rule (`check.py` refuses them). For flag-rate reads (H-x1, RZ1 storage) the comparison is the
  section 5.3 same-data learner's flag share. Every contrast also prints a **pixel-only floor** without the two
  file-size values (`F27:png_bytes`, `STORE:png_bytes_per_px`), because the PNG encoder differs between some sides
  (bordered copies were written by another script); the registered floor stays the full one, the pixel-only one is
  printed beside it.
- **F4, E3 gate.** `train_lad_S4_vs_S3` / `_S0` bind only for E2's out-of-fold linear probe. Beside E3's splice-fit
  gate (an in-sample training AUC) an in-sample gbt AUC on the same rows is printed as context; no rule.
- **F5, labels.** Every stage-2 floor for the frozen candidate (Sb, already read) is labelled "after the frozen
  candidate's read; features designed with Sb's landmark_combined value known". The stage-1 arms (SbFM, Sbx, GX1, RZ1,
  E3, E2) are unread at this amendment.
- **F6, F7.** Held-out scores written at full precision; `check.exceeds` asserts that the held-out file reproduces the
  committed floor, rejects non-finite network scores and returns the git blob hashes of the floor files it read.
- **F8 (limitation, not changed).** The DCT comb statistic uses blocks offset by one pixel from the blockiness grid
  it follows; this can only weaken the floor. Features are not recomputed.
- **F9.** A fold with no usable column or one class returns 0.5 instead of failing.
- **F10.** R2w4 rows (warped toward the partner's geometry) link the partner. `af0_dev_u50_vs_photo` has 26
  components: context only. E3's fetch deadline is 15 Nov 18:00 (BB2 amendment), not 14 Nov. GX1's secondary analogue is
  `gd2_R4_vs_R2s1` (R2 on s1 only, 74 / 119); `gd2_R4_vs_R2` (s1 and s2) is printed.

**Added contrasts (lead's message of about 19:20): regional identity (RI1, d4ebfd9) and texture band profile (TB1).**
On the 291 BD1 hosts (191 test + 100 development, native rows), the same models and rules:
`ri_R4_vs_R3` (OpenCV R4 vs R3, 291 / 291), `ri_R4_vs_R0` (OpenCV R4 vs camera photo R0, 291 / 291),
`ri_S4_vs_S3` (291 / 291) with **within-D quintiles** printed by BD1's primary rule (quintile edges of log D over the
pooled rows; AUC per stratum on the floor's held-out scores; mean weighted by n_pos × n_neg over strata with ≥ 10 of
each class; D = `D_ac` of `/mnt/t7/smad_next/BD1/d_feats.csv`, with the pure-D reference beside it). The same within-D
print is added to `dev_S4_vs_S3` and `test_S4_vs_S3`. TB1's premise P is read on half-differences (not images any
network sees) and gets no adversary floor. These floors are announced to the lead as **pending**; RI1 and TB1 keep
their own registered 27-statistic floors as binding; the adversary floor is printed beside them (section 6).

**Relation to RZ1's floor (RZ1 3c3470d, M3).** RZ1's binding floor is 0.886 (the in-sample best single statistic at
full resolution) with input-matched floors printed. The adversary does not duplicate those: its `lcomb` floor is on the
stored 512 frame, cross-fitted, with all six families; for the 512 arms it is the same input, for the 224 and crop arms
it is the frame-level companion. It is printed beside RZ1's floors; RZ1's binding rule is unchanged. The same holds for
BB2 (fs_read fmax 0.886 binding, adversary printed) and GX1 (its own F binding).

## Amendment 2 (13 Nov, before any floor is computed): the lead-ordered pre-run check (`experiments/reviews/PRERUN_ADV_LEAD_20261113.md`, 112d50c)

GO WITH FIXES, no blockers. The owner-launched check that led to amendment 1 is saved as
`experiments/reviews/PRERUN_ADV_SELF_20261113.md`. Registered now (what amendment 1 already did is not repeated):

- **F1, order.** Stage 1 is split: **stage 1a** = `lcomb` and the four test-ladder contrasts (`test_fm_R4_vs_R2w`,
  `test_cv_R4_vs_R2w`, `test_fm_R4_vs_R3`, `test_cv_R4_vs_R3`), computed and committed first, with the commit hash
  posted in README.md; the lead holds every SbFM, Sbx and RZ1 read until then. Then stage 1b (the rest of section 4's
  stage-1 rows), then the RI1/TB1 rows (amendment 1 and F6 below), then stage 2 and the same-data learner.
- **F2, frozen files.** Each stage commit adds `floors/pins_stage<k>.sha256` over its JSON and held-out CSV files
  (`run_floors.py pins`). `check.exceeds` refuses a floor file whose sha256 is not listed in a pins file that is
  tracked by git and unmodified.
- **F3, name and regression gate.** The bar is called **the ADV floor** everywhere. An arm's own registered floor
  (RZ1's 0.886, GX1's F, RI1's and TB1's 27-statistic floors, BB2's fs_read floor) remains the only floor in that arm's
  verdict; the ADV floor is printed beside it and never replaces it. "Within the ADV floor" is internal-record wording
  until the author decides on paper prose. **Regression gate:** on `lcomb` the in-sample best single statistic over F27
  must reproduce 0.886 (noise_std_face) to 3 decimals; otherwise no floor is committed (asserted in `run_floors.py`).
- **F4, nuisance floor.** The all-cue ADV floor contains blending statistics (BLEND, and blend-sensitive F27 values),
  which are morph signal. Beside it every contrast gets the **nuisance floor**: the same three models on the BORDER,
  RES, STORE and RENDER families only (no F27, no BLEND); its held-out scores are in the `nu_*` columns and
  `check.exceeds(..., floor="nuisance")` applies the same rule. Reading (internal record): beyond the nuisance floor
  but within the all-cue floor = "not beyond hand-made morph statistics; not explained by nuisance cues"; within the
  nuisance floor = "not shown beyond nuisance cues".
- **F5.** `train_lad_*` floors are context only; no exceeds rule for E3's in-sample gate; for E2's probe only if E2
  uses the ADV components and fold seed (it does not: E2 uses random_state 0), so for E2 the floor is printed context.
- **F6, RI1/TB1 rows.** On the 291 BD1 hosts (natives): `ri_S4_vs_S3` (all 291, the RI1 and TB1 S4-vs-S3 read, with
  D-quintile strata), `ri_R4_vs_R3`, `ri_R4_vs_R0`, and the controls `ri_R0s61_vs_R0` (stored small vs camera photo),
  `ri_S0_vs_R0`, `ri_R2w4_vs_R0` (separability ceilings: the arm should not separate them). **D** is BD1's D, defined in
  `experiments/BD1_blend-difference-attribution/prereg.md` line 30 ("mean over hull pixels and the 3 channels of
  |S − counterpart| on the stored 512 px PNGs"), values in `/mnt/t7/smad_next/BD1/d_values.csv` column `D` (the lead's
  correction; amendment 1's `D_ac` of `d_feats.csv` is withdrawn). TB1's S4-vs-S3 read gets this floor too; both are
  pending until committed.
- **F7.** Arm differences are also printed as AUC difference within quintiles of the floor's held-out score
  (`check.diff_within_floor_quintiles`), printed only.
- **F8.** Stage-2 floors on the frozen candidate's audit rows are labelled post hoc (amendment 1 F5 label).
- **F9.** `check.py` uses numpy ranks only; `feats.py` asserts the sha256 of `smadcvpr/cue_floor.py` (556e7aba…) and
  `src/TT1/build_border_ref.py` (36605880…) besides `cues_all.py`.
- **F10.** PNG container facts parsed from the file bytes join the STORE family: number of IDAT chunks and their mean
  size, zlib level flag, number of ancillary chunks, colour type, share of each scanline filter type (0-4) — 10 values,
  so 72 features in all. They are file-provenance cues (the bordered copies, for example, were written with zlib level 0
  and filter 1 only); they are excluded from the pixel-only floor. The bootstrap holds the folds fixed (section 9).
- **Feature code note.** The 62 cached image values were computed by `feats.py` at 4a0abb0 (34716797…); the edits after
  it add the pins and `pngmeta` only and change no image value.

## Amendment 3 (13 Nov, from about 20:10; POST HOC: after the stage-1a floors and their post-result review `experiments/reviews/REVIEW_ADV_STAGE1A_20261113.md`, 6f7c181; no arm score opened)

1. **Name.** The amendment-2 "nuisance floor" (BORDER, RES, STORE, RENDER) is renamed **non-F27/non-BLEND floor
   (contains face-box texture)**: RES cut-offs and RENDER residual statistics are partly measured on the face box,
   which blending changes (proof: test R4 vs R2w, same pipeline and photos, reaches 0.986-0.996 on it). Its files keep
   the key `nuisance_floor` and columns `nu_*`; `check.exceeds(floor="nuisance")` keeps working under the new name.
2. **Region floors** (`feats.regional`, `run_floors.py regionfloors`): 18 measures (noise residual std of luma and of
   each channel, residual cross-channel correlations, chroma noise, Laplacian variance, gradient energy, residual
   kurtosis, mean and std of luma, black fraction, four spectral band powers) computed separately on the **surround**
   (cue_floor's border ring: top 64 rows, left and right 64 columns, without black pixels and a 2-px edge; bands from
   the top strip) and on the **face box** (cue_floor's canonical box); plus the **file floor** (PNG size and container
   values). Same three models, folds and bootstrap. Written to separate files `floors/<name>_regional.json` and
   `_regional_heldout.csv` (columns `surround_*`, `face_*`, `file_*`); the pinned stage files are not rewritten.
   Computed for every stage-1 contrast as the region features become available.
3. **lcomb_bal (history-balanced 1:1 subset; `src/adversary/balance.py`).** Disclosure of timing: the build rule was
   **not** committed before the builds ran. Two builds ran between about 20:17 and 20:24 (machine clock), both before
   this amendment. Build 1 matched on the logit of the cross-fitted **logreg** surround score plus pre_ied (greedy 1:1,
   caliper 0.2 SD, × 0.7 per round, stop when the refit surround and file floors are ≤ 0.60 for single, logreg and gbt,
   at most 12 rounds): it did not converge (gbt surround floor 0.80 → 0.76 → 0.73 while pairs fell 335 → 167 → 61 →
   5; it crashed at 5 pairs). Build 2 changed one thing, the matching score, to the **gbt** cross-fitted surround score
   (the logreg score cannot balance what the boosted trees see), and added the stop "fewer than 50 pairs": it
   converged in two rounds with **125 morphs and 125 genuine photos** (round 0: 256 pairs, surround floor single /
   logreg / gbt 0.534 / 0.592 / 0.631; round 1, caliper 0.14: 125 pairs, surround 0.474 / 0.565 / 0.524, file 0.444 /
   0.466 / 0.460). A third run only added the pair column and the face floor to the outputs (same rows). The rule is
   now fixed as build 2 (balance.py eb2d237d…) and is not changed to reach 150 per class: it is **below 150 per
   class**, so a consumer with that bar reads "not read". Face-box floor on lcomb_bal: single 0.876, logreg 0.941, gbt
   0.936 (≥ 0.80). The round-0 score is computed inside balance.py with the same folds as
   `floors/lcomb_regional_heldout.csv` (identical by construction; gbt column there `surround_gbt`).
   Outputs: `floors/lcomb_bal_rows.csv` (id, label, pair), `floors/lcomb_bal_build.json`, and the full floor report
   `floors/lcomb_bal.json` (contrast `lcomb_bal`) with its region floors `floors/lcomb_bal_regional.json`.
4. **lcomb_ipw (weights over all 3,000 rows; `src/adversary/ipw.py` 5d15fa61…), registered here before it is
   computed (lead's specification).** Propensity: unpenalised logistic regression of the label on [logit of round-0
   `surround_logreg` from `floors/lcomb_regional_heldout.csv`, pre_ied, pre_ied²] (standardised, all rows).
   Stabilised weights P(class) / p(class | x), propensity clipped at its own 1st and 99th percentiles. Reported:
   weighted cross-fitted surround, file, face-box and all-cue floors (single, logreg, gbt; trained with the weights,
   weighted AUC on held-out rows), effective sample size per class. **Usable** only if the effective sample size is
   ≥ 300 per class and the weighted surround floor is ≤ 0.60 for both logreg and gbt; otherwise published as
   "not usable". Outputs `floors/lcomb_ipw_weights.csv` (id, label, weight), `floors/lcomb_ipw_build.json`, pinned.
   Not re-tuned after it is seen.
5. **Same-data shortcut learner (section 5.3) brought forward**: computed now, before stage 2 (it is the fair
   comparator for networks that never saw landmark_combined).
6. **R4 vs R3 within BD1's D quintiles.** R4 and R3 rows take the D of their host's S4 and S3 splice (inside the hull
   S4 equals R4 and S3 equals R3; BD1 prereg line 30; `d_values.csv` column D); the floors' held-out scores are read
   within D quintiles by BD1's rule. OpenCV only: FaceMorpher has no splices and so no D (not computable).
7. **Matched subsets replace the quintile print**: `check.diff_on_matched` (1:1 greedy matching of positives to
   negatives on the floor's held-out score, caliper 0.1 SD, default_rng(20261117); AUC difference of two networks on
   the matched rows with a person bootstrap). `diff_within_floor_quintiles` is withdrawn (degenerate on lcomb).
8. **Wording** in FLOORS.md as the review's section 5 gives it; "exceeds" on lcomb is predetermined and carries no
   information.
9. **Frames that are not 512 px** (GD1 DiffAE, 256 px) are measured on the networks' own loader view at 512
   (`smadcvpr` `common.ImageItems` through cue_floor, unchanged), the PR1 amendment-4 precedent; the 26 statistics
   reproduce PR1's cached GD1 cues exactly (max difference 0.0 on 8 frames).

## Amendment 4 (13 Nov, about 20:40 by the machine clock, committed in 1067700; descriptive, post hoc; registered before the two reads below are computed; review `experiments/reviews/REVIEW_ADV_STAGE3_STRATEGY_20261113.md`, 93f4210)

- **Naming.** The S4-vs-S3 and R4-vs-R3 floors (and their D-quintile reads) are **simple morph-cue floors**, not
  shortcut floors: blending two different people leaves colour, illumination and ghosting mismatch, which is a
  legitimate morph cue. "Shortcut" is kept for history, border and storage contrasts. `test_S4bg_vs_S0bg` is
  "face-only blend vs warp-only" (a blending contrast, not a ceiling). Every number from the inverse-probability weights
  (`lcomb_ipw`) is "uninterpretable (about 8 effective morphs)". lcomb_bal is "balanced to within detection power at
  n = 250".
- **Build disclosure, added.** The face-box floor on lcomb_bal was first printed by the third run, after convergence,
  with no change to the rows after it (the third run reproduced the same 250 rows). The stop "fewer than 50 pairs" was
  added after build 1 fell to 5 pairs.
- **Same-data shortcut learner** extended to every arm's own training list (Sb, A, B, SbZ, SbS, Sp, AS, SbH, SbR,
  SbnS0, SbH61, SbnS3, SbSp, SbFM, Sbx); unchanged models (section 5.3).
- **H-new-1 (descriptive).** On lcomb_bal rows, the cross-fitted floor (single, logreg, gbt; ADV folds) on the F27
  and BLEND families alone. The review's prediction: ≥ 0.90; falsified if ≤ 0.80.
- **H-new-3 (descriptive).** On R4 vs R3 (`ri_R4_vs_R3` and `test_cv_R4_vs_R3` rows), cross-fitted floors on two
  feature sets, read within BD1's D quintiles by the amendment-3 rule (host's S4 / S3 D): **chroma-only** =
  FACE:chroma_cb, FACE:chroma_cr, FACE:resid_corr_rg, FACE:resid_corr_gb, F27:sat_face; **luma-only** =
  FACE:noise_std_Y, FACE:lapvar, FACE:grad_energy, FACE:resid_kurt, FACE:mean_Y, FACE:std_Y, FACE:band0-3. The
  review's prediction: chroma-only ≥ 0.70 and luma-only ≤ 0.62 within D (best of the three models); falsified
  otherwise.
- The already-computed `*_withinD.json` (R4 vs R3 held-out floor scores within D, amendment 3 item 6) and
  `*_regional.json` files are committed and pinned as computed.

## Amendment 5 (13 Nov, committed 20:56:34 by git (61c6466); registered before computing; pre-run check of the selection rule `experiments/reviews/PRERUN_NEXT_SELECTION_RULE_V2_20261113.md`, 3d14793, findings 1, 2, 4, 10; code `src/adversary/amend5.py`)

1. **Per-row scores of the same-data learner.** For the training lists `train_Sb` and `train_SbFM` (GX when its
   manifest exists), the section-5.3 learner (logreg and gbt, unchanged) writes per-row scores to
   `floors/transfer_<arm>_rows.csv` (set, id, label, component, logreg, gbt) on three row sets: the 3,000
   landmark_combined rows (`lcomb`, components of `floors/lcomb_heldout.csv`), the 360 selection ladder rows
   (`sel360`, below, components of `floors/ri_R4_vs_R3_heldout.csv`) and the surround-matched rows (`lcomb_smatch`,
   below, components of `floors/lcomb_heldout.csv`), so that network minus learner can be bootstrapped in the same
   person-component draws.
2. **lcomb_smatch (a new, separately named product; not lcomb_bal, not for H-hb1).** 1:1 greedy matching of morphs to
   genuine photos on the logit of `surround_gbt` (`floors/lcomb_regional_heldout.csv`), caliper 0.1 SD (SD over all
   3,000 rows), morphs in numpy default_rng(20261117) permutation order, nearest genuine photo without replacement.
   Published: `floors/lcomb_smatch_rows.csv` (id, label, pair) and `floors/lcomb_smatch_build.json` with balance
   diagnostics refitted on the matched rows (surround, face-box, file and all-cue floors; single, logreg, gbt; ADV
   folds). Known limit, stated with every use: **surround-balanced only** (the face-box floor stays high, so history
   inside the face interior is not removed).
3. **sel360 and its within-D simple-cue floor.** Rows: the OpenCV R4 and R3 rows of `floors/ri_R4_vs_R3_heldout.csv`
   whose host is one of the 100 development hosts or one of the 80 test hosts of
   `/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv` (sha256 814c4486…). The floor's committed held-out
   scores (single, logreg, gbt) are read within D quintiles by BD1's rule with the quintile edges taken over these 360
   rows (D of the host's S4 / S3 splice), coverage printed; 95% interval by 2,000 draws of the file's `component`
   column (numpy default_rng(20261119)). Output `floors/sel360_withinD.json` and the row list `floors/sel360_rows.csv`.
4. Tree hygiene: amendment 4's header time corrected (committed 20:42:49 by git); transfer files of all arms committed
   and pinned (735a65e, stage 8); pins.sha256 refreshed with this commit.

## Note (13 Nov, 21:14 by the machine clock; text only)

Section 0 quotes "Sb's landmark_combined AUC 0.873-0.906 (seeds 408-412)": that is the candidate recipe at seeds
408-412 (AB1/result.md:82). The frozen candidate (seeds 403-407) is 0.814-0.885, mean 0.860 (PN1/result.md:294);
frozen S4 vs S3 on test hosts 0.716-0.744 (PR1/result.md:21) and R4 vs R3 0.80-0.85 (PR1/result.md:117). Seed table:
RECORDS ledger entry 6 (ca47f00). No rule or floor changes.

## Amendment 6 (13 Nov, from 21:29 by the machine clock; registered before computing; lead's request for AB1 amendment 7, batch C, 06a2351)

- The same-data shortcut learner (section 5.3, unchanged models) is fitted on `train_SpV.csv` (sha256 f6521d96…) and
  `train_BN.csv` (c1b4497b…) of `/mnt/t7/smad_next/AB1/c/manifests/`. Before fitting, `src/adversary/amend6.py`
  asserts that both files hash to these values and to the lines in AB1's `pins.sha256`; if the AB1 owner re-pins after
  the pre-run check, the learner is recomputed on the new lists and the old files are kept and labelled superseded.
- Outputs: `floors/transfer_SpV.json`, `floors/transfer_BN.json` (every development contrast and pool, as for the
  other arms) and per-row scores `floors/transfer_<arm>_rows.csv` (set, id, rung, label, component, logreg, gbt) on
  `sel360` (components of `ri_R4_vs_R3_heldout.csv`) and `splice80`: the native S4, S3 and S0 rows of the 80 test hosts
  in `/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv` (components from their person keys); summary in
  `floors/transfer_<arm>_rows_summary.json`. Pinned as stage 11. No network score is read.

### Amendment 6, addendum (13 Nov, 21:39 by the machine clock; registered before computing; AB1 amendment 7b, 35c8a9f)

- The same learner and outputs are added for the control list `train_BV.csv` (B plus 312 database-matched repeated
  native negatives; sha256 ee4e227b2cd6648d…, full hash checked against AB1's `pins.sha256` by `amend6.py BV` before
  fitting). Outputs `floors/transfer_BV.json`, `floors/transfer_BV_rows.csv`, `floors/transfer_BV_rows_summary.json`,
  pinned as stage 12. The stage-11 files of SpV and BN are unchanged (their lists did not change).
