# Combined results review: TB1 S part, ME1 single-image part, RI1

Saved from the results-reviewer (opus) hand-back, 13 Nov 2026 (development data only; the reviewer edited nothing). The reviewer's post hoc script is not kept in the repo.

I checked all three. The code pins match (`sha256sum -c` OK for src/TB1, src/ME1 and src/RI1, and the tree is clean). I re-derived each verdict from the JSONs. For ME1 and RI1 I also recomputed key numbers from the development feature and embedding files, read-only. Those numbers are post hoc and labelled as such. I did not open any fst, valx, A12SP, benchmark or sealed file.

## Verdicts
- **TB1 S part: ACCEPT WITH EDITS.** The string follows mechanically, but its wording claims more than the evidence supports.
- **ME1 single-image part: ACCEPT WITH EDITS.** "No readable claim" stands. But the stated cause is wrong, and the code departs from the registered text in a way that changes the verdict string.
- **RI1: ACCEPT.** "Inconclusive: P1 invalid" is the correct branch and follows mechanically. It needs a result.md, and one rewording of the Sb increment.

## Findings (most severe first)

**1. ME1, major: the "> 5% missing" comes from the reader taking a log, not from the statistic.**
- `/mnt/t7/smad_next/ME1/me1_feats.csv` has `R2w4_echo_in = 0.0` and `R2w_echo_in = 0.0` (the hull median prominence) on 287 of 291 rows. The ring values `*_echo_out` are positive (only 4 R2w4 ring values are 0). So the ratio is a finite 0.0.
- `me1_read.py:99` takes `np.log(...)`, which turns 0 into −inf, and the code then drops those rows as non-finite (stdout: "divide by zero encountered in log").
- result.md line 39 says "the ring median prominence is 0". That is wrong: it is the hull median that is 0.
- Genuinely NaN rows: S4 4, S3 4, R2w4 4, R2w 4 (1.4%), R0_61 16 (5.5%).
- The code also makes the whole part "not measured" if any rung fails (`me1_read.py:275`). Amendment 1 S4 says "its contrast is 'not measured'", which scopes it to the contrasts using that rung.
- Read as the text says (post hoc, AUCs on the raw ratio, by rank):

| Contrast | AUC |
|---|---|
| R2w4 vs R0_m7 | 0.002 |
| S0 vs R2w4 | 0.991 |
| R2w4 vs R2w | 0.500 (all ties) |
| S4 vs R2w4 | 1.000 |
| S3 vs R2w | 0.991 |
| S4 vs S3 | 0.601 |

- So the text-faithful verdict is "invalid (control): R2w4_vs_R0m7, S0_vs_R2w4 outside [0.42, 0.58]; R0_61_vs_R0 not measured (5.5% missing)".
- Both readings give no readable result, no kill and no arm. The registered output stays as it is, and the lead should rule which string the record carries.

**2. ME1, major (what the statistic actually reads).**
- The median of the per-window maximum prominence is exactly 0 on 287 of 291 single-warp images and 117 of 291 stored-small images.
- It is non-zero on genuine photos and on both kinds of blend (two-person and same-person).
- So it mostly records image history (one warp or one downscale removes all secondary autocorrelation peaks). It does not isolate a second person.
- The logged prediction ("sees a second layer" ≤ 0.55) would be falsified post hoc, but only for this confounded reason.
- S4 vs S3 within D is 0.596 [0.561, 0.633]. This is printed only. It must not be called a kill, because the control branch comes first.

**3. TB1, major (over-claim): the row-1 string must not be used as prose.**
- The derivation is correct. `--part s` does not compute the outcome, so I re-derived it by hand:
  - P within D 0.7576 (`tb1_premise.json`);
  - S within D 0.6573;
  - no binding control outside its band;
  - shortcut gain +0.006 and 0 of 5 seeds at +0.03, so the arm condition is not met.
- But the evidence behind the label is weak:
  - The margin over 0.65 is 0.007. There is no interval, and the folds are by host, not by connected person component (the standard from tonight's reviews).
  - The guard-band version gives 0.625, which would be row 2. colorFERET gives 0.583.
  - The arm is below every adversary floor, with intervals excluding 0:
    - all-cue: 0.654 vs 0.773, difference −0.118 [−0.151, −0.087];
    - nuisance: 0.719, difference −0.064 [−0.100, −0.032];
    - within D: 0.657 vs the logistic floor's 0.757.
  - It equals the best single 27-statistic cue (0.657).
  - The premise sentence behind the label was withdrawn by the premise review, and amendment 2 falsified the profile (+0.010 over band energy and geometry).

**4. TB1, minor: storage sensitivity.**
- The R0_61 vs R0 refit ceiling is 0.657, the same as S4 vs S3 within D.
- The band statistics r separate storage history as well as they separate the classes. The binding control (0.565; FRGC 0.575) passed only because of the direction of the S4/S3 model.

**5. TB1, minor: the Sb increment should be described more carefully.**
- It is +0.013 to +0.026 on all 5 seeds (test hosts +0.013 to +0.025). The five values share r and the folds, so they are not five replications.
- r adds about +0.02 over Sb but only +0.006 over the hand cues. So Sb leaves splice cues unused that the hand features already carry; this is not a new trace.
- Related: Sb on S4 vs S3 (0.729-0.754) is below the all-cue floor (0.773).

**6. RI1: the gate, fidelity and branch are correct.**
- Controls run first and all are in [0.40, 0.60]: R0_61 0.452, R2w4 vs R0 0.493, S0 vs R2w4 0.536, R2w4 vs R2w 0.499.
- The gate is implemented as amendment 1b R1 specifies (`ri1_read.py:174-176, 206-207, 295-298`). It gave 0.934 and 0.873, both outside the required [0.40, 0.60], so P1 is invalid and the outcome is inconclusive.
- I reproduced P1 = 0.7016 and gate = 0.9343 independently.
- It is not a near-miss. The direction alone separates genuine photos at 0.934, which is more than P1's 0.702. The likely cause: u_HB loads more heavily on emb(H), because cos_HB ≤ 0.65 < 0.68 ≤ cos_HS.
- Post hoc, comparing within the same direction:
  - R4 vs R0 along u_HB: 0.057;
  - R3 vs R0 along u_HS: 0.259;
  - paired difference: 0.181.
  So the morph shows less occlusion spread than its own camera photo.
- P1 = 0.7016 with lower bound 0.660 would have met the pass bar by 0.0016. It must never be reported as "P1 passes".

**7. RI1, under-claim to avoid.**
- Δ fails on its own:
  - S4 vs S3 within D is 0.522, against a pure-D reference of 0.524;
  - R4 vs R3 within D is 0.580;
  - shortcut gain −0.0002;
  - below every floor: 0.540 vs 0.773 / 0.719 / 0.757, and 0.595 vs 0.793 / 0.705 / 0.785.
- Every outcome row with a valid P1 would also say "Δ does not read it". So that sentence is licensed even though M1 is not closed.
- "Negative on all 5 seeds" should become "−0.003 to −0.004 (test hosts −0.008 to −0.011), as expected for an uninformative feature". The seeds are not independent.
- There is no result.md for RI1 yet.

## Next steps (ranked by information per hour)

| # | Step | Cost | Decides | Approval |
|---|---|---|---|---|
| 1 | Lead ruling on the ME1 verdict string, plus the three errata and rewordings above | 0 GPU, about 30 min | What the record carries | Lead |
| 2 | Sb logit plus the adversary all-cue floor features, cross-fitted on S4 vs S3 (stored development scores) | about 5 CPU min | Whether the frozen net leaves the splice shortcut information unused (Finding 5) | Labelled post-hoc descriptive; lead |
| 3 | TB1 S within D with component folds and a component-bootstrap interval | about 5 CPU min | Whether the row-1 margin survives the standard folds (labels only) | Labelled post-hoc descriptive; lead |

No new single-image identity-mechanism arm should be registered before the look-alike set (LA1) exists. All three single-image identity statistics fall 0.06-0.25 AUC below the adversary floors.
