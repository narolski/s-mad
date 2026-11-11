# AG5: existing StyleGAN3 sets under the common ladder rules (post hoc)

Written 11 Nov 2026 before this owner opened any per-image score file. **Post hoc: outcomes are known
in aggregate** (A41 h3: no row at AUC ≥ 0.65 for morphs vs renders; X4 0.42–0.52). This page only
re-labels existing scores under `11_AUDIT_PLAN.md`.

- **Hypothesis (plain words):** on StyleGAN3 morphs, released and re-implemented detectors separate
  generator output from camera photos (R0 → R2) but not morphs from one-identity renders (R2 → R4).
- **Data (no new images, no rescoring):**
  - R0 = FRLL camera photos (`frll_bona`, 204, registered eval frames). Different person pool and
    capture from the CASIA-based renders: cross-pool, stated as such.
  - R2 = H3 one-identity renders G(w+_C) of a third CASIA person (`h3_bona`, orig, 423); second R2 =
    X4 spread-matched renders (`a37spread`, orig).
  - R4 = H3 morphs G((w+_A + w+_B)/2) (`h3_sg3`, orig, 423). `pp` variant descriptive.
  - R1 and R3 do not exist for these sets (no history-matched photo, no same-person StyleGAN3 mix).
  Score files: `smadcvpr_runs/A12_scored/{A12BR,A12REL}/…/scores_{h3sg3,eval}.npz`,
  `smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz`, `/mnt/t7/smad_heldout/a41g/a41g_out/x4/…/scores_a37spread.npz`.
- **Rows:** the 12 primary method rows of A41 h3 (M1, M2, M3, M3L, M4, M5, M6, M8, M8O R×d0 recipes;
  SelfMAD release own preprocessing; MADation ViT-B/16 and ViT-L/14 releases). One network per result:
  every recipe seed is read separately; a row summary gives the count of seeds per label.
- **Metric:** AUC and d′ per step; shares relative to d′(R0 vs R4). Bootstrap: H3 pairs resampled
  (morph and render of one pair share the weight, the A41 unit), FRLL persons resampled independently
  (pigeonhole person draw), B = 10,000.
- **Verdict rules:** main verdict on R2 vs R4 exactly as in `11_AUDIT_PLAN.md`. Because R1 and R3 are
  missing, "R0 → R2 share" is the single step R0 → R2; the side study on R3 is not available.
- **Gates:** G-a not applicable to off-benchmark sets (printed as such). G-b from the h3sg3 manifest
  potency (morphs verifying against both contributors at FMR 1e-3), already recorded in A41.
- **Falsifier:** none (post hoc); labels printed whichever way they fall.
- **Stop rule and budget:** CPU only, minutes.
- **Command:** `python3 src/AG5/ag5_read.py`.
- **Pre-run review:** not run (zero-compute re-read).
