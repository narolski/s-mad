# What is a morph, what is a genuine image, and what is neither

11 Nov 2026. Answer to the author's two questions, from a literature check in which every cited
claim was re-opened by a second, independent agent (five topics, 126 claims checked: 98 confirmed,
21 partly, 2 wrong and corrected, the rest not reachable). Raw material with quotations and links:
`literature/class_definition_check_raw.json`. Proposal at the end; it needs the author's yes.

## 1. What the sources say

### Definitions count subjects

Every formal definition that could be opened defines a morph by two or more people:

- ICAO Doc 9303, Part 2: "two or more subjects' faces are morphed or blended together to form a single
  face in a photograph".
- NIST FATE MORPH (report updated September 2026): the same sentence; "all morphs are created with two
  subjects"; the other class is "bona fide (nonmorph)".
- ISO/IEC 20059:2025 (the morphing evaluation standard), introduction: references "manipulated to match
  two or more biometric data subjects". Only the preview could be read; the term definitions (clause
  3) are behind a paywall, so the standard cannot be quoted on the one-subject case.
- ISO/IEC 30107-1:2023, the FVC-onGoing S-MAD benchmark ("mixing faces of two subjects"), and the two
  main surveys (Scherhag et al. 2019; Venkatesh et al. 2021: the attack "breaks the rule of single
  ownership").

None of them discusses a morph made from one person. Read literally, such an image is not a morphing
attack, because only one person can verify against it.

### Same-person morphs: two opposite labelling habits, never argued

| Label | Who | Reason given |
|---|---|---|
| Genuine ("selfmorphs" of two photos of one person) | One group, five papers 2022 to 2025: MorDeephy (ICPRAM 2023), Pimenta et al. (BIOSIG 2023), Medvedev et al. (WACV Workshops 2024; IWBF 2024), MorphGuard (arXiv 2505.10497). Origin of the device: Borghi et al., IEEE Access 2021 | identity is unchanged; the detector should rely on identity features, not on merging artefacts. Their own evidence of benefit is mixed |
| Attack (two photos of one person, morphed) | Kashiani et al., IJCB 2023 | attacks with few visible artefacts, as training augmentation |
| Attack (one image blended with a transformed copy of itself) | SelfMAD (FG 2025), following self-blended images in deepfake detection (CVPR 2022) | a stand-in for real attacks; the detector should learn traces of the process |

All of this is training-set design. Nobody evaluates on such images with a label, nobody cites the
opposite habit, and nobody states a definition. A photo morphed with its own mirror image was not
found anywhere in the morph detection literature (it is a standard stimulus in face perception).

### One-photo reconstructions: no convention

- Standards and NIST are silent. NIST's genuine class is real photographs only (live captures and a
  printed-and-scanned subset); it contains no synthetic or reconstructed image.
- ICAO separates two risks, "photo manipulation" and "morphing", and lists the admissible processing of
  a portrait: in-plane rotation, cropping, down-sampling, white balance, colour management, one raw
  conversion, compression. A portrait must "not be digitally altered or enhanced to change the
  subject's appearance in any way". A generator reconstruction is therefore not admissible processing,
  and it is also not called morphing.
- Inside morph detection there are precedents for treating generated single-identity images as
  genuine: SMDD's genuine class is fully synthetic, and Zhang, Ramachandra, Raja and Busch (CVPR
  Workshops 2024) add GAN-reconstructed genuine images "to reduce the bias between bona fide and morph
  samples". One lab takes the opposite line and treats deep-morph detection as synthetic-image
  detection (Colbois and Marcel).
- In generated-image detection the majority rule is the reverse: a real image passed through a
  generator is the fake class (DRCT, Aligned Datasets, B-Free, Dual Data Alignment). A minority keeps
  it real, and one paper proposes a third, "laundered" class.
- No source says how a morph detector should be scored on a one-photo reconstruction.

### Processing of genuine photos

Giving both classes the same processing is established advice in part of the literature (same resize,
compression and print-and-scan on both classes: Scherhag et al. 2020, the SOTAMD and NTNU sets), and
NIST reports a quality-matched genuine error rate. This supports treating crop, resize and compression
of a genuine photo as benign, and it means our history-matched control has precedent.

## 2. Answers to the two questions

1. **Is a same-person morph or a mirror self-morph a morph?** By every formal definition, no: a morph
   needs two or more subjects. In research practice the label is split and the choice has never been
   discussed. There is no stand to follow; there is a gap to name.
2. **Is a one-photo reconstruction a matter for a morph detector?** No convention exists. Definitions
   place it outside "morphing"; ICAO places it outside admissible processing; the neighbouring field
   treats it as its own detection task. Scoring it for or against a morph detector is not supported by
   any source.

## 3. Proposal: three categories, the same for every detector

| Category | Definition | In our ladder | Role in results |
|---|---|---|---|
| Genuine | one capture of one person, with admissible processing only (crop, alignment, resize, compression, colour management, print and scan) | camera photo; history-matched photo | negative class of every morph detection error rate; flagging it is an error |
| Morphing attack | an image that combines two or more persons, by any method | two-person morph | positive class |
| Single-subject manipulation | any other alteration that involves one person only | tool or generator run on one photo (reconstruction), warp-only image, mirror self-morph, same-person morph | never in a morph detection error rate; reported in its own table as "where the detector places it", for every detector including ours |

Consequences:

- **Benchmark shortcut** = a cue that separates genuine images from attacks in a benchmark and
  disappears under admissible processing or balanced composition: resolution history, storage,
  format, frame, colour, expression balance, photo source, and on the training side the five
  recurring partners of SMDD.
- **The single-subject table is a description, not a verdict.** It answers "what does this score
  respond to": for example, that on diffusion morphs the released detectors place one-photo
  reconstructions with the morphs, so those benchmark cells measure generated-image detection.
- **The identity step** (single-subject output of a pipeline against a two-person morph of the same
  pipeline) is reported as the morph-specific part of a detector's response.
- Our own detector is treated identically: its blend map will respond to same-person and mirror
  morphs, and that goes into the single-subject table, not into its detection rate.

For the paper's discussion section: formal definitions count subjects; labelling practice for
one-subject morphs is split and undiscussed; no protocol says how to score single-subject outputs; we
propose reporting them as a third category.

## 4. Not verified

- ISO/IEC 20059:2025 clause 3 (terms) and clause 5; ISO/IEC 39794-5 values.
- The Bologna group's treatment of same-subject morphs in an IWBF 2024 paper (seen in slides only).
- "No morph detection paper uses a mirror self-morph" rests on searches, not on proof of absence.
