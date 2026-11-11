# Resources

All hours are estimates until the first timed run. H100-hour = one hour of one NVIDIA H100.
Budget rules from the author (11 Nov): WCSS as much as the scheduler gives; Vast 20 USD now, 100 USD
at most, each lease justified; ablations on WCSS.

## Where each kind of work runs

| Work | Estimate | Runs on | Why |
|---|---|---|---|
| Landmark morphs, self-morphs, graded mixing | CPU, half a day | DGX CPU (WCSS CPU array if slow) | no GPU needed |
| Features, heads, audits on twins, cue baselines | 25 GPU-h | DGX | small jobs, no queue |
| MIPGAN, StyleGAN and DiffAE twins for the audit (about 2,000 pairs per family) | 35 GPU-h | WCSS first | needs x86; free |
| Twin training data at scale (10,000 pairs per generator family) | 150 GPU-h | WCSS; Vast only as overflow | only after gate 0 shows a signal |
| Morph-free networks, retrains of released methods, LoRA runs, benchmark scoring | 150 H100-h | WCSS | ablations and long jobs |

## Queue strategy on WCSS

- At approval, everything long is submitted in one batch so it ages in the queue: AD4/AR6, AD5, AG4
  and the generation arrays. Scripts are tested on 8 images locally first.
- Generation is an array of small tasks (one H100, 2 hours each). Small jobs backfill into gaps that
  14-hour jobs cannot use.
- Generation arrays are submitted in two priority steps so that the audit set (small) is never behind
  the training set (large).
- Polls follow job ETAs. One SSH connection at a time.

## Choosing a rented card (author, 11 Nov)

Pick the cheapest card that fits the measured peak memory, ranked by price per unit of work and by the
host's reliability score. Smaller cards (RTX 3080, 4080, 5080; 10 to 16 GB) are preferred for
generation and scoring; 24 to 32 GB cards (RTX 4090, 5090) for LoRA training of large backbones. An
RTX Pro 6000 or larger is used only when a measured peak exceeds 32 GB. Every task logs its peak
memory in its smoke test, and the lease is sized from that number.

Host filter: reliability at least 0.98, verified, x86 with a CUDA 12 driver, download speed enough to
receive the input pack in under 10 minutes. A host that fails to start within 10 minutes, or shows a
different card than advertised, is replaced and noted.

## When Vast is used, and what it returns

Vast is a way to skip the WCSS queue for data that many experiments wait on. A lease is opened only
if the forecast WCSS start is later than the Vast finish.

| Lease | Produces | Unblocks | Cap |
|---|---|---|---|
| V1 | MIPGAN one-person twins and reconstructions for the 102 benchmark persons; DiM twins | AG1, AG2, AG3, AD2: the GAN causal test and the diffusion extension | 20 USD |
| V2 | GAN and DiffAE twin pairs for training | T4 on generator morphs | 40 USD, only after gate 0 is positive |
| V3 | Reserve for one rerun | — | 40 USD, needs the author's yes |

No training and no ablation runs on Vast. Each lease uses one task queue per machine, one worker per
GPU, results copied back every 30 minutes, and a watchdog that closes it at the cap.

A B200 is not needed: the work is many small independent tasks, and several ordinary cards finish
them sooner per dollar.

## Other needs

| Need | Why | Who |
|---|---|---|
| Hand-over of the DGX from the other loop | all quick work runs there | author |
| x86 build of MIPGAN and the StyleGAN inverter | StyleGAN inversion has only run on x86 so far; DiffAE already runs on the DGX | us; first task on WCSS CPU |
| SelfMAD release weights copied back from WCSS | local copies are placeholders | us, first WCSS connection |
| 150 GB on `/mnt/t7` | TwinSet; 357 GB free | fine |
| Released weights of further detectors | wider audit table | see `10_ASSET_INVENTORY.md` |
| Two hours of Kamil's time on Saturday | human read of tables and claim wording | author |
