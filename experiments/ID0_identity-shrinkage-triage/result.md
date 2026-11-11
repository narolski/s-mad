# Identity-shrinkage triage: how average is a morph, and what is the ceiling [ID0] — result

Owner run, 11 Nov 2026 (DRAFT while the feature arms run; landmark section final). Pre-registration:
`prereg.md` (written before any statistic). Code `src/ID0/`; features and logs `/mnt/t7/smad_next/ID0/`;
per-arm results `arm_<arm>.json` and `contrasts_<arm>.csv`; decision table `verdicts.json`; benchmark pair
similarity `bench_similarity.json`; fit and item counts `lists_summary.json`. AUC = area under the ROC curve with
the second-named group positive; [a, b] = 95% two-way person bootstrap (a41_read.Draw, B = 2,000).

## Fit set (genuine photos only)

776 FRGC + colorFERET persons (FERET 710, FRGC 66), 1,395 photos after AR1's duplicate rule (325 dropped); 471
persons with at least 2 photos (619 within-person degrees of freedom), only 47 with 2 or more capture sessions. 87
validation-reserved persons excluded by `is_val`. No AR1 host or partner, no FRLL person, no morph or render.
The within-person covariance is therefore mostly within-session (FERET fa/fb expression change, FRGC stills of one
day). 16 AR1 hosts drop out of every ID0 contrast because the host or the partner is an `is_val` person (8 hosts
are themselves `is_val`; fact reported to the lead, AR1 files not touched): AR1 contrasts use 520 hosts.

## Landmark-shape arm (exact shapes, pixel-blind) — final

Fit: k = 11 PCA components (96% of shape variance), d = 10 directions where persons differ more than sessions
(λ 15.2 … 1.23), session-to-identity ratio n = 0.175. Predicted AUC of a midpoint of two unrelated people against
one capture: 0.795 (closed form) / 0.781 (fitted spectrum) at c = 0; 0.707 / 0.689 at c = 0.3; 0.646 / 0.630 at
c = 0.5; 0.585 / 0.574 at c = 0.7. Genuine-only virtual check (descriptive, added after the prereg): held-out
single fit shapes against held-out exact midpoints of two fit persons, 0.834 (0.919 / 0.879 / 0.703 from the
lowest to the highest third of shape similarity).

Exact shapes on the AR1 primary pool (520 hosts), ISS score:

| Contrast | AUC [95%] | predicted (closed / spectrum) at the pairs' own c |
|---|---|---|
| R0 host shape vs R4 mean(host, partner) | **0.725 [0.689, 0.758]** | 0.687 / 0.669 (c median 0.37) |
| R3 = R2w shape mean(host, own 2nd photo) vs R4 | 0.687 [0.650, 0.720] | same |
| R3m mean(host, mirrored host) vs R4 | 0.651 [0.614, 0.687] | same |
| R0 vs R3 (same-person average) | 0.548 [0.536, 0.559] | — |
| R0 vs R3m | 0.572 [0.565, 0.581] | — |

Dose (1−m)·host + m·partner, all 520 hosts: Page L = 44,047, p = 4e-234; mean ISS rises at every step; AUC
against m = 0: 0.574 / 0.637 / 0.685 / 0.714 / 0.724 for m = 0.1 … 0.5.
FRLL AR1 pool (102, descriptive; partner shape is the smiling photo): R0 vs R4 0.797 [0.721, 0.869], R3 vs R4
0.754 [0.676, 0.831]; session read-out SES also separates (0.83), i.e. part of the FRLL separation is expression.
Benchmark pairs (exact mean of the two contributors' neutral FRLL shapes vs single FRLL shapes, descriptive):
FRLL-Morphs pairs 0.731–0.737 (all five families share almost the same pair list), corrected MAD22 pairs
0.736–0.758. Shrink law (Spearman of ISS with 2a(1−a)(1−cos_glint)): AR1 R4 +0.08 [−0.08, 0.24]; FRLL-Morphs
pairs −0.06 [−0.18, +0.06]: within morphs, the shape-shrinkage score does not follow FR dissimilarity.

Caveats: these are exact landmark files, not landmarks detected on a morph image; the pairs' own c (0.37 median,
10–90% range −0.16 to 1.18) is a noisy per-pair estimate that a pool offset from the fit mean inflates, so the
"predicted at own c" column is conservative; R0 vs R1 does not apply (no image).

## FR arm (glintr100) and GEO-0 reads

(pending)

## Feature arms: CLIP ViT-L/14, DINOv3 ViT-L/16, DiffAE z_sem

(pending)

## Predicted ceiling and the similarity range in benchmark pairs

Contributor similarity actually present (glintr100 cosine of the two contributors' FRLL photos, a46 gallery;
median [10%, 90%]): FRLL-Morphs 0.037 [−0.066, 0.144] (five families); corrected MAD22 0.114 [0.048, 0.188]
(all five families); published MorDIFF 0.114 [0.048, 0.188]; DiM-C / Greedy-DiM / Greedy-DiM-S 0.116 [0.053,
0.190]; AR1 pool (look-alike assignment) 0.234 [0.163, 0.310]; AR1 same-person 0.868 [0.804, 0.918].
FRLL-Morphs file names pair a person with themselves in 2–3 files per family in 4 of 5 families (061_061, 096_096,
036_036; not AMSL); they enter the similarity range as cosine 1.0.

(ceiling per arm pending)

## Falsifiers applied

(pending)

## What could not be verified, deviations, gaps

(pending)
