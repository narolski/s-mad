# FFHQ FaceMorpher two-person morph against matched warp-only image (XF1): result

Reviewed in `experiments/reviews/REVIEW_XF1_20261113.md` (ACCEPT WITH EDITS; the edits are applied in the text below).

## Scope
- XF1 is a post-freeze development diagnostic, registered after the sealed read (registration 01283b0, read 04e1417, Athena job 3553044).
- It uses development data only (FFHQ MS1 hold-out frames). FFHQ is never reported as a benchmark.
- It cannot change the frozen Sb recipe, its seeds or any headline claim, and is reported in diagnostics only.
- All 15 networks passed the byte-identical gate (3,417 rows each).

## Face-only form (registered decision form)
The face-only form is the face plus the tool's halo ring, with the surround blanked to grey. Seed-mean AUC of FaceMorpher two-person morphs against matched warp-only images:

| Arm | Seed-mean AUC (95% CI) |
|---|---|
| A | 0.864 [0.848, 0.881] |
| B | 0.879 [0.862, 0.894] |
| Sb | 0.889 [0.873, 0.908] |

Intervals are 95%, from the 64-block bootstrap over the 299 hosts, 5 seeds per arm.

## Gains
- **Sb − B (primary):** +0.011 [−0.010, +0.031], positive on 3 of 5 seeds. Verdict: **inconclusive**.
- **Sb − A (secondary; A's training list has no warp-only negatives):** +0.025 [+0.003, +0.048], positive on 4 of 5 seeds. Verdict: **inconclusive**, because the seed-mean is below the registered +0.03.
- These intervals resample hosts only. A seed-level t-interval on the five paired gains gives [−0.027, +0.049] and [−0.003, +0.054].

## Licences
- All three arms separate blend from warp and receive **licence (b)**: "consistent with blending and noise averaging; no evidence beyond low-level statistics".
- **Licence (c) is not reached by any arm.** It requires beating both learners of the arm's own training list on at least 4 of 5 seeds; the counts are A 0 of 5, B 3 of 5, Sb 3 of 5.
- These counts are not comparable across arms, because each arm's learners differ (face-only gbt: A 0.885, B 0.833, Sb 0.859).

## Adversary floors
- Hand-made statistics cross-fitted on these rows themselves reach 0.925 (logreg) and 0.917 (gbt), and outrank every network. They are in-domain references, whereas the networks never saw FFHQ or FaceMorpher.
- The best single statistic reaches 0.878 [0.856, 0.901]. It is the best of several, so it carries a winner's-curse caveat.
- The face-only file-size floor is 0.666.

## Flags at the networks' own threshold
- Face-only warp-only images are flagged at 47–99% (A 0.51–0.90, B 0.47–0.99, Sb 0.69–0.93).
- The same images in the whole frame are flagged at 2–14%.
- The grey surround shifts scores towards "attack", so the face-only result describes ranking, not operating-point behaviour.

## Printed only
- The whole-frame AUCs are 0.979 (A), 0.990 (B) and 0.983 (Sb). The whole frame is surround-dominated; the adversary's all-cue gbt reaches 0.981 there. Whole minus face is +0.115, +0.112 and +0.094.
- The order of Sb and B reverses in the whole frame (Sb − B ≈ −0.007, near ceiling).
- The ring-share terciles are flat (Sb 0.888–0.897).

## Predictions
The registered arm-AUC predictions (0.50–0.80) were too low. The predictions "Sb − B inconclusive" and "no arm reaches (c)" held.

## What may not be written
- No outcome of XF1 licenses "detects identity mixing".
- Also not allowed: "Sb detects blending better than B (or A)", "beyond hand-made statistics", and any generalisation claim.

## Not run, available after the deadline (post hoc; registration first)
1. A seed-plus-block bootstrap as the standard uncertainty for paired gains, plus a network-minus-best-single-statistic comparison that accounts for how the statistic was selected.
2. An eroded-hull face-only form that removes the halo ring (unchanged AR1 `blank.one()` with a smaller hull).

## Files
- `xf1_read.json`
- Result tar `/mnt/t7/smad_next/XF1/results/XF1_scores.tar` (61f001ae…), with a second verified copy in `results_copy2/`.
- Job log `results/XF1-3553044.out`.
