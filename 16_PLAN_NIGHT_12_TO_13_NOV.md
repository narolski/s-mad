# Plan for the night of 12 to 13 November 2026 and for 13 November

Written by the lead on 12 Nov, about 23:20 CET, on the author's instruction: define the evening's work, report meaningful progress by 09:00 on 13 Nov, and aim for decisive conclusions by 18:00 on 13 Nov. Ultimate goal: a single-image morphing attack detector that does not rely on benchmark shortcuts, compared with the state of the art on MAD22 and FRLL-Morphs.

Binding rules stay as in OWNER_BRIEF.md and NOTEBOOK.md (12 Nov entries): no benchmark set in development; every experiment registered before it runs and reviewed before and after; no placeholder cluster jobs; nothing released while it holds the only copy.

## The route to a method

1. **Is the candidate recipe real?** Protocol negatives plus face-spliced positives, tested on five fresh seeds against the plain recipe and the protocol alone (fresh seeds, FS1), on development data only.
2. **Does it need its matched negatives?** Ablation arm Sp.
3. **Can the threshold transfer?** Multi-source training (MS1) and the unseen genuine sources (TT1).
4. **What do the baselines do under the same controls?** Retrains of the released recipes (AD5) and the morph-free networks (AD4), which are audits and may use benchmarks.
5. **Freeze the method, then read the benchmarks once.** A written freeze rule and a sealed final protocol for MAD22 and FRLL-Morphs, prepared tonight, executed only after the author's go.

## Goals for 09:00 on 13 November, per experiment

| Experiment | Owner | Goal by 09:00 | Where |
|---|---|---|---|
| Fresh seeds of the protocol network (FS1) | PN1 owner | all 16 fits back (expected about 08:30), read once as registered, sent to independent review | rented A100, running |
| Ablation arm (Sp) | PN1 owner | running behind FS1; first fit under way | same machine |
| Sealed final benchmark protocol (FINAL) | PN1 owner | draft registration: freeze rule, benchmark sets, metrics, history-matched controls, comparison set, one read; pre-run review requested | paper work, no compute |
| Multi-source training set (MS1) | MS1 owner | FFHQ source built and verified; training comparison registered and pre-run reviewed; ten fits (current recipe and three-source recipe, five seeds each) submitted on WCSS and, if the build allows, finished | DGX CPU, then WCSS |
| Unseen genuine sources (TT1) | TT1 owner | scoring plan pre-run reviewed; the 12 existing networks scored on the eight unseen sources with the border-matched reference; registered reading | WCSS or DGX |
| Diffusion: what the released recipe reads (A16) and whether a second-identity signal is learnable (A18) | SM1 owner | A16 scored and read; A18 linear probe read and the three fits finished and read; both sent to review | WCSS |
| Morph-free networks (AD4) | AD4 owner | three ViT-L/14 fits and the deciding ViT-B/16 rerun finished on WCSS; readings updated | WCSS |
| Retrains of released recipes (AD5) | AD5 owner | MADation ViT-B/16 (five seeds) finished and read; MixFaceNet running; ViT-L/14 submitted | WCSS |
| New genuine sources | lead | CelebA-HQ downloaded and inventoried; MUCT inventoried; each judged against the MS1 requirements for a fourth source | DGX |

## Report at 09:00

One page, `17_MORNING_REPORT_20261113.md`: what finished, the numbers (reviewed and unreviewed kept apart), what each result means for the method, what failed, spend, and the decisions needed from the author (first of all: the freeze rule and the go for the sealed benchmark read).

## Goals for 18:00 on 13 November

1. Fresh seeds and ablation read and reviewed: a yes or no on "protocol plus spliced positives" as the method, on development data.
2. Multi-source and unseen-source results read and reviewed: a yes or no on threshold transfer.
3. Method frozen by a written rule (about 14:00), or a written statement that no method can be frozen and why.
4. If frozen and the author agrees: the sealed read on MAD22 and FRLL-Morphs executed once, with history-matched controls, beside the released detectors and their retrains; independently reviewed.
5. A conclusions page in plain English for the authors.

What cannot be promised: that the results will favour the method. What is promised: each question above gets a registered, reviewed answer.

## Risks watched tonight

- WCSS access or queue: every job carries its workload; the lead lists both queues at each 30-minute check.
- The fresh-seed machine: release is held until both queues are fetched and verified; cap 15.5 USD, deadline 15:52 on 13 Nov.
- Disk: 410 GB free.
- Budget: 50 USD for today from 22:54 on 12 Nov; credit then 59.37 USD.
