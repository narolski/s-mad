<!-- Post-result review of the standing adversary's amendment 3 outputs (104ee36, 35f25a7) and strategy answer on a valid development measure, by the results-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. The reviewer's post hoc script is copied to experiments/reviews/scripts_adv/overlap.py. -->

**Verdict: the numbers hold up, but some readings need qualifying.** Every number the owner reported matches the pinned files. The build-1 to build-2 change is acceptable with disclosure. "Not usable" is the right reading of the weights. Three readings go further than the evidence:
- "No balancing can work" is too strong. Full-population balancing fails, but an overlap population exists.
- The "face-blanked S4 vs S0 ceiling" is mislabelled. It is a face-only blend-versus-warp contrast, not a ceiling and not base geometry.
- The S4-vs-S3 and R4-vs-R3 floors (0.75-0.82) are simple morph-cue floors, not shortcut floors.

The registered same-data shortcut learner (ADV prereg line 343, "brought forward, computed now") has **not been computed**. There is no `transfer` output in `floors/`. It is the missing comparator that most of Part 2 depends on.

## Part 1: findings (most severe first)

**1. Major. The comparator for zero-shot networks is missing.**
- In-distribution floors are cross-fitted on the evaluation rows themselves. Networks never saw those rows.
- `run_floors.py cmd_transfer` (lines 423-453) exists and section 5.3 is registered, but no output is committed.
- Until it exists, every comparison of a network with a floor is between a learner fitted on the evaluation set and one that is not.
- Fix: run it now. It needs no GPU, only CPU on the cached features.

**2. Major. "Surround-only 0.942, so no balancing can work" overstates.** Read-only recompute on `floors/lcomb_regional_heldout.csv` (scripts in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/adv3/overlap.py`):
- **Overlap coefficient of the boosted-tree surround logit: 0.258.**
- Morph / genuine counts per pooled decile: (2,298) (4,296) (9,291) (14,286) (25,275) (53,247) (124,176) (202,98) (276,24) (291,9).
- Only 1.8% of morphs fall below the genuine median; 54.7% fall below the genuine 99th percentile.
- Effective sample size (ESS) under three weighting schemes:

| Weighting | Morph ESS | Genuine ESS | Meets 300 per class? |
|---|---|---|---|
| ATE inverse-probability (registered) | 8.02 (10 morphs carry 72% of the weight; max weight 1,039) | 413.8 | No |
| ATT, logistic score | n/a | 7.9 | No |
| ATT, boosted-tree score | n/a | 78 | No |
| Overlap weights, boosted-tree score | 420 | 709 | Yes |

Correct reading:
- Landmark_combined cannot be history-balanced for the full morph population.
- A surround-balanced overlap population of a few hundred per class does exist.
- AB1 3d item 8 forbids adding that route for H-hb1, so it could only be a separately labelled descriptive print.
- It would not help anyway. On the balanced rows the full-data held-out face-box scores still give 0.962 (logistic) and 0.968 (boosted trees); the refit gives 0.941. History balance leaves a face floor near 0.95, and a network "exceeds" test there is again close to predetermined.

**3. Major. The S4bg-vs-S0bg "ceiling" is mislabelled.**
- `contrasts.py:215` and the audit (PARTNER_OVERLAP_AUDIT.md:351) show S4_bg is the two-person face blend with the **background** blanked. S0_bg is warp-only pixels on the same R2w4 base, also blanked.
- So both sides are not genuine, and it is not surround-only.
- Regional file: surround 0.500 (blank), face box 0.968 [0.951, 0.982], file 0.716. The F27 family alone gives 0.949 and BLEND 0.941.
- This is blend texture inside the face. It matches the face floors of R4 vs R2w (0.987 for both engines).
- It is not warp geometry of the base. Rename it "face-only blend vs warp-only".

**4. Moderate. The S4-vs-S3 and R4-vs-R3 floors are not shortcut floors.** At equal blend difference D, the logistic floor still gives:
- 0.744-0.785 for splices;
- 0.767-0.785 for R4 vs R3 (`ri_R4_vs_R3_withinD.json`, `test_cv_R4_vs_R3_withinD.json`, both uncommitted);
- against 0.57-0.59 for D alone.

What carries it, and why it is legitimate:
- Surround is weak (R4 vs R3: 0.62 OpenCV, 0.53 FaceMorpher); the face box carries 0.74-0.77.
- Blending two different people leaves colour, illumination and ghosting mismatch, a physical consequence of the second identity. That is a legitimate low-level cue, not a construction artefact.
- Rename these to "simple morph-cue floor". Keep "shortcut" for cues unrelated to the attack (history, border, storage).

The frozen candidate against these floors:
- Its test S4 vs S3 is 0.72-0.74 and stratified 0.714-0.751 (REVIEW_PR1_PART1:14,17).
- That is **at or below** the in-distribution simple-cue floor (test 0.754 [0.712, 0.799]; within D 0.744).
- Supported wording: "Sb's two-person sensitivity is not shown to exceed what hand-made blend statistics reach when fitted on these rows". This stays until the transfer learner (finding 1) gives the fair comparator.
- This confirms the PR1 claim boundary: "detects in-face blending", never identity.

**5. Moderate. The disclosure of the post hoc build change is good but incomplete.**
- Iterating the matching score on covariate-balance results only, with no outcome or network score seen, is standard design-stage practice (Rubin). It is acceptable.
- Add: (i) the face floor was first printed by the third run, after convergence, and no change followed; (ii) the stop "fewer than 50 pairs" was added after build 1 crashed at 5 pairs.
- Add the consumer-side timing: AB1 3b (prereg lines 389-397) set the 150-per-class minimum while already citing "125 morphs and 125 genuine". The gate was therefore known to fail when written. That is conservative, but it must be stated.

**6. Minor. "Converged" partly reflects low power.**
- On 250 rows the refit logistic surround floor is 0.565 [0.494, 0.634]; the upper bound is above the 0.60 bar.
- Full-data held-out scores on those rows: logistic 0.587, boosted trees 0.510.
- Say "balanced to within detection power at n=250".

**7. Minor. Do not quote any weighted number from the inverse-probability weights.**
- The boosted-tree weighted surround floor of 0.404 (below 0.5) and the weighted face floor of 0.63-0.75 are noise from about 8 effective morphs.
- FLOORS.md:71 prints the face 0.629 / 0.745. Mark those "uninterpretable".

**8. Minor. Pins and the working tree.**
- pins_stage1/3/4/5 all verify (14/10/8/2 OK).
- `pins.sha256` fails only for the working-tree `run_floors.py`, which has an uncommitted additive `withind` command.
- The committed blob matches its pin (8b40a0cc). The `*_withinD.json` and `test_*_regional.json` files are uncommitted. Commit and pin them before any consumer cites them.

## Part 2: a valid development measure of morph detection

The framing:
- In-distribution floors of 0.97-1.00 on blend-versus-no-blend do not make those contrasts invalid. They show the contrasts are easy for a learner fitted on the rows.
- A development measure for selection needs four things: (a) it is not saturated; (b) a challenger cannot gain on it by exploiting a nuisance its own training changes; (c) it has a fair zero-shot comparator; (d) nuisance-invariance guards on genuine-versus-genuine contrasts, where the nuisance is visibly separable (0.997-1.000). The draft rule already has (d) as criteria b-e.
- Criterion (a) of the draft rule (landmark_combined + 0.03) fails (b) for exactly the arms most likely to win. RZ1 resize mixing trains on shrink-and-enlarge, and landmark_combined's surround floor of 0.94 is a resampling-history difference. Sbx changes border handling.

Options, ranked by validity:

| Rank | Measure | Validity | Cost | What it licenses / what it does not |
|---|---|---|---|---|
| 1 | Network AUC minus same-data transfer floor (section 5.3, each arm's own training list), on every development contrast | High; the fair zero-shot comparator | 0 GPU, about 1 CPU-hour | Licenses "beyond hand-made statistics trained on the same data". Does not license generalisation. RZ1 on-the-fly augmentation cannot be reproduced (it would be new resampling), so state that limit. |
| 2 | Pipeline-matched development ladder, R4 vs R3 within D quintiles, development hosts (plus the 80 test hosts clean of development), person-component bootstrap, OpenCV and FaceMorpher | High on history (same aligner and storage by construction); not saturated (nets 0.72-0.74) | 0 GPU if rescored in the planned rescoring job (about 1 GPU-hour) | Licenses "sensitivity to a second identity at matched blend strength" only if above the floor. In-domain (FRGC/FERET). FaceMorpher rows are seen by SbFM, so they are asymmetric for it. |
| 3 | New FFHQ FaceMorpher two-person morphs FM(H,B) from the existing MS1 hold-out frames, against the D1d one-photo renders FM(H,H), same rendering path | High on history; external face domain; unchanged morpher, so an allowed operation | CPU minutes plus about 0.5 GPU-hour scoring; needs DATA registration and ADV floors | Licenses "zero-shot blend detection on an unseen face domain at matched rendering". The floor will be about 0.99, so compare against the transfer floor. Engine seen for SbFM. |
| 4 | Landmark_combined paired gain within surround-matched subsets (`check.diff_on_matched`) | Medium; only 125-256 pairs, SE about 0.025 against a 0.03 margin | 0 GPU | Robustness print only. |
| 5 | Landmark_combined AUC as is (current criterion a) | Low for RZ1/Sbx (differential history confound) | 0 | "Zero-shot on an external set with a documented history confound" only. |

None of these licenses a generalisation claim. Only the sealed reads do.

**The single change I would make first:** compute the registered same-data shortcut learner now. Then, before any challenger is read, amend criterion (a) so that a challenger qualifies only if its landmark_combined gain persists with a non-negative paired difference (≥ −0.01 on 4 of 5 seeds) on the pipeline-matched development ladder R4 vs R3. For RZ1 and Sbx, the gain must also hold within surround-matched subsets. Registration is needed before reads; the deadline is 15 Nov 18:00.

## New hypotheses

**H-new-1: what history balancing leaves on landmark_combined is blend texture.**
- Prediction: on lcomb_bal rows the face-box floor is reached by the F27/BLEND families alone at ≥ 0.90, the level of face-only S4bg vs S0bg (0.965).
- Falsified if F27+BLEND alone is ≤ 0.80.
- Cost: 0 GPU, before the freeze.

**H-new-2: the same-data learner explains the candidate's landmark_combined level.**
- Prediction: the transfer floor trained on train_Sb is ≥ 0.85 on landmark_combined.
- Falsified (the network adds information) if it is ≤ 0.75 while Sb is 0.873-0.906.
- Cost: 0 GPU, tonight.

**H-new-3: two-person excess at equal D is colour/illumination mismatch.**
- Prediction: within D quintiles, chroma-only face statistics reach ≥ 0.70 on R4 vs R3; luma-only stays ≤ 0.62.
- Falsified otherwise.
- Cost: 0 GPU.

**H-new-4: resize-mixing arms gain on landmark_combined through history.**
- Prediction: SbM/SbMR's paired gain over Sb0 on landmark_combined shrinks by ≥ 50% within surround-matched subsets, and is ≤ 0.01 on R4 vs R3.
- Falsified if the gain holds on both.
- Data: RZ1 scores once read under the amended rule.

## Next experiments

| Experiment | GPU-h | When | What it decides | Approval |
|---|---|---|---|---|
| Same-data transfer learner (section 5.3), all arms | 0 | Tonight | Fair comparator for every development read; H-new-2 | None (registered) |
| F27/BLEND-only face floor on lcomb_bal; chroma/luma split within D | 0 | Tonight | H-new-1, H-new-3; floor naming | ADV amendment (descriptive) |
| Commit and pin withinD/regional files; relabel S4bg | 0 | Now | Citability | None |
| Amend criterion (a) of the selection rule (ladder co-primary, surround-matched print) | 0 | Before any challenger read | Prevents a history-driven winner | Author's written yes |
| Ladder R4/R3 rows in the planned rescoring job | about 1 | 14 Nov | Supplies ranks 1-2 | Owner amendments |
| FFHQ FM(H,B) vs D1d FM(H,H) | about 0.5 | 14 Nov | External pipeline-matched measure | DATA registration; lead |

## Risks
- The MAD22 genuine photos are history-matched, so a history-reliant candidate loses its crutch there. That is good for validity, but the AUC may fall.
- If the transfer floor is at or above the networks, the "beyond shortcuts" story fails at development level.
- Partner sharing: 171 of 191 test hosts share a person component with a development host. Any ladder measure must use component bootstrap.

## Edits for the conclusions text (18_EVENING_CONCLUSIONS / FLOORS.md:69-72)
- **What we learned:** "Landmark_combined's surround separates morphs from genuine photos at 0.94 (overlap coefficient 0.26), so it cannot be history-balanced for the whole morph population. Where the surround is balanced, the face box still separates at 0.94-0.97, the level of pure blend-texture contrasts. Two-person versus same-person blends separate at 0.75-0.82 in-distribution, 0.74-0.79 at equal D: a legitimate simple morph cue, not a shortcut."
- **How sure:** "The lcomb_bal reading is descriptive: 125 per class, rule fixed after two builds that saw balance diagnostics only. The weighted read is not usable (ESS 8). No network has yet been compared with the same-data shortcut learner, which is the fair comparator."
- **Future directions:** "Run the section-5.3 transfer learner. Make the pipeline-matched development ladder R4 vs R3 a co-primary of selection criterion (a). Add the FFHQ FaceMorpher two-person versus one-photo-render contrast."

Key files are under `/home/narolski/smad-next/`:
- `experiments/ADV_shortcut-floors/prereg.md` (lines 318-343)
- `experiments/ADV_shortcut-floors/FLOORS.md` (lines 50, 69-72)
- `experiments/AB1_protocol-ablation-and-replication/prereg.md` (lines 389-397, 458-482)
- `src/adversary/run_floors.py` (lines 423-453)
- `src/adversary/contrasts.py` (line 215)
