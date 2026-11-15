# Audit plan: closing the shortcut question per morph family

Answers the author's points (a), (b), (c) of 11 Nov. Status: proposal, revised after the pre-run
review of 11 Nov (verdict: go with fixes; all fixes are in this version). Nothing launched.
GPU-hours are estimates. All MAD22 numbers use the corrected MAD22 only
(`10_ASSET_INVENTORY.md`, section B).

Terms. AUC = area under the ROC curve, 0.5 is chance. EER = equal error rate. d′ = distance between
two score distributions in standard deviations. E7 = the existing, approved control that gives the
genuine photos the same shrink-and-enlarge history as the morphs. FR = face recognition.

## One ladder for every family

A benchmark cell compares morphs with camera photos. Between those two lie three kinds of
intermediate image. Scoring all five tells us which step the detector reacts to.

| Rung | Image | Made how |
|---|---|---|
| R0 | camera photo, as in the benchmark | — |
| R1 | camera photo with matched history | existing E7 output only; no new code |
| R2 | pipeline-only | the tool or generator run on one photo (mixing 0, or A with A) |
| R3 | twin | the tool or generator run on two photos of one person |
| R4 | morph | the tool or generator run on photos of two persons |

| Step | Name in the paper | Counts as |
|---|---|---|
| R0 → R1 | benchmark construction cue | shortcut |
| R1 → R2 | processing trace on a genuine image | shortcut: a genuine photo that was only processed is not a morph (author, 11 Nov) |
| R2 → R3 | morphing of two photos of one person | morphing: the method was applied (author, 11 Nov); studied as a side problem |
| R3 → R4 | second identity | morphing |

For each detector and family the table gives the AUC of each step and its share of the benchmark
separation (step d′ divided by d′ of R0 vs R4). The sentence "uses a benchmark cue" covers the
R0 → R2 share, with its two parts printed. The morph signal is the R2 → R4 share, with its two parts
printed. For generators, R2 is the reconstruction of one photo (inversion and render, or the
optimiser with A = B); it is treated as a processed genuine image, and this reading is printed beside
every generator cell so it can be judged.

### Amendment, 11 Nov 15:40 CET (before any landmark ladder score was read)

Measured: for the landmark tools, "tool on one photo" returns the photo itself (OpenCV: pixel-identical
on 60 of 60 files; FaceMorpher: within 1 grey level). R2 as defined is therefore R0 for this family.
Two rungs are added for landmark tools; the verdict rules apply with R2w in place of R2.

| Rung | Image | Made how |
|---|---|---|
| R2w | warp-only | the host photo warped by the tool's own routine to the mean shape of the host and its same-person photo; texture from the host only; no blending |
| R3m | mirror self-morph | the host photo morphed with its own mirror image by the unchanged tool; one photograph, one person, real warp and real averaging; no expression confound |

R2w is the "processed genuine image" for landmark tools. Whether R3m counts as a morph or as a genuine
image is the author's call (same question as for same-person morphs); it is reported as its own rung.
Also registered now: the clean-negative test CN0 and the mirror-distance score (definitions and fixed
verdicts in the lead's message to the AF0 owner, copied into `experiments/AF0/result.md`).

### Composition rule for twins

R3 and R4 always use the same tool, the same host photo A, and the same kinds of photo on both sides:
morph(A, B) against twin(A, A′), where A′ and B are both neutral and both from a different session
than A. Every B also appears as host of its own twin. Primary pool: FRGC and colorFERET (several
neutral sessions per person). FRLL has only one neutral and one smiling photo per person, so on FRLL
the pair is morph(A neutral, B smiling) against twin(A neutral, A smiling); it is the benchmark-linked
secondary pool. Published benchmark morphs enter only R0 vs R4 and a bridge number: published morphs
against our own same-pair morphs, expected near 0.5 (A43 found 0.505).

### Gates before any verdict

- **G-a, reproduction.** The detector's benchmark number is within 3 points EER of the published one;
  otherwise the cell is "not reproduced, descriptive".
- **G-b, twin validity (P1).** An FR oracle that knows the contributors separates morphs from twins
  at AUC ≥ 0.90; morphs verify against both contributors in ≥ 70% of cases at a false-match rate of
  1 in 1,000; twins verify against A. Negative control: twin(A, A′) against twin(A′, A) sits at 0.5.
- **G-c, readability (P2).** A probe trained on frozen features to separate morphs from twins,
  5-fold by person. If it stays below 0.65 the wording for that cell is "neither the released
  detectors nor a probe trained for it read identity blending", never "the detector failed".

Both controls are computed before any detector score is opened.

### Verdict rules, fixed here

Main verdict, on R2 vs R4 (processed genuine image against morph), with a 95% two-way bootstrap over
persons (the `a41_read.py` method):

- **Reads morphing:** AUC ≥ 0.75, lower bound above 0.65, and R0 → R2 share ≤ 0.2.
- **Reads the benchmark:** R0 → R2 share at least 0.5 (lower bound), or R2 vs R4 AUC folded around 0.5
  below 0.60 with upper bound below 0.65.
- **Mixed:** anything else, with the four shares.

Side study, on R3 vs R4 (does the detector need a second person, or does it react to morphing as
such) and on R2 vs R3 (are same-person morphs detected):

- **No identity reading:** AUC folded around 0.5 below 0.60, upper bound below 0.65.
- **Twin artefact, cell invalid:** AUC below 0.40 with upper bound below 0.5 (twins score higher than
  morphs; seen once already, SelfMAD 0.29 in A43).
- **Identity reading:** AUC ≥ 0.75, lower bound above 0.65.
- **Mixed:** anything else, reported with shares.
- Twins' rejection rate at the benchmark threshold is printed with an exact interval; no rule on it.

With about 100 persons an AUC interval is about ±0.08, so many FRLL cells will read "mixed"; the
FRGC and colorFERET pool is larger for that reason. Primary cells, corrected for multiplicity (Holm):
4 releases × 3 families, first tool, primary pool = 12. Everything else is descriptive. Cells whose
outcome is already known (StyleGAN3 sets; ViT-B/16 on MorDIFF) are labelled "post hoc".

Detectors: released SelfMAD, MADation ViT-B/16, MADation ViT-L/14, MixFaceNet-MAD (RGB path), scored
on their own crops; further releases if weights exist (`10_ASSET_INVENTORY.md`). Our retrains that
did not reproduce published numbers go in a separate block, labelled as such.

## (a) Diffusion morphs: beyond SelfMAD

MAD22 has no diffusion morphs. The diffusion cells are MorDIFF, DiM and Greedy-DiM, built on FRLL.

| ID | Experiment | Data | New compute | Closes |
|---|---|---|---|---|
| AD1 | Ladder on MorDIFF for all releases. First step is a re-read: A43 already holds scores of reconstructions, same-pair morphs and same-person mixes for ViT-B/16, ViT-L/14 and SelfMAD; add MixFaceNet. Then expression-matched twins (the R2x set planned in A43, never run) | `a43` set; 100 matched mixes | re-read: none; R2x: 2 GPU-h | A43 extended from one release to four |
| AD3 | History control on a second photo pool: FRGC and colorFERET photos, native vs existing E7 output | a pool no scored network was trained on: FFHQ pools with existing E7 outputs first; FRGC and colorFERET count only for the released detectors (our own networks trained on them) | scoring | "Everything rests on 204 FRLL photos" |
| AD4 | Morph-free network: the registered A47 I-3 data, unchanged; 5 seeds (401 to 405), last checkpoint; recipes M3 (ViT-B/16) and M3L (ViT-L/14). Chance reference per recipe: 5 label-permuted seeds plus one untrained network | `/mnt/t7/smad_heldout/a47/data47` | 15 H100-h | A47 I-3 with a working control |
| AD2 | Ladder on DiM and Greedy-DiM | needs DiM code on x86 | 10 GPU-h | A46's two open refuters. Cut if DiM code is not running by Thursday |
| AD5 | Retrains of SelfMAD with the authors' code (MADation already has 8 retrains from A44) | SMDD | 30 H100-h | First item to cut |

AD4 reading: a cell counts as "passable without morphs" only if the morph-free error is at least
10 points below the lowest of the five permuted-label networks and of the untrained network.
Falsifier of hypothesis A1: error above 15% in at least 3 of 5 seeds. This control replaces the idea
of a chance gate: A47 showed that a network trained on random labels need not sit at 0.5.

## (b) GAN morphs: causal tests

What the record says: SMDD's genuine class is itself GAN output, so SMDD labels cannot teach "GAN
output = attack". Yet SMDD-trained networks rank GAN renders above camera photos (AUC 0.95 for our
MADation-recipe networks; 0.92 for frozen CLIP). Pretraining or the attack-side processing supplies
it. SelfMAD is read on its own. Correction, 11 Nov 18:15: the earlier wording "SelfMAD is not SMDD-trained" was wrong. By its paper, both training classes are SMDD StyleGAN renders and self-blends of them; what the released weights were trained on is not stated (`docs/PLANNING_RECORD.md` sections 3 and 4).

| ID | Experiment | Data | New compute | Reading |
|---|---|---|---|---|
| AG1 | Ladder on the benchmark's generator. R2 = MIPGAN optimiser with A = B; R3 = MIPGAN on two photos of one person; R4 = our own MIPGAN morphs; bridge to the published MIPGAN morphs. Fixed iteration count; final loss and latent distance from the mean logged; R3 vs R4 also reported within matched bins of those | MIPGAN on x86 (`h4_mipgan1` re-implementation, StyleGAN v1) | 15 GPU-h | The main causal test |
| AG2 | Genuine side: replace camera photos by R2 images of the same photos; morphs unchanged. Two-sided reading registered: error may go to chance or reverse | from AG1 | none extra | If the cell collapses or reverses, it measured "generator output vs camera" |
| AG3 | Dose: two-person mixing 0.1 … 0.5 on a subset | from AG1 runs | 5 GPU-h | Ramp = identity; flat = pipeline |
| AG5 | Existing StyleGAN3 sets under these rules (post hoc) | on disk | minutes | Old result in the common table |
| AG4 | Morph-free network for the GAN cue: camera photo vs its reconstruction, trained on StyleGAN2, tested on MIPGAN-I (StyleGAN v1). Benchmark-level statement only | FFHQ + inversions | 12 H100-h | Second item to cut |

Benchmark side of AG1 on MAD22 needs the corrected-MAD22 scoring (queued by the other loop). Fallback:
the FRLL StyleGAN cell.

## (c) Regular (landmark) morphs

Open today: four CLIP-based rows keep their accuracy under E7 and beat the file-size floor on our
clean Poisson set.

| ID | Experiment | Data | Compute | Reading |
|---|---|---|---|---|
| AR1 | Ladder with self-morph twins on FRGC and colorFERET (primary) and FRLL (secondary). Tools: OpenCV and FaceMorpher run unchanged, plus the A27 warp path as a third | needs the author's ruling on which generation paths may run (open question 2) | CPU | The decisive test |
| AR2 | Dose: mixing 0.1 … 0.5 on the same pairs (Page trend test) | CPU | CPU | Step-by-step rise |
| AR3 | Baselines on benchmark and twin set. Non-content: file attributes, border mask only, background only. Content: 32-pixel thumbnail, face only | constant-colour blanking with existing aligner masks | minutes | Non-content baselines are cues; content baselines may legitimately carry "average face" signal |
| AR4 | Each detector with background blanked, and with face blanked | same | minutes | Works with the face blanked = reads the frame |
| AR5 | E7 with identical borders for both classes, if producible from existing approved outputs | existing | scoring | Closes the border gap |
| AR7 | Pairs binned by contributor similarity | from AR1 | CPU | Cut if short of time |

Wording aimed for: "no tested benchmark cue explains the result; an identity share of X survives".
It is **supported** when all hold:

1. "reads morphing" (main verdict above) on both pools with composition-matched images;
2. the detector beats the best non-content baseline, paired lower bound above 0;
3. monotone dose curve;
4. accuracy kept with the background blanked;
5. benchmark link: bridge AUC between published and our same-tool morphs within 0.40 to 0.60, and at
   the benchmark threshold our morphs are detected within 10 points of the benchmark rate;
6. R0 → R2 share ≤ 0.2 under the border-matched control.

It is **refuted** when "reads the benchmark" holds on both pools.
Otherwise "mixed", with the four shares. A universal "free of all cues" is not claimed; the cue
matrix (`08_CUE_MATRIX.md`) lists what was tested.

## Order and cuts

Start: AD1 re-read, untrained-network scores on all cells, AG5 (all need no new data). Then AR1 on
FRGC and colorFERET with controls P1 and P2 and the baselines. WCSS at the start signal: AD4, the
x86 container build, AG1 generation.

Cut order if time runs out: AD5, AG4, method extras (T5, T6, X3), the MADMamba arm, AD2, AR7, the
large generator training sets. Kept to the end: AR1 to AR5, AD1, AD3, AD4, AG1 to AG3, AG5.

## Author rulings of 11 Nov (afternoon)

1. A genuine image that was only processed (crop, alignment, compression and the like) and is called
   a morph is an error. Morphing two photos of one person is still morphing; it is studied as a side
   problem.
2. Agents may run the approved warp script, the unchanged OpenCV and FaceMorpher morphers and
   constant-colour blanking. If other warp paths are needed, they are verified too.
3. All datasets may be processed on rented machines; they are published research data.
4. A freshly trained MADMamba arm may be scored; it is a side quest. MambaVision is the expected
   stronger state-space backbone and is added as an arm.
5. Registration: brevity. One page per experiment in this repository (`experiments/<ID>/`), plain
   conclusions in `NOTEBOOK.md` and `CONCLUSIONS.md`, everything in git. No full ledger folders.
6. The old generated-morph training arms (CG, CD, CGD) are retired.
