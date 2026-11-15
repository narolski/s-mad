# DRAFT, superseded by prereg.md part 4 (for pre-run check): MS1 part 4, dilution against diversity (G2) and splice share (G3) on WCSS H100

Not registered until copied into `prereg.md` at a commit before the smoke and before any part-4 fit. Lead's
instruction, 13 Nov 14:10: the two drafted training experiments go to WCSS, all fits and all scoring of each on the
H100 in the fit job, with their own comparators there; the own-rule miss guard on the unseen-pipeline attack pool and
the printed within-sex guards in the registration; a pre-run check; one smoke through the real path; then the
submission files to the dispatcher queue. Source texts: `prereg_gpu_hypotheses_draft.md` G2 and G3; reviews
REVIEW_MS1_20261113.md (H-new-2, H-new-3), REVIEW_MS1_PART3_20261113.md, REVIEW_MS1_PART3B_20261113.md.

## 4.1 Arms, fits, platform

- Arms (all new fits, one platform; none of the L40S fits is used): **Sb** (train_Sb, 6,250 steps), **Sb63** (train_Sb
  at 3,938 = 0.63 × 6,250 steps, the per-image exposure of FRGC / colorFERET rows in SbM3), **SbM3** (train_SbM3, 6,250),
  **SbM3S** (train_SbM3S, 6,250: SbM3 with 97 of its 124 spliced-morph rows entered twice before the per-stratum
  balance, so the splice share of attack rows is 0.1026 = Sb's; `src/MS1/mkmanifest_s4.py`, manifest
  `eaefef80c3a2d2167bbcd65e9da9815347af4c42f7803576736bb2c89ec731e5`, 13,414 rows).
- G2 uses Sb, Sb63, SbM3; G3 uses Sb, SbM3, SbM3S. Sb and SbM3 are shared: **20 fits** (4 arms × seeds 403-407), not 30.
- Platform: WCSS H100 (lem-gpu-short, `gpu:hopper:1`), `~/dmenv` (torch 2.11.0+cu128, timm 1.0.30; supports sm_90;
  printed by the smoke with `torch.cuda.get_arch_list()`), one job per fit (array 0-19%6), seed by seed. Training and
  scoring commands unchanged (train.py of the AD4 pack, PN1 flags; pn1_score.py with TF32 on) except `--steps` for Sb63.
  Every score of part 4 is made in its fit job on the H100 (evaluation manifest includes CFD and KDEF); nothing is
  compared with L40S or A100 scores.
- Driver `src/MS1/run_p4.sh` (`db75e5b6b6184a1cb3bd8990b8449d5115c364a8a66a769e4634a48f3a09a9b1`) = `src/MS1/run.sh` with: arm list Sb|SbM3|Sb63|SbM3S (Sb63 →
  train_Sb.csv, default steps 3,938), default pack `pn1_pack_ms2.tar`, results folder `results/MS1P4`, and a line writing the training-manifest sha256
  into the result (`manifest.txt`). DGX smoke of run_p4.sh (Sb63, 20 steps, 64 rows) passed; the reader's configuration
  check parsed its tar.
- Pack `/mnt/t7/smad_next/MS1/pn1_pack_ms2.tar` sha256 `79c2a7b883e8e8adb5860c9b84746ea26754e89159d49702e8b23ec4ad254f81`
  (14,871,592,960 bytes, 52,245 files; `build_pack_ms2.py` `c50f85f1…`): the part-2 pack plus train_SbM3S.csv and the
  CFD (831) and KDEF (140) frames; evaluation manifest `f7a5c98c7b2ccdd968108131c248f4a0e77d3c050f001e0ce0eaaacdeb3ac396`
  (43,337 rows).
- Smoke `src/MS1/wcss/ms1p4_smoke.sbatch` (`2ccc82180d8d85cc658355f9b90f19ddbee2c8ead27db1d34985a2377dcb1a2d`): 20 steps, 64 scoring rows, arms Sb63 and SbM3S, seed 403,
  through run_p4.sh; the fit array `src/MS1/wcss/ms1p4_fit.sbatch` (`e0b19fccaa00fea87287b37675bec220c9fc8f553de65dddc0a48e387a06c44f`) is queued only after the smoke log
  shows MS1P4_SMOKE_DONE.
- Reader `src/MS1/ms1_read_p4.py` (`d5b7985a33e7869d31da42c95b789bec5dbca50ba28bb6278b352e51be7ec091`; tested on mock scores only), run once.

## 4.2 G2: dilution against diversity

Statement: SbM3's CFD gain (part 2, P1-S) comes from seeing each FRGC / colorFERET image 0.63 times as often, not from
the third source. Statistic: CFD own-rule genuine flag rate (831 images), per network.
- Positive control (the P1-S effect must replicate on the H100): median(SbM3) ≤ 0.5 × median(Sb) AND exact one-sided
  Mann-Whitney p ≤ 0.025 (SbM3 lower); otherwise G2 is "uninformative (positive control not met)". Floor: median(Sb) <
  0.02 → "untestable (floor)".
- **Supported** if median(Sb63) ≤ 0.5 × median(Sb) AND p ≤ 0.025 (Sb63 lower). **Falsified** if median(Sb63) ≥ 0.8 ×
  median(Sb) OR p > 0.5. Otherwise "inconclusive, no claim". Ties half; margins inclusive. A floor hit on the control
  reads "untestable (floor)".
- What each outcome can show (pre-run check F3): Sb63 is the first 3,938 steps of Sb's same-seed run (constant LR, last
  checkpoint), so it changes per-image exposure AND total optimisation length, and the CFD flag is the own rule
  (logit > 0), whose calibration also changes with steps. "Supported" means "stopping Sb at matched per-image exposure
  reproduces at least half of SbM3's CFD gain without a third source"; it does not separate per-image exposure from
  total optimisation length. "Falsified" means "matched exposure by truncation does not reproduce it". (3,938 steps is
  0.8% above the exact 0.625 exposure of 3,908.)
- Printed: the fraction explained (Sb − Sb63) / (Sb − SbM3) of median CFD flags; per-seed paired Sb63 − Sb (same seed
  and data order); a scale-free CFD read (AUC of CFD against the development AF0 camera photos, and CFD mean logit
  minus the camera-photo mean); the training-row margin per arm (median logit of negative and attack training rows);
  rank-AUC memorisation (part 3b rules: per-kind table, count of kinds below 0.5, per-seed paired differences against
  Sb); TT1 F, MS1 FFHQ hold-out flags, KDEF flags.

## 4.3 G3: splice share

Statement: the S4 cost of SbM3 (development S4 against S0/S3 AUC 0.891 → 0.881, part-2 review F5) comes from the smaller
splice share. Statistic: AUC of development S4 (100) against development S0 + S3 (200), per network.
- Control: AUC(SbM3) < AUC(Sb) on at least n−1 of n read seeds (n = 5) or n of n (n = 4), AND Δ = median AUC(Sb) −
  median AUC(SbM3) ≥ 0.006; otherwise "uninformative (cost not replicated)".
- **Supported** if median AUC(SbM3S) − median AUC(SbM3) ≥ 0.5 Δ AND median AUC(SbM3S) ≥ median AUC(Sb) − 0.005.
  **Falsified** if median AUC(SbM3S) − median AUC(SbM3) ≤ 0.25 Δ. Supported is checked first; otherwise "inconclusive,
  no claim". Printed beside the verdict, not part of it: median CFD own-rule flags of SbM3S (≤ 0.01 or not), and the
  FFHQ landmark_combined miss of SbM3S against SbM3. (From the L40S SDs: P(falsified | no recovery) ≈ 0.8,
  P(falsified | full recovery) ≈ 0.04, P(supported | full recovery) ≈ 0.85; on the L40S the control held: AUC .891 vs
  .881, SbM3 lower on 5 of 5.)
- Disclosed side change of SbM3S: inside FRGC / colorFERET native strata the attack rows that make room for the doubled
  S4 rows are u50 (2,711 → 2,502 rows) and R4 (435 → 386); per-image S4 exposure 661 (Sb 662, SbM3 413).

## 4.4 Guards (each new arm Sb63, SbM3, SbM3S against Sb, same seeds)

- **Own-rule miss guard, attack pool from an unseen pipeline** (FFHQ landmark_combined orig, 1,000; no arm trained on
  its morph pipeline): holds if median miss(arm) ≤ median miss(Sb) + 0.05 AND the per-seed excess is > 0.10 on at most
  1 seed. A failing guard is printed with the arm's verdict ("at a cost in unseen-pipeline misses"); it does not change
  G2 or G3, which are mechanism tests. Parent-sex strata: not available (FFHQ parents carry no sex labels). Known in
  advance: on the L40S SbM3 failed this guard (miss median 0.585 against Sb 0.271); SbM3S is also printed against SbM3
  (its comparator for source familiarity).
- **Printed within-sex guards (part 3b note):** per seed, signed ρ(CFD logit, Feminine) within women and within men, paired
  against Sb, with the flagged counts beside it; sex-stratified CFD own-rule flags.

## 4.5 Seed rules, deadline, cost

- A seed is read for G2 (G3) only if all its arms finished with finite logits, a verified tar and a passing
  configuration check (per tar: steps 3,938 for Sb63 and 6,250 otherwise and limit 0 in task_info.txt; the training
  manifest sha256 in manifest.txt equal to the registered one; gpu.txt naming an H100; env.txt identical across tars);
  a failed check is "config mismatch", treated as an infrastructure failure. A timeout or NODE_FAIL is an
  infrastructure failure. 4 or 5 read seeds → the rules above (5 against 5: "supported" needs U ≥ 23 of 25; 4 against 4:
  U = 16 of 16); 3 or fewer → "not read". A non-finite run is never rerun; an infrastructure failure once, unchanged,
  same partition. No seed chosen on a score. If dilution explains only about half the gain, the likely G2 result is
  "inconclusive".
- Deadline: fits finished and fetched by 14 Nov 2026 15:00 CET are read; fewer than 4 read seeds then is reported as
  "not read (deadline)", with no extension without an amendment.
- The fit array fails fast unless `~/dmenv` is torch 2.11.0+cu128 / timm 1.0.30 with sm_90 (shared environment); the
  smoke asserts the same. The dispatcher places the array behind the method-critical arrays.
- Cost: about 1.1 H100-h per fit (6,250 steps) and about 0.75 for Sb63: about 21 H100-h, free (WCSS); jobs sort behind
  the method-relevant ones (dispatcher queue).
- Disclosure: written after the part-2 read, its review and part 3 (H-mem supported by mean logit and rank AUC; it
  does not separate dilution from regularisation). The L40S values of Sb and SbM3 are known; the H100 fits are new. The
  G2 floor (0.02, against P1-S's 0.03) was set after seeing Sb's L40S CFD median 0.035 and seed 407 at 0.018.
- Pre-run check: experiment-reviewer (opus), GO WITH FIXES (F1-F8), all applied (G3 rule, per-tar configuration check,
  G2 interpretation and prints, floor label, paired prints, guard notes, power and deadline text, environment asserts);
  the reader was mock-tested on every G3 branch (uninformative, inconclusive, falsified, supported) and G2.
