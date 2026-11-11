# Mirror-asymmetry test (AS0): result of phase 1

11 Nov 2026, about 20:30 CET. Owner of the mirror-asymmetry test (AS0). Registration `prereg.md` (amendments A1-A13,
all before any contrast); full record `README.md`; all tables `tables.md`; numbers `contrasts.csv`, `history.csv`,
`dose.csv`, `shares.csv`, `verdict.json`, `analysis.json`, `typ_detected.csv`, `blank_vs_primary_same_hosts.json`.
Statistic: L = ln(E_A / E_S), energies of the mirror-asymmetric and mirror-symmetric parts in octave bands B1..B5
(half-power wavelengths IOD to IOD/32) inside a symmetric face mask; luminance; lossless flip about the frame centre.
AUC = P(L(X) < L(Y)); 95% two-way person bootstrap, B = 2,000. No detector score was opened; no image was built.

## Registered verdict: **weak**

Primary pool, landmark ladder (AR1), 536 FRGC / colorFERET hosts, both engines pooled. Two-person morph (R4) against
same-person morph (R3), all R3 cross-session:

| band | B1 | B2 | B3 | B4 | B5 | B1-B5 |
|---|---|---|---|---|---|---|
| AUC | 0.563 [0.525, 0.603] | 0.599 [0.556, 0.635] | **0.618 [0.578, 0.655]** | 0.562 [0.522, 0.599] | 0.524 [0.484, 0.564] | 0.611 [0.570, 0.648] |
| history shift d, FaceMorpher E7 (own landmarks) | -0.018 | +0.048 | +0.102 | +0.095 | +0.016 (above cut-off) | -0.175 |

No band reaches 0.70 (pass fails); B2 and B3 are at or above 0.60 (kill does not fire). Positive control: the mirror
self-morph (R3m) collapses in every band (median ratio to R2w <= 0.003, AUC 1.000; by construction, same flip). Without
the 8 reserved persons 0.567 / 0.603 / 0.622 / 0.567 / 0.526; OpenCV 0.625, FaceMorpher 0.611 (B3); two person-disjoint
halves 0.635 / 0.624 (B3). External prediction of the identity-shrinkage review (A11: best band 0.58-0.70 with dose
slope below 0.7): best band 0.618, slope 0.535 there: **inside the predicted zone**.

## What carries the 0.62

- Geometry: partialling out shape asymmetry, three midline offsets and mask size leaves 0.596 (B3); shape asymmetry
  alone (calculated from source landmark files, arithmetic) 0.595; on landmarks detected on the built images 0.590.
  Symmetrising only the shape (R2wm against R0) already lowers the ratio at 0.56 / 0.66 / 0.71 / 0.73 / 0.74.
- Softness does not explain it (residual after Laplacian variance 0.627; Laplacian variance alone 0.530). Pose and
  lighting: residual 0.604; |yaw| tertiles 0.59 / 0.64 / 0.59. Low-band leakage: blanking outside the mask in memory
  gives 0.651 against 0.642 on the same 187-host subsample (B3).
- Capture-specific averaging is real. Same-person cross-session morphs lose asymmetry against warp-only images (R3
  against R2w 0.58 / 0.58 / 0.58 / 0.56 / 0.53); within colorFERET, cross-session same-person morphs (record's r8 arms)
  are below same-session ones at 0.587 / 0.574 / 0.616 / 0.573 / 0.541 (620 / 1,172). Two-person morph against
  same-session same-person morph, colorFERET only: 0.61 / 0.62 / **0.69 [0.61, 0.77]** / 0.63 / 0.56; against
  cross-session (K1 within colorFERET) 0.56 / 0.56 / 0.58 / 0.52 / 0.51. (A same-session rung on the same hosts does
  not exist: phase 2.)
- The two-person morph does not halve the asymmetric energy: median ratio to R2w 0.61 / 0.65 / 0.68 / 0.81 / 0.95
  (predicted 0.5). Dose curve (graded FaceMorpher, 300 hosts): slope 0.63 [0.54, 0.72], 0.60 [0.53, 0.68], 0.54 [0.47,
  0.60] in B1-B3, 0.27 and 0.08 in B4-B5: shrinks less than the square-root law. Person-specific share of the
  asymmetric energy 0.49-0.75 (B1-B3, bounds pi_A / pi_L).

## Storage history

FaceMorpher E7 (204 FRLL photos, canonical frame, scale 0.47, B1-B4 below the cut-off), own landmarks: d = -0.02,
+0.05, +0.10, +0.10 (B1-B4); the shift is 8 to 42% of the R3-R4 difference in L. With the native's landmarks it is
larger in B2-B3 (+0.11, +0.20). AR1 photos through the same 61.2 px path (Lsoft fm61, own landmarks): R0 +0.02 / -0.01
/ +0.03 / +0.04, R2w +0.03 to +0.13 (B3-B4 above 0.1). OpenCV / Webmorph / AMSL / FaceMorpher-FRLL-Morphs copies:
|d| <= 0.07. SMDD 80 px copies: +0.035, +0.060 (B1-B2, below their Nyquist). So the ratio is history-stable within
0.1 SD in B1-B2 and at the 0.1 edge in B3-B4.

## Other families (descriptive readings)

- GAN latent blocks (StyleGAN3, 64 blocks): two-person morph against same-person mix (x3 against x2) **0.48-0.52**
  (does not separate); any two-code mix against a one-code reconstruction 0.61-0.68 (x3 against x1, x2 against x1);
  reconstruction against photo 0.52-0.65. The ratio reads "two codes were mixed", not "two persons".
- Diffusion autoencoder (A43, FRLL): two-person morph against same-person mix (B20 against C20) 0.65 / 0.71 / **0.74
  [0.65, 0.82]** / 0.69 / 0.61; but the same-person mix (neutral + smiling, one session) is MORE asymmetric than the
  one-photo reconstruction (C20 against D20 0.37-0.46), and B20 against D20 is only 0.61 / 0.63 / 0.60 / 0.57 / 0.50.
  The same on the stored crops (0.72 in B3). Mirror mix (AD1b smoke, 4 persons): 1.000. The lead's face-box number
  reproduces on persons 001-004 (photo 19.4, D20 17.7, C20 18.7, B20 12.0, mirror mix 2.1) but on all persons the gap
  is small (12.9 / 11.8 / 13.4 / 10.9).
- Detected landmarks on the built ladder images (A10, review H-new-2): ID0 typicality, R4 against R3, **0.653 [0.616,
  0.692]** (calculated from source files 0.687): supported (>= 0.65) by 0.003.

## Failed, cut or not verified

- Cut because of the CPU load (about 140 on 20 cores from 18:50): expanded123 DiffAE blocks not measured; R8 measured
  on colorFERET pairs only; blank run on a host subsample and on R3 / R4 only (no R3m there); Fe on two families.
- Not verified: whether the FRGC "environment" field (a camera id) matters; same-session same-person morphs on the
  AR1 hosts (do not exist); the R4 reference at its own H-B mean shape (needs warp-only images toward that shape,
  phase 2); the AD1b full run (32 persons) was still rendering at the analysis; the geometry share as registered
  (log ratio to the mirror self-morph) is degenerate because R3m is near zero; the energy version is in `shares.csv`.
