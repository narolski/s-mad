Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only, development data only, at 6aa02f8. Saved by the PR1 owner; findings condensed, all findings, numbers and replacement texts kept.

# PR1 part 1 results review: accept with corrections

The reviewer recomputed every number independently from the 15 tars, with its own code, and found no mismatch. Matched: Z0 ranges; Z1 (training S3 flagged 0.276/0.256/0.301/0.365/0.295, S4 missed 0.040/0.065/0.032/0.032/0.040); Z2a, τ5 and G_max; Z2c 0.6674-0.7945; ρ +0.557 with p 0.034; Z3 at 1.0000; Z4; Z6; the FFHQ printed values. Every registered verdict follows its rule, including the amendment-1 order for Z1.

Trivial differences: B's lowest τ5 is −1.93, not −1.94. The Z2c "10% of S3" cut-off depends on the quantile definition (63.9-90.2% against 61.5-90.2%), so state the definition. Explain why the Z0 row for B prints "differs".

## Findings
1. Major: Z3 "no engine gap" is a ceiling non-result. Every AUC is 1.0000 and misses are 0-0.5%. It must not cancel arm #6, because a saturated contrast can never fire the Δ ≥ 0.03 trigger. Replacement text applied.
2. Major: the Z1 write-up does not say what the result licenses.
   - Sb fits every other kind on all 5 seeds (result.md wrongly said "on seed 403").
   - S3 flags are a training-level problem (gap +4.5 to +8.9 points). S4 misses are a generalisation gap (+12 to +23 points).
   - The S4-vs-S3 training AUC is 0.85-0.88 and the test AUC 0.72-0.74. Weighting moves the threshold, not the ranking.
   - So there is no support for SL1. Nothing shows that SE1 works either. Replacement text applied.
3. Moderate: the facts section under-reports support for the strategist. At the S3-10%/20% cut-offs landmark_combined misses are 61.5-90.2% / 48.0-75.6%. Unregistered side note: A and B separate landmark_combined from dev S3 at 0.90-0.96. Retitle the section, move item 4 out, and add the selection-set note. 0 of 100 dev and 0 of 191 test splice hosts or partners are among the 156 training persons.
4. Moderate: Z6 is a ceiling read on one statistic and 60% of the rows. Its informative part is Sb's stratified S4 vs S3, 0.714-0.751 on all seeds, against 0.503 for lapvar alone.
5. Moderate: Z2a "usable" for Sb needs qualifiers. G_max excludes the one-person images (Sb flags 32-43% of dev S3 at τ5), and A fails through its history-matched FFHQ copies (19-22%).
6. Minor: update the review status. Add the reason for the A/B S0 "inconclusive" (weak S4 detection, 91-98% missed). Word ρ as "across recipes".

## New hypotheses (zero GPU unless stated)
- H-new-1, host memorisation: the same training S3 rows are flagged across seeds. Falsified if the cross-seed overlap is ≤ 1.5 × chance on ≥ 4 seeds.
- H-new-2, donor-host mismatch drives S3 flags: |ρ| ≥ 0.3 with donor-minus-host cue differences. Falsified if |ρ| < 0.2 on ≥ 4 seeds.
- H-new-3, ranking not weighting: at the training cut-off flagging 5% of training S3, training S4 misses are ≥ 30%.
- H-new-4, engine gap on a non-saturated axis: AUC(R4 vs R3) OpenCV minus FaceMorpher ≥ 0.03 for Sb on ≥ 4 seeds; falsified if ≤ 0.01.
- H-new-5: the dev/test difference in S4 vs S3 is selection or sampling (host-bootstrap CI includes 0 on ≥ 3 seeds).

## Next experiments
Ranked: Z1b (H-new-1, 3, 5); Z3b (H-new-4); Z2b-τ5; H-new-2; GD0-GD2; SE1 as an ablation only; an S3-balanced Sb only if Z1b confirms. SL1 is deprioritised.

## Risks
Carry the ceiling qualifiers wherever Z3 and Z6 are cited. The claim must be "detects in-face blending", never identity (R3 is flagged 83-99%). F10 is open until Z2b-τ5 is read. GAN families are untested (GD0).
