Reviewer: experiment-reviewer (Opus), 13 Nov 2026, read-only, on the LA1 plan drafts. Saved by the owner; condensed.

# LA1 look-alike pair search plan: GO WITH FIXES (as a plan)

1. **Major.** CelebA labels are on disk (`datasets_processed/data-celeb-aligned/split.csv`, 202,084 rows, 10,177 identities, 128 px). Only the CelebA-HQ-to-CelebA mapping and the attribute file are missing. Do not rebuild the mapping by embeddings.
2. **Major.** The MS1 overlap guard removes about 37% of images by chance (CASIA), and those are the look-alike population. Kept pairs number about 4.9×10⁷, not 2.6×10⁸. The author or lead must decide whether CASIA overlap matters; if it does, use a per-identity calibrated threshold; print with and without.
3. **Major.** The label-noise rule misses single wrong images. Use image-level own-identity tests, thresholds from labelled CelebA, and noise injection. Use no pHash (it needs a downscale); use cosine ≥ 0.97 plus landmarks. Relatives are not detectable.
4. **Major.**
   - MUCT yields nothing (IED 87-93 px < 112.7; only 751 frontal images).
   - The alignment step is missing.
   - `a2f_common` forces CUDA; the paths are pinned; the second-model embeddings do not exist.
   - Recommend the DGX for about 2,000 MEDS images. Queue naming follows OWNER_BRIEF.
5. **Major.**
   - Count a disjoint matching; match counterparts from the same source.
   - No-go floor about 50.
6. **Minor.**
   - Published FMR 1e-6 at about 0.4 cosine, so the true tail at 0.6 is far rarer than 1e-5.
   - The calibration used about 2×10⁶ pairs.
   - Name which same-person range is meant.
7. **Minor.**
   - The ladder persons are hosts and must be excluded.
   - Add a role list with a val10 assertion.
   - Keep LA1 identities disjoint from the MS1 held-out set.
8. **Minor.** Define pose, sex source, threshold values, and what happens if no mapping file is available.

## Improvement
LA1-0: a labelled tail calibration on data-celeb-aligned. Two models, about 20k images, about 0.5 DGX GPU-hour. It turns the yield guess into a measurement.

## Questions
- Does CASIA overlap matter?
- May the mapping and attribute files be downloaded?
- WCSS or DGX for about 2,000 images?
