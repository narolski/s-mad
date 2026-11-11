# AG5 result: StyleGAN3 sets under the common ladder rules (post hoc)

Owner run, 11 Nov 2026. **Post hoc, outcome known in aggregate** (A41 h3, A41g X4). No new image, no
rescoring. Code `src/AG5/ag5_read.py` (CPU, about 3 min). Outputs `ag5_ladder.json`, `ag5_ladder.csv`
(one line per network).

## Sources and mapping

- R0 = FRLL camera photos (`frll_bona`, 204, registered eval frames; eval.csv sha 86d055d3…).
- R2 = H3 one-identity renders G(w+_C), C a third CASIA person (`h3_bona`, orig, 423). Second R2 =
  A37 X4 latent-spread-matched renders of contributor A (`a37spread`, orig, 423).
- R4 = H3 morphs G((w+_A + w+_B)/2) (`h3_sg3`, orig, 423). R1 and R3 do not exist for these sets.
- Scores: `smadcvpr_runs/A12_scored/A12BR/<run>/scores_{h3sg3,eval}_es.npz` (the registered es.pt
  checkpoint of each primary recipe network, as in A41; no last-checkpoint X4 scores exist),
  `A12REL/<release>/scores_{h3sg3,eval}.npz`, `smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz` +
  `experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz`,
  `/mnt/t7/smad_heldout/a41g/a41g_out/x4/<net>/…/scores_a37spread.npz` (MixFaceNet:
  `a46/a41g_out/a46x4/…`). Manifest sha256 checked in every file.
- Cross-check: the release rows reproduce A41 h3 (ViT-B/16 0.554, ViT-L/14 0.427, SelfMAD own 0.353)
  and A41g X4 (0.42–0.45).
- Bootstrap: H3 pairs resampled (morph, its render and its X4 render share the pair weight), FRLL
  persons resampled independently; B = 10,000. Shares relative to d′(R0 vs R4).

## Gates

- G-a: not applicable (off-benchmark sets).
- **G-b fails**: only 47.99% of the orig H3 morphs verify against both contributors at FMR 1e-3
  (`h3sg3_stats.json`; bar 70%). So the "reads morphing" branch could not be credited even if reached;
  the "reads the benchmark" branch does not depend on it. A41's potent subset (morphs that verify,
  203) gave the same AUCs within 0.02 (a41_h3.md).
- G-c: not done.

## Results per method row (12 primary rows + MixFaceNet release, descriptive)

Ranges over the networks of a row. "No sep." = networks whose R0-vs-R4 AUC lower bound is ≤ 0.5
(they do not separate StyleGAN3 morphs from camera photos at all; verdict not meaningful).

| Row | nets | R0 vs R4 | R0 → R2 | **R2 vs R4** | X4: R2x4 vs R4 | share R0→R2 | share R0→R2x4 | Verdict, H3 renders | Verdict, X4 | No sep. |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 Inception-MAD R×d0 | 5 | 0.99 | 0.96–0.97 | 0.55–0.56 | 0.44–0.45 | 0.79–0.82 | 0.97–1.05 | reads the benchmark 5/5 | RB 5/5 | 0 |
| M2 MorphHRNet-style R×d0 | 5 | 0.35–0.70 | 0.28–0.59 | 0.56–0.61 | 0.44–0.49 | −0.46–0.42 | 1.29–1.59 | RB 2, mixed 1 | RB 3 | 2 |
| M3 MADation ViT-B/16 R×d0 | 8 | 0.91–0.98 | 0.92–0.99 | 0.38–0.50 | 0.45–0.47 | 1.01–1.15 | 1.03–1.15 | RB 8/8 | RB 8/8 | 0 |
| M3L MADation ViT-L/14 R×d0 | 5 | 0.73–0.88 | 0.90–0.95 | 0.36–0.45 | 0.43–0.45 | 1.33–2.09 | 1.08–1.32 | RB 5/5 | RB 5/5 | 0 |
| M4 SelfMAD-style R×d0b | 5 | 0.18–0.53 | 0.16–0.47 | 0.53–0.57 | 0.50–0.53 | — | — | — | — | 5 |
| M5 PW-MAD R×d0 | 8 | 0.84–0.98 | 0.77–0.98 | 0.53–0.60 | 0.44–0.47 | 0.73–1.10 | 0.98–1.16 | RB 8/8 | RB 8/8 | 0 |
| M6 OrthoMAD R×d0 | 5 | 0.52–0.74 | 0.42–0.63 | 0.57–0.58 | 0.45–0.48 | 0.01–0.52 | 1.16–1.34 | RB 4 | RB 4 | 1 |
| M8 MixFaceNet-MAD R×d0 | 5 | 0.42–0.97 | 0.38–0.94 | 0.55–0.57 | 0.43–0.47 | 0.71–0.83 | 1.01–1.12 | RB 4 | RB 4 | 1 |
| M8O MixFaceNet official code O×d0 | 5 | 0.65–0.81 | 0.61–0.78 | 0.53–0.58 | 0.44–0.47 | 0.61–0.85 | 1.10–1.34 | RB 5/5 | RB 5/5 | 0 |
| SelfMAD release, own preprocessing | 1 | 0.999 [0.998, 1.000] | 1.000 | **0.353 [0.325, 0.379]** | 0.447 [0.419, 0.475] | 1.00 [1.00, 1.00] | 1.00 | RB | RB | 0 |
| MADation ViT-B/16 release | 1 | 0.975 [0.963, 0.985] | 0.947 [0.929, 0.964] | **0.554 [0.526, 0.582]** | 0.423 [0.395, 0.451] | 0.83 [0.75, 0.91] | 1.03 [0.94, 1.14] | RB | RB | 0 |
| MADation ViT-L/14 release | 1 | 0.849 [0.819, 0.878] | 0.904 [0.880, 0.927] | **0.427 [0.399, 0.455]** | 0.445 [0.417, 0.472] | 1.26 [1.13, 1.42] | 1.13 [1.02, 1.27] | RB | RB | 0 |
| MixFaceNet-MAD release (desc., our frames) | 1 | 0.689 [0.642, 0.734] | 0.588 [0.538, 0.637] | 0.581 [0.555, 0.608] | 0.446 [0.419, 0.472] | 0.45 [0.23, 0.63] | 1.43 [1.20, 1.75] | RB (folded rule) | RB | 0 |

RB = "reads the benchmark". Every RB above fires on both arms of the rule except where the share is
undefined or small (M2, M6 s2–s5, MixFaceNet release on H3 renders), where it fires through "R2 vs R4
folded below 0.60 with upper bound below 0.65". No network in any row reaches the "reads morphing"
bar (maximum R2 vs R4 over all 55 networks: 0.609, M2 s1). The one "mixed" network is M2 s1 (R0 vs R4
0.648, R2 vs R4 0.609 [0.58, 0.64], share 0.02).

Side study: not available (no same-person StyleGAN3 mix). The rule "twin artefact, cell invalid" has
no R3 to act on; note only that X4 renders score above the morphs in every separating network (AUC
0.42–0.49), as A37 / A41g reported.

## Verdict summary (post hoc; G-b failed, so read as an absence result)

Of the 51 recipe networks, 42 separate StyleGAN3 morphs from camera photos; 41 of them "read the
benchmark" and one (M2 s1) is "mixed". The other 9 (all 5 M4, two M2, one M6, one M8) do not separate
the cell at all. The three primary releases (and the MixFaceNet release, descriptive) all "read the
benchmark". So 10 of 12 rows read the benchmark in every separating network; M2 does in 2 of its 3 separating
networks (one mixed); M4 has no separating network. With the latent-spread-matched X4 renders as R2 the
label is the same for every separating network.

## Caveats and what is not verifiable

- R0 is a different pool (FRLL studio photos, 1350 px JPEG) from the CASIA-based renders and morphs,
  so R0 → R2 includes source, capture and resolution differences as well as the generator. A
  CASIA-camera R0 scored by these networks does not exist.
- G-b fails (morph potency 48%). An identity reading could be absent because half the morphs do not
  carry both identities; A41's potent-subset numbers argue against that, but no G-c probe was run here.
- Recipe networks use the es.pt checkpoint (registered A36/A41 choice), not the last checkpoint the
  new protocol prescribes; last-checkpoint X4 scores do not exist.
- The MixFaceNet release row uses our 512-frame path, not its MTCNN crop (suspended branch).
