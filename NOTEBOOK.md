# Notebook

One line per idea. Newest state only; history is in git. Updated by the lead after every result.

Status: `planned` → `ready` (pre-registered, command tested) → `running` → `done` → `reviewed`.
Verdict: `yes`, `no`, `mixed`, or blank.

Last update: 11 Nov 2026, 14:25 CET. Started. WCSS: 48 one-GPU slots queued (jobs 6301498, 6301499).

## Where we stand, in five lines

- Shown: benchmark files differ by class; SelfMAD's diffusion results follow photo history.
- Partly shown: MADation ViT-B/16 on MorDIFF follows decoding step count.
- Not shown: any cue use on GAN or landmark morphs; any detector reading two identities.
- No training change has removed a shortcut so far.
- Next: one test design (morph vs camera, twin vs camera, morph vs twin) applied to every family and
  every released detector, then a detector trained on twins.

## Audit: do existing detectors read the morph or the benchmark

| ID | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| AR1 | Landmark: do detectors flag a one-person "self-morph" like a real morph? | planned | | | build pairs (FRLL, FRGC, colorFERET) |
| AR2 | Landmark: does the score rise with the mixing fraction? | planned | | | after AR1 |
| AR3 | Which single cues separate the classes on their own (file, thumbnail, border, background)? | planned | | | |
| AR4 | Do detectors still work with the face blanked, or the background blanked? | planned | | | |
| AR5 | Photo-history control with identical borders | planned | | | |
| AR7 | Landmark: does the signal weaken for look-alike pairs? | planned | | | after AR1 |
| AD1 | MorDIFF: three-number test for all four released detectors | planned | | | data mostly on disk (A43) |
| AD2 | DiM and Greedy-DiM: same | planned | | | needs twin generation |
| AD3 | Photo-history control on a second photo pool (not FRLL) | planned | | | scoring only |
| AD4 | Can a network that never saw a morph pass the benchmarks? 4 recipes × 5 seeds, fixed checkpoint | planned | A47: yes for one recipe, once | | WCSS, submit first |
| AD5 | Do retrains of SelfMAD and MADation behave like the released checkpoints? | planned | | | WCSS |
| AG1 | MIPGAN: are one-person MIPGAN outputs flagged like morphs? | planned | | | needs x86 GPU |
| AG2 | MIPGAN: does accuracy vanish when genuine photos are GAN reconstructions? | planned | | | needs x86 GPU |
| AG3 | GAN: score against two-person mixing fraction | planned | | | with AG1 |
| AG4 | Can a network that never saw a morph pass the GAN cells? | planned | A47: no, for the photo-history cue | | WCSS |
| AG5 | Existing StyleGAN3 sets under the common verdict rules | planned | old result: no detector above 0.59 | | minutes |

## Method: can a detector read identity blending

| ID | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| T0 | First signal: twin-trained head on frozen features, existing StyleGAN3 and DiffAE sets | partly done by Codex, 11 Nov | no transfer between generators (0.26 to 0.52); held-out sets 0.46 to 0.63; only 16 to 90 training pairs | no (underpowered) | rerun at 2,000 pairs |
| T2 | Do released detectors' features hold the signal if only the last layer is refit on twins? | planned | | | after features |
| T3 | Is a morph a more "average" face in face-recognition space? | planned | | | after features |
| T4 | Twin-trained detector, 3 backbones × 5 seeds, held-out tool and generator | planned | | | after TwinSet |
| T5 | Can a head recover both contributors' identities from one image? | planned | | | after T4 gate |
| T6 | Mixing fraction regression: ramp or step? | planned | | | after T4 gate |

## Data extension: does more or different training data remove cue use

| ID | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| X0 | Register the numbers derived from the 60 existing fits: adding photos cuts the diffusion history effect by 13 to 29 points in all four architectures; adding classical morphs gives 9 to 22 back | planned | post hoc, exploratory | | write up, 0 GPU |
| X1 | Re-score the 60 existing fits and the older checkpoints on the unseen-source landmark set (H1) and on twin sets | planned | on benchmarks: no effect of added data | | about 0.5 H100-h |
| X2 | Same backbone and same image count, matched (twins) vs unmatched added data | planned | | | frozen heads, about 1 H100-h |
| X4 | Photo-history control on a photo pool no network was trained on (FFHQ) | planned | | | about 0.3 H100-h |
| X5 | Landmark twins from an unseen source (CASIA), built with the unchanged approved script | planned | | | CPU |
| X3 | Does the number of different pipelines per class matter once twins are present? | planned | | | cut first |
| — | Generated-morph training arms (CG, CD, CGD) of the old plan | retired (author, 11 Nov) | | | |

## Zero-compute cue checks (from the cue table)

| ID | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| C1 | Are expressions balanced between classes in each benchmark cell? | planned | | | file lists |
| C2 | Do any persons appear in both training sets and test benchmarks? | planned | | | manifests |
| C3 | Do colour statistics alone separate the classes? | planned | | | |
| C4 | Does chroma subsampling alone separate the classes? | planned | only on MAD22 Webmorph so far | | |

## Data builds

| ID | What | Status | Size | Where |
|---|---|---|---|---|
| D1 | Pair lists: same-person and two-person, matched, identity-disjoint splits | planned | | |
| D2 | Landmark morphs, self-morphs, pipeline-only, graded mixing | planned | | DGX CPU |
| D3 | MIPGAN and StyleGAN twins | planned | | WCSS, Vast as fallback |
| D4 | DiffAE and DiM twins | planned | | WCSS, Vast as fallback |
| F1 | Feature cache for all detectors and backbones | planned | | DGX |

## Facts to work from (see `10_ASSET_INVENTORY.md`)

- Corrected MAD22, raw: `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/` (204 genuine; 1,000 / 984 / 500 / 1,000 / 999 morphs). Aligned: `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/`. Never `Datasety/downloads/MAD22` or `eval.csv` (old subset).
- Nothing has been scored on the corrected MAD22 yet. Old scores cannot be merged in.
- Released weights on this machine: MADation (all variants), MixFaceNet-MAD. SelfMAD is on WCSS only. SPL-MAD is public, not downloaded. No public weights: PW-MAD, Inception-MAD, MorphHRNet, MorDeephy, FD-MAD, SRL-MAD, R-FLoRA.
- Twin material that exists: 5,000 landmark self-morphs (OpenCV, FaceMorpher; training persons), StyleGAN3 and DiffAE self-morphs (FERET, FRGC), FRLL self-morphs from A41 and A43.
- Copied out of volatile storage on 11 Nov: `/mnt/t7/smad_next/volatile_backup_20261111/` (landmark self-morphs, corrected-MAD22 manifest).

## Open decisions and blockers

- Codex loop is paused; its DGX controllers still run (20 CLIP fits, up to 66 h). See `12_STATE_AT_HANDOVER.md`.
- No x86 build of MIPGAN yet (GAN causal test depends on it).
- For our own networks, FERET and FRGC have no unsealed held-out persons; unseen-source tests use CASIA or Multi-PIE.

## Log

- 11 Nov: plan, evidence dossier, cue matrix, audit plan and workflow written. Repository created.
- 11 Nov: author rulings recorded. Main contrast is now processed genuine image against morph; same-person morphs are a side study.
- 11 Nov 14:22: transcript read; start. 48 WCSS slots submitted. Owners assigned to first-round experiments.
