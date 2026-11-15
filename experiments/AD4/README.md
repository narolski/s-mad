# Morph-free networks (AD4): full record

Written 11 Nov 2026, 17:45 CET, by a documentation agent from the files, logs and agent transcripts listed in each
section. Times are CET. Agent transcripts carry UTC; they were converted (+1 h). The verdict file is
`/home/narolski/smad-next/experiments/AD4/result.md`; the registration is
`/home/narolski/smad-next/experiments/AD4/prereg.md` (with Amendment 1 and Amendment 1b). This README is the full
record. It follows `/home/narolski/smad-next/DOCUMENTATION.md`.

Abbreviations used throughout:
- **EER**: equal error rate, the error at the threshold where the share of missed morphs equals the share of flagged
  genuine images.
- **AUC**: area under the ROC curve. "Signed AUC" means morph is the positive class and the value is not folded
  (an AUC below 0.5 means the network ranks morphs below genuine images).
- **SMDD**: the synthetic training set of face renders (genuine class) used to train the released MADation
  detectors.
- **FRLL**: the Face Research Lab London photo set; its morph sets ("FRLL-Morphs": AMSL, FaceMorpher, OpenCV,
  Webmorph, StyleGAN) are benchmark cells. No FRLL person enters any training.
- **MorDIFF**, **DiM** (six diffusion-morph families: DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM,
  Greedy-DiM-S): diffusion morph benchmarks built on FRLL.
- **Corrected MAD22**: the full MAD22 benchmark delivered by its authors and aligned by us
  (`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`), families FaceMorpher, OpenCV, Webmorph
  (landmark) and MIPGAN-I, MIPGAN-II (GAN).
- **E7**: genuine photos given the morphs' shrink-and-enlarge history (rung R1 of the ladder in
  `/home/narolski/smad-next/EXPERIMENTS.md`). "Native cell" = family morphs against the set's genuine photos;
  "E7 cell" = family morphs against that family's E7 genuine photos.
- **CLIP ViT-B/16, ViT-L/14**: the OpenAI CLIP vision transformers (patch 16 base model, patch 14 large model).
- **LoRA**: low-rank adaptation, here rank 2 on the attention query and value projections; only LoRA and the
  linear head are trained.
- **TTA**: test-time augmentation; the score is the mean of the sigmoid of the image and of its horizontal flip.
- **M3** = the ViT-B/16 recipe (batch 256, 6,250 steps); **M3L** = the ViT-L/14 recipe (batch 32 with 8
  accumulation steps, 6,250 steps). Same learning rates and other settings (section 4).
- Arms: **morph-free** (`mf`, true labels), **label-permuted** (`perm`, labels shuffled per seed), **untrained**
  (`zero`, the network before its first training step). Task names `AD4_<recipe><arm>_s<seed>`, for example
  `AD4_m3mf_s401`.
- Machines: **DGX** (this ARM machine, one shared NVIDIA GB10), **T7** (the 1.8 TB data drive `/mnt/t7`),
  **WCSS** (Wrocław supercomputer, H100 cards, Slurm queue), **Athena** (Cyfronet PLGrid cluster, A100 40 GB),
  **Vast** (vast.ai, rented GPU machines; "lease" = one rented machine). **SSH**: remote login.
- Related experiments: the original morph-free experiment (A47, part I-3; before 11 Nov, see
  `/home/narolski/mambamorph-code/experiments/A47_training-interventions/`), the benchmark-recipe retrains (A12BR),
  the SMDD five-partner audit and rebuild (SM1). The registration says AD4 "also serves AR6", the descriptive read
  of all other benchmark cells; AR6 has no plain name in `EXPERIMENTS.md`.

---

## 1. Question and current answer

**Question.** A network that never sees a morph is trained only to tell SMDD renders (label 0) from their own
shrunk-and-enlarged copies (label 1), using the registered A47 part I-3 data. How low is its error on the morph
benchmark cells (MorDIFF and the six DiM families first; FRLL landmark and StyleGAN cells and corrected MAD22
including MIPGAN as description)? If it passes the diffusion cells, those cells measure processing history, not
morphing (hypothesis A1 in `/home/narolski/smad-next/04_HYPOTHESES.md`). References per recipe: five networks
trained on the same images with shuffled labels and one untrained network. Two recipes (ViT-B/16 and ViT-L/14),
seeds 401 to 405, last checkpoint, no selection: 20 trained networks plus 2 untrained ones.

**Current answer (11 Nov 2026, 17:45 CET): none yet. Status: running for ViT-B/16, blocked for ViT-L/14.**
- No trained network of this experiment has been scored. The first one (`AD4_m3mf_s401`, machine A) finished
  training at about 17:40 and was being scored at 17:43 (`/mnt/t7/smad_next/AD4/vast/leaseA/remote/logs/AD4_m3mf_s401.log`).
- The ten ViT-B/16 fits run on two rented single-GPU machines under watchdogs. Expected end: machine A about
  22:00 to 23:20, machine B about 00:10 to 01:25 on 12 Nov (section 10; projections, not measured). The spending
  cap may bind on the last permuted fit (section 10).
- The ten ViT-L/14 fits wait. Athena does not yet accept the Slurm account (17:20, `ATHENA.md`). WCSS has been
  unreachable since about 16:55 (`NOTEBOOK.md`), and the same ten tasks also sit in its ready queue.
- Available so far: the untrained ViT-B/16 network's numbers. MorDIFF EER 53.9%. On FRLL landmark cells it is
  **not at chance** (EER 32.8 to 37.3%, AUC up to 0.72). The scorer-equivalence gate passed (largest |AUC
  difference| 0.0011), and the sample-order predictor reproduces a recorded order exactly (200 of 200 batches).
- The final reading (`src/AD4/summarise.py`, the gates of Amendment 1, the rules of Amendments 1 and 1b) has not
  been run. It belongs to the lead.

---

## 2. Timeline

Sources: the owner transcript
`/home/narolski/.claude/projects/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/subagents/agent-ac3d3ade3ea6e3fe5.jsonl`
(message numbers in brackets), the pre-run reviewer transcript `.../subagents/agent-aa72859b559814d57.jsonl`, the
lease folders under `/mnt/t7/smad_next/AD4/vast/`, file times, and process lists read at 17:36 to 17:43.

| Time (11 Nov) | What happened | Why / evidence |
|---|---|---|
| 14:23 | Owner agent starts on the morph-free networks experiment (AD4). | Lead's task [0]. |
| 14:24 to 14:32 | A47 I-3 recipe, scorer and data read. The A12 converted CLIP weights `hf/a12/` are not on WCSS Lustre, only inside the 31 GB `hf` pack. WCSS SMDD file sizes fetched to `/mnt/t7/smad_next/AD4/build/wcss_data_train_os25k.content` (25,000 lines). | [146]-[147], [214]-[215]. |
| 14:32 to 14:33 | `src/AD4/ad4_score.py` and `src/AD4/build_pack.py` written. | [218], [222]. |
| 14:33 to 14:36 | Pack built in 139 s: `/mnt/t7/smad_next/AD4/ad4_pack.tar`, 69,942 tar members, sha256 `1ad170be…`. | [231]-[233]. |
| 14:36 | `src/AD4/run.sh` written. Bug fixed before the first run: `py -I ad4_score.py` changed to `py ad4_score.py`. | [237], [241]. |
| 14:37 to 14:44 | DGX test `AD4_m3mf_s401` (3 steps, 8 scored images per manifest, 4 loader workers): rc 0, wall 452 s. | `/mnt/t7/smad_next/AD4/test/AD4_m3mf_s401.stdout.log`. |
| 14:40 | `prereg.md` written (before any score was read). | [256]. |
| 14:44 to 14:50 | Re-run of the finished task exits "already done" (idempotent). DGX test `AD4_m3lperm_s402` (ViT-L/14, 2 steps, 8 images): rc 0, wall 360 s. | [302]-[319]; `/mnt/t7/smad_next/AD4/test/AD4_m3lperm_s402.stdout.log`. |
| 14:48 to 14:55 | Pack uploaded to WCSS (5 min 12 s) and checked there (`ad4_pack.tar: OK`). The 20 task folders built with `make_tasks.sh`, uploaded as `staging_AD4.tar` and unpacked in WCSS `staging/AD4`. | [310], [314], [326]-[331]. |
| 14:51 | Untrained-network scoring started on the DGX, M3 first, then M3L (`--workers 6 --bs 64`). | [322]. |
| 15:05 | `result.md` written (preparation stage). | [353]. |
| 15:15 | Untrained M3 network scored (1,478 s: 454 s evaluation, 1,024 s training set). Metrics copied to `experiments/AD4/zero_step/metrics_m3.json`. The genuine E7 photos of MIPGAN-I are byte-identical to the native ones (`cmp`). | [379]-[389]; `/mnt/t7/smad_next/AD4/zero_step_m3.log`. |
| 15:35 | The first untrained-M3L scoring run (child of the agent's shell, no output after 20 min) was killed and restarted detached (`nohup setsid`, PID 1872565). The `pkill` pattern also killed the owner's own shell (exit 144). Two watchers (PIDs 1856530, 1873227) copy `metrics_m3l.json` when it finishes. | [428]-[442]. |
| 15:36 | Owner's first report: 20 tasks staged, none in the ready queue. | [452]. |
| 15:37 | Lead: the 20 tasks passed review and are in the WCSS ready queue, but WCSS forecasts no slot before 13 Nov 23:20. The ViT-B/16 arm goes to one Vast lease, cap 10 USD. Pre-run review starts. | [454]; reviewer [0]. |
| 15:38 | `prereg.md` first committed (commit 4068c3a), after the untrained M3 metrics were read at 15:15. The decision rule itself was committed earlier (commit 16ebda6, in `11_AUDIT_PLAN.md`). | Amendment 1 (f); reviewer finding 7. |
| 15:40 to 15:41 | Vast credit 111.85 USD, no instance of ours. Offer search done. The ten ViT-B/16 tasks moved from WCSS `queue/ready` to `staging/AD4`. WCSS job logs give the container's software: torch 2.2.1, CUDA 12.1, Python 3.10.13 (`apptainer` is not on the login node, so it could not be run there). | [488]-[516]. |
| 15:42 to 15:43 | `vast/remote_setup.sh`, `vast/remote_queue.sh`, `vast/watchdog.py`, `vast_api.py` written. | [485], [522]-[528]. |
| 15:43 | Instance creation (offer 58777466, 2x RTX 4090, China, 0.73 USD/h) refused by the session's permission system ("real-world transactions"). Ten tasks put back into `ready/`. | [543]-[548]. |
| 15:45 to 16:10 | Reviewer's read-only checks: model rebuild from the saved LoRA and head (0 of 203 tensors differ), the five permutations regenerated, EER tie behaviour, sample order (200 of 200), a CPU memory probe (32 to 36 GB estimate at batch 256). | Reviewer [173]-[291]. |
| 16:06 | Author approved the Vast run; owner retried the identical creation command; refused again. | [566]-[575]. |
| 16:07 | Lead: rental commands are run from the main session only. Owner moves the ten ViT-B/16 tasks out of WCSS `ready/` again (result: `ready_AD4=10 staging=10`, i.e. only the ten ViT-L/14 tasks stay in `ready/`). `vast/launch_remote.sh` and `vast/make_lease.py` written; smoke-step `wait` fixed (`|| true`); `remote_setup.sh` pins torch and torchvision to the image's versions with a pip constraints file. | [581]-[601]. |
| 16:08 | Lease 1 created by the lead: instance 60223497, 2x RTX 4090 (24 GB), Sweden, offer 35743571, 0.962 USD/h, image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, cap 9.6 USD, 8-hour deadline. | `/mnt/t7/smad_next/AD4/vast/lease1_2x4090_aborted/lease.json`. |
| 16:11 | Pre-run review delivered: go with fixes for the 20 cluster tasks; stop for the rented arm as configured (batch 256 does not fit 24 GB). | `/home/narolski/smad-next/experiments/reviews/PRERUN_AD4_20261111.md`. |
| about 16:13 | Lease 1 destroyed before any task ran; 0.11 USD. | `lease1_2x4090_aborted/README.txt`, last watchdog poll 16:13:35. |
| 16:14 | Lease 2 created: instance 60224295, 2x RTX PRO 5000 (72 GB each), California, offer 59841609, 0.993 USD/h, image `pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime`, cap 9.4 USD. | `lease2_2xPRO5000_unreachable/lease.json`. |
| 16:19 to 16:21 | E7 identity counts checked with `cmp` on the pack. Amendment 1 appended to `prereg.md` (header first "16:25", later changed to "about 16:21"). | [646]-[657], [768]. |
| 16:21 | Lease 2 reports "running" but refuses SSH (every watchdog poll ends with ssh exit 255). | `lease2_2xPRO5000_unreachable/watchdog.jsonl`. |
| 16:21 | One A47 I-3 checkpoint copied from WCSS (`last.pt`, sha256 `f9e391c4…`, equal to its registered list line) and scored on the DGX for the scorer-equivalence gate. | [674]-[678]. |
| 16:22 to 16:24 | `src/AD4/gates.py` written; the sample-order predictor reproduces A47 seed 1 (200 of 200) and gives the seed-401 prediction. `src/AD4/summarise.py` rewritten to follow Amendment 1; run on the empty result folder, it wrote `ad4_cells_m3.csv`, `ad4_train_m3.csv` (untrained network only) and an empty `ad4_gates_m3.json`. | [682]-[695]. |
| about 16:28 | Lease 2 destroyed under the ten-minute rule; no task ran. The two aborted leases cost 0.27 USD together. | `lease2_2xPRO5000_unreachable/README.txt`; Amendment 1b. |
| 16:30 to 16:45 | Machine A rented: instance 60226054, A100-SXM4-40GB, offer 58855597, 0.433 USD/h. Reachable 16:31, pack upload 476 s, setup OK 16:40, 200-step smoke test rc 0 (1.83 then 1.90 it/s, peak 30,839 MiB), queue started 16:45:21. | `/mnt/t7/smad_next/AD4/vast/leaseA/driver.log`, `smoke.txt`, `remote/queue.log`. |
| 16:31 to 16:44 | First machine B: instance 60226099 (offer 56042632, 1.00 USD/h) never reachable; destroyed 16:44:11 after 13 minutes. Next offer 59644447 not available. | `/mnt/t7/smad_next/AD4/vast/leaseB/driver.log`, `leaseB/unreachable_60226099/`. |
| 16:34 to 16:47 | Amendment 1b appended (header first "16:40", corrected to "16:37"); machine B's card filled in at 16:47. | [733], [764], [795]. |
| 16:44 to 17:00 | Machine B rented: instance 60227348, RTX 6000 Ada Generation (48 GB), offer 55800354, 0.738 USD/h. Reachable 16:45, pack upload 564 s, setup done 16:56, smoke test rc 0 (1.43 it/s, peak 30,842 MiB), queue started 17:00:27. | `leaseB/driver.log`, `smoke.txt`, `remote/queue.log`. |
| 16:46 | Scorer-equivalence gate passed on 24 cells. | `/home/narolski/smad-next/experiments/AD4/gate_scorer_equivalence.json`. |
| 16:47 | Owner's last message. The author then stopped the owner agent; the lead took over. | [808]; NOTEBOOK log. |
| 16:58 | Account credit drops 0.39 USD in one minute (0.645 to 1.033 USD since the baseline). Cause not identified. | `leaseA/watchdog.jsonl`. |
| 17:13 | Untrained M3L network: evaluation scores written; training-set scoring continues. | `/mnt/t7/smad_next/AD4/zero_step/m3l/scores_eval.npz`. |
| 17:20 to 17:29 | Athena: Slurm refuses both grant accounts ("Invalid account or account/partition combination"). Job scripts written in `src/athena/`. Lead's watcher `wait_and_submit_smoke.sh` started (PID 2085779, 9 tries every 20 min). The ten ViT-L/14 tasks were uploaded to Athena (lead's statement; no local log). | `/home/narolski/smad-next/ATHENA.md`; `src/athena/wait_and_submit_smoke.sh`. |
| about 17:31 | The SMDD five-partner audit and rebuild (SM1) sets up CPU-only work on machine B (`/workspace/sm1`, `nice -n 19`). | Process list 17:36; NOTEBOOK log "17:35". |
| 17:40 | Machine A: first network `AD4_m3mf_s401` trained (`train_hours` 0.872, "AD4 trained (3288 s)"); scoring started. | `leaseA/remote/logs/AD4_m3mf_s401.log`. |

---

## 3. Data

### 3.1 Training images (no morph anywhere)

- Root: `/mnt/t7/smad_heldout/a47/data47/i3` (registered A47 part I-3 data, built 7 Nov; nothing re-made).
- Manifest `manifests/train.csv`: 50,000 rows, sha256
  `0273c11bd0fe4b70fc9c5490859bc185ea50b9ed971a783993b843a399e7b880` (checked against `data47/i3/SHA256SUMS` by
  `build_pack.py`).
  - 25,000 SMDD genuine renders, label 0, `train/smdd/os25k_bf_t/*.png`. Byte copies of
    `/home/narolski/mambamorph-code/smadcvpr_data/train/smdd/os25k_bf_t/`; each size checked against the WCSS
    `data_train` pack listing `/mnt/t7/smad_next/AD4/build/wcss_data_train_os25k.content`.
  - 25,000 copies made by `prep_eval.degrade(img, "R", 0.3125)`, label 1, `train/smdd_a47e7/os25k_bf_t/*.png`
    (each checked against `data47/i3/SHA256SUMS`).
- In the pack: `ad4/data/manifests/train_i3.csv` (same sha256).

### 3.2 Label-permuted manifests

The same 50,000 rows; only the label column is shuffled with `random.Random(2026111100 + seed).shuffle`. Built by
`build_pack.py`; recorded in the pack's `ad4/build_info.json` (copy read from
`/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4/build_info.json`).

| Seed | Manifest in pack | sha256 | Labels changed | Label-1 rows |
|---|---|---|---|---|
| 401 | `train_perm_s401.csv` | `c0dfdb26fa793657678f1b5801e3e78b88d90f0ec86d8071b3a0f95ad0b254cd` | 24,930 | 25,000 |
| 402 | `train_perm_s402.csv` | `efdec77f112f420e7e08c1c58b2a30c4c90c78a0c6625eb337eaa23421ea7030` | 24,938 | 25,000 |
| 403 | `train_perm_s403.csv` | `a237185798994ac142b64bf29b6951596ea81b5c2675e71f0706eb727d247ea8` | 24,920 | 25,000 |
| 404 | `train_perm_s404.csv` | `47ebf4ea27a26c8c376a602800439af435e172508f574829ca7e07e620f77017` | 24,890 | 25,000 |
| 405 | `train_perm_s405.csv` | `df2a3d70a2603c767018571a547107bb623f6e13fe3130c4e3064b4a2259b93d` | 25,080 | 25,000 |

The reviewer regenerated all five from the seeds and found them identical; any two seeds agree on 49.6 to 50.2% of
labels (reviewer report, check 2).

### 3.3 Evaluation images

- Manifest `ad4/data/manifests/ad4_eval.csv`: 19,827 rows, sha256
  `5d3950ab5ccdeed4d376a15126cff660da2a35041579b3513eb7a1059baaa061`. Columns `id,path,set,family,label,variant,src_id`.
  - 14,120 rows from `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv`: sets `dim` (4,427 rows),
    `frllm` (8,285), `mordiff` (1,408); variants `orig` (native) and `resmatch` (E7) only.
  - 5,707 rows of corrected MAD22 (`mad22c`): `native/` 4,687 and `e7/` 1,020, each file checked against the
    folder's `PROCESSED_SHA256SUMS`.
  - Not used: the robustness variants of `eval.csv` (blur, JPEG, chip, resample50) and the old MAD22 subset of
    `eval.csv`. No file name contains `fst`, `valx` or `A12SP` (reviewer, check 3).
- Cells (built by `cells()` in `src/AD4/ad4_score.py`): 17 native and 17 E7 cells, 204 genuine images in every
  cell. Morph counts: MorDIFF 1,000; DiM families 500 each (Fast-DiM-ODE 499); FRLL AMSL 2,175, FaceMorpher 1,222,
  OpenCV 1,221, StyleGAN 1,222, Webmorph 1,221; corrected MAD22 FaceMorpher 1,000, MIPGAN-I 1,000, MIPGAN-II 999,
  OpenCV 984, Webmorph 500 (`experiments/AD4/ad4_cells_m3.csv`).
- E7 genuine copies that are byte-identical to the native genuine photos (checked with `cmp` on the unpacked pack
  [646]-[647]): FRLL StyleGAN 204/204, corrected MAD22 MIPGAN-I 204/204 and MIPGAN-II 204/204 (labelled "E7 not
  applicable"); corrected MAD22 OpenCV 108/204 and Webmorph 104/204 ("E7 partial"); every other E7 cell 0/204.

### 3.4 Model weights

Source: the timm hub files in `/home/narolski/.cache/huggingface/hub`, loaded with `weights_only=True` and written
as safetensors (the A12 "converted" path `hf/a12/`).

| Model | Source blob sha256 (= its file name) | Converted file in pack | sha256 | Bytes | Tensors |
|---|---|---|---|---|---|
| `vit_base_patch16_clip_224.openai` | `53b401837e5baa82115d3b6db60c6fff43cfd1a6412e48ed0193d54a69d2f993` (registered, `smadcvpr/PROTOCOL.md` line 12578) | `ad4/hf/a12/vit_base_patch16_clip_224.openai.safetensors` | `4b8699299b1e8997753c64b052ba32031449d5d853f55a039148560ee02b820f` | 598,516,980 | 302 |
| `vit_large_patch14_clip_224.openai` | `eb70c15b117effa76315db43fcbd9f32a655292fc861798343939a02f561c6ae` | `ad4/hf/a12/vit_large_patch14_clip_224.openai.safetensors` | `9ce2e8a8ebfff3793d7d375ad6d3c35cb9aebf3de7ace0fc7308accab7cd207e` | 1,710,517,724 | 446 |

Local copies: `/mnt/t7/smad_next/AD4/build/weights/`. A47's own converted files sit only inside the WCSS `hf` pack;
their listed sizes are 598,517,148 and 1,710,517,892 bytes, 168 bytes more than ours (`hf.content` listing read at
14:27 [136]). Tensor equality with A47's files was not checked. Weights are not redistributed.

### 3.5 The pack (one tar)

- `/mnt/t7/smad_next/AD4/ad4_pack.tar`: 11,193,948,160 bytes, sha256
  `1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde` (same constant `PACK_SHA` in `src/AD4/run.sh`;
  `.sha256` beside it). 69,942 tar members; `ad4/SHA256SUMS` lists 69,941 files. Not unpacked for this README.
- Contents (`build_pack.py` docstring): `ad4/code/smadcvpr/*.py` and `ad4/code/morphmamba/**` (103 files from the A47
  job root `jobroot_a47.tar`, sha256 `0ba35b335e39630aa291eca32f44f68d9960e0088b020348854b1036e9280ce9`; names with
  fst/valx/a12sp skipped), `ad4/src/ad4_score.py`, `ad4/hf/a12/*`, the training and evaluation images, the seven
  manifests, `ad4/build_info.json`, `ad4/SHA256SUMS`.
- Key code hashes inside the pack: `train.py` `cbb2cbd1…`, `common.py` `b5d42a99…`, `analyze.py` `6dd9220f…`,
  `a47_train.py` `3a3d04bb…`, `src/ad4_score.py` `f0cadb7a…` (`ad4/SHA256SUMS`).
- Copies:
  - T7: `/mnt/t7/smad_next/AD4/ad4_pack.tar`.
  - DGX test extraction: `/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4/` (used by `gates.py` and
    `summarise.py`; do not delete).
  - WCSS: `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AD4/ad4_pack.tar` (sha256 checked there at 14:55).
  - Machine A and machine B: `/workspace/ad4/root/smad-next/packs/AD4/ad4_pack.tar` (sha256 checked by
    `remote_setup.sh`: `ad4_pack.tar: OK` in `leaseA/setup.log` and `leaseB/setup.log`).
  - Athena: `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD4/` (lead's statement; not verified, no
    local log).

### 3.6 Task folders

- Built by `bash /home/narolski/smad-next/src/AD4/make_tasks.sh /mnt/t7/smad_next/AD4/staging/AD4`: 20 folders
  `AD4_{m3mf,m3perm,m3lmf,m3lperm}_s{401..405}`, each with `run.sh` (sha256 `5aae2ef9…` in all 20, checked 17:30),
  `task.env` (`TASK`, `RECIPE`, `ARM`, `SEED`), `est_minutes` (75 for M3, 180 for M3L).
- Upload tar: `/mnt/t7/smad_next/AD4/staging_AD4.tar`, 184,320 bytes, sha256
  `88c86e93318107b969dc47794cb0f3eb0015bc62fd4dba801592786f6c2d3e0f`.
- Where they are (last check of each place):
  - WCSS, 16:07 (owner [584]): the ten ViT-B/16 tasks in `/lustre/pd03/hpc-narolski-1790461090/smad-next/staging/AD4/`,
    the ten ViT-L/14 tasks in `/lustre/pd03/hpc-narolski-1790461090/smad-next/queue/ready/`. Not re-checked
    (WCSS unreachable).
  - Machine A: the five `AD4_m3mf_*` in `/workspace/ad4/tasks/`; machine B: the five `AD4_m3perm_*`.
  - Athena: the ten ViT-L/14 tasks in `/net/pr2/projects/plgrid/plggrestoration/smad-next/tasks/` (lead's
    statement; not verified).

### 3.7 Outputs produced so far

| Path | What | Size / hash |
|---|---|---|
| `/mnt/t7/smad_next/AD4/zero_step/m3/` | untrained ViT-B/16: `scores_eval.npz`, `scores_train.npz`, `metrics.json` | `scores_eval.npz` sha256 `a846fbdf5c3f44e338609716dfdf8b7dea53cbcf54cebe54084a47a549853d4b`; `scores_train.npz` `c92b0065f5f41700e8e4a2a5b7de1ce96c49661078cf996e4dfc52b4de5e62bb` |
| `/home/narolski/smad-next/experiments/AD4/zero_step/metrics_m3.json` | copy of the M3 `metrics.json` | 5,333 bytes |
| `/mnt/t7/smad_next/AD4/zero_step/m3l/scores_eval.npz` | untrained ViT-L/14, evaluation scores only (17:13) | 3,808,056 bytes; not read |
| `/mnt/t7/smad_next/AD4/equiv/` | A47 I-3 seed-1 `last.pt` (345,130,460 bytes, sha256 `f9e391c4d1c3b17c0df544ee92568e985e5a92b529159e5e3d36442f4b86e40b`), `meta.json`, scorer output `out/` | `out/metrics.json` also holds this network's corrected MAD22 cells; not read or reported |
| `/mnt/t7/smad_next/AD4/test/` | DGX test logs, mock root, result tars of the 3-step and 2-step tests | result tars sha256 `aec95203…` (M3), `6a5744d6…` (M3L) |
| `/mnt/t7/smad_next/AD4/vast/` | four lease folders (section 7 and 10) | |
| `/mnt/t7/smad_next/AD4/results_vast/` | rented results arrive here | empty at 17:43 |
| `/home/narolski/smad-next/experiments/AD4/ad4_cells_m3.csv`, `ad4_train_m3.csv`, `ad4_gates_m3.json` | first reader output (untrained network only; gates empty) | |

Dropped items: none beyond the unused variants listed in 3.3. No training row was dropped.

---

## 4. Code

All in `/home/narolski/smad-next/src/AD4/` unless stated. Hashes read 17:30 (sha256, first 8 hex).

| Script | Job | Arguments used | sha256 |
|---|---|---|---|
| `build_pack.py` | Builds the single pack from registered inputs only (byte copies, each hash-checked). Reads the A47 job root from a scratchpad path (see section 9). | `--out /mnt/t7/smad_next/AD4/ad4_pack.tar --work /mnt/t7/smad_next/AD4/build/weights` | `5c296a3e` |
| `ad4_score.py` | Scores one network (a `train.py` run, or `--zero-step`) on `ad4_eval.csv` with TTA and on its training manifest without TTA; writes `scores_eval.npz`, `scores_train.npz`, `metrics.json`, `last_trainable.pt` (LoRA and head only), `last_pt.sha256`. Core identical to `smadcvpr/score.py` (`ImageItems`, bilinear resize of the whole image, no crop, mean of two sigmoids). | inside `run.sh`; zero-step: `--zero-step --recipe m3|m3l --seed 401 --workers 6 --bs 64` | `f0cadb7a` |
| `run.sh` | One task = train one network with `train.py`, score it, write one result tar plus `.sha256` to `$ROOT/smad-next/results/AD4/`. Idempotent ("already done" if a matching tar exists). WCSS: apptainer with the SIF and two library packs; `AD4_LOCAL=1`: host Python. | env `TASK_DIR`, `TASK_WORK`; test knobs `AD4_LOCAL`, `AD4_PY`, `AD4_ROOT`, `AD4_STEPS`, `AD4_LIMIT`, `AD4_WORKERS` (default 7) | `5aae2ef9` |
| `make_tasks.sh` | Writes the 20 task folders. | destination folder | `4b714eff` |
| `gates.py` | `order`: CPU prediction of the first 200 batch compositions (generalises the reviewer's `order_check2.py`), compared with a network's `meta.json` if given. `equiv`: AUC and Kendall tau per shared cell between two score files. Depends on the DGX test extraction. | `order --arch … --seed … --manifest … [--meta …]`; `equiv --ours … --ref … --out …` | `cfba77c4` |
| `summarise.py` | The reader of Amendment 1: refuses bad networks, recomputes EER (`analyze.eer`) and AUC (`analyze.auc`) per cell, writes `ad4_cells_<recipe>.csv`, `ad4_train_<recipe>.csv`, `ad4_gates_<recipe>.json`, with `--reading` the fixed reading `ad4_reading_<recipe>.json`. | `--results DIR --recipe m3|m3l [--order] [--reading]` | `33269760` |
| `vast_api.py` | Minimal Vast client (balance, search, instances, show, create, destroy). The API key is read from a file [stored outside the repository] and never printed. Image constant `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` (it was `2.7.1-cuda12.8` until about 16:00; reviewer finding 2). | main session only | `48834f58` |
| `vast/lead_lease.sh` | Lead-side driver per machine: rents the first available offer, starts the watchdog, waits up to 780 s (13 min) for SSH, runs setup, a 200-step smoke test, then the queue. | `NAME CAP CREDIT_BASELINE "TASKS" OFFER...` (section 11) | `2732db57` |
| `vast/launch_remote.sh` | Upload pack, scripts and tasks; `setup`, `smoke` (two-GPU form, not used for A/B), `queue N`. Log folder from `AD4_LEASE_DIR`. | `HOST PORT setup|smoke|queue N` | `11c90b47` |
| `vast/remote_setup.sh` | On the rented machine: checks the pack sha256, installs timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3 with torch and torchvision held at the image's versions, records versions, asserts timm 1.0.27. | none | `0d3139a3` |
| `vast/remote_queue.sh` | One worker per GPU, claims tasks by atomic `mkdir`, runs `run.sh` as a WCSS slot would, records `rc/`, samples GPU memory every 20 s, writes `ALL_DONE`. | `NGPU` (1 on A and B) | `15342f02` |
| `vast/watchdog.py` | DGX-side, every 60 s: reads instance and account credit, pulls results to `results_vast/` and logs to `<lease>/remote/`, verifies sha256, tries to copy verified tars to WCSS, destroys the instance at the cap, at the deadline, or when the queue is done and every finished task is verified on the DGX. | `--config <lease>/lease.json` | `fa47a6a2` |
| `vast/make_lease.py` | Writes a lease config for a machine rented by hand (cap 9.6 USD, 8 h). Apparently used for no machine: every lease config carries fields it does not write (`offer_id`, `gpu` or `image`). | | `0ff422b1` |
| `/home/narolski/smad-next/src/athena/env_and_smoke.sbatch` | Athena job: builds the shared venv (torch 2.2.1+cu121, torchvision 0.17.1, timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3, pillow 10.2.0) and runs a smoke test of `AD4_m3lmf_s401` (default 40 steps, 8 images), prints `PEAK_MIB`. | | |
| `/home/narolski/smad-next/src/athena/ad4_vitl_array.sbatch` | Athena array 0-9 over the ten ViT-L/14 tasks, one A100, 8 CPUs, 64 GB, 10 h, `-C localfs`, `AD4_LOCAL=1`, `AD4_ROOT=/net/pr2/projects/plgrid/plggrestoration`. Account hard-coded `plgrestorearc-gpu-a100`. | | |
| `/home/narolski/smad-next/src/athena/wait_and_submit_smoke.sh` | Lead's watcher: every 20 min asks Slurm with `--test-only` whether an account is accepted, then submits `env_and_smoke.sbatch` once. Stops on a failed connection without retrying. | `9 1200` | |
| `/home/narolski/smad-next/src/wcss/slot.sh` | Generic WCSS GPU slot (6 h or 14 h) that runs tasks from `queue/ready/` if `est_minutes` fits. | | |

**Training call** (from `run.sh`; `train.py` is called directly, `a47_train.py` is a pass-through without
`--acq-aug`):
`train.py --arch {a12_clip_vitb16_madation | a12_clip_vitl14_madation} --regime d0 --split train90 --lofo none --lr 3.33e-06 --seed S --res 224 --workers 7 --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250 --ft=lora --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw --wd=0.05 --head-lr=3.33e-05 {--bs=256 | --bs=32 --accum=8} --aug=flip --sched=const --clip-grad=5 --pos-weight=1`.
Trainable parameters: 74,241 (ViT-B/16), 197,377 (ViT-L/14) (DGX test logs).

**Run order.** `build_pack.py` → `make_tasks.sh` → DGX test with `run.sh` → upload → `ad4_score.py --zero-step` per
recipe → (rented) `lead_lease.sh` → `launch_remote.sh setup` → smoke → `remote_queue.sh` under `watchdog.py` →
`summarise.py` with `--order --reading`.

**Environments.**
- DGX: `/home/narolski/mambamorph-code/.venv-spark/bin/python`, Python 3.12.3, torch 2.12.1+cu130, timm 1.0.27,
  numpy 1.26.4, Pillow 12.2.0, scipy 1.17.1, safetensors 0.8.0 (test logs; versions printed 17:40).
- Machines A and B (identical): image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, Python 3.10.13, torch 2.2.1
  (CUDA 12.1), torchvision 0.17.1, Pillow 10.2.0 (image's own), installed timm 1.0.27, huggingface_hub 0.36.2,
  safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3, hf-xet 1.8.0 (`leaseA/remote/logs/pip.log`, same install line on B;
  `versions.txt`). Drivers: A 535.154.05, B 580.178.04. CPUs: A 64, B 128 (`gpus.txt`, `nproc.txt`).
- WCSS container (not used yet for AD4): `/lustre/software-data/container-images/pytorch_latest.sif`, torch 2.2.1,
  CUDA 12.1, Python 3.10.13 (from WCSS job logs [512]) plus `pylib.tar` and `pylib_a12.tar` (timm 1.0.27).
- Athena: shared venv `/net/pr2/projects/plgrid/plggrestoration/smad-next/venv`, to be built by
  `env_and_smoke.sbatch` (not built yet).

**Seeds.** 401 to 405 for every arm and recipe; permutation seed `2026111100 + seed`; untrained network seed 401.

---

## 5. Results

No trained network of this experiment has been scored yet. Intervals: the registration asks for a 95% bootstrap over
FRLL persons at read time; none has been computed (the reader does not implement it, section 9). The numbers below
are point values.

### 5.1 Untrained ViT-B/16 network (seed 401, scored on the DGX at 15:15)

Source: `/home/narolski/smad-next/experiments/AD4/ad4_cells_m3.csv` (EER recomputed by `summarise.py` with
`analyze.eer`), raw scores `/mnt/t7/smad_next/AD4/zero_step/m3/`. 204 genuine images in each cell.

| Cell | Morphs | Native EER % | Native AUC | E7 EER % | E7 AUC | E7 note |
|---|---|---|---|---|---|---|
| MorDIFF | 1,000 | 53.86 | 0.4361 | 48.02 | 0.5512 | |
| DiM-A | 500 | 50.00 | 0.4925 | 45.05 | 0.5687 | |
| DiM-C | 500 | 48.02 | 0.5182 | 43.17 | 0.5953 | |
| Fast-DiM | 500 | 49.01 | 0.5081 | 44.16 | 0.5826 | |
| Fast-DiM-ODE | 499 | 52.03 | 0.4616 | 46.09 | 0.5367 | |
| Greedy-DiM | 500 | 55.84 | 0.4055 | 50.00 | 0.4836 | |
| Greedy-DiM-S | 500 | 53.42 | 0.4457 | 47.03 | 0.5226 | |
| FRLL AMSL | 2,175 | 37.34 | 0.6561 | 35.30 | 0.6848 | |
| FRLL FaceMorpher | 1,222 | 33.40 | 0.7085 | 32.38 | 0.7247 | |
| FRLL OpenCV | 1,221 | 34.76 | 0.6805 | 33.33 | 0.7002 | |
| FRLL Webmorph | 1,221 | 32.84 | 0.7225 | 30.39 | 0.7478 | |
| FRLL StyleGAN | 1,222 | 46.57 | 0.5534 | 46.57 | 0.5534 | E7 not applicable |
| Corrected MAD22 FaceMorpher | 1,000 | 44.60 | 0.5792 | 39.21 | 0.6588 | |
| Corrected MAD22 OpenCV | 984 | 49.95 | 0.4918 | 49.45 | 0.4952 | E7 partial (108/204 identical) |
| Corrected MAD22 Webmorph | 500 | 41.19 | 0.6204 | 40.74 | 0.6241 | E7 partial (104/204 identical) |
| Corrected MAD22 MIPGAN-I | 1,000 | 56.39 | 0.3996 | 56.39 | 0.3996 | E7 not applicable |
| Corrected MAD22 MIPGAN-II | 999 | 54.43 | 0.4418 | 54.43 | 0.4418 | E7 not applicable |

Training set, true labels, threshold 0.5, no TTA, 50,000 images: accuracy 0.2953, AUC 0.2270 (the random head ranks
copies below natives) (`ad4_train_m3.csv`; `zero_step/metrics_m3.json`). Scoring took 453.8 s (evaluation) and
1,023.9 s (training set) on the shared GB10.

### 5.2 Untrained ViT-L/14 network

Running (section 10). Evaluation scores exist since 17:13; no metrics yet; nothing was read.

### 5.3 Scorer-equivalence data (A47 I-3, ViT-B/16 morph-free network, seed 1, last checkpoint)

`ad4_score.py` on the DGX against the registered `scores_eval_last.npz`
(`/mnt/t7/smad_heldout/a47/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3/`).
File: `/home/narolski/smad-next/experiments/AD4/gate_scorer_equivalence.json`. 24 shared cells; corrected MAD22 is
not in the registered file.

| Cell | AUC ours | AUC registered | abs. diff | Kendall tau | EER ours % | EER registered % |
|---|---|---|---|---|---|---|
| DiM-A native | 1.00000 | 1.00000 | 0.00000 | 0.99853 | 0.000 | 0.000 |
| DiM-A E7 | 0.67189 | 0.67303 | 0.00114 | 0.99774 | 38.763 | 38.763 |
| DiM-C native | 1.00000 | 1.00000 | 0.00000 | 0.99878 | 0.000 | 0.000 |
| DiM-C E7 | 0.80964 | 0.81000 | 0.00036 | 0.99843 | 26.980 | 26.880 |
| Fast-DiM native | 0.99954 | 0.99954 | 0.00000 | 0.99836 | 0.990 | 0.990 |
| Fast-DiM E7 | 0.53439 | 0.53506 | 0.00067 | 0.99765 | 49.010 | 49.010 |
| Fast-DiM-ODE native | 0.99893 | 0.99893 | 0.00000 | 0.99809 | 1.437 | 1.437 |
| Fast-DiM-ODE E7 | 0.43470 | 0.43583 | 0.00113 | 0.99729 | 53.469 | 53.469 |
| Greedy-DiM native | 0.99982 | 0.99983 | 0.00001 | 0.99845 | 0.545 | 0.545 |
| Greedy-DiM E7 | 0.65308 | 0.65279 | 0.00028 | 0.99778 | 39.753 | 39.753 |
| Greedy-DiM-S native | 0.99723 | 0.99722 | 0.00001 | 0.99842 | 1.435 | 1.435 |
| Greedy-DiM-S E7 | 0.45320 | 0.45306 | 0.00014 | 0.99784 | 53.316 | 53.316 |
| FRLL AMSL native | 1.00000 | 1.00000 | 0.00000 | 0.99690 | 0.000 | 0.000 |
| FRLL AMSL E7 | 0.99881 | 0.99881 | 0.00000 | 0.99691 | 0.973 | 0.973 |
| FRLL FaceMorpher native | 0.99651 | 0.99653 | 0.00002 | 0.99767 | 1.472 | 1.472 |
| FRLL FaceMorpher E7 | 0.98851 | 0.98861 | 0.00010 | 0.99766 | 4.456 | 4.456 |
| FRLL OpenCV native | 0.84769 | 0.84731 | 0.00038 | 0.99632 | 22.945 | 23.027 |
| FRLL OpenCV E7 | 0.63215 | 0.63193 | 0.00022 | 0.99622 | 43.149 | 43.231 |
| FRLL StyleGAN native | 0.69872 | 0.69854 | 0.00018 | 0.99655 | 38.226 | 38.226 |
| FRLL StyleGAN E7 | 0.69872 | 0.69854 | 0.00018 | 0.99655 | 38.226 | 38.226 |
| FRLL Webmorph native | 1.00000 | 1.00000 | 0.00000 | 0.99703 | 0.000 | 0.000 |
| FRLL Webmorph E7 | 0.99944 | 0.99944 | 0.00000 | 0.99706 | 0.941 | 0.941 |
| MorDIFF native | 1.00000 | 1.00000 | 0.00000 | 0.99900 | 0.000 | 0.000 |
| MorDIFF E7 | 0.95743 | 0.95744 | 0.00000 | 0.99891 | 11.782 | 11.782 |

Largest |AUC difference| 0.00114 (DiM-A E7); smallest Kendall tau 0.99622 (FRLL OpenCV E7); largest EER difference
0.10 points (DiM-C E7). Scoring took 1,436 s on the shared GB10 (`/mnt/t7/smad_next/AD4/equiv/score.log`; training
scoring limited to an 8-row manifest `equiv_train8.csv`).

### 5.4 Reference numbers of the original morph-free experiment (A47 I-3, ViT-B/16, 3 seeds)

Context for the reproduction gate, from `/home/narolski/mambamorph-code/smadcvpr/results/A47/a47_read.md` lines 84
to 100 (native EER %, per seed in the file's order). The first value of each row equals seed 1's last-checkpoint EER
in 5.3, so the rows are last-checkpoint values. The old-MAD22 rows of that file are not comparable with corrected
MAD22 and are omitted.

| Cell | Mean | Per seed | Gate bound for the AD4 seed mean |
|---|---|---|---|
| MorDIFF | 0.00 | 0.00, 0.00, 0.00 | at most 3.0 |
| DiM-A | 0.15 | 0.00, 0.45, 0.00 | at most 3.0 |
| DiM-C | 0.00 | 0.00, 0.00, 0.00 | at most 3.0 |
| Fast-DiM | 0.48 | 0.99, 0.45, 0.00 | at most 3.0 |
| Fast-DiM-ODE | 1.17 | 1.44, 1.09, 0.99 | at most 3.0 |
| Greedy-DiM | 0.22 | 0.55, 0.10, 0.00 | at most 3.0 |
| Greedy-DiM-S | 0.63 | 1.44, 0.45, 0.00 | at most 3.0 |
| FRLL FaceMorpher | 2.62 | 1.47, 4.91, 1.47 | at most 5.6 |
| FRLL Webmorph | 0.65 | 0.00, 0.49, 1.47 | at most 5.6 |
| FRLL AMSL | 0.82 | 0.00, 0.50, 1.97 | at most 5.6 |
| FRLL OpenCV | 18.66 | 23.03, 21.19, 11.78 | 8.8 to 26.0 |
| FRLL StyleGAN | 27.47 | 38.23, 19.62, 24.57 | none |

### 5.5 Speed and memory (training of ViT-B/16 at batch 256)

| Where | Card | Speed (it/s) | Peak GPU memory (nvidia-smi) | Source |
|---|---|---|---|---|
| DGX test, 3 steps | GB10 (shared) | not measured | not measured | `test/AD4_m3mf_s401.stdout.log` |
| Machine A smoke, 200 steps | A100-SXM4-40GB | 1.83 (step 100), 1.90 (step 200) | 30,839 MiB | `leaseA/smoke.txt` |
| Machine A, `AD4_m3mf_s401` | A100-SXM4-40GB | 1.84 rising to 1.99 | 30,839 MiB | `leaseA/remote/logs/AD4_m3mf_s401.log`, `gpumem.csv` |
| Machine B smoke, 200 steps | RTX 6000 Ada (48 GB) | 1.43 | 30,842 MiB | `leaseB/smoke.txt` |
| Machine B, `AD4_m3perm_s401` | RTX 6000 Ada | 1.39 to 1.40 | 30,842 MiB | `leaseB/remote/logs/AD4_m3perm_s401.log`, `gpumem.csv` |
| A47 I-3 seed 1 (WCSS) | H100 | about 3.3 (6,250 steps in 0.520 h) | not recorded | `/mnt/t7/smad_next/AD4/equiv/meta.json` |

First full network: `train_hours` 0.872 on machine A; "AD4 trained (3288 s)" counted from task start, including
114 s of pack copy, check and unpacking. Pack copy, check and unpacking took 114 s on A, 99 s on B, 190 s and 169 s on
the DGX. Pack upload from the DGX: 476 s to A, 564 s to B (`launch.log`).

---

## 6. Checks

### 6.1 What was verified

- **Recipe.** The ViT-B/16 call is flag for flag the registered A47 I-3 row (`A47_train.tsv` `18c4db56…`, equal to
  `A12_BR_T1.tsv` `cba30bd6…`) minus `--es-snaps=10`; the ViT-L/14 call is the `A12_BR_T2.tsv` (`7e968a00…`) row
  minus `--es-snaps=10` with `--bs=32 --accum=8`. Dropping the snapshots leaves `last.pt` unchanged (`es_steps(6250,10)[-1]`
  is 6250; snapshots are scored after training) (reviewer, check 1).
- **Pack integrity.** Pack sha256 checked on WCSS, on A and on B, and by every `run.sh` before unpacking;
  `SHA256SUMS` checked after unpacking.
- **DGX end-to-end tests** (section 2): both recipes, rc 0, result tar copied and hash-checked; re-run is idempotent.
- **Permutations.** Regenerated by the reviewer; class balance 25,000/25,000; true labels kept by path in
  `scores_train.npz` (`label_true`).
- **Scorer.** Code reading (reviewer) and the scorer-equivalence gate (5.3): pass, tolerance |AUC difference| ≤
  0.005 and Kendall tau ≥ 0.99 per cell.
- **Sample order.** `gates.py order` reproduces all 200 recorded batch compositions of A47 seed 1 (WCSS, torch
  2.2.1, x86) on the DGX (torch 2.12.1, ARM): first three `[[129,127,0],[133,123,0],[133,123,0]]`. For seed 401 it
  predicts `[[139,117,0],[125,131,0],[124,132,0]]`, which equals the DGX 3-step test's record and the reviewer's
  expectation ([686]-[687]).
- **Rebuild from saved weights.** On the DGX smoke network, `build_run_model(meta)` plus pack weights plus
  `last_trainable.pt` reproduce `last.pt`: 203 tensors, 0 differ (reviewer's `rebuild_check.py`, reviewer [174]).
  `result.md` still lists this as not tested; it was checked by the reviewer.
- **EER on tied scores.** `common.eer` (used in `metrics.json`) gives 69.7% or 30.4% on constant scores depending on
  row order; `analyze.eer` gives 50%. Without ties they agree. Hence read-time `analyze.eer` (Amendment 1 (b)).
- **Memory.** Reviewer's CPU probe: 1,540 / 2,536 / 3,664 MB at batch 4 / 12 / 20, so 125 to 141 MB per image and 32
  to 36 GB at batch 256. Measured later on A and B: 30,839 and 30,842 MiB (includes the CUDA context).
- **Rented software.** Both machines: identical image and pins, versions recorded and timm asserted (section 4).
- **Training manifests on the rented machines.** `train_i3.csv` sha256 `0273c11b…` on A and `train_perm_s401.csv`
  `c0dfdb26…` on B, as registered (task logs).

### 6.2 What was not verified

- The WCSS container path (apptainer, SIF, library packs) was never run for this experiment.
- The Athena path: venv not built, no smoke test, M3L speed and peak memory on A100 40 GB unknown (reviewer's
  scaling guess about 16 GB at batch 32; not measured). Upload of pack and tasks to Athena: lead's statement only.
- Tensor equality of our converted CLIP weights with A47's (sizes differ by 168 bytes, 3.4).
- That the untrained network equals `train.py`'s step-0 state (true by construction of the same seeding and build
  order; not checked bitwise).
- That the sample-order predictor is right for ViT-L/14 (`gates.py` uses batch 32 for M3L; checked only on the
  2-step DGX test's first micro-batches, not against a full record).
- Inference equivalence on the rented cards (the reviewer's "inference gate": score the untrained network on A or B
  and compare with `a846fbdf…`). Not run; not registered.
- Cause of the 0.39 USD jump in account credit at 16:58.
- Location (country) of machines A and B: not in the lease files.
- WCSS state after 16:07 and Athena state at any time (no access from this documentation task).
- The 15:15 read of the untrained network preceded the first commit of the registration (disclosed in Amendment 1 (f)).

### 6.3 Where sources disagree

- **Lease 2 price.** Amendment 1 (a) and the lead's message [639] say 0.962 USD/h;
  `lease2_2xPRO5000_unreachable/lease.json` says 0.9933 USD/h. 0.962 is lease 1's price (`lease1_2x4090_aborted/lease.json`).
- **Lease 1.** `NOTEBOOK.md` ("Lease: 2x RTX 4090, 0.73 USD per hour") and `result.md` ("Chosen offer: 58777466 …
  China, 0.73 USD/h") give the offer that was refused; the machine actually rented was offer 35743571 in Sweden at
  0.962 USD/h (`lease1_2x4090_aborted/lease.json`, and `result.md`'s later section). Why the lead switched offers is
  not recorded in the sources read.
- **Lease 2 price in NOTEBOOK.md** "0.96 USD per hour" against 0.9933 in `lease.json`.
- **Machine B card.** `NOTEBOOK.md` ("two single-A100 machines") against `leaseB/driver.log` and Amendment 1b (RTX
  6000 Ada Generation, 48 GB).
- **Reason lease 1 was given up.** The lead's summary says batch 256 "needs about 31 GB"; at 16:13 the evidence was
  the reviewer's estimate of 32 to 36 GB (`lease1_2x4090_aborted/README.txt`). The 30.8 GB figure was measured only
  later, on machine A.
- **Ten-minute rule.** `lead_lease.sh` comments say 10 minutes; the code waits 780 s (13 minutes), and lease B's
  first machine was destroyed after 13 minutes (Amendment 1b says so too). Lease 2's README says SSH was refused "for
  7 minutes" after it reported running at 16:21; it was created at 16:14.
- **Watchdog deadline.** `watchdog.py` and `make_lease.py` say 8 hours; `lead_lease.sh` writes 9 hours into the
  configs of machines A and B (deadlines 12 Nov 01:30:46 and 01:44:15).
- **Watchdog destroy condition.** Its docstring says results must be copied back "to the DGX and to WCSS"; the code
  requires only the DGX copy before destroying.
- **NOTEBOOK.md log times.** Entries dated 18:15 to 12 Nov 00:20 describe events that the lease files and transcripts
  place between about 15:37 and 17:30 on 11 Nov (for example "20:30: first rented machine destroyed"; the files say
  about 16:13). This README uses the file and log times.
- **Untrained M3L finish.** `result.md` expected about 17:30; at 17:43 the training-set scoring was still running.
- **Lease 2 upload.** The lead's message of 16:18 said setup was uploading; the lease folder has no upload log and the
  owner saw no transfer process at 16:24 (section 7, item 4).
- **`result.md` section "opened by the main session"** names instance 60223497 and `vast/lease.json` with watchdog PID
  1952064; that machine was destroyed at about 16:13 and its files moved to `vast/lease1_2x4090_aborted/`.

---

## 7. Dead ends and failures

1. **Owner could not rent (15:43 and 16:06).** The instance-creation call for offer 58777466 (2x RTX 4090, China,
   0.73 USD/h, reliability 0.997; fallbacks Quebec 58852161 at 0.94 and Slovakia 50305477 at 1.07 USD/h) was refused
   twice by the permission system ("real-world transactions"), the second time after the author's approval had been
   relayed by the lead. Nothing was rented. The author then ruled that rental commands run in the main session only
   ([543]-[581]). At that time `vast_api.py` still used the torch 2.7.1 image; the owner flagged it [580].
2. **WCSS queue moves.** The ten ViT-B/16 tasks were moved `ready/` → `staging/AD4` at 15:41, back at 15:44 (after the
   refusal), and out again at 16:07. None had been claimed (owner checks of `claimed/`, `done/`, `failed/`).
3. **Lease 1 aborted (about 16:08 to 16:13).** Instance 60223497, 2x RTX 4090 24 GB, Sweden, 0.962 USD/h. Destroyed
   before any task ran because the registered batch of 256 was estimated at 32 to 36 GB; 0.11 USD
   (`/mnt/t7/smad_next/AD4/vast/lease1_2x4090_aborted/`; last poll 0.102 USD credit drop). The batch was never changed
   (Amendment 1b: replace the card, never the batch).
4. **Lease 2 unreachable (16:14 to about 16:28).** Instance 60224295, 2x RTX PRO 5000 72 GB, California, 0.993 USD/h,
   image torch 2.7.1-cuda12.8 (these cards need it). Reported "running" from 16:21 but every watchdog poll failed to
   reach it (ssh exit 255; one rsync exit 12) on the proxy `ssh3.vast.ai:16990` and the direct port. No upload is
   recorded: the folder has no `launch.log` or `setup.log`, and at 16:24 the owner saw no ssh or rsync process to
   the machine [706]-[710], although the lead's message of 16:18 said the upload was running [639]. Destroyed under
   the ten-minute rule (`lease2_2xPRO5000_unreachable/`). The two aborted leases together: 0.27 USD (credit 111.85 →
   111.58).
5. **First machine B unreachable (16:31 to 16:44).** Instance 60226099, offer 56042632, 1.00 USD/h; card not recorded;
   never got an SSH host or port, so its watchdog only updated the budget. Destroyed at 16:44:11 after 13 minutes; no
   task ran (`leaseB/unreachable_60226099/`). Its own cost was not separated from the account total (estimate about
   0.22 USD at 1.00 USD/h for 13 minutes; not verified).
6. **Offer 59644447 not available** at 16:44:14 (`leaseB/driver.log`).
7. **The software deviation of Amendment 1 (a) was withdrawn.** Amendment 1 registered lease 2 with torch 2.7.1;
   Amendment 1b replaced it with two single-GPU machines on torch 2.2.1, the cluster's version.
8. **First untrained-M3L scoring run killed (15:35).** It ran from about 15:15 as a child of the owner's shell and had
   written nothing after 20 minutes; it was killed and restarted detached so that it would survive the agent. The
   `pkill -f "ad4_score.py --zero-step --recipe m3l"` also matched and killed the owner's own shell (exit 144); the
   restart was issued again [428]-[439]. About 20 minutes of shared-GPU work were lost.
9. **Bugs found and fixed before any real run.**
   - `run.sh`: `py -I ad4_score.py` would have dropped the `PYTHONPATH` that carries the library packs in the
     container; changed to `py ad4_score.py` [241].
   - `launch_remote.sh` smoke step: background PIDs were not captured and `wait` could fail the step; fixed with
     `P1=$!`, `P2=$!` and `wait … || true` [593]-[597].
   - `remote_setup.sh`: installing timm could have upgraded torch; torch and torchvision are now held at the image's
     versions with a constraints file [597]. The lead later made it copy the version records into `logs/` (so the
     watchdog brings them back) and assert timm 1.0.27 (reviewer finding 2; [639]).
   - `vast_api.py` image constant changed from torch 2.7.1 to 2.2.1 (reviewer finding 2). Who changed it is not
     recorded.
   - `python -I -c "import vast_api"` fails (isolated mode drops the current folder from the path); calls use
     `sys.path.insert(0, '.')` [532]-[535].
10. **Risks the reviewer found that were handled by design, not code.** A smoke test with the real `AD4_ROOT` would
    leave `<TASK>.tar` and make the real task exit "already done" (`run.sh` lines 26 to 28). All rented smoke tests
    used a separate `smokeroot` and task names with a `_smoke_t200` suffix (`lead_lease.sh`).
11. **Reviewer proposals not adopted** (reviewer report, section 4; no decision recorded): inference gate on the rented
    card; untrained seeds 402 to 405 as extra references; renting for the ViT-L/14 morph-free arm instead of ViT-B/16
    (the ViT-B/16 outcome was already seen in A47); pinning Pillow (it is 10.2.0 on A, B and in the Athena pins, but
    12.2.0 on the DGX). The reviewer's data-residency question (FRLL and MAD22 face images on a host in China) became
    moot when the China offer was not rented; the countries of A and B are not recorded.
12. **Withdrawn or superseded statements.** `result.md` "Not tested: rebuilding a network from `last_trainable.pt`"
    (checked by the reviewer, 6.1). `result.md` section on instance 60223497 as the lease (superseded). Amendment 1 (a)
    (replaced by 1b). `result.md` "metrics_m3l.json … expected about 17:30" (still running at 17:43).

---

## 8. Observations and ideas

- **The untrained reference is not at chance and its sign is arbitrary.** FRLL landmark AUC 0.66 to 0.72 with one
  random head, while the same network gives AUC 0.227 on natives against copies of its own training set (5.1). The
  untrained seed-401 network is also the initial state of both seed-401 trained networks (reviewer finding 4). On
  landmark cells the registered wording is "at least 10 points below every label-free reference", never "above chance".
- **Training loss so far (not a registered outcome).** Morph-free `AD4_m3mf_s401` on A: 0.6914 at step 100 falling to
  0.0310 at step 5,900. Permuted `AD4_m3perm_s401` on B: 0.6921 at step 100, between 0.6923 and 0.6940 up to step
  3,400 (task logs). The reviewer expected that permuted training at this learning rate barely moves the head (not
  verified).
- **Speeds.** A100 40 GB 1.99 it/s, RTX 6000 Ada 1.40 it/s, H100 about 3.3 it/s for the same batch-256 step (5.5).
  Memory 30.8 GB on both rented cards, so 24 GB cards are excluded for this recipe and 40 GB suffices.
- **The ViT-L/14 falsifier is confounded with recipe strength.** The morph-trained ViT-L/14 recipe retrains (A12BR
  R × d0) are themselves above 10% EER on MorDIFF, DiM-C, Fast-DiM and Greedy-DiM ("0 eligible",
  `/home/narolski/mambamorph-code/smadcvpr/PROTOCOL.md` lines 19879 to 19880, cited by the reviewer). Amendment 1 (d)
  therefore asks to print the twin beside each cell.
- **E7 cells.** A47 saw MorDIFF E7 at 5.25%; the reviewer suggests the wording "the E7 control does not remove this
  network's cue", not "measures history only". Failing GAN cells rules out the shrink cue only.
- **Positive control on corrected MAD22 available unread.** `/mnt/t7/smad_next/AD4/equiv/out/metrics.json` holds the
  A47 seed-1 morph-free network's numbers on the corrected MAD22 cells. Nobody has read or reported them.
- **Account credit jump.** +0.39 USD between 16:57:48 and 16:58:52 (`leaseA/watchdog.jsonl`), shortly after machine
  B's pack upload. Possibly a bandwidth or storage charge (not verified). Since 17:00 the credit has fallen at about
  1.18 USD/h, matching the sum of the two hourly prices (1.171 USD/h).
- **Machine B is shared.** From about 17:31 the SMDD five-partner audit and rebuild (SM1) uses B's idle CPU cores
  (`/workspace/sm1`, `nice -n 19`; `NOTEBOOK.md` 17:35). At 17:43 B still ran at 1.40 it/s.
- **The DGX test extraction is a dependency.** `gates.py` and `summarise.py` read code, manifests and
  `build_info.json` from `/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/`. An extra file
  `data/manifests/equiv_train8.csv` was added there for the equivalence run (outside the pack's checked content).

---

## 9. Open items and next steps

In priority order. Items for the lead unless marked.

1. **Rescue files that live only in a session scratchpad** (DOCUMENTATION rule). Not done by this documentation task.
   - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/a47/jobroot_a47.tar`
     (140,728,320 bytes, sha256 `0ba35b33…`): `build_pack.py` reads it from this path; without it the pack cannot be
     rebuilt. Suggested copy: `/mnt/t7/smad_next/AD4/build/jobroot_a47.tar`, then change `A47_JOBROOT`.
   - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/ad4rev/`: the
     reviewer's `order_check2.py` (sha256 `16e8d238…`, named in Amendment 1 as the registered order predictor),
     `order_check.py` (`aadce433…`), `rebuild_check.py` (`20f568f8…`), `mem_probe.py` (`5fe1986d…`), and the A47 code
     copies. Suggested copy: `/home/narolski/smad-next/src/AD4/review/`.
2. **Re-project the rented cost** when `AD4_m3mf_s401` finishes (its log line `AD4_TASK_DONE … wall N s`), and decide
   in advance what happens if the cap would cut the fifth permuted fit (section 10).
3. **Reader gaps** (`summarise.py`):
   - the registered 95% bootstrap over FRLL persons (the `a41_read.py` two-way method) is not implemented;
   - Amendment 1 (d), the morph-trained ViT-L/14 twin beside each cell, is not implemented, and the twin scores were
     not located (WCSS logs `~/jobs/smadcvpr_a12/logs/a12-br-t2-m3l-6207420_[0-4].out` give training times only);
   - the reproduction gate exists only for M3 (as registered).
4. **Run the reading of the ViT-B/16 recipe** when all ten tars are in (section 10 commands), then the
   results-reviewer.
5. **ViT-L/14 arm.** Decide where it runs (Athena or WCSS) and remove the ten tasks from the other place before both
   can start; then Athena smoke test, array, copy-back, reading (section 10).
6. **Untrained ViT-L/14 metrics.** Check that `experiments/AD4/zero_step/metrics_m3l.json` appears (watchers) once
   scoring ends.
7. **Correct `result.md`** for the superseded statements in 6.3 and 7.12 (lead or a resumed owner).
8. **After the lease:** confirm that no instance is left, record the final spend, and close the rented arm in
   `result.md` (card, price, wall time, cost, peak memory, speed per machine).
9. **Watchdog and WCSS.** Decide whether the watchdogs should keep trying to copy verified tars to WCSS while WCSS
   refuses our address (section 10, risk 3).

---

## 10. Handover state (read 17:36 to 17:43 CET, 11 Nov)

### 10.1 Running now

| Where | What | Process / id | Log | Expected end |
|---|---|---|---|---|
| Vast machine A | five morph-free ViT-B/16 fits `AD4_m3mf_s401..405`, one after another | instance 60226054, `root@192.165.134.28 -p 12386`, remote queue `/workspace/ad4/queue.log`, task logs `/workspace/ad4/logs/`, results `/workspace/ad4/root/smad-next/results/AD4/` | DGX copies: `/mnt/t7/smad_next/AD4/vast/leaseA/remote/` | 22:05 to 23:20 (scoring time per network unknown: 10 to 25 min assumed) |
| Vast machine B | five permuted ViT-B/16 fits `AD4_m3perm_s401..405` | instance 60227348, `root@89.221.67.144 -p 17736`, same remote paths | `/mnt/t7/smad_next/AD4/vast/leaseB/remote/` | 12 Nov 00:10 to 01:25 |
| DGX | watchdog of A | PID 1978388 (`watchdog.py --config /mnt/t7/smad_next/AD4/vast/leaseA/lease.json`) | `leaseA/watchdog.jsonl`, `leaseA/LIVE_BUDGET.json` | exits after the machine is gone (`TERMINATED.json`) |
| DGX | watchdog of B | PID 2041051 | `leaseB/watchdog.jsonl`, `leaseB/LIVE_BUDGET.json` | same |
| DGX | lead drivers still waiting on a hung `ssh` of the `queue` step (harmless; the queues run) | `lead_lease.sh` PIDs 1978309, 1978387 (A), 1978726, 2041050 (B); `launch_remote.sh … queue 1` PIDs 2042153, 2062480 and their `ssh` 2042157, 2062484 | `leaseA/driver.log`, `leaseB/driver.log` (no "QUEUE STARTED" line because the ssh never returned) | killing them should not affect the remote queue (started with `setsid nohup`; not tested) |
| DGX | untrained ViT-L/14 scoring | PID 1872565 (+ 6 loader workers) | output `/mnt/t7/smad_next/AD4/zero_step/m3l/`; log `/mnt/t7/smad_next/AD4/zero_step_m3l.log` (empty until the final line) | evaluation done 17:13; training set (50,000 images) running; end not estimated reliably (shared GPU, load average 114) |
| DGX | two watchers that copy `metrics_m3l.json` to `experiments/AD4/zero_step/` | PIDs 1856530, 1873227 | none | when the scorer prints `AD4_SCORE_DONE` |
| DGX | Athena account watcher (lead) | PID 2085779 `wait_and_submit_smoke.sh 9 1200` | its stdout | up to 9 tries 20 minutes apart from about 17:29, so until about 20:10 at most |
| Machine B (not AD4) | CPU work of the SMDD five-partner audit and rebuild (SM1) | `/workspace/sm1` | SM1's records | killed when the AD4 watchdog destroys B |

State at 17:43: A had finished training `AD4_m3mf_s401` (`train_hours` 0.872) and was scoring it; B was at step 3,400
of 6,250 of `AD4_m3perm_s401` at 1.40 it/s. `results_vast/` empty. Account credit drop since the 111.58 USD baseline:
1.887 USD (`leaseB/watchdog.jsonl`, 17:42:57).

**Destroy rules** (`watchdog.py`, configs in `leaseA/lease.json`, `leaseB/lease.json`): cap 9.4 USD on the drop in
account credit from 111.58 USD (global: both watchdogs see the same number, so both machines go at the cap);
deadline A 12 Nov 01:30:46, B 12 Nov 01:44:15; or the remote `ALL_DONE` file plus every task with rc 0 verified in
`results_vast/`. Before destroying, a last pull is made. 9.4 USD from the baseline plus the 0.27 USD of the aborted
leases stays under the author's 10 USD limit for this rented run.

### 10.2 Cost projection (estimate, not measured)

Training time per network is measured (A 52.4 min, B 74.4 min at 1.99 and 1.40 it/s); scoring time on the rented
cards is not. Per-machine end times and the projected account drop from the baseline:

| Scoring time per network | A ends | B ends | Projected drop at B's end | Against the 9.4 USD cap |
|---|---|---|---|---|
| 10 min | 22:06 | 00:10 | about 8.6 USD | fits, margin about 0.8 |
| 15 min | 22:31 | 00:35 | about 9.0 USD | fits, margin about 0.35 |
| 25 min | 23:21 | 01:25 | about 10.0 USD | cap reached about 00:35, during B's fifth fit (`AD4_m3perm_s405` would be lost) |

Method: 1.887 USD at 17:43, plus 0.433 USD/h for A and 0.738 USD/h for B until each ends (observed rate since 17:00
equals the sum of the prices). Extra charges like the 16:58 jump, or another Vast instance on the same account,
reduce the margin. If the fifth permuted fit is lost, Amendment 1 (b) makes the "passable" verdict "provisional" (5 of
6 references); the prereg allows one unchanged rerun of a failed task. Any other remedy (raising the cap, running it
elsewhere) is an author or lead decision.

### 10.3 Queued and waiting

- **Ten ViT-L/14 tasks on Athena** (lead's statement, not verified): pack in
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD4/`, tasks in `.../smad-next/tasks/AD4_m3l*`. Waiting
  because Slurm accepts neither `plgrestorearc-gpu-a100` nor `plgmultivision-gpu-a100` (17:20, `ATHENA.md`).
- **The same ten tasks in the WCSS ready queue** `/lustre/pd03/hpc-narolski-1790461090/smad-next/queue/ready/`
  (state at 16:07). Any generic WCSS slot that starts will claim them (48 slots queued per `OWNER_BRIEF.md`, 108 per
  `NOTEBOOK.md` at 15:15). They must be removed from one of the two places before both can run. WCSS refuses our
  address since about 16:55 (`NOTEBOOK.md`), so this cannot be done now.
  If both ran, the outputs would land in two different results folders (Athena `.../smad-next/results/AD4/`, WCSS
  `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AD4/`) and two networks would exist per seed; which one
  counts must be fixed before any is read (one network per result, no seed picking).
- **The ten ViT-B/16 tasks in WCSS `staging/AD4`** (not in `ready/`); leave them there.

### 10.4 Commands for the remaining steps

Status (any time, read only):
```
tail -n 3 /mnt/t7/smad_next/AD4/vast/leaseA/remote/queue.log /mnt/t7/smad_next/AD4/vast/leaseB/remote/queue.log
tail -n 2 /mnt/t7/smad_next/AD4/vast/leaseA/remote/logs/AD4_m3mf_s40*.log /mnt/t7/smad_next/AD4/vast/leaseB/remote/logs/AD4_m3perm_s40*.log
cat /mnt/t7/smad_next/AD4/vast/leaseA/LIVE_BUDGET.json /mnt/t7/smad_next/AD4/vast/leaseB/LIVE_BUDGET.json
tail -n 1 /mnt/t7/smad_next/AD4/vast/leaseA/watchdog.jsonl /mnt/t7/smad_next/AD4/vast/leaseB/watchdog.jsonl
ls -la /mnt/t7/smad_next/AD4/results_vast/ /mnt/t7/smad_next/AD4/vast/leaseA/remote/rc /mnt/t7/smad_next/AD4/vast/leaseB/remote/rc
```

Check one result by hand:
```
cd /mnt/t7/smad_next/AD4/results_vast && sha256sum -c AD4_m3mf_s401.tar.sha256
```

After both machines are gone (`DESTROY_REQUESTED.json` and `TERMINATED.json` in each lease folder), main session,
because these calls use the API key [stored outside the repository]:
```
cd /home/narolski/smad-next/src/AD4 && /home/narolski/mambamorph-code/.venv-spark/bin/python -I vast_api.py instances   # expect []
cd /home/narolski/smad-next/src/AD4 && /home/narolski/mambamorph-code/.venv-spark/bin/python -I vast_api.py balance     # spend = 111.58 - credit, plus 0.27
```

Reading of the ViT-B/16 recipe (DGX CPU; the order gate takes about one minute per network):
```
cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= /home/narolski/mambamorph-code/.venv-spark/bin/python summarise.py \
  --results /mnt/t7/smad_next/AD4/results_vast --recipe m3 --order --reading
```
Writes `experiments/AD4/ad4_cells_m3.csv`, `ad4_train_m3.csv`, `ad4_gates_m3.json` (order and reproduction gates),
`ad4_reading_m3.json`. It refuses the reading with fewer than five morph-free networks and marks it "provisional"
without all five permuted networks plus the untrained one. It prints "REFUSED" for any tar failing the Amendment 1
checks.

ViT-L/14 on Athena (lead; one SSH connection per command under the lock, never repeat a failed login):
```
# 1. the watcher submits the environment build and smoke test on first acceptance; otherwise, from the DGX:
flock -w 120 /tmp/smadnext-athena.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl \
  'bash -lc "cd /net/pr2/projects/plgrid/plggrestoration/smad-next && sbatch -A <accepted account> src/athena/env_and_smoke.sbatch"'
# 2. read .../smad-next/logs/env-<job>.out: ENV_OK, SMOKE_RC=0, PEAK_MIB
# 3. remove the ten ViT-L/14 tasks from the WCSS ready queue (or decide that WCSS runs them instead), then:
flock -w 120 /tmp/smadnext-athena.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl \
  'bash -lc "cd /net/pr2/projects/plgrid/plggrestoration/smad-next && sbatch -A <accepted account> src/athena/ad4_vitl_array.sbatch"'
# 4. copy back with a hash check, then read:
flock -w 600 /tmp/smadnext-athena.lock rsync -a plgpnarolski@athena.cyfronet.pl:/net/pr2/projects/plgrid/plggrestoration/smad-next/results/AD4/ /mnt/t7/smad_next/AD4/results_athena/
cd /mnt/t7/smad_next/AD4/results_athena && for f in *.tar.sha256; do sha256sum -c "$f"; done
cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= /home/narolski/mambamorph-code/.venv-spark/bin/python summarise.py \
  --results /mnt/t7/smad_next/AD4/results_athena --recipe m3l --order --reading
```
`-A` on the command line overrides the hard-coded `#SBATCH -A plgrestorearc-gpu-a100`. `results_athena/` is a
proposed folder name; it does not exist yet. The array asks for 10 hours per task; M3L took 1.94 h per network on
H100 (A12BR), A100 speed unknown.

### 10.5 What to do if something fails

1. **A rented machine dies or disappears.** Its watchdog logs `INSTANCE_ABSENT`, writes `TERMINATED.json` and exits.
   Results already pulled stay in `results_vast/`; the network in progress is lost. Per the prereg a failed task is
   rerun once unchanged, never because of its values. Within a recipe all ten networks share image and pins
   (Amendment 1b), and the arm's card is registered (A100 for morph-free, RTX 6000 Ada for permuted); a replacement
   card is a deviation to register before its result exists. Re-rent only the unfinished tasks from the main session,
   keeping the global cap:
   ```
   cd /home/narolski/smad-next/src/AD4/vast && bash lead_lease.sh leaseA2 9.4 111.58 "AD4_m3mf_s40x ..." <offer> [<offer> ...]
   ```
   (`leaseA2` is a new folder name; the baseline 111.58 keeps the cap global.)
2. **A watchdog process dies** (for example a DGX restart) while its machine runs: nothing else will destroy the
   machine. Restart it (main session):
   ```
   cd /home/narolski/smad-next/src/AD4/vast && setsid nohup /home/narolski/mambamorph-code/.venv-spark/bin/python -I watchdog.py \
     --config /mnt/t7/smad_next/AD4/vast/leaseA/lease.json >> /mnt/t7/smad_next/AD4/vast/leaseA/watchdog.out 2>&1 < /dev/null &
   ```
   (same with `leaseB`). To pull and destroy by hand instead: the `pull()` rsync in `watchdog.py` (SSH key [stored
   outside the repository], `UserKnownHostsFile` in the lease folder), then `vast_api.py destroy 60226054` or
   `60227348`.
3. **WCSS copy attempts while WCSS refuses our address.** Once a tar is verified, each watchdog poll runs
   `flock -w 120 /tmp/opencode/wcss-client.lock rsync … narolski@ui.wcss.pl:…` per uncopied task (no connect timeout
   on that rsync), and again before destroying. Code reading suggests two effects, not observed yet: repeated
   connection attempts to a host that has blocked us, and a slower poll loop that delays the cap check and the final
   destroy by up to a few minutes per task. If this shows in `watchdog.jsonl` (long gaps between polls, `ERROR`
   entries), the lead may restart the watchdog with the WCSS copy disabled; that is a code change for the lead.
4. **A task fails on a rented machine** (`remote/rc/<task>` not 0): the queue continues with the next task; the
   failed task's work folder stays on the machine (`/workspace/ad4/work/<task>`) and its log is pulled to
   `<lease>/remote/logs/<task>.log`. Rerun once unchanged.
5. **Cap reached before B finishes:** both machines are destroyed; whatever was verified stays. See 10.2.
6. **Athena smoke fails or memory is too high:** do not change the batch (32 × 8 is registered); report to the lead.

### 10.6 Compute spent (to 17:43)

- Vast, USD: 0.27 (leases 1 and 2) + 1.887 (credit drop since the 111.58 baseline, includes the first machine B and the
  16:58 jump) = about 2.16 USD.
- Vast, GPU time billed: lease 1 about 0.17 GPU-h (2 cards, 5 min), lease 2 about 0.45 (2 cards, 14 min), first
  machine B about 0.22, machine A about 1.2, machine B about 1.0. Productive training so far: about 1.9 GPU-h.
- DGX (shared GB10, other jobs running): tests about 0.23 h, untrained M3 0.41 h, scorer equivalence 0.40 h,
  untrained M3L about 2.1 h so far plus the killed 20-minute first attempt.
- WCSS and Athena GPU: none.

---

## 11. Reproduce from scratch

DGX, in this order. `P=/home/narolski/mambamorph-code/.venv-spark/bin/python`.

1. Inputs: A47 I-3 root `/mnt/t7/smad_heldout/a47/data47/i3`; SMDD natives in
   `/home/narolski/mambamorph-code/smadcvpr_data`; corrected MAD22 in
   `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`; timm hub blobs in
   `/home/narolski/.cache/huggingface/hub`; the A47 job root `jobroot_a47.tar` (sha256 `0ba35b33…`, see section 9, item 1).
2. WCSS size listing (one connection under the WCSS lock):
   `flock -w 60 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl 'grep -P "\tdata/train/smdd/os25k_bf_t/" /lustre/pd03/hpc-narolski-1790461090/smadcvpr/packs/data_train.content' > /mnt/t7/smad_next/AD4/build/wcss_data_train_os25k.content`
3. Pack: `cd /home/narolski/smad-next/src/AD4 && $P -I build_pack.py --out /mnt/t7/smad_next/AD4/ad4_pack.tar --work /mnt/t7/smad_next/AD4/build/weights`
   (refuses to overwrite; expect sha256 `1ad170be…` if every input is unchanged; tar times are fixed).
4. Tasks: `bash /home/narolski/smad-next/src/AD4/make_tasks.sh /mnt/t7/smad_next/AD4/staging/AD4`
5. DGX test (mock root):
   ```
   B=/mnt/t7/smad_next/AD4/test; mkdir -p $B/root/smad-next/packs/AD4 $B/root/smad-next/results $B/tmp
   ln -sf /mnt/t7/smad_next/AD4/ad4_pack.tar $B/root/smad-next/packs/AD4/ad4_pack.tar
   # task folders under $B/tasks/<TASK> with run.sh and task.env, then:
   cd $B/work/task_AD4_m3mf_s401 && TMPDIR=$B/tmp TASK_DIR=$B/tasks/AD4_m3mf_s401 TASK_WORK=$PWD AD4_ROOT=$B/root AD4_LOCAL=1 \
     AD4_PY=$P AD4_STEPS=3 AD4_LIMIT=8 AD4_WORKERS=4 bash $B/tasks/AD4_m3mf_s401/run.sh
   ```
6. Untrained networks:
   ```
   B=/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401
   for r in m3 m3l; do SMAD_DATA=$B/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 $P $B/ad4/src/ad4_score.py --zero-step --recipe $r --seed 401 \
     --code $B/ad4/code --eval-manifest ad4_eval.csv --train-manifest train.csv --true-manifest train_i3.csv \
     --out /mnt/t7/smad_next/AD4/zero_step/$r --workers 6 --bs 64 > /mnt/t7/smad_next/AD4/zero_step_$r.log 2>&1; done
   ```
7. Scorer-equivalence gate: copy `last.pt` and `meta.json` of
   `/lustre/pd03/hpc-narolski-1790461090/smadcvpr/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3/`
   to `/mnt/t7/smad_next/AD4/equiv/`; write the first 9 lines of `train_i3.csv` to `$B/data/manifests/equiv_train8.csv`; then
   ```
   SMAD_DATA=$B/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 $P $B/ad4/src/ad4_score.py --run /mnt/t7/smad_next/AD4/equiv --code $B/ad4/code \
     --eval-manifest ad4_eval.csv --train-manifest equiv_train8.csv --true-manifest train_i3.csv --out /mnt/t7/smad_next/AD4/equiv/out --workers 6
   cd /home/narolski/smad-next/src/AD4 && $P gates.py equiv --ours /mnt/t7/smad_next/AD4/equiv/out/scores_eval.npz \
     --ref /mnt/t7/smad_heldout/a47/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3/scores_eval_last.npz \
     --out /home/narolski/smad-next/experiments/AD4/gate_scorer_equivalence.json
   ```
8. Order predictor check: `cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= $P gates.py order --arch a12_clip_vitb16_madation --seed 1 --manifest train_i3.csv --meta /mnt/t7/smad_heldout/a47/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3/meta.json`
9. WCSS path: upload pack and `.sha256` to `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AD4/`, the task tar to
   `.../smad-next/staging/`; the lead moves tasks to `queue/ready/`.
10. Rented path (main session; author's approval required): from `/home/narolski/smad-next/src/AD4/vast`,
    ```
    bash lead_lease.sh leaseA 9.4 111.58 "AD4_m3mf_s401 AD4_m3mf_s402 AD4_m3mf_s403 AD4_m3mf_s404 AD4_m3mf_s405" 58855597 52068706 57950807 60207967
    bash lead_lease.sh leaseB 9.4 111.58 "AD4_m3perm_s401 AD4_m3perm_s402 AD4_m3perm_s403 AD4_m3perm_s404 AD4_m3perm_s405" 56042632 59644447 55800354 59852375
    ```
    (offer ids are those used on 11 Nov; offers change; 111.58 was the credit baseline then).
11. Athena path: section 10.4.
12. Reading: section 10.4 (`summarise.py --order --reading` per recipe), then the results-reviewer.

## Addendum by the lead, 11 Nov 18:49 CET (Athena)

- 18:25: Slurm on Athena accepted the account `plgrestorearc-gpu-a100` (refused from 17:20 to 18:05; the user's
  association had not been synchronised).
- Job 3544186 (environment build and smoke test): the environment was built
  (`/net/pr2/projects/plgrid/plggrestoration/smad-next/venv`: python 3.10.4, torch 2.2.1+cu121, timm 1.0.27,
  numpy 1.26.4, pillow 10.2.0, safetensors 0.8.0), then the job FAILED copying the pack: node-local scratch
  (`-C localfs`) is only 4.0 GB (measured by job 3544200). Dead end recorded in `ATHENA.md`.
- Job files changed to the RAM disk (`-C memfs`, `--mem=120G`, work in `$MEMFS`); `run.sh` unchanged.
- Job 3544204 (smoke test again): COMPLETED in 3 min 16 s on an A100-SXM4-40GB. One ViT-L/14 task
  (`AD4_m3lmf_s401`, 40 steps, 8 scored images): pack check 33 s, training 136 s including start-up, peak GPU
  memory 14,263 MiB, peak process memory 13.3 GB, exit 0. The log prints no step rate at 40 steps; 136 s for 40
  steps bounds a full fit of 6,250 steps at 5.9 hours.
- Job array 3544219_[0-9], submitted 18:49: the ten ViT-L/14 tasks (five morph-free, five label-permuted), 10-hour
  limit each, one A100 each. Results go to `.../smad-next/results/AD4/<TASK>.tar` with `.sha256`; logs
  `.../smad-next/logs/AD4L-3544219_<n>.out`. Amendment 1c (prereg) fixes that the Athena result of each task is
  the registered one.
- To do when they end: copy the ten tars to `/mnt/t7/smad_next/AD4/results_athena/`, verify hashes, then the lead's
  reading (the reader still lacks the registered person bootstrap and the ViT-L/14 twin of Amendment 1(d)).

## Addendum by the reading owner, 11 Nov 2026 (from 22:30 CET)

New owner of the reading of the morph-free networks experiment (AD4), assigned by the lead on the author's request.

### Timeline of the reading

| Time (11 Nov) | What happened | Evidence |
|---|---|---|
| about 22:20 to 22:34 | Read the brief, documentation rules, prereg (amendments 1, 1b, 1c), this README, `result.md`, the pre-run review, `src/AD4/*.py`, `ideas/CONSOLIDATED_v3.md` section 3, the EV1 and FZ1 reviews. State: `results_vast/` holds nine tars (ViT-B/16 morph-free 401 to 405, label-permuted 401 to 404); permuted 405 started on machine B at 22:16; `results_athena/` does not exist yet. Disk `/mnt/t7`: 47 GB free. | `ls -la /mnt/t7/smad_next/AD4/results_vast/`; `leaseB/remote/queue.log` |
| about 22:34 | Located the morph-trained ViT-L/14 twin of Amendment 1 (d): `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR/a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{1..5}_r/scores_eval_last.npz` (keys and manifest hash only were read: manifest = old `eval.csv`, sha256 `86d055d3…`). | |
| about 22:36 to 22:38 | **Amendment 2** appended to `prereg.md` before any trained score was opened: bootstrap size, seed and person set (with the corrected-MAD22 file-name patterns, found because those names lack the `_orig` suffix), the twin files and matching, fixed-threshold flag and miss rates (0.5 rule and FRLL-5%), incomplete-arm rows, labels, ViT-L/14 order batch, printed checks. | `prereg.md` |
| about 22:38 to 22:41 | `src/AD4/summarise.py` rewritten (old reader sha256 `332697603508e4ca6d0c1d1f5f5f69ddc8a4fde50cd6b22ae74484f7f62d1e50`, 16:24, lacked the bootstrap, twin and rates). Two stages: `--stage gates` (refusals, order gate, reproduction gate; prints only gate outcomes) and `--stage read`. Synthetic test `src/AD4/test_summarise.py`: seeded synthetic scores on the real row structure, 40 checks (verdicts, named case, A1 wording with twin, E7 labels, landmark wording, refusal of each Amendment 1 (b) condition, incomplete arm, reproduction gate, fixed-threshold rates recomputed independently, bootstrap interval sanity, order gate pass and miss with a real seed-401 prediction): **40 of 40 pass** (27 s). Outputs `/mnt/t7/smad_next/AD4/read/synth_test/` (128 MB, synthetic only). | `OMP_NUM_THREADS=2 nice -n 10 $P test_summarise.py --order` |

**Reader frozen for the reading: `src/AD4/summarise.py` sha256 `b9213a5d1b087da31b5ca6cf765f4b5cd2012113088bf02d51edbe0165283af2`**
(test `test_summarise.py` sha256 `c19aff284e72b960d881ec445d2a457733f6514eb5dd51a581abc9935c5ad014`). Recorded 22:41 (machine clock),
before any score, metric or training accuracy of a trained AD4 network was opened.

### Gates (11 Nov, 22:41 to 22:43, reader `b9213a5d…`)

Commands: `cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10 $P summarise.py --stage gates --results /mnt/t7/smad_next/AD4/results_vast --recipe m3`
(log `/mnt/t7/smad_next/AD4/read/gates_m3_2241.log`, output `experiments/AD4/ad4_gates_m3.json`) and the same with `results_athena --recipe m3l`
(log `gates_m3l_2242.log`, `ad4_gates_m3l.json`). Order-gate predictions: `/mnt/t7/smad_next/AD4/read/order/pred_<task>.json`.

- ViT-B/16, nine tars (morph-free 401 to 405 on the A100, label-permuted 401 to 404 on the RTX 6000 Ada; torch 2.2.1): no refusal; meta seed and arch correct in all nine.
- **Sample-order gate: 9 of 9 pass** (200 of 200 rows each).
- **Reproduction gate: MISS on 1 of 11 cells, so "not reproduced on this stack".** Morph-free seed means (per seed 401 to 405), EER %, our frames:
  MorDIFF 0.00 (all 0) pass; DiM-A 0.84 (1.44, 1.88, 0.45, 0.00, 0.45) pass; DiM-C 0.00 pass; Fast-DiM 1.72 (2.87, 1.88, 0.99, 0.45, 2.43) pass;
  **Fast-DiM-ODE 4.01 (8.72, 1.88, 3.96, 0.10, 5.40), bound 3.0, MISS**; Greedy-DiM 2.43 (11.24, 0.00, 0.45, 0.00, 0.45) pass;
  Greedy-DiM-S 1.01 (2.97, 0.10, 0.45, 0.10, 1.44) pass; FRLL FaceMorpher 4.11 (12.26, 3.92, 2.45, 0.49, 1.43) pass (bound 5.6);
  FRLL Webmorph 0.99 pass; FRLL AMSL 1.10 pass; FRLL OpenCV 19.71 (40.20, 23.52, 11.74, 7.85, 15.21) pass (bound 8.8 to 26.0).
  By the prereg, the WCSS cluster tasks would then decide (the ten ViT-B/16 tasks re-queued on WCSS); that is for the lead.
- Scorer-equivalence gate: pass (11 Nov 16:46, unchanged).
- ViT-L/14: `AD4_m3lmf_s402` (Athena task 1, COMPLETED 22:38, 3 h 43 min; `train_hours` 3.58, A100-SXM4-40GB, torch 2.2.1+cu121) copied to
  `/mnt/t7/smad_next/AD4/results_athena/` with `flock -w 1800 /tmp/smadnext-athena.lock rsync`; `sha256sum -c` OK (tar sha256 `30cc8414…`).
  Sample-order gate pass (200 of 200, micro-batch 32: first rows [[15,17,0],[13,19,0],[14,18,0]]). The other nine tasks were RUNNING at 22:41 (elapsed 2:34 to 3:47).

### Lead's ruling on the reproduction gate (11 Nov, about 22:50) and the reader change it needs

- State (lead): the registration is applied as written. Every number of the rented ViT-B/16 arm carries the flag "not reproduced on this stack
  (1 of 11 cells: Fast-DiM-ODE native, seed mean 4.01% against a bound of 3.0, seeds 0.10 to 8.72)". The registered remedy, the WCSS cluster
  tasks, cannot run tonight because WCSS refuses all connections. The ten ViT-B/16 tasks are still in the WCSS ready queue from this afternoon,
  so they run when WCSS reopens, and by the registered rule they then decide. This is the state, not a deviation chosen after the numbers. Until
  then the rented arm is read as registered for a flagged arm: descriptive, with the flag, the missed cell's per-seed values printed beside
  its bound, no seed dropped or reweighted.
- Reader change, presentation only (no number, rule or verdict changes): the flag with the missed cells' seed means, bounds and per-seed values
  is printed at the top of `ad4_reading_<recipe>.md` and under every table, stored as `reproduction_flag` in the reading json, and given as a
  column `reproduction_gate` in `ad4_cells_<recipe>.csv` for every trained network. Two synthetic checks added; **42 of 42 pass**.
- **Reader used for the readings: `summarise.py` sha256 `8fd182b49aa75268d44b5c220dd6d7a8c745cf99cdab1d58d5c3574357e3056b`**
  (test `8f8f0a67124471d5f9a435c1e01d13ba3cc6b0ef9f48be4bcce8794e97d66078`). This supersedes `b9213a5d…`, which ran the gates; the gate code
  is unchanged. No score was opened by the reader between the two versions beyond the gate cells listed above.

### ViT-L/14 progress, 22:56 (Athena job logs `.../smad-next/logs/AD4L-3544219_<n>.out`)

| Task | Network | Node | Elapsed | Step | Rate (it/s) | Projection |
|---|---|---|---|---|---|---|
| 0 | `AD4_m3lmf_s401` | t0017 | 4:01 | 6100 | 0.43 | ends about 23:08 |
| 1 | `AD4_m3lmf_s402` | | 3:43 | done | | COMPLETED 22:38, copied, gate pass |
| 2 | `AD4_m3lmf_s403` | t0020 | 3:57 | 1200 | 0.11 | about 13 h of training left: exceeds the 10 h limit |
| 3 | `AD4_m3lmf_s404` | t0014 | 3:42 | 800 | 0.09 (0.23 at step 700) | about 17 h left: exceeds the limit |
| 4 | `AD4_m3lmf_s405` | t0020 | 3:33 | 500 | 0.05 | about 32 h left: exceeds the limit |
| 5 to 9 | `AD4_m3lperm_s401..405` | t0019, t0021, t0013 | 2:49 to 3:04 | 4800 to 5300 | 0.46 to 0.49 | end about 23:35 to 23:50 |

Reported to the lead at 22:57: at these rates the ViT-L/14 morph-free arm ends with 2 of 5 networks unless tasks 2 to 4 are rerun (the prereg
allows one unchanged rerun of a failed task); cancelling or resubmitting is the lead's decision. Nodes t0020 and t0014 are slow for this job.

### Rerun of three ViT-L/14 morph-free tasks (lead, 11 Nov 22:56)

- **What:** the lead cancelled Athena tasks 3544219_2, _3 and _4 (`AD4_m3lmf_s403`, `_s404`, `_s405`) and resubmitted them unchanged as
  job array **3546123_[2-4]**: same job file `src/athena/ad4_vitl_array.sbatch` and `run.sh`, account `plgmultivision-gpu-a100`, 6-hour limit,
  `--exclude` of nodes t0010, t0014 and t0020. Pending on priority at 22:56; about 3 h 45 min each after start at the healthy rate.
- **Why (infrastructure, not values):** at 22:56 the three tasks ran at 0.11 it/s (t0020, step 1200 after 3:57), 0.09 it/s (t0014, step 800
  after 3:42, 0.23 it/s at step 700) and 0.05 it/s (t0020, step 500 after 3:33), against 0.43 to 0.49 it/s on the other nodes. None could finish
  inside its 10-hour limit (projections 13, 17 and 32 hours). The three tasks had written no result (`run.sh` writes the tar only at the end),
  so no value of these networks existed or was seen.
- **Rule applied:** the prereg's "a failed task is rerun once unchanged; never rerun because of its values". This is that one rerun for each
  of the three seeds. A further failure of any of them leaves the arm incomplete.
- **Slow nodes for this job (add to the `ATHENA.md` note on t0010):** t0020 (two tasks, 0.05 and 0.11 it/s) and t0014 (0.09 it/s), against
  0.43 to 0.49 it/s elsewhere for the same ViT-L/14 batch.
- **Reading state:** until all five morph-free networks are back, the ViT-L/14 morph-free arm is read only as "incomplete (k of 5)"
  (Amendment 2 (d)). Watched: arrays 3544219 (tasks 0 and 5 to 9) and 3546123 (tasks 2 to 4).

### Reading of the ViT-B/16 recipe (11 Nov, 23:36 to about 23:45; reader `8fd182b4…`)

Command: `cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10 $P summarise.py --stage read --results /mnt/t7/smad_next/AD4/results_vast --recipe m3`
(log `/mnt/t7/smad_next/AD4/read/read_m3.log`). `AD4_m3perm_s405` arrived and was verified at 23:36. All ten tars plus the untrained network; no refusal;
sample-order gate 10 of 10 pass; bootstrap 10,000 replicates over 102 persons, seed [20261111, 4].
**Full tables: `experiments/AD4/ad4_reading_m3.md`** (EER, AUC, both fixed thresholds, training accuracy); per network and cell:
`ad4_cells_m3.csv`; reading `ad4_reading_m3.json`; training `ad4_train_m3.csv`. Our frames throughout.
Status printed by the reader: "final" (all six references present), with the reproduction flag on top and under every table, so the arm is
read descriptively until the WCSS tasks decide (lead's ruling above).

Headline rows (EER %, morph-free seed mean [95% person-bootstrap interval of the mean]; references = five label-permuted plus the untrained):
- MorDIFF native (primary): 0.0 [0.0, 0.0], all five seeds 0.0; references 37.3 to 60.8 (untrained 53.9); passable yes (5/5 seeds); A1 not falsified.
- Six DiM natives (secondary): DiM-A 0.8, DiM-C 0.0, Fast-DiM 1.7, Fast-DiM-ODE 4.0, Greedy-DiM 2.4, Greedy-DiM-S 1.0; lowest reference 37.2 to 43.1;
  all passable yes (5/5 seeds), A1 not falsified on any.
- E7 (history-matched) cells: MorDIFF 2.9; DiM-C 21.7; DiM-A 63.4, Fast-DiM 60.5, Fast-DiM-ODE 75.9 (AUC 0.33, 0.37, 0.18: morphs ranked below the
  history-matched photos); Greedy-DiM 49.9, Greedy-DiM-S 46.5 (per seed 4.4 to 94.6 and 19.5 to 73.0).
- FRLL natives: AMSL 1.1, FaceMorpher 4.1, Webmorph 1.0 (each at least 10 points below every label-free reference; lowest 24.0 to 27.4);
  OpenCV 19.7 (not passable, lowest reference 26.5); StyleGAN 32.9.
- Corrected MAD22 natives: FaceMorpher 0.0 (E7 0.1); OpenCV 34.3; Webmorph 27.2 (passable by the margin rule, above 15% in 5 seeds);
  MIPGAN-I 76.4 and MIPGAN-II 75.1 (AUC 0.18 and 0.19).
- 0.5 rule: morph-free networks flag 0.0% of unprocessed genuine photos and miss 64.5% of MorDIFF (per seed 4.1 to 98.4), 86 to 100% of DiM
  morphs, 100% of every FRLL family, 4.3% of corrected MAD22 FaceMorpher.
- FRLL-5%: misses 0.0 to 4.1% on MorDIFF and DiM natives, but the history-matched genuine photos are flagged 100% in every MorDIFF, DiM and
  corrected MAD22 FaceMorpher E7 cell; FRLL landmark E7 flag rates 26 to 45%.
- Training accuracy: morph-free 1.000 on their labels; label-permuted 0.512 to 0.520 on their own labels and 0.399 to 0.686 on the true labels;
  untrained 0.295.

### Independent review of the ViT-B/16 reading, post hoc addendum and result.md rewrite (11 Nov, 23:40 to 23:55)

- Review: `/home/narolski/smad-next/experiments/reviews/REVIEW_AD4_VITB_20261111.md` (needs qualification; the history-matching conclusion is
  partly wrong). The lead asked for (1) the reviewer's readings, registered and run with the registered bootstrap, (2) result.md rewritten
  with the corrected wording, (3) follow-ups H-new-1 to H-new-5 registered before scoring, (4) the same corrections in the ViT-L/14 reading.
- 23:44: **Amendment 3** (post hoc, descriptive) appended to `prereg.md` before running: floor logits, own-genuine flag rate at FRLL-5% with
  miss rates, file-size null per cell, seed-spread rule (wide = EER range above 30 points; reversed = all AUC below 0.5; split = one AUC
  below 0.4 and one above 0.6; no seed mean for reversed or split), label-permuted accuracies; wording rules.
- `src/AD4/posthoc_m3.py` (sha256 `595af89b…`; uses `summarise.py` unchanged) run:
  `cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10 $P posthoc_m3.py --results /mnt/t7/smad_next/AD4/results_vast --recipe m3`
  (log `/mnt/t7/smad_next/AD4/read/posthoc_m3.log`). Outputs `experiments/AD4/posthoc_m3.md` (`c8f62471…`) and `posthoc_m3.json` (`5df95a81…`).
  Main numbers (our frames): training natives at logit -3.67 to -3.63 and copies at +3.60 to +3.65 (medians, morph-free); FRLL-5% threshold
  p = 0.027 to 0.036; MorDIFF's own unprocessed genuine photos flagged at FRLL-5%: 50.7% [47.5, 53.7] (per seed 1.0, 70.1, 54.9, 87.7, 39.7)
  with 0.0% of MorDIFF morphs missed; file-size null on native cells AUC 0.72 (Greedy-DiM) to 1.000 (MAD22 FaceMorpher), MorDIFF 0.999;
  on history-matched cells 0.04 (Greedy-DiM) to 0.99 (FRLL FaceMorpher); reversed cells: DiM-A E7, Fast-DiM-ODE E7, MIPGAN-I, MIPGAN-II;
  split cells: Greedy-DiM E7, Greedy-DiM-S E7, FRLL OpenCV E7; wide: FRLL OpenCV native.
- result.md rewritten (copy of the earlier version: `/mnt/t7/smad_next/AD4/read/result_md_before_rewrite_20261111T2350.md`): new top sections
  with the corrected wording, a "Withdrawn" list with reasons, the earlier record kept below, the superseded 23:36 reading text quoted.

### Follow-ups of the review (Amendment 4, registered 23:50; post hoc follow-ups)

- Face region fixed in the canonical frame of `prep_eval.py` (eyes at (190, 210) and (322, 210)): ellipse centre (256, 264), semi-axes
  125 x 172 px; face box x 166 to 345, y 160 to 379. No detector.
- **(a) H-new-1 and H-new-2, DGX CPU, done 23:55.** `src/AD4/fu_sharpness.py` (8-image test first, then
  `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10 $P fu_sharpness.py`; log `/mnt/t7/smad_next/AD4/read/fu_sharpness_m3.log`;
  per-image measures `/mnt/t7/smad_next/AD4/read/fu_sharpness.npz`). Tables `experiments/AD4/fu_sharpness_m3.md`, `fu_sharpness_m3.json`.
  Our frames:
  - S = minus the high-frequency power share in the face box. Native cells: S alone separates morphs from genuine photos at AUC 0.998 to
    1.000 in the 8 qualifying cells (network AUC at least 0.99 in all seeds: MorDIFF, DiM-A, DiM-C, Fast-DiM, Greedy-DiM-S, FRLL AMSL,
    FRLL Webmorph, corrected MAD22 FaceMorpher); median Spearman (network score, S) at least 0.7 in 4 of the 8 (DiM-A, DiM-C, Fast-DiM,
    Greedy-DiM-S), 0.39 to 0.67 in the other 4. **H-new-1: mixed** by the registered rule.
  - **H-new-2: Spearman 0.86 over the 7 diffusion history-matched cells, "consistent with overshoot"**: x (AUC of S, morphs against the
    history-matched photos) MorDIFF 0.910, DiM-A 0.087, DiM-C 0.493, Fast-DiM 0.213, Fast-DiM-ODE 0.023, Greedy-DiM 0.448, Greedy-DiM-S
    0.665; y (median network AUC) 0.996, 0.342, 0.846, 0.404, 0.104, 0.294, 0.594.
- **(b) H-new-3 and (c) H-new-4, H-new-5, Athena.** `src/AD4/fu_rescore.py` (blank and score), `src/AD4/fu_pack.py` (staging folder of
  symlinks plus the eleven networks' `meta.json` and `last_trainable.pt` from the verified tars), job file `src/athena/ad4_fu.sbatch`
  (shared venv, the environment AD4 used on Athena, per the `ATHENA.md` rule that an experiment keeps its environment; account
  `plgmultivision-gpu-a100`, `--exclude=t0010,t0014,t0020`, 2 h limit).
  - Extra pool rows (`fu_extra.csv`, sha256 `e00835e6…`): landmark ladder frgcferet R0 536, R2w 1,072, R3 1,072, R4 1,072 (both tools);
    SMDD evaluation genuine renders 1,000 (sample seed 2026111104); StyleGAN3 single-identity renders (H3) 423; StyleGAN v1 renders (H4b) 338.
  - DGX 8-image test 23:53 (`/mnt/t7/smad_next/AD4/fu/dgxtest/`): blanking changes exactly the 194,585 pixels outside the ellipse of a test
    image; the rebuilt network `AD4_m3mf_s403` reproduces its registered scores within 0.0004 (DGX CPU against A100) on 8 rows.
  - Pack streamed to Athena without a local tar (`tar -chf - | tee >(sha256sum) | ssh … cat >`): `.../smad-next/packs/AD4/fu_pack.tar`,
    1,680,128,000 bytes, sha256 `ee117981…`, checked on Athena.
  - 23:55: smoke job **3546199** submitted (`FU_LIMIT=8`, 30 min limit).

### ViT-L/14 recipe: copy-back, gates and the descriptive "incomplete (2 of 5)" reading (11 Nov 23:56 to 23:59)

- Copied with hash check to `/mnt/t7/smad_next/AD4/results_athena/`: morph-free 401, 402; label-permuted 401 to 405 (tasks 0, 1, 5 to 9 of
  array 3544219, COMPLETED; 3 h 38 min to 4 h 13 min each; `train_hours` 3.53 to 4.07; all A100-SXM4-40GB, torch 2.2.1+cu121).
  Morph-free 403 to 405: rerun array 3546123_[2-4] PENDING at 23:56.
- Gates (`gates_m3l_2357.log`, `ad4_gates_m3l.json`): no refusal, meta seed and arch correct, **sample-order gate 7 of 7 pass** (200/200,
  micro-batch 32). No reproduction gate is registered for ViT-L/14.
- Descriptive reading of the incomplete arm, reader `8fd182b4…` unchanged, and `posthoc_m3.py --recipe m3l` (Amendment 3 readings applied
  to this recipe, as the lead asked that the review's corrections carry over). Logs `read_m3l_incomplete2.log`, `posthoc_m3l_incomplete2.log`;
  tables `experiments/AD4/ad4_reading_m3l.md`, `posthoc_m3l.md`; copies of this state `/mnt/t7/smad_next/AD4/read/incomplete2_*`.
  Every verdict column reads "incomplete (2 of 5)". Our frames, in our preprocessing:
  - Floor: training natives at logit -4.07 to -4.06, copies +4.02 (medians); FRLL-5% threshold p 0.019.
  - MorDIFF native: 0.0 and 0.0%; references 41.2 to 52.0% (untrained 50.0); morph-trained twin (A12BR M3L R x d0, seeds 1 to 5, old
    manifest, same files) 48.7% (34.8 to 56.9). MorDIFF history-matched 2.0 and 8.9%.
  - DiM natives 0.0 to 6.9% per seed (means 0.5 to 3.5); twin 10.2 to 29.7%. DiM history-matched cells reversed in both seeds
    (AUC 0.02 to 0.27).
  - FRLL AMSL 0.0 and 7.3%, Webmorph 0.0 and 4.0%, FaceMorpher 5.0 and 35.8% (wide), OpenCV 18.6 and 45.6%, StyleGAN reversed;
    twin 0.1 to 1.1% on the landmark cells. Corrected MAD22 FaceMorpher 0.0% native, 44.6 and 55.4% history-matched; MIPGAN-I and -II
    reversed; OpenCV 45.8, Webmorph 37.7 (no twin on corrected MAD22).
  - 0.5 rule: 0.0% genuine flagged; misses 12.7 and 98.9% (MorDIFF), 99.8 to 100% (DiM and FRLL). FRLL-5%: MorDIFF morphs missed 0.0%
    while 25.5% of MorDIFF's own unprocessed genuine photos are flagged (39.2, 11.8).
  - Label-permuted networks: own-label accuracy 0.514 to 0.519; true-label accuracy 0.357 to 0.683.

### Handover state, 12 Nov 00:01 (reading owner)

| Where | What | Id | Expected | If it fails |
|---|---|---|---|---|
| Athena | ViT-L/14 morph-free reruns, seeds 403 to 405 (lead) | array 3546123_[2-4], PENDING (priority 2143) | about 3 h 45 min each after start | the prereg's one rerun is used; a second failure leaves the arm "incomplete (k of 5)" |
| Athena | follow-up smoke job, 8 images per manifest | 3546199, PENDING (priority 2007) | about 10 min after start | read `.../smad-next/logs/AD4FU-3546199.out`; fix, re-test on 8 images on the DGX, resubmit |
| Athena | follow-up production job | not yet submitted | after the smoke passes: `sbatch src/athena/ad4_fu.sbatch` from `.../smad-next` (FU_LIMIT unset) | as above |
| DGX | watcher of 3546199 (one ssh per 10 min) | background task of the reading owner | ends when 3546199 ends | none |

Next steps: when the three reruns are back, copy with hash check, `summarise.py --stage gates` then `--stage read` and `posthoc_m3.py`
for `m3l` (the 23:59 interim copies stay in `/mnt/t7/smad_next/AD4/read/incomplete2_*`). When the production follow-up tar is back
(`.../smad-next/results/AD4_fu/fu_<job>_limit0.tar`): copy, check the unblanked-score gate, then read H-new-3, H-new-4 and H-new-5 (reader
for these still to be written; registered rules in Amendment 4). Compute so far for follow-ups: none on GPU.

### Follow-ups (b) and (c) moved to the DGX (lead, 12 Nov about 00:00; Amendment 4b registered 00:02)

- Athena priority collapsed (fair-share 0.045 / 0.020); the lead moved (b) and (c) to the idle DGX GPU. Smoke job 3546199 cancelled
  (`scancel` 00:02, before it started). The ViT-L/14 reruns 3546123_[2-4] stay on Athena (Amendment 1c); the lead moved them to the
  better account.
- Blanking is applied in memory before the unchanged `ImageItems.load` step (subclass `BlankItems` in `fu_rescore.py`); no image is
  written. Test: in-memory blanking and the PNG-blanked test images give identical scores (largest difference 0.0, 8 rows, GB10).
- Scorer `src/AD4/fu_rescore.py` sha256 `e0ab24b5…`. Reader `src/AD4/fu_read.py` sha256 `3e86a8c0…`, tested before any production score
  on a synthetic result folder (`/mnt/t7/smad_next/AD4/fu/readtest/`): unblanked = registered scores gives gate pass with |dAUC| 0.0000;
  "blanked" = registered scores reproduces the ViT-B/16 reading table exactly (MorDIFF E7 2.9 [1.8, 4.2]); planted ladder gaps recovered
  (OpenCV 0.218, FaceMorpher 0.001, "mixed").
- 00:02: full pass started on the DGX: PID 2828502 (`setsid nohup`, nice 10, 2 threads, 4 loader workers), 11 networks (morph-free first),
  manifests `ad4_eval.csv`, `ad4_eval.csv:blank`, `fu_extra.csv`; data root `/mnt/t7/smad_next/AD4/fu/dgx/data` (symlinks only);
  scores `/mnt/t7/smad_next/AD4/fu/dgx/out/<network>/scores_*.npz`; log `/mnt/t7/smad_next/AD4/fu/dgx/score.log`. Expected about 15 to 20
  min per network on the GB10 (estimate from the untrained network's 454 s per 19,827 images), so about 3 to 3.5 h in all.
  If it dies: rerun the same command with `--nets` pointing at a folder of symlinks to the networks without a finished `scores_fu_extra.npz`.

### Follow-ups (b) and (c): results of the DGX pass (12 Nov 00:02 to 01:03; reader 01:03 to 01:10)

- Scoring done 01:02 (11 networks, 314 to 364 s each on the GB10; `fu/dgx/score.log`). Disk after: 34 GB free (score files only).
- **Unblanked-score gate: MISS for 3 of the 5 morph-free networks** (seeds 401, 404, 405: Kendall tau 0.988, 0.987, 0.989 against the
  registered 0.99; largest |AUC difference| 0.0009, 0.0012, 0.0008, inside the 0.005 tolerance). Seeds 402 and 403 pass (tau 0.991, 0.992);
  the five label-permuted networks and the untrained network pass (tau ≥ 0.999). By Amendment 4 a network that misses is reported and
  not read, so every follow-up row of the morph-free arm is "incomplete (2 of 5)". The DGX (GB10, torch 2.12.1) and the rented cards
  (A100, torch 2.2.1) differ in the order of near-tied scores of the saturated morph-free networks; not investigated further.
- **Reader fix after the first run (01:05), disclosed:** with fewer than five networks the first version printed verdicts (H-new-4
  "falsified" although both readable seeds were below the FRLL median; H-new-3 and H-new-5 a verdict on two seeds). Amendment 2 (d)
  makes such rows "incomplete (k of 5)"; the reader now prints that. `fu_read.py` sha256 `cea617cb…` (first version `3e86a8c0…`); no
  rule or number changed. Logs `read/fu_read.log` (first), `read/fu_read2.log`.
- Results, our frames (H-new-3) and the ladder's own frames (H-new-5), seeds 402 and 403 only; files `fu_blank_m3.md`, `fu_pools_m3.md`:
  - H-new-3 (border blanked, both classes): MorDIFF history-matched 2.9 and 13.2% (mean 8.1 [5.3, 10.8]); MorDIFF native 0.0; DiM
    natives 0.0 to 9.8; corrected MAD22 FaceMorpher native 0.0, history-matched 0.5 and 5.9; FRLL AMSL / FaceMorpher / OpenCV / Webmorph
    natives 3.2 / 6.1 / 11.2 / 8.3. References (blanked) 31.9 to 56.3%.
  - H-new-5: gap AUC(R4 vs R0) − AUC(R3 vs R0) OpenCV 0.009 [-0.008, 0.023], FaceMorpher -0.006 [-0.029, 0.015]; R4 vs R3 AUC 0.47 to 0.52;
    R3 vs R0 0.84 to 0.91.
  - H-new-4: SMDD evaluation renders sit 0.03 and 0.05 logits below the FRLL genuine median (both readable seeds); StyleGAN3 renders
    (H3) 0.91 and 1.85 above; StyleGAN v1 renders (H4b, 112 px native) 7.1 above (near the copy class).

### Handover state, 12 Nov 01:07 (supersedes the 00:01 table)

| Where | What | Id | Expected | If it fails |
|---|---|---|---|---|
| Athena | ViT-L/14 morph-free reruns, seeds 403 to 405 | array 3546123_[2-4], PENDING (priority 2215, no start forecast) | about 3 h 45 min each after start | the one registered rerun is used; the arm stays "incomplete (k of 5)" |
| DGX | watcher `src/AD4/watch_m3l.sh 14` (one ssh per 15 min; copies each finished tar with hash check to `results_athena/`) | background task of the reading owner | exits when all three are verified, on a bad task state, on a login problem (never retried), or after 14 h | log `/mnt/t7/smad_next/AD4/read/watch_m3l.log` |
| none | follow-ups (b), (c) | done on the DGX | | |

When all five ViT-L/14 morph-free tars are in: `summarise.py --stage gates`, then `--stage read`, then `posthoc_m3.py --recipe m3l`
(commands as for ViT-B/16 with `--results /mnt/t7/smad_next/AD4/results_athena --recipe m3l`), then update result.md with the review's
wording rules. Compute for the follow-ups: DGX GB10 about 1 h (11 networks x about 5.3 min); Athena none (smoke job cancelled unstarted).

### Review of follow-ups (b), (c) and the bounded head (12 Nov; review `experiments/reviews/REVIEW_PN1_TIER1_20261112.md`, Subject 2, commit 64863c6)

Applied on the lead's instruction:
- `fu_blank_m3.md` and `fu_blank_m3.json`: platform "Athena, NVIDIA GB10" corrected to "DGX, NVIDIA GB10, blanked (Amendment 4b)" (8
  occurrences each, edited in place; numbers unchanged); `src/AD4/fu_read.py` now writes that label.
- H-new-4: worded "indistinguishable: both at the trained floor" (the -0.03 and -0.05 logit differences lie inside a floor whose 5th to
  95th percentile spans about 0.03, with no interval); added to `fu_pools_m3.md` and result.md. Its printed status stays "incomplete (2 of 5)".
- Unblanked-score gate misses (tau 0.987 to 0.989): noted as probably ties at the saturation floor; not rescued (`fu_pools_m3.md`, result.md).
- H-new-5 stands as written.
- Bounded head, measured on the AD4 tensors (`last_trainable.pt`, key `head.cls`; features L2-normalised in `archs_a12.py` line 277):
  ViT-B/16 morph-free ||w|| 3.721 / 3.747 / 3.740 / 3.758 / 3.739, bias -0.035 / 0.013 / -0.020 / 0.004 / 0.008; label-permuted ||w||
  0.609 to 0.649; ViT-L/14 morph-free 401 and 402 ||w|| 4.155 and 4.156. Logits are bounded by ||w|| + |b|, so the training floor
  (-3.65 for ViT-B/16, -4.07 for ViT-L/14) is near the bound, and every FRLL-5% reading of AD4 reads a band about 0.03 logits wide.
  Paragraph added to result.md ("What the networks are").

### Handover state, 12 Nov 15:18 (reading owner hands back)

- The watcher `src/AD4/watch_m3l.sh 14` ended after 14 h (01:05 to 15:02) with array **3546123_[2-4] still PENDING** (never started;
  log `/mnt/t7/smad_next/AD4/read/watch_m3l.log`). No watcher runs now. The ViT-L/14 morph-free arm stays "incomplete (2 of 5)".
- To finish when the three reruns are back: copy `AD4_m3lmf_s40{3,4,5}.tar` + `.sha256` from `.../smad-next/results/AD4/` with
  `flock -w 1800 /tmp/smadnext-athena.lock rsync` and `sha256sum -c`; then in `/home/narolski/smad-next/src/AD4`:
  `summarise.py --stage gates --results /mnt/t7/smad_next/AD4/results_athena --recipe m3l`, then `--stage read`, then
  `posthoc_m3.py --results /mnt/t7/smad_next/AD4/results_athena --recipe m3l` (all with `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10`,
  Python `/home/narolski/mambamorph-code/.venv-spark/bin/python`); write result.md with the review's wording rules (Amendment 3) and the
  bounded-head caveat. Readers are frozen: `summarise.py` `8fd182b4…`, `posthoc_m3.py` `595af89b…`.
- Open for the lead: the ViT-B/16 reproduction flag (WCSS cluster tasks, queued); the three morph-free ViT-B/16 networks that missed the
  DGX unblanked-score gate in the follow-ups (rerun on an A100, or leave "incomplete (2 of 5)").
- Nothing of this owner runs on any machine. Compute of the reading owner: DGX CPU readings; DGX GB10 about 1 h (follow-up scoring);
  Athena 0 GPU-h (smoke job 3546199 cancelled before it started).

## Resumed by the reading owner, 12 Nov from 23:00 (WCSS reachable again)

| Time | What | Evidence |
|---|---|---|
| 23:00 | Lead: WCSS reachable since about 23:00; finish the ViT-L/14 seeds 403 to 405 and the ViT-B/16 cluster rerun on WCSS. Local pack `/mnt/t7/smad_next/AD4/ad4_pack.tar` still present, sha256 `1ad170be…` OK; reader working copy re-extracted to `/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/` (pack `SHA256SUMS` OK; `data/` symlinks as `run.sh` makes them). | |
| 23:01 | WCSS listing: pack, library packs, the ten ViT-B/16 task folders in `staging/AD4` (`run.sh` sha256 `5aae2ef9…` in all ten) and **all ten ViT-L/14 result tars** in `results/AD4/`, written 12 Nov 12:50 to 15:54 by the generic queue slots (`queue/done/` lists the ten tasks; `task_info.txt`: `local 0`, pack `1ad170be…`, steps 6250, limit 0, wall about 7,200 s, nodes r18-*). All ten `.sha256` OK on WCSS. No score opened. | ssh listing |
| 23:02 | **Amendment 5** registered and committed (082f945, 23:03:05; corrected 13 Nov: ba88926 is an SM1 commit), before any WCSS result was opened: WCSS results are the registered networks for ViT-L/14 morph-free seeds 403 to 405; the other seven WCSS ViT-L/14 results are cross-platform repeats; the WCSS ViT-B/16 ten-network rerun is the registered ViT-B/16 arm whatever its outcome; H100 gates before reading. | `prereg.md` |
| 23:03 | Ten WCSS ViT-L/14 tars copied to `/mnt/t7/smad_next/AD4/results_wcss/` (rsync under the WCSS lock), all ten `sha256sum -c` OK. Athena array 3546123_[2-4] cancelled (never started). Registered ViT-L/14 folder `/mnt/t7/smad_next/AD4/results_m3l_registered/` (symlinks: Athena morph-free 401, 402 and label-permuted 401 to 405; WCSS morph-free 403 to 405). | |
| 23:14, 23:18 | First two `sbatch` attempts of the smoke + equivalence job failed: "Unable to contact slurm controller (connect failure)" (ssh login fine). Nothing submitted. Retry every 15 min. | |
| 23:20 | Sample-order gate: **20 of 20 pass** (registered ViT-L/14 arm and the ten WCSS repeats); no refusal; meta seed and arch correct; cards: Athena A100-SXM4-40GB, WCSS H100. Files `ad4_gates_m3l.json` (registered arm), `ad4_gates_m3l_results_m3l_registered.json`, `ad4_gates_m3l_results_wcss.json`; logs `read/gates_m3l_results_*.log`. | |

Job files (on WCSS in `/lustre/pd03/hpc-narolski-1790461090/smad-next/jobs_ad4/`, copies in `src/wcss/`), both carry their full workload,
`--extra=FORCE_RM_TMPDIR`, IO in `$TMPDIR`:
- `ad4_smoke_equiv.sbatch` (1 H100, 1 h limit): `run.sh` of `AD4_m3mf_s401` with 50 steps and 8 scored images into `smad-next/smoke_AD4/root`
  (never read), then the H100 scorer-equivalence gate: A47 I-3 seed-1 `last.pt` re-scored with `ad4_score.py` in the container; tar to
  `smad-next/results/AD4_equiv/`.
- `ad4_vitb_array.sbatch` (array 0-9%5, 2 h 30 min limit): the ten ViT-B/16 tasks through the unchanged `run.sh`; results to `smad-next/results/AD4/`.
| 23:36 | Third attempt failed the same way; retry loop every 15 min (one ssh each). | |
| 23:57 | **Job 6308825 submitted** (smoke + H100 equivalence; owner: AD4 reading owner). Slurm forecast start 13 Nov 14:00, end 15:00 (forecast assumes full limits; 20 nodes powered down, 139 jobs pending in lem-gpu-short). | `squeue` |
| 23:59 | **Job 6308830_[0-9%5] submitted** (the ten ViT-B/16 tasks; owner: AD4 reading owner), `--dependency=afterok:6308825` so the smoke passes first. Expected: starts when 6308825 ends OK (forecast about 13 Nov 15:00); each task about 45 to 75 min on an H100 (A47 I-3 trained in 0.52 h; scoring and pack copy about 15 to 20 min); two waves of five, so about 2.5 h after start: end about 13 Nov 17:30 (estimate from the A47 H100 train time, to be replaced by the step rate of the first task log). | `squeue` |

Check plan (no polling loop): at the 6308825 forecast start plus 40 min (13 Nov about 14:40), read
`/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ad4-smoke-equiv-6308825.out`; if `AD4 equiv done`, copy
`results/AD4_equiv/equiv_h100_6308825.tar` + `.sha256` and run `gates.py equiv` against the registered A47 `scores_eval_last.npz`;
then compute the array's ETA from the first task's step rate and check at that time. If 6308825 fails, 6308830 stays pending on its
dependency (DependencyNeverSatisfied): fix, re-test, resubmit both, and cancel 6308830.

### Cluster-stack readings (13 Nov 08:28 to 08:45)

- 6308825 (smoke + H100 equivalence) and 6308830_0 to _9 (ten ViT-B/16 tasks) COMPLETED on WCSS (lead: 03:44 to 06:46, about 33 min each;
  smoke done 03:02, equivalence 03:02:30, 19,827 images scored in 21 s). Fetched with rsync under the WCSS lock to
  `/mnt/t7/smad_next/AD4/results_wcss_m3/` (10 tars, all `sha256sum -c` OK), `/mnt/t7/smad_next/AD4/equiv_h100/` (tar OK) and the job
  logs to `/mnt/t7/smad_next/AD4/wcss_logs/`. The originals stay on WCSS (second copy); nothing on the cluster side was touched.
- H100 scorer-equivalence gate (`gates.py equiv` against the registered A47 `scores_eval_last.npz`): pass, 24 cells, |dAUC| 0.0, tau 1.0
  (`gate_scorer_equivalence_h100.json`).
- ViT-B/16 cluster arm (registered, Amendment 5 (b)): no refusal; sample-order 10/10; **reproduction gate pass, 11/11** (Fast-DiM-ODE
  2.69 against 3.0). Reading with the frozen reader `8fd182b4…`: `ad4_reading_m3.md`, `ad4_cells_m3.csv`, `ad4_train_m3.csv`,
  `ad4_gates_m3.json`, `posthoc_m3.md` (logs `read/gates_m3_wcss.log`, `read_m3_wcss.log`, `posthoc_m3_wcss.log`). The rented-arm files of
  11 Nov were kept as `*_rented.*` before the reader overwrote the standard names. Cross-platform repeat: `src/AD4/xplat.py` (new, per
  network and cell EER and AUC differences) → `xplat_m3_wcss_vs_rented.md`.
- ViT-L/14: all-WCSS repeat read first and renamed `*_m3l_wcssrepeat.*`; then the registered arm
  (`/mnt/t7/smad_next/AD4/results_m3l_registered/`) read under the standard names `ad4_reading_m3l.*`, `posthoc_m3l.*`;
  `xplat_m3l_wcss_vs_athena.md`. Logs `read/read_m3l_wcssrepeat.log`, `read_m3l_registered.log`, `posthoc_m3l_registered.log`.
- Headline numbers are in `result.md` (rewritten top; previous version `/mnt/t7/smad_next/AD4/read/result_md_before_cluster_20261113.md`).
  Registered outcome in words: on both recipes MorDIFF native is 0.0% in every seed and passable; all six DiM natives are passable for
  ViT-B/16; for ViT-L/14 five are passable and Fast-DiM-ODE falsifies A1 (11.8%, above 15% in 3 of 5 seeds; morph-trained recipe 13.7%).

### Reviews of 13 Nov and the H100 follow-up (Amendment 6)

- **Results review of the cluster-stack readings** (results-reviewer, Opus, 13 Nov about 08:50): "conclusions hold but need qualifying".
  Applied to result.md (copy of the previous version: `/mnt/t7/smad_next/AD4/read/result_md_before_cluster_20261113.md`): F1 Fast-DiM-ODE
  wording (three single-run WCSS seeds 1.2 to 3.6 points above 15%; "not passable" rests on label-permuted seed 403 at 18.2%, which
  did not learn its training task, true-label AUC 0.47; next reference 32.4%; twin 1 of 5 seeds above 15%); F2 bounded-head note on the
  ViT-L/14 DiM verdicts (morphs 0.04 to 0.38 logits above the genuine floor); F3 same-seed cross-platform differences as large as seed
  differences (registered-cell maximum 10.7 points; the reproduction pass is stack-specific); F4 seed 403 sentence corrected; F5
  `posthoc_m3.md` line 5 corrected and `posthoc_m3.py` now takes the flag from `ad4_gates_m3.json`; F6 the follow-ups describe the rented
  networks; F7 per-seed ranges on wide cells, DiM-C reduced not removed, Greedy-DiM borderline, reader seed means on reversed/split cells
  flagged; F8 Amendment 5 commit is 082f945 (not ba88926, an SM1 commit); F9 stale "not verified" item, ViT-L/14 tensor source, H100 gate
  is a same-stack check (score sha256 `97eae24c…` and `2c3fba3e…`), twin defined. Reviewer hypotheses (random-head shared axis,
  floor-band instability, Fast-DiM-ODE run-level rate on fresh seeds, run-to-run determinism) are listed for the lead; none registered.
- **Amendment 6** (08:48) and additions after the **pre-run check** (experiment-reviewer, Opus: GO WITH FIXES; additions 08:56): H100
  re-score of follow-ups (b), (c) on the registered WCSS networks. Prepared: staging `/mnt/t7/smad_next/AD4/fu/stage_wcss`; pack on WCSS
  `packs/AD4/fu_pack_wcss.tar` (1,680,128,000 bytes, sha256 `e4b60874…`, checked there); job `jobs_ad4/ad4_fu_h100.sbatch`. Not submitted:
  the dispatcher relayed a lead ruling dropping the item (networks "trained on other GPU models"); the networks of Amendment 6 are the WCSS
  H100 ones, so the lead is asked to confirm. Remaining before submission if confirmed: reader fixes F2 and F4 of the pre-run check, the
  pinned pack sha in the job script.
- 09:00 to 09:10, lead: proceed (re-scoring the WCSS-trained networks on an H100 keeps one platform). Reader fixes of the pre-run check
  applied: `fu_read.py` sha256 `31cc088a…` (new `--flag` option, gate refuses incomplete cells and `limit` ≠ 0 outside the smoke,
  non-finite blanked score stops the reader, H-new-4 floor label and FRLL p5-p95 span columns, "not computable" instead of None);
  re-tested on the synthetic folder (`readtest/*_t3*`). Job script `src/wcss/ad4_fu_h100.sbatch` sha256 `81df7e88…` (pack sha
  `e4b60874…` and scorer sha `e0ab24b5…` pinned, network source checked), uploaded to WCSS `jobs_ad4/` (hash equal there).
  Submission through the dispatcher queue: smoke `wcss_ad4_fu_h100_smoke.cmd`, production `wcss_ad4_fu_h100_prod.cmd` (submit only
  after the smoke completed with exit 0). Owner: AD4 reading owner. Expected run: smoke about 5 min, production about 20 min, after start.
- 09:02: smoke submitted by the dispatcher as **WCSS job 6310086** (ad4-fu-smoke). Production follows only after 6310086 completes with exit 0.
- 09:07, dispatcher on the lead's order: production submitted as **WCSS job 6310123** (ad4-fu-prod) alongside the smoke, Nice=30 for both. Its output is read only if smoke 6310086 completes with exit 0; if the smoke fails, the dispatcher cancels 6310123.

### Handover state, 13 Nov 14:41 (reading owner)

- WCSS 6310086 (smoke) and 6310123 (production), H100 follow-up re-score (Amendment 6), both PENDING on priority (Nice=30) at 14:40; the
  dispatcher watches them and cancels 6310123 if the smoke fails. Production results: `smad-next/results/AD4_fu/fu_h100_6310123_limit0.tar`.
- When 6310086 completes with exit 0 and 6310123 is done: copy the tar and `.sha256` under the WCSS lock to
  `/mnt/t7/smad_next/AD4/fu/h100/`, `sha256sum -c`, extract, then
  `cd /home/narolski/smad-next/src/AD4 && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 10 $P fu_read.py --res <extracted>/fu_h100_6310123_limit0
  --ref-res /mnt/t7/smad_next/AD4/results_wcss_m3 --tag _h100 --platform "WCSS H100" --flag "Reproduction gate: pass on the cluster stack."`
  (reader `31cc088a…`), then update result.md (follow-ups section) and send to review.
- Nothing else of AD4 runs anywhere. Athena array 3546123 cancelled (12 Nov 23:03).
- 19:08 13 Nov: the two reviews of 13 Nov saved verbatim (the record keeper found no saved file): `experiments/reviews/REVIEW_AD4_CLUSTER_20261113.md` (results review of both halves of the cluster-stack reading) and `experiments/reviews/PRERUN_AD4_FU_H100_20261113.md` (pre-run check of Amendment 6).
