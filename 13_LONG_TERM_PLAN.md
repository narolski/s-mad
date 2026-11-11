# Long-term plan

The sprint to 16 Nov (`05_RESEARCH_PLAN.md`) is the first of three stages. Estimates only.

## Why queue on WCSS now

Measured on 11 Nov: priority there is mostly waiting time (about 60 points per hour; fair share adds
a fixed 507). `lem-gpu-short` had 11 jobs running and 233 pending; our own jobs waited 20 minutes to
9 hours this morning and the latest is forecast 14 hours. `lem-gpu-normal` is at about 2 days. Our
limits are 250 running and 500 submitted jobs. So a job submitted now is ahead of one submitted
tomorrow by a day of priority, whatever it will run.

We therefore queue generic one-GPU "slots" now and decide what each runs when it starts
(`OWNER_BRIEF.md`, section "The WCSS slot queue"). A slot that finds no task waits 30 minutes and
exits, which costs at most half a GPU-hour.

| Wave | Submitted | Slots | For |
|---|---|---|---|
| 1 | 11 Nov 14:22 | 40 × 6 h, 8 × 14 h (jobs 6301498, 6301499) | morph-free networks (AD4), GAN twin generation (AG1), first twin-trained runs |
| 2 | 12 Nov morning | sized from wave 1's measured wait and task times | five-seed matrix of the method (T4), retrains (AD5), re-scoring (X1) |
| 3 | 13 Nov | same | held-out tests, ablations, benchmark scoring, one rerun reserve |
| 4 | 15 Nov | 20 × 6 h | rebuttal and camera-ready reserve; cancelled if unused |

## Stage 1: to 16 Nov, the submission

Audit table (detector × morph family, five rungs), cue matrix, TwinMAD on landmark morphs with
generator morphs as far as the data allow. Cut order is fixed in `11_AUDIT_PLAN.md`.

## Stage 2: 17 Nov to the rebuttal (about late January)

Work that reviewers will ask for and that takes longer than the sprint. All of it is WCSS work and
can sit in the queue from the day its inputs exist.

| Item | Why | Estimate |
|---|---|---|
| TwinSet at full size: 10,000 pairs per family, three landmark tools, StyleGAN2/3, MIPGAN-I/II, DiffAE, one further diffusion morpher | the benchmark contribution; removes "small panel" objections | 400 GPU-h generation |
| Unseen-source and unseen-person tests on a pool never used anywhere (Multi-PIE or CASIA) | generalisation claim | 20 H100-h |
| Full method matrix: 4 backbones × 4 training sets × 5 seeds, plus ablations (loss terms, twin ratio, head-only vs LoRA) | methodological completeness | 300 H100-h |
| Every released detector and every retrain on every rung, corrected MAD22 included | the audit table without gaps | 30 H100-h |
| Retrains of released methods with the authors' code, five seeds each | "one checkpoint is not the method" | 150 H100-h |
| Print-and-scan and re-compression of TwinSet (needs approved processing paths) | the realistic passport channel | to be sized |
| Morph-free networks for every family and recipe | benchmark-level claim per cell | 60 H100-h |

## Stage 3: 2027

- **Public benchmark.** Release pair lists, code and scoring server for the five-rung ladder; images
  only where licences allow.
- **Larger models and pretraining.** Twin-contrast pretraining of a face foundation encoder on
  generated twins at scale; this is what the EuroHPC request (JUPITER, 40,000 node-hours, draft
  27275) would pay for.
- **Differential detection.** The same ladder with a trusted live capture; our pre-registered D-MAD
  programme resumes there.
- **External tests.** Submission to NIST FATE MORPH; a second lab's data.
- **Journal version.** Audit, benchmark and method in one long paper.

## Standing queue policy

- Long or five-seed work goes to WCSS the day it is specified, as tasks for slots.
- Discovery work runs on the DGX without a queue.
- Rented GPUs only for data that blocks several experiments and only when WCSS would be slower.
- Every evening: count ready tasks against queued slots, and submit the next wave.
