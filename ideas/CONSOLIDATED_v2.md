# Ideation round 2: what the vetting changed

11 Nov 2026, late evening. Seven agents attacked the consolidation of round 1 (`CONSOLIDATED_v1.md`):
three novelty checks, one check against our own record, three hostile reviews (CVPR area chair,
image forensics, morph detection community). Raw output: `ROUND2_vetting_raw.json`. This file states
what the lead accepts from it. Nothing below has been run unless a line says "measured".

## 1. What does not survive

| Claim in round 1 | Why it falls | Source |
|---|---|---|
| "The blend-evidence target is zero for any one-capture image, so no image-constant cue can predict it, including unlisted cues" | True of the labels, not of the image. Blending two warped faces roughly halves fine-detail energy (measured: 0.52 times the Laplacian variance of the morph's own warped halves), and that single number separates a morph from its own halves at AUC 0.76 at 512 px and 0.87 at 224 px. The registered pass marks (0.75, 0.85) sit at that floor. With a pooled score and all-zero negatives, "a global flag times an anatomy template" also fits the target | forensics reviewer (measured on the landmark ladder images), area chair |
| "The target is small for same-person blends" | A photo blended with its mirror already carries 40 to 76% of the two-person value. The map reads blending of two captures, not a second identity | forensics reviewer (measured) |
| "The measured-disagreement target is new" | It is the Face X-ray map 4·M·(1−M) multiplied by a source difference. Pixel-wise supervision exists in morph detection (PW-MAD, constant map), and partial morphs with region labels exist since Seibold et al. 2018. What was not found: the measured, content-dependent target, the planted-confound test, and warped halves as declared genuine images. One paper (Qin, Peng, Long, TIFS 2022) could not be read and may be closer | novelty check |
| "A frozen encoder protects" | In our record the frozen-encoder MADation ViT-B/16 release rises 6 to 13 points on landmark cells and 21 to 29 on diffusion cells under the history control. Frozen ViT-L/14 is supported only for reading the mixing step of diffusion morphs | record check |
| "The bar to beat is 1.0 / 1.0 / 14.7 / 4.4% (released MADation ViT-L/14 on FRLL landmark cells)" | Those are numbers on our own frames. Published values are far lower (AMSL 7.26 for ViT-L/14, 3.85 for ViT-B/16). Our frames do not reproduce the releases | morph detection community reviewer |
| "SMDD's two classes have disjoint identity pools" as a finding | It is the documented design. The new part is five partners in total per split, where the paper reads as five per key image. SMDD-trained detectors reach 0.42 to 2.51% on the evaluation split, which has five other partners, so "they detect five faces" is unlikely as a main explanation | novelty check |
| "Identity-shrinkage closed form gives the ceiling" | Algebra right, but not a ceiling: on exact landmark geometry a fit on genuine photos overshoots by 0.11 to 0.14 AUC, and same-person averages show the effect too | forensics reviewer (measured) |

Also withdrawn earlier today after independent reviews: "detectors use the expression cue" (the
smiling FRLL photos also differ in capture detail) and two summary sentences of the first ladder
re-reads.

## 2. The structural objection, and the answer

The area chair's main point: the audit shows cue dependence on diffusion and GAN cells, where the
blend map is silent by design; the method claims state of the art on landmark cells, where the audit
has not shown the leading baseline to fail. The two halves do not meet.

Accepted. The paper is rebuilt around one chain that holds on the same cells:

1. **Measured failure of released detectors that needs no class ruling**: false alarms on genuine
   photos after benign processing at one fixed threshold (resize and storage history; a photo merely
   stored small is flagged by the SelfMAD release in 203 of 204 cases), and the dependence of
   benchmark numbers on the smiling half of the genuine class. On each release's own preprocessing,
   with published numbers reproduced, on at least two photo pools.
2. **A training protocol that removes that measured failure**: pipeline-matched and history-crossed
   training data on the standard recipe (the SMDD rebuild arms), judged by the same measurements.
3. **The blend-evidence map** stays as a candidate component and is kept only if it passes the
   controls of section 3. It is no longer the headline.

Generator cells are reported under both class policies (a one-photo reconstruction counted as genuine;
counted as inadmissible), for every detector including ours, with no verdict words.

## 3. Controls the alpha-field probe (AF0) must pass before the map is used

| Control | Pass |
|---|---|
| Sharpness floor: Laplacian variance alone, morph against its own halves | every reported AUC is given as excess over this floor |
| Softened genuine images: native-to-history-matched shift of genuine scores, mean and top-tenth pooling | at most 0.3 standard deviations; flag rate at the 5% threshold at most 10% |
| Template baseline: correlation of each true map with the mean training map | reported beside every map correlation; map correlation after removing the template at least 0.2 |
| Pair swap: predicted map against its own target minus against the target of another morph with the same host | lower bound above 0.10 |
| Shuffled maps: refit with target maps shuffled between positive images | image-level AUC or history shift must get worse; otherwise the map is decoration |
| Five-arm ablation: image label with photos; image label with halves; constant map with halves; measured map with halves; measured map with photos | measured map with halves beats image label with halves by 0.03 AUC or halves the history shift |
| Target sanity: value on flat against busy patches; correlation with the patch's own contrast | flat below busy; contrast correlation below 0.3. The registered contrast-normalised target fails this (highest on flat skin) and is replaced by a variant that excludes flat regions |
| Border cue of stored halves (black bands) | blank identical regions in both classes |
| FaceMorpher is descriptive only (its morph pastes onto a double-exposed surround) | the OpenCV-style engine and the approved Poisson path decide |

Needs the author: sharpness-matched negatives require either the existing shrink-and-enlarge path run
on new images or a blur; neither is run without a yes.

## 4. New or changed experiments

| Experiment | Why | Compute |
|---|---|---|
| Own-crop re-score of the audit rows (RS1): each release through its own preprocessing on the FRLL landmark cells and the MorDIFF ladder, native and history-matched; accepted only where the published number is reproduced within 1.5 points or 25% | every audit row about released detectors depends on it | about 1 GPU-hour |
| SMDD partner tests with no new image (added to the SMDD audit, SM1): training split against evaluation split miss rates; rank of the five partner renders among 25,000; then the paired audit and a partner-count dose curve | decides whether the five-partner property matters | minutes |
| Both class policies and a per-pool false-alarm block (added to the fixed-threshold re-read, EV1) | removes the dependence on the class ruling | CPU |
| Identity-dose slope is run with two controls (the morph-free network and file size) | "construction cannot fake this" was false as written | CPU |
| History control on a second photo pool (AD3) moves up | "everything rests on 204 photos" | scoring |

## 5. For the author

1. SMDD's terms appear to require that morphs derived from it are published and shared with its
   authors. The rebuild arms are derived morphs. Internal use for the paper is one thing; releasing
   the rebuilt set would need their agreement.
2. Three statements about other groups' releases should not be printed without asking them, or must
   be worded as unknown: the SelfMAD checkpoint selection, MADation "reading the benchmark", and the
   five-partner structure of SMDD. The author ruled earlier against emailing method authors; say if
   that changes for these three points.
3. May the existing shrink-and-enlarge path be run unchanged on training photos, warped halves and our
   own morphs? Without it nothing in training teaches a detector that softness is not blending.
4. The three-category class definitions (`../14_CLASS_DEFINITIONS.md`) still await a yes or no.
