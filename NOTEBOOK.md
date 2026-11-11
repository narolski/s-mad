# Notebook

One line per idea. Newest state only; history is in git. Updated by the lead after every result.

Status: `planned` → `ready` (pre-registered, command tested) → `running` → `done` → `reviewed`.
Verdict: `yes`, `no`, `mixed`, or blank.

Last update: 11 Nov 2026, 15:15 CET. Started. WCSS: 48 one-GPU slots queued (jobs 6301498, 6301499).

## Where we stand, in five lines

- Shown: benchmark files differ by class; SelfMAD's diffusion results follow photo history.
- Partly shown: MADation ViT-B/16 on MorDIFF follows decoding step count.
- Not shown: any cue use on GAN or landmark morphs; any detector reading two identities.
- No training change has removed a shortcut so far.
- Next: one test design (morph vs camera, twin vs camera, morph vs twin) applied to every family and
  every released detector, then a detector trained on twins.

## Audit: do existing detectors read the morph or the benchmark

| Experiment (ID) | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| Landmark ladder (AR1) | Landmark: do detectors flag a one-person "self-morph" like a real morph? | planned | | | build pairs (FRLL, FRGC, colorFERET) |
| Landmark dose curve (AR2) | Landmark: does the score rise with the mixing fraction? | planned | | | after AR1 |
| Single-cue baselines (AR3) | Which single cues separate the classes on their own (file, thumbnail, border, background)? | planned | | | |
| Face-blanked and background-blanked scoring (AR4) | Do detectors still work with the face blanked, or the background blanked? | planned | | | |
| Border-matched history control (AR5) | Photo-history control with identical borders | planned | | | |
| Look-alike bins (AR7) | Landmark: does the signal weaken for look-alike pairs? | planned | | | after AR1 |
| MorDIFF ladder re-read (AD1) | MorDIFF: ladder for the released detectors (re-read of existing scores, post hoc) | reviewed (accept-qualified) | Three adapted releases: morph vs one-photo reconstruction 0.48 / 0.49 / 0.40. One frozen-encoder release (MADation FE ViT-L/14) does separate them: 0.66 at 20 steps, 0.85 at 100, without reacting to rendering. Giving genuine photos the morphs' resolution history raises the share flagged from 5 to 54% (ViT-B/16), 26 to 51% (ViT-L/14), 2 to 98% (SelfMAD), at each detector's own EER threshold. Descriptive: published error not reproduced on our frames | adapted releases: no reaction to the mixing step; one frozen-encoder release: yes | FZ1 (frozen features), AD1b (identical and mirrored inputs), own-crop re-score |
| DiM ladder (AD2) | DiM and Greedy-DiM: same | planned | | | needs twin generation |
| History control on a second photo pool (AD3) | Photo-history control on a second photo pool (not FRLL) | planned | | | scoring only |
| Morph-free networks (AD4) | Can a network that never saw a morph pass the benchmarks? Two recipes × 5 seeds, plus 5 label-permuted networks and one untrained network per recipe | 20 tasks released to the WCSS queue (no slot forecast before 13 Nov 23:20); ViT-B/16 arm moved to one rented GPU machine, cap 10 USD | Untrained ViT-B/16 network is not at chance on FRLL landmark cells (AUC up to 0.72); MorDIFF 53.9% | | pre-run review running |
| Retrains of released methods (AD5) | Do retrains of SelfMAD and MADation behave like the released checkpoints? | planned | | | WCSS |
| MIPGAN one-person controls (AG1) | MIPGAN: are one-person MIPGAN outputs flagged like morphs? | planned | | | needs x86 GPU |
| GAN-reconstructed genuine photos (AG2) | MIPGAN: does accuracy vanish when genuine photos are GAN reconstructions? | planned | | | needs x86 GPU |
| GAN dose curve (AG3) | GAN: score against two-person mixing fraction | planned | | | with AG1 |
| Morph-free GAN network (AG4) | Can a network that never saw a morph pass the GAN cells? | planned | A47: no, for the photo-history cue | | WCSS |
| StyleGAN3 ladder re-read (AG5) | Existing StyleGAN3 sets under the ladder rules (post hoc) | reviewed (wording corrected) | No network of 55 separates StyleGAN3 two-identity morphs from one-identity renders (best 0.61). Absence result; only 48% of these morphs verify against both contributors | absence | AG1 for a causal reading |

## Method: can a detector read identity blending

| Experiment (ID) | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| First twin-trained heads (T0) | First signal: twin-trained head on frozen features, existing StyleGAN3 and DiffAE sets | partly done by Codex, 11 Nov | no transfer between generators (0.26 to 0.52); held-out sets 0.46 to 0.63; only 16 to 90 training pairs | no (underpowered) | rerun at 2,000 pairs |
| Last-layer refit of released detectors (T2) | Do released detectors' features hold the signal if only the last layer is refit on twins? | planned | | | after features |
| Typicality detector (T3) | Is a morph a more "average" face in face-recognition space? | planned | | | after features |
| Twin-trained detector matrix (T4) | Twin-trained detector, 3 backbones × 5 seeds, held-out tool and generator | planned | | | after TwinSet |
| Two-contributor embedding head (T5) | Can a head recover both contributors' identities from one image? | planned | | | after T4 gate |
| Mixing-fraction regression (T6) | Mixing fraction regression: ramp or step? | planned | | | after T4 gate |

## New method line: targets that vary inside the image

| Experiment (ID) | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| Alpha-field probe (AF0) | Can a per-patch head on frozen features learn a mixing-fraction map, and does its mean separate real morphs from processed genuine photos without reacting to photo history? Includes a deliberately confounded training set as a stress test | running (owner assigned 15:10) | | | falsifiers in `experiments/AF0/prereg.md` |
| ID1 | Ideation round 1: seven independent idea generators | running | | | lead consolidates, then a vetting round |
| Frozen features read mixing (FZ1) | Do frozen foundation features read the mixing step of diffusion and GAN morphs, where adapted detectors do not? Probe, plus five fresh heads on frozen CLIP ViT-L/14 trained on SMDD | running | | | falsifiers in its prereg |
| Expression cue use (C1b) | Is the expression imbalance used by detectors? All detectors, all cells, neutral-only genuine column | reviewed (corrections required, applied) | 12 of 17 cells imbalanced (11 scored). Dropping the smiling half of the genuine class raises the released MADation ViT-L/14 error by 4.5 points on average (AMSL 17.7 to 24.5) and lowers the frozen-encoder ViT-B/16 error by 9.4; rankings move. But the smiling FRLL photos also differ in capture detail (larger file and noisier backdrop in 102 of 102 persons), and the ViT-L/14 ordering fades when detail is removed and is absent on two other photo pools | benchmark numbers depend on the smiling half; the cause (expression or capture detail) is not settled | neutral-only headline column; register the separation checks; FRLL neutral+smiling controls are confounded |
| Identical and mirrored inputs for diffusion (AD1b) | Is a diffusion morph of two identical photos the reconstruction, and does a horizontal flip give a real second image? | running | | | fixed readings in its prereg |
| Fixed-threshold re-read (EV1) | At one fixed threshold: how many processed genuine photos are flagged, how many morphs are missed, what morph-blind models already reach, and does any score rise with the dissimilarity of the two contributors? Existing scores only | done, in review | On our frames, at the threshold giving 5% false alarms on development photos: released MADation ViT-L/14 flags 24 to 34% of genuine photos at JPEG quality 50, 24.5% of photos stored at the published MorDIFF size and 22% of FFHQ photos; ViT-B/16 flags 23 to 36% of history-matched MorDIFF and DiM copies; SelfMAD flags 96 to 100% of resampled or stored-small photos. Stored-file width separates the classes in all 17 cells; only 3 of 17 cells cannot be solved at AUC 0.90 by a morph-blind model that sees the aligned frame. Identity-dose slopes are weak and vanish within gender. ViT-L/14 prefers the neutral photo in 0.99 of FRLL persons but 0.41 of FEI persons | failures under benign processing shown on our frames; benchmark cells mostly solvable without morph knowledge | own-crop re-score (RS1) must confirm; independent review running |
| SMDD five-partner audit and rebuild (SM1) | Do released detectors score morphs with the five training partners higher than with unused partners? Does a rebuilt training set (balanced partners, warped halves as genuine images) change what a head learns? | running | Verified on disk: 15,000 training morphs share 5 second contributors; no genuine render is a contributor | | |
| Identity-shrinkage triage (ID0) | Is a morph measurably closer to the average face, with a detector fitted on genuine photos only, and what is the ceiling? | running | | | mostly CPU |
| Ideation round 2, vetting (ID2) | Novelty checks, contradictions in our record, three hostile reviews of the consolidated method | done | Softness alone separates a morph from its own warped halves at 0.76 to 0.87 (measured), at the level of the probe's pass marks; the blend-map target is a known map times a source difference; our frames do not reproduce the releases' published numbers (AMSL 17.7 against 7.26 for MADation ViT-L/14); the audit and the method did not meet on the same cells | method line demoted to a candidate; paper rebuilt around a failure that needs no class ruling and a training protocol that removes it (`ideas/CONSOLIDATED_v2.md`) | controls added to the alpha-field probe (AF0); own-crop re-score (RS1) started |
| Own-crop re-score of the audit rows (RS1) | Do the audit findings about released detectors hold when each release is scored through its own preprocessing, where its published number is reproduced? | running | | | about 1 GPU-hour on the DGX |

| Signal isolation by paired differences (PD1) | The author's idea: can the morph signal be learned from morphs of one image with itself, its mirror, or another photo of the same person, and does a head trained only on such one-person images detect two-person morphs? Per family (landmark, diffusion, GAN), each result attacked by an independent sceptic, then a cross-family test | running (workflow of 7 agents) | | | fixed readings in each family's prereg |

| What the smiling half carries: expression or capture detail (C1c) | Is the smiling-half effect expression, or the capture-detail difference of the FRLL smiling files? All score sets, three photo pools, registered variants | done | Smiling FRLL files are 1.43 times larger and their backdrop 4.8 times noisier in 102 of 102 persons; FERET and FRGC pairs have no such difference. Released MADation ViT-L/14: preference for the neutral photo falls with resolution on FRLL (0.99 to 0.78) and is near chance on FERET (0.56) and FRGC (0.57): mainly capture detail. Last-checkpoint ViT-B/16 retrains: detail. Last-checkpoint ViT-L/14 retrains: near 1.00 on FRLL at any resolution but 0.5 on other pools, so something specific to the FRLL files. Early-stopped retrains and frozen-encoder releases: expression itself (0.60 to 0.76 on FERET, reversed sign for the frozen-encoder releases). At a fixed threshold the release flags 6 of 102 neutral against 1 of 102 smiling photos | the smiling half matters for benchmark numbers; for the leading release the cause is mainly capture detail, not expression | neutral-only genuine photos as headline (ViT-L/14 release: 20.2% against 15.6%, rank 4 to 7 of 9); independent review to follow |

## Data extension: does more or different training data remove cue use

| Experiment (ID) | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| Derived data-extension numbers (X0) | Register the numbers derived from the 60 existing fits: adding photos cuts the diffusion history effect by 13 to 29 points in all four architectures; adding classical morphs gives 9 to 22 back | planned | post hoc, exploratory | | write up, 0 GPU |
| Re-score of the 60 existing fits (X1) | Re-score the 60 existing fits and the older checkpoints on the unseen-source landmark set (H1) and on twin sets | planned | on benchmarks: no effect of added data | | about 0.5 H100-h |
| Matched vs unmatched added data (X2) | Same backbone and same image count, matched (twins) vs unmatched added data | planned | | | frozen heads, about 1 H100-h |
| History control on FFHQ photos (X4) | Photo-history control on a photo pool no network was trained on (FFHQ) | planned | | | about 0.3 H100-h |
| Landmark twins from an unseen source (X5) | Landmark twins from an unseen source (CASIA), built with the unchanged approved script | planned | | | CPU |
| Pipeline-count ablation (X3) | Does the number of different pipelines per class matter once twins are present? | planned | | | cut first |
| — | Generated-morph training arms (CG, CD, CGD) of the old plan | retired (author, 11 Nov) | | | |

## Zero-compute cue checks (from the cue table)

| Experiment (ID) | Question in plain words | Status | Result | Verdict | Next |
|---|---|---|---|---|---|
| Cue check: expression balance (C1) | Are expressions balanced between classes in each benchmark cell? | reviewed | No in 12 of 17 cells: genuine class is half smiling, morphs are neutral (DiM x6 by README, FRLL-Morphs x5 by a probe, corrected MAD22 Webmorph by file names). Expression alone gives AUC up to 0.75 | cue exists; reviewer preview: used by CLIP-based MADation networks (ViT-L/14 release scores neutral above smiling in 101 of 102 persons; AMSL error 17.7 to 24.5 with neutral-only genuine photos), not by CNN recipes or SelfMAD | C1b registers and reruns it |
| Cue check: person overlap (C2) | Do any persons appear in both training sets and test benchmarks? | done, in review | No FRLL image in any audited training set by path or label. SelfMAD's shipped configuration picks the checkpoint by FRLL-Morphs test error; whether the release used it is unknown | no overlap found; one selection risk | face-matching check not run |
| Cue check: colour statistics (C3) | Do colour statistics alone separate the classes? | done, in review | Yes on aligned crops: AUC 0.71 to 1.00 per cell (0.61 to 0.98 without the border) | cue exists; use untested | |
| Cue check: chroma subsampling (C4) | Does chroma subsampling alone separate the classes? | done, in review | Only corrected MAD22 Webmorph (AUC 1.00); elsewhere it coincides with PNG vs JPEG | cue exists in one cell | |

## Data builds

| Build (ID) | What | Status | Size | Where |
|---|---|---|---|---|
| Pair lists (D1) | Pair lists: same-person and two-person, matched, identity-disjoint splits | planned | | |
| Landmark image build (D2) | Landmark morphs, self-morphs, pipeline-only, graded mixing | planned | | DGX CPU |
| GAN twin build (D3) | MIPGAN and StyleGAN twins | planned | | WCSS, Vast as fallback |
| Diffusion twin build (D4) | DiffAE and DiM twins | planned | | WCSS, Vast as fallback |
| Feature cache (F1) | Feature cache for all detectors and backbones | planned | | DGX |

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
- 11 Nov 15:15: first results in (AD1, AG5, C1 to C4), under independent review. Alpha-field probe AF0 pre-registered and assigned. WCSS: 108 slots queued, none started.
- 11 Nov 15:40: found that the landmark "tool on one photo" rung is pixel-identical to the photo. Added warp-only and mirror self-morph rungs (amendment in `11_AUDIT_PLAN.md`). Strategist's 16 ideas in `ideas/IDEAS_v1.md`.
- 11 Nov 16:40: independent review of AD1, AG5, cue checks in `experiments/reviews/`. Two earlier sentences withdrawn (flag-rate range; "41 of 42"). New: one frozen-encoder release reads the mixing step; CLIP-based networks use expression. Owners assigned: FZ1, C1b, AD1b.
- 11 Nov 17:30: ideation consolidated. New owners: fixed-threshold re-read (EV1), SMDD five-partner audit and rebuild (SM1), identity-shrinkage triage (ID0); alpha-field probe gets a second wave (ghost-energy target, warped halves as negatives). Naming rule adopted: plain name first, ID in brackets.
- 11 Nov 18:15: morph-free networks (AD4) staged, tested locally, released; WCSS forecasts no start before 13 Nov 23:20, so the ViT-B/16 arm goes to one rented machine (cap 10 USD). PLGrid account `plgpnarolski` is not provisioned on WCSS (checked).
- 11 Nov 18:40: expression cue use (C1b) finished: pre-registered test held; count corrected to 12 of 17 imbalanced cells. Cue table updated (dated list at its top).
- 11 Nov 19:00: literature check on class definitions done (126 claims re-opened by a second agent). Formal definitions count subjects; labelling of same-person morphs is split and undiscussed; no convention for one-photo reconstructions. Proposal in `14_CLASS_DEFINITIONS.md` awaits the author.
- 11 Nov 19:40: author approved the rented-GPU run of the ViT-B/16 arm of the morph-free networks experiment (AD4); owner resumed. Lease: 2x RTX 4090, 0.73 USD per hour, cap 10 USD.
- 11 Nov 20:30: morph-free networks (AD4): pre-run review said the registered batch does not fit 24 GB; first rented machine destroyed before any task ran (0.11 USD); second lease is 2x RTX PRO 5000 with 72 GB each at 0.96 USD per hour, newer PyTorch (deviation, to be registered as amendment 1). Author approved stopping the Codex CLIP fits and using WCSS CPU nodes; the stop command was blocked by the permission system and is with the author.
- 11 Nov 21:00: independent review of the expression cue use study (C1b): corrections required. The smiling FRLL photos differ from the neutral ones in capture detail as well as expression, so "uses the expression cue" is withdrawn; the error shifts stand. FRLL controls that mix neutral and smiling photos are confounded.
- 11 Nov 22:00: vetting round done; consolidation revised (`ideas/CONSOLIDATED_v2.md`). Rented machines for the morph-free networks experiment (AD4): two single-A100 machines (same PyTorch as the cluster), one reachable and uploading, one starting; earlier leases aborted at 0.27 USD in total.
- 11 Nov 22:40: author decisions recorded (SMDD licence accepted; softened examples approved through the existing path; emails to other groups after the experiments stage). Started: signal isolation by paired differences (PD1). SMDD rebuild submitted as WCSS CPU job 6301971. PLGrid account not yet usable from this machine.
- 11 Nov 23:20: fixed-threshold re-read (EV1) finished. WCSS and Helios login nodes refuse connections from our address since about 16:55 (probably a block after my repeated failed PLGrid login attempts); all cluster logins stopped; sparse probe running. The owner agent of the morph-free networks experiment (AD4) was stopped by the author; training continues on the two rented machines under their watchdogs.
