# Resources

All hours are estimates. H100-hour = one hour of one NVIDIA H100.

## What the plan needs

| Work | GPU-hours | Kind of GPU | Why there |
|---|---|---|---|
| GAN inversion and mixes (D3) | 80 | any 24 GB card | embarrassingly parallel, one pair per task |
| DiffAE mixes (D4) | 120 | any 24 GB card | same |
| LoRA training, 3 backbones × 5 seeds (T4) | 60 | H100 or 5090 | batch fits in 24–32 GB |
| Heads, features, audits, guards | 25 | DGX GB10 | small, no queue |
| Morph-free repeat, benchmark scoring | 20 | WCSS H100 | scorers already live there |
| Total | about 300 | | |

## Recommendation

1. **Vast: 8 × RTX 5090 (or 4090) for about 30 hours, in two 4-GPU machines.** About 200 GPU-hours of
   generation finish in one day of wall time. At typical prices this is 100–150 USD. The current
   ceiling is 100 USD with about 15 USD on the account, so the ceiling and balance need raising to
   250 USD.
2. **WCSS: 8 concurrent H100 jobs** for T4 and scoring from Friday. If the queue forecast stays at
   more than 6 hours, T4 moves to the Vast machines after generation ends.
3. **DGX GB10:** all frozen-feature work. It must be free of the other loop's jobs, or share by
   agreement (decision 5).
4. **B200: not needed.** The workload is many small independent tasks. A B200 would run one of them
   faster and leave most of its memory unused. Eight consumer cards give about four times the
   throughput per dollar here. It would only pay off for full fine-tuning of ViT-L at large batch,
   which the plan avoids on purpose.

## Using rented machines fully

- One work queue per machine: a file of tasks, one worker per GPU, each task writes its output and a
  done-marker; workers pull the next task until the file is empty. No GPU waits for another.
- The machine is rented only after the pair lists (D1) exist and the generation command has passed an
  8-image test on the DGX.
- Inputs go up as one tar pack; outputs come back as tar packs every 30 minutes, so a lost machine
  loses at most 30 minutes.
- When generation ends, the same machines take the LoRA runs. The lease is closed the minute its queue
  is empty; a watchdog on the DGX enforces a hard cost stop.
- Target: above 90% GPU utilisation, checked from `nvidia-smi` logs kept with the results.

## Other things to arrange

| Need | Why | Who |
|---|---|---|
| Written scope for FRGC and colorFERET (may we publish derived morphs? features only?) | decides whether TwinSet can be released, and unblocks generation | author |
| StyleGAN2 inverter and DiffAE on x86 | the DGX is ARM; the x86 DiffAE build failed in A139 | us, on Vast (prebuilt container) |
| 150 GB free on `/mnt/t7` | TwinSet about 100 GB; 357 GB free now | fine |
| Released weights for each compared detector | twin audit "as released" | have SelfMAD, MADation; check the rest |
| Agreement on which loop owns the DGX and WCSS slots until 16 Nov | two loops, one repository, shared budgets | author |
| Kamil: 2 hours on Saturday for a read of the tables and the claim wording | independent human check before text is frozen | author |
