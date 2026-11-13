# ADV floors: one line per contrast (standing adversary)

Registration: `prereg.md` with amendments 1 and 2. Every number here is copied from the committed JSON in `floors/`
(`floors/<contrast>.json`; held-out scores `floors/<contrast>_heldout.csv`; frozen by `floors/pins_stage<k>.sha256`).
Development data only. No network score was read to make this page.

How to read a line:
- **ADV floor** = the best of three cross-fitted shortcut-only models (single statistic, logistic regression, boosted
  trees) on all 72 features, persons kept apart; 95% person-cluster interval. **Nuisance floor** = the same on border,
  resolution, storage and rendering features only (no 27 statistics, no blend features).
- **Must exceed** = the arm's network must exceed the floor by the registered rule (`src/adversary/check.py`
  `exceeds()`: 2.5% bound of network AUC minus floor AUC, same person draws, above 0). Quick bar: the floor's upper
  bound; a network AUC below it cannot pass.
- The ADV floor is printed beside an arm's own registered floor; it never replaces it.
- **Ceiling** lines (both sides genuine) say how visible a nuisance is to shortcut features; no exceeds rule.

## Stage 1a (lcomb and the test ladder)

| Contrast | Arm read | Rows (pos / neg; components) | ADV floor [95%] (model) | Carried by | Nuisance floor [95%] | Pixel-only floor | In-sample best single (27 stats; all) | Must exceed (quick bar) |
|---|---|---|---|---|---|---|---|---|
| `lcomb` | Second engine H-fm1; Sbx, GX1, RZ1 guards; E3 contrast 1; SA1 row 18 | 1000 / 2000; 3000 | 0.982 [0.978, 0.986] (logreg) | F27 (alone 0.952) | 0.964 [0.958, 0.970] (gbt) | 0.982 | 0.886 (noise_std_face); 0.889 (RENDER:resid_corr_gb) | > 0.986 (ADV), > 0.970 (nuisance) |
| `test_fm_R4_vs_R2w` | Second engine H-fm2 | 191 / 191; 130 | 0.993 [0.987, 0.998] (gbt) | RENDER (alone 0.973) | 0.996 [0.992, 0.999] (gbt) | 0.993 | 0.880 (b3_.125-.25); 0.880 (F27:b3_.125-.25) | > 0.998 (ADV), > 0.999 (nuisance) |
| `test_cv_R4_vs_R2w` | Second engine H-fm3 (guard) | 191 / 191; 130 | 0.990 [0.981, 0.997] (gbt) | RENDER (alone 0.975) | 0.986 [0.974, 0.994] (gbt) | 0.990 | 0.876 (b3_.125-.25); 0.876 (F27:b3_.125-.25) | > 0.997 (ADV), > 0.994 (nuisance) |
| `test_fm_R4_vs_R3` | Second engine, printed engine table | 191 / 191; 130 | 0.796 [0.762, 0.832] (logreg) | F27 (alone 0.737) | 0.725 [0.683, 0.769] (logreg) | 0.799 | 0.653 (b2_.063-.125); 0.653 (F27:b2_.063-.125) | > 0.832 (ADV), > 0.769 (nuisance) |
| `test_cv_R4_vs_R3` | Second engine, printed engine table | 191 / 191; 130 | 0.774 [0.737, 0.813] (logreg) | F27 (alone 0.775) | 0.692 [0.646, 0.736] (gbt) | 0.769 | 0.670 (b2_.063-.125); 0.670 (F27:b2_.063-.125) | > 0.813 (ADV), > 0.736 (nuisance) |

Regression gate (amendment 2 F3): on `lcomb` the in-sample best of the 27 statistics is noise_std_face 0.8856, which
reproduces the reviewed 0.886 (gate passed; `floors/lcomb.json` `regression_gate`). Frozen by `floors/pins_stage0.sha256`.
These floors were computed before any read of SbFM, Sbx, RZ1 or E3 (none of their results has been opened).

What these lines say, plainly:
- **FFHQ landmark_combined (`lcomb`).** Shortcut cues alone separate these morphs from their resolution-matched
  genuine photos at 0.982 when fitted on other persons of the same rows; border, resolution, storage and rendering cues
  alone (no blend statistics, no 27 statistics) reach 0.964. The frozen candidate's 0.873-0.906 (seeds 408-412,
  reviewed) lies far below both. A second single statistic, the cross-channel noise-residual correlation, already
  reaches 0.889. A network has to exceed 0.986 (ADV) or 0.970 (nuisance) for a gain on this set to count beyond
  shortcuts. This set is dominated by a rendering/processing difference between the two sides.
- **Test-ladder R4 against warp-only R2w, both engines.** Shortcut cues reach 0.99 and nuisance cues alone 0.986-0.996:
  the two-person morph and its warp-only image differ in rendering and resolution statistics (blending softens), so a
  high network AUC here is not evidence of a second identity.
- **Test-ladder R4 against same-person morph R3.** With blending on both sides the floor falls to 0.774-0.796 (nuisance
  0.692-0.725); this is the most informative of the five: a network above 0.81-0.83 on these rows shows something the
  listed cues do not.


## Attack sets (requests to the DATA role through the lead; nothing built by the adversary)

Only allowed operations: the approved warp `h1_build.py`, the unchanged OpenCV and FaceMorpher morphers, constant-colour
region blanking, existing E7 outputs, lossless PNG. Items marked "author" need an operation that is the author's to
allow.

**Second-engine arm (SbFM).**
1. FaceMorpher same-person morphs and FaceMorpher warp-only images of new development hosts, at the same counts as the
   FaceMorpher R4 rows (morpher unchanged). Breaks the claim if SbFM's FaceMorpher gain is an engine-signature prior:
   it would flag these as often as R4.
2. Two-person FaceMorpher and OpenCV morphs of look-alike pairs (LA1 pairs, contributor cosine in the top decile) beside
   random-pair morphs of the same hosts. If detection rests on blend energy rather than two identities, look-alike
   morphs (low blend difference) are missed.
3. Self-morphs and warp-only images of FFHQ hold-out photos made with the unchanged OpenCV morpher at landmark_combined's
   frame (FFHQ, 1024 source): if SbFM's landmark_combined gain is a processing-history cue, it flags these too.

**Border-crossed arm (Sbx).**
1. The same camera photos and FFHQ photos with constant-colour borders of a non-black colour (mid-grey 128, white 255)
   and the same TT1 mask geometry. If Sbx learned "exactly-black region = ignore", the reaction returns at grey/white.
2. Border-blanked morphs: development R4, S4 and landmark_combined morphs with the same masks (Sbx trained bordered
   attacks at 25%). Tests whether detection survives the border and whether the border shifts misses (surround cue).
3. Masks from the largest-fraction TT1 frames (masked fraction above 0.55) that reach the face hull: partial-face
   blanking on camera photos and morphs; separates a border cue from a face-content read.

**GAN arms (GX, GXp).**
1. Look-alike two-person MIPGAN morphs (unchanged generator, LA1 pairs at contributor cosine above 0.30) against R3 of
   the same hosts: if GX's R4-vs-R3 separation rests on contributor dissimilarity, it collapses here.
2. A stratification product (no new image): GX1 held-out R4 and R3 rows binned by the latent distance from the mean
   code (PD1's "closeness to the mean latent" signal) and by contributor cosine, so the read can be taken at matched
   latent spread.
3. R3 made from two photos of one person with the largest available session gap (FERET fa/fb across years) against R4
   with small appearance difference: a same-person pair with large appearance change should not be flagged.

**Resolution and resize study (RZ1).**
1. Storage copies at sizes inside the mixR band (eye distance about 80-95 px), genuine and morph: existing E7 outputs if
   any exist at those sizes; otherwise **author** (new storage size). Tests whether the mixed-kernel arms learned
   invariance only to the trained band; morphs stored in-band could evade.
2. JPEG-history development genuine photos and morphs (**author**: JPEG re-encoding of development images, decision 5
   of the evening conclusions).
3. For the crop arms: "inverse splices" (two-person blend outside the face hull, warp-only inside), built with the
   existing PN1 splice code and swapped masks, if the lead rules that it is within the approved splice operation.
   A crop arm that "detects" these reads the hull edge or jaw, not the face.

**DINOv3 programme (E3, E2).** No new build needed first: the existing face-only same-person splices (S3_bg) against
S4_bg (identity on the face-only read), the border-blanked camera photos, and the GD2 one-photo renders. If those
show the CLIP pattern, request the SbFM and Sbx attack sets above for DINOv3.

**Frozen candidate (Sb).** 1. Look-alike two-person morphs against same-person morphs matched on BD1's D. 2. Grey and
white constant borders (as Sbx 1). 3. Border-blanked morphs (as Sbx 2).
