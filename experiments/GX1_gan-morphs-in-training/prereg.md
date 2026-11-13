# GAN morphs in training with one-person renders as genuine (GX1): registration

Written 13 Nov 2026 before any GX1 image is generated and before any GX1 network exists. Owner: AG1 owner (Opus agent).
Author's go (13 Nov 18:50, verbatim): "Ok, go ahead" to "GAN morphs in training with one-person renders as genuine";
lead's scope decision 19:35. Code `src/GX1/` (plus the unchanged `src/AG1/` generator wrapper and vendored code);
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
