# Morning report, 12 November 2026

Written 05:35 CET by the lead for Paweł Narolski. Reviewed results only, unless a line says otherwise. Sources are the experiment folders and the reviews in `experiments/reviews/`.

## 1. Method verdict

**No positive method claim survives yet.** The protocol network (PN1: MADation recipe, CLIP ViT-B/16 with LoRA, eight fits on two seeds) does not pass its registered marks, and the planned fixed-threshold claim is dead for these networks.

What the eight fits and the second batch show (reviews `REVIEW_PN1_TIER1_20261112.md`, `REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md`):

- **Registered reading:** the protocol arms (B, Bn, C) do not pass; three marks fail on both seeds; no kill rule is met. The plain arm (A) fails robustly.
- **The protocol removes the reaction to storage history.** At its own rule the plain network flags 20% and 32% of photos stored at 61 px; the protocol arms flag 0.5 to 3.1%. On 2,000 unseen FFHQ persons the plain network's score rises for 72 to 78% after shrink-and-enlarge, against 30 to 44% for the protocol arms (post hoc).
- **Thresholds do not transfer between genuine sources.** The output is bounded near ±3.87 and training-database photos sit on that floor. A threshold set there flags 30 to 95% of FRLL, 95 to 98% of FFHQ and 99.5 to 100% of H1 genuine photos. Ranking does transfer (AUC 0.988 or more within FFHQ).
- **The protocol costs detection of face-spliced attacks** (H1 AUC 0.07 to 0.17 below the plain recipe).
- **Spliced morphs in training restore it** (H1 AUC 0.06 to 0.09 above the plain recipe; face-only read 0.94 and 0.96 against 0.84 and 0.87). This arm was killed by its registered rule, which tested surround reliance. It is a lead from first-test data on two seeds, not a result, and it is close to existing self-blending practice.

**What the evidence supports now is a diagnostic paper:**

1. Standard recipes read storage history; protocol negatives remove that.
2. Ranking transfers across genuine sources, thresholds do not.
3. Full-frame morphs are detectable from the surround alone (0.999 with the face blanked); the face-interior read governs face-spliced attacks.
4. Released detectors do not beat simple-statistic floors on controlled contrasts.
5. Morph-free networks trained only on softness reach near-zero error on several benchmarks.
6. On diffusion morphs the separability is in the render path, not in a second identity.

## 2. Cue table and findings

`08_CUE_MATRIX.md` has nine new reviewed rows dated 12 Nov: bounded output scale and threshold transfer; resampling history (reproduced, and removed by protocol negatives); scoring-path dependence (JPEG decoder build, detector boxes, the authors' crop script); partner structure; softness as a sufficient cue; blend in the surround; diffusion render path; one-person training; MAD22 and FRLL genuine classes are the same 204 photos.

## 3. What ran overnight and what it cost

| Experiment | Where | State | Cost (USD) |
|---|---|---|---|
| Protocol network (PN1): 8 fits, reference row, spliced arm, volume control, rescoring, FFHQ test | two rented A100s | done, reviewed, machines released | 12.6 |
| Own-crop re-score (RS1) | rented | done, reviewed, released | 1.4 |
| Diffusion add-on generation (DG1) | rented | done, released; face codes of shard 7 were not copied back and no longer exist (images and results are safe) | 1.8 |
| Frozen read of the diffusion ladder (FZ2) | DGX | done, reviewed, closed | 0 |
| Blending-trace floors (AR1 amendments 9 to 11) | DGX | done, reviewed | 0 |
| Morph-free networks (AD4), review corrections | DGX | done; three ViT-L/14 reruns stuck on Athena | 0 |
| SMDD rebuild (SM1), ViT-B/16 fits | rented A100 | 4 of 12 fits back; registered reading at the eighth, about midday | 5.1 so far, cap 12 |
| MIPGAN controls (AG1) | rented A100 | in production since 03:17, 9 to 18 hours of work; accepted under a looser platform rule by lead decision, not a registered pass | 1.4 so far, cap 10 |

Rental spend since your approval: 27.1 USD of the 50 (credit 105.1 to 78.0). If both running machines reach their caps the total is about 43 USD.

Athena is closed for the sprint in practice: fair-share is exhausted and Slurm forecasts new jobs for late December. WCSS is still not reachable.

## 4. Decisions needed on 12 November

1. **Is any FFHQ morph family reserved as an endpoint in the main registration?** A small test of the spliced-morph lead on FFHQ "combined" morphs is ready (about 0.3 USD) and held for this answer. Note: the FFHQ "complete" family was already read on the eight PN1 networks last night under a registered amendment.
2. **May the killed spliced arm be refitted on fresh seeds?** The pre-run reviewer wants your ruling because the refit was chosen after H1 had been seen.
3. **Fresh-seed budget.** Recommended: plain, protocol and protocol-plus-spliced arms on five seeds plus one replicate, 16 fits, about 11.6 USD, about 11 hours on two machines. With the JPEG arm at three seeds: 19 fits, about 13.8 USD. Tonight's 50 USD approval does not cover this.
4. **Paper direction.** Diagnostic paper as in section 1, with the spliced-morph result added only if fresh seeds replicate it. Yes or no.
5. **Stuck on Athena, to rent or drop:** retrains table (AD5: ViT-B/16 17 A100-hours, ViT-L/14 64, MixFaceNet 34, SelfMAD 150); 23 SMDD-rebuild ViT-L/14 fits; 3 morph-free ViT-L/14 reruns. At about 0.5 USD per A100-hour.
6. **Disk.** `/mnt/t7` has 25 GB free. The deletion list in `docs/DISK_CLEANUP_PROPOSAL_20261111.md` (about 138 GB of second copies) needs your yes.
7. **Still open from before:** blur, resample and chip branches on training images; a JPEG genuine pool from raw MAD22; a shrink size below 61 px; the web server on port 8000; the helpdesk mail to WCSS.
8. **Only if wanted:** diagnostic diffusion images with an edited noise map. I recommend no; the diffusion line is closed.
