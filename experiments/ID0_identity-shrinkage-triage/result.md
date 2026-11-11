# Identity-shrinkage triage: how average is a morph, and what is the ceiling [ID0] — result

Owner run, 11 Nov 2026, finished 18:20 CET. Pre-registration `prereg.md` (written before any statistic). Full
record, commands, hashes, dead ends: `README.md`. Code `src/ID0/`; features and logs `/mnt/t7/smad_next/ID0/`;
per-arm results `arm_<arm>.json`, `contrasts_<arm>.csv`; falsifier table `verdicts.json`; benchmark pair
similarity `bench_similarity.json`. AUC = area under the ROC curve, second-named group positive; [a, b] = 95%
two-way person bootstrap (a41_read.Draw, B = 2,000). ISS = the pre-registered identity-subspace shrinkage score
(higher = closer to the average face). Facts only.

## Fit (genuine photos only)

776 FRGC + colorFERET persons (FERET 710, FRGC 66), 1,395 photos; 471 persons with ≥ 2 photos (619 within-person
degrees of freedom), only 47 with ≥ 2 capture sessions, so "within-person" is mostly within-session variation.
87 `is_val` persons excluded; no AR1 host/partner, no FRLL person, no morph or render. 16 AR1 hosts drop out
because host or partner is `is_val` (8 AR1 hosts are themselves `is_val`; AR1 does not filter them).

## Main table (ISS score)

| Arm | native vs E7 control (4 primary families) | AR1 OpenCV R2w vs R4 | MorDIFF D20 vs B20 | StyleGAN3 render vs morph | dose m0→m0.5 (Page p; means) |
|---|---|---|---|---|---|
| Landmark, exact shapes | not applicable (no image) | 0.687 [0.650, 0.720] (shape of R2w = R3) | — | — | 4e-234; rising |
| glintr100 (FR) | 0.500–0.509, clean | 0.503 [0.460, 0.548] | 0.554 [0.471, 0.640] | 0.545 [0.513, 0.578] | 0.42; flat |
| CLIP ViT-L/14 | mordiff 0.582 [0.543, 0.621] | 0.364 [0.323, 0.404] | 0.698 [0.616, 0.775] | 0.542 [0.511, 0.572] | 1.0; falling |
| DINOv3 ViT-L/16 (bf16) | mordiff 0.356 [0.300, 0.406] | 0.533 [0.486, 0.578] | 0.611 [0.522, 0.698] | 0.624 [0.598, 0.652] | 4e-5; rise then fall |
| DiffAE z_sem | mordiff 0.000 [0.000, 0.000] | 0.692 [0.657, 0.729] | 0.688 [0.626, 0.749] (DiffAE-native frames) | 0.597 [0.568, 0.627] | 9e-99; rising |

Other primary-family controls (opencv, facemorpher) are 0.502–0.531 in every arm; the stylegan E7 frames are
identical to the native frames (0.500, zero-width interval), so that family carries no information.

Same-person vs two-person morph: landmark R3m vs R4 0.651 [0.614, 0.687]; glint R3 vs R4 0.498, C20 vs B20
0.540; CLIP C20 vs B20 0.419 [0.343, 0.498]; DINOv3 0.478; DiffAE (native) C20 vs B20 0.747 [0.685, 0.807],
R3 vs R4 0.676 [0.637, 0.715], R3m vs R4 0.807 [0.772, 0.840]. Photo vs morph: landmark R0 vs R4 0.725 [0.689,
0.758]; DiffAE AR1 R0 vs R4 0.695 [0.659, 0.732], a256 vs B20 0.687 [0.612, 0.757]; CLIP AR1 R0 vs R4 0.391
(landmark morphs score less average than photos), E vs B20 0.635. One-photo output vs same-person: AR1 R2w vs
R3 0.498–0.537; DiffAE-native D20 vs C20 0.445. Landmark FRLL-Morphs / MAD22 pair shapes vs FRLL shapes:
0.731–0.758. Full tables: `README.md` section 5, CSV files.

## GEO-0 reads (glintr100)

1. Fidelity F = cos(e_built, normalise(e_A + e_B)), median: AR1 R4 0.876 (OpenCV) / 0.856 (FaceMorpher);
   twins R3 0.978, R3m 0.962; published FRLL-Morphs frames 0.81–0.82; A43 B20 0.711, B 0.719, published MorDIFF
   0.700, DiM-C 0.691, Greedy-DiM 0.848; same-person mix C20 0.915. Landmark morphs lie between the 0.75 and 0.90
   lines; diffusion morphs at or below 0.75 (off-span part dominates), and it is larger for morphs than twins.
2. Mean-direction gain: AR1 R4 1.108 [1.057, 1.157] (prediction 1.27), FaceMorpher R4 1.008 [0.955, 1.061];
   R3 1.030 [1.017, 1.042] (prediction 1.03); A43 B20 1.009 [0.808, 1.206], published MorDIFF 0.981 (predicted
   κ 1.34 at the pairs' cosine 0.11).
3. Virtual head (fit persons only; in-domain 5-fold AUC 0.744, 0.71–0.76 per cosine bin): AR1 R3 vs R4 0.557
   [0.514, 0.598], host photo vs R4 0.593 [0.549, 0.633], R2w vs R4 0.590; a43_B vs a43_D 0.522 [0.453, 0.593];
   D20 vs B20 0.524; rec vs published MorDIFF 0.489; StyleGAN3 bona vs morph 0.600 [0.571, 0.628]. Controls:
   native vs E7 opencv / facemorpher / stylegan 0.496 / 0.497 / 0.500, **mordiff 0.415 [0.396, 0.427]**,
   rec vs aligner copy 0.536 [0.530, 0.547].
4. Λ (Mahalanobis length of the mean embedding, Ledoit-Wolf) = 2.68 (ridge variants 3.70–4.81). Ceiling morph
   vs photo: 0.784 (c = 0), 0.746 (0.1), 0.710 (0.2), 0.676 (0.3), 0.616 (0.5); vs twin 0.768 / 0.691 at c = 0
   / 0.2. AD1's R2 vs R4 values for the releases: 0.48 / 0.49 / 0.40 (adapted), 0.66 / 0.85 (MADation FE
   ViT-L/14 at 20 / 100 steps).

## Predicted vs observed, and the ceiling against benchmark similarity

Contributor similarity present (glintr100 cosine, median [10%, 90%]): FRLL-Morphs 0.037 [−0.066, 0.144];
corrected MAD22, MorDIFF, DiM 0.114–0.116 [0.05, 0.19]; H3 StyleGAN3 0.162 [0.069, 0.246]; AR1 look-alike pool
0.234 [0.163, 0.310]. FR ceiling at these values: about 0.74–0.77 (benchmarks), 0.70 (AR1).
Physics closed form at the pool-centred c (the pre-registered c_pair gave values above 1, see README 7):
landmark AR1 0.693 predicted vs 0.725 observed; FRLL-Morphs pairs 0.739 vs 0.737; MAD22 pairs 0.728–0.736 vs
0.736–0.758. Image-feature arms: CLIP 0.874 vs 0.364 (AR1), 0.952 vs 0.698 (MorDIFF); DiffAE 0.953 vs 0.692,
0.978 vs 0.688; DINOv3 0.886 vs 0.533, 0.846 vs 0.611; glintr100 0.964 vs 0.503 (its genuine-only virtual check
is 0.521: unit normalisation removes the shrinkage). The closed form holds for exact shapes and overshoots every
image arm by 0.24–0.51.

## Falsifiers (as pre-registered)

- Physics, part 1 (best arm R2 vs R4 < 0.65 on both a43 D20 vs B20 and AR1 R2w vs R4): **does not fire**
  (DiffAE 0.688 and 0.692; CLIP 0.698 on MorDIFF only; exact shapes 0.687 on AR1).
- Physics, part 2 (native vs E7 outside the stricter 0.45–0.55): **fires for CLIP (0.582), DINOv3 (0.356) and
  DiffAE (0.000)**; with the entry's original 0.40–0.60 band CLIP would pass. glintr100 is clean.
- Physics, part 3 (no monotone dose, Page p > 0.05): fires for glintr100 (0.42) and CLIP (1.0); not for
  landmark, DiffAE; DINOv3 p 4e-5 but means fall after m = 0.3.
- Landmark kill (exact R0 vs R4 < 0.60): **does not fire** (0.725).
- Decision text: no arm ≥ 0.75 on R2 vs R4 with a clean control; not all arms below 0.65.
- GEO-0: Go no; Kill (≤ 0.55 on both) no — landmark head 0.557, DiffAE 0.522; identity idea 0 falsifier
  strictly not fired (0.557 > 0.55), but its control clause **fires** (mordiff E7 0.415).
- Identity idea 1 (shrink law, ISS): no generator family has an upper bound ≤ +0.10 in glintr100 (A43 B20 ρ
  0.100 [−0.130, 0.342], published MorDIFF 0.045 [−0.072, 0.162], DiM-C 0.084, Greedy-DiM 0.063), none has a
  lower bound above 0; landmark families positive (AR1 FaceMorpher 0.182 [0.007, 0.338], FRLL-Morphs frames
  0.12–0.14, lower bounds 0.014–0.029); the virtual head's ρ is ≤ 0 everywhere. Oracle power 0.38–0.80 in
  every family (audit not void). Exact shapes ρ ≈ 0 (AR1 0.083 [−0.085, 0.236]).

## Not verified, gaps

Not verified: that Enc(Dec(lerp)) returns the generator's lerp code in its own precision path (z_sem midpoint
fidelity 0.82 for B20 vs 0.85 for reconstructions is measured); fp16 CLIP equals a46's fp32 CLIP on identical
files; that the stylegan E7 identity is intended. Gaps: CLIP, DINOv3, DiffAE ran on tier-1 sets only
(FaceMorpher rungs, R2/NC, FRLL AR1 pool, published FRLL-Morphs frames missing there); exact shapes are given,
not landmarks detected on morph images; the fit pool (92% FERET) differs from AR1 (80% FRGC), FRLL, A43 and
H3; no BPCER per demographic group; released-detector shrink-law audit not run.
