# AG1 / AG2 / AG3 GAN causal test (MIPGAN ladder)

Written 11 Nov 2026 before any image of this experiment exists and before any score is read; amendment 1 (pre-run
review, same afternoon, still before any data image) is folded in and listed at the end. Owner: AG1 owner (Opus).
Code: `src/AG1/`. Large outputs: `/mnt/t7/smad_next/AG1/`. Rules: `11_AUDIT_PLAN.md` (ladder, gates, verdicts), (b).

- **Hypothesis (plain words):** on the MIPGAN cells, released detectors react to "this image came out of the
  generator" rather than to a morph made from two photographs. R2 vs R4 tests "two photographs"; only R3 vs R4 tests
  "a second identity". A detector "reads identity blending" only with an identity reading on R3 vs R4 as well.

- **Data.**
  - *Benchmark-linked pool (secondary, descriptive):* the 102 FRLL persons of the corrected MAD22 bona fide
    (`.../marco_owncloud_20261109T103840Z/author_files/original_sorted/BonaFide`, NNN_03 neutral = s1, NNN_08
    smiling = s2). R4 partner sigma(p) = a cycle cover restricted to pairs published in MAD22 MIPGAN-I in both the
    03-03 and the 08-08 list, maximising w600k cosine of s1(p) vs s1(q) (same expression, as the bridge pair). 48 of
    50 cycles are 2-cycles: R4 holds about 50 dyads.
  - *Primary pool:* 100 colorFERET + 100 FRGC 2.0 persons (seeded draw), two neutral photos of two capture dates
    each: FERET `fa*` frontals; FRGC controlled stills (env nd1E00004/5, emotion `BlankStare`). val10 persons
    (`prep_train.is_val`) excluded. R4 partner = cycle cover within (database, gender) maximising w600k cosine of
    s1(p) vs s2(q). Primary cells pool FERET and FRGC (200 persons, one bootstrap draw); each database alone is
    descriptive.
  - *Composition:* R3 = twin(s1(p), s2(p)); R4 = morph(s1(p), s2(sigma p)): same host photo, A' and B from the other
    session (FRLL: the other expression), every B hosts its own twin. MIPGAN's objective and initialisation are
    symmetric in (A, B). Known residual: the session gap is larger for morphs than for twins (median 306 vs 121 days
    FERET, 160 vs 64 FRGC); a sensitivity analysis is registered below. Contributor w600k cosine: twins 0.84 to 0.91,
    morphs 0.14 to 0.17 (pool means, `pairs.csv`).
  - Rungs per person: R0 camera photo (FRLL: admitted canonical512 native frame; FERET / FRGC decoded once to
    lossless PNG, then `prep_eval.align`); R1 = existing E7 frame (FRLL only); R2 = MIPGAN with A = B on s1 and on
    s2; R3; R4; RT = order-reversed twin (every FRLL person + 25 FERET + 25 FRGC; run-to-run noise floor).
    FRLL also: BR = our morph of the published pair at the same expression (03-03, 08-08; unordered pairs
    deduplicated, 108); PUB = the published MAD22 MIPGAN-I / -II files. R2i = G(w_inv) render (descriptive only).
  - AG2: published MIPGAN morphs vs the R2 images of the same 204 FRLL photos, morphs unchanged.
  - AG3: 40 FERET + 40 FRGC hosts (seeded): two-person mixing alpha in {0, 0.1, 0.2, 0.3, 0.4} through
    `mipgan_alpha` (alpha 0.5 = their R4); AG3T: the same hosts' twin pairs at alpha 0.1 ... 0.4 (alpha 0.5 = their
    R3), separating "second photo" from "second identity". Both use the core shards' inversion latents.
  - Files: `pairs.csv` (sha256 19145659...), `shards.csv` (978c3ea0...), inputs pack `ag1_inputs.tar` (7771484e...,
    holds `photos.json`, the 604 crops and the 13 shard plans); `/mnt/t7/smad_next/AG1/inputs/`.

- **Model and recipe (generation).** mip1 = our MIPGAN-I-style re-implementation (A33): StyleGAN v1 FFHQ-1024
  (official karras2019 weights, PyTorch port in `gan_sg1.tar` 1571c1a3...), contributor latents by W+ inversion (500
  Adam steps, lr 0.02, LPIPS + MSE + 0.1 ID), then the MIPGAN optimisation (150 Adam steps, lr 0.03 x 0.95 per 6,
  0.0002 Perc + 10 ID + 1 MS-SSIM + 1 ID-Diff). mip2 = our MIPGAN-II-style re-implementation (A28): e4e + StyleGAN2
  FFHQ config-f (`gan_weights.tar` e06f19af...), same MIPGAN loss; FRLL only (the MAD22 MIPGAN-II cell). Generator
  code = branch gan1 24cc974 files vendored unchanged (`src/AG1/vendor/VENDOR.sha256`, the A33 hashes). Wrapper
  `ag1_gen.py` (5acbff93...): `generate.mipgan` for every alpha-0.5 job; `mipgan_alpha` (weights 1 - a, a; ID =
  (1-a) dA + a dB, ID-Diff = 2 |(1-a) dA - a dB|) for AG3 / AG3T, equal to `generate.mipgan` term by term at a = 0.5.
  Its alpha-0 point is not R2 (R2 has ID-Diff = 0), so AG3's curve uses its own alpha-0 level. Fixed iteration
  counts everywhere; TF32 off, cuDNN deterministic; a non-finite latent or loss stops the shard. Logged per image:
  final loss and terms at the final latent, latent distance from the mean latent (mean over 18 layers) and of the
  initial latent, generator-side w600k cosines, seconds. Output 1024 x 1024 RGB PNG, the published files' format
  and framing (eyes at (387, 482) / (634, 481) vs (385, 476) / (640, 478) on a published MIPGAN-I file).
  *Input alignment (flagged for the author):* the H4 / A33 path, `prep_eval.kps` -> `gancommon.ffhq_align` 1024
  (LANCZOS shrink, reflect padding with Gaussian blur and median blend of the padded border, bilinear quad warp) ->
  `cv2.resize` INTER_AREA 512. These are not on OWNER_BRIEF's allowed list; they are the generator input step of
  the approved A33 set, used on purpose and identically for every rung. Reflect padding hit 158 of 604 photos
  (FERET 145 / 200, FRGC 13, FRLL 0), balanced between twins and morphs within a pool, not across pools.
  *One platform:* every data image is generated on WCSS H100 in the container of H4 / H4b
  (`pytorch_latest.sif`); `run.sh` refuses to run without it (exit 5). The same code gave a different image on the
  GB10 (mean 15.5 grey levels), so rungs are never mixed across platforms or torch stacks.

- **Detectors (scoring).** Released MADation ViT-B/16, ViT-L/14, SelfMAD HRNet-W18 (our pipeline and own crop); FE /
  FS variants descriptive. Path: `src/AG1/ag1_score.py` (29a87898...) = the registered A43 adapter (339533c4...)
  with a43 -> ag1, over amendment G's `a41g_score.py` (f53612cb...) unchanged, run from a c669666 job root
  (`make_score_root.sh`); manifest `ag1.csv` pinned by the AG1 data registration before any score. MixFaceNet-MAD
  (RGB path): no AG1 scorer (its scorer is bound to the A46 plan); "not scored", never inferred. Open for the
  author: which SelfMAD row is primary, and whether ViT-B/16 alone decides; until then all four rows are primary.

- **Primary metric.** AUC with 95% two-way (dyadic) person bootstrap, B = 10,000 (`a41_read.py` `Draw`, copied), one
  draw per pool, distinct seeds per pool. Shares = step d' / d'(R0 vs R4).

- **Readings.** Both readings below are registered now; the author's class definition (`07_DECISIONS_NEEDED.md`,
  item "one-photo reconstructions"; `14_CLASS_DEFINITIONS.md` pending) selects one **before any score is read**.
  The other is printed, labelled "not selected".
  - *Reading A (11_AUDIT_PLAN; R2 = processed genuine image):* R2 vs R4 reads morphing if AUC >= 0.75, lower bound
    > 0.65 and R0 -> R2 share <= 0.2; reads the benchmark if the R0 -> R2 share lower bound >= 0.5, or folded AUC <
    0.60 with folded upper bound < 0.65; else mixed.
  - *Reading B (author's position of 11 Nov, 16:00; R0 -> R2 = generated-image detection, not penalised):* R2 vs R4
    reads morphing if AUC >= 0.75 and lower bound > 0.65; does not read morphing if folded AUC < 0.60 with folded
    upper bound < 0.65; else mixed. The R0 -> R2 share is printed as "generated-image detection".
  - FRLL prints R0 -> R1 and R1 -> R2 as the two parts of R0 -> R2. Every generator cell carries "R2 = the
    generator's reconstruction of one photo".
  - Side, R3 vs R4 and R2 vs R3: no identity reading (folded < 0.60, folded upper < 0.65) / twin artefact (AUC <
    0.40, upper < 0.5, cell invalid) / identity reading (>= 0.75, lower > 0.65) / mixed. Noise floor: R3 vs RT AUC on
    the RT persons. Flag rates of R0 / R2 / R3 / R4 at the release's corrected-MAD22 EER threshold with exact
    intervals.
  - *R3 vs R4 in matched bins (also reported, never the stated reading):* tertiles of the MS-SSIM term x tertiles
    of latent distance (non-identity terms only; final loss is identity-driven and is not matched on); cell-weighted
    AUC with bootstrap interval; "not matchable" if the cells holding both rungs cover < 50% of R4.
  - *Session-gap sensitivity (primary pool, CPU):* R3 vs R4 restricted to morphs whose B photo lies within 60 days
    of the host's A' (about 72), and stratified by tertiles of the session gap.
  - *AG2 (two-sided):* read only if the release's bridge AUC (PUB vs BR) lies in [0.40, 0.60]; otherwise
    "implementation-confounded". Then: "reverses" if AUC < 0.40 with upper < 0.5; "collapses to chance" if folded
    AUC < 0.60 with folded upper < 0.65 (both mean the cell measured generator output vs camera); "retained" if AUC
    >= 0.75, lower > 0.65 and within 0.10 of the camera AUC; else mixed. Neither direction is "the expected one".
  - *AG3 / AG3T:* AUC of each level against R2 of the host photos s1. Ramp if Spearman of level means >= 0.8 and
    AUC(0.1) < AUC(0.5) - 0.10 with AUC(0.1)'s upper bound below AUC(0.5); flat if |AUC(0.1) - AUC(0.5)| <= 0.05
    with AUC(0.1)'s lower bound > 0.5; else mixed. Read against the achieved dose (glint cosine to A and to B per
    level). A ramp in AG3 and not in AG3T points at the second identity; a ramp in both at the second photo. alpha
    also moves the latent, perceptual and MS-SSIM targets, so "ramp" is not by itself "identity".
  - Primary cells: mip1 x primary pool x 4 release rows. One-sided bootstrap p of "R2 vs R4 AUC <= 0.65" per cell;
    Holm within AG1 printed; the family-wide Holm (11_AUDIT_PLAN, 12 cells) is applied by the lead with these p.
    FRLL, single-database and mip2 cells descriptive.

- **Gates (computed by `ag1_read.py --gate-only` and committed before any detector score is opened).**
  - G-b (glintr100, not the w600k loss model), per generator and pool: oracle AUC of -cos(image, host camera photo)
    for R4 vs R3 >= 0.90 (a sanity check: near-guaranteed by construction); R4 verifies both contributors in >= 70%
    at FMR 1e-3 on the input photos (threshold from impostor pairs of the pool's camera photos; A23's 0.2394 beside),
    also printed on photos the generator never saw (s2(p) for A, s1(q) for B); R3 verifies A in >= 90%; R2
    false-match rate against other persons' camera photos printed. Failure labels: "morph construction weak" (R4
    side) or "twin construction invalid" (R3 side); such a cell is not read. Negative control: twin(A, A') vs
    twin(A', A) is the same objective under MIPGAN's symmetric loss; only the floating-point summation order differs,
    and that alone makes the runs diverge (GB10 smoke: mean 3.9, max 133 grey levels). So RT is printed as the
    run-to-run perturbation (pixel difference, no gate) and the R3 vs RT detector AUC is the noise floor. In effect
    G-b has no informative negative control; stated as such.
  - G-a: the release's EER on the corrected MAD22 cell (our FRLL R0 vs PUB rows) within 3 points of the published
    number (given to the reader as a file); else "not reproduced, descriptive".
  - G-c (probe on frozen features): not computed by AG1; cells carry "G-c pending" until the feature cache provides it.
  - Generation sanity: every job's PNG present, finite latent and loss (enforced in `ag1_gen.py`); inversion cosine,
    final loss and latent distances (final and initial) per rung printed; aligned-flag rate per rung >= 0.90 (else
    flagged); identity-disjoint pools (max cross-pool w600k cosine 0.331), val10 excluded.

- **Stop rule and budget.** Rates measured on WCSS H100 (H4 job 6237081: inversion 23.3 s, MIPGAN-I 150 steps 6.9 s;
  A28 MIPGAN-II 9.3 s per image incl. e4e). 13 tasks (`shards.csv`): 3,421 images, 608 inversions; 9.8 H100-h of
  compute (smoke 0.05, FRLL mip1 2.5, primary mip1 4.2, FRLL mip2 1.6, AG3 + AG3T 1.4), 15.6 slot-h of `est_minutes`
  (x 1.3 + 12 min per task). Order: the two smoke tasks go to ready/ alone; the rest only after both return
  (48 slots start tasks in parallel, so queue order alone protects nothing). AG3 tasks go to ready/ only after
  o04-o07 have returned (exit 3 otherwise). One retry per failed shard; a shard failing twice stops that pool.

- **Command (tested).** See `result.md` (DGX GB10 runs of the unchanged `run.sh` on the smoke shards; WCSS
  login-node import test; pack hashes on Lustre). Not tested: the container path inside a slot, any H100 run of
  `ag1_gen.py`.

- **Pre-run review:** 11 Nov, experiment-reviewer: GO WITH FIXES. Fixed in amendment 1 (below). Not fixed: the
  mirror-twin arm (needs the author's ruling on flipping), MixFaceNet scorer.
- **Amendment 1 (11 Nov, before any data image):** both readings A and B registered, selection by the author before
  scores; hypothesis worded "two photographs"; matched bins on non-identity terms, also-reported only, coverage rule,
  interval; session-gap sensitivity; AG2 bridge gate; G-b on unseen photos, R2 false-match rate, R3 >= 90% rule,
  failure labels, honest negative control; cuDNN deterministic and finiteness checks; dmenv fallback removed (one
  torch stack); RT extended to 152 persons; AG3 alpha 0 via `mipgan_alpha`; AG3T twin-dose arm; primary pool
  pooled; distinct bootstrap seeds per pool; FERET decode fix in the manifest builder; input alignment flagged.
- **Result:** pending.
