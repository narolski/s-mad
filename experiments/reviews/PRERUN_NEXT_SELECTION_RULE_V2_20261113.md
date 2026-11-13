<!-- Pre-run check of the selection rule draft v2 (3c2b9d5) by the experiment-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. The reviewer's simulation scripts are copied to experiments/reviews/scripts_selection_rule/. -->

## Pre-run check: selection rule v2 for the next method version (prereg_draft_v2.md, commit 3c2b9d5)

**Verdict: GO WITH FIXES.** All fixes are text changes or CPU-only, with no GPU cost. Make them before the author's yes and before any challenger tar is opened.

As written, the rule would almost never pick a real +0.03 arm, and it favours the DINOv3 route. Two criteria cannot be computed as specified.

I checked: draft sha256 1388a0ac… equals 3c2b9d5. The manifests ab1_eval.csv, ab1x_eval.csv and FS1 pn1_eval.csv all hold the 582 R4/R3 ladder rows and the 3,000 landmark_combined rows, with the same paths. BD1 d_values.csv covers S4 and S3 for all 291 hosts. No score was opened.

### Findings

**1. Blocker: criterion (a)(iv) cannot be computed.** (lines 125, 133-135, 220)
- transfer_*.json (735a65e, stage 8, all 15 training lists) store only one logreg and one gbt AUC per contrast. Example: transfer_Sb lcomb is 0.787 and 0.665. There are no per-row scores and no interval.
- Their ladder contrasts are dev_cv and test_cv separately. None covers the 100 + 80 subset, and none is within D.
- So "the 2.5% bound … re-taken in the same person-component draws" cannot be produced.
- Fix: before pins, the learner writes per-row held-out scores on the landmark_combined rows, the 360 ladder rows and the matched rows. One file per training list: train_Sb (for Sb, Sb0, the RZ1 arms and DINOv3), train_SbFM, and GX once its manifest exists.
- Also update section 9: the learner for SbFM and train_Sb now exists, but only as summaries.

**2. Blocker: the (a)(iii) subset is specified two incompatible ways.** (lines 114-115, 120)
- `check.diff_on_matched` (src/adversary/check.py:99-127) matches on the contrast's all-cue floor: lcomb logreg, 0.982. It cannot read `surround_gbt`.
- Matching on that floor gives **186 pairs**, and the surround floor still separates them at **0.774**.
- Matching on `surround_gbt` with caliper 0.1 and rng 20261117 gives **360 pairs**, with surround balanced at **0.504**. But the face-box floor stays at **0.949** and the all-cue floor at **0.945**.
- "125" is the size of lcomb_bal, not of this subset.
- Replacement text: "Subset: 1:1 greedy matching of morphs to genuine photos on the logit of `surround_gbt` (floors/lcomb_regional_heldout.csv), caliper 0.1 SD, default_rng(20261117); 360 pairs; ids pinned. Known limit: surround-balanced only; face-box floor 0.949 on these rows, so history in the face interior is not removed."

**3. Major: the 4-of-5 votes are fragile, and all seeds share the same hosts.**

I simulated the per-seed difference as d_s = Δ + τ (shared rows) + noise from two independent fits with seed SD σ, 200k draws.

| Criterion | What is tested | Rule as written | Proposed rule |
|---|---|---|---|
| (ii) ladder, σ 0.015-0.025, τ 0-0.02 | equal arm fails | **35-64%** | 3-32% |
| (ii) ladder | arm with a true −0.03 loss passes | 0-10% | 14-27% |
| (i) landmark_combined | true +0.03 arm passes | **19-28%** | 65-74% |
| (i) landmark_combined | equal arm passes | ≤0.2% | ≤2% |
| (iii) matched | equal arm passes | 1-18% | 6-31% (seed-mean ≥ +0.015) |
| (iii) matched | true +0.03 arm passes | 46-65% | 69-94% (seed-mean ≥ +0.015) |
| All of (a) | true +0.03 arm with an equal ladder qualifies | **about 3-18%** | about 0.3-0.65 |

- Under the current (i) rule an arm needs about +0.045 true gain for 80% power.
- Replacement for (ii), paired arms: "Pass: seed-mean within-D difference ≥ −0.02 and no seed below −0.06. Printed: the 95% person-component bootstrap interval of the seed-mean difference (the same draws for all seeds)."
- Replacement for (iii): "seed-mean matched gain ≥ +0.015 and ≥ half the seed-mean full-set gain."
- Optional for (i), author's call: "seed-mean gain ≥ +0.025 and gain > 0 on ≥ 4 of 5." Otherwise disclose: "a true +0.03 gain passes about 1 time in 5."
- Replace the "not known" sentence in section 11 (lines 247-251) with these numbers.

**4. Major: the bootstrap unit is ambiguous.** (line 99)
- "components of the full person graph, as the audit defines them" includes training persons, where one component holds 432 persons.
- The floor file's `component` column instead has 110 evaluation-pool components. On the 360 subset rows the largest has 14 rows (3.9%).
- Replacement: "the `component` column of floors/ri_R4_vs_R3_heldout.csv (110 evaluation-pool person components)". This also lets network-minus-floor reuse the same draws.
- Also state that the D quintile edges are taken over the 360 subset rows, and print coverage.

**5. Major: the DINOv3 route is easier than the CLIP route.**
- (i): the fixed bar 0.922 with U ≤ 4 passes a true +0.03 about 40-49% of the time, against 19-28% for paired arms.
- (ii): median minus 0.01 fails an equal arm 19-30% of the time, against 51-64%.
- (iii) never applies to DINOv3, and (b)-(d) use medians.
- Fix: put every arm on seed-mean rules. For DINOv3, use the seed-mean difference against the five AB1 Sb fits with a seeds × components bootstrap. Apply (iii) to **every** challenger: it costs no GPU, and GX and SbFM change composition, so they can change how much the network leans on resampling history.

**6. Major: the tie-break re-imports the history cue and mixes scales.** (lines 180-182)
- Ranking by landmark_combined gain uses the very measure the redraft distrusts.
- Paired gains against Sb0, gains against AB1 Sb, and the unpaired median difference are not on one scale.
- Replacement: "Several qualify: the earliest in the list of section 3 is chosen." Flatten the list explicitly: 1 SbFM, 2 GX, 3 SbMR, 4 SbM, 5 Sb512, 6 SbMR512, 7 Sbc, 8 DINOv3.

**7. Major: a history-only gain can still qualify.**
- Today, a non-RZ1 arm can gain on (i) through the history cue and pass (ii) on tolerance alone. Finding 5's universal (iii) closes most of this.
- Add to (iv): for SbM, SbMR and SbMR512 (on-the-fly resampling), "beyond hand-made statistics trained on the same data" is not allowed. Use "…trained on the stored frames of the same list".
- Define "the seeds the arm's registration requires" (line 135) as 4 of 5.

**8. Major: the freeze, MAD22 and winner's-curse safeguards are missing.**
Add to section 7:
- "The margins, list and order of this text are fixed at commit <sha> before anyone in the lead chain sees the frozen candidate's MAD22 result. If the author's yes comes later, no text may change except fixes named in this check."
- "Selection numbers are selection-biased and are never reported as the chosen arm's effect. The chosen arm is confirmed on fresh seeds 413-417 (RZ1 m6) with the same rule before freeze. If it fails, Sb stays."

Question 4 should become a rule, not a question: there are up to 8 challengers and the comparators are shared. Section 8 should add "one network per reported number; per-seed mean ± SD; no ensembles."

**9. Minor: deadline and "not read" can be gamed.** (lines 173, 193)
- Replacement: "Read by the deadline = all fit and rescoring tars landed and hash-verified by 15 Nov 18:00, whenever the read itself happens. The jobs supplying each arm's inputs are listed and committed now. An arm is 'not read' only for a listed reason (deadline, infrastructure failure, missing seeds), and that reason is reported."

**10. Minor: inputs that do not exist yet.**
- The 32 shape-linked test hosts are only counts in partner_overlap_addendum.json, not a host list. Build and pin it.
- The within-D floor on the 360 subset is not computed (the existing withinD file covers 582 rows).
- ADV prereg.md has an uncommitted change, and run_floors.py's pin fails. Pins-first needs a clean tree.

**11. Minor: arms that cannot qualify without new jobs or rulings.**
- DINOv3: no border-blanked rows and MEDS unknown, so (d) is not read.
- SbFM and GX: no TT1 or MEDS rows (needs question 3).
- GX: no border rows, and its manifest is not built.
- Sbc: waits on the crop ruling.
- SbMR512: trains on mixed resizing but has no (e) test. Exclude it, or disclose that it is untested.
- So today only SbMR and SbM have every input apart from the learner and the pins.

The licence in section 1 is otherwise modest and correct.

### Improvements, all with no GPU cost
1. Per-row transfer and within-D files, then pins (findings 1 and 10). Lead or ADV owner; no author approval needed.
2. Seed-mean rules, universal (iii), list-order choice (findings 3, 5, 6). Text change; needs the author's yes.
3. The freeze-before-MAD22 and fresh-seed clauses (finding 8). Needs the author's yes.

### Questions for the authors
1. Will you approve the text before you see the frozen candidate's MAD22 result?
2. Do you accept a fresh-seed confirmation after 15 Nov?
3. Do you accept (i) as a seed-mean rule, or keep +0.03 per seed and disclose its low power?

Files:
- /home/narolski/smad-next/experiments/NEXT_method-selection-rule/prereg_draft_v2.md
- /home/narolski/smad-next/src/adversary/check.py
- /home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/transfer_Sb.json
- /home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_regional_heldout.csv
- /home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/ri_R4_vs_R3_heldout.csv
- Simulation scripts: /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/sim.py and /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/sim2.py
