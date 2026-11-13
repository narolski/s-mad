# Selection rule for the next method version, version 2 (DRAFT, not yet registered)

**Status: DRAFT.** This text binds nothing yet. It becomes binding only after (1) a pre-run check by the
independent reviewer and (2) the author's written yes to this text, recorded in FINAL. Binding happens at the
commit that removes "DRAFT" from this heading. Until then, no read may cite it as a rule.

**Supersedes** `prereg_draft.md` (version 1, commit 351a7f2). Version 1 stays in the folder unchanged, for the
record. Where the two differ, this version applies.

Drafted for the lead on 13 Nov 2026, about 20:45 CET by the machine clock. Sources applied:
- the pre-run check of version 1, `experiments/reviews/PRERUN_NEXT_SELECTION_RULE_20261113.md` (5092bc6; GO WITH
  FIXES; every fix applied, see "What changed from version 1");
- the post-result review of the adversary's stage-1a floors, `experiments/reviews/REVIEW_ADV_STAGE1A_20261113.md`
  (6f7c181);
- the stage-3 review and strategy answer, `experiments/reviews/REVIEW_ADV_STAGE3_STRATEGY_20261113.md` (93f4210),
  Part 2 (the core of this redraft);
- the partner-overlap audit, `experiments/DATA_builds/PARTNER_OVERLAP_AUDIT.md`;
- the floors page, `experiments/ADV_shortcut-floors/FLOORS.md`;
- the registrations of the challengers (listed in the inputs table below).

No network score, closed benchmark or sealed set was opened to write this draft. Only registrations, reviews,
floor summaries and the FS1 evaluation manifest's row counts were read.

## 1. What this rule can and cannot license

- **It can:** choose at most one arm, among a closed list, as the method of the next version, using development
  data only.
- **It cannot:** support any claim of generalisation. Passing it does not show that an arm detects morphs better
  in the wild, on other datasets or on other morphing tools. Only the sealed reads of the next version carry such
  claims.
- Every development number it uses is printed beside the shortcut floors of section 4(iv). Wording beyond
  "selected on development data" is allowed only where section 4(iv) allows it.

## 2. Scope

- The current method stays as the author froze it on 13 Nov: arm Sb (CLIP ViT-B/16 + LoRA), seeds 403-407, read
  once on MAD22.
- This rule chooses the method of the NEXT version. That version is read once on the sets that are still sealed
  (FRLL-Morphs, FEI, MorDIFF, the DiM families).
- MAD22 is a seen benchmark for the next version. No MAD22 number is ever an input to this rule.
- Every input is a registered read on development data.

## 3. Default, challengers and comparators

**Default:** Sb stays.

**Challengers** (closed list, in this order; the order matters in section 6):
1. Second morphing engine in training (SbFM; AB1 owner, `prereg_fm.md`). Comparator: the H100 Sb of AB1 at the same
   seed (408-412), paired.
2. GAN morphs with one-person renders as genuine examples (GX; GX1). Comparator: the H100 Sb of AB1 at the same seed
   (408-412), paired. The arm without render negatives (GXp) is a **control**, never a challenger.
3. Resize mixing at 224 (SbMR, then SbM; the resolution study (RZ1), wave 1). Comparator: RZ1's own refit Sb0 at the
   same seed, paired. Never AB1's Sb.
4. Larger input and interior crop (Sb512, then SbMR512, then Sbc; RZ1 waves 2b and 2a). Comparator: RZ1's Sb0 at the
   same seed, paired.
5. DINOv3 ViT-L/16 with the rule-fixed learning rate (Sb arm of the second-backbone study (BB2), block E3, seeds
   403-407). Comparator: the five H100 CLIP Sb fits of AB1 (seeds 408-412), **unpaired**.

**Not challengers (ablation rows only):**
- Border-crossed training (Sbx): its own registration says it cannot become the method, and the TT1 embargo applies.
- Same-person blends as genuine (SE; SE1): the A100 block already fails detection on 4 of 4 seeds, and SE1 section 2
  required an author clause first.
- GXp (control) and every plain arm (A0, AN, AM, AMR, Ac, A512, E3 A and B).
- Any combination of two challengers. A combination is a new arm. It needs its own registration and five seeds.

## 4. Criterion (a): detection

### Why criterion (a) changed

Version 1 selected on the FFHQ landmark_combined contrast alone. That set carries a resampling-history cue in the
image surround: surround-only statistics separate it at 0.942. The morphs' surround went through the generator's
own 1024 to 256 resize; the genuine photos went through E7 INTER_AREA. The set cannot be history-balanced for the
whole morph population (inverse-probability weights leave 8 effective morphs; the matched subset has 125 per
class). So a gain on landmark_combined alone could come from reading resampling history. Arms that change resize or
border handling are the most exposed. A gain on it alone must not select a method.

### The rule

A challenger meets criterion (a) only if (i), (ii) and, where it applies, (iii) all hold, and (iv) is printed.

**(i) landmark_combined gain (paired bar).**
- Paired arms: challenger AUC minus comparator AUC ≥ +0.03 on at least 4 of 5 seeds, within seed.
- RZ1 arms also: the median paired gain exceeds the largest same-seed refit difference |δ| of Sb0 against AB1's Sb
  on landmark_combined (RZ1 amendment 1).
- DINOv3 (unpaired): seed median ≥ 0.922 (AB1 H100 Sb median 0.892 + 0.03; Sb 408-412 = 0.894, 0.892, 0.906,
  0.888, 0.873), AND exact one-sided Mann-Whitney U ≤ 4 against the comparator's five seeds.
- Rows: the 1,000 landmark_combined morphs and 2,000 genuine photos of the evaluation pack, unchanged.

**(ii) No loss on the pipeline-matched development ladder.**
- Contrast: two-person morph (R4) against same-person morph (R3). Both sides went through the same aligner, the same
  morpher and the same storage, so resampling history cannot separate them.
- Rows: the OpenCV R4 and R3 rows of `floors/ri_R4_vs_R3_heldout.csv` (one row of each per host) restricted to the
  100 development hosts plus the 80 test hosts that are clean of development
  (`/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv`).
- Strata: blend-difference D quintiles by BD1's rule (quintile edges of log D over the pooled rows; strata with at
  least 10 of each class; weighted by n_pos × n_neg). D of an R4 or R3 row is the D of its host's S4 or S3 splice
  (`d_values.csv` column D), as in ADV amendment 3 item 6.
- Statistic: within-D AUC of the challenger minus within-D AUC of the comparator, on the same rows, per seed.
- Interval: person-component bootstrap (components of the full person graph, as the audit defines them; 2,000 draws,
  numpy default_rng(20261115)). Hosts are never resampled as independent units: development and test hosts share
  partners, and 171 of 191 test hosts share a component with a development host.
- **Pass:** paired difference ≥ −0.01 on at least 4 of 5 seeds.
- DINOv3 (unpaired): seed median of its within-D AUC ≥ the comparator's seed median − 0.01.
- Printed, not deciding:
  - the same read without the test hosts that are shape-linked to training negatives (the audit's 32; PR1
    amendment 5a prints an n = 11 linked-versus-clean comparison within the 80, so about 11 of them are among the 80;
    the exact list is pinned with the inputs). This matters for every arm that keeps Sb's S3 and S0 rows;
  - the 100 development hosts alone and the 80 clean test hosts alone;
  - the FaceMorpher R4 against R3 rows of the same hosts, unstratified (FaceMorpher has no splices and so no D).
    **For SbFM these rows are marked "seen engine"**: SbFM trained on FaceMorpher morphs, so the read is asymmetric.

**(iii) Gain within surround-matched subsets (arms that change resize or border handling).**
- Applies to every RZ1 arm (SbMR, SbM, Sb512, SbMR512, Sbc) and to any arm that changes border handling.
- Subset: `check.diff_on_matched` (1:1 greedy matching of morphs to genuine photos on the boosted-tree surround score,
  column `surround_gbt` of `floors/lcomb_regional_heldout.csv`; caliper 0.1 SD; default_rng(20261117)).
- **Pass:** paired landmark_combined gain on the matched rows ≥ +0.015 (half the full-set bar) on at least 4 of 5
  seeds, AND the seed-mean matched gain is at least half the seed-mean full-set gain.
- Fewer than 100 matched pairs: (iii) is "not read" and the arm cannot qualify.
- Printed beside it: the gain on `lcomb_bal` (125 per class; descriptive, labelled "do not cite as a test").
- Known limit: with 125-256 pairs the standard error of the gain is about 0.025. This test can miss a history-driven
  gain. It can also fail a real one.

**(iv) Floors printed beside every detection number.**
- Every number of (i), (ii) and (iii), per seed, is printed beside:
  - the **same-data transfer shortcut learner** (ADV prereg section 5.3: logistic regression and boosted trees on the
    hand-made statistics, fitted on the unique rows of that arm's own training list, applied to the evaluation rows);
  - the **in-distribution simple-cue floors** on the same rows: the all-cue ADV floor, the non-F27/non-BLEND floor,
    the surround floor and the face-box floor; for the ladder, the floor within D quintiles.
- Training lists: train_Sb for Sb, Sb0, SbM, SbMR, Sb512, SbMR512, Sbc and DINOv3 E3 Sb; train_SbFM for SbFM;
  GX's own manifest for GX. For RZ1 arms the learner sees the stored 512 frames; the arm's on-the-fly resampling
  cannot be reproduced (that would be new resampling code). This limit is printed beside each RZ1 number.
- Wording:
  - "beyond hand-made statistics trained on the same data" is allowed **only** if the network exceeds the transfer
    learner: the 2.5% bound of (network AUC − learner AUC), re-taken in the same person-component draws, is above 0
    on the seeds the arm's own registration requires;
  - "beyond hand-made statistics fitted on these rows" only if it exceeds the in-distribution floor by the ADV rule;
  - on landmark_combined the in-distribution "exceeds" test is predetermined (quick bar 0.986). "Within the ADV floor"
    there is never read as evidence of shortcut use;
  - the R4 against R3 floors are "simple morph-cue floors", not shortcut floors.
- (iv) adds no pass bar. A missing print means (a) is "not read", and the arm cannot qualify.

## 5. Criteria (b)-(f)

A challenger qualifies only if (a) and all of (b)-(f) hold.

**(b) Storage.** The rise in own-rule flags on stored genuine photos is at most the comparator's + 0.02 at both
storage sizes (fm61 and amsl112) on at least 4 of 5 seeds. The plain control of the same platform (AB1 A, RZ1 A0 or
A512, E3 A) must meet its own control bar. Storage evasion of morphs (H-new-1) must be falsified. DINOv3: medians.

**(c) Unseen genuine sources.** Mean own-rule flag share over the seven TT1 families (F̄): seed-mean difference
challenger minus comparator ≤ +0.02. DINOv3: median ≤ comparator median + 0.02. The own rule transfers on the NIST
mugshots (MEDS; TT-M1, person-bootstrap upper bound ≤ 10%) on at least 4 of 5 seeds.

**(d) Same-person blends and borders.**
- Development same-person splice (S3) flag share ≤ comparator's + 0.05 on at least 4 of 5 seeds.
- Flags on the border-blanked development camera photos ≤ comparator's + 0.01 on at least 4 of 5 seeds.
- Job-path check: both arms' border rows come from the same scoring path (fit job, or a rescoring job whose
  bit-identity gate passed). Rows labelled "other job" are not compared, and (d) is then "not read".
- DINOv3: medians, same margins.

**(e) Stability to the viewer's resize (RZ1 resize arms SbMR and SbM only).** κ_ho (largest change in own-rule flag
share under the four held-out test transforms; RZ1 amendment M2) ≤ 0.05 on at least 4 of 5 seeds, and κ over the
nine training kernels ≤ 0.05 on at least 4 of 5 seeds. Other arms: not applicable. No kernel cross table is made for
non-RZ1 arms (that would need resampling outside RZ1, which is the author's to allow).

**(f) Own registration.** Every guard of the challenger's registration is met, and its platform and training-fit
gates passed (for E3: the splice-fit gate on at least 4 of 5 seeds; for RZ1: provenance and the refit gate; for
rescoring jobs: the bit-identity gate).

**Counting rules (all criteria).**
- Five seeds per arm. "On at least 4 of 5" means 4 of 5 with five read seeds and 4 of 4 with four.
- A seed whose fit failed or gave non-finite scores counts as failing every criterion. The denominator stays 5.
- Three or fewer read seeds: "not read". A not-read arm is not a challenger.
- Margins are inclusive. Numbers are compared as printed by the reader, not rounded.

## 6. Choice among qualifiers

- None qualifies: Sb stays.
- One qualifies: it replaces Sb.
- Several qualify: the earliest in the list of section 3 is chosen, unless a later qualifier's seed-mean
  landmark_combined gain (DINOv3: median minus comparator median) exceeds the earliest's by at least 0.015.
  If two or more later arms do so, the one with the largest such gain is chosen.
- At most one arm is chosen. Every other arm is reported as an ablation row with all its reads.

## 7. Timing, pins and one application

- **Pins first.** Before any challenger tar is opened, every input row set and every floor file is committed and its
  sha256 is listed in a pins file in this folder. That includes: the ladder host list (100 development + 80 clean
  test hosts) and the shape-link list; the D values; the landmark_combined rows; the surround-matched subset ids; the
  `*_withinD.json` and `*_regional*` floor files (several are uncommitted today); the new within-D floor on the
  ladder subset; and the transfer-learner outputs for every training list used. The reader refuses to run if a pin
  fails. A criterion whose inputs were not pinned before the arm's tar was opened is "not read" for that arm.
- **Deadline.** An arm not read by 15 Nov 2026 18:00 CET is not a challenger. Its rows are labelled late.
- **Once.** The rule is applied once, after all challengers are read or the deadline passes. It is not re-run with
  changed rows, floors or margins.
- **Before binding.** An arm whose development scores were opened before this rule became binding is an ablation
  row only, unless the author rules otherwise in writing (question 2).

## 8. The read of the next version

Once, on the still-sealed sets, on the GPU model and software build that trained the chosen arm (WCSS H100 for every
listed challenger; never a rented A100), with the byte-identity gate on development rows first. The deciding measure
and its forms are those of the final protocol of the MAD22 read. MAD22 numbers of the next version are printed as
"seen during development".

## 9. Inputs per challenger today

"Yes" = rows are scored inside the fit job or a registered job. "Unknown" = not established from the files read.
No cluster state was checked for this draft; job states are as last written in the READMEs.

| Challenger | Fits / state | (a)(i) landmark_combined | (a)(ii) ladder R4 vs R3 (dev + 80) | (a)(iii) surround-matched | (a)(iv) transfer learner | (b) storage | (c) TT1 F̄ + MEDS | (d) S3 + border | (e) kernels | Still needed |
|---|---|---|---|---|---|---|---|---|---|---|
| SbFM (AB1 owner) | WCSS 6315597, 5 fits; state unknown | yes (ab1x_eval in fit) | yes (ab1x_eval); FaceMorpher rows "seen engine" | n/a | train_SbFM listed in ADV 5.3; not computed | yes (in fit) | **no**, for SbFM; AB1 Sb from RZ1 rescoring 6316319 | S3 yes; border: SbFM in fit, Sb only from rescoring 6314812 ("other job"; job path unknown) | n/a | rescoring job for TT1 + MEDS (about 1 H100-h, owner amendment, before any tar is opened); Sb border rows on a gated path |
| GX (GX1) | generation smoke 6315653 + arrays pending; training path (amendment 2) not written; 10 fits not submitted | yes (ab1_eval in fit) | yes (ab1_eval) | n/a | GX manifest not built; not computed | yes (in fit) | **no** | S3 yes; border **no** (ab1_eval has no border rows) | n/a | amendment 2 + its pre-run check; rescoring job for TT1, MEDS and border rows; GX learner after its manifest exists; readable by the deadline: unknown |
| SbMR, SbM (RZ1 wave 1) | WCSS 6316284 (35 tasks), behind smoke 6316283; refit yardstick 6316319 | yes (ab1x_eval, primary transform) | yes (ab1x_eval) | required | train_Sb, resampling not reproduced; not computed | yes | yes (TT1 + MEDS in fit) | yes (S3; border rows and Bd) | yes (9 + 4 held-out) | the transfer learner and the pinned inputs of section 7 only |
| Sbc (RZ1 wave 2a) | WCSS 6316285 (10 tasks); author's reading of the crop ruling pending (RZ1 M7) | yes | yes | required | as wave 1 | yes | yes | yes | n/a (no cross table) | author's crop ruling; as wave 1 |
| Sb512, SbMR512 (RZ1 wave 2b) | not queued (after the smoke's step rate, M6); SbMR512 dropped if over 7 h | yes | yes | required | as wave 1 | yes (control A512) | yes | yes | n/a | submission; readable by the deadline: uncertain (needs start by about 15 Nov 06:00); sealed sets as 512 frames: unknown (question 5) |
| DINOv3 E3 Sb (BB2) | WCSS 6313860 (15 fits); merged rescoring 6315676 behind it | yes (FS1 pack in fit) | yes (FS1 pack holds development and test ladder R4/R3, both engines) | n/a | train_Sb; not computed | via 6315676 (C2P) | TT1 via 6315676; MEDS: unknown (no WCSS MEDS job when the plan was written) | S3 yes; border-blanked development camera photos: **no** in the FS1 pack (unknown whether added); TT1 border references via 6315676 | n/a | MEDS job; border rows on a gated path; selection part (D-sel) replaced by this rule |

Common to all: the transfer learner (zero GPU, about 1 CPU-hour per training list), the within-D floor on the
ladder subset, and the commit and pins of section 7, all before any challenger tar is opened.

## 10. What changed from version 1

- Pre-run check fix 2: Sbx and SE dropped to ablation rows; GXp named a control.
- Fix 3: DINOv3 unpaired bar raised from median 0.904 to median ≥ 0.922 with Mann-Whitney U ≤ 4, against the AB1
  H100 CLIP Sb (not the FS1 CLIP Sb).
- Fix 4: counting rules and margins for (b)-(e): (c) seed-mean ≤ +0.02 and MEDS on 4 of 5; (d) S3 ≤ +0.05 and border
  ≤ +0.01 with the job-path check; (e) RZ1 resize arms only. (e) adds RZ1's binding held-out κ_ho beside v1's nine
  kernels, since a mix arm trained on the nine kernels is not tested by them.
- Fix 5: choice by list order unless a later qualifier exceeds by ≥ 0.015 (was: largest gain, tie band 0.005).
- Fix 6: failed or non-finite seeds fail every criterion; three or fewer read seeds = not read.
- Fix 7: RZ1 arms compare with their own Sb0, never AB1's Sb.
- Fix 8: late arms (not read by 15 Nov 18:00 CET) are not challengers; the rule is applied once.
- Fix 1: missing inputs listed per challenger (section 9); jobs to fill them need owner amendments before any tar is
  opened.
- Fixes 9 and 10: disclosures (section 11) and the binding clause (top of this file).
- New: criterion (a) rebuilt (section 4); the pins-first requirement (section 7); the licence statement (section 1).

## 11. Disclosures

- **Timing.** Written after: the 13 Nov reads of the CLIP arms (which fix the comparators' known levels, e.g. AB1 H100
  Sb landmark_combined 0.873-0.906); the adversary's stage-1a and stage-3 floors and both reviews; the AB1
  history-balanced reads (H-hb1 not read: 125 per class; H-hb1w not read: ESS 8); the partner-overlap audit. Written
  before any read of a challenger. The drafter opened no network score.
- **Margins.** +0.03 and the unpaired bar come from the owners' proposals and the 13 Nov seed spread (about
  0.02-0.04 AUC on landmark_combined). The ladder tolerance −0.01 and the matched-subset bar +0.015 are the strategy
  reviewer's and this draft's choices. Their false-fail rate for an arm equal to its comparator is not known. With
  between-arm seed spread near 0.013 (AB1 H-fm1 estimate) and about 180 hosts per side, an equal arm may fail
  (ii) on 4 of 5 seeds with a probability that is not small. The pre-run check should estimate it without opening
  challenger scores.
- **What the ladder measure is.** In-domain (FRGC and colorFERET, the training domain). Not saturated (networks near
  0.72-0.74 on test S4 against S3). The frozen candidate is at or below the in-distribution simple-cue floor there
  (0.754; 0.744 within D). It licenses at most "sensitivity to a second identity at matched blend strength", and only
  above the floors.
- **Partner sharing.** 99 of 191 test hosts have a development host as partner; 80 test hosts are clean of
  development; 32 test hosts are shape-linked to training negatives of every arm that keeps Sb's S3 and S0 rows.
  Intervals use person-component bootstrap.
- **Storage.** SbMR and SbMR512 train on shrink-and-enlarge; the mixR band excludes both storage sizes at 224 but lies
  within 7-9% of them at 512. A storage pass for those arms is not a held-out test of an unseen operation.
- **FRLL genuine photos** are scored in the frozen candidate's MAD22 read. They are not used here.
- **Seeds.** DINOv3 uses 403-407 (not fresh for DINOv3); the CLIP comparators use 408-412.
- **Volume.** SbFM (+6%) and GX (+8.8%) change training composition at fixed steps; no volume-matched control.

## 12. Open questions for the author (yes / no)

1. Do you approve this text, after its pre-run check, as the binding selection rule for the next version, recorded
   in FINAL?
2. Should every challenger read (SbFM, GX, RZ1, DINOv3 E3) wait until this rule is binding, with any arm read earlier
   kept as an ablation row only?
3. Do you approve one H100 rescoring job (about 1-2 GPU-hours, with the bit-identity gate) to supply the missing TT1,
   MEDS and border rows for SbFM and GX (and the AB1 Sb border rows on a gated path)?
4. Should the chosen arm be confirmed on five fresh seeds (413-417) before the next version is frozen, as RZ1's
   registration proposed (this would fall after 15 Nov)?
5. Are the sealed sets available as aligned 512 px frames, so that a 512-input or interior-crop arm can be read on
   them? (If no, Sb512, SbMR512 and Sbc are ablation rows only.)
