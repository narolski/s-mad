# NE1b: splice feature ceiling and rank-7 border erasers on the saved NE1 features: registration draft

Owner: TT1/NE1 owner, on the lead's assignment (13 Nov 2026, after the NE1 result 41df045 and its review 78f0ca1,
`experiments/reviews/REVIEW_NE1_20261113.md`, hypotheses H-new-3 and H-new-1). Status: draft for the pre-run check.
It is registered at the git commit that changes this status line. At this commit no NE1b quantity has been computed
on real features. The NE1 numbers in result.md are known; NE1b is designed after them. CPU only, development rows only,
on the saved NE1 features (`NE1_feats.tar` `18d13b10…`, gate byte-identical on 5/5). The frozen networks and the
sealed read are untouched. H-new-2 and H-new-4 wait. **Storage is dropped from NE1b**: no storage quantity is read.

## A. Splice feature ceiling (H-new-3)

**Question.** Is the same-person (S3) against two-person (S4) splice distinction present in the frozen features at
all, on held-out persons?

- **Fit rows.** The development hosts of L (100 hosts): S3, S3_bg, S3_face (label 0) and S4, S4_bg, S4_face (label 1),
  OpenCV, 600 rows.
- **Read rows.** The test hosts of L (191 hosts), S4::opencv against S3::opencv (the same rows as H0's S4-vs-S3 AUC
  in NE1). AUC over the three variant pairs is printed.
- **Probes.**
  - Linear: logistic, class-balanced, C from {0.01, 0.1, 1, 10} by 5-fold GroupKFold on hosts, maximising AUC; ties
    go to the smaller C.
  - Nonlinear (small): sklearn MLPClassifier, one hidden layer of 256, alpha 1e-3, max_iter 2000, random_state 0.
  - Printed: a linear probe fitted on Sb's own training rows lad_S3 against lad_S4.
- **Reference.** H0 (the frozen head) AUC on the same read rows.
- **Bootstrap.** Test hosts, 2,000 draws, `default_rng(20261131)`; probe − H0 AUC intervals (probes fixed).

| Result on ≥ 4 of 5 seeds | Reading | Licenses |
|---|---|---|
| linear probe ≤ H0 + 0.03 AND MLP ≤ H0 + 0.05 | low ceiling: the frozen features lack a usable same-person vs two-person distinction | no head-level method (refit, reweighting, group DRO, JTT) can supply it; the second-identity route needs a new signal or backbone training |
| linear probe ≥ max(0.85, H0 + 0.10) | the head is the bottleneck; the distinction is linearly present | a targeted head refit for splices may be registered (not group DRO) |
| linear ≤ H0 + 0.03 AND MLP ≥ H0 + 0.10 | present nonlinearly only | a nonlinear head may be registered |
| otherwise | intermediate (above H0, below the bar) | nothing new licensed |

The rows are checked in the order listed.

## B. Rank-7 border erasers (H-new-1)

**Question.** Does a rank ≤ 7 linear eraser remove the border dependence two-sidedly (toward zero, not past it), per
mask, without the 0.03-0.09 recall loss the rank-1 eraser showed?

- **Fitting rows (half A, as NE1).** Half-A R_cam photos and their bordered copies (7 masks).
- **Erasers.**
  - E7: the span of the 7 per-mask mean differences (mean bordered copies of mask m − mean photos), orthonormalised by
    QR and projected out.
  - LEACE (Belrose et al. 2023, closed form) on 8 classes (photo + 7 masks): r(x) = x − W⁺PW(x − μ), W = Σ^{-1/2}
    (eigenvalues below 1e-8·max dropped), P = projection onto colspace(W Σ_XZ).
  - E1: the NE1 rank-1 direction, printed for reference.
- **Heads per eraser.** The refit (H1 refit on erased T, C = 1, class-balanced) is binding; the frozen head on erased
  features (H0's w, b) is printed. Reference heads: H1 for the refit, H0 for the frozen head.
- **Nulls (rng `default_rng(20261130)`, one stream over networks in seed order).**
  - Isotropic: 20 uniform random rank-7 subspaces (QR of 512×7 Gaussian), each followed by the H1 refit. This null is
    binding.
  - Covariance: 20 rank-7 subspaces drawn from N(0, Cov(T)), each followed by the H1 refit. Printed only; NE1 showed it
    erases the detection axis.
- **Reads (half-B persons, 1,435 copy-photo pairs, 202 hosts; host means, then mean over hosts).**
  - Logits: paired Δlogit, copy − own photo. Pooled and per mask.
  - Flags: paired excess flag, copy flagged − photo flagged, at each head's own 99th-percentile cut of its camera-pool
    scores (P = R_cam ∪ L ladder R0, 1,290 rows). Pooled and per mask.
  - Ranks: the NE1 paired rank shift in P.
  - Removal(unit) = 1 − value(head)/value(reference).
- **Detection, each head at its own 99th-percentile camera cut.**
  - Recall on FFHQ landmark_combined orig morphs (C; cross-domain).
  - Recall on L test-host ladder R4 morphs (OpenCV and FaceMorpher, native strength; in-domain, 382 rows).
  - AUC on C.

**Per-seed conditions (eraser e, refit head against H1).**
- **two-sided:** |1 − removal| ≤ 0.3 in logits AND in flags AND in ranks.
- **per mask:** |Δlogit_m| ≤ 0.3 × |pooled Δlogit of H1| on at least 6 of the 7 masks.
- **removed** = two-sided AND per mask.
- **no cost:** recall loss ≤ 0.02 on C AND on L R4, AND AUC loss on C ≤ 0.01.
- **null:** at most 1 of the 20 isotropic nulls is two-sided in both logits and flags.
- **clean** = removed AND no cost AND null.
- **floor:** H1's pooled Δlogit ≤ 0.05 or excess flags ≤ 0.01. A floor seed is excluded; with fewer than 4 non-floor
  seeds the row reads "floor".

| Result (checked in order; ≥ 4 non-floor seeds) | Reading | Licenses |
|---|---|---|
| clean for E7 or for LEACE (named) | clean two-sided removal without recall loss | a training-time debiasing arm (border-adversarial head or erasure layer) is worth H100 hours, read beside Sbx |
| removed but not no-cost, for E7 or LEACE | removable only at a detection cost: border and detection share features | no debiasing arm licensed |
| not two-sided in logits or flags, for both E7 and LEACE | not removable two-sidedly by a rank ≤ 7 linear eraser | no debiasing arm licensed by NE1b; data (Sbx) remains the route |
| otherwise | inconclusive (border) | nothing licensed |

Testing two erasers is a two-way choice, stated here. Point values are used; the bootstrap intervals (hosts, 2,000
draws, `default_rng(20261131)`) are printed: removal in logits and flags for E7 and LEACE (P hosts redrawn and cut
recomputed), and the C recall loss.

## C. Code and run

- `src/NE1/ne1b.py` (sha256 at registration below). It imports the registered NE1 reader `ne1_heads.py`
  (`5c6fdcd2…`) for load, half split, AUC and ranks.
- Inputs: `/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats/` (verified tar), manifests as in NE1.
- Tests: `--mock` on one network (random unit features with the real manifests; every read computed, 20 s with 50
  draws). Every branch of both outcome tables was exercised with synthetic values. The LEACE function was checked on
  synthetic data: class means equal after erasure (max spread 8e-15), rank 7. The span eraser is idempotent.
- Run once on the DGX CPU (thread caps 2, nice 10), sklearn 1.9.0. Then the results-reviewer pass.

| File | sha256 |
|---|---|
| `src/NE1/ne1b.py` | `1951737c2c908fb6…` |
| `src/NE1/ne1_heads.py` (imported) | `5c6fdcd2173d7fb9…` |
