# DRAFT (for pre-run check): MS1 part 4, dilution against diversity (G2) and splice share (G3) on WCSS H100

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
- Driver `src/MS1/run_p4.sh` (`00679e0f…`) = `src/MS1/run.sh` with: arm list Sb|SbM3|Sb63|SbM3S (Sb63 →
  train_Sb.csv, default steps 3,938), default pack `pn1_pack_ms2.tar`, results folder `results/MS1P4`.
- Pack `/mnt/t7/smad_next/MS1/pn1_pack_ms2.tar` sha256 `79c2a7b883e8e8adb5860c9b84746ea26754e89159d49702e8b23ec4ad254f81`
  (14,871,592,960 bytes, 52,245 files; `build_pack_ms2.py` `c50f85f1…`): the part-2 pack plus train_SbM3S.csv and the
  CFD (831) and KDEF (140) frames; evaluation manifest `f7a5c98c7b2ccdd968108131c248f4a0e77d3c050f001e0ce0eaaacdeb3ac396`
  (43,337 rows).
- Smoke `src/MS1/wcss/ms1p4_smoke.sbatch` (`8d69cd10…`): 20 steps, 64 scoring rows, arms Sb63 and SbM3S, seed 403,
  through run_p4.sh; the fit array `src/MS1/wcss/ms1p4_fit.sbatch` (`e61eceb6…`) is queued only after the smoke log
  shows MS1P4_SMOKE_DONE.
- Reader `src/MS1/ms1_read_p4.py` (`e2cb1e0a…`; tested on mock scores only), run once.

## 4.2 G2: dilution against diversity

Statement: SbM3's CFD gain (part 2, P1-S) comes from seeing each FRGC / colorFERET image 0.63 times as often, not from
the third source. Statistic: CFD own-rule genuine flag rate (831 images), per network.
- Positive control (the P1-S effect must replicate on the H100): median(SbM3) ≤ 0.5 × median(Sb) AND exact one-sided
  Mann-Whitney p ≤ 0.025 (SbM3 lower); otherwise G2 is "uninformative (positive control not met)". Floor: median(Sb) <
  0.02 → "untestable (floor)".
- **Dilution supported** if median(Sb63) ≤ 0.5 × median(Sb) AND p ≤ 0.025 (Sb63 lower). **Falsified** (dilution does not
  explain it) if median(Sb63) ≥ 0.8 × median(Sb) OR p > 0.5. Otherwise "inconclusive, no claim". Ties half; margins
  inclusive.
- Printed: rank-AUC memorisation (part 3b rules: per-kind table, count of kinds below 0.5, per-seed paired differences
  against Sb on identical row sets; Sb and Sb63 share rows), TT1 F, MS1 FFHQ hold-out flags, KDEF flags.

## 4.3 G3: splice share

Statement: the S4 cost of SbM3 (development S4 against S0/S3 AUC 0.891 → 0.881, part-2 review F5) comes from the smaller
splice share. Statistic: AUC of development S4 (100) against development S0 + S3 (200), per network.
- Control (the cost must replicate on the H100): SbM3's AUC below Sb's on ≥ 4 of 5 seeds; otherwise "uninformative".
- **Supported** if median AUC(SbM3S) ≥ median AUC(Sb) − 0.005 AND median CFD own-rule flags(SbM3S) ≤ 0.01.
  **Falsified** if AUC(SbM3S) ≤ AUC(SbM3) + 0.002 on ≥ 4 of 5 seeds. Otherwise "inconclusive, no claim".

## 4.4 Guards (each new arm Sb63, SbM3, SbM3S against Sb, same seeds)

- **Own-rule miss guard, attack pool from an unseen pipeline** (FFHQ landmark_combined orig, 1,000; no arm trained on
  its morph pipeline): holds if median miss(arm) ≤ median miss(Sb) + 0.05 AND the per-seed excess is > 0.10 on at most
  1 seed. A failing guard is printed with the arm's verdict ("at a cost in unseen-pipeline misses"); it does not change
  G2 or G3, which are mechanism tests. Parent-sex strata: not available (FFHQ parents carry no sex labels).
- **Printed within-sex guards (part 3b note):** per seed, signed ρ(CFD logit, Feminine) within women and within men, paired
  against Sb, with the flagged counts beside it; sex-stratified CFD own-rule flags.

## 4.5 Seed rules, deadline, cost

- A seed is read for G2 (G3) only if all its arms finished with finite logits and a verified tar; 4 or 5 read seeds →
  the rules above (4 against 4: smallest one-sided p 1/70); 3 or fewer → "not read". A non-finite run is never rerun;
  an infrastructure failure once, unchanged, same partition. No seed chosen on a score.
- Deadline: fits finished and fetched by 14 Nov 2026 15:00 CET are read.
- Cost: about 1.1 H100-h per fit (6,250 steps) and about 0.75 for Sb63: about 21 H100-h, free (WCSS); jobs sort behind
  the method-relevant ones (dispatcher queue).
- Disclosure: written after the part-2 read, its review and part 3 (H-mem supported by mean logit and rank AUC; it
  does not separate dilution from regularisation). The L40S values of Sb and SbM3 are known; the H100 fits are new.
