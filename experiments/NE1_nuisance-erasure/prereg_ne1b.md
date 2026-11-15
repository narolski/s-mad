# NE1b: splice feature ceiling and rank-7 border erasers on the saved NE1 features: registration

Owner: TT1/NE1 owner, on the lead's assignment (13 Nov 2026). It follows the NE1 result 41df045 and its review 78f0ca1
(`experiments/reviews/REVIEW_NE1_20261113.md`, hypotheses H-new-3 and H-new-1).

Status: draft 65f13a4 → pre-run check GO WITH FIXES (`experiments/reviews/PRERUN_NE1B_20261113.md`, b8288e3); fixes
1-7 applied, and the lead's answers (component cross-fitting; DATA audit 1b05940). **registered** (this commit). At
this commit no NE1b quantity has been computed on real features.

Scope:
- CPU only, development rows only, on the saved NE1 features (`NE1_feats.tar` `18d13b10…`, gate byte-identical on
  5/5).
- The frozen networks (Sb seeds 403-407, frozen by author ruling) and the sealed read are untouched.
- H-new-2 and H-new-4 wait.
- **Storage is dropped from NE1b**: no storage quantity is read.

**Known before the read (stated up front, pre-run fix 2 and improvement 3).**
- NE1's H1d, a linear head fitted on L's development hosts with S3 = 0 and S4 = 1 among its rows, already has an
  S4-vs-S3 AUC within 0.011 of H0 on 5 of 5 seeds (result.md).
- NE1's border direction overlaps the frozen head: cos(d3, w) = 0.29-0.52 (post hoc).
- Both make "low ceiling" in Part A and "removed with cost" in Part B the expected outcomes. A result in that direction
  is not a surprise.
- NE1b is designed after the NE1 numbers.

**Answer to the reviewer's question 1 (checked by the owner from `AR1/pool.csv` and `ne1_train.csv`).**
- 32 of the 156 training-list ladder hosts have an L host as their two-person partner.
- None of these 32 contributes a row that uses the partner photo: their training kinds are lad_R0, lad_R2w, lad_S0
  and lad_S3, which are single-identity rows.
- None of the 124 training hosts with partner-photo rows (lad_S4, lad_R4, lad_half) has an L host as partner.
- No L host has a training host as partner.
- The source images (H, S, B, R) of the training ladder rows and of the L hosts share 0 files (312 against 949).
- So the training-list probe `lin_T` is person- and image-clean against L. The data owner's audit
  (`experiments/DATA_builds/PARTNER_OVERLAP_AUDIT.md`, 1b05940) confirms this for every training list: 0 shared hosts,
  partners or source photos with any evaluation set. It also confirms the development-against-test sharing (99/99; 80
  clean test hosts).

## A. Splice feature ceiling (H-new-3)

**Question.** Does a head fitted on held-out development persons separate two-person (S4) from same-person (S3)
splices better than the frozen head?

**Binding split (pre-run fix 1; lead's answer 2).**
- 5-fold cross-fitting over the connected components of the person graph: all 291 L hosts, with host-partner edges
  from `AR1/pool.csv`. Partners outside the 291 are graph nodes, as in TB1 amendment 2.
- **Why there is no giant component here.** The audit's person graph (142 components, the largest 432 persons) uses
  every pool and training row. Part A uses only L rows, whose persons are each L host and its partner. So the graph
  that decides leakage between Part A's fit and read rows has only host-partner edges of the 291 L hosts. It has 110
  components, and the largest holds 10 L hosts. Rows outside L (training, other pools) are never fitted or read in
  Part A, except `lin_T`, which the audit shows is clean.
- Components are assigned to folds by `default_rng(20261132).permutation(n_components) % 5`. That gives 55-65 read
  hosts per fold, printed.
- Printed beside the binding read: the read without the largest component, as the lead asked.
- The 80 clean test hosts are asserted equal to the audit's list
  (`/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv`).
- Every read is out of fold, so fit and read persons and images are disjoint (S4 uses the partner's S photo, which
  is why partners are linked).
- **Fit rows (per fold):** the training-fold hosts' S3, S3_bg, S3_face (label 0) and S4, S4_bg, S4_face (label 1),
  OpenCV.
- **Read rows:** the held-out fold's S4::opencv against S3::opencv.
- **H0** (the frozen head) is read on the same out-of-fold rows.

**Probes.**
- **Linear:** logistic, class-balanced. C from {0.01, 0.1, 1, 10} by inner 5-fold GroupKFold on components,
  maximising AUC; ties go to the smaller C.
- **Small MLP:** StandardScaler, then one hidden layer of 256 (ReLU), max_iter 2000, random_state 0. Alpha from
  {1e-3, 0.1, 1, 10} by the same inner CV; ties go to the larger alpha. It is scored with its pre-sigmoid output, so
  scores do not saturate.
- **Printed:**
  - a linear probe on core rows only (S3/S4 without the _bg/_face variants);
  - a learning curve: the linear probe at the chosen C on 25, 50, 75 and 100 training-fold hosts and on all of them
    (host order from the same rng);
  - a host-level label-permutation null: within each training-fold host, the S3 and S4 family labels are swapped with
    probability 0.5, 20 draws;
  - the training-list probe `lin_T` (lad_S3 against lad_S4 of Sb's training rows, C = 1), read on all 291 hosts;
  - the 80 clean test hosts (partner not a development host and not a development host's partner) and the old
    191-host read, both with the probe fitted on the 100 development hosts.
- **Bootstrap:** over components, 2,000 draws, for the out-of-fold linear − H0 and MLP − H0 AUC (scores fixed).

| Result on ≥ 4 of 5 seeds (checked in order) | Reading | Licenses |
|---|---|---|
| the upper 95% bound of (linear − H0) ≤ +0.05 AND MLP ≤ H0 + 0.05 AND plateau (AUC at 100 hosts ≤ AUC at 50 hosts + 0.02, and AUC on all hosts ≤ AUC at 100 hosts + 0.02) AND lin_T ≤ H0 + 0.05 | low ceiling: a linear or small-MLP head fitted on these development hosts does not separate S4 from S3 better than the frozen head; this is evidence, not proof, that the features lack the distinction | no head-level route for splices is supported by NE1b |
| linear ≥ max(0.85, H0 + 0.10) | the head is the bottleneck; the distinction is linearly present | a targeted head refit may be registered as a post-freeze ablation only |
| linear ≤ H0 + 0.03 AND MLP ≥ H0 + 0.10 | present nonlinearly only | a nonlinear head may be registered as a post-freeze ablation only |
| otherwise | intermediate (probe above H0 but below the bottleneck bar) | nothing new licensed |

## B. Rank-7 border erasers (H-new-1)

**Question.** Does a rank ≤ 7 linear eraser remove the border dependence two-sidedly (toward zero, not past it), per
mask, without an in-domain detection cost?

**Fitting rows (half A, as NE1).** Half-A R_cam photos and their bordered copies (7 masks).

**Erasers.**
- **E7:** the span of the 7 per-mask mean differences (mean bordered copies of mask m − mean photos), orthonormalised
  by QR and projected out.
- **LEACE** (Belrose et al. 2023, closed form) on 8 classes (photo + 7 masks): r(x) = x − W⁺PW(x − μ), with W the
  inverse square root of the Ledoit-Wolf shrunk covariance (pre-run fix 6) and P the projection onto colspace(W Σ_XZ).
  Printed: condition number, eigenvalues kept, rank, and the residual class-mean spread on half B (before, after
  LEACE, after E7).
- **E7c (ceiling, pre-run fix 3a):** E7 fitted on half B, i.e. on the rows it is read on.
- **E1:** the NE1 rank-1 direction, printed for reference.

**Heads.**
- The refit is binding: H1 refit on erased T (C = 1, class-balanced), compared with H1.
- The frozen head on erased features (H0's w, b, compared with H0) is printed.

**Nulls** (`default_rng(20261130)`, one stream over networks in seed order; the feature dimension is taken from the
data).
- **Isotropic:** 20 uniform random rank-7 subspaces, each followed by the H1 refit. They are the cost reference
  (below). Their two-sided pass count is printed.
- **Covariance:** 20 rank-7 subspaces drawn from N(0, Cov(T)). Printed only; NE1 showed this null erases the detection
  axis.
- **Head-matched (pre-run fix 3c):** 20 random rank-7 subspaces whose projection of ŵ has E7's norm. Printed only.

**Reads (half-B persons, 1,435 copy-photo pairs, 202 hosts; host means, then mean over hosts).**
- Logits: paired Δlogit, copy − own photo. Pooled and per mask.
- Flags: paired excess flag, copy flagged − photo flagged, at each head's own 99th-percentile cut of its camera-pool
  scores (P = R_cam ∪ L ladder R0, 1,290 rows). Pooled and per mask.
- Ranks: the NE1 paired rank shift in P.
- Removal(unit) = 1 − value(head)/value(reference).
- **In-domain detection (binding, pre-run fixes 4 and 7):** L test hosts of half B only.
  - Recall of ladder R4 morphs (OpenCV and FaceMorpher, native strength) at each head's own 99th-percentile camera
    cut.
  - R4-vs-R0 AUC.
- **Printed only:** FFHQ landmark_combined recall at the same cut and its AUC. Shortcut cues alone separate this set at
  0.964, and it is cross-domain for refitted heads.

**Per-seed conditions (eraser e, refit head against H1).**
- **two-sided:** |1 − removal| ≤ 0.3 in logits AND in flags AND in ranks.
- **per mask:** |Δlogit_m| ≤ 0.3 × |pooled Δlogit of H1| on at least 6 of the 7 masks.
- **removed** = two-sided AND per mask.
- **no cost:**
  - the R4 recall loss is ≤ the tolerance, where tolerance = max(0.02, the largest R4 recall loss among the 20
    isotropic nulls on that seed), pre-run fix 3b;
  - AND the R4-vs-R0 AUC loss is ≤ 0.01.
- **clean** = removed AND no cost.
- **floor:** H1's pooled Δlogit ≤ 0.05 or excess flags ≤ 0.01. A floor seed is excluded; with fewer than 4 non-floor
  seeds the row reads "floor".

| Result (checked in order; ≥ 4 non-floor seeds) | Reading | Licenses |
|---|---|---|
| E7c is clean on fewer than 4 seeds | criteria unreachable (inconclusive by design) | nothing |
| clean for E7 or for LEACE (named) | a post-hoc linear eraser removes the border response on frozen features | a training-time debiasing arm may be registered as a post-freeze ablation beside Sbx (author approval; the result does not predict that adversarial training succeeds) |
| removed but not no cost, for E7 or LEACE | removable only at a detection cost: border and detection share features | no debiasing arm licensed |
| not two-sided in logits or flags, for both E7 and LEACE | not removable two-sidedly by a rank ≤ 7 linear eraser | no debiasing arm licensed by NE1b |
| otherwise | inconclusive (border) | nothing |

Notes on the rules:
- Testing two erasers is a two-way choice, stated here.
- E7 and LEACE zero the half-A per-mask mean differences by construction, so the informative tests are the flags, the
  ranks, transfer to half B, and cost.
- Point values are used. The bootstrap intervals (P hosts, 2,000 draws, `default_rng(20261131)`, cut recomputed) of
  the logit and flag removal for E7 and LEACE are printed.

## C. Code and run

- `src/NE1/ne1b.py` (sha256 below) imports the registered NE1 reader `ne1_heads.py` (`5c6fdcd2…`) for load, the half
  split, AUC and ranks. Inputs: `/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats/` (verified tar), the NE1
  manifests and `/mnt/t7/smad_next/AR1/pool.csv`.
- **Tests (code only):**
  - a `--mock` run on one network (random unit features with the real manifests; every read computed);
  - every branch of both outcome tables exercised with synthetic values (again after the fixes);
  - the revised mock takes about 6 min per network (the MLP alpha grid);
  - LEACE checked on synthetic data (class means equal after erasure, rank 7);
  - the span eraser is idempotent.
- **Run:** once, on the DGX CPU (thread caps 2, nice 10), sklearn 1.9.0, then the results-reviewer pass.

| File | sha256 |
|---|---|
| `src/NE1/ne1b.py` | `9b78d588d29dcb0a…` |
| `src/NE1/ne1_heads.py` (imported) | `5c6fdcd2173d7fb9…` |
| `/mnt/t7/smad_next/AR1/pool.csv` | `861019781e79159f…` |
| `/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv` | `814c44861d706553…` |
