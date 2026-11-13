# Selection rule for the next method version, version 3 (DRAFT, not yet registered)

**Status: DRAFT.** This text binds nothing yet. It becomes binding only after the author's written yes to this
text, recorded in FINAL. Binding happens at the commit that removes "DRAFT" from this heading.

**Fixed now (section 7, clause 1).** The margins, the list and the order of this text are fixed at the git commit
that adds this file under this name. That commit is made before anyone in the lead chain sees the frozen
candidate's MAD22 result. If the author's yes comes later, no text may change except fixes named in the pre-run
check of this version.

**Supersedes** `prereg_draft_v2.md` (3c2b9d5) and `prereg_draft.md` (351a7f2). Both stay unchanged, for the record.
Where they differ, this version applies.

Drafted for the lead on 13 Nov 2026, about 20:55 CET by the machine clock. Sources applied:
- the pre-run check of version 2, `experiments/reviews/PRERUN_NEXT_SELECTION_RULE_V2_20261113.md` (3d14793; GO WITH
  FIXES; every finding applied with its replacement text, see section 10), with the lead's decisions on its options;
- the pre-run check of version 1, `experiments/reviews/PRERUN_NEXT_SELECTION_RULE_20261113.md` (5092bc6);
- the adversary reviews `REVIEW_ADV_STAGE1A_20261113.md` (6f7c181) and `REVIEW_ADV_STAGE3_STRATEGY_20261113.md`
  (93f4210), Part 2;
- the partner-overlap audit `experiments/DATA_builds/PARTNER_OVERLAP_AUDIT.md`; the floors page
  `experiments/ADV_shortcut-floors/FLOORS.md`; the challengers' registrations (section 9).

No network score, closed benchmark or sealed set was opened to write this draft.

## 1. What this rule can and cannot license

- **It can:** choose at most one arm, among a closed list, as the method of the next version, using development
  data only.
- **It cannot:** support any claim of generalisation. Passing it does not show that an arm detects morphs better
  in the wild, on other datasets or on other morphing tools. Only the sealed reads of the next version carry such
  claims.
- Selection numbers are selection-biased. They are never reported as the chosen arm's effect (section 7).

## 2. Scope

- The current method stays as the author froze it on 13 Nov: arm Sb (CLIP ViT-B/16 + LoRA), seeds 403-407, read
  once on MAD22.
- This rule chooses the method of the NEXT version. That version is read once on the sets that are still sealed
  (FRLL-Morphs, FEI, MorDIFF, the DiM families).
- MAD22 is a seen benchmark for the next version. No MAD22 number is ever an input to this rule.
- Every input is a registered read on development data.

## 3. Default, challengers and comparators

**Default:** Sb stays.

**Challengers** (closed, flattened list; the order decides the choice in section 6):
1. Second morphing engine in training (SbFM; AB1 owner, `prereg_fm.md`).
2. GAN morphs with one-person renders as genuine examples (GX; GX1).
3. Resize mixing with an intermediate size at 224 (SbMR; the resolution study (RZ1), wave 1).
4. Resize mixing at 224 (SbM; RZ1 wave 1).
5. 512-px input (Sb512; RZ1 wave 2b).
6. 512-px input with resize mixing (SbMR512; RZ1 wave 2b). **Cannot qualify** unless a kernel test for it is
   registered before its read (it trains on mixed resizing and has no cross table; section 5(e)).
7. Interior crop (Sbc; RZ1 wave 2a).
8. DINOv3 ViT-L/16 with the rule-fixed learning rate (Sb arm of the second-backbone study (BB2), block E3, seeds
   403-407).

**Comparators:**
- SbFM, GX: the H100 Sb of AB1 at the same seed (408-412), paired.
- RZ1 arms: RZ1's own refit Sb0 at the same seed, paired. Never AB1's Sb.
- DINOv3: the five H100 CLIP Sb fits of AB1 (408-412), unpaired. Per-seed DINOv3 value minus the comparator's
  seed mean; intervals by a seeds × components bootstrap (resample the five DINOv3 seeds and the five comparator
  seeds with replacement, and the person components, in the same draw).

**Not challengers (ablation rows only):** border-crossed training (Sbx; its registration says it cannot become the
method, TT1 embargo); same-person blends as genuine (SE; fails detection on 4 of 4 A100 seeds, author clause
required); GXp (control); every plain arm (A0, AN, AM, AMR, Ac, A512, E3 A and B); any combination of two challengers
(a new arm with its own registration and five seeds).

## 4. Criterion (a): detection

### Why criterion (a) changed

Version 1 selected on the FFHQ landmark_combined contrast alone. That set carries a resampling-history cue in the
image surround: surround-only statistics separate it at 0.942. It cannot be history-balanced for the whole morph
population (inverse-probability weights leave 8 effective morphs). A gain on it alone could come from reading
resampling history, so it must not select a method. Every arm can change how much the network leans on that cue:
RZ1 arms change resizing, and SbFM and GX change training composition. So (iii) applies to every challenger.

### The rule

A challenger meets criterion (a) only if (i), (ii) and (iii) all hold, and the prints of (iv) exist.

Notation: d_s = challenger minus comparator on seed s (paired arms: same seed; DINOv3: its seed s minus the
comparator's five-seed mean). "Seed-mean" = the mean of d_s over the read seeds.

**(i) landmark_combined gain.**
- **Pass:** seed-mean gain ≥ +0.025, AND d_s > 0 on at least 4 of 5 seeds.
- RZ1 arms also: the seed-mean gain exceeds the largest same-seed refit difference |δ| of Sb0 against AB1's Sb on
  landmark_combined (RZ1 amendment 1).
- Rows: the 1,000 landmark_combined morphs and 2,000 genuine photos of the evaluation pack, unchanged.

**(ii) No loss on the pipeline-matched development ladder.**
- Contrast: two-person morph (R4) against same-person morph (R3). Both sides went through the same aligner, morpher
  and storage, so resampling history cannot separate them.
- Rows: the OpenCV R4 and R3 rows of `floors/ri_R4_vs_R3_heldout.csv` restricted to the 100 development hosts plus
  the 80 test hosts that are clean of development (`/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv`):
  360 rows.
- Strata: blend-difference D quintiles by BD1's rule (strata with at least 10 of each class; weighted by
  n_pos × n_neg). **The quintile edges of log D are taken over the 360 subset rows.** D of an R4 or R3 row is the D of
  its host's S4 or S3 splice (BD1 `d_values.csv` column D). Coverage (share of rows in strata that count) is printed.
- Statistic: within-D AUC difference d_s.
- **Bootstrap unit:** the `component` column of `floors/ri_R4_vs_R3_heldout.csv` (110 evaluation-pool person
  components). 2,000 draws, numpy default_rng(20261115); the same draws for all seeds and for network-minus-floor.
- **Pass:** seed-mean within-D difference ≥ −0.02, AND no seed below −0.06.
- Printed: the 95% person-component bootstrap interval of the seed-mean difference (the same draws for all seeds).
- Printed, not deciding:
  - the same read without the test hosts that are shape-linked to training negatives (the audit's 32; the host list
    is built and pinned first, section 7);
  - the 100 development hosts alone and the 80 clean test hosts alone;
  - the FaceMorpher R4 against R3 rows of the same hosts, unstratified (FaceMorpher has no splices and so no D).
    **For SbFM these rows are marked "seen engine"**.

**(iii) Gain within the surround-matched subset (every challenger).**
- **Subset:** 1:1 greedy matching of morphs to genuine photos on the logit of `surround_gbt`
  (`floors/lcomb_regional_heldout.csv`), caliper 0.1 SD, default_rng(20261117); 360 pairs; ids pinned.
- **Known limit:** surround-balanced only (surround floor 0.504 on these rows); the face-box floor is 0.949 on these
  rows, so history in the face interior is not removed.
- **Pass:** seed-mean matched gain ≥ +0.015, AND ≥ half the seed-mean full-set gain of (i).
- Printed beside it: the gain on `lcomb_bal` (125 per class; descriptive, "do not cite as a test").

**(iv) Floors printed beside every detection number.**
- Every number of (i), (ii) and (iii), per seed, is printed beside:
  - the **same-data transfer shortcut learner** (ADV prereg section 5.3), from **per-row held-out scores** on the
    landmark_combined rows, the 360 ladder rows and the 360 matched pairs. The adversary writes and pins one file per
    training list before any read: train_Sb (for Sb0, SbMR, SbM, Sb512, SbMR512, Sbc and DINOv3 E3 Sb, and for the
    comparators), train_SbFM, and GX's list once its manifest exists. The existing `transfer_*.json` summaries (one
    AUC per contrast, no rows) are not enough;
  - the **in-distribution simple-cue floors** on the same rows: all-cue ADV floor, non-F27/non-BLEND floor, surround
    floor, face-box floor; for the ladder, the floor within D quintiles on the 360 rows.
- Wording:
  - "beyond hand-made statistics trained on the same data" is allowed **only** if the network exceeds the transfer
    learner: the 2.5% bound of (network AUC − learner AUC), re-taken in the same person-component draws, is above 0
    on at least 4 of 5 seeds;
  - **for SbM, SbMR and SbMR512** (on-the-fly resampling the learner cannot reproduce) that wording is not allowed;
    use "beyond hand-made statistics trained on the stored frames of the same list";
  - "beyond hand-made statistics fitted on these rows" only if the network exceeds the in-distribution floor by the
    ADV rule on at least 4 of 5 seeds;
  - on landmark_combined the in-distribution "exceeds" test is predetermined (quick bar 0.986); "within the ADV
    floor" there is never read as evidence of shortcut use;
  - R4 against R3 floors are "simple morph-cue floors", not shortcut floors.
- (iv) adds no pass bar. A missing print means (a) is "not read", and the arm cannot qualify.

## 5. Criteria (b)-(f)

A challenger qualifies only if (a) and all of (b)-(f) hold. For DINOv3, d_s is defined as in section 4 and the
same counts apply.

**(b) Storage.** The rise in own-rule flags on stored genuine photos: d_s ≤ +0.02 at both storage sizes (fm61 and
amsl112) on at least 4 of 5 seeds. The plain control of the same platform (AB1 A, RZ1 A0 or A512, E3 A) meets its
own control bar. Storage evasion of morphs (H-new-1) is falsified.

**(c) Unseen genuine sources.** Mean own-rule flag share over the seven TT1 families (F̄): seed-mean d ≤ +0.02. The
own rule transfers on the NIST mugshots (MEDS; TT-M1, person-bootstrap upper bound ≤ 10%) on at least 4 of 5 seeds.

**(d) Same-person blends and borders.**
- Development same-person splice (S3) flag share: d_s ≤ +0.05 on at least 4 of 5 seeds.
- Border-blanked development camera photos: d_s ≤ +0.01 on at least 4 of 5 seeds.
- Job-path check: both arms' border rows come from the same scoring path (fit job, or a rescoring job whose
  bit-identity gate passed). Otherwise (d) is "not read".

**(e) Stability to the viewer's resize (resize-mixing arms).** SbMR and SbM: κ_ho (RZ1 amendment M2, four held-out
test transforms) ≤ 0.05 and κ over the nine training kernels ≤ 0.05, each on at least 4 of 5 seeds. SbMR512 has no
cross table: it cannot qualify unless a kernel test for it is registered before its read. Other arms: not
applicable. No cross table is made for non-RZ1 arms (resampling outside RZ1 is the author's to allow).

**(f) Own registration.** Every guard of the challenger's registration is met, and its platform and training-fit
gates passed (E3: splice-fit gate on at least 4 of 5 seeds; RZ1: provenance and refit gate; rescoring jobs: the
bit-identity gate).

**Counting rules (all criteria).**
- Five seeds per arm. "On at least 4 of 5" means 4 of 5 with five read seeds and 4 of 4 with four.
- A seed whose fit failed or gave non-finite scores counts as failing every criterion; the denominator stays 5.
- Three or fewer read seeds: "not read". A not-read arm is not a challenger.
- Margins are inclusive. Numbers are compared as printed by the reader, not rounded.

## 6. Choice among qualifiers

- None qualifies: Sb stays.
- Several qualify: the earliest in the list of section 3 is chosen (1 SbFM, 2 GX, 3 SbMR, 4 SbM, 5 Sb512, 6 SbMR512,
  7 Sbc, 8 DINOv3). There is no tie-break by gain.
- The chosen arm then goes to the fresh-seed confirmation (section 7). Every other arm is reported as an ablation row
  with all its reads.

## 7. Safeguards, timing, pins and one application

- **Clause 1 (fixed before MAD22 is seen).** The margins, list and order of this text are fixed at the git commit
  that adds this file, before anyone in the lead chain sees the frozen candidate's MAD22 result. If the author's yes
  comes later, no text may change except fixes named in the pre-run check of this version.
- **Clause 2 (selection bias and fresh seeds).** Selection numbers are selection-biased and are never reported as the
  chosen arm's effect. The chosen arm is confirmed on fresh seeds 413-417 (RZ1 m6) with the same rule, against its
  comparator at the same fresh seeds, before freeze. If it fails, Sb stays.
- **Pins first.** Before any challenger tar is opened, every input row set and every floor file is committed and its
  sha256 listed in a pins file in this folder, from a clean tree (the uncommitted change in the ADV prereg and the
  failing `run_floors.py` pin are resolved first). That includes: the 360-row ladder subset and its D values; the
  32 shape-linked test hosts as a host list (today only counts exist in `partner_overlap_addendum.json`); the
  landmark_combined rows; the 360 matched-pair ids; the within-D floor on the 360 ladder rows (not computed yet);
  the `*_withinD.json` and `*_regional*` floor files; and the per-row transfer-learner files of section 4(iv). The
  reader refuses to run if a pin fails. A criterion whose inputs were not pinned before the arm's tar was opened is
  "not read" for that arm.
- **Deadline.** Read by the deadline = all fit and rescoring tars landed and hash-verified by 15 Nov 2026 18:00 CET,
  whenever the read itself happens. The jobs supplying each arm's inputs are listed and committed now (section 9).
  An arm is "not read" only for a listed reason (deadline, infrastructure failure, missing seeds), and that reason
  is reported.
- **Once.** The rule is applied once. It is not re-run with changed rows, floors or margins.
- **Before binding.** An arm whose development scores were opened before this rule became binding is an ablation
  row only, unless the author rules otherwise in writing.

## 8. The read of the next version

- Once, on the still-sealed sets, on the GPU model and software build that trained the chosen arm (WCSS H100 for
  every listed challenger; never a rented A100), with the byte-identity gate on development rows first.
- The deciding measure and forms are those of the final protocol of the MAD22 read.
- One network per reported number; per-seed mean ± SD; no ensembles.
- MAD22 numbers of the next version are printed as "seen during development".

## 9. Inputs per challenger today

"Yes" = rows are scored inside the fit job or a registered job. "Unknown" = not established from the files read.
Job states are as last written in the READMEs; no cluster was checked. All three evaluation manifests (ab1_eval,
ab1x_eval, FS1 pn1_eval) hold the 582 R4/R3 ladder rows and the 3,000 landmark_combined rows (pre-run check v2).

| # | Challenger | Supplying jobs | (a)(i), (ii), (iii) rows | (a)(iv) per-row learner | (b) storage | (c) TT1 F̄ + MEDS | (d) S3 + border | (e) kernels | Can qualify today? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SbFM | fits WCSS 6315597; AB1 Sb fits; RZ1 rescoring 6316319 (AB1 Sb TT1, MEDS) | yes (ab1x_eval) | train_SbFM: summary only (`transfer_SbFM.json`); per-row file needed | yes | **no** for SbFM | S3 yes; border: AB1 Sb only from rescoring 6314812 ("other job") | n/a | **No**: needs the H100 rescoring job (question 2) and Sb border rows on a gated path |
| 2 | GX | generation 6315653, 6315654, 6315655; training amendment 2 not written; 10 fits not submitted | yes (ab1_eval) | GX manifest not built | yes | **no** | S3 yes; border **no** | n/a | **No**: manifest, amendment 2, rescoring job (question 2); deadline unknown |
| 3 | SbMR | wave 1 WCSS 6316284 behind smoke 6316283; refit 6316319 | yes (ab1x_eval) | train_Sb: summary only; per-row file needed | yes | yes | yes | yes (9 + 4 held-out) | **Yes**, once the learner files and pins exist |
| 4 | SbM | as SbMR | yes | as SbMR | yes | yes | yes | yes | **Yes**, as SbMR |
| 5 | Sb512 | wave 2b not queued (after the smoke's step rate, M6) | yes | as SbMR | yes (control A512) | yes | yes | n/a | Only if queued and landed by the deadline, and if sealed sets exist as 512 frames (question 3) |
| 6 | SbMR512 | wave 2b; dropped if the projected fit exceeds 7 h | yes | as SbMR | yes | yes | yes | **no cross table** | **No**, unless a kernel test is registered before its read |
| 7 | Sbc | wave 2a WCSS 6316285 | yes | as SbMR | yes | yes | yes | n/a | Only after the author's crop ruling (question 4), and if sealed sets exist as 512 frames |
| 8 | DINOv3 E3 Sb | fits WCSS 6313860; merged rescoring 6315676 | yes (FS1 pack) | train_Sb: as SbMR | via 6315676 | TT1 via 6315676; MEDS unknown | S3 yes; border-blanked camera photos **no** | n/a | **No**: (d) not read without border rows; MEDS unknown |

So today only SbMR and SbM have every input apart from the per-row learner files and the pins.

## 10. What changed from version 2 (pre-run check v2 findings)

1. (iv) uses per-row learner scores written and pinned by the adversary; section 9 updated.
2. (iii) subset defined once, by the reviewer's replacement text (360 pairs; known limit stated).
3. Seed-mean rules: (i) seed-mean ≥ +0.025 and d_s > 0 on 4 of 5 (lead's choice); (ii) seed-mean ≥ −0.02 and no seed
   below −0.06, interval printed; (iii) seed-mean ≥ +0.015 and ≥ half the full-set gain. Simulated rates in
   section 11.
4. Bootstrap unit = the `component` column of `floors/ri_R4_vs_R3_heldout.csv`; D edges over the 360 rows; coverage
   printed.
5. DINOv3 on the same seed-mean rules (seeds × components bootstrap); (iii) for every challenger.
6. Choice by flattened list order only; no tie-break by gain.
7. Wording for SbM, SbMR, SbMR512 restricted; "required seeds" = 4 of 5.
8. Clauses 1 and 2 in section 7; the fresh-seed confirmation is a rule; section 8 adds one network per number,
   mean ± SD, no ensembles.
9. Deadline = tars landed and hash-verified; "not read" only for listed reasons.
10. Missing inputs listed for pins: shape-link host list, within-D floor on 360 rows, clean tree.
11. Arms that cannot qualify today are named; SbMR512 excluded unless a kernel test is registered.

## 11. Disclosures

- **Timing.** Written after: the 13 Nov reads of the CLIP arms (comparator levels known, e.g. AB1 H100 Sb
  landmark_combined 0.873-0.906); the adversary's floors, transfer summaries and both reviews; the AB1
  history-balanced reads (not read: 125 per class; ESS 8); the partner-overlap audit; the pre-run check of v2.
  Written before any read of a challenger and before the frozen candidate's MAD22 result was seen by the drafter.
  The drafter opened no network score.
- **Power of the rule (pre-run check v2, simulation).** Per-seed difference d_s = Δ + τ (shared rows) + noise of two
  independent fits with seed SD σ; 200,000 draws; scripts in `experiments/reviews/scripts_selection_rule/`.

  | Criterion | What is tested | Rule of v2 | Rule of this version |
  |---|---|---|---|
  | (ii) ladder, σ 0.015-0.025, τ 0-0.02 | equal arm fails | 35-64% | 3-32% |
  | (ii) ladder | arm with a true −0.03 loss passes | 0-10% | 14-27% |
  | (i) landmark_combined | true +0.03 arm passes | 19-28% | 65-74% |
  | (i) landmark_combined | equal arm passes | ≤ 0.2% | ≤ 2% |
  | (iii) matched | equal arm passes | 1-18% | 6-31% |
  | (iii) matched | true +0.03 arm passes | 46-65% | 69-94% |
  | All of (a) | true +0.03 arm with an equal ladder qualifies | about 3-18% | about 0.3-0.65 |

  The rates are for paired arms. The DINOv3 route under the same seed-mean rules was not simulated. The looser (ii)
  lets an arm with a true −0.03 ladder loss pass 14-27% of the time.
- **What the ladder measure is.** In-domain (FRGC and colorFERET). Not saturated (networks near 0.72-0.74 on test
  S4 against S3). The frozen candidate is at or below the in-distribution simple-cue floor there (0.754; 0.744
  within D). It licenses at most "sensitivity to a second identity at matched blend strength", and only above the
  floors.
- **Matched subset.** Surround-balanced only; face-box floor 0.949 and all-cue floor 0.945 on its rows.
- **Partner sharing.** 99 of 191 test hosts have a development host as partner; 80 test hosts are clean of
  development; 32 test hosts are shape-linked to training negatives of every arm that keeps Sb's S3 and S0 rows.
- **Storage.** SbMR and SbMR512 train on shrink-and-enlarge; the mixR band excludes both storage sizes at 224 but
  lies within 7-9% of them at 512. A storage pass for those arms is not a held-out test of an unseen operation.
- **FRLL genuine photos** are scored in the frozen candidate's MAD22 read. They are not used here.
- **Seeds.** DINOv3 uses 403-407 (not fresh for DINOv3); the CLIP comparators use 408-412; the confirmation uses
  413-417 and falls after 15 Nov.
- **Volume.** SbFM (+6%) and GX (+8.8%) change training composition at fixed steps; no volume-matched control.

## 12. Open questions for the author (yes / no)

1. Do you approve this text as the binding selection rule for the next version, recorded in FINAL?
2. Do you approve one H100 rescoring job (about 1-2 GPU-hours, with the bit-identity gate) to supply the missing TT1,
   MEDS and border rows for SbFM and GX (and the AB1 Sb border rows on a gated path)?
3. Are the sealed sets available as aligned 512 px frames, so that a 512-input or interior-crop arm can be read on
   them? (If no, Sb512 and Sbc are ablation rows only.)
4. Do you rule that the 224 interior crops (wave 2a, Sbc) fall within your ruling on native resolution (RZ1 M7)?
