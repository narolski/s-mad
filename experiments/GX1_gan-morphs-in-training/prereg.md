# GAN morphs in training with one-person renders as genuine (GX1): registration

Written 13 Nov 2026 before any GX1 image is generated and before any GX1 network exists. Owner: AG1 owner (Opus agent).
Author's go (verbatim): "Ok, go ahead" to "GAN morphs in training with one-person renders as genuine"; lead's scope
decision after it. Time note (13 Nov, added in amendment 1, 18:48 by git): the lead's messages gave these as 18:50 and
19:35; the machine clock and git are the record: both fall between about 18:32 and 18:46 machine clock (NOTEBOOK
"CORRECTION OF TIMES"); the freeze ruling was at about 18:27. This registration was committed at 18:40:15 (git). Code `src/GX1/` (plus the unchanged `src/AG1/` generator wrapper and vendored code);
large outputs `/mnt/t7/smad_next/GX1/`; WCSS results `$L/smad-next/results/GX1/`.

**Status of this arm.** Development of the next method version. The author froze the current candidate (arm Sb, seeds
403-407) at 18:28 and ruled tonight to read MAD22 now ("READ NOW, improve later"). GX1 cannot replace the frozen
method. For any later version built on GX1, MAD22 and its MIPGAN cells are a seen benchmark.

## 1. Question

Can the protocol network learn something morph-specific about MIPGAN-style two-person morphs when rendering alone
carries no class information? Earlier reads (PR1 part 2, GD2): Sb flags 78-90% of one-photo MIPGAN renders and shows
no identity step beyond simple statistics. If GX does not separate held-out two-person morphs from their hosts'
one-photo renders, the paper's GAN sentence reads "nothing morph-specific was learnable at this resolution and dose"
(see section 7).

## 2. Generation (first; image-level checks and hashes fixed before any network sees an image)

- **Persons** (PN1 split files only, `experiments/PN1_protocol-network-first-tests/split/{ladder_split,af0_split}.csv`;
  `valx.csv` never opened): protocol-network training persons = ladder hosts with `train_genuine = 1` plus AF0 persons
  with `pn1_use = train` (637); development persons = ladder role `dev` plus AF0 `pn1_use = dev` (215). Of these, the
  persons with two neutral photos of two capture dates under the AG1 rule (FERET `fa*` frontals; FRGC controlled stills
  env nd1E00004/5, emotion BlankStare; val10 excluded): **202 training persons** (FRGC 134, FERET 68; 124 M, 78 F)
  and **109 development persons** (FRGC 84, FERET 25; 65 M, 44 F). Seeded choice of the two dates and photos
  (`src/GX1/build_gx1.py select`, seed 20261113; `select.json`).
- **Inputs:** the AG1 input path unchanged (`src/AG1/build_inputs.py stage_prep`, called with the GX1 folder):
  `prep_eval.kps` -> `gancommon.ffhq_align` 1024 -> `cv2.resize` INTER_AREA 512 -> `prep_eval.kps` on the crop. Same
  steps as the approved A33 / AG1 set; no new image operation. Photos with no face are dropped and listed.
- **Pairs** (`build_gx1.py pair`): within (group, database, gender), the AG1 look-alike cycle cover (max total w600k
  cosine of s1(p) vs s2(q), diagonal forbidden). Training persons: two disjoint covers (second cover forbids the first
  cover's pairs in both orders): 2 two-person morphs per host, target 404. Development persons: one cover, target 109.
  The composition rule holds (same host photo s1(p), B from the other session, every B hosts its own twin).
- **Rungs per host** (MIPGAN-I = mip1, our MIPGAN-I-style re-implementation): R2 = MIPGAN with A = B on s1 and on s2;
  R3 = MIPGAN on s1(p), s2(p); R4 = MIPGAN on s1(p), s2(q) for each cover. MIPGAN-II-style (mip2, e4e + StyleGAN2) on
  the same jobs as separate shards that may be dropped if the queue is slow (dropping them changes no rule; reads on
  mip2 are descriptive).
- **Generator:** `src/AG1/ag1_gen.py` (sha256 b2dc54eb...) with the vendored gan1 code (A33 hashes, checked at start),
  weights `gan_weights.tar` e06f19af... and `gan_sg1.tar` 1571c1a3... (verified on WCSS Lustre 13 Nov 19:50),
  inversion 500 Adam steps lr 0.02, MIPGAN 150 steps; TF32 off, cuDNN deterministic. Platform: WCSS H100 only,
  `~/dmenv/bin/python -I` used read-only (nothing installed; pytorch_msssim 1.0.0 from the weights pack). Every GX1
  image comes from this one platform; nothing from Athena, the rented machine or AG1 is reused.
- **Image-level checks (binding before any training):** every job's PNG present and its sha256 equal to its log line;
  1024 x 1024 RGB PNG with only IHDR / IDAT / IEND; finite latent and loss; frame alignment `prep_eval.align` aligned
  flag >= 0.95 per rung (rows with the flag 0 are dropped and listed); identity gate (glintr100, as AG1 G-b): R4
  verifies both contributors at FMR 1e-3 in >= 70% and R3 verifies its person in >= 90%, per group; otherwise the
  group's R4 (or R3) rows are not used and the shortfall is reported. The frame hashes of every admitted image are
  written to `pins_images.sha256` and committed before any fit is submitted.
- **Similarity of the pairs:** the distribution of the contributor w600k cosine (s1(p) vs s2(q)) is printed per group
  and cover (quartiles) in `pairs_summary.json`; every identity read below is printed overall and within tertiles of
  this cosine (bears on BD1's question whether a residual tracks face similarity).

## 3. Training arms (WCSS H100, AB1's proven path)

- Base: the frozen recipe Sb, `train_Sb.csv` (2cf3fda3..., 8,386 rows from 5,535 unique), unchanged; model, flags,
  6,250 steps, batch 256, last checkpoint: `src/AB1/run.sh` v2 (cfa4ed26...) copied as `src/GX1/run.sh` with only the
  arm names, the overlay and the extra scoring call changed (marked GX1).
- **GX:** Sb rows plus the admitted training R4 rows (label 1, kind `gx_R4`, target 404) plus, for every R4 row, one
  matched one-person render of the same host (label 0): the host's R2 on s1 for the cover-0 morph and its R3 for the
  cover-1 morph (kinds `gx_R2`, `gx_R3`). Within the rendered rows the classes are exactly balanced (same number of R4
  and render rows; if a host loses an image to the checks, its matched partner row is dropped too). Rows are appended
  once each (no re-balancing of the Sb rows, so the Sb part is byte-identical to AB1's).
- **GXp (control without render negatives):** Sb rows plus the same R4 rows only.
- Shares (at 404): GX 808 / 9,194 rows (8.8%; rendered rows 4.4% per class); GXp 404 / 8,790 (4.6%).
- **No volume-matched arm:** training runs a fixed number of steps, so added rows change only composition; the
  within-seed contrasts GX - Sb and GXp - Sb carry a composition change of 8.8% and 4.6% of draws; GX - GXp isolates
  the render negatives at a 4% volume difference. Stated as a limitation, not controlled.
- MIPGAN-II rows: not in training (they exist only if the mip2 shards finish; reads only).
- Seeds 408-412; compared within seed with the AB1 owner's WCSS H100 Sb fits (`AB1_Sb_s408`-`s412`, tars pinned in
  `experiments/AB1_protocol-ablation-and-replication/pins.sha256`). 10 fits.
- Excluded from every pack: FRLL, MAD22, MorDIFF, DiM, FEI, CASIA / H1 and every closed set (VAL-X, FST, A12SP).

## 4. Reads (scored inside each fit job; read once when all 10 fits have ended, latest 15 Nov 18:00)

Scoring: `pn1_score.py` unchanged on `ab1_eval.csv` (AB1's evaluation rows unchanged) and on `gx1_eval.csv` = the
GX1 held-out rows (development persons: R0 camera frames, R2 s1 / s2, R3, R4; mip1 and, if present, mip2) plus PR1's
GD rows (`pr1_gd.tar` 40aa95d2..., unchanged: GD0 FFHQ-Morphs StyleGAN / DiffAE families, GD1 diffusion ladder, GD2 AG1
controls). Logit (`logit_noTTA`); AUC with the dyadic person bootstrap (B = 10,000, `src/AG1/ag1_read.py` Draw).

- **Primary (H-GX):** on the held-out development hosts, AUC of R4 against the host's R2 (s1) for GX.
  **Supported:** AUC >= 0.70 on >= 4 of 5 seeds. **Falsified:** AUC <= 0.60 on >= 4 of 5 seeds (nothing morph-specific
  learnable at this resolution and dose with these data). Otherwise inconclusive.
- **Render flags:** flag rate of held-out R2 at the network's own rule (its training threshold rule as in AB1) for GX;
  target <= 10% on >= 4 of 5 seeds, against Sb's 78-90% (GD2); printed for GXp and Sb.
- **Identity step:** R4 against R3 (held-out) for GX, GXp, Sb; overall and within tertiles of the contributor cosine;
  descriptive with the AG1 side rule ("identity reading" AUC >= 0.75 with lower bound > 0.65).
- **Control reading:** GXp's R4 vs R2 and its R2 flag rate (expected: it learns "rendered = morph").
- **Transfer reads (descriptive):** GD0 StyleGAN wplus / w morphs against their resmatch genuine and against GD2 R2;
  GD1 diffusion ladder; mip2 held-out rows if generated.
- **Guards (each against the same seed's Sb):** landmark_combined AUC not below Sb - 0.02 on >= 4 of 5 seeds;
  storage reads (the AB1 storage-test rows, printed); camera-photo flags (FFHQ / AF0 genuine at the own rule, printed).
  A guard failure is reported beside every reading of that arm.
- Excess over the best simple statistic (AG1 baselines) printed beside the primary read, post hoc label not needed
  (registered here).

## 5. Compute and order

Generation about 6.7 H100-h (mip1) + 3.7 (mip2), in 1-1.5 h shards; a 2-person generation smoke first (submitted with
the arrays; a failed smoke means the dispatcher cancels them). Training 10 fits x about 45 min plus scoring of about
33,000 eval rows, about 9 H100-h; a training smoke (AB1-style, short steps) before the fit array because the overlay and
the second scoring call differ from AB1's path. Submission files go to the dispatcher queue, sorted behind the
second-engine arm.

## 6. What is not done

No new generation method, no new image operation, no reuse of images from other platforms, no MAD22 / FRLL contact,
no change to Sb's recipe or rows.

## 7. What each outcome means for the paper's GAN sentence

- **Supported** (GX separates held-out two-person morphs from one-person renders, >= 0.70, and keeps the guards): "with
  one-person renders as genuine examples, a protocol network learns to separate two-person MIPGAN-style morphs from
  one-person renders of the same pipeline on new persons", a development result for the next version (not the frozen
  method).
- **Falsified** (<= 0.60): "even when trained with matched one-person renders, the network finds nothing that separates
  two-person MIPGAN-style morphs from one-person renders at this resolution and dose; detection on MIPGAN cells reflects
  generator output, not morphing."
- **Inconclusive:** no sentence beyond the descriptive numbers.
- **GXp** shows what training on GAN morphs against camera photos alone does (expected: render detection).

## Amendment 1 (13 Nov, committed 18:48:45 by git (eabdcc4); after the pre-run check `PRERUN_GX1_20261113.md` (GO WITH FIXES),
## before any GX1 image is generated)

- **F1, primary read replaced (before any data).** The question of section 1 is the identity step with rendering
  matched, so the primary contrast is **R4 against R3** on the held-out development hosts, paired within seed against
  Sb scored on the same images (Sb s408-412 rescore, F2). Cue floor F = the best of the AG1 simple statistics and of a
  cross-fitted logistic on them (trained on the GX1 training R3 / R4 rows, tested on the held-out rows), computed on the
  frames before any fit and committed. **Supported:** GX - Sb >= +0.10 on >= 4 of 5 seeds and GX >= F + 0.05 (median
  over seeds). **Falsified:** GX - Sb <= +0.03 on >= 4 of 5 seeds, or GX <= 0.65 on >= 4 of 5 seeds. Otherwise
  inconclusive. R4 vs R2 (former primary) and the R2 flag rate become secondary reads (descriptive; Sb already reaches
  0.86-0.93 on R4 vs R2 on GD2). Every identity read is also printed within tertiles of the contributor cosine.
  Section 7 sentences now refer to this contrast: supported = "trained with matched one-person renders, the network
  separates two-person from same-person MIPGAN-style morphs on new persons beyond simple statistics"; falsified =
  "even with matched one-person renders in training, no second-identity signal beyond Sb's appears at this resolution
  and dose".
- **F2, Sb on the same rows.** A registered rescore job scores the AB1 owner's WCSS H100 Sb fits AB1_Sb_s408-412
  (`last_trainable.pt`, tars pinned in AB1 pins.sha256) on `gx1_eval.csv` with the unchanged `rescore.py` + TF32
  wrapper (AB1X path), about 1 H100-h. Every GX / GXp comparison uses these Sb numbers; GD2 figures are context only.
- **F3, code pins.** Generation code pinned now (GX1SUMS below). The training path (`src/GX1/run.sh`, manifest and
  overlay builder, fit sbatch) is written after generation and pinned in amendment 2, which gets its own pre-run check
  before the fit array. Known traps registered: GX rows carry `source=smdd, val=0, mixed=0` (else `train_rows` drops
  them under `--regime d0`); the training smoke asserts 9,194 / 8,790 rows and the composition cells; the second
  `pn1_score.py` call writes to its own out directory; GX frames come from `prep_eval.align` with `hist=native` like
  the Sb rows; smoke images (`gx1smoke_*`) never enter any data.
- **F4.** GXp's flag rates are printed also at a camera-photo-matched threshold (descriptive); its class prior
  (4,597 / 4,193) is stated beside every GXp flag read.
- **F5.** A missing or non-finite fit keeps the denominator at 5 and counts as not meeting a rule; infrastructure
  failures are re-run unchanged; non-finite runs are never re-run; fewer than 5 fits at the read deadline (15 Nov
  18:00) -> "partial: n of 5", no verdict.
- **F6.** The generation arrays are submitted with `--dependency=afterok:<smoke job>`; the smoke's PNGs and log.csv are
  checked against section 2 before the arrays' output is used. Shards are cut by job count, so some photos are
  inverted in two shards; one shard boundary is checked for identical inversion latents (same stack, deterministic
  cuDNN) and the result printed.
- **F7.** Training contributor cosine quartiles per cover (cover 0 = R2-matched, cover 1 = R3-matched) are printed.
- **F8.** The landmark_combined guard (-0.02 on >= 4 of 5 seeds) can fail through composition noise (AB1 SbZ - Sb ran
  -0.001 to -0.025); it is reported, not a veto.
- **Generation counts (built 18:37-18:47 machine clock):** 311 persons prepared, 0 photos dropped (training 202,
  development 109). Pairs: training cover 0 = 202, cover 1 = 202, development 109. Contributor cosine quartiles
  (min / 25% / median / 75% / max): training 0.023 / 0.135 / 0.170 / 0.211 / 0.705; development 0.005 / 0.106 / 0.145 /
  0.186 / 0.339. Four training pairs exceed 0.4: frgc_04637 / frgc_04638 (0.705 and 0.611; consecutive subject ids,
  possibly the same or twin persons) and frgc_04217 / frgc_04557 (0.460, 0.429); kept, flagged, visible in the
  cosine-stratified reads.
- **Generation pins (GX1SUMS, packs/GX1 on WCSS):** gx1_inputs.tar c56aa151..., gx1_code.tar 8504079b... (=
  the AG1 Athena code tar: ag1_gen.py b2dc54eb... + vendored gan1 files), gx1_gen_task.sh eaf99f3b..., gx1_gen.sbatch
  1e560f63..., gx1_gen_smoke.sbatch ae4ed31b..., gen_mip1.txt c671280d... (12 shards), gen_mip2.txt 19fd50d4... (8
  shards); smoke shards GX1_smoke_mip1 / _mip2 (3 images each).
