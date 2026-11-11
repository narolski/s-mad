# Ideation round 3: what the lead takes from it

11 Nov 2026, 19:05 CET. Five lenses each proposed up to three ideas from today's numbers; each set was
then attacked by a hostile reviewer (novelty search, cheapest confound, feasibility by 14 Nov). Brief:
`ROUND3_BRIEF.md`. Full write-ups: `round3/<lens>_ideas.md` and `round3/<lens>_vetting.md`. Raw
structured output: `ROUND3_raw.json`. The four cross-field analyses (deepfake, GAN-image, anti-spoofing,
diffusion portraits) are still running and will be folded in as section 6.

Numbers marked "unreviewed" come from owners' records read by the reviewers; they are leads.

## 1. Outcome in one paragraph

No idea survived unchanged: 11 were revised, 2 dropped, none kept. The reviewers converge on one
method and one honest claim. The method is a **training-data protocol on the standard recipe** (CLIP
with LoRA, as in MADation): the genuine class contains everything a morph has been through except the
mixing (the morph's own warped halves, warp-only images, stored-small copies), the morph class
contains two-person morphs and their stored-small copies, the threshold comes from camera photos, and
every result is read at one fixed threshold. The claim is **the lowest miss rate at a fixed threshold
among detectors that pass the storage and softness controls**, not "state of the art on the published
tables". New loss terms, layer selection, canonical input sizes and physical statistics were all
reduced to evaluation rows or dropped.

## 2. The cards

| Lens | Idea (plain name) | Verdict | What remains of it |
|---|---|---|---|
| Paired differences | Self-morph ladder training | revise | Becomes extra arms of the SMDD rebuild (SM1): one-person blends against renders; with exact warp-only twins; with crossed storage history; with two-person morphs. Normal two-class loss. Mirror partner only if it passes a symmetry test |
| Paired differences | Noise-only mirror mix for diffusion morphs | revise | A small audit of which input makes a diffusion morph look like a morph; no training use |
| Paired differences | Dose-matched second-identity test | revise | A reporting control: score against measured in-face disagreement for same-person and two-person blends, valid only where the morph still verifies against both contributors |
| Frozen features | Three-level ordinal score on trace-matched twins | revise | A three-arm comparison on the landmark family; the ordinal label is kept only if "two persons above twin" survives a warp-size control |
| Frozen features | Code-factorised one-person twins (diffusion, GAN) | revise | Audit instrument only |
| Frozen features | Ladder-selected layers with a nuisance eraser | drop | Frozen features already carry storage history; nothing to erase where measured |
| Physics | Layer-count evidence (two textures against one softened texture) | revise | The **bracketing test** (a morph must outrank a sharper and a softer negative of the same host) becomes an evaluation instrument for every detector; the statistic gets one CPU test |
| Physics | Left-right parity ratio | revise | One evidence row inside the running mirror-asymmetry test (AS0) |
| Paper network | Ladder-based training of one CLIP ViT-L/14 LoRA network | revise | **The method candidate** (section 4) |
| Paper network | Canonical-band network at the smallest storage size | revise | A measurement (size sweep), not a network |
| Paper network | SMDD-only ladder set | revise | The comparable "SMDD-only" row and a releasable set; no GAN family in training |
| Nuisance removal | False-alarm limit for every storage history | revise | Environment-balanced batches and a genuine-side margin; shown only if the usual loss violates the limit first |
| Nuisance removal | Train only on what the cues cannot explain | revise | An acceptance test for training sets and optional weights |
| Nuisance removal | Canonical view | drop | Removes a cue the leading recipe does not use |

## 3. Programme-level points raised by the reviewers (each changes something)

1. **The storage-history failure is not shown for the ViT-L/14 recipe.** In existing score files the
   ViT-L/14 recipe retrains flag 0% of 23 genuine pools at their own rule (and detect 0% of AMSL), and
   at most 4.9% of any full-frame shrink-history pool at the development threshold; they do fail on
   JPEG quality 50 (23 to 50%) and on the tight MorDIFF frame (43 to 76%) (unreviewed reads of the
   fixed-threshold re-read, EV1). Storage history is a SelfMAD and ViT-B/16 result. The chain "failure,
   then a protocol that removes it" must be shown on a recipe where the failure exists, and a fixed-rule
   table must always print flag rate and miss rate together.
2. **The softness control is one-sided today.** Softened copies exist only for unmixed images. Needed:
   stored-small copies (61.2 and 112.7 px) of the ladder's two-person and same-person morphs, built
   with the approved shrink-and-enlarge path. One CPU job; serves three first tests.
3. **The mirror self-blend is not a matched twin.** A symmetry score isolates it perfectly, a 32-pixel
   thumbnail separates it from a two-person morph at 0.93, the background alone at 0.90 (unreviewed).
   It may serve a trace contrast only, never a second-person claim, also in the diffusion and MIPGAN
   generation jobs.
4. **"Second person" has no clean measurement yet.** It is confounded with warp size. Cheapest missing
   control: a warp-only image moved toward the two-person mean shape (approved warp path, CPU minutes).
5. **No route to the published level on generator cells without training a generated-image detector.**
   Twin-trained frozen heads reach 31 to 39% EER on the published GAN cells and equal PNG file size on
   diffusion morph against camera photo (unreviewed). The paper reports those cells under both class
   policies and makes no state-of-the-art claim there.
6. **"Tops the published tables" cannot be claimed as written**: published MAD22 values are on the
   original release, we score the corrected copy; the same release moves 0.4 to 1.5 points between two
   machines; one genuine photo of 204 is 0.49 points.
7. **Frozen-head tests cannot clear a LoRA network.** Decisive tests need real ViT-B/16 LoRA fits (0.87
   A100-hours each, measured). Athena makes this cheap.
8. **Corrected MAD22 FaceMorpher is not evidence of morph detection without blanking**: a network that
   never saw a morph reaches 0.55% EER there under the history control.
9. Everything measured today reads "two captures were averaged". The paper should use those words.
10. Notebook entries of the lead between 17:15 and 17:40 were stamped up to 15 minutes ahead of the
    machine clock.

## 4. The method candidate ("protocol network"), as vetted

- One CLIP ViT-L/14 LoRA network, the registered MADation recipe, last checkpoint, no selection. One
  seed is named in advance as the paper's network; four more give the spread.
- Genuine class: camera photos, SMDD renders, warp-only images, the morph's own warped halves, and the
  61.2 px stored copies of these. Morph class: two-person morphs and their 61.2 px copies. One-photo
  generator output is genuine (class policy A). Mirror and same-person blends are never trained on and
  are reported in the single-subject table.
- No new loss in step 1. An equality term between genuine views of one host is written only if the data
  protocol passes the signal marks and fails the shift mark.
- Ladder persons are split in advance: 200 hosts test, 100 hosts development; none in training.
- Threshold: 5% false alarms on every development genuine pool with at least 60 px between the eyes.
- Reported: fixed-threshold miss per family with all history-matched pools protected (headline); the
  crossed softness contrast; excess over the best simple statistic; the bracketing test; both class
  policies on generator cells; released detectors through their own crop on the same files.
- Reference rows on the same data: the recipe on released SMDD; our data without halves and stored
  copies; history-only and label-permuted networks.

First tests: tier 0 tonight on frozen features (CPU); tier 1 on Athena: four ViT-B/16 LoRA fits, manifest
A (photos against morphs) against manifest B (the protocol), about 5 A100-hours. Then a ViT-B/16 screen
(8 configurations, 3 seeds), the frozen configuration at 5 seeds on ViT-L/14, and eight ablation rows:
about 270 A100-hours in total.

## 5. Decisions

Taken by the lead (say if wrong):
- The three class categories of `14_CLASS_DEFINITIONS.md` are the working rule for table layout until the
  author rules: genuine; morphing attack (two or more persons); single-subject manipulation (reported
  separately).
- Warp-only images are genuine (the author's rule: a processed genuine image called a morph is an error).
- New owner for the protocol network (PN1); the softened ladder copies and the warp-only rung toward the
  two-person mean shape are added to the running experiments.

Needed from the author:
1. May the existing registered processing function be run unchanged with its JPEG, blur and 50%
   resample branches on training images? Without it nothing teaches the network that JPEG compression is
   not a morph, and the ViT-L/14 recipe fails exactly there.
2. Yes or no on the three class categories.

## 6. Cross-field analyses

Pending (`../literature/crossfield/`).
