# NE1b: splice feature ceiling and rank-7 border erasers: result

Status: read once, 13 Nov 2026 (`date` Fri Nov 13 08:30:50 PM CET 2026 to 08:57:10 PM). Not yet reviewed.

- Registration 22618b8 (pre-run check b8288e3, fixes 1-7; DATA audit 1b05940).
- Reader `ne1b.py` `9b78d588…`; output `ne1b_read.json` `4227f8eabe0c7fde…`.
- CPU only, saved NE1 features, development rows only. All five networks are platform-certified (NE1 gate).
- Storage is not read.

## Registered table

| Part | Reading | Count |
|---|---|---|
| A. Splice feature ceiling | **intermediate (probe above H0 but below the bottleneck bar)** | low ceiling on 3 of 5 seeds (needs 4); bottleneck 0; nonlinear-only 0 |
| B. Rank-7 border erasers | **criteria unreachable (inconclusive by design)** | the half-B ceiling eraser E7c is clean on only 3 of 5 seeds; E7 is clean on 2, LEACE on 0 |

## Part A readings (out-of-fold over 110 person components, 291 hosts; seeds 403 / 404 / 405 / 406 / 407)

- **AUCs.**
  - Frozen head H0, S4 against S3: 0.757 / 0.754 / 0.739 / 0.769 / 0.748.
  - Linear probe: 0.760 / 0.785 / 0.762 / 0.791 / 0.787.
  - Gain over H0 +0.003 to +0.039, with component-bootstrap intervals [−0.016, 0.021], [0.011, 0.050], [0.005, 0.040],
    [0.004, 0.039] and [0.018, 0.058]. The gain is above 0 on 4 of 5 seeds.
- **Why "low ceiling" holds on only 3 seeds.**
  - Seed 407's upper bound is 0.058, above the 0.05 bar.
  - The learning curve has not flattened on some seeds. From 100 hosts to all of them (226-236), AUC rises by +0.001
    to +0.022. From 25 hosts to all, it rises by 0.03-0.05.
- **Other probes.**
  - Small MLP: 0.725-0.776, never above the linear probe.
  - Core-only probe: about the same as the linear probe.
  - Training-list probe (lin_T): equal to H0 (±0.003).
  - Label-permutation null: at most 0.57.
- **Printed checks.**
  - 80 clean test hosts (fit on development hosts): linear probe minus H0 is +0.015 to +0.033.
  - Without the largest component (10 hosts): unchanged.
- **Plain reading.**
  - The frozen features carry a little more same-person against two-person information than the frozen head uses:
    about +0.02-0.04 AUC, and still growing with more fit persons.
  - The ceiling is nowhere near the bottleneck bar (0.85). The best probe reaches 0.79.
  - So no head-level change makes this distinction good. A modest gain from a larger refit set is not excluded.

## Part B readings (half-B persons, 1,435 pairs, 202 hosts)

- **H1's border response.** Pooled Δlogit 0.47-0.72; excess flags at the 99th-percentile camera cut 0.048-0.166.
- **E7 (rank-7 per-mask span).**
  - Logits: cancelled two-sidedly (removal 0.91-1.02), and per mask on 6-7 of 7 masks.
  - Ranks: two-sided (1.05-1.11).
  - Flags: two-sided only on seeds 403 and 407 (0.72, 0.72). Elsewhere 0.26-0.66.
  - The residual flags sit mostly in CFP-FF and MSU-MFSD (0.04-0.15 excess on those masks).
- **E7c (fitted on the read rows, the ceiling).** Flags 0.66-0.87, two-sided on 3 of 5 seeds. By the registered order
  this makes the criteria unreachable: even an in-sample rank-7 mean-difference eraser leaves part of the excess flags.
- **LEACE (Ledoit-Wolf).** It removes the half-B class-mean spread by 88-90% (0.39-0.60 → 0.05-0.06), but transfers
  worse to flags: removal 0.22-0.48, never two-sided. Its condition number is 1.0e4-2.8e4. E7 removes the spread
  further (to 0.02-0.03).
- **Nulls.** Isotropic rank-7 nulls pass two-sided on 0 of 20 on every seed; head-matched on 0; covariance on 0-2.
- **The registered in-domain cost check is saturated.**
  - Every head, null and eraser has R4 recall 1.000 and R4-vs-R0 AUC 1.000 on the half-B test hosts (198 R4 rows).
  - So "no cost" held trivially, and the check could not detect a cost. This is a design flaw of the registration: the
    native-strength ladder R4 is too easy for these networks.
- **Cross-domain cost (printed only).** On FFHQ landmark_combined, recall at the 99th-percentile camera cut falls for
  E7 against H1 by 0.269 / 0.060 / 0.188 / −0.011 / 0.141, and AUC falls on 3 seeds (0.811 → 0.736, 0.847 → 0.766).
  LEACE costs little (−0.05 to +0.03).
- **Overlap with the head.** The E7 span contains most of the frozen head direction: the norm of ŵ's projection onto
  it is 0.68-0.90. Erasing E7 removes most of what the frozen head reads, and the refit has to rebuild detection from
  the rest. It does so for easy in-domain R4 but not for FFHQ landmark morphs.

## What this does and does not show

- **Shows.**
  - The border response is not one direction. A rank-7 per-mask span cancels it in logits per mask, but the flags at
    a fixed false-alarm cut keep 13-74% of the excess, mostly on CFP-FF and MSU-MFSD.
  - That span overlaps the frozen head (projection 0.68-0.90).
  - Removing it costs FFHQ landmark-morph recall on 4 of 5 seeds (up to 0.27), even though in-domain R4 recall stays
    at 1.0.
- **Does not show.**
  - That a training-time debiasing arm would help. The registered reading is "criteria unreachable", and the printed
    cross-domain cost points to border and detection sharing features.
  - That the splice distinction is absent from the features. A small gain (+0.02-0.04) is present; it is not large
    enough to change the S3/S4 trade-off.
- **Licenses.** No debiasing arm and no splice-head arm is licensed by NE1b.
