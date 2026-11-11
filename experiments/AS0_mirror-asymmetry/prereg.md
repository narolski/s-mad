# Mirror-asymmetry test (AS0): pre-registration

Written 11 Nov 2026, about 18:10 to 18:17 CET (file time 18:17), by the owner of the mirror-asymmetry test (AS0), **before any asymmetry
statistic, band energy, shape-asymmetry value or contrast of this experiment was computed on any image**. Known
before writing: the lead's unreviewed numbers on 4 persons of the identical and mirrored inputs for diffusion
experiment (AD1b) (face-box mean |image - mirror| 19.6 photo, 18.3 one-photo reconstruction, 18.7 same-person mix,
12.0 two-person morph, 2.1 mix with own mirror); the established facts in `ideas/ROUND3_BRIEF.md` (softness floor:
Laplacian variance alone separates a landmark morph from its own halves at AUC 0.76 to 0.87); the identity-shrinkage
triage (ID0) landmark-shape numbers (two-person mean shape against a real shape AUC 0.725). Inventory checks done
before writing (no outcome): file counts, image sizes, landmark-file existence, the 106-point layout (mean positions
of the AR1 host shapes), session dates in the pool tables, alignment eye coordinates of the frames, and that the
insightface detector finds faces in 8 images per set (landmark detection for 4,228 images started at 18:13; landmarks
are geometry, not an asymmetry statistic). No detector score is opened at any point. No sealed file is opened.

Abbreviations: AUC = area under the ROC curve (0.5 = chance); CI = 95% percentile bootstrap interval; IOD =
inter-ocular distance (distance between the two pupil landmarks, 106-point indices 38 and 92); FFT = fast Fourier
transform; E7 = the existing shrink-and-enlarge storage-history copy of a genuine photo; SD = standard deviation;
FR = face recognition; OLS = ordinary least squares.

## Hypothesis (plain words)

A face is roughly mirror-symmetric plus a person-specific asymmetric part. A two-person morph averages two
independent asymmetry patterns, so its asymmetric energy falls (to about one half at equal mixing; amplitude by about
the square root of two) while the symmetric part stays. A same-person morph averages a shared pattern and should keep
it. Blur, shrink-and-enlarge and compression act alike on both halves, so the per-band ratio of asymmetric to
symmetric energy should not move with softness or storage history. Competing explanation registered with equal
weight: much of a photo's asymmetry is capture-specific (head pose, lighting direction, expression); averaging two
captures of the same person from two sessions then also shrinks it, and the ratio separates "two captures were mixed"
rather than "two persons were mixed".

## Data (all images exist; no image is built or written)

Item list `/mnt/t7/smad_next/AS0/items.csv` (25,160 rows, built by `src/AS0/as0_lists.py`; summary
`lists_summary.json`). Sets:

- **L, primary: the landmark ladder (AR1)**, FRGC (427) and colorFERET (109) hosts, 536 hosts, both engines
  (OpenCV, FaceMorpher), 512 x 512 frames of `73_delin_align` (eyes at (190, 210) and (322, 210)). Rungs per host
  and engine: camera photo (R0, = host photo H); the host's other-session photo (S0, the same person's second photo,
  measured as a second genuine photo); tool run on one photo (R2); warp-only image toward the mean shape of H and S
  (R2w); warp-only toward H's own mirrored shape (R2wm); mirror self-morph, tool(H, mirror of H) (R3m); same-person
  morph tool(H, S) (R3); two-person morph tool(H, B), B = another person's S photo (R4). All R3 pairs are
  **different-session** by construction (session = capture date; 536 of 536). Graded FaceMorpher mixing (AR2) at
  m = 0, 0.1, ..., 0.5 on 300 hosts (same H, B as R4). Landmarks: the 106-point `.tem` files; a built image's shape is
  the tool's target shape, (1 - w) * shape(H) + w * shape(partner) with w = 0.5 (R2w, R3, R4: partner S or B; R2wm,
  R3m: partner = the mirrored, re-indexed shape written by AR1 `variants.py mirror`), w = m for the graded set.
- **R8, landmark same-person morphs with session information** (the record's r8 arms, byte backup
  `/mnt/t7/smad_next/volatile_backup_20261111/r8_{cv,fm}`, pairs `/dev/shm/smad_arms/r8_pairs.csv`): 2,500 pairs x 2
  engines, two captures of one FRGC or colorFERET person, same 512 frame, shapes = mean of the two `.tem`. colorFERET
  same-session pairs (same date, mostly fa + fb, i.e. an expression change) 586, cross-session 310; FRGC sessions from
  the FRGC metadata dump (AR1 `pool.frgc_meta`, imported unchanged).
- **G, GAN latent blocks** (StyleGAN3, set G of the signal isolation by paired differences experiment (PD1)): 64
  blocks, camera photo (x0, 256, shared-512 frame), one-photo reconstruction (x1, 256), same-person mix of the two
  captures (x2, 128), two-person morph (x3, 128), raw 1024 renders. colorFERET captures are mostly fa/fb of one
  session, FRGC two stills (dates from the dump).
- **D, diffusion-autoencoder ladder** (A43 material, DiffAE-native 256 frames, FRLL persons, evaluation only): photos
  (a256 inputs, 204), one-photo reconstruction at 20 steps (D20, 204), same-person mix neutral + smiling (C20, 102,
  same session), two-person morph at 20 steps (B20, 200) and at 100 steps (B, 200, descriptive).
  **M**: mix of a photo with its own mirror (P_AF) and the re-run reconstruction (D20r) of the identical and mirrored
  inputs experiment (AD1b), 4 smoke persons; the 32-person full run is added if complete before the analysis (it is
  being written by another process until about 20:30; it is not touched before it ends).
  **Ds**: the same A43 arms after the A43 storage step (stored crops, about 150 x 190 px; photo E, D20, C20, B20)
  and the published MorDIFF morphs (A, descriptive).
- **History-control sets**: **Fm (primary)**: corrected MAD22 canonical 512 frames (prep_eval alignment, eyes at the
  same coordinates as L), native genuine photos (204) against their E7 copies with the FaceMorpher history (204, scale
  about 0.30); secondary E7 OpenCV and Webmorph copies (only copies that differ in pixels from the native image).
  **Fe**: FRLL-Morphs evaluation frames, native against `resmatch_{amsl, facemorpher, opencv, webmorph}`.
  **Lsoft**: 200 AR1 hosts, R0 and R2w of both engines, against their copies through the existing registered
  shrink-and-enlarge path (alignment-eye-distance targets 112.7 px and 61.2 px; built by the alpha-field probe owner,
  `/mnt/t7/smad_next/AF0/img/soft`). **S**: 2,000 SMDD genuine renders against their stored-small (80 px) E7 copies.
  **Ds vs D**: A43 arms before and after storage (frames differ: descriptive only).
- **X (secondary, descriptive)**: diffusion-autoencoder blocks on colorFERET / FRGC (`diffae-expanded123-v1`, 102
  complete blocks; photo, reconstruction, same-person mix, two-person morph). Contains non-frontal captures (FERET rc,
  qr ...): yaw is reported beside every number.

Landmarks of images without `.tem`: insightface buffalo_l (det_10g + 2d106det, the pack of `73_delin_align` and
`prep_eval`), CPU, det size 512, largest face; if no face is found, one retry on an in-memory copy padded with black
by half the image size (detector input only; needed for the tight A43 stored crops). History copies use the
landmarks of their native image (same geometry); SMDD uses the record's insightface-106 landmark file
(`/dev/shm/smad_arms/smdd_bona_landmarks_if106.npz`), scaled by 80/256 for the 80 px copies. Items without a face or
with a symmetric mask under 1,000 pixels are dropped and counted.

## Statistic (fixed)

Per image (RGB, float, 0-255). **Nominal IOD per frame type** = median pupil distance (landmarks 38-92) over that
frame type's genuine images (computed from landmarks before any statistic; for frames without genuine images, over
all images): frame types ar1_512 and canon512 (same geometry), shared512_photo, stylegan_raw1024, diffae256,
a43_stored, smdd256 (smdd80 = 0.3125 x smdd256).

1. **Flip and midline.** Primary flip F0: lossless left-right flip about the frame's vertical centre line,
   x -> W - 1 - x (the flip that built every mirror rung: AR1 `cv2.flip`, AD1b `torch.flip`). In the L frames the
   alignment puts the eye midpoint at x = 256.0 (kps) and the 106-point midline points at about 255.3, so F0 is the
   alignment midline. Exception: the A43 stored crops (Ds) are not centred on the face, so Ds uses F1 as its primary.
   Secondary flip F1 (all sets): mirror about the per-image landmark midline c = mean x of the 106 landmarks (the
   least-squares vertical reflection axis of the shape and its re-indexed mirror), rounded to the nearest half pixel;
   mirror(x)[.., j] = x[.., 2c - j], a lossless index map; pixels whose mirror falls outside the frame are excluded.
2. **Face mask** M: polygon through the face contour (temple to chin to temple, 106-point indices 1, 9-16, 2-8, 0,
   24-18, 32-25, 17) and the upper edges of both brows (101, 105-102; 50, 51, 49, 48, 43): it excludes forehead and
   hair above the brows, ears and backdrop. Eroded by round(0.04 x IOD) pixels. Alignment border: zero pixels
   (R = G = B = 0) connected to the frame edge, dilated by 3 px, are excluded. Symmetric mask
   M_sym = M ∩ mirror(M) ∩ not border ∩ mirror(not border).
3. **Bands.** One FFT per channel of the whole frame; radial frequency f (cycles/pixel), u = log2(f x IOD).
   Octave bands B1..B5 with amplitude weights H_k(u) = cos(pi/2 (u - k + 0.5)) for |u - (k - 0.5)| <= 1, else 0;
   half-power edges at wavelengths IOD/2^(k-1) and IOD/2^k (B1: IOD/2 to IOD, ..., B5: IOD/32 to IOD/16); the squared
   weights sum to one (energy partition). Descriptive residual bands: B0 (all below B1, includes the mean) and B6
   (all above B5). Bands are truncated at the frame's Nyquist frequency. Band images b_k = inverse FFT of H_k x FFT(x);
   since H_k is radial it commutes with the F0 flip exactly (and with F1 away from the frame edge), so
   A_k = (b_k - mirror(b_k)) / 2 and S_k = (b_k + mirror(b_k)) / 2.
4. **Energies and ratio.** E_A,k = sum over M_sym of A_k^2, E_S,k likewise; **L_k = ln(E_A,k / E_S,k)** (primary
   statistic, per band). Also reported: broadband L_bb = ln(sum_{k=1..5} E_A,k / sum E_S,k).
5. **Channels.** Luminance Y = 0.299 R + 0.587 G + 0.114 B (**primary**); R, G, B separately and the channel-summed
   energies "RGB" (secondary). Y band images are the same linear combination of the R, G, B band images.
6. **Shape asymmetry (landmark shapes, no image).** Shape X (106 x 2); mirrored re-indexed shape Xm (x -> W - 1 - x,
   AR1 permutation `mirror_perm106.json`); ordinary Procrustes superimposition of Xm onto X (translation, rotation,
   uniform scale, no reflection); A = (X - Xm*) / 2, S = (X + Xm*) / 2 minus its centroid;
   **L_shape = ln(sum |A|^2 / sum |S|^2)**. L and R8 shapes are exact (tool target shapes); G, D, X shapes are
   detected.
7. **Covariates** (measured, not assumed away): yaw proxy (x86 - x12 - (x28 - x86)) / (x28 - x12) (nose tip relative
   to the left and right contour at nose height; signed) and nose offset (x86 - eye midpoint x) / IOD; roll (angle of
   the pupil line); midline offset c - (W - 1)/2 in IOD units; lighting index = (mean Y on the left half of M_sym -
   mean Y on the right half) / mean Y on M_sym; softness = log of var(cv2.Laplacian(grey, CV_64F)) over M_sym (grey =
   OpenCV BGR-to-grey of the 8-bit image; the record's Laplacian-variance measure, restricted to the mask; whole-frame
   value also stored); mask size.
8. **Replication of the lead's number** (descriptive): mean |x - flip(x)| over rows 70-220, columns 64-192 of the
   diffae256 frames (the AD1b box), RGB channels averaged; and the same quantity over M_sym in Y for every set.

## Contrasts (AUC with person-level bootstrap interval, per band, Y, F0 unless stated)

Direction: for "X against Y" the score is -L (lower asymmetry ratio = positive), positive class X; AUC = P(L(X) <
L(Y)) with ties one half. AUC > 0.5 = X has the lower ratio, as the idea predicts where it predicts a fall. Intervals:
the record's pigeonhole person bootstrap (AR1 `stats.py`: `a41_read.Draw`, `a36_read.wauc`, imported unchanged; a
two-person item weighs the product of its two persons' counts), B = 2,000, seed [20261111, 61]. Persons: AR1 pid
(L), "db:subject" (R8 and the R8-against-L comparison, one draw over the union), block (G, X), FRLL person (D, M, Ds,
Fm, Fe), SMDD render (S).

**Landmark ladder, primary pool (both engines pooled; also each engine):**
- K1 **two-person morph (R4) against same-person morph (R3)** — the key contrast.
- K2 R4 against warp-only (R2w). K3 R3 against R2w. K4 R2w against photo (R0) (processing control; registered as
  "photo (R0) against R2w"; predicted near 0.5). K5 **mirror self-morph (R3m) against R2w** (positive control: the
  ratio must collapse). Also R2 against R0, R2wm against R0 (shape-only symmetrisation), S0 against R0 (two genuine
  photos, 0.5 expected).
- **Dose curve (graded mixing, FaceMorpher, 300 hosts)**, prediction stated before looking: if asymmetric energy is
  independent between the two contributors and equal in size, and the symmetric energy is unchanged, the energy ratio
  scales as a^2 + (1 - a)^2 (the amplitude ratio as sqrt(a^2 + (1 - a)^2)), i.e. dL(m) = L(m) - L(0) =
  ln(m^2 + (1 - m)^2) = -0.198, -0.386, -0.545, -0.654, -0.693 at m = 0.1 ... 0.5. Read: per band, the OLS slope beta
  of the paired dL on the predicted value (all hosts and levels, no intercept), host-bootstrap CI. "Follows the
  square-root law" if 0.7 <= beta <= 1.3; "shrinks less" if beta < 0.7; "more" if beta > 1.3. Prediction caveat
  registered: in bands where skin texture dominates (expected B4 to B5) the symmetric energy is not shared between
  persons, so the ratio there is expected near 1 and the law is not expected to hold. Also: AUC of each level against
  m = 0, and the paired R4 - R0 shift against its prediction -0.693.
- Person-specific share of asymmetric energy (descriptive, per band): with E_A(R3)/E_A(R2w) = (P + N/2)/(P + N) and
  E_A(R4)/E_A(R2w) = 1/2 (P person-specific, N capture-specific energy), pi = 2 x median exp(L_R3 - L_R2w) - 1
  (paired per host); pi near 0 = asymmetry is capture-specific, near 1 = person-specific. The observed
  median exp(L_R4 - L_R2w) is reported beside its predicted 0.5.

**Session, pose, lighting and softness (confounds):**
- Session gap: R3 gap = days between H and S; R4 gap = days between H and B. K1 within registered strata gap <= 60
  days, 61-365, > 365 (both groups restricted to the stratum). FRGC environment (controlled / uncontrolled) of the
  partner photo reported per stratum.
- Same-session against different-session same-person morphs: R8 same-session against R8 cross-session (prediction
  of the competing explanation: same-session keeps more asymmetry), R4 (L) against R8 same-session (the key contrast
  at a matched zero session gap; different hosts, so unpaired), and R8 cross-session against L R3 (calibration of the
  two sets). Per engine and pooled. Expression change of the R8 same-session pairs (fa + fb) is reported.
- Yaw: K1 within tertiles of |yaw| (cut points from the pooled R3 + R4 items) and within tertiles of the pose gap
  |yaw(H) - yaw(partner)|; lighting gap |light(H) - light(partner)| tertiles likewise.
- Partial out: AUC of the OLS residual of L_k on (a) log Laplacian variance, (b) |yaw|, yaw, nose offset, lighting
  index, (c) both, fitted on the pooled items of the two groups of the contrast; and the AUC of log Laplacian variance
  alone (both directions shown). Descriptive reading: "softness explains the contrast" if the raw AUC is >= 0.70 and
  the residual AUC after (a) is < 0.60.

**Storage history** (paired shift d_k = mean(L_k(copy) - L_k(native)) / SD(L_k(native)), CI by bootstrap over
persons): **primary Fm E7 FaceMorpher**; secondary Fm OpenCV / Webmorph (differing copies only), Fe (four families),
Lsoft (R0 and R2w, two strengths), S (SMDD), Ds vs D (descriptive, frames differ). Cut-off: a copy shrunk by scale s
keeps frequencies below f_c = 0.5 s cycles/pixel of the native frame; band k counts as **below the cut-off** if its
whole support lies below it, k + 0.5 <= log2(f_c x IOD) (median s of the set). Registered expectation: |d_k| < 0.1 in
bands below the cut-off.

**GAN blocks:** x3 against x2 (key), x3 against x1, x2 against x1, x1 against x0; x3 against x2 split by the
same-session status of the x2 captures (colorFERET same date vs other). **Diffusion-autoencoder ladder (D):** B20
against C20 (key; C20 is a same-session mix), B20 against D20, C20 against D20, D20 against photo, B against D20;
P_AF against D20 (positive control, n = 4 smoke persons, or 32 when the AD1b full run is complete); X (secondary):
two against same, two against rec, same against rec, rec against photo, with session split.

## Pass and kill (fixed before the run; primary pool L, both engines pooled, Y, F0, bands B1..B5)

- **Kill**: AUC(R4 against R3) < 0.60 in every band B1..B5.
- **Pass**: at least one band k in B1..B5 with AUC(R4 against R3) >= 0.70 **and** history shift |d_k| < 0.1 on the
  primary history control (Fm E7 FaceMorpher) **and** the positive control collapses in that band: median paired
  exp(L_R3m - L_R2w) <= 0.25 and AUC(R3m against R2w) >= 0.95.
- **Weak**: everything else. Qualifiers reported beside the verdict (they do not change it): the lower CI bound of
  the passing band (above or below 0.60); whether softness or pose explains the contrast (partial-out readings);
  whether the same-session R8 comparison keeps the separation (AUC of R4 against R8 same-session >= 0.70 or not).
- GAN, diffusion and shape contrasts get descriptive readings with the same marks (>= 0.70 separates, < 0.60 does
  not), no verdict of their own.

## Guards

No detector score is opened; no network is trained. Allowed operations only: lossless flip and index maps, FFT band
energies and image differences computed in memory, constant-colour padding of a detector input in memory, landmark
detection. No image is written. No sealed file (names with fst, valx, A12SP) is opened (path guard in
`as0_common.guard`). FRLL persons are used only for measurement. Multiple bands, channels and contrasts are reported
without correction; the verdict uses only the registered primary cell.

## Stop rule and budget

CPU only, at most 2 processes at nice 10, BLAS / FFT threads 1-2; no GPU, no WCSS, no Athena. Landmark detection
about 45 min; measurement about 1 to 2 h; analysis minutes. Stop and report if the measurement has not finished by
23:30 CET (then report the sets that are complete, primary pool first).

## Commands (each tested on 8 images first)

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; cd /home/narolski/smad-next/src/AS0
$P -I as0_lists.py
OMP_NUM_THREADS=2 nice -n 10 $P -I as0_landmarks.py --threads 2 && $P -I as0_landmarks.py --merge
OMP_NUM_THREADS=1 nice -n 10 $P -I as0_measure.py --sets <sets> [--limit 8]
OMP_NUM_THREADS=1 nice -n 10 $P -I as0_analyse.py
```

## Pre-run review

Independent read of this file by the experiment-reviewer agent requested 11 Nov about 18:18 (CPU measurement; result
and any amendment recorded below with time, before any contrast is opened).

### Review result and amendments (11 Nov, 18:38 to 18:45 CET, before any contrast was computed or opened)

Reviewer verdict (experiment-reviewer agent, about 18:35): **GO WITH FIXES** (no rule violation). Record of timing
(fix 2): this file was first saved 18:17:27; the save at 18:21:55 changed only three time stamps in the header and in
the review line (from wrongly estimated times to the file times); its content was otherwise final at 18:17:27. After
18:17:27 and before these amendments the owner saw: 8-image test runs of `as0_measure.py` (L, Lsoft, R8, S; outputs
`meas/smoke_*` deleted unread at 18:21), and `check.json` (18:20:49), which holds the L vector of one AR1 camera photo
(host feret:00002) and synthetic checks. No contrast, no group statistic and no `meas/<set>_*.npz` file has been read.
Amendments (each fixed before any contrast):

- A1 (finding 1, geometry). Face geometry alone can lower the ratio of a two-person morph (its target shape averages
  two midlines). Added: partial-out (d) on shape asymmetry L_shape, the midline offsets at eye, nose and mouth level
  (from the 106-point fixed and paired points, in IOD units) and the mask size; reported as the qualifier "beyond
  geometry" (K1 residual AUC after (d)). Added per band the geometry share (L_R2wm - L_R0) / (L_R3m - L_R0) (paired,
  median; R2wm symmetrises the shape only). K4 (R2w against R0) is no longer predicted to be 0.5: the warp to the
  mean shape of two captures can lower the ratio. The decisive geometry-matched test (warp-only toward the H-B mean
  shape) needs new images and is proposed for phase 2.
- A2 (finding 3a). The cut-off scale of the E7 copies is relative to the 512 frame, not to the raw photo:
  s = min(1, alignment-input eye distance / 132) (132 px = the kps eye distance of the canonical frame); for Fm
  FaceMorpher this is about 0.47 (bands B1..B4 below the cut-off), for Fe s = min(1, family target eye distance / 132).
  Lsoft already used the 512-frame scale.
- A3 (finding 3b). History copies were re-aligned, so their geometry is not exactly the native one. **Primary**: each
  copy (Fm, Fe, Lsoft) and each Lsoft native uses its own detected landmarks (same detector); secondary: the native's
  landmarks for both (as first registered). Added the shift in units of the K1 effect, mean(L_copy - L_native) /
  (mean L_R3 - mean L_R4), and the Lsoft fm61 shift (same 61.2 px target, same pool and frame as K1) as a
  co-qualifier beside the binding Fm E7 FaceMorpher shift (whether Fm stays binding is left to the lead).
- A4 (finding 4, low-band leakage). Sensitivity run: everything outside M_sym (F0) set in memory to the mean colour of
  M_sym (constant-colour blanking), then the same FFT bands; Y and F0; sets L (R0, R2w, R3, R3m, R4) and Fm. K1 and
  the history shift are reported on it beside the primary numbers.
- A5 (finding 5). E_A is floored at 1e-12 x E_S before the logarithm (an almost exactly symmetric image can give
  E_A <= 0 numerically); floored items are counted and kept.
- A6 (finding 6). Dose curve: per-level median dL against the prediction reported beside the OLS slope (the slope on
  mean log ratios is biased toward beta < 1). Person-specific share: computed from the E_A ratio alone (pi_A) and from
  the L ratio (pi_L), reported as bounds; E_S ratios reported.
- A7 (finding 7). Session-gap strata also within each database; the R8 reading that informs the competing
  explanation is same-session against cross-session within colorFERET (the R4 against R8 same-session comparison
  mixes databases and is descriptive). The FRGC "environment" field is a camera id; reported as such.
- A8 (finding 8). canon512 uses the median IOD of its own genuine images (as registered per frame type; the code
  first reused the ar1_512 value); the SMDD landmark file is read from the byte copy
  `/mnt/t7/smad_next/AS0/inputs/` (sha256 f167eaf8...). Added (improvement 2): K1 on two person-disjoint halves of the
  hosts (split by sha1 of the host id) and per engine, for the passing band.

### Lead's additions (message of 11 Nov about 18:40, from the independent review of the identity-shrinkage triage (ID0), `experiments/reviews/REVIEW_ID0_20261111.md` sections 2 F3, 3, 4), registered 18:45 before any contrast

- A9. Statistics computed from the mean of two source landmark files (the exact-shape asymmetry of L and R8, and of the
  graded set) are arithmetic, not evidence about morph images. They are kept and labelled "calculated from source
  landmark files"; only pixel-band statistics on the built images, and statistics on landmarks **detected** on the built
  images, test the idea.
- A10 (review hypothesis H-new-2, shared arm). The 106-point landmarks are detected (the same insightface buffalo_l
  detector, unchanged, CPU) on the built ladder images: R0, S0, R3, R4 (both engines) first, then R2w, R3m, R2wm,
  then the graded set. On the detected shapes: (a) the identity-shrinkage triage's typicality score (ID0 `iss.py` and
  its landmark-arm fit, imported unchanged; fit photos and generalised Procrustes reference exactly as in ID0
  `analyse.landmark_features`), contrast same-person morph (R3) against two-person morph (R4), AUC = P(score R4 > score
  R3) (two-person more typical); exact-file value 0.687; **prediction (review) >= 0.65; falsified below 0.60**; (b) the
  shape-asymmetry statistic L_shape of this registration (K1 and the other L contrasts on detected shapes).
- A11 (external prediction, review H-new-4). Best band of K1 (two-person against same-person) lands at 0.58 to 0.70,
  with dose slope below 0.7; falsified by any band at 0.75 or more with slope at least 0.7. Recorded here as an external
  prediction; the registered verdict rule is unchanged.
- A12. The 8 validation-reserved persons (rule `prep_train.is_val`, through ID0 `id0_common.is_val`) are dropped from
  everything fitted on the ladder (the partial-out regressions); every L contrast is reported with and without items
  that contain one of them (as host or partner).
- A13. All 536 primary-pool same-person pairs are cross-session, so the same-person rung R3 already contains session,
  pose and lighting change; this is stated wherever the pose and lighting confound is discussed, and the yaw
  stratification is still reported.

## Result

(to be written in `result.md`; README.md holds the full record)
