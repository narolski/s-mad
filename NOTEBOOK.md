# Notebook

One line per idea. Newest state only; history is in git. Updated by the lead after every result.

Status: `planned` → `ready` (pre-registered, command tested) → `running` → `done` → `reviewed`.
Verdict: `yes`, `no`, `mixed`, or blank.

Last update: 11 Nov 2026, 14:30 CET. Nothing has been launched yet.

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
| T0 | First signal: twin-trained head on frozen CLIP, existing StyleGAN3 and DiffAE sets | planned | | | 2 h on the DGX |
| T2 | Do released detectors' features hold the signal if only the last layer is refit on twins? | planned | | | after features |
| T3 | Is a morph a more "average" face in face-recognition space? | planned | | | after features |
| T4 | Twin-trained detector, 3 backbones × 5 seeds, held-out tool and generator | planned | | | after TwinSet |
| T5 | Can a head recover both contributors' identities from one image? | planned | | | after T4 gate |
| T6 | Mixing fraction regression: ramp or step? | planned | | | after T4 gate |

## Data extension: does more or different training data remove cue use

| ID | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| X1 | Re-score the 60 existing fits (SMDD / + photos / + classical morphs) on twin tests | planned | old result on benchmarks: no effect | | scoring only |
| X2 | Same backbone, four training sets: SMDD; + unmatched data; + twins; twins only | planned | | | part of T4 |
| X3 | Does the number of different pipelines per class matter once twins are present? | planned | | | after X2 |

## Data builds

| ID | What | Status | Size | Where |
|---|---|---|---|---|
| D1 | Pair lists: same-person and two-person, matched, identity-disjoint splits | planned | | |
| D2 | Landmark morphs, self-morphs, pipeline-only, graded mixing | planned | | DGX CPU |
| D3 | MIPGAN and StyleGAN twins | planned | | WCSS, Vast as fallback |
| D4 | DiffAE and DiM twins | planned | | WCSS, Vast as fallback |
| F1 | Feature cache for all detectors and backbones | planned | | DGX |

## Open decisions and blockers

- Start signal from the author (plan is under review).
- Hand-over of the DGX and WCSS slots from the other loop.

## Log

- 11 Nov: plan, evidence dossier, cue matrix, audit plan and workflow written. Repository created.
