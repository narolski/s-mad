Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only, at ca76ca3. Saved by the owner; condensed.

# BD1 amendments 2-3 review: accept with corrections

All values were recomputed: FS1 all seeds; AB1 408, 412; SE1 411. Every verdict follows the amended rules and the pins match.

## Findings
1. **Major (factual).** Inside-only rows are flagged 88-100% only in FS1. S3_bg is 0.62-0.94 in AB1 and SE1.
   - S4_bg sits at a ceiling (SD 0.16-0.43); the ranking comes from some S3 rows falling below it.
   - These rows are out of distribution and are not evidence of a deployable inside cue.
2. **Major (calibration).** H1 rests on point estimates; the intervals cross 0 on 2 of 5 FS1 seeds and on most replication seeds.
   - Seeds rank the hosts alike (ρ 0.87-0.95). The seed-averaged partial is −0.23 [−0.42, −0.01].
   - The effect is stronger with more covariates (−0.21 to −0.30).
3. **Major.** The gap action over-claims. Falsification depends on partialling cos_HS (ρ(gap, cos_HS) −0.45). Without that covariate the partial is +0.03 to +0.08.
4. **Moderate.** H4 is an oracle linear comparison. Sb is not a linear read of these statistics. Not a ceiling and not identity.
5. **Moderate.** H2's D_dc verdict was predictable (reference 0.496). D_lin is the informative control.
6. **Minor.** Seed 405 inside is 0.6506, at the bar. Add the AB1/SE1 H1 intervals.

## Licence
BD1 supports no training arm before the freeze. FR-matched look-alikes (author item, post-freeze) rank above a colour-matched rescore. Before the freeze, at most a zero-GPU descriptive read of low-cos_HS S3.
