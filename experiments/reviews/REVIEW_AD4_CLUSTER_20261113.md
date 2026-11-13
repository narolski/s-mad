<!-- Independent results review by the results-reviewer agent (on Opus), 13 Nov 2026, delivered about 08:50 to 08:53 CET to the AD4 reading owner; covers both halves of the cluster-stack reading (ViT-B/16 WCSS arm and ViT-L/14 registered arm); saved verbatim by the AD4 reading owner on 13 Nov. Its corrections were applied in commit ad792a0. -->

## Results review: morph-free networks experiment (AD4), cluster-stack readings of 13 Nov

### 1. Verdict
**The conclusions hold but need qualifying.** The main claim holds. In our preprocessing, networks trained only to flag shrink-and-enlarge copies of synthetic SMDD faces reach 0.0% EER on MorDIFF native: 10 of 10 networks across two recipes, each recipe on two stacks, plus A47. So low error on that cell is not evidence of morph detection. The ViT-L/14 verdicts on the DiM cells, and above all "A1 falsified on Fast-DiM-ODE", are much more fragile than result.md suggests:
- The count rule is met by margins of 1.2 to 3.6 points.
- The three seeds that meet it each exist as one run only.
- The "not passable" verdict rests on a single label-permuted network.
- Everything is decided inside the bounded-head floor.

Precedence was fixed before the numbers, and the git and file times confirm it. Several sentences in result.md are wrong or stale.

### 2. Findings (most severe first)

**F1 (Major). ViT-L/14 Fast-DiM-ODE: both verdicts are fragile.**
- Per-seed EER is 0.4, 5.9 (Athena) and 18.6, 17.6, 16.2 (WCSS) (`ad4_reading_m3l.md:35`). All three seeds above 15% are the WCSS-only runs, 1.2 to 3.6 points over the line.
- "Not passable" uses the lowest reference, label-permuted seed 403 at 18.2%. That network's true-label training AUC is 0.47. The next lowest reference is 32.4% (untrained); with it the margin would be −20.6 and the cell passable.
- Label-permuted seed 403 is the lowest reference in **15 of 17 native cells** for ViT-L/14. Its signed AUC is above 0.5 in all 17, mean 0.843 (my computation from `ad4_cells_m3l.csv`).
- Under the same count rule the morph-trained twin has only 1 of 5 seeds above 15% (22.6, 12.7, 9.3, 9.3, 14.7).
- The all-WCSS repeat reuses the same three deciding files, so it is not independent confirmation of the falsification.
- Rewrite: "Fast-DiM-ODE native 11.8% (per seed 0.4, 5.9, 18.6, 17.6, 16.2). By the registered rule A1 is falsified: 3 of 5 seeds are above 15%, by 1.2 to 3.6 points, and these three seeds were each trained once, on WCSS. The cell is not passable because one label-permuted network (seed 403, which did not learn the training task) reaches 18.2%; every other reference is at 32.4% or above. The morph-trained recipe reaches 13.7% (1 of 5 seeds above 15%)."

**F2 (Major). The bounded-head caveat is not applied to the ViT-L/14 DiM verdicts.**
- Median DiM-native morph logits are −3.61 to −3.96, against genuine photos at −3.96 to −4.01 (`posthoc_m3l.md:27-34`). The morph–genuine gap is 0.04 to 0.38 logits, out of a trained span of about 8.1.
- At the 0.5 rule, 100% of DiM morphs are missed.
- The earlier review's rule (REVIEW_AD4_VITB line 34) asks for this. Add: "On ViT-L/14 the DiM morphs sit 0.04 to 0.38 logits above the genuine floor (span about 8.1), and all are missed at 0.5. 'Passable' and 'falsified' on these cells are both read inside the floor band."

**F3 (Major). Same-seed cross-platform differences are as large as seed differences.**
- ViT-B/16: the median over cells of (largest same-seed |ΔEER|) / (between-seed SD) is **0.94**. ViT-L/14: 0.17.
- These are whole-network shifts, not cell noise. Rented seed 401 is worse by 5.7 EER points on average over 34 cells, with 27 of 34 cells in the same direction. Seed 403 is worse by 2.1 (24 of 34). Label-permuted networks are within ±0.14.
- On registered cells, seed 401 gives Greedy-DiM native 11.2% (rented) against 0.5% (WCSS), and Fast-DiM-ODE 8.7% against 2.0%.
- What follows:
  - A per-seed number identifies one run, not a seed.
  - The reproduction-gate pass (Fast-DiM-ODE 2.69 against a bound of 3.0) is within platform noise. The same five seeds gave 4.01 on the rented stack.
- Add to the cross-platform bullet: "On registered cells the largest same-seed difference is 10.7 points (Greedy-DiM native, seed 401). The gate passed on the cluster stack and missed on the rented stack with the same seeds, so 'reproduced' is stack-specific."

**F4 (Moderate). "Seed 403 (WCSS) is the weakest seed in most cells" (result.md:71) is false.**
- Seed 403 has the highest EER in 11 of 34 cells; seed 402 (Athena) in 12 of 34.
- Rewrite: "Seed 403 (WCSS) has the highest EER in 5 of the 6 DiM natives (for example Fast-DiM 24.6%, DiM-A 11.8%); seed 402 (Athena) is the highest in most FRLL cells."
- The platform mix does not explain the weakness of seeds 403 to 405. The WCSS repeats of 401 and 402 match Athena: 401 at about 0 everywhere; 402 with a largest |ΔEER| of 3.0 on the DiM natives (Fast-DiM) and 6.3 overall.

**F5 (Moderate). Stale flag in a registered file.** `posthoc_m3.md:5` (the WCSS arm) still says "not reproduced on this stack (… 4.01%)". The line is hard-coded in `src/AD4/posthoc_m3.py:146-148`. Regenerate the file with the WCSS gate value, or delete the line.

**F6 (Moderate). The follow-ups (H-new-1 to H-new-5) describe the rented networks, not the registered ones.**
- Rented seed 403 differs from its WCSS twin by up to 21.1 points, and blanking used rented seeds 402 and 403.
- Add: "These follow-ups describe the rented networks (now a cross-platform repeat); the registered WCSS networks of the same seeds differ by up to 21.1 points, so the follow-ups do not describe the registered arm."

**F7 (Minor). Wording-rule slips.**
- Wide cells need their ranges: ViT-L/14 AMSL history-matched 15.6% (1.5 to 36.3); FRLL FaceMorpher native 20.6% (5.0 to 35.8); corrected MAD22 FaceMorpher history-matched 37.7% (2.0 to 55.4).
- "Reverses every DiM cell (reversed or split in all seeds)" → "five DiM history-matched cells are reversed (AUC below 0.5 in every seed); DiM-C is split (AUC 0.12 to 0.62)".
- ViT-B/16 DiM-C history-matched: "reduced but not removed (19.4%, AUC 0.72 to 0.93)".
- ViT-L/14 Greedy-DiM is passable on 3 of 5 seeds, with 2 of 5 above 15%; mark it borderline.
- The frozen reader prints seed means for reversed or split cells (for example DiM-A history-matched 83.7); add a table note.

**F8 (Minor). Record corrections.**
- Amendment 5 is commit **082f945** (23:03:05), not ba88926. ba88926 is an SM1 commit; the README 23:02 row and the brief both carry the wrong hash.
- The timing itself is consistent with the claim:
  - The ViT-L/14 WCSS tars got their ctime on the DGX at 23:03:14 to 23:03:16 (ext4 mounted noatime), 9 s after the commit.
  - The ViT-B/16 array was submitted at 23:59 and its results are timestamped 03:44 to 06:46.
  - What was viewed on WCSS before 23:03 can only be checked against the log.

**F9 (Minor). Other stale or confusing text.**
- "Not verified: cluster rerun queued" is out of date.
- "ViT-L/14 ||w|| 4.16 … measured on the rented-arm tensors": no ViT-L/14 network ran on the rented machines.
- The H100 scorer gate is a same-stack, bitwise self-consistency check (|ΔAUC| 0.0, tau 1.0). Print the sha256 of both score files.
- "Does not reach 15%" beside a mean of 11.8% reads as a contradiction; use the F1 wording.
- Define the twin "A12BR R × d0" in the MorDIFF sentence (48.7%).

**On the Amendment 5 precedence choices.**
- ViT-B/16: rerunning on the cluster after a miss was set in Amendment 1 gate 2, before any network existed. It is still an asymmetric, conditional retry: a rented pass would not have triggered it. The A1 verdicts are identical on both stacks; only the gate flips.
- ViT-L/14: the mixed arm was fixed while the Athena numbers for seeds 401 and 402 were known and none for seeds 403 to 405 existed on the DGX. The verdicts do not depend on the precedence, since the all-WCSS arm gives the same ones (Fast-DiM-ODE 11.5%). But the deciding seeds were never run on a second platform.

### 3. New hypotheses

**H-new-1, a shared axis that random heads pick up.**
- Statement: frozen CLIP features hold one direction d = mean(benchmark morphs) − mean(FRLL genuine photos), shared across families. A label-free head scores along it according to cos(w, d).
- Why: reference AUCs move together across cells (median correlation between cells across reference networks 0.77 for ViT-L/14, 0.66 for ViT-B/16). Label-permuted seed 403 has signed AUC above 0.5 in 17 of 17 cells, label-permuted seed 401 has mean signed AUC 0.34.
- Prediction: Spearman(cos(w, d), mean signed AUC) ≥ 0.8 over the 12 reference heads.
- Falsified if it is below 0.4.
- Extension: cos(d, r) with r = copies − natives in the training features. If high, frozen CLIP already reads benchmark morphs as "resampled".
- Cost: about 0.5 GPU-h of frozen-feature extraction; scoring only, no training.

**H-new-2, floor-band instability.**
- Statement: cross-platform |ΔEER| is largest where both classes sit on the floor or ceiling.
- Evidence (exploratory, mine, 170 ViT-B/16 morph-free network-cell pairs): Spearman(|ΔEER|, morph–genuine median logit gap) is −0.36. This is confounded by EER near 0, where Spearman with distance from 0 or 100 is 0.61.
- Test: partial correlation controlling for EER level.
- Falsified if it is above −0.1.
- Cost: 0 GPU.

**H-new-3, the run-level rate on Fast-DiM-ODE.**
- Statement: the share of ViT-L/14 morph-free runs above 15% on Fast-DiM-ODE is at least 0.4.
- Test: fresh seeds 406 to 410 on WCSS, plus a repeat of 403 to 405.
- Falsified if 1 or fewer of the 5 fresh seeds is above 15%.
- Cost: about 16 H100-h. It needs a new registration and the author's extension (past Nov 8) and cannot change the AD4 verdict.

**H-new-4, run-to-run determinism on one stack.**
- Statement: repeating ViT-B/16 seed 401 twice on WCSS H100 is bitwise identical.
- Falsified if any cell differs by more than 0.5 points. In that case per-seed statements are not reproducible even on one stack, which matters to the protocol-network (PN1) and SMDD rebuild (SM1) programmes too.
- Cost: about 1.2 GPU-h.

### 4. Next experiments

| # | Experiment | GPU-h | When | Decides | Approval |
|---|---|---|---|---|---|
| 1 | Fix the posthoc_m3 flag, the hash and the result.md wording (F1 to F9) | 0 | now | correctness of the record | none |
| 2 | Rerun the H-new-1 and H-new-2 sharpness correlations on the registered WCSS scores | 0 (CPU) | now | whether the "softness" reading holds for the registered arm | post hoc amendment |
| 3 | Floor-band partial correlation (H-new-2 above) | 0 | now | how per-seed and gate statements are worded | none |
| 4 | Frozen features plus a random-head null (1,000 heads on features, CPU) and cos(w, d) (H-new-1 above) | 0.5 | Nov 13 to 14 | what the label-free references mean; whether the margin rule is an order-statistic artefact | new registration |
| 5 | Determinism repeat of ViT-B/16 seed 401 (H-new-4) | 1.2 | Nov 14 | whether per-seed claims can be made across the programme | registration, author (date) |
| 6 | ViT-L/14 fresh seeds 406 to 410 plus repeat of 403 to 405 (H-new-3) | about 16 | only with an extension; otherwise after the deadline | robustness of the Fast-DiM-ODE falsification | registration, author |

None of these runs new resampling or blur code; they reuse the registered pack. They touch no frozen networks and no sealed sets.

### 5. Edits for the synthesis page
smad-next has no `experiments/CONCLUSIONS.md`; put these in the AD4 notebook row and `17_MORNING_REPORT_20261113.md`.

- **What we have learned:** "In our preprocessing, CLIP networks trained only to flag shrink-and-enlarge copies of synthetic SMDD faces (no morph, no blending) reach 0.0% EER on MorDIFF in all 10 networks (two recipes, two stacks each). Low MorDIFF error therefore cannot by itself show morph detection. The ViT-B/16 recipe also passes all six DiM natives. The ViT-L/14 recipe passes five, inside the saturation floor. On Fast-DiM-ODE the registered count rule falsifies A1 by narrow margins, with the morph-trained recipe no better (13.7%)."
- **How sure we are:** "The MorDIFF result is robust. The DiM verdicts are decided within a few hundredths to tenths of a logit on a bounded head. Same-seed networks on different hardware differ by as much as different seeds for ViT-B/16 (up to 10.7 points on a registered cell), so per-seed statements describe single runs. The Fast-DiM-ODE falsification rests on three single-run seeds and one unusual reference network."
- **Future directions:** "Test whether label-free references read a shared morph-against-genuine axis of frozen CLIP features (random-head null). Test run-to-run determinism on one stack. With approval, re-estimate the ViT-L/14 Fast-DiM-ODE rate on fresh seeds."

Files: `/home/narolski/smad-next/experiments/AD4/result.md`, `/home/narolski/smad-next/experiments/AD4/posthoc_m3.md`, `/home/narolski/smad-next/src/AD4/posthoc_m3.py`, `/home/narolski/smad-next/experiments/AD4/ad4_cells_m3l.csv`, `/home/narolski/smad-next/experiments/AD4/xplat_m3_wcss_vs_rented.md`, `/home/narolski/smad-next/experiments/AD4/README.md`. I edited no files.
