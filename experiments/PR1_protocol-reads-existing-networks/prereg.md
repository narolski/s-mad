# Registered reads of the existing fresh-seed protocol networks (PR1)

Owner: PR1 owner agent (Opus), 13 Nov 2026. Task source: `experiments/reviews/STRATEGIST_IDLE_GPUS_20261113.md`
sections 0, 1 and item #1 of section 2. Development data only. No training.

Registered at the git commit that adds this file (`date` at writing: Fri Nov 13 2026, about 09:00 CET). At that commit
no number of this file's reads Z0, Z1, Z2, Z3 or GD0 has been computed by this owner. Values that others already
computed and that this owner has seen are listed in section 1 ("known before registration").

## 0. Networks, data, exclusions

- **Networks (15):** the fresh-seed checkpoints of the protocol network (FS1), arms A (plain recipe), B (protocol
  negatives), Sb (protocol negatives plus face-spliced morphs), seeds 403-407, last checkpoint. Result tars
  `/mnt/t7/smad_next/PN1/results_fs/PN1_<arm>_s<seed>.tar`, pinned by the full sha256 values in the `.tar.sha256`
  files next to them, which are the values listed in the C2P registration (`PN1 prereg.md`, C2P.2, commit 2715e48).
  The reader checks every tar against its sha256 and reads the score files **from the tar members** (never from an
  unpacked folder). Seeds 401/402, the replicate A seed 401 and the three Sp fits are not read.
- **Stored scores used (Z0-Z3, zero GPU):** each tar's `scores_eval.npz` (19,797 FS1 development evaluation rows,
  manifest `fs_tree/pn1/data/manifests/pn1_eval.csv` sha256 `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045`)
  and `scores_train.npz` (5,535 unique training rows of the network's own training list; logit of the last
  checkpoint in eval mode, TF32 on, scored by `pn1_score.py` on the A100 right after training).
- **Families read:** `af0`, `ladder`, `splice` (our builds from FRGC / colorFERET hosts), `ffhq` (HN2 list),
  `ffhq_lcomb` (landmark_combined); GD0 adds FFHQ-Morphs `stylegan_wplus`, `stylegan_w`, `diffae` and their
  history-matched genuine pools. FFHQ under `/mnt/t7/smad_heldout/ffhq_morphs` is the sprint's development set and is
  never reported as a benchmark.
- **Closed (no row read, no list opened):** FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace and every sealed set;
  `manifests/valx.csv`, FST, A12SP. The reader asserts that every row it reads has `fam` in {af0, ladder, splice,
  ffhq, ffhq_lcomb} (GD0: {gd0}) and a path under `eval/pn1/`, `eval/hn2/`, `eval/a14/` (GD0: `eval/gd0/`), and that
  no path contains `fst`, `valx`, `a12sp`, `a12-sp`, `frll`, `mad22`, `mordiff`, `dim`, `h1`, `fei`, `casia`.
  The reader does not call `pn1lib.catalog()` (it opens benchmark lists); the engine check reads
  `/mnt/t7/smad_next/AF0/lists/ar1.csv` (ladder list, development) only.
- **Own rule:** logit > 0 is "flagged" (the networks' decision rule, as in FS1).
- **AUC:** rank form, ties counted half, direction fixed (attack/positive class higher), never flipped.
- **Intervals (printed only, never part of a rule unless stated):** 2,000 bootstrap draws, images within class,
  `numpy.random.default_rng(20261141)`; Z3 paired by host.
- **Seed counts:** a rule "on ≥ k of 5 seeds" keeps the denominator 5; a missing or unreadable network counts as not
  meeting the rule's condition on that seed. Margins inclusive at full float precision.

## 1. Known before registration (seen by this owner or in reviewed files)

- From `REVIEW_PN1_FS1_20261113.md` F6 (fresh seeds): Sb flags 31-41% of development S3 (A and B 2-7%); Sb separates
  S3 from S0 at 0.86-0.93 and S4 from S3 at 0.78-0.82; own-rule misses development S4 15-29%, landmark_combined
  26-47%. Training accuracy (all unique training rows, own rule): A and B 1.000, Sb 0.989-0.991 (`info.json`
  `train_acc_rule0`; Sb s403 0.99133). Which kinds of training rows Sb gets wrong has not been looked at.
- From `PN1 prereg.md:778` (Sp reader test): Sb seeds 401/402 flag 0 of 100 development S0 images; S0-vs-S4 AUC
  0.9875 / 0.9927. The strategist cites this as "Sb flags 0 of 100 seam-only images"; it is a 401/402 figure, not
  a fresh-seed figure. Fresh-seed S0 flags have not been computed by this owner.
- F10: at 5% flags on R0 + AF0 (τ_dev(i)) every FS1 arm flags 96-98% of FFHQ genuine photos.
- Contrast-1 AUCs on landmark_combined (A 0.736, B 0.674, Sb 0.860 means), the 27-statistic ladder baseline 0.814
  (s-lad) and the best single statistic 0.886 on landmark_combined.
- Training list facts (counted before registration, no score involved): `train_Sb.csv` has 156 S3, 156 S0, 430 S4
  (124 unique), 435 R4 rows (124 unique); every S0/S3/S4 path is an OpenCV-style splice (`sp2_*_opencv_*`). The
  `tool` column is `smdd` on every row, so it does not record the engine; Z3 checks the ladder R4 engine from the
  AR1 list.
- Not seen: any GD0 score (no PN1 network has scored stylegan_wplus, stylegan_w or diffae), any TT1 score of the
  fresh-seed networks, any C2P hold-out score.

## 2. Z0: check of the strategist's three cited facts (printed, no verdict)

Per arm and seed, own rule: flag share of splice S0, S3 (development 100 each; test 191 each), miss share of S4
(development 100, test 191); AUC S3 vs S0 and S4 vs S3 (development and test); landmark_combined orig morph miss
(1,000). Printed beside the cited ranges; a cited range "holds" if the recomputed fresh-seed range over seeds 403-407
agrees to within 0.01 AUC and 1 percentage point at both ends; otherwise "differs" with both values. Specifically
printed: Sb's development S0 flags per fresh seed (the strategist's "0 of 100", cited from seeds 401/402).

## 3. Z1: are Sb's own training splice rows fit? (zero GPU)

- **Hypothesis H-Z1 (underfit):** Sb does not fit its own training same-person splices (S3) or two-person splices
  (S4); its development S3 flags (31-41%) and S4 misses (15-29%) are then partly a training-fit problem.
- **Alternative (does not generalise):** Sb fits its training S3 and S4 rows, and the development errors arise on
  new hosts.
- **Read (per Sb seed, from `scores_train.npz`, unique training rows):** f_tr(S3) = share of the 156 training S3
  rows with logit > 0; m_tr(S4) = share of the 124 unique training S4 rows with logit ≤ 0. Printed beside: the same
  for every training kind (S0, R0, R2w, R4, halves, af0 kinds) and for A and B on their own training kinds; training
  AUC S3 vs S0 and S4 vs S3; the development values of Z0 next to the training values.
- **Rule (Sb):**
  - "underfit" if f_tr(S3) ≥ 0.20 OR m_tr(S4) ≥ 0.15, on ≥ 4 of 5 seeds;
  - "fit, does not generalise" if f_tr(S3) ≤ 0.05 AND m_tr(S4) ≤ 0.05, on ≥ 4 of 5 seeds;
  - otherwise "mixed, no claim".
- **Caveats stated now:** training rows are scored without the flip augmentation used in training, in eval mode;
  S4 rows are repeated in training (430 rows, 124 unique), S3 rows are not (156 unique) — the class balance of the
  list, not a choice of this read. Training accuracy is over 5,535 unique rows, so ≈ 48-61 wrong rows per Sb seed
  bound what Z1 can find.
- **Decides:** the strategist's choice between "Sb trained twice as long" (SL1, if underfit) and a data change
  (SE1, if fit, does not generalise). PR1 only prints the verdict.

## 4. Z2: calibration of a multi-source development threshold (zero GPU now; Z2b when TT1-FS is read)

- **Calibration pools (native genuine photos, development, never in any training list):**
  (c1) FRGC / colorFERET: AF0 development photos, native (126) + development ladder R0 native (100);
  (c2) FFHQ: `ffhq_bona_orig` rows of the HN2 list whose person key k has `sha256(k)[0] % 2 == 0` (calibration
  half, about 1,000).
  The TT1 pools and the MS1 CFD photos have not been scored by these networks and are not used (see Z2b).
- **Threshold τ5(n):** per network, the smallest logit cut-off t (over the pooled calibration logits) such that the
  flag share (logit > t) is ≤ 0.05 in **each** of c1 and c2 ("every calibration source protected").
- **Printed per network, at τ5 and at the own rule (0):**
  - flags on held-out genuine pools: FFHQ `ffhq_bona_orig` evaluation half (the other ≈ 1,000 persons); FFHQ
    `landmark_complete_resmatch` and `landmark_combined_resmatch`, evaluation-half persons (history-matched copies);
    test ladder R0 native (191) and its 61 px / 112 px stored copies (191 each); development ladder R0 61 / 112
    (100 each); AF0 development photo 61 / 112 (126 each);
  - flags on protocol-genuine pools (one-person images that the protocol labels genuine): splice S0, S3
    (development, test); ladder R2w native per engine (development, test); AF0 halfA, halfB, zero;
  - misses on attack pools: landmark_combined orig (1,000), landmark_complete orig (1,000), ladder R4 native per
    engine (development 100 each, test 191 each), ladder R4 opencv 61 / 112 (development, test), splice S4
    (development, test), AF0 u50 (180).
- **H-Z2a (a usable operating point exists):** seed s of arm X is "usable" if at τ5 both
  G_max ≤ 0.10, with G_max the largest flag share over {FFHQ bona evaluation half, FFHQ landmark_complete_resmatch
  evaluation half, FFHQ landmark_combined_resmatch evaluation half, test ladder R0 native, test R0 61, test R0 112},
  AND the landmark_combined miss ≤ 0.30.
  Arm verdict: "usable operating point" if ≥ 4 of 5 seeds are usable; "no usable operating point" if ≤ 1 of 5;
  otherwise "inconclusive, no claim". Read for A, B and Sb.
- **H-Z2c (the strategist's "same score band"):** for Sb, AUC of landmark_combined orig morphs against development
  S3. "Same band" (supported) if ≤ 0.65 on ≥ 4 of 5 seeds; "separate bands" (falsified) if ≥ 0.80 on ≥ 4 of 5;
  otherwise "inconclusive". Printed beside: Sb's landmark_combined miss at the cut-offs that flag 10% and 20% of
  development S3.
- **Z2-ρ (TT1 H-new-4 trade-off, extended to the 15 fresh-seed networks):**
  x = own-rule flag share on FFHQ `ffhq_bona_orig` (all 2,000; unseen-source native genuine photos);
  y = mean of the own-rule miss shares on three development attack pools, equal weights, exactly as TT1 H-new-4:
  ladder R4 native (strength empty), development and test hosts, both engines (582 rows); AF0 u50 (180); splice S4
  development and test (291). Spearman ρ(x, y) over the 15 networks; p from 200,000 random permutations
  (`default_rng(20261142)`), two-sided. **Rule (as H-new-4):** falsified if ρ ≥ 0; "supported" if ρ ≤ −0.6;
  otherwise "weak (not decided)". Printed: the same ρ within each arm (5 points; no rule) and with x, y at τ5
  (x = G_max, y = the same three-pool mean miss at τ5).
- **Z2b (registered now, read later):** the same ρ and rule with x = TT1-FS F̄ (registered R5 of
  `TT1 prereg_fs1_block.md`), taken from the TT1 owner's committed `tt1_read_fs.json`, read only after the TT1 owner
  has read and committed it. Networks that failed TT1's gate are missing (denominator printed). If TT1-FS is not read
  by 14 Nov 12:00, Z2b is "not read".
- **Feeds:** the author's pending F10 ruling. PR1 states the verdicts only.

## 5. Z3: tool transfer (zero GPU)

- **Fact check first (printed):** the engine of every training ladder R4 row of A, B, Sb (looked up by id in
  `AF0/lists/ar1.csv`), and of the S0/S3/S4 splice rows (path).
- **Hypothesis H-Z3 (engine gap):** a network trained on OpenCV-style morphs only detects FaceMorpher morphs worse.
- **Read (test ladder, 191 hosts, native rows only):** AUC_cv = AUC(R4 opencv vs R2w opencv);
  AUC_fm = AUC(R4 facemorpher vs R2w facemorpher); Δ = AUC_cv − AUC_fm. Interval: 2,000 paired host draws.
  Printed beside: AUC of each engine's R4 against R0 native (engine-free negative); own-rule and τ5 misses per
  engine; the development-ladder versions (100 hosts); FFHQ landmark_complete vs landmark_combined AUC (each against
  its resmatch pool).
- **Rule (Sb decides; A and B read by the same rule and printed):** "engine gap" if Δ ≥ +0.03 on ≥ 4 of 5 seeds
  (the strategist's condition for the second-engine arm #6); "no engine gap" if Δ ≤ +0.01 on ≥ 4 of 5 seeds;
  otherwise "inconclusive, no claim".
- **Stated limit:** the FaceMorpher R2w negative differs from the OpenCV one (its seam is weaker, `REVIEW_SPLICE`),
  so Δ mixes "harder positive" with "different negative"; the R0 column separates them descriptively only.

## 6. GD0: GAN and diffusion families of the development set (about 0.5 GPU-hour; new scoring)

- **Hypothesis H-GD0:** Sb's ranking, trained on landmark morphs only, transfers to StyleGAN morphs.
- **Rows (`/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv`, sha256 `732b53c8…`):** for each family f in
  {stylegan_wplus, stylegan_w, diffae}: 1,000 `orig` morphs (label 1) and the 2,000 `resmatch` genuine copies of
  family f (label 0; the 2,000 FFHQ bona fide persons, shrunk to the family's native eye distance by the unchanged
  E7 function at build time). 9,000 rows, each file checked against the set's `SHA256SUMS`. Bona fide persons are
  disjoint from morph contributors (checked by the pack builder, as in HN2). The native `ffhq_bona_orig` scores of the
  same persons exist (FS1) and are printed beside.
- **Read per network and family:** AUC(orig morphs vs that family's resmatch genuine), bootstrap interval; own-rule
  miss and genuine flag share; AUC against `ffhq_bona_orig` (stored scores, printed).
- **Baselines printed beside (zero GPU, DGX CPU):** (i) the 27-statistic ladder baseline of PN1 amendment 15 (s-lad
  and b-lad; same training rows, model and code path as `baseline27.py`), scored on the GD0 rows; (ii) the best single
  statistic of the 27 by direction-free AUC on the same images (an upper-biased floor). Cues from `cues27.py`
  unchanged.
- **Rule (Sb; the strategist's bars):** per StyleGAN family, "transfers" if AUC ≥ 0.80 on ≥ 4 of 5 seeds; "does not
  transfer" if AUC ≤ 0.65 on ≥ 4 of 5 seeds; otherwise "inconclusive, no claim". H-GD0 is supported if both StyleGAN
  families "transfer", falsified if both "do not transfer"; otherwise mixed. **Added qualifier:** a "transfers"
  verdict may be written "beyond the 27-statistic baseline" only if Sb − s-lad ≥ +0.05 on ≥ 4 of 5 seeds for that
  family; otherwise it carries "not shown beyond simple statistics". DiffAE: printed only (no rule; the render-path
  confound of the diffusion family is known). A and B are printed with the same bars, no claim.
- **Platform (decided now):** the rented A100 "pn1fs" (NVIDIA A100-PCIE-40GB, GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad,
  the GPU that trained these networks and stored their scores), image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`
  with the FS1 pip pins, after the TT1-FS block has finished (`/workspace/tt1/DONE_FS`) and under the host's FS1
  queue lock, before any RELEASE (the lead keeps the lease). Fallback, only if pn1fs is gone: Athena A100 through the
  dispatcher's queue (`plgrid-now`, pieces ≤ 1 h), with the same gate. Never two platforms for one read: if any GD0
  score is made on a platform, all 15 networks are read from that platform.
- **Scoring:** `src/PN1/rescore.py` unchanged (sha256 `6f6eede7…`) run through TT1's `rescore_tf32.py` (TF32 on, as
  `pn1_score.py` stored the FS1 scores; sha256 pinned in `src/PR1/SHA256SUMS`), batch 64, list order fixed by the
  GD0 manifest (sorted by id).
- **Reproduction gate (per network, fixed now):** in the same job, before its GD0 rows, every network re-scores all
  19,797 FS1 development evaluation rows in manifest order with TF32 on. Pass: 99th percentile |Δlogit| ≤ 0.05 AND
  maximum |Δlogit| ≤ 0.10 AND own-rule decisions agree on ≥ 99.5% of rows, against the network's stored
  `scores_eval.npz` (the C2P gate criterion). Byte identity is printed. A network that fails is not read on GD0: its
  seed counts as not meeting any condition (denominator 5). No tolerance changes after a gate is seen.
- **Outputs:** one result tar `PR1_GD0_<lease>.tar` + sha256, copied to `/mnt/t7/smad_next/PR1/` and verified before
  the lead releases the machine.

## 6a. Parts added at the lead's request (13 Nov, from the shortcut audit table SA1, ranked gap list items 2, 5, 6, 7, 8)

All before any of them is computed. Rows already printed elsewhere for seeds 401/402 are known (SA1 rows 6-9, 17);
none of the fresh-seed values below has been computed by this owner.

### Z4: warp-only, same-person morph, mirror, seam-only and splice rows (zero GPU; SA1 rows 6, 7, 8, 9)

Per arm and seed, stored `scores_eval.npz`, native rows (strength empty), test ladder (191 hosts) as the deciding
rows and development ladder (100 hosts) printed beside; both engines printed, OpenCV-style decides (the training
engine).
- **Row 6, warp only (R2w):** f(R2w) = own-rule flag share of R2w opencv; AUC(R4 vs R2w) opencv. "Warp-only not
  flagged" if f(R2w) ≤ 0.05 AND AUC(R4 vs R2w) ≥ 0.90 on ≥ 4 of 5 seeds; "warp-only flagged" if f(R2w) ≥ 0.20 on
  ≥ 4 of 5 seeds; otherwise "inconclusive, no claim". Printed: AUC(R2w vs R0), the 61 / 112 px R2w copies.
- **Row 7, same-person morph (R3) and mirror self-morph (R3m):** f(R3), f(R3m) own-rule flag shares (opencv);
  "flagged like a morph" if f ≥ 0.50 on ≥ 4 of 5 seeds; "not flagged" if f ≤ 0.10 on ≥ 4 of 5; otherwise
  "inconclusive". Printed: AUC(R4 vs R3), AUC(R4 vs R3m), AUC(R3 vs R0), the 61 / 112 px R3 and R3m copies.
- **Row 8, same-person face splice (S3), and row 9, seam-only (S0):** splice rows (OpenCV only), test (191) decides,
  development (100) printed. f(S3), f(S0) and m(S4) (own-rule miss); AUC(S4 vs S0), AUC(S4 vs S3), AUC(S3 vs S0).
  S3: same rule as row 7. S0: "seam-only not flagged" if f(S0) ≤ 0.05 AND AUC(S4 vs S0) ≥ 0.90 on ≥ 4 of 5 seeds;
  "seam-only flagged" if f(S0) ≥ 0.20 on ≥ 4 of 5; otherwise "inconclusive". S0 and S3 are trained negative types
  of Sb (not of A, B); stated beside every Sb row.
- Z0 (section 2) prints the strategist's cited figures from the same numbers.

### Z5: storage evasion of morphs for A, B and the three-source arm (zero GPU; SA1 row 2)

- Formula and rule exactly as C2P.4 (H-new-1): Δm_att(n, z) = mean over the hold-out u50 morph pairs of (stored −
  native logit) / SD(native genuine logits of n over the 300 native photos), z ∈ {fm61, amsl112}. Per arm:
  "supported" (evasion) if Δm_att ≤ −0.20 on ≥ 4 of 5 seeds at either size; "falsified" if Δm_att ≥ −0.10 on
  ≥ 4 of 5 seeds at both sizes; otherwise "inconclusive". Printed: native and stored morph misses (logit ≤ 0).
- **A and B (FS1 networks):** from the C2P result tar `/mnt/t7/smad_next/MS1/c2p/C2P_m1.tar` and the C2P owner's
  committed `c2p_read.json`; read **only after** that file is committed by the C2P owner. Where `c2p_read.json`
  already holds a value, it is copied, not recomputed; values it lacks (A's Δm_att if absent) are computed from the
  tar with the C2P.4 formula and only from rows that passed the C2P gate.
- **Three-source arm (SbM3):** from the MS1 score files, only after the MS1 owner has done and committed its
  registered read, and only if those files hold the hold-out rows (`fam = ms1ffhq`) for SbM3; otherwise "not
  available". Same formula and rule. If neither owner's read exists by 14 Nov 12:00, Z5 is "not read".

### Z6: softness (Laplacian variance) for the fresh seeds (zero GPU; SA1 row 17)

- Measure: `lapvar_face` of the 27-statistic files already computed (`/mnt/t7/smad_next/AF0/cues/ar1.npz` for ladder
  native rows, `/mnt/t7/smad_next/PN1/cues/splice_nat.npz` for splice natives; `cues27.py` / AF0 `cues_all.one`
  unchanged). Deviation from TT1 H-new-1, stated: that read used its own face-box Laplacian on TT1 frames; here the
  cue-file statistic on the ladder frames is used, so that no image is read again. If an id has no cue, it is left
  out and the count is printed.
- **Hypothesis H-Z6 (softness explains the warp-only contrast):** within narrow sharpness strata, an arm no longer
  separates the two-person morph R4 from its warp-only image R2w.
- **Read (test ladder, opencv, native):** stratified AUC(R4 vs R2w): quintile edges of log lapvar_face over the
  pooled 382 R4 + R2w rows; AUC within each stratum; mean weighted by n_pos × n_neg (strata with no pair left out).
  Printed: unstratified AUC; lapvar_face alone (direction-free AUC); within-class Spearman ρ(logit, log lapvar_face)
  on R0, R2w, R3, R4 (ladder) and S0, S3, S4 (splice, test); the same stratified AUC for S4 vs S3.
- **Rule (per arm):** "softness explains" if the stratified AUC ≤ 0.70 on ≥ 4 of 5 seeds; "not softness alone" if
  ≥ 0.85 on ≥ 4 of 5 seeds; otherwise "inconclusive, no claim".

### GD1 and GD2: diffusion and GAN one-person controls in the GD0 job (new scoring; SA1 rows 13, 14)

Added to the GD0 pack only if the frames exist on the DGX in the networks' input format (E7-aligned 512 px frames
of the FS1 evaluation pack) and their hosts can be checked through the PN1 split files
(`experiments/PN1_protocol-network-first-tests/split/ladder_split.csv`, `af0_split.csv`; never valx.csv). The exact
rows, counts and paths are fixed in a GD operations note before the pack is built; the hypotheses and rules are
fixed here.
- **GD1 (DG1 diffusion ladder, test hosts only):** rows: two-person DiffAE morph X, same-person mix SAME and
  one-photo reconstruction REC of the same host, restricted to hosts with ladder role "test" (test_read 1) and with
  every contributing person outside the PN1 training and validation hosts. Hypothesis H-GD1 (render-path use): the
  network ranks the two-person morph above the reconstruction no better than chance-plus. Read per network:
  AUC(X vs REC), AUC(SAME vs REC), AUC(X vs SAME), own-rule flag share of REC. **Rule (per arm):** "render path
  not used" if AUC(X vs REC) ≥ 0.75 AND f(REC) ≤ 0.20 on ≥ 4 of 5 seeds; "render path used" if f(REC) ≥ 0.50 on
  ≥ 4 of 5 seeds, or AUC(X vs REC) ≤ 0.60 on ≥ 4 of 5 seeds; otherwise "inconclusive, no claim".
- **GD2 (AG1 MIPGAN one-person controls):** rows: camera photo R0, MIPGAN render of one photo (one-person render),
  same-person MIPGAN morph, two-person MIPGAN morph, on hosts outside every PN1 training and validation host
  (persons checked through the split files). Hypothesis H-GD2 (GAN one-person render use): the network flags a
  one-person GAN render like a two-person GAN morph. Read: AUC(two-person vs one-person render), AUC(two-person vs
  same-person), AUC(one-person render vs R0), own-rule flags of each rung. **Rule (per arm):** "one-person render
  flagged like a morph" if f(one-person render) ≥ 0.50 on ≥ 4 of 5 seeds; "not flagged" if ≤ 0.10 on ≥ 4 of 5
  seeds; otherwise "inconclusive". Printed: AUC values with host-bootstrap intervals.
- Same platform, gate and scorer as GD0 (section 6). If GD1 or GD2 frames do not exist in the input format, the part
  is "not read (no frames in the networks' format)" and no new image operation is made.

## 7. What may not be claimed

No benchmark claim; no "removes", "shortcut-free", "reads identity" or "reads the seam". Z verdicts are on our own
development data, read once each by this owner. The test ladder (191 hosts) has been read many times before; its rows
here are descriptive development reads. FFHQ is the development comparison set.

## 8. Code and commands

- Z0-Z3 reader: `src/PR1/pr1_read.py` (sha256 in `src/PR1/SHA256SUMS`, committed with this file), tested before this
  commit on mock scores only (`--mock`, random logits over the true row ids; output
  `experiments/PR1_protocol-reads-existing-networks/pr1_read_mock.json`). Run once:
  `OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PR1/pr1_read.py --out experiments/PR1_protocol-reads-existing-networks/z_read.json`
- GD0 code (pack builder, remote script, reader) is committed and pinned in a GD0 operations note added to this file
  before the job starts; that note may change operations only, never the rows, rules, gate or bars above.

## 9. Pre-run review

To be run by the experiment-reviewer agent (Opus) on this registration as a whole; fixes of blockers and majors are
added below as a dated amendment before any read.
