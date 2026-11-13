# Which part of the training protocol removes which shortcut, and does the result replicate (AB1): registration

Written 13 Nov 2026 from 08:55 CET (machine clock) by the AB1 owner (Claude agent for the lead), before any AB1 fit
exists and before any score of any network at seeds 408-412 exists. Source of the task: the lead's message of 13 Nov
morning, which takes items 2, 3 and 4 of section 2 of `experiments/reviews/STRATEGIST_IDLE_GPUS_20261113.md`.
Status: registered at the git commit that adds this file (after the pre-run review `PRERUN_AB1_20261113.md`, GO WITH
FIXES, fixes F1-F10 applied below; section 12 lists them).

**What this is not.** No arm here is a candidate for the frozen method. FINAL section 1 freezes only Sb, then B, then
the MS1 version of Sb; no selection clause for any other arm is registered. Every AB1 arm is an ablation or a
replication row. One network per arm and seed, last checkpoint, no ensembles, no seed picking, every arm and seed
reported. Development data only: no FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace or sealed row is in any AB1 pack
(asserted by `src/AB1/mk_ab1.py` for every evaluation row; every training row is asserted to be an FS1 training row
of FRGC or colorFERET); `manifests/valx.csv`, FST and A12SP are never opened; `prep_eval.py` and
`prep_gtest.py` are not touched. No new image operation: every training image is already in the FS1 pack; the
manifests are made by dropping row kinds from existing manifests.

## 0. Terms and what was known when this was written

- Training row kinds of the FS1 manifests (`/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/`, PN1 prereg section 0
  and amendments 4 and 10): camera photos `af0_photo`, `lad_R0` (genuine); two-person morphs `af0_u50`, `lad_R4`
  (attack); **warp-only images** `af0_zero` (toward the pair's two-person mean shape) and `lad_R2w` (toward the host's
  own two-photo mean shape); **halves** (the morph's own two warped halves) `af0_half`, `lad_half`; **stored-small
  copies** (shrunk to 61.2 px between the eyes and enlarged back) `af0_photo61`, `af0_half61` (negatives) and
  `af0_u5061` (attacks); **face-spliced morphs** `lad_S4` (attack) with their **matched splice negatives** `lad_S0`
  (seam only) and `lad_S3` (same-person splice).
- Arm names: **A** plain (photos against morphs, `train_A.csv` af070a60…); **B** protocol negatives (`train_B.csv`
  bd53dc32…); **Sb** protocol negatives plus face-spliced morphs with matched negatives (`train_Sb.csv` 2cf3fda3…).
- Known at writing (disclosed): the FS1 numbers of seeds 403-407 in `17_MORNING_REPORT_20261113.md` (landmark_combined
  AUC A 0.736 ± 0.031, B 0.674 ± 0.028, Sb 0.860 ± 0.030; contrast 1 met on 5 of 5 seeds; FFHQ storage rise A +14.7
  to +21.8 points, B +2.5 to +5.5, Sb +0.5 to +2.7; Sb flags 31-41% of same-person face splices and 0 of 100
  development S0 images at seeds 401/402; Sb S3 0.34 / 0.36 at 401/402); the 27-statistic baseline 0.814 (PN1
  amendment 15). The C2P read of the FS1 checkpoints on the MS1 FFHQ hold-out was **not** known at writing; whether
  it is known at the registration commit is stated in section 11. No warp-only, halves or softened-photo placement of
  any FS1 network was opened by the owner. Margins below were set without the per-component values of any network.

## 1. Questions

1. Replication (strategist item 3): do the replacement storage test (contrast 2-prime, C2P, registered at 2715e48)
   and contrast 1 (Sb above B on landmark morphs, FS1 v4) replicate on five new seeds, 408-412, on another platform?
2. Mechanism (strategist item 2): which component of Sb carries which reduction? Storage (stored-small copies?),
   warp (warp-only images?), softness (halves or stored-small copies?), same-person splice (matched splice negatives?).
3. Conditional (strategist item 4): is Sb under-trained? Run only on the lead's word (section 6).

## 2. Arms and manifests (built, `src/AB1/mk_ab1.py`, outputs `/mnt/t7/smad_next/AB1/`, summary `ab1_summary.json`)

Volume matching follows the Bv rule of PN1 amendment 10: the number of unique rows dropped from Sb's 5,535 unique rows
is drawn back from the arm's remaining unique rows (seeded, without replacement) as repeated rows, so that every
leave-one-out arm has Sb's 5,535 rows before the class balance; then the unchanged amendment-4 balance inside each
database × storage stratum (`mkmanifests.balanced_strata`).

| Arm (plain name) | Rows dropped from Sb (or added to A) | Unique images | Repeated for volume | Rows after balance | sha256 |
|---|---|---|---|---|---|
| **SbZ** Sb without the warp-only images | af0_zero 730, lad_R2w 156 | 4,649 | 886 | 7,868 | 9b429554… |
| **SbH** Sb without the native halves | af0_half 1,456, lad_half 248 (af0_half61 kept) | 3,831 | 1,704 | 7,200 | b8e17cd2… |
| **SbS** Sb without the stored-small copies | af0_photo61 254, af0_half61 363, af0_u5061 366 | 4,552 | 983 | 8,692 | 9c7e43ff… |
| **AS** plain plus stored-small copies only | A + af0_photo61 254, af0_u5061 366 (from train_B) | 2,146 | 0 (not matched) | 2,850 | b7e9f3a3… |
| **Sp** Sb without the matched splice negatives | lad_S0 156, lad_S3 156 (registered PN1 Sp manifest, unchanged) | 5,223 | 0 (as registered) | 7,762 | cf386dc7… |
| B, Sb, A (replication) | FS1 manifests, unchanged | 5,099 / 5,535 / 1,526 | – | 7,762 / 8,386 / 1,992 | bd53dc32… / 2cf3fda3… / af070a60… |

Choices stated:
- `af0_half61` (a stored-small copy of a half) is removed only in SbS, never in SbH (review F2: it is 200 of the 225
  unique FRGC stored-small negatives of Sb, so removing it in SbH would also remove most of the storage component).
  The removed sets of SbZ, SbH, SbS and Sp are disjoint. SbH therefore reads "native halves, given their stored copies".
- "Volume matching" (review F6): with steps fixed (6,250 × 256) every arm sees the same number of samples; the repeated
  rows only give a random subset of the remaining images double weight. Passes per unique image still differ from Sb by
  a factor of about 1.19 (SbZ), 1.44 (SbH) and 1.22 (SbS); SbH repeats 44% of its unique images (1,704 of 3,831). An
  omission arm is therefore also an arm that sees each remaining image more often; this is stated with every row.
- AS is not volume-matched: it is compared with A, and matching it to Sb's volume would repeat every image 2.6 times,
  unlike any registered arm. It is read only against A (sufficiency of history crossing).
- Sp is the registered PN1 Sp manifest (PN1 prereg "Registration Sp"), kept unchanged so that AB1's Sp at 408-412 is
  the same arm as the Sp fits at 403-405. **Why Sp is repeated here:** the 403-405 Sp fits ran on the rented A100 PCIe
  host, and scores depend on the GPU model (TT1: three failed platform gates). Every AB1 contrast is paired within seed
  against Sb on one platform; without Sp at 408-412 on H100, the matched-splice-negative component could not enter the
  same table as the other three components. Cost 5 fits. The 403-405 Sp read stays its own registered result.
- The evaluation manifest `ab1_eval.csv` (93a5ba23…, 21,277 rows) = the 19,797 rows of FS1's `pn1_eval.csv`
  (f0f29f22…, order kept) + the 1,480 MS1 FFHQ hold-out rows (`fam ms1ffhq`, byte-equal to the MS1 pack's rows, the
  C2P data). Families: af0, ladder, splice (our FRGC / colorFERET images), ffhq, ffhq_lcomb, ms1ffhq (FFHQ, the
  development comparison set; never a benchmark).
- Overlay v2 `ab1_overlay.tar` (on WCSS as `packs/AB1/ab1_overlay_v2.tar`) sha256
  `171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149` (563,363,840 bytes; 5 manifests, ab1_eval.csv, 1,480
  hold-out images, AB1SUMS); it adds files to the FS1 pack and replaces none (run.sh checks the FS1 SHA256SUMS after
  unpacking). Overlay v1 (`4e3afaa1…`, the first SbH) is used by the smoke job only.

## 3. Networks, seeds, platform

- Recipe unchanged: CLIP ViT-B/16 MADation arch with LoRA, the FS1 `train.py` (cbb2cbd1…) and flags (PN1 prereg
  section 4), 6,250 steps, batch 256, last checkpoint; scoring by the unchanged `pn1_score.py` inside the pack (logit
  without flip, TF32 on as in FS1). Task script `src/AB1/run.sh` (a copy of `src/SE1/run.sh` b2a975f1 with AB1 changes
  marked; sha256 pinned in section 11).
- Seeds 408, 409, 410, 411, 412 for every arm.
- **Platform: WCSS H100 only** (partition lem-gpu-short, `gpu:hopper:1`, 8 CPUs, 64 GB, local disk via $TMPDIR,
  `--extra=FORCE_RM_TMPDIR`, Python `~/dmenv` torch 2.11 cu128). Every fit and every score of AB1 comes from H100s;
  GPU name and UUID are in each tar (`gpu.txt`). A network whose `gpu.txt` does not name an H100 is not read. Athena is
  not used (dispatcher, 13 Nov 08:50: all A100 nodes reserved until 22 Dec); a move to another platform would be a
  deviation for the lead, and then all networks of AB1 would move, never a mix.
- **A and Sb are AB1's own fits (lead's decision, 13 Nov 09:15, via the dispatcher).** The first draft reused the A
  and Sb networks of the seam-shortcut training arm (SE1) at 408-412. The lead moved SE1 to rented A100 PCIe machines,
  so SE1's networks are on another GPU model; AB1 fits A and Sb itself on WCSS H100 and never reads an SE1 network
  (review F1). AB1's array (`src/AB1/wcss/ab1_fit.sbatch`, array 0-39) fits A, Sb, B, Sp, SbZ, SbH, SbS, AS at each
  seed, seed by seed: 40 fits. SE1's A and Sb at 408-412 and AB1's are different networks of the same arm and seed on
  different platforms; each experiment reads only its own, and neither is compared with the other.
- Platform measurement (descriptive, decides nothing): the smoke job rescores the FS1 network Sb seed 403 (A100 PCIe
  original) on the H100 through the unchanged `rescore.py` (6f6eede7) with TF32 on (`rescore_tf32.py` 0d0b6b6f) on
  the 6,339 FS1 gate rows; printed: 99th percentile and maximum |Δlogit| against the stored A100 logits and own-rule
  agreement (the C2P gate statistics). AB1 compares no H100 number with an A100 number; FS1 values are printed beside
  AB1 values only, labelled "other platform, other seeds".

## 4. Reads (every AB1 network, own rule = logit > 0; development data only; the 191-host test ladder is not read)

| Read | Rows (all in ab1_eval.csv) | Definition |
|---|---|---|
| C2P quantities | ms1ffhq: 300 native photos, 291 fm61 / 290 amsl112 copies, 150 u50 morphs with copies | Δf(n, z), Δm(n, z), Δm_att(n, z), upper 95% bound of Δf (2,000 person draws, `default_rng(20261131)`, same draws for all networks), exactly C2P.3 and C2P.4, computed with the functions of `src/PN1/c2p_read.py` (`holdout`, `net_stats`, imported unchanged) |
| landmark_combined AUC | ffhq_lcomb: 1,000 orig morphs vs 2,000 resmatch genuine | rank AUC, ties half; 95% interval from 2,000 bootstraps of images within class (`default_rng(20261118)`, as FS1) |
| Same-person splice placement (S3) | development splice S3, 100 | share > 0 |
| Seam-only placement (S0) | development splice S0, 100 | share > 0; and raw development S0-vs-S4 AUC (S4 100), as the Sp registration |
| Warp-only placement | development ladder R2w OpenCV 100 + R2w4 OpenCV 100 + AF0 development zero 171 = 371 | pooled share > 0 (each pool printed) |
| Halves placement | AF0 development halfA 288 + halfB 322 = 610 | share > 0 (printed only) |
| Development storage rise (called "softened-photo rise" in the task) | development ladder R0_61, R0_112 (200) + AF0 development photo 61, 112 (252) = 452, against their 226 native photos | Δsoft = share > 0 of the 452 shrunk-and-enlarged copies minus share > 0 of the 226 native photos; each size printed. It is the stored-small operation on development persons of the training sources (FRGC / colorFERET), so for SbS it overlaps C2P (review F2) |
| Training-row flags (printed only) | each arm's own training rows (`scores_train.npz`) | share > 0 per training row kind |
| Camera-photo flag rate | development ladder R0 100 + AF0 development photo 126 = 226; ms1ffhq native photos 300 | share > 0 (printed only) |
| Floor and baseline | ffhq_lcomb cues `a14_lcomb.npz` (pinned) | best of 27 statistics (direction-free AUC) and the 27-statistic baseline 0.814 (PN1 amendment 15), printed beside every landmark_combined AUC |

"Rise of arm X" for a read means read(X_s) − read(Sb_s) at the same seed s (for AS: AS_s − A_s).

## 5. Hypotheses, pass and fail rules (fixed now)

Seed counting (FS1 v4 table): with n read seeds, a rule "on ≥ 4 of 5" means 4 of 5 when n = 5, 4 of 4 when n = 4;
with n ≤ 3 the hypothesis is "not read (too few seeds)" (review F3: for the C2P rule, the X network's read seeds are
counted among A's control seeds at each size; C2P's own rule that a lost seed keeps the denominator 5 still applies
when 4 or 5 seeds are read). A seed is read for a hypothesis only if every network the
hypothesis needs at that seed finished with a finite loss, a verified tar and complete finite scores on the rows read.
Margins inclusive at full float precision. Middle outcomes: "inconclusive, no claim".

**R1. C2P replicates (Sb and B).** C2P.3 and C2P.4 applied unchanged to A, B, Sb at seeds 408-412 (A's control,
X passes (s, z), the verdict rule "passes / fails / uninformative / inconclusive", H-new-1 "supported / falsified /
inconclusive"). R1 for X ∈ {Sb, B}: **replicated** if C2P "passes" for X; **not replicated** if C2P "fails" for X;
"uninformative" if C2P is uninformative; otherwise "inconclusive, no claim". H-new-1 is printed with its registered
verdict for Sb and B. The freeze rule of FINAL is NOT read here: AB1 seeds do not enter the freeze.

**R2. Contrast 1 replicates.** FS1 v4 contrast 1 unchanged: seed meets it if Sb − B ≥ +0.05 and Sb − A ≥ −0.02
(landmark_combined AUC); seeds with B ≥ 0.95 untestable; **replicated** on ≥ 4 of 5, **not replicated** on ≤ 1. Floor:
"exceeds the best single statistic" only if on every read seed the 2.5% bound of (Sb AUC − floor maximum re-taken in
the same draw) is above 0.

**H-ab1. The stored-small copies carry the storage reduction.** Per seed s and size z with A's C2P control met:
ρ(s, z) = Δf(SbS_s, z) / Δf(A_s, z). **Supported** if ρ ≥ 1/2 on ≥ 4 of 5 seeds at both sizes. **Falsified** if
ρ ≤ 1/3 on ≥ 4 of 5 seeds at both sizes. "Uninformative" if A's control is met on ≤ 3 seeds at either size. Otherwise
"inconclusive, no claim". Printed: the C2P per-seed pass of SbS.

**H-ab1s. Stored-small copies alone suffice on the plain recipe.** AS read as an X of C2P.3 against A at the same seed
(Δf(AS) ≤ Δf(A)/3, |Δm(AS)| ≤ Δm(A)/3, Δf(AS) ≤ +0.05, upper bound ≤ +0.08). **Supported** if AS passes on ≥ 4 of 5 at
both sizes; **falsified** if it passes on ≤ 1 seed at either size while A's control is met on ≥ 4 seeds at that size;
uninformative / inconclusive as C2P. Guard printed: AS's landmark_combined AUC minus A's.

**Seed-mean rule (decider for H-ab2, H-ab3, H-ab3s and the attribution table; review F4).** Over the n read seeds, the
mean paired rise and its Student-t 95% interval (t with n − 1 degrees of freedom; 2.776 for n = 5, 3.182 for n = 4).
**Supported** if the mean is ≥ +0.05 and the lower bound > 0. **Falsified** ("a rise of +0.05 is excluded") if the
upper bound is < +0.05. Otherwise "inconclusive, no claim". The per-seed rule of the first draft (rise ≥ +0.05 on
≥ 4 of 5 seeds supports, ≤ +0.01 on ≥ 4 of 5 falsifies) is printed beside it as a secondary verdict.

**H-ab2. The warp-only images carry the warp reduction.** Rise of SbZ in warp-only placement, seed-mean rule.

**H-ab3. The native halves carry the softness reduction (given their stored copies).** Rise of SbH in Δsoft, seed-mean
rule. "Falsified" reads "the native halves are not needed for it, given the stored copies". The competing attribution
is read with the same rule on SbS (**H-ab3s**: the stored-small copies carry the development storage rise; it overlaps
H-ab1, which reads the same operation on unseen FFHQ persons).

**H-ab4. The matched splice negatives carry the seam and same-person reduction.** The registered Sp predictions
applied at 408-412 against Sb at the same seed: (1) Sp's development S0 placement ≥ max(2 · Sb, Sb + 0.10); (2) Sp's
raw development S0-vs-S4 AUC at least 0.05 below Sb's. **Supported** if both hold on ≥ 4 of 5 seeds; **falsified** if
neither holds on ≥ 4 of 5 seeds. Printed: S3 rise.

**Attribution table (secondary, same rule everywhere, printed for completeness).** For each omission arm X ∈ {SbZ,
SbH, SbS, Sp} and each read r ∈ {C2P Δf at fm61, C2P Δf at amsl112, warp-only placement, Δsoft, S3 placement, S0
placement}, by the seed-mean rule: "removing it brings the reaction back" if supported; "not needed for it, given the
others" if falsified; otherwise "inconclusive". 24 cells; the four primary cells are those of H-ab1
(by its own ratio rule), H-ab2, H-ab3, H-ab4; the others are labelled secondary, with no multiplicity correction and
no claim beyond the cell. Printed beside every arm: landmark_combined AUC and its difference from Sb (cost of the
omission), the camera-photo flag rate, halves placement, and the per-seed values.

Noise level, stated: on 100 images a difference of two placement shares has a binomial SD of up to about 0.07; on the
371 warp-only and 452 softened images about 0.035; training-seed noise comes on top (the SE1 review measured about 0.04
AUC between arms in same-seed differences), so "falsified" is reachable only for effects near zero and "inconclusive"
is a likely outcome for mid-rate reads. The +0.05 bars on single 100-image pools are not primary reads (S0 uses the
registered Sp rule).

## 6. Conditional arm: Sb trained twice as long (SbL)

Prepared, NOT submitted. It is submitted only if the lead tells the owner that the training-row read (owner PR1, part
Z1) shows underfit; otherwise it is reported as "not run (condition not met)". Arm SbL = `train_Sb.csv`, 12,500
steps (the only change; `run.sh` arm SbL), seeds 408-412, WCSS H100, `src/AB1/wcss/ab1_long.sbatch` (array 0-4,
4-hour limit), compared with AB1's Sb at the same seed. Hypothesis (strategist item 4): **supported** if SbL lowers
development S3 placement by ≥ 0.10 AND raises landmark_combined AUC by ≥ +0.02 on ≥ 4 of 5 seeds; **falsified** if
the S3 change is < 0.03 in absolute value and the AUC change is < +0.01 on ≥ 4 of 5 seeds; otherwise "inconclusive".
Printed only: "landmark_combined above 0.886 (the best single statistic on FS1's report) on ≥ 4 of 5 seeds"; C2P for
SbL by the C2P.3 rule against A as a guard. SbL is not a candidate.

## 7. Failures, deadline, read once

- Infrastructure failure: re-run once, unchanged, on H100. A non-finite run is never re-run. A lost arm-seed is
  reported "lost" and counts against the denominator as in FS1 v4.
- Read once, by `src/AB1/ab1_read.py --branch R` (committed with its sha256 before the first AB1 tar is fetched, tested
  on mock scores only, including a mock with two Sb seeds missing), when all 40 networks have ended (45 if SbL runs),
  or at 14 Nov 2026 12:00 CET with the networks present then, whichever comes first (review F5: no partial read at
  17:30; if all have ended by then the read is then). No network is read before that single read; no tar is read if the
  smoke job fails (the dispatcher cancels the array then).
- Provenance checked per tar before it is read (review F7): sha256, gpu.txt names an H100, task_info steps 6,250
  (12,500 for SbL) and limit 0, pack 96c31ae2…, overlay 171fdb21…, task.env arm, meta.json n_items equal to the arm's
  manifest rows and steps, finite loss values in train.log (SE1's regex), complete finite scores on every read row.
- Two verified copies of every tar before the read: WCSS Lustre `results/AB1` and
  `/mnt/t7/smad_next/AB1/results/` with sha256 checked against the job's own hash. Trained weights are kept.

## 8. Must not be claimed

- That any arm is a method, a candidate or "shortcut-free"; anything about benchmarks; generalisation beyond the
  OpenCV-style training engine and FRGC / colorFERET training hosts.
- An omission "causes" a reaction beyond what the paired within-seed rise shows; attribution under any rule other than
  section 5. "Removed" is never used; the reads say "reduced at the decision rule on development data".
- Any comparison of an AB1 (H100) number with an FS1 (A100) number as a measured difference.

## 9. Budget and timing

40 fits (about 1.2 H100-hours each with pack copy and scoring; limit 2:30) + smoke (about 0.3) ≈ 48 H100-hours, above
the 35-45 of the task because A and Sb are now fitted here; SbL 5 × 2.3 ≈ 12 more only if triggered (limit 4:00).
The smoke is job 6310091 (submitted 09:03, pending); the array goes into the dispatcher's queue at the registration
commit and runs beside the smoke (lead's order 09:05); its outputs count only if the smoke passes. Readings about 17:30
only if the WCSS controller starts the array by about 14:00 with about 20 GPUs.

## 10. Commands

```
# manifests and overlay (done 08:47; DGX CPU)
/home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/AB1/mk_ab1.py
# local code-path test (DGX, 20 steps, 8 rows): see README
# WCSS (via the dispatcher's queue if sbatch is refused)
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AB1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR ab1_smoke.sbatch
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AB1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR ab1_fit.sbatch   # 40 tasks
# read once
python3 -I /home/narolski/smad-next/src/AB1/ab1_read.py --branch R --out /home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication/ab1_read.json
```

## 11. Pins at the registration commit

| File | sha256 |
|---|---|
| src/AB1/run.sh (on WCSS as packs/AB1/run_v2.sh) | cfa4ed26d747e1d50f66cfc2af823ed55fd7f31634d6285cff9363a5fa796ab4 |
| src/AB1/wcss/ab1_fit.sbatch (40 tasks) | 186fd6bc259e2dec4f20a5b74a94da77e15bb4eafd91765d3a921d2fd12e3aa3 |
| src/AB1/wcss/ab1_long.sbatch (conditional SbL) | ad1c822e3942df6e0acc411f115aa8fb7b98461dc7ba8ad1f961da1928c8d693 |
| src/AB1/wcss/ab1_smoke.sbatch (job 6310091) | 7c6af62ee76b2ce17f524071e499763e1586757228dca170625b290febc0d6b8 |
| smoke's run.sh v1 (packs/AB1/run.sh; copy /mnt/t7/smad_next/AB1/run_v1_smoke_893e856a.sh) | 893e856abd6f3b692e6a4819917d0649209a0cae9e59e9953c06433963b4612c |
| overlay v2 / v1 (smoke) | 171fdb21… / 4e3afaa1… |
| src/AB1/mk_ab1.py, src/AB1/ab1_read.py, src/AB1/ab1_platform.py | in `pins.sha256` beside this file |

At the commit: no AB1 or SE1 network at seeds 408-412 exists; the FS1 C2P read (`c2p_read.json`) does not exist; the
Sp 403-405 read does not exist (no Sp read file in PN1's folder). The FS1 contrast 1 and storage numbers quoted in
section 0 were known.

## 12. Pre-run review fixes (`PRERUN_AB1_20261113.md`)

F1 own A and Sb on H100 (section 3; reader branch R only reads AB1 tars). F2 SbH keeps af0_half61; Δsoft renamed and
its overlap stated. F3 seed counting in the reader. F4 seed-mean decider. F5 single read time kept, no 17:30 partial
read. F6 volume wording. F7 provenance checks. F8 pins hard-coded in the job files. F9 training-row assertions. F10
disclosures (section 11); the stale run.sh pin in SE1's README is SE1's to fix (told via the dispatcher). Not taken up:
SbHS and the random-drop control (improvements 4-5; they need lead approval and about 6 H100-hours each).

## Amendment 1 (`date`: Fri Nov 13 09:36 CET 2026; before any AB1 tar exists or is read; lead's instruction after review `experiments/reviews/REVIEW_PN1_C2P_20261113.md`, findings F7 and Q5)

- The fresh-seed storage test (C2P on seeds 403-407) came out "uninformative" at its platform gate (scored on an L40S,
  trained on an A100 PCIe), so there is no earlier pass to replicate. R1's labels change from "replicated / not
  replicated" to **"first test at seeds 408-412: passed / not passed / uninformative"** (C2P "passes" / "fails" /
  "uninformative"; "inconclusive, no claim" and "not read (too few seeds)" unchanged). The rule itself is unchanged.
  Question 1 of section 1 reads accordingly: "does contrast 2-prime pass on seeds 408-412 (first test), and does
  contrast 1 replicate?" R2 (contrast 1) keeps its labels: FS1 contrast 1 was read "replicated" on 5 of 5 seeds.
- Scoring, confirmed: every AB1 network is scored on all 21,277 rows of `ab1_eval.csv`, including the 1,480 hold-out
  rows (fam ms1ffhq), by the unchanged `pn1_score.py` inside its own fit job (`run.sh` step after training,
  `--limit 0`), with TF32 on (`pn1_score.py` lines 45-46), on the H100 and software build of that fit. The reader takes
  every statistic of a network from that network's single `scores_eval.npz`; no C2P statistic mixes scores from two
  jobs or platforms. The smoke's rescoring of FS1 Sb s403 is a separate measurement and enters no AB1 read.
- Reader `src/AB1/ab1_read.py` changed only in the R1 labels; new sha256
  `aacb11cdab662bb147a228195cdf6955bfa9f3b65656e90ecf9f3179c447e9e2` (replaces the line in `pins.sha256`).

## Note (`date`: Fri Nov 13 10:10 CET 2026): the Sp 403-405 read was performed after this registration

Section 11 states that the Sp 403-405 read did not exist at the registration commit (61f7994). On the lead's
instruction the AB1 owner performed it afterwards, at 10:08, under its own earlier registration (PN1 "Registration Sp",
1b8fe48; reader sp_read.py 3ff01108…), on A100 PCIe networks; result in PN1 `result.md`. H-ab4 of AB1 (the same
predictions at seeds 408-412 on H100) is unchanged; its rules were fixed before that read.

## Amendment 2 (`date`: Fri Nov 13 10:40 CET 2026; before any AB1 tar exists or is read; lead's instruction after the results review of the Sp 403-405 read, `experiments/PN1_protocol-network-first-tests/REVIEW_PN1_SP_20261113.md`)

**Disclosure.** All directions below were **set after seeing seeds 403-405** of Sp, Sb and B (A100 PCIe, PN1 result.md
"Ablation arm without matched splice negatives (Sp), seeds 403-405"). Seeds 408-412 on WCSS H100 are new networks on
another platform; these are confirmatory tests of those directions on them. Arms, fits and every earlier rule are
unchanged.

Seed counting as section 5 (Sp and Sb at the same seed both read; n = 5: 4 of 5; n = 4: 4 of 4; n ≤ 3: "not read
(too few seeds)"). For each test: **supported** if the direction holds on ≥ 4 of 5 seeds (4 of 4 when n = 4);
**falsified** if it holds on ≤ 1 seed (≤ 1 of 4 when n = 4, as R2 contrast 1); otherwise "inconclusive, no claim".
Development data only, labelled post hoc in origin. Four post hoc tests plus H-ab4, no multiplicity correction. The two
tests without a margin (H-sp2, H-sp3b) reach "supported", and equally "falsified", with probability 6/32 = 0.19 under a
coin-flip null: weak evidence; the margin tests (H-sp1, H-sp3) are stricter. Per-seed Sp − Sb values are printed for
all four, with Sp − Sb native FFHQ and camera-photo flag rates beside H-sp1 and H-sp3.

- **H-sp1 (cost of fitting same-person against two-person splices).** Sp − Sb landmark_combined AUC ≥ +0.03.
  Supported: removing the matched splice negatives buys landmark_combined detection on new seeds; the Sb recipe trades
  detection for the matched-negative constraint, and that trade is reported (development landmark_combined only; Sp's
  native-genuine flag rate is printed beside it). Falsified: a gain of +0.03 did not recur at 408-412 (H100); the
  403-405 gains are not confirmed (seed noise and platform cannot be separated).
- **H-sp2 (matched splice negatives and the storage reaction).** Sp's C2P Δf at amsl112 (112.7 px, FFHQ hold-out) above
  Sb's (strictly greater). "Uninformative" if A's C2P control at amsl112 is met on ≤ 3 seeds. Supported: Sb's Δf at
  amsl112 is below Sp's on ≥ 4 of 5 seeds (direction only, no size claimed), consistent with the S0 + S3 negatives
  together reducing the storage reaction at an untrained size. Falsified: no reduction by the S0 + S3 negatives was
  detected at amsl112.
- **H-sp3 (same-person splices).** Sp's development S3 placement ≥ Sb's + 0.20. **H-sp3b, threshold-free companion (the
  review's qualification):** Sp's development S3-vs-S4 AUC below Sb's (S4 100 against S3 100). Supported (both): Sb's
  lower S3 flagging is more than a threshold shift; the matched negatives change how same-person splices are ranked
  against two-person splices. H-sp3 supported with H-sp3b falsified: the difference is mainly operating point (Sp also
  flags more genuine photos). H-sp3b supported with H-sp3 not supported: ranking changes without a 0.20 flag rise;
  reported as is. H-sp3b inconclusive: undetermined. H-sp3 falsified: no S3 rise of 0.20 on new seeds. The H-sp3b
  statistic was first computed by the results reviewer on 403-405. Margins on 100-image pools are compared as integer
  counts (inclusive, as section 5 requires). Part of any S3 rise is built
  in (Sp never sees S3 negatives); S0 and S3 were removed together, so no S0-against-S3 attribution is possible.
- **H-ab4 is unchanged.** The review's note is recorded: it is expected to be falsified for floor and ceiling reasons
  (S0 at the floor in every arm including B, S0-vs-S4 AUC near the ceiling, a 3-statistic floor at 0.90 on these hosts);
  if so, it says only that Sp did not learn an S0-type seam cue.
- Not registered (need the author): arms separating seam-only (S0) from same-person (S3) negatives.
- Reader: `src/AB1/ab1_read.py` adds `S3_vs_S4_auc` per network and the four rules (`H_sp1_lcomb`,
  `H_sp2_storage_amsl112`, `H_sp3_S3_flags`, `H_sp3b_S3_vs_S4_auc`); sha256 in `pins.sha256` at this commit; mock-tested.
- Pre-run check: `PRERUN_AB1_AMEND2_20261113.md` beside this file (GO WITH FIXES; F1-F6 applied).
- Correction to the reader's H-ab4 code, not to its rule (check F1): prediction 1 (S0 counts) and prediction 2 (AUC in
  exact half-pair units) are now compared as integers, so the registered margins are inclusive at full precision as
  section 5 states; with float sums an exact +0.10 or −0.05 could have been missed. The H-ab4 text is unchanged.
  Date of the change: 13 Nov 2026, 10:50-10:55 CET, before any AB1 tar exists; kept on the lead's ruling (10:58).
  Reader sha256 before (amendment 1): `aacb11cdab662bb147a228195cdf6955bfa9f3b65656e90ecf9f3179c447e9e2`; after (this
  amendment, H-sp rules and the H-ab4 integer comparison): `fb990bb50c10181d15fed943520a856aa96ed2e0747f00709b9daed9aabe42fd`.

## Deviation D1 (`date`: Fri Nov 13 14:30 CET 2026): reader crash on the first run, fixed before any statistic was computed

The first run of `ab1_read.py --branch R` (fb990bb5, 14:26) stopped with a KeyError while loading the first tar's
training scores: `scores_train.npz` holds `path, logit, label, kind, manifest_sha256`, not `id` (the mock never loaded a
training-score file). The crash came in the loading loop, before any statistic, verdict or printed value was computed
or shown; nothing was written. Fix (code only, rules unchanged): training flags per row kind are taken from the file's
`kind` field; and, using the files' own `manifest_sha256` fields, the reader now also checks that each network was
scored on ab1_eval.csv (93a5ba23…) and trained on its arm's manifest. Reader sha256 fb990bb5… → 74ecdf7a…. The read is
then run once (14:29). Record gaps noted by the results review: the mock never loaded a scores_train.npz, which is why
the crash was not caught; the fixed reader 74ecdf7a was pinned and committed with the result (8109cad, 14:31), after
the run, not before it. The reviewer checked the diff (loading and provenance checks only) and recomputed every number
independently with equal results.

## Note 2 (`date`: Fri Nov 13 15:00 CET 2026; registered before computing; zero GPU, post hoc, decides nothing): sharpness of persons whose flag flips under storage

For A, AS and SbS at each seed and size (fm61, amsl112), on the FFHQ hold-out pairs: share of the net flag increase
(persons ≤ 0 → > 0 minus > 0 → ≤ 0) coming from the top quartile of lapvar_face over the 300 native photos (the C2P
H-new-2 edge and file `c2p_holdout.npz` 4a9da201…; undefined if the net increase is ≤ 0); "enriched" if ≥ 0.50 on ≥ 4 of
5 seeds at both sizes, "not enriched" if ≤ 0.35 on ≥ 4 of 5 at both sizes, otherwise "inconclusive"; per arm; code
`src/AB1/ab1_sharp.py`, scores from the AB1 tars only.

## Amendment 3 (`date`: Fri Nov 13 20:22 CET 2026; POST HOC; before the lcomb_bal row list exists; zero GPU): landmark_combined at matched history

Lead's instruction after the review of the adversary's stage-1a floors (`experiments/reviews/REVIEW_ADV_STAGE1A_20261113.md`,
6f7c181): FFHQ landmark_combined is separable at 0.96-0.98 by statistics fitted on it and at about 0.79 from the image
surround alone (a resampling-history difference between morphs and genuine photos), so R2's gain (Sb − B +0.15 to
+0.21, Sb − A +0.12 to +0.14 at 408-412, known) is untested at matched history. The adversary is building
`lcomb_bal` (matched on the surround-only score and pre-alignment eye distance, existing images only, published with
pins in experiments/ADV_shortcut-floors/). **Disclosure:** registered after seeing every AB1 landmark_combined number on
all 3,000 rows; no network's score on any history-balanced subset or surround stratum has been computed by anyone.

- **H-hb1 (the review's H-new-2): "Sb's gain over B shrinks by at least half on the history-balanced subset."** Per seed
  (408-412, AB1's H100 fit-job scores, the same rows for every network, paired): g_full = AUC(Sb) − AUC(B) on the 3,000
  rows; g_bal = the same on lcomb_bal. **Supported** if g_bal ≤ ½ × g_full on ≥ 4 of 5 seeds. **Falsified** if g_bal ≥
  +0.10 on ≥ 4 of 5 seeds. Otherwise "inconclusive, no claim"; ≤ 3 read seeds "not read". Sb − A by the same rule,
  secondary. Unweighted read (any weight column is ignored); if the adversary publishes only weights and no 1:1
  subset, this read is "not read" until a registered amendment says how to use them.
- **Printed:** per-network AUC on lcomb_bal (A, B, Sb) with 95% intervals (2,000 bootstraps of images within class, rng
  20261116); paired Sb − B and Sb − A on lcomb_bal with intervals from the same draws; the same three differences
  within quintiles of the adversary's surround-only held-out score (edges over all 3,000 rows); Sb's AUC on lcomb_bal
  beside the adversary's same-data shortcut learner on lcomb_bal (when published).
- **Inputs, asserted by the reader:** the lcomb_bal list and the surround-score file must be committed in git, unmodified,
  with the sha256 given in the adversary's commit; ids must be landmark_combined rows of ab1_eval.csv.
- **Follow-up arms:** the SbFM and Sbx reads print the arm's AUC on lcomb_bal and arm − Sb there, beside
  landmark_combined (`--arm` option of the same reader; printed only, their registered verdicts unchanged).
- Reader `src/AB1/ab1_hb_read.py` (de6e61ae…), mock-tested (`ab1_hb_read_mock.json`); read once when the adversary
  posts the lcomb_bal commit; then the results-reviewer. Pre-run check: requested from the lead.

## Amendment 3b (`date`: Fri Nov 13 20:28 CET 2026; before the lcomb_bal commit exists; fixes of the pre-run check `experiments/reviews/PRERUN_AB1_A3_20261113.md`, 3a5d712, GO WITH FIXES)

**Disclosure.** While implementing these fixes the owner looked at the adversary's **uncommitted** build files in
experiments/ADV_shortcut-floors/floors/ for their structure: `lcomb_bal_build.json` (converged true, 125 morphs and 125
genuine) and the column names of `lcomb_bal_rows.csv`, `lcomb_regional_heldout.csv` and `lcomb_bal_regional.json`. No
network score on any subset was computed or seen. Under the rule below a committed subset of that size would be
"not read".

1. **Exclusive per-seed rule (F1).** Per seed: *shrinks* if g_full > 0 and g_bal ≤ ½·g_full; *stays* if g_bal ≥ +0.10
   and g_bal > ½·g_full; a seed with g_full ≤ 0 counts as neither. Supported if ≥ 4 of 5 seeds shrink; falsified if ≥ 4
   of 5 stay; otherwise inconclusive; ≤ 3 read seeds "not read". Sb − A secondary, same rule.
2. **Minimum size and subset noise (F2; lead's answer).** **Not read if lcomb_bal has fewer than 150 morphs or fewer than
   150 genuine photos;** nothing is loosened afterwards. All five seeds share one subset, so the seed vote does not
   average subset noise. Printed, not binding: the seed-mean g_bal with a joint row bootstrap (the same draws for all
   seeds; 500 of the registered 2,000 draws), and a null from 2,000 random class-balanced subsets of the same sizes
   (rng 20261117) with the percentile of each seed's g_bal and of the seed mean.
3. **Convergence and blend signal (F3).** The reader asserts that `floors/lcomb_bal_build.json` is committed and pinned
   with converged = true and n_morph = n_genuine equal to the rows file's counts; otherwise "not read". It prints the
   adversary's face-region floor on lcomb_bal (`floors/lcomb_bal_regional.json`, face_floor); if that floor is below
   0.80, a supported outcome reads "gain lost on the subset, not attributable to history alone".
4. **Printed (F4):** the covariate table for retained against dropped rows within each class (pre_ied, pre_w,
   pre_png_bytes, border_frac, scale, aligned_png_bytes from `ffhqm_meta.csv`; nu_gbt from `lcomb_heldout.csv`;
   face_logreg and surround_logreg from `lcomb_regional_heldout.csv`); each network's AUC decomposed as retained
   morphs against all genuine and all morphs against retained genuine; the gain on the probit scale √2·Φ⁻¹(AUC).
5. **Quintiles (F5):** no difference is printed for a quintile with fewer than 20 morphs or 20 genuine photos.
6. **Fixed inputs (F6):** surround score = `experiments/ADV_shortcut-floors/floors/lcomb_regional_heldout.csv`, column
   `surround_logreg` (round 0, all 3,000 rows). The reader asserts that `src/adversary/balance.py` is committed with
   the sha256 given in the adversary's amendment, in a commit no later than the commit that adds the rows file, and that
   every input file is tracked, unmodified and at the stated sha256.
7. **Intervals (F8):** all intervals are conditional on the chosen subset and leave out the uncertainty of the matching.

**What each outcome licenses** (development data, post hoc; the reviewer's text):
- **Supported** (with item 3 satisfied): "On a history-balanced development subset, most of the candidate's
  landmark_combined gain disappears." The +0.12 to +0.21 figure is then not presented as evidence of better morph
  detection.
- **Falsified:** "The gain stays ≥ 0.10 on a history-balanced development subset (post hoc)." It does not say "not
  history": the matching balanced only surround statistics.
- **Inconclusive or not read:** keep the review's qualifier unchanged ("on a development set whose surround carries a
  kernel-history cue (0.79) and which in-distribution shortcut models separate at 0.96-0.98; whether the gain holds at
  matched history is untested").
- Never worded as held-out or test evidence.
- Reader `src/AB1/ab1_hb_read.py` after these fixes: sha256 `2ff58b5b8201a273d33f9c73a656b394dd2e72add6f05538c2a340739cb35df6` (replaces de6e61ae… in the pins files); mock-tested (`ab1_hb_read_mock.json`).

## Amendment 3c (`date`: Fri Nov 13 20:32 CET 2026; POST HOC; before any weights exist; lead's ruling): H-hb1 with inverse-probability weights

**Disclosure.** Written after the owner had seen the size of the adversary's uncommitted 1:1 subset (125 morphs, 125
genuine; amendment 3b) but no network score on it or on any subset. Lead's ruling: on that subset H-hb1 is "not read"
(amendment 3b, item 2) and stays so; when the adversary commits it, `ab1_hb_read.py` is run once so that the
"not read" status and the descriptive prints (covariate table, random-subset null, seed-mean with joint bootstrap) are
on record, labelled descriptive, no verdict.

**H-hb1w (weighted).** Same exclusive rule as amendment 3b item 1, with g_bal replaced by the paired weighted gain g_w =
weighted AUC(Sb) − weighted AUC(B), using inverse-probability weights over all 3,000 landmark_combined rows that the
adversary will publish (from the round-0 surround-only score plus pre_ied; stabilised and trimmed by the adversary;
committed and pinned). Weighted AUC = Σ_i Σ_j w_i w_j ([s_i > s_j] + ½[s_i = s_j]) / (Σ w_pos Σ w_neg). g_full stays the
unweighted 3,000-row gain. Sb − A secondary.
- **Usable only if** the effective sample size (Σw)²/Σw² is ≥ 300 in each class AND the weighted AUC of the round-0
  held-out surround-only scores (`lcomb_regional_heldout.csv`, surround_logreg and surround_gbt, folded) is ≤ 0.60 for
  both models; otherwise "not read". Computed by the reader from the published weights.
- **Guard:** if the weighted face-region floor (max of face_logreg and face_gbt, weighted, folded) is below 0.80, a
  supported outcome reads "gain lost under weighting, not attributable to history alone".
- **Printed:** weighted AUC per arm and seed with a weighted row bootstrap (2,000 draws of rows within class with
  replacement, weights kept, rng 20261119, the same draws for all arms and seeds); paired weighted gain with its
  interval; a null from 2,000 random re-assignments of the weights within class (rng 20261117) with the percentile of
  each seed's g_w and of the seed mean; the probit-scale gain √2·Φ⁻¹(AUC), unweighted and weighted. Intervals are
  conditional on the weights.
- **What each outcome licenses:** as amendment 3b, with "under history weighting" in place of "on a history-balanced
  subset". Never held-out or test evidence.
- Reader `src/AB1/ab1_hbw_read.py` (2cffd88b…); weighted AUC checked against brute force and,
  with unit weights, against c2p_read.fauc; mock-tested (`ab1_hbw_read_mock.json`). Pre-run check: requested from the
  lead. Read once when the adversary commits the weights.
