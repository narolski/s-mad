# AD1 step 1: MorDIFF ladder, post hoc re-read of A43 scores

Written 11 Nov 2026 before any per-image score file was opened by this owner. **Post hoc: outcomes are
partly known.** The A43 aggregate table (`mambamorph-code/smadcvpr/results/A43/a43_read.md`) was read
before this page; it already prints AUCs for several of the contrasts below (e.g. ViT-B/16 R0m 0.487,
SelfMAD R2m 0.290). This step only re-labels existing scores under `11_AUDIT_PLAN.md`.

- **Hypothesis (plain words):** for each released detector, the MorDIFF separation is carried by the
  processing steps (R0 → R2) rather than by morphing (R2 → R4).
- **Data (no new images, no rescoring):** A43 per-image score files
  `/mnt/t7/smad_heldout/a43/a43_out/a43/<release>/<mode>/scores_a43.npz` (manifest
  `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`, sha ce3a264a…), plus the registered eval scores
  `smadcvpr_runs/A12_scored/A12REL/<release>/scores_eval.npz` and
  `experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` for the E7 rows.
  Ladder mapping:
  - R0 = FRLL camera photo in the MorDIFF cell (`mordiff_bona`, registered frames, 204).
    Descriptive alternative R0s = arm E (photo through DiffAE's aligner, A43 storage path).
  - R1 = E7 MorDIFF pool (`mordiff`/`resmatch`, 204), only where the same detector and same
    preprocessing scored it.
  - R2 = D20 (one-photo reconstruction at the matched 20 steps, 204). D (100 steps) descriptive.
  - R3 = C20 (same-person mix, neutral + smiling of one person, 102). Expression confound: the R3
    images mix two expressions; R4 B20 morphs keep one expression per pair (100 neutral, 100 smiling).
  - R4 = B20 (our same-pair DiffAE morphs, 20 steps, 200). Benchmark R4 = published MorDIFF (arm A /
    registered `mordiff` rows, 200 sampled).
  - Bridge = A vs B20.
- **Detectors:** MADation ViT-B/16 release, MADation ViT-L/14 release (score_noTTA), SelfMAD release
  with its own preprocessing (primary) and in our pipeline (descriptive). FE / FS variants descriptive.
  MixFaceNet-MAD: added only if the A46 RGB-only scorer runs unchanged on the A43 images.
- **Metric:** AUC per step (higher rung = positive class) and d′ = √2·Φ⁻¹(AUC); share = step d′ /
  d′(R0 vs benchmark R4 = A). 95% intervals from the two-way (pigeonhole) person bootstrap of
  `a41_read.py` (Owen 2007: persons ~ Multinomial(n, 1/n); photo weight = its person's count, morph
  weight = product of its two contributors' counts), B = 10,000, same draw for all arms. Folded AUC =
  0.5 + |AUC − 0.5|, bounds from the replicates. The reader is checked by reproducing A43's printed
  point AUCs and intervals.
- **Verdict rules (fixed in `11_AUDIT_PLAN.md`, applied unchanged):** main verdict on R2 vs R4;
  side study on R3 vs R4 and R2 vs R3, including "twin artefact, cell invalid" (AUC < 0.40 and UB < 0.5).
- **Gates:** G-a from the recorded published EERs (cell "not reproduced, descriptive" if off by > 3
  points). G-b computed from the A43 manifest glint cosines before scores are opened (oracle AUC
  morph vs twin with min cosine to the two source photos; morphs verifying against both contributors
  at the A43 FMR 1e-3 threshold; twins verifying against A). Negative control twin(A, A′) vs twin(A′, A)
  not available (one twin per person). G-c (probe) needs features: not done in this step.
- **Falsifier:** none in the strict sense (post hoc); the labels are printed whichever way they fall.
- **Stop rule and budget:** CPU only, minutes. No GPU.
- **Command:** `python3 src/AD1/ad1_read.py` (smoke on 8 rows per arm first).
- **Pre-run review:** not run (zero-compute re-read; lead to decide).
