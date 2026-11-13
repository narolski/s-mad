# DRAFT: contrast 2-prime, a new confirmatory storage test of the fresh-seed protocol networks (FS1 checkpoints)

DRAFT for the author. Nothing in this file is registered and nothing it describes has been run or scored. Written by
the MS1 owner at the lead's request (13 Nov 2026, after the FS1 read at 06:38 and its review
`experiments/reviews/REVIEW_PN1_FS1_20261113.md`, option (b) and H-new-1 / H-new-2). Registration needs: the author's
amendment of FINAL section 1 (item 4 below) committed first, then this text committed, then an independent pre-run
check, all before any score of the 15 FS1 checkpoints on the data below exists.

## 1. Data: the MS1 FFHQ hold-out (development data; never a benchmark)

Built by the multi-source training set experiment (MS1, part 1, commit 3d4411b; build 9f02906-d5603db) with the
unchanged aligner and morph engine; rows `fam = ms1ffhq` of the MS1 evaluation manifest
(`/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv`, sha256 `d1fab6ad…`), images inside the MS1 fit pack
`pn1_pack_ms1.tar` (`c11b16bc…`):

| kind | rung, strength | n | class |
|---|---|---|---|
| native photo | photo, "" | 300 | genuine |
| stored copy, 61.2 px (trained size) | photo, fm61 | 291 (9 failed re-alignment) | genuine |
| stored copy, 112.7 px (size no network trained on) | photo, amsl112 | 290 (10 failed) | genuine |
| two-person morph (OpenCV-style engine, 0.5) | u50, "" | 150 | attack |
| stored morph, 61.2 px | u50, fm61 | 150 | attack |
| stored morph, 112.7 px | u50, amsl112 | 149 | attack |
| warp-only image | zero, "" | 150 | single-subject (placement only) |

**Proof of non-exposure (computed 13 Nov 2026 before the commit that adds this draft (4591b9f, 06:52:42), from the manifests):**
- None of the 1,480 hold-out rows is among the 19,797 rows the FS1 networks scored (FS1 manifest `f0f29f22…`): 0 shared
  ids and 0 shared image sha256 (FS1 pack SHA256SUMS against MS1 pack SHA256SUMS). The FS1 checkpoints' stored score
  files (`scores_eval.npz`, checked on PN1_Sb_s403) hold 19,797 ids, none starting with `hold_`.
- The 300 hold-out FFHQ keys share no key with the FFHQ rows of the FS1 manifest (ffhqm HN2 and landmark_combined), and
  MS1's exclusion proof (`experiments/MS1_multi-source-training-set/exclusion_proof.json`) shows no key, file or
  identity overlap (glintr100 cosine < 0.40; largest 0.396) with ffhqm's 2,000 genuine persons and the 2,000
  contributors of its sampled pairs, and hold-out vs MS1 training persons at most 0.374.
- FS1 training sets share no person with the hold-out: train_A, train_B and train_Sb hold FRGC and colorFERET images only
  (db counts A frgc 1,004 / feret 988; B 3,878 / 3,884; Sb 4,398 / 3,988 rows); FFHQ is not in them.
- Networks that HAVE scored the hold-out: only the MS1 fits (arms Sb, SbM3, SbV at seeds 403-407, trained on rented
  L40S 48 GB under MS1-D2; the hold-out rows are in their fit-pack evaluation list), 11 of 15 tars local at that time
  (MS1_Sb_s403-406, SbM3_s403-405, SbV_s403-405), none opened by any reader. The 20-step DGX smoke scored only the
  first 64 manifest rows (FS1 rows). Not scored by: the 15 FS1 checkpoints A, B, Sb at seeds 403-407; the replicate A
  seed 401; seeds 401/402; the Sp fits (their manifest is byte-equal to FS1's); any amendment-14, HN2 or TT1 job.
- Consequence (binding if registered): MS1's own read (`src/MS1/ms1_read.py`, which prints storage shifts and flags on
  this hold-out for MS1's Sb, a network of the same recipe) must not run before this test is registered; otherwise the
  hold-out's storage behaviour for the Sb recipe is known before the margins are fixed. MS1's last machine ends about
  11:00 on 13 Nov.

## 2. Contrast 2-prime (reviewer's text, forks closed)

Networks: the 15 FS1 checkpoints, arms A (plain), B (protocol), Sb (spliced), seeds 403-407, last checkpoint, exactly
the result tars of FS1 (`/mnt/t7/smad_next/PN1/results_fs/PN1_<arm>_s<seed>.tar`, sha256 in `fs_kept/`). Scores: logit
without flip from the unchanged `src/PN1/rescore.py` (meta.json + last_trainable.pt), on one GPU model (section 5).

Per network n and storage size z in {fm61, amsl112}, on the genuine photos with both a native and a stored copy
(paired by person; 291 for fm61, 290 for amsl112):
- flag increase Δf(n, z) = share(stored logit > 0) − share(native logit > 0) (own rule; points);
- mean shift Δm(n, z) = mean(stored − native logit) / SD(native genuine logits of n over the 300 native photos).

Within each seed s:
- **Positive control**: Δf(A_s, z) ≥ +0.05 AND Δm(A_s, z) > 0. A seed where the control fails at size z is
  "control failed" for that size and counts as NOT passing for every X at that size.
- **X ∈ {B, Sb} passes seed s at size z** if Δf(X_s, z) ≤ Δf(A_s, z) / 3 AND |Δm(X_s, z)| ≤ Δm(A_s, z) / 3 (both
  inclusive, full float precision).
- **X passes contrast 2-prime** if it passes on at least 4 of 5 seeds at fm61 AND on at least 4 of 5 seeds at amsl112.
- **X fails** if it passes on at most 1 seed at either size while A's control is met on at least 4 seeds at that size.
- **Uninformative** if A's control fails on 2 or more seeds at either size. Otherwise "inconclusive, no claim".
- Lost seeds: a seed with a missing, non-finite or gate-failed (section 5) network of A or X counts as not passing for
  X; the 5-seed denominator stays.
- Printed (no decision): per seed and size, Δf and Δm of A, B, Sb with 95% intervals from 2,000 person bootstraps
  (persons resampled with replacement, the same draw for native and stored, `numpy.random.default_rng(20261131)`);
  the ratio Δf(X)/Δf(A); the exact one-sided sign test across seeds of {Δf(X_s) < Δf(A_s)/3} (5 of 5: p = 1/32); the
  same statistics at the network's τ_cam and τ_dev(ii) (F10, item 4).
- Disclosure: the one-third margins, the +5-point control and the two sizes were set knowing the FS1 effect sizes on
  OTHER FFHQ persons (ffhqm HN2: A's own-rule flags rise +14.7 to +21.8 points, B +2.5 to +5.5, Sb +0.5 to +2.7; mean
  shifts A +0.61 to +0.79 SD, B +0.07, Sb −0.09). No score of any FS1 checkpoint on the hold-out exists at this
  writing. Claim if passed: "storage reaction at the own rule reduced to at most one third of the plain recipe's on
  unseen persons and an unseen storage size, 5 seeds" — never "removed".

## 3. Co-registered reads

**H-new-1 (storage evasion).** Statement: protocol negatives teach "resampled means genuine", so storing a morph small
lowers Sb's score. Per network and size z: miss(n, z) = share(stored u50 logit ≤ 0) on the stored morphs (150 fm61,
149 amsl112); miss(n, native) on the 150 native u50.
- **Supported** if miss(Sb_s, z) − miss(Sb_s, native) > +0.03 on at least 4 of 5 seeds at either size.
- **Falsified** if that difference is ≤ +0.03 on at least 4 of 5 seeds at both sizes.
- Otherwise "inconclusive". Printed: the same for A and B (the reviewer expects A's miss to fall); intervals by
  bootstrap over morph pairs (2,000, rng 20261132). Note: one morph is 0.67 points; +3 points is about 5 morphs.
- B is read by the same rule and printed (it matters for freeze step 2).

**H-new-2 (the plain reaction is a person-level tail tied to sharpness; measurement only).** Sharpness = `lapvar_face`
(Laplacian variance of the canonical face box) of each native hold-out photo, computed with AF0's `cues_all.one`
through `src/PN1/cues27.py` (unchanged, sha256 1ab50f30… for cues_all), before any score. Per A network and size: the
share of A's net flag increase (persons going from ≤ 0 to > 0 minus the reverse) contributed by persons in the top
sharpness quartile (quartile edges fixed from the 300 native photos). Predicted ≥ 0.50 at both sizes on at least 4 of
5 seeds; falsified if ≤ 0.35 on at least 4 of 5 seeds; otherwise "inconclusive". Zero GPU.

## 4. Proposed amendment of FINAL section 1 (for the author; the author decides)

Replace steps 1-3 of `experiments/FINAL_sealed-benchmark-read/prereg.md` section 1 by:

> Inputs: FS1 contrast 1 (v4 frozen, ac585b7), the original FS1 contrast 2 (reported as read: "uninformative", the
> plain arm's control failed), and contrast 2-prime with H-new-1 as registered at commit <hash>.
> 1. **Sb** is frozen if FS1 contrast 1 is "replicated" (it is: 5 of 5 seeds, read 13 Nov 06:38) AND contrast 2-prime
>    "passes" for Sb with A's positive control met AND H-new-1 is not "supported" for Sb (no storage evasion).
> 2. **Otherwise, B** is frozen if contrast 2-prime "passes" for B with A's positive control met AND H-new-1 is not
>    "supported" for B (contrast 1 is not required for B).
> 3. **Otherwise, no method** is frozen; the read is an audit of the comparison set only.
> Both the failed original contrast 2 and contrast 2-prime are reported in the paper, with the disclosure that
> contrast 2-prime was registered after the original failed on its control and that its margins were set knowing the
> FS1 effect sizes on other FFHQ persons. The MS1 rule and the BB2 row are unchanged.

**Endpoint fix (review F10), proposal:** at τ_dev(i) (5% false alarms on R0 + AF0, our training-source photos) every
arm and seed flags 96-98% of FFHQ genuine photos (thresholds about −3.6 for A and B, −3.4 for Sb), so a BPCER at
τ_dev(i) on any unseen genuine pool reads about 100% and cannot be the confirmatory operating point. Proposed text for
FINAL section 0 / the endpoint: "The confirmatory endpoint is AUC and EER within each cell (morphs against that cell's
genuine photos), computed by the pinned metrics function. Printed beside them, never deciding: BPCER and APCER at the
own rule, at τ_dev(ii) (EV1 devbona) and at τ_dev(i), each labelled with its pool. No fixed-threshold claim is made for
our networks." M4's "the decision uses (i)" is withdrawn.

## 5. Where and how to score (proposal; nothing is changed until the author decides)

- **Platform:** one rented MS1 machine, ms1m1b (NVIDIA L40S 48 GB, GPU-c1ff3444…, torch 2.2.1 / CUDA 12.1, timm
  1.0.27; the FS1 checkpoints were trained and scored on one A100 PCIe 40 GB with pn1_score.py, torch 2.2.1, TF32 on).
  ms1m1b already holds the MS1 fit pack (FS1 code, base weights, the FS1 evaluation images and the hold-out images), so
  only the 15 FS1 result tars (3.6-4.7 MB each, about 65 MB) are uploaded. Fallback: ms1m2 (ends about 11:00). The
  fresh-seed host pn1fs is not proposed: its uplink is about 1 MB/s and it would need the hold-out images uploaded;
  the A100 there would be the same GPU model as FS1, but the gate below makes the L40S equally safe.
- **Platform gate (fixed now):** each of the 15 checkpoints is rescored on L40S on rows it already scored on the A100:
  FS1 fam `af0` (1,339) and fam `ffhq` (5,000: HN2 genuine, landmark_complete orig and resmatch). A network passes if,
  against its stored FS1 logits, the 99th percentile of |Δlogit| ≤ 0.05, the maximum |Δlogit| ≤ 0.15 and the own-rule
  decision agrees on ≥ 99.5% of the 6,339 rows. A deciding network that fails the gate makes the decision of every
  contrast it enters "not available" (for contrast 2-prime: the seed counts as not passing, section 2). Gate values
  printed for all 15. (References: the SXM4/PCIe A100 replicate agreed within 0.044 logits; RS1's cross-platform
  feature check found logit differences up to 0.022.)
- **Order on ms1m1b:** after its MS1 queue and held-out step end (ALL_DONE_m1), under the host lock, before RELEASE:
  rescore the 15 checkpoints on fam af0, ffhq and ms1ffhq (`src/MS1/c2p/remote_c2p.sh`, draft); about 15 x 2-3 min =
  about 40 min of L40S, about 0.4 USD.
- **Commands (draft scripts, not run):**
  ```
  touch /mnt/t7/smad_next/vast/ms1m1b/HOLD            # by the lead on the author's go, BEFORE ms1m1b's queue ends
  cd /home/narolski/smad-next/src/MS1/c2p
  bash drive_c2p.sh 147.124.211.53 9630 /mnt/t7/smad_next/vast/ms1m1b m1 upload   # 15 FS1 tars + list (needs HOLD)
  bash drive_c2p.sh 147.124.211.53 9630 /mnt/t7/smad_next/vast/ms1m1b m1 start    # waits for the queue end and the lock
  bash drive_c2p.sh 147.124.211.53 9630 /mnt/t7/smad_next/vast/ms1m1b m1 pull     # repeat until "C2P kept"; removes HOLD
  ```
- **Release logic change needed (one line in `src/MS1/rented/drive_ms1.sh`, pull step, immediately before each
  `touch "$L/RELEASE"`):** `[ -f "$L/HOLD" ] && { log "HOLD present: RELEASE deferred"; exit 0; }`. The MS1 loop keeps
  pulling; RELEASE is written in the first round after `drive_c2p.sh pull` has fetched, verified and second-copied
  `C2P_m1.tar` and removed HOLD. The loop calls the script by path each round, but because the running loop process
  must not read a script rewritten in place, the loop is stopped while sleeping and restarted after the edit (as done
  at 06:10). The reader (contrast 2-prime, H-new-1, H-new-2, gate) is written and committed before `pull`.
- **Decision needed by about 09:30 on 13 Nov** (ms1m1b's queue is expected to end about 09:50; HOLD and the edited
  loop must be in place before that). If later: ms1m2 by about 10:40. If neither: the step needs a fresh lease
  (about 0.5 USD, plus the 15.5 GB pack upload) or the DGX GB10 (another GPU model, same gate).
