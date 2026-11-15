# Mirror-asymmetry test (AS0): result (closed 11 Nov 2026)

Version 2, 11 Nov 2026, about 21:00 CET, after the independent review (`experiments/reviews/REVIEW_AS0_20261111.md`,
verdict "needs qualification"; corrections applied here) and amendment A14. Owner of the mirror-asymmetry test (AS0).
Registration `prereg.md` (A1-A14, each before the numbers it governs); full record `README.md`; tables `tables.md`;
numbers in `contrasts.csv`, `history.csv`, `dose.csv`, `shares.csv`, `verdict.json`, `analysis.json`,
`typ_detected.csv`, `blank_vs_primary_same_hosts.json`, `a14.csv`, `a14.json`, `posthoc_addendum.json` (post hoc).
Statistic: L = ln(E_A / E_S), energies of the mirror-asymmetric and mirror-symmetric parts in octave bands B1..B5
(half-power wavelengths IOD to IOD/32) inside a symmetric face mask; luminance; lossless flip about the frame centre.
AUC = P(L(X) < L(Y)); 95% two-way person bootstrap, B = 2,000. No detector score was opened; no image was built.

## Registered verdict: **weak**

Landmark ladder (AR1), 536 FRGC / colorFERET hosts, both engines pooled; two-person morph (R4) against same-person
morph (R3); every R3 and every R4 is a mix of two captures from different sessions:

- **Selection-free, all bands B1-B5: 0.611 [0.573, 0.651].**
- Per band: 0.563 [0.526, 0.603], 0.599 [0.561, 0.640], **0.618 [0.580, 0.659]** (best of five, B3), 0.562 [0.522,
  0.605], 0.524 [0.483, 0.565].
- No band reaches 0.70: the pass rule fails. Only one band, B3, is at or above the kill mark of 0.60 (B2 is 0.599), so
  the line between "weak" and "kill" is within noise.
- Without the 8 reserved persons: 0.615 (B1-B5), 0.622 (B3). OpenCV 0.625 and FaceMorpher 0.611 (B3); person-disjoint
  halves 0.635 and 0.624 (B3). Mostly an FRGC result: FRGC 0.634, colorFERET 0.581 [0.499, 0.661] (B3).
- External prediction of the identity-shrinkage review (A11): best band 0.618 with dose slope 0.535 there, inside the
  predicted zone: **not falsified**.

## Controls

- The mirror self-blend control (R3m: AUC 1.000, ratio to R2w at most 0.003) is **algebra**. It was built with the
  same flip as the statistic, so it checks the code, not the sensitivity.
- The informative positive control is the **dose curve** (graded FaceMorpher, 300 hosts). It is monotone; m = 0.5
  against m = 0 gives 0.71 in B3. But it shrinks at only 0.54-0.63 of the square-root-law rate in B1-B3 (slopes 0.63
  [0.54, 0.72], 0.60 [0.53, 0.68], 0.54 [0.47, 0.60]), and at 0.27 and 0.08 in B4-B5.
- **Storage history: history-stable, not history-free.**
  - FaceMorpher E7 copies (204 FRLL photos), own landmarks: d = -0.02, +0.05, +0.10, +0.10 SD (B1-B4, all below the
    cut-off). That is 8-42% of the R3-to-R4 gap in L.
  - In B3, the band that carries the effect, the shift is at or above the registered 0.1 mark in every variant:
    +0.20 with native landmarks; +0.12 to +0.17 on the ladder's own softened warp-only images.
  - With the primary frame-centre flip the shift points toward the genuine side: no shift below the cut-off is more
    negative than -0.03 in 84 rows. So the ratio cannot flag stored genuine photos; it can only hide stored morphs.
  - Exception (owner's check of the review's statement): with the landmark-midline flip F1 and own landmarks, the
    FaceMorpher E7 shift is -0.08 (B3) and -0.14 (B4), toward the morph side. The "genuine side only" statement holds
    for F0, not for every variant.
- **Pool level.** The level of the ratio differs between photo pools more than between morph types. Genuine FRGC
  against genuine colorFERET photos: 0.74 / 0.76 / 0.72 / 0.67 / 0.57 (B1-B5). The ratio is usable only within one
  pool on the same hosts, never as one threshold across pools.
- Softness does not explain the key contrast within the pool: 0.627 (B3) after partialling out Laplacian variance;
  Laplacian variance alone 0.530. Blanking outside the mask in memory: 0.651 against 0.642 on the same 187 hosts.

## Geometry-matched reference (amendment A14, registered before reading)

R2w4 is the host photo warped to the two-person target shape, with no second texture. B3, pooled:

| quantity | value | registered prediction | result |
|---|---|---|---|
| R2w4 against R2w (geometry only) | 0.540 [0.503, 0.576] | 0.55-0.60 | below the range |
| median exp(L_R2w4 - L_R2w) | 0.903 [0.878, 0.938] | 0.82-0.90; falsified if >= 0.95 | not falsified on this count |
| R4 against R2w4 | **0.655 [0.628, 0.685]** | 0.58-0.64; falsified if >= 0.65 | **falsified** |
| texture excess (R4 vs R2w4 minus R3 vs R2w 0.576) | **+0.079** | revisit a learned version only if >= 0.03 | rule met |
| geometry share of the R3-to-R4 gap | **0.33 [0.23, 0.43]** | 0.40-0.70 | below the range |

- Geometry share in the other bands: B1 0.17, B2 0.30, B4 0.51, B1-B5 0.24.
- R4 against R2w4 in the other bands: B1 0.63, B2 0.65, B4 0.59, B5 0.53, B1-B5 0.70.
- **H-new-1 ("geometry carries most of the key contrast") is falsified.** Shape accounts for about a third of the
  B3 gap. Blending in a second person's texture lowers the ratio more than blending in a second capture of the same
  person (0.655 against 0.576).
- Detected-landmark typicality (H-new-2): R4 against R2w4 0.528 [0.505, 0.552] (prediction 0.44-0.56); R2w4 against
  R3 0.626 [0.590, 0.662] (prediction >= 0.62). **Not falsified**: the detected typicality reads the target shape,
  not blend artefacts, so the A10 conclusion stands. Detected typicality of R4 against R3 is 0.653 [0.616, 0.692]
  (0.687 from source files): not falsified, lower bound above 0.60.

## Session and capture

- About half of a photo's coarse-band asymmetry belongs to the capture, not the person (person-specific share 0.49 to
  0.75 in B1-B3).
- Same-person cross-session morphs lose asymmetry against warp-only images: 0.58 / 0.58 / 0.58 / 0.56 / 0.53.
- Within colorFERET, cross-session same-person morphs sit below same-session ones: 0.587 / 0.574 / 0.616 / 0.573 /
  0.541.
- Because R3 and R4 are both cross-session, the capture loss appears in both arms of K1 and cancels to first order.
  K1 fades with the session gap: 0.642 at 60 days or less, 0.563 above 365 days.
- **Not to be quoted:**
  - The 0.69 of two-person against same-session same-person morphs: colorFERET only, best of five bands, adds capture
    averaging.
  - The pooled 0.84 of two-person against same-session morphs: it mixes databases, and the pool offset is larger than
    the effect.

## Other families (descriptive readings)

- **GAN latent blocks** (StyleGAN3, 64 blocks): two-person against same-person mix 0.48-0.52 (no two-person
  reading). Any two-code mix against the one-code reconstruction: 0.61-0.68. Reconstruction against photo: up to 0.65
  (the inversion itself symmetrises).
- **Diffusion autoencoder** (A43): two-person morph against same-person mix 0.74 [0.65, 0.82] (B3). This is mainly
  that mix being unusually asymmetric: same-person mix against reconstruction is 0.37-0.46, while its inputs are not
  asymmetric (neutral against smiling FRLL photos 0.46-0.54, post hoc). Two-person morph against reconstruction: 0.60.
  Mirror mix against its reconstruction (32 persons): 1.000 (algebra, as above).
- **Context** (review F8): released detectors already score R4 against R3 on this ladder at 0.60-0.75. The ratio is
  a floor that most of them clear, not a method.

## Post hoc addendum (lead's request after the review; not registered; `posthoc_addendum.json`)

- **Pool offset** (review F2), genuine FRGC against colorFERET (427 / 109):
  - Raw: 0.743 [0.691, 0.795], 0.761 [0.706, 0.813], 0.720 [0.666, 0.769], 0.667 [0.613, 0.717], 0.567 [0.513,
    0.617].
  - With yaw, nose offset and lighting partialled out: 0.780, 0.790, 0.739, 0.682, 0.569. So the offset is **not pose
    or lighting**.
  - With log Laplacian variance added: 0.539 [0.476, 0.599], 0.532, 0.520, 0.537, 0.506. The offset follows the
    pools' capture sharpness and detail.
- **Logistic ceiling** (5 strictly person-disjoint folds, out-of-fold, reserved persons dropped):
  - Same-person against two-person: five bands 0.632 [0.588, 0.674]; plus calculated shape 0.635; plus detected shape
    0.634; detected shape alone 0.589.
  - Warp-only against two-person: five bands 0.701 [0.660, 0.741]; plus shape 0.700.
  - Combining the bands adds little over the best band.
- **F9** (partner similarity): Spearman of cos_HB with L_R4 - L_R2w is -0.10 [-0.18, -0.01] (B2-B3, both engines;
  B4-B5 -0.12 to -0.15). More similar partners lose slightly more asymmetry. The look-alike explanation of the weak
  halving is disfavoured and dropped.
- **F8:** neutral against smiling FRLL photos 0.46-0.54 per band; recorded with the released-detector context above.

## Cut, dropped or not verified

- Dropped (lead): the expanded123 DiffAE blocks and the R8 FRGC pairs.
- Reduced because of CPU load: the blank run (host subsample, R3 / R4 only) and Fe (two families).
- Not before 14 Nov: the learned head on f(x) - f(flip x), and same-session FRGC morphs.
- To the frozen read of the new diffusion ladder (FZ2): the diffusion expression-mix reading (review H-new-3).
- Not verified: whether the FRGC camera id matters; same-session same-person morphs on the AR1 hosts (none exist).
- The registered geometry share in log units (relative to R3m) is degenerate; its energy version is in `shares.csv`.

**Paper wording (review):** "averaging two captures, and to a lesser degree two persons, lowers mirror asymmetry";
never "the ratio detects a second person". About a third of the identity part is face shape; the rest is the
person-specific texture asymmetry that the blend averages.
