# StyleGAN3 ladder re-read of the existing H3 and X4 sets (AG5): full record

Owner: hypothesis-owner agent (Opus), 11 Nov 2026. `result.md` is the short verdict; this README is the
full record.

Terms. H3 = our StyleGAN3 diagnostic set (A35): morph = G((w+_A + w+_B)/2) of two CASIA-WebFace
contributors, against a single-identity render G(w+_C) of a third CASIA person. X4 = the A37 renders of
contributor A matched to the morphs' latent spread (`a37spread`). FRLL = Face Research Lab London photos
(the camera photos of every benchmark). AUC = area under the ROC curve. d′ = √2·Φ⁻¹(AUC). Rungs as in
`11_AUDIT_PLAN.md`: R0 camera photo, R2 one-identity render ("pipeline only"), R4 morph; R1 and R3 do not
exist for these sets. G-b = twin-validity gate (morphs must verify against both contributors in ≥ 70%).

## 1. Question and current answer

Status: **finished** 11 Nov 2026 (about 14:50 CET); independent review the same day: "corrections
required (wording only; numbers accepted)". Post hoc: the aggregate H3 and X4 results (A41 h3, A41g X4)
were known before.

Question: on StyleGAN3 morphs, do the 12 primary method rows (9 re-implemented recipes with all their
seeds, 3 released networks) separate morphs from one-identity renders, or only generator output from
camera photos? Answer (review's corrected wording): **no network of 55 separates two-identity morphs from
one-identity renders** (maximum AUC 0.61; 0.42–0.53 against spread-matched renders). In 33 of the 42
recipe networks that separate the morphs from FRLL photos (95% lower bound of the d′ share ≥ 0.5; 36 by
point estimate), and in all three releases, one-identity renders are separated from those photos at
least half as strongly; that step mixes generator, source pool and resolution. This is an **absence
result with power not demonstrated**: only 48% of the H3 morphs verify against both contributors.

## 2. Timeline

- 11 Nov ~14:22: task received (with AD1 and C1–C4).
- ~14:36: located the per-image scores: registered H3 and eval scores per network
  (`/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/...`, file pins listed in
  `smadcvpr/results/A36/a36_read_own.json`), X4 scores (`/mnt/t7/smad_heldout/a41g/a41g_out/x4/...`), the
  12 primary rows from `smadcvpr/results/A41/a41_h3.md` and `A36_networks.tsv`.
- ~14:37: wrote `prereg.md` before opening any per-image score.
- ~14:40: wrote `src/AG5/ag5_read.py`; smoke (`--smoke`, 8 items per set, B = 200) passed; full run
  about 3 min CPU (moved to the background by the tool's 120 s limit; exit 0).
- ~14:55: wrote `result.md`; a first count error (45 of 51 instead of 42 of 51 separating networks) was
  found and corrected in `result.md` before hand-back (section 7).
- 11 Nov afternoon: independent review → wording corrections (section 7).
- 11 Nov ~17:30: documentation pass: `src/AG5/ag5_count.py` re-reads `ag5_ladder.json` to verify the
  review's 33 of 42 count (`ag5_count.json`); input hashes in `inputs_sha256.txt`.

## 3. Data

No image generated, nothing rescored. sha256 of all 170 input files: `inputs_sha256.txt` in this folder.

| Item | Path | n | Origin |
|---|---|---|---|
| H3 manifest | `/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv` (sha 4b29a7c9…) | 1,692 rows (423 pairs × morph/render × orig/pp) | A35 (WCSS H100) |
| H3 potency stats | `/mnt/t7/smad_heldout/h3_sg3/data/h3sg3_stats.json` (sha 9cb2995c…) | — | A35 finalise |
| X4 manifest | `/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv` (sha 28bde1ef…) | 846 (423 orig, 423 pp) | A37 re-decodes (WCSS) |
| Network list | `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv` (sha 51a80e93…) | 51 primary recipe networks | A36 |
| Recipe scores | `.../smadcvpr_runs/A12_scored/A12BR/<run>/scores_h3sg3_es.npz`, `scores_eval_es.npz` (the registered es.pt checkpoint, as A41 used) | 51 × 2 | A12-BR scoring |
| Release scores | `.../A12_scored/A12REL/{madation_vitb16,madation_vitl14,mixfacenet_mad_smdd}/scores_{h3sg3,eval}.npz`; SelfMAD own: `.../smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz` + `.../experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` | — | A12REL, A36, A32 |
| X4 scores | `/mnt/t7/smad_heldout/a41g/a41g_out/x4/<run>/nets/scores_a37spread.npz`, `.../x4/<release>/<mode>/scores_a37spread.npz`; MixFaceNet release: `/mnt/t7/smad_heldout/a46/a41g_out/a46x4/mixfacenet_mad_smdd/rel/scores_a37spread.npz` | 55 | A41g / A46 |
| Eval manifest | `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` (sha 86d055d3…) | `frll_bona`/`orig`: 204 | registered |

Sets used: R0 = 204 FRLL photos (registered frames); R2 = 423 H3 renders (orig); R2x4 = 423 X4 renders
(orig); R4 = 423 H3 morphs (orig). The `pp` variants were not used (descriptive in A41). Nothing dropped.
Outputs: `ag5_ladder.json` (420e2793…), `ag5_ladder.csv` (c49685e9…, one line per network),
`ag5_count.json` (054679…).

## 4. Code

| Script | sha256 | Job |
|---|---|---|
| `/home/narolski/smad-next/src/AG5/ag5_read.py` | 1d9a4ffa… | per network: AUCs, d′ shares, verdicts (H3 renders and X4 renders as R2); writes `ag5_ladder.{json,csv}` |
| `/home/narolski/smad-next/src/AG5/ag5_count.py` | 6942bd92… | documentation check: counts of separating networks and of "half or more" (point and lower bound) |

`ag5_read.py` imports `wauc`, `dprime`, `Draw` from `/home/narolski/smad-next/src/AD1/ad1_read.py`.
Environment: spark venv (Python 3.12.3, numpy 1.26.4, scipy 1.17.1), CPU. Bootstrap B = 10,000: H3 pairs
resampled with multinomial weights, seed [20261111, 5, 1] (a morph, its H3 render and its X4 render share
the pair weight — A41's unit), FRLL persons resampled independently with the pigeonhole draw, seed
[20261111, 5, 2]. Score keys: `score` for recipes and SelfMAD own, `score_noTTA` for MADation releases,
MixFaceNet release auto (`score_noTTA` if present). Manifest sha256 inside every score file checked.

## 5. Results

Per network (all in `ag5_ladder.csv`). Ranges over the networks of a row; "no sep." = networks whose
R0-vs-R4 AUC lower bound is ≤ 0.5.

| Row | nets | R0 vs R4 | R0 → R2 | **R2 vs R4** | X4 vs R4 | share R0→R2 | share R0→X4 | no sep. |
|---|---|---|---|---|---|---|---|---|
| M1 Inception-MAD R×d0 | 5 | 0.99 | 0.96–0.97 | 0.55–0.56 | 0.44–0.45 | 0.79–0.82 | 0.97–1.05 | 0 |
| M2 MorphHRNet-style R×d0 | 5 | 0.35–0.70 | 0.28–0.59 | 0.56–0.61 | 0.44–0.49 | −0.46–0.42 | 1.29–1.59 | 2 |
| M3 MADation ViT-B/16 R×d0 | 8 | 0.91–0.98 | 0.92–0.99 | 0.38–0.50 | 0.45–0.47 | 1.01–1.15 | 1.03–1.15 | 0 |
| M3L MADation ViT-L/14 R×d0 | 5 | 0.73–0.88 | 0.90–0.95 | 0.36–0.45 | 0.43–0.45 | 1.33–2.09 | 1.08–1.32 | 0 |
| M4 SelfMAD-style R×d0b | 5 | 0.18–0.53 | 0.16–0.47 | 0.53–0.57 | 0.50–0.53 | — | — | 5 |
| M5 PW-MAD R×d0 | 8 | 0.84–0.98 | 0.77–0.98 | 0.53–0.60 | 0.44–0.47 | 0.73–1.10 | 0.98–1.16 | 0 |
| M6 OrthoMAD R×d0 | 5 | 0.52–0.74 | 0.42–0.63 | 0.57–0.58 | 0.45–0.48 | 0.01–0.52 | 1.16–1.34 | 1 |
| M8 MixFaceNet-MAD R×d0 | 5 | 0.42–0.97 | 0.38–0.94 | 0.55–0.57 | 0.43–0.47 | 0.71–0.83 | 1.01–1.12 | 1 |
| M8O MixFaceNet official code O×d0 | 5 | 0.65–0.81 | 0.61–0.78 | 0.53–0.58 | 0.44–0.47 | 0.61–0.85 | 1.10–1.34 | 0 |
| SelfMAD release, own prep. | 1 | 0.999 [0.998, 1.000] | 1.000 | **0.353 [0.325, 0.379]** | 0.447 [0.419, 0.475] | 1.00 | 1.00 | 0 |
| MADation ViT-B/16 release | 1 | 0.975 [0.963, 0.985] | 0.947 [0.929, 0.964] | **0.554 [0.526, 0.582]** | 0.423 [0.395, 0.451] | 0.83 [0.75, 0.91] | 1.03 [0.94, 1.14] | 0 |
| MADation ViT-L/14 release | 1 | 0.849 [0.819, 0.878] | 0.904 [0.880, 0.927] | **0.427 [0.399, 0.455]** | 0.445 [0.417, 0.472] | 1.26 [1.13, 1.42] | 1.13 [1.02, 1.27] | 0 |
| MixFaceNet-MAD release (desc., our frames) | 1 | 0.689 [0.642, 0.734] | 0.588 [0.538, 0.637] | 0.581 [0.555, 0.608] | 0.446 [0.419, 0.472] | 0.45 [0.23, 0.63] | 1.43 [1.20, 1.75] | 0 |

Counts (`ag5_count.json`): 42 of 51 recipe networks separate morphs from FRLL photos (the 9 that do not:
all 5 M4, M2 s3 and s5, M6 s5, M8 s3). Of the 42, the d′ share R0 → R2 is ≥ 0.5 in 36 by point estimate
and in **33 by its 95% lower bound** (the review's count); all three primary releases meet both; the
MixFaceNet release does not (0.45). Maximum R2 vs R4 over all 55 networks: 0.609 (M2 s1). Labels under
the fixed rule: "reads the benchmark" in 41 of the 42 separating recipe networks and in the three
releases, "mixed" in M2 s1 — **this label count is withdrawn as a summary (see section 7)**.

Gates: G-a not applicable (off-benchmark sets). **G-b fails**: 47.99% of the orig H3 morphs verify against
both contributors at FMR 1e-3 (threshold 0.2394; `h3sg3_stats.json`); A41's potent subset (203 morphs
that verify) gave AUCs within 0.02 of the full set (`smadcvpr/results/A41/a41_h3.md`). G-c not done.

Review-only number (not recomputed): the released MADation FE ViT-L/14, which reads the mixing step on
MorDIFF, scores H3 morphs vs renders at 0.505 (no transfer).

## 6. Checks

Verified: release rows reproduce A41 h3 (ViT-B/16 0.554, ViT-L/14 0.427, SelfMAD own 0.353) and A41g X4
(0.42–0.45); recipe per-seed values sit inside A41's pooled row values; manifest sha256 in every score
file equals the manifest's; the reviewer recomputed the numbers from the per-image files and accepted
them. Not verified: last-checkpoint behaviour (only es.pt scores exist for X4); a CASIA camera-photo R0
(none scored); the potent-subset version of the X4 contrast; the MixFaceNet release's own MTCNN crop
(suspended branch, not used).

## 7. Dead ends and failures

- Counting error before hand-back: my first `result.md` draft said "45 of 51 recipe networks plus the
  three releases" separate the cell and "the remaining 6"; the correct numbers are 42 and 9. Fixed in
  `result.md` the same afternoon (an arithmetic slip in summing the per-row counts).
- The full `ag5_read.py` run exceeded the tool's 120 s foreground limit and was moved to the background;
  it completed normally (exit 0).
- Statements corrected or withdrawn by the independent review (11 Nov):
  1. "41 of 42 separating recipe networks (and all releases) read the benchmark" and "10 of 12 rows read
     the benchmark in every separating network" → **withdrawn**. Corrected: "No network of 55 separates
     two-identity morphs from one-identity renders (max 0.61; 0.42–0.53 vs spread-matched). In 33 of the
     42 recipe networks that separate the morphs from FRLL photos, and in the three releases, one-identity
     renders are separated from those photos at least half as strongly; that step mixes generator, source
     pool and resolution." Reason: the "reads the benchmark" label fires mostly through the folded-AUC
     arm (R2 vs R4 near 0.5), which also fires for networks that read nothing; and R0 is a different
     photo pool, so the R0 → R2 step is not a pure generator step.
  2. Any reading that implies identity is absent "because the detectors cannot read it" → absence
     result; power not demonstrated (G-b 48%).
  3. d′ shares in prose (values up to 2.09) → drop; quote AUCs.

## 8. Observations and ideas

- X4 renders (spread-matched) score *above* the morphs in every separating network (0.42–0.49), while the
  morphs score slightly above the H3 third-person renders in most CNN recipe networks (0.53–0.61) but
  below them in M3, M3L, the ViT-L/14 release and SelfMAD own (0.35–0.50): the morph's latent position,
  not identity, decides the direction (as A37 reported).
- The FRLL camera pool is the least matched pool for CASIA-based renders; a CASIA or FFHQ camera R0
  would separate the generator step from the source-pool step.
- M4 (SelfMAD-style recipe) ranks StyleGAN3 output *below* FRLL photos in all five seeds (0.18–0.53).

## 9. Open items and next steps

- A same-person StyleGAN3 mix (R3) does not exist; the GAN causal test is AG1 (MIPGAN, x86).
- A camera-photo pool matched to the CASIA sources; potent-subset X4 contrast; last-checkpoint scores.

## 10. Handover state

Nothing running. Compute: about 3 CPU-minutes, 0 GPU-hours, 0 USD. No file needed from /tmp or a
scratchpad (the run's console output was only progress lines; all numbers are in `ag5_ladder.json`).

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
sha256sum -c <(sed 's/ /  /' experiments/AG5/inputs_sha256.txt)
$PY -I src/AG5/ag5_read.py --smoke          # 8 items per set, prints only
$PY -I src/AG5/ag5_read.py                  # -> experiments/AG5/ag5_ladder.{json,csv} (about 3 min)
python3 src/AG5/ag5_count.py                # -> experiments/AG5/ag5_count.json
```
