# Morning report, 13 November 2026 (09:00)

Written by the lead at 08:45 CET, following `16_PLAN_NIGHT_12_TO_13_NOV.md`. Numbers are split into **reviewed** (an independent reviewer checked them against the files) and **unreviewed** (the owner's reading only). Experiments are named by what they do, with the ID in brackets.

## Where we stand in one paragraph

We do not have a shortcut-free method yet. The candidate training protocol (protocol negatives plus face-spliced morphs) removes the storage-history shortcut on five fresh seeds, and the protocol keeps false alarms low on unseen camera sources on two seeds. It still flags 31–41% of same-person face splices (it partly reads the blending seam), misses 26–47% of landmark morphs at its own rule, and is no better than the best single hand-made statistic. Under the rule registered before the read, the fresh-seed result froze no method, because one of its two tests was uninformative. The author approved a replacement test; it is read today. The author then asked to attack the seam shortcut, build one audit table of all shortcuts, and run the second backbone, so the freeze moves from midday to this evening.

## What finished overnight, per experiment

### Fresh seeds of the protocol network (FS1) — reviewed

16 fits (plain A, protocol B, protocol plus spliced morphs Sb; seeds 403–407; one repeat) on a rented A100, development data only. Read once by the lead, since the owner had been stopped. Review: `experiments/reviews/REVIEW_PN1_FS1_20261113.md`.

| Read | A (plain) | B (protocol) | Sb (protocol + splices) |
|---|---|---|---|
| Landmark morphs against genuine, AUC (mean ± SD, 5 seeds) | 0.736 ± 0.031 | 0.674 ± 0.028 | 0.860 ± 0.030 |
| Rise in flagged genuine photos after shrink-and-store (points) | +14.7 to +21.8 | +2.5 to +5.5 | +0.5 to +2.7 |
| Same-person face splices flagged | – | – | 31–41% |
| Landmark morphs missed at the own rule | – | – | 26–47% |

- Contrast 1 (Sb above B on landmark morphs) replicated on 5 of 5 seeds.
- Sb is not above the best single hand-made statistic (0.886) and is level with the 27-statistic baseline (0.814).
- Contrast 2 (storage) was "uninformative": the control arm did not reach its registered bar (0.53–0.63 against 0.65). The storage numbers in the table are post hoc.
- Registered outcome: **no method frozen**.
- New finding for the final protocol (F10): the fixed development threshold taken from training-source photos flags 96–98% of unseen genuine photos, so it cannot be the deciding operating point.

Meaning: the spliced positives help detection, the protocol negatives remove the storage shortcut, the seam shortcut is open, and detection strength is weak.

### Replacement storage test (contrast 2′, C2P) — registered, not yet read

Drafted after the review, pre-run check GO WITH FIXES, approved by the author ("Yes"), registered at 2715e48. The freeze rule in the final protocol was amended (6691adc). The 15 fresh-seed networks are uploaded and verified on a rented L40S; scoring starts when the multi-source fits finish there (about 09:50), one read after about 10:30.

### Unseen genuine sources (TT1) — reviewed

11 networks from seeds 401 and 402 on eight unseen low-resolution genuine sources. Review: `REVIEW_TT1_20261113.md`.

- Protocol arm B: at most 4.9% of unseen genuine photos flagged at the own rule. Plain arm: up to 23.5%.
- The plain arm flags 46–57% of its own training-source photos after the 112-pixel path.
- Sb flags more than B; its "supported" verdict clears the 5% bar by 0.1–0.3 points.
- Limits: false alarms only, two seeds, each seed on its own machine; the fixed camera threshold is unusable.
- Three platform gates failed before a valid one (DGX stack, batch composition, one network): scores depend on GPU model and software build. The DGX is excluded as a scoring platform; the pin list for the final read is in `experiments/TT1_threshold-transfer-unseen-genuine/PLATFORM_PINS_FOR_FINAL_READ.md`.

The fresh-seed block (15 networks) is registered (a2fef5c, ab81b35) and queued on the rented A100 behind the ablation fits; scoring about 12:45.

### Multi-source training set (MS1) — running

FFHQ source built and verified; comparison registered and pre-run reviewed; 15 fits on three rented L40S (WCSS refused submissions last night). One machine finished and was released after its outputs were verified; the other two have 5 of 6 and 4 of 6 fits verified and end about 09:50 and 11:00. Nothing read yet.

### Ablation arm without matched negatives (Sp) — running

Three fits on the rented A100: 1 of 3 verified. The reading needs an owner or the lead (the reader is committed).

### Diffusion: what the released recipe reads (SM1) — reviewed, four rounds

Reviews: `REVIEW_SM1_A16_A18_20261113.md`, `REVIEW_SM1_A19_20261113.md`, `REVIEW_SM1_A21_20261113.md`, `REVIEW_SM1_A22_20261113.md`. Development data, one DiffAE generator.

- The earlier sentence "the network learns a second-identity signal" is **withdrawn**.
- The detector's two-person signal does not exceed the similarity of the source pair: noise-only mixes 0.92 (pair similarity alone 0.99); semantic-only mixes 0.72 (semantic-code dissimilarity alone 0.87, post hoc).
- No evidence of identity reading: +0.02 [−0.19, +0.27], low power.
- Same-person diffusion edits are also scored morph-like (0.93 / 0.82): part of the response is to the re-rendering itself. Sharpness, file size and high-frequency energy do not explain it for one arm; file size is a partial, unsettled explanation for the other.
- A proposed training arm with render-matched diffusion controls (A20) is a draft. The reviewer: not before the freeze; afterwards only as a labelled ablation, and it would make MorDIFF a seen family.
- Three ViT-L/14 tasks are running on Athena (first ends 10:50–12:10).

Meaning: a reviewed sentence for the paper's diffusion section; no change to the method.

### Competitor baselines on corrected MAD22 and FRLL-Morphs (CB1) — reviewed (review launched by the owner)

- Released weights with our scoring exist for MADation (ViT-B/16, ViT-L/14), MixFaceNet-MAD and SelfMAD. With plain genuine photos we reproduce the published MADation ViT-B/16 and MixFaceNet-MAD numbers on landmark families; with history-matched genuine photos their error rises sharply (for example MADation ViT-B/16, FRLL AMSL 3.9 → 24.4; MAD22 FaceMorpher 0.0 → 13.7), while MADation ViT-L/14 barely moves. Table: `experiments/CB1_competitor-baselines-corrected-mad22/cb1_released_rs1_bpcer.csv`.
- PW-MAD, Inception-MAD, OrthoMAD, MorphHRNet, FD-MAD: "as reported, not verified"; our re-implementations were re-scored on the corrected MAD22 (`tables_all.md`).
- The manuscript's OrthoMAD FRLL row has a transcription error (AMSL 14.80, not 9.50).
- IDistill: retraining on the DGX, one seed, ends 14 Nov 04:00–08:30. A WCSS version with three seeds is ready and waits for the Slurm controller.

### Morph-free networks (AD4) — fits finished, reading in progress

Ten ViT-B/16 fits completed on WCSS between 03:12 and 06:46. The owner is fetching and reading them. No numbers yet.

### Retrains of released methods (AD5) — mostly not started

- Athena: MixFaceNet-MAD seed 401 running (ends about 14:40). All five SelfMAD tasks failed at start (our job script did not create the output folder; fixed, test job queued). MADation arrays waiting.
- WCSS: both smoke tests failed after 29 seconds (missing Python package; fixed); the arrays chained behind them can never start and are to be cancelled and resubmitted.
- Author's ruling (08:25): retrains stay on the clusters and arrive when they arrive; they no longer gate the sealed read.

### Second backbone (BB2) — ready, not running

Registered (4393990). WCSS smoke clean (features equal to the reference within 6.8e-7). Nine fits wait in the dispatcher's queue; two more seeds approved as an amendment (five seeds per arm).

### New genuine sources (lead)

CelebA-HQ (Hugging Face mirror, 33.9 GB, checksum recorded) and MUCT downloaded; Chicago Face Database and KDEF copied by the author. Chicago is a co-primary read of the multi-source experiment. Reminder for the author: check the CelebA-HQ mirror's provenance.

## What failed, and what I got wrong

1. **WCSS overnight.** I relied on Slurm's forecast (15 Nov). The jobs started at 03:00. Four failed at start and sat unseen until 08:40, because the controller did not answer the morning checks. Fix: a persistent dispatcher agent (Opus, on the author's instruction, with his full approval to submit, cancel and change jobs) checks both clusters every 10 minutes and submits from a queue the moment the controller answers (`src/dispatch/DISPATCHER_BRIEF.md`).
2. **WCSS controller.** It has refused most queries since 07:09. Nothing of ours runs there now. The author's order: if not WCSS, then Athena; the dispatcher is preparing Athena versions of the queued work.
3. **Platform sensitivity** cost the unseen-sources experiment three failed gates.
4. **The first storage test** was badly calibrated (the control could not reach its bar). Replaced by contrast 2′.
5. **Night goals missed:** multi-source fits not finished; retrains of released recipes not finished; A16 read "undecided".

## Spend

Credit 59.37 USD at the approval (12 Nov 22:54), 28.02 USD now: 31.35 USD used of the 50 USD approved. Three machines are running (caps 15.5, 12 and 10 USD; estimated at 11.1, 7.0 and 7.1). Expected total by the time they are released: about 38–40 USD.

## Cluster queues at 08:40

- **WCSS:** controller not answering; state unknown. Last seen: no job of ours running, three retrain arrays that cannot start, about 20 idle GPU nodes. Waiting in the dispatcher's queue: nine second-backbone fits, the IDistill smoke.
- **Athena:** running: three diffusion ViT-L/14 tasks, MixFaceNet-MAD seed 401. Waiting for nodes: MADation ViT-B/16 and ViT-L/14 arrays, MixFaceNet-MAD seeds 402–405, the SelfMAD test job. The partition has 23 failed and 12 reserved nodes. The grant has 30,000 A100-hours, 692 used.
- **DGX GPU:** IDistill.

## Plan for today

| When | What |
|---|---|
| about 10:30 | read of the replacement storage test (C2P), then review |
| about 11:00 | read of the multi-source experiment (MS1), then review; first version of the shortcut audit table (SA1) |
| about 11:00 | registration and pre-run check of the seam-shortcut arm (SE1); fits by about 12:00 |
| about 12:45–13:30 | ablation arm (Sp) read; unseen-sources fresh-seed block (TT1) scored and read |
| afternoon | second backbone fits and readings; hypothesis strategist's ranked experiments registered and submitted |
| about 18:00 | seam arm read and reviewed |
| evening | freeze by the registered rule, or a written statement that no method can be frozen and why |

These are plans, not results.

## Decisions needed from the author

1. **Freeze rule.** Already approved in its amended form (contrast 2′). New: the freeze moves to this evening so that the seam-shortcut arm can enter the method. Confirm, or freeze at midday and report the seam shortcut as a limitation.
2. **Go for the sealed benchmark read.** One read of MAD22 and FRLL-Morphs right after the freeze, on a pinned platform, run by the lead, with history-matched genuine photos, beside the released detectors. It needs your explicit go when the freeze is written.
3. **Operating point of the final protocol (F10).** Proposal: the deciding measure is ranking quality within each history-matched cell (AUC and EER); the networks' own rule and a second development threshold are printed beside it. Approve, or name another deciding measure.
4. **Which closed sets are the confirmatory test** (FEI, the sealed sets), and whether the Chicago Face Database stays a test set or becomes a training source.
5. **Render-matched diffusion controls (A20).** Recommendation: skip unless Athena is idle after the freeze; it would make MorDIFF a seen family.
6. **SelfMAD row on the corrected MAD22** and the e-mails to the authors of FD-MAD, IDistill, SelfMAD, MADation and SMDD (after the experiment stage).
7. **CelebA-HQ mirror:** please check it before it is used as a source.
