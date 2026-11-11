# Research plan, 11–15 Nov 2026

Status: proposal. Nothing has been launched. Compute hours below are estimates, not measurements.

## The idea in three sentences

Every benchmark so far compares morphs from one pipeline with photos from another, so a detector can
score well by recognising the pipeline. We build training and test data in which both classes come
from the same pipeline with the same post-processing, and the only difference is whether one or two
people went in. On that data we measure what released detectors do, and train the first detector that
is checked against it.

Working name: **TwinMAD** (twin-controlled morphing attack detection). The paper has two halves that
share one dataset: the audit (existing numbers follow construction) and the method (what remains
detectable once construction is matched).

## What the paper says under each outcome

| Outcome on held-out twins | Paper |
|---|---|
| Landmark and generator morphs both detected | First S-MAD detector shown to respond to identity blending, with dose-response curves. Strongest paper. |
| Landmark detected, generator morphs not (most likely) | Benchmark + audit + method for landmark morphs + a measured limit: well-rendered latent morphs leave only a typicality signal with a stated ceiling. |
| Nothing detected | Audit and benchmark paper: current S-MAD numbers measure construction; single-image detection of identity blending is unsupported. Weakest of the three for a main-track paper. |

Honest assessment: the second outcome is a credible CVPR submission. The third is a strong workshop
or benchmark-track paper and a risky main-track one. Four days is enough to learn which one we have.

## Base model

Frozen CLIP ViT-L/14 with a small head first, LoRA second. Reasons: the released MADation ViT-L/14 is
the only row that does not move under E7 on Greedy-DiM (Δ 0.00); head-only DINOv3 beat adapted DINOv3
in A49; frozen features make each experiment minutes, not hours. DINOv3 ViT-L is the second backbone.
MADMamba joins only as one arm of T4 with the identical data; it stays in the paper only if it wins there.

## The dataset: TwinSet

| Family | Morph (attack) | Twin (not an attack) | Tools | Sources |
|---|---|---|---|---|
| Landmark | morph(A, B), mixing 0.5 | morph(A, A′), same tool and mask | OpenCV, FaceMorpher; hold out one | FRGC, colorFERET, Multi-PIE, FRLL (two photos per person) |
| GAN | decode(mix(wA, wB)) | decode(mix(wA, wA′)) | StyleGAN2 train, StyleGAN3 held out | same |
| Diffusion | DiffAE mix of A, B | DiffAE mix of A, A′ | DiffAE at 20 and 100 steps | same |
| Graded | mixing 0, 0.1 … 0.5 for a subset | — | all | same |

Rules: one sampled post-processing chain per pair, applied to both members; pairs matched on head
pose; identity-disjoint train/validation/test; every person under both labels. Target size: 20,000
pairs per family for training, 2,000 per family for test. Existing material that is reused, not
regenerated: `h3_sg3` (2,909 StyleGAN3 morphs), `a37_sg3ctl` (19,570 renders), `a41_diffae`, `a43`
(same-pair 20-step morphs), `diffae-expanded123`, the GAN32 inversions.

No new blur, resampling or JPEG code is written. The shared chain uses the existing, approved
`a37_restore` path only; if that is not enough, the pairs stay as lossless PNG at generator resolution
(decision 3 in `07_DECISIONS_NEEDED.md`).

## Workstreams (run in parallel)

| ID | Work | Depends on | Where | Estimate |
|---|---|---|---|---|
| D1 | Pair lists: same-person and two-person pairs, pose-matched, identity splits | decision 1 | DGX CPU | 3 h |
| D2 | Landmark morphs and self-morphs, 2 tools | D1 | WCSS CPU array or DGX CPU | 4 h wall |
| D3 | GAN inversions and latent mixes | D1 | Vast, 4–8 GPUs | 80 GPU-h |
| D4 | DiffAE mixes at 20 and 100 steps | D1 | Vast (x86; the DGX build is not ready) | 120 GPU-h |
| F1 | Feature cache: CLIP-L, DINOv3-L, ArcFace, AdaFace, each released detector's penultimate layer | D2–D4, rolling | DGX | 6 GPU-h |
| T1 | Audit: released detectors on twins, zero-shot (A2) | F1 | DGX | minutes |
| T2 | Audit: last-layer refit of released detectors (A3) | F1 | DGX CPU | minutes |
| T3 | Typicality detector and dose curves (M3) | F1 | DGX CPU | 1 h |
| T4 | Twin-contrast head, then LoRA; CLIP-L, DINOv3-L, MADMamba; 5 seeds (M1, M2, M5) | F1 | DGX for heads, WCSS/Vast for LoRA | 60 GPU-h |
| T5 | Two-identity embedding head with retrieval test (M4) | F1 | DGX | 10 GPU-h |
| T6 | Mixing-fraction regression (M6) | graded subset | DGX | 6 GPU-h |
| A1r | Morph-free network repeat with fixed checkpoint and chance control (A1) | none | WCSS, 3 jobs | 12 GPU-h |
| G | Guards G1–G4 on every trained model | T4–T6 | DGX CPU | 1 h |
| B | Benchmark numbers: MAD22, FRLL, with and without E7 | T4 | WCSS (existing scorer) | 8 GPU-h |
| W | Paper text and figures | rolling | — | — |

A1r, D1 and F1-on-existing-sets need no new data and can start the moment this plan is approved.

## Day by day

**Wed 11 Nov (evening).** Decisions 1–5. D1. Rent Vast machines and start D3/D4. Submit A1r.
First signal the same night: F1 + T1 + T2 + T3 + a frozen-feature T4 head on the *existing* sets
(StyleGAN3 morphs vs spread-matched renders; DiffAE same-pair sets). This is a 2-hour experiment on
the DGX and tells us early whether M2 has any chance.

**Thu 12 Nov.** D2 complete by noon; D3/D4 half done. Landmark T1–T4 (the family most likely to
work). Gate 1 at 18:00.

**Fri 13 Nov.** D3/D4 complete. Full T4 with LoRA, 5 seeds, three backbones. T5, T6. Gate 2 at 20:00.

**Sat 14 Nov.** Held-out pipelines, guards, benchmark numbers (B), dose and similarity curves.
Results reviewer on every finished study. Figures.

**Sun 15 Nov.** Buffer for one rerun. Tables frozen at 14:00. Text.

**Mon 16 Nov.** Submission.

## Gates

- **Gate 0 (tonight, existing sets).** If a twin-trained head on frozen CLIP-L reaches held-out AUC ≥ 0.60
  on StyleGAN3 or DiffAE twins: scale generator data as planned. If not: halve D3/D4, put the saved
  budget into landmark tools and graded-mixing data.
- **Gate 1 (Thu 18:00).** Landmark twin AUC ≥ 0.60 on the held-out tool and thumbnail guard passed:
  the method half of the paper exists. Otherwise the paper is audit + benchmark, and T5/T6 are dropped
  for more audit coverage (more released detectors, second genuine-photo pool).
- **Gate 2 (Fri 20:00).** Choose the single reported network: fixed recipe, last checkpoint, seed mean
  with interval. No selection on test twins.

## Evidence still to add for the audit half

1. A47 I-3 into `PROTOCOL.md`, and its repeat A1r.
2. Landmark twins: the first test of whether the CLIP rows that hold under E7 detect blending or pipeline.
3. A second genuine-photo pool (FRGC, colorFERET) for the E7-style control, so the result no longer
   rests on 204 FRLL photos.
4. More than one network per release where weights exist.
5. Drop Inception-MAD, MorphHRNet and MixFaceNet-MAD from causal claims unless their published numbers
   reproduce; keep them in the twin test "as released" if weights exist.

## Working rules for this sprint

- One page per experiment in `prereg/`: hypothesis, data, metric, falsifier, stop rule. One pre-run
  review, one results review. No other gates.
- Standing author rules stay: single network, no ensembles or seed picking; sealed files closed;
  `prep_eval.py` and `prep_gtest.py` untouched; WCSS job rules (`--extra=FORCE_RM_TMPDIR`, `$TMPDIR`
  packs, one SSH connection, excluded nodes).
- Seeds 301–305, so nothing collides with the other loop's 201–205.
- Outputs under `/mnt/t7/smad_next/`; nothing written into the other loop's folders.
- Every command is tested with its real command line on 8 images before a paid GPU starts.
