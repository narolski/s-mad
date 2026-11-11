# AD4 Morph-free network (A47 I-3 repeated with a working chance reference); also serves AR6

Written 11 Nov 2026 before any AD4 network exists or any AD4 score is read. The zero-step networks are
part of the reference and are scored on the DGX together with this registration (their numbers go to
`zero_step/` and are not used to change anything below).

- **Hypothesis (plain words):** A1 of `04_HYPOTHESES.md`. A network that never sees a morph, trained only
  to tell SMDD renders (label 0) from their own shrunk-and-enlarged copies (label 1), passes the FRLL
  diffusion benchmark cells. If it does, those cells measure processing history, not morphing. The same
  networks are read on every other benchmark cell (landmark, GAN, corrected MAD22) as AR6.
- **Data:**
  - Training: the registered A47 I-3 root, unchanged (`/mnt/t7/smad_heldout/a47/data47/i3`,
    `manifests/train.csv` sha256 `0273c11b…`, 25,000 SMDD bona fide natives label 0 + 25,000 copies by
    `prep_eval.degrade(img, "R", 0.3125)` label 1, built 7 Nov). No new resampling is run. Natives are
    byte copies of `smadcvpr_data/train/smdd/os25k_bf_t` (sizes checked against the WCSS `data_train`
    pack listing); copies checked against `data47/i3/SHA256SUMS`.
  - Label-permuted reference: the same 50,000 rows, the label column shuffled by
    `random.Random(2026111100 + seed).shuffle` (seed 401…405, a fresh permutation per seed; 24,890 to
    25,080 labels changed; 25,000 / 25,000 kept). Manifest sha256 in `build_info.json` of the pack.
  - Untrained reference: the zero-step network of each recipe (seed 401): the state train.py holds
    before its first step (seeds set, `build_model`, `apply_lora`): frozen CLIP, LoRA B = 0, random head.
  - Test (no FRLL person enters training; SMDD is synthetic): from `smadcvpr_data/manifests/eval.csv`
    the sets `mordiff`, `dim` (dim_a, dim_c, fast_dim, fast_dim_ode, greedy_dim, greedy_dim_s), `frllm`
    (amsl, facemorpher, opencv, webmorph, stylegan), variants `orig` (native) and `resmatch` (E7 photos),
    14,120 rows; and the **corrected MAD22** canonical512 inputs
    (`mad22_canonical_E7_inputs_v3_20261109T113746Z`, `native/` 4,687 + `e7/` 1,020, checked against
    `PROCESSED_SHA256SUMS`), families FaceMorpher, OpenCV, Webmorph (landmark) and MIPGAN-I, MIPGAN-II
    (the MIPGAN cells). The old MAD22 subset in `eval.csv` is not used. Manifest `ad4_eval.csv`
    (19,827 rows, sha256 `5d3950ab…`).
  - Cells: native = family morphs vs the set's bona fide; E7 = family morphs vs that family's E7 photos.
- **Model and recipe:** the A12BR R rows used by A47 (M3 row byte-identical to A47 I-3; M3L = the
  A12_BR_T2 M3L row): CLIP ViT-B/16 (M3) or ViT-L/14 (M3L), frozen, LoRA r 2 on q,v (alpha 4, rsLoRA,
  dropout 0.4), linear head; AdamW, LR 3.33e-6 (head 3.33e-5), wd 0.05, constant LR, 6,250 steps,
  batch 256 (M3L: 32 × 8 accumulation), flip augmentation, clip-grad 5, pos-weight 1, input 224.
  Seeds 401–405. Checkpoint: `last.pt`, no selection. `train.py` and `common.py` are the A47 job-root
  files (sha256 `0ba35b33…` of `jobroot_a47.tar`), unchanged.
  - Arms per recipe: morph-free (mf) × 5 seeds; permuted (perm) × 5 seeds; zero-step × 1. 20 trained
    networks in all.
- **Primary metric:** per cell and network, EER (%) and signed AUC (morph positive, not folded), TTA =
  mean of sigmoid(image, h-flip) as `score.py`. Training accuracy (threshold 0.5, no TTA) on the network's
  own training labels and on the true labels, for every trained network. Intervals: 95% bootstrap over
  FRLL persons (the `a41_read.py` two-way method) computed at read time; seed range printed.
- **Decision rule (fixed in `11_AUDIT_PLAN.md`, "AD4 reading"; applied per recipe and cell):**
  - A cell is **"passable without morphs"** only if the morph-free EER is at least 10 points below the
    lowest EER among the five permuted networks and the zero-step network. Decided on the morph-free
    seed mean; printed beside it: how many of the 5 seeds individually meet the same margin.
  - **A1 falsified** for a cell if the morph-free EER is above 15% in at least 3 of 5 seeds. Primary
    cell: MorDIFF native (the A47 observation); secondary: the six DiM / Greedy-DiM natives. All other
    cells (FRLL landmark and StyleGAN, corrected MAD22 incl. MIPGAN, every E7 cell) are descriptive (AR6).
  - Neither outcome, for a primary or secondary cell: "mixed", with all numbers.
  - The permuted networks are not required to sit at 0.5 (A47 showed they need not); they are the
    reference, nothing is gated on them. Their training accuracy is reported so that memorisation can be
    judged.
- **Guards:** single network per number; no ensembles, fusion or seed picking; no FRLL person in
  training; corrected MAD22 only; no image operation beyond the registered A47 data; the evaluation
  images are byte copies. Non-finite run: reported, not replaced.
- **Stop rule and budget:** 20 WCSS slot tasks. Estimate (basis: A47 I-3 M3 `train_hours` 0.52 h and
  A12BR M3L 1.94 h on H100 with 14 workers): M3 task ≤ 75 min, M3L task ≤ 180 min, including about
  10 min for pack copy, check and extraction and about 10 min of scoring. Total about 21 H100-h. A failed
  task is rerun once unchanged; never rerun because of its values.
- **Command (tested on 8 images):** `TASK_DIR=… TASK_WORK=… bash run.sh` (`src/AD4/run.sh`; per task
  `task.env` = TASK RECIPE ARM SEED). DGX test: `AD4_LOCAL=1 AD4_STEPS=3 AD4_LIMIT=8` (see `result.md`).
- **Deviations from the registered A47 recipe (disclosed):**
  1. `--es-snaps=10` dropped. A47 selected `es.pt` on VALX-A*, which AD4 does not use; the snapshots
     consume no random numbers, so `last.pt` is the same network as A47's would be at that seed.
  2. Seeds 401–405 (A47: 1–3); M3L added (A47 had M1 and M3).
  3. CLIP weights: the timm hub `pytorch_model.bin` loaded with `weights_only=True` and stored as
     safetensors under `hf/a12/` (the A12 converted-weights path). Same tensors as A47's file is assumed,
     not byte-checked (A47's converted file is only inside the 31 GB WCSS `hf` pack).
  4. 7 loader workers (slot has 8 CPUs; A47 used 14). The sample order comes from the global torch RNG
     in the main process and is unchanged; the flip draws come from per-worker seeds, so the flips differ
     from a 14-worker run at the same seed.
  5. E5 robustness variants (blur, jpeg, chip, resample50) of `eval.csv` are not scored; corrected
     MAD22 replaces the old MAD22 subset.
  6. Scoring by `src/AD4/ad4_score.py` (the `score.py` core: same loader, TTA, sigmoid), because
     `score.py`'s A12 locks refuse non-registered manifests.
- **Pre-run review:** pending (lead).
- **Result:** pending.

## Amendment 1 (11 Nov 2026, about 16:21 CET; written before any trained network of the morph-free networks experiment (AD4) exists)

Source: the independent pre-run review of 11 Nov, the lease change, and the lead's instructions. Nothing below was
chosen after seeing a trained network. The only scores read so far are the untrained ViT-B/16 network's
(see (f)).

**(a) Rented path for the ViT-B/16 recipe (M3).**
- **Machine and stack:** all ten ViT-B/16 networks (five morph-free, five permuted) train on one Vast lease:
  instance 60224295, 2x RTX PRO 5000 (72 GB each), California, 0.962 USD/h. Image
  `pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime`, because these cards need a newer PyTorch. timm 1.0.27,
  huggingface_hub 0.36.2 and safetensors 0.8.0 match the WCSS library packs. numpy is pinned to 1.26.4 and
  Pillow is the image's own. The exact versions are recorded in `/mnt/t7/smad_next/AD4/vast/` (setup log).
- **Torch differs from the cluster container** (2.7.1 against 2.2.1). The ten ViT-B/16 networks all come from
  this one stack; stacks are never mixed within a recipe. The ViT-L/14 recipe (M3L) runs on WCSS in the
  container.
- **Training call:** `train.py` is called directly. `a47_train.py` (A47's entry) is a pass-through to `train.py`
  when `--acq-aug` is absent, which is the case for every I-3 row.
- **Earlier lease, closed unused:** instance 60223497 (2x RTX 4090, 24 GB) was destroyed before any task ran
  (0.11 USD), because the review estimated the batch-256 memory at 32–36 GB.

**(b) Gaps in the decision rule, closed.**
- Named case "below every reference, not at the published level": the morph-free EER is at least 10 points
  below every label-free reference, but above 15% in at least 3 of 5 seeds. It is reported as such for every
  cell. On the primary and secondary cells it means "A1 falsified on this cell although the network beats the
  references".
- A "passable without morphs" verdict needs all six references (five permuted-label networks and the untrained
  network). With fewer, the verdict is "provisional", and the number of references present is printed.
- EER is recomputed at read time from `scores_eval.npz` with `analyze.eer` (code-tree `smadcvpr/analyze.py`).
  The `metrics.json` value uses `common.eer`, which depends on row order when scores are tied. AUC is
  recomputed with `analyze.auc`.
- The reader refuses a network if any of these hold:
  - a non-finite score;
  - `steps` other than 6250 in `meta.json`;
  - a scoring limit other than 0;
  - an evaluation-manifest sha256 other than `5d3950ab5ccdeed4d376a15126cff660da2a35041579b3513eb7a1059baaa061`;
  - a training-manifest sha256 other than the registered one for its arm.

**(c) Wording on landmark cells.** The untrained network already reaches FRLL landmark AUC up to 0.72, so the
claim there is "at least 10 points below every label-free reference (range a to b %)". It is never "above
chance". The folded reference (|AUC − 0.5| + 0.5) is printed beside it. A miss on a landmark cell does not show
that the cell needs morphs.

**(d) ViT-L/14 recipe.** Each cell prints the morph-trained twin beside it: the A12BR M3L R × d0 networks, seeds
1–5, last checkpoint, where their scores exist. Those scores are on the old `eval.csv`, so there is no twin for
the corrected MAD22 cells; those are marked "no twin". A miss is worded "does not reach 15%; the morph-trained
recipe reaches x%".

**(e) E7 cells.** The genuine E7 copies are byte-identical to the native photos for:
- FRLL StyleGAN, 204 of 204;
- corrected MAD22 MIPGAN-I and MIPGAN-II, 204 of 204 each;
- corrected MAD22 OpenCV, 108 of 204;
- corrected MAD22 Webmorph, 104 of 204.

These counts were checked with `cmp` on the pack. The first three cells are labelled "E7 not applicable", the
last two "E7 partial (n identical)". Every other E7 cell has 0 identical copies.

**(f) Disclosures and hashes.**
- The untrained ViT-B/16 network was scored and its metrics read at about 15:15 CET. The pre-registration file
  was first committed at 15:38 (commit 4068c3a). The decision rule itself is the one fixed earlier in
  `11_AUDIT_PLAN.md` ("AD4 reading") and `04_HYPOTHESES.md` (A1). Nothing in the rule was changed after that
  read.
- File hashes (sha256):
  - `run.sh`: 5aae2ef9dad93134548a75516955f14732de0e5f5729d488b2b85d2d6faf7dec (identical in all 20 task
    directories);
  - `ad4_score.py`: f0cadb7af320990d74ceffd9b92d1dab1d0085f30202bb7328ca4947f9cdd2cf (same inside the pack);
  - `build_pack.py`: 5c296a3e8663f4998dae445bb61b2e83a49b1c223718b366ac9c7d0359753957;
  - plan file `make_tasks.sh`: 4b714effa1d154f206733dcfa7b21e5d1cb72152b65052c42b020b552f2a61a3;
  - pack: 1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde.

**Gates. They are computed when results arrive; a miss is reported and stops nothing.**
1. **Sample-order gate.** Each task's recorded batch composition (`meta.json` `composition.per_batch`, the
   first 200 batches) must equal the CPU prediction for its seed and manifest. The prediction comes from the
   reviewer's `order_check2.py` (sha256 16e8d238…) run with that seed. For seed 401 the first three batches
   are expected to be [[139,117,0],[125,131,0],[124,132,0]]. Tolerance: exact equality of all 200 rows. A
   miss means "sample order differs from the cluster stack" and is printed beside every number of that
   network.
2. **Reproduction gate.** The comparison is the three ViT-B/16 morph-free networks of the original A47 I-3
   run (seeds 1–3, last checkpoint, H100). The ViT-B/16 morph-free seed means on this stack must meet:
   - each of the seven diffusion native cells (MorDIFF and six DiM) at most 3.0% EER;
   - FRLL FaceMorpher, Webmorph and AMSL at most 5.6%;
   - FRLL OpenCV within 8.8–26.0%.

   A miss means "not reproduced on this stack". The cluster tasks then decide; they would need the ten
   ViT-B/16 tasks re-queued on WCSS.
3. **Scorer equivalence.** One last-checkpoint ViT-B/16 network of the original A47 I-3 run, re-scored with
   `ad4_score.py` on the DGX, must agree with its registered `scores_eval_last.npz` on every shared cell:
   |AUC difference| ≤ 0.005 and Kendall tau ≥ 0.99 per cell.

## Amendment 1b (11 Nov 2026, 16:37 CET; written before any trained network of the morph-free networks experiment (AD4) exists)

The rented path changes again (author's suggestion). It replaces point (a) of Amendment 1. Points (b) to (f)
and the gates stand.

- **Aborted lease, nothing ran:** instance 60224295 (2x RTX PRO 5000) reported "running" but refused SSH for
  7 minutes. It was destroyed under the ten-minute rule (records in `vast/lease2_2xPRO5000_unreachable/`).
  Together with lease 1, the two aborted leases cost 0.27 USD in total.
- **Two single-GPU machines, identical image and package pins.** The image is
  `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, the same PyTorch as the WCSS container. The packages are
  timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0 and numpy 1.26.4, plus the image's Pillow. The
  software deviation of Amendment 1 (a) therefore falls away; only the card differs from the cluster (A100
  class instead of H100).
  - **Machine A** (`vast/leaseA`): instance 60226054, NVIDIA A100-SXM4-40GB, 0.433 USD/h. It runs the five
    ViT-B/16 morph-free networks (AD4_m3mf_s401..405).
  - **Machine B** (`vast/leaseB`): instance 60227348, NVIDIA RTX 6000 Ada Generation (48 GB), 0.738 USD/h.
    It runs the five ViT-B/16 label-permuted networks (AD4_m3perm_s401..405). It replaced instance 60226099
    (offer 56042632, 1.00 USD/h), which was destroyed at 16:44 after it stayed unreachable for 13 minutes; no
    task ran on it. Card filled in at 16:46, before any trained network existed.
- **Within a recipe all ten networks share image and pins.** The two machines carry different card models
  (A100 for the morph-free arm, RTX 6000 Ada for the permuted reference; same software). This is printed beside
  every number.
- **Batch fixed.** If the registered batch of 256 does not fit in 40 GB, the machine is replaced by a 48 GB or
  80 GB card. The batch, steps or any other recipe value is never changed.
- **Cap and watchdogs.** The global cap of 10 USD is enforced through the account-level drop in credit from the
  baseline of 111.58 USD. Each machine has its own watchdog.
- **Results:** they arrive in `/mnt/t7/smad_next/AD4/results_vast/` and are read with the reader and gates of
  Amendment 1.

## Amendment 1c (11 Nov 2026, committed 18:28 CET as 7f0630f, lead; before any ViT-L/14 result exists or is read)

Platform and precedence, written because the same ten ViT-L/14 tasks (five morph-free, five label-permuted) are
staged in two places and one of them cannot be reached.

- The ten ViT-L/14 tasks run on Athena (Cyfronet, A100 40 GB, x86, the environment of
  `src/athena/env_and_smoke.sbatch`: torch 2.2.1 with CUDA 12.1, timm 1.0.27, pillow 10.2.0, numpy 1.26.4), through
  the unchanged `run.sh` with `AD4_LOCAL=1`. **The Athena result of each task is the registered one.**
- The same ten tasks also sit in the WCSS ready queue (staged before WCSS closed to our address on 11 Nov). They
  cannot be removed while WCSS is unreachable, and slot jobs submitted earlier may run them. If a WCSS result of a
  task appears, it is kept and reported only as a cross-platform repeat (difference in each cell's error rate and
  AUC against the Athena result); it never replaces or is averaged with the Athena result, and no choice between
  the two is made after seeing numbers.
- The ViT-B/16 arm ran on two rented x86 machines (A100 40 GB for the morph-free fits, RTX 6000 Ada for the
  label-permuted fits) with the same package versions. Its results are the registered ones for that arm.
- Unchanged: recipes, seeds 401 to 405, last checkpoint, no selection, the gates of amendments 1 and 1b.

## Amendment 2 (11 Nov 2026, about 22:36 CET, new owner of the reading; written before any score of a trained network of the morph-free networks experiment (AD4) is opened)

Seen before writing this: the names, sizes and sha256 files of the nine result tars in `results_vast/` (member
list of one tar), the untrained networks' metrics already disclosed in Amendment 1 (f) and the README, and the keys
and manifest hash (not the values) of the five morph-trained ViT-L/14 twin score files. No score, metric or
training accuracy of a trained AD4 network has been opened. The registration leaves the points below undefined; each
is fixed here, with the reason. Nothing in the decision rule, the gates or the refusal rules changes.

**(a) Person bootstrap** (registered as "95% bootstrap over FRLL persons, the `a41_read.py` two-way method"; size,
seed, person set and the statistics it covers were not given).
- Scheme: the pigeonhole (dyadic) person bootstrap of `a41_read.py` (`Draw`, `persons`; file sha256
  `0bc7381b0eddb29b6abb74fbf705f9befaae2700316bcb804b94e7cc3e743cb1`), copied unchanged. A genuine photo weighs its
  person's count, a morph the product of its two contributors' counts (a self-pair: the count).
- Persons: the FRLL persons of the 204 unprocessed FRLL genuine photos (`frllm/frll_bona/orig`), 102, asserted.
  Every row of `ad4_eval.csv` (DiM, MorDIFF, FRLL-Morphs, corrected MAD22, native and E7) is mapped to FRLL persons
  by its file name; a row whose person is not among the 102 stops the reader. DiM, MorDIFF and FRLL-Morphs rows use
  `a41_read.py`'s patterns unchanged. Corrected MAD22 names carry no `_orig` suffix, so these rows use the same
  patterns ending at `.png`: genuine `^(\d{3})_(\d{2})\.png$`, morph `^(\d{3})_\d{2}-vs-(\d{3})_\d{2}\.png$`
  (checked on file names only: 1,224 of 1,224 genuine and 4,483 of 4,483 morph rows match; added about 22:38, before any
  reading).
- B = 10,000 (`a41_read.py`'s decision bootstraps), `numpy.random.default_rng([20261111, 4])`. One draw shared by
  every network, cell and both recipes (paired).
- 95% interval = 2.5 and 97.5 percentiles of the replicates, for: EER and signed AUC of every network in every cell;
  the seed mean of each arm (mean of the networks' replicate values); the margin "morph-free seed mean minus the
  lowest reference", replicate by replicate. Unit weights must reproduce the point EER and AUC exactly (checked).
- The intervals are descriptive. The verdicts stay on point values, as registered.

**(b) The morph-trained ViT-L/14 twin of Amendment 1 (d)** (files and matching were not given).
- Files: `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR/a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{1..5}_r/scores_eval_last.npz`,
  key `score` (the TTA score), the A12BR M3L R × d0 networks, seeds 1 to 5, last checkpoint. Their manifest is the
  old `eval.csv` (sha256 `86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9`, checked in each file).
- Rows are matched by id after checking that each `ad4_eval.csv` row's id and path equal the `eval.csv` row of that
  id. A cell has a twin only if every one of its rows has a twin score; otherwise it is marked "no twin" (all
  corrected MAD22 cells). The sha256 of the five files is printed.
- Printed beside each ViT-L/14 cell: twin seed mean EER, its range and its fixed-threshold rates. The twin is not a
  reference and enters no verdict. A primary or secondary cell where A1 is falsified is worded "does not reach 15%;
  the morph-trained recipe reaches x%", x = the twin seed mean.

**(c) Fixed-threshold rates** (the lead's instruction of 11 Nov; not in the registration; descriptive only, no
verdict uses them). Two thresholds per network, both fixed without looking at any morph:
- the 0.5 rule: flagged if the TTA score is at least 0.5 (the rule of the registered training accuracy);
- FRLL-5%: flagged if the score is above the 11th highest score of the network's 204 unprocessed FRLL genuine photos
  (so at most 10 of 204, 4.9%, of that pool are flagged).
- Per cell: flag rate = share of the cell's genuine photos flagged (native cell: the set's unprocessed genuine
  photos; E7 cell: the history-matched genuine photos); miss rate = share of the cell's morphs not flagged. Always
  printed together, with the threshold pool as a column. Point values, per network and as arm means.

**(d) Incomplete arms.** An arm with fewer than five networks is printed only as descriptive rows labelled
"incomplete (k of 5)": no verdict and no reproduction gate. Fewer than five permuted networks makes the verdict
"provisional" as in Amendment 1 (b).

**(e) Labels.** Every table is labelled "our frames" (our alignment of every benchmark, `REVIEW_EV1_20261111.md`).
Beside every network its card and platform, from `metrics.json` (`info.device`) and the result folder (rented
machine or Athena).

**(f) Sample-order gate for ViT-L/14.** `train.py` records one composition row per loader batch, which for the
ViT-L/14 recipe is the micro-batch of 32 (8 per optimiser step); the prediction uses batch 32 (`gates.py`).

**(g) Printed checks that refuse nothing:** `meta.json` seed equals the task's seed and `meta.json` arch equals the
recipe's.

**(h) The reader.** `src/AD4/summarise.py` is rewritten to implement the registration with these points; its sha256
is recorded in the README before it reads any trained network.

## Amendment 3: post hoc addendum to the ViT-B/16 reading (11 Nov 2026, 23:44 CET, after the independent review `experiments/reviews/REVIEW_AD4_VITB_20261111.md`; registered before these readings are run)

Post hoc and descriptive: these readings were asked for by the reviewer after the ViT-B/16 numbers were seen. They change no
verdict of the registration. Zero GPU, one CPU process, script `src/AD4/posthoc_m3.py`, outputs `experiments/AD4/posthoc_m3.{json,md}`.
Bootstrap: the registered one (Amendment 2 (a): 10,000 replicates, seed [20261111, 4], 102 FRLL persons, the same draw). Our frames throughout.
Inputs: the ten ViT-B/16 result tars and the untrained network, already verified by the reader; PNG file sizes of the evaluation images in
`/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/data/` (the pack's byte copies, i.e. our frames).

1. **Floor logits.** logit = log(p / (1 − p)), p clipped to [1e-7, 1 − 1e-7]. Training set (`scores_train.npz`, no TTA, true labels): per
   network, median and 5th / 95th percentile logit of the SMDD natives and of their shrink-and-enlarge copies. Evaluation (TTA score): per
   network and cell, median logit of the morphs, of the cell's genuine photos and of the set's unprocessed genuine photos. Per network the
   FRLL-5% threshold as a probability and a logit.
2. **Own-genuine flag rate at FRLL-5%.** For each set's unprocessed genuine pool (MorDIFF, DiM, FRLL, corrected MAD22): flag rate per seed,
   arm mean with its 95% interval (weighted share under the bootstrap draw), always beside the miss rate of each family of that set.
3. **File-size null per cell** (native and history-matched): signed AUC and EER of the score "smaller PNG file = more morph"
   (−bytes), with 95% intervals; and per network the Spearman correlation of the network score with −bytes inside the cell (both classes).
4. **Seed spread.** For each cell of the morph-free arm: the per-seed EER and AUC, the range; "wide" if the EER range exceeds 30 points;
   "reversed" if all five AUCs are below 0.5; "split" if at least one AUC is below 0.4 and at least one above 0.6. For reversed and split
   cells no seed mean is printed. For wide cells the range is printed beside the mean.
5. **Label-permuted networks:** training accuracy and AUC on their own labels and on the true labels, per seed (from `metrics.json`).

Wording rules adopted from the review for every later text of this experiment (result.md and the ViT-L/14 reading): the networks are
"trained only to flag shrink-and-enlarge copies of synthetic faces (no morph, no blending)"; "resolution history", not storage history;
the history-matched control "removes or overshoots the cue", never "chance"; every statement "in our preprocessing"; flag and miss rates
always together.

## Amendment 4: follow-ups of the review, H-new-1 to H-new-5 (11 Nov 2026, 23:50 CET; registered before any of these measurements or scores exists)

Approved by the lead after `experiments/reviews/REVIEW_AD4_VITB_20261111.md`. Post hoc in origin (the ViT-B/16 numbers are
known), so every verdict below is labelled "post hoc follow-up". Our frames unless stated. Bootstrap: the registered person
bootstrap (Amendment 2 (a)); for the ladder sets a pigeonhole bootstrap over their FRGC / colorFERET persons (columns `p1`,
`p2`), B = 10,000, seed [20261111, 4, 5]. Networks: the five ViT-B/16 morph-free networks (seeds 401 to 405; the arm carries the
flag "not reproduced on this stack"); beside them the five label-permuted networks and the untrained network as references.
Each number is one network; no fusion.

**Face region (fixed, no detection).** Our frames are eye-aligned to the canonical 512 x 512 frame of `prep_eval.py` (eyes at
(190, 210) and (322, 210), inter-eye distance 132 px). Face ellipse: centre (256, 264), semi-axes 125 px (horizontal) and 172 px
(vertical). Face box (inside the ellipse): x 166 to 345, y 160 to 379 (180 x 220 px). Images that fell back to a plain resize in
`prep_eval` (non-frontal) are not aligned; they are kept and counted.

**(a) H-new-1, face-only softness null; H-new-2, rank test** (DGX CPU, one process, `src/AD4/fu_sharpness.py`; reads the
evaluation PNGs, writes no image).
- Measures per evaluation image, on the grey image (ITU-R 601 luma, float): M1 = variance of the 3 x 3 Laplacian (cv2.Laplacian,
  a measurement) inside the face ellipse; M2 = share of spectral power above 0.25 cycles per pixel (radial) in the face box after a
  2-D Hann window, DC excluded. Primary statistic: S = −M2 (softer = more morph); M1 printed beside it.
- H-new-1 (native cells): per cell AUC of S (morph positive) with interval; per morph-free network the Spearman correlation of
  the network score with S inside the cell. Qualifying cells: native cells where the morph-free AUC is at least 0.99 in all five
  seeds. **Supported** if S reaches AUC ≥ 0.7 in every qualifying cell and the median (over seeds) Spearman is ≥ 0.7 in every
  qualifying cell; **falsified** if S has AUC < 0.7 in at least half of the qualifying cells; otherwise **mixed**.
- H-new-2 (the seven diffusion history-matched cells, MorDIFF and six DiM): x = AUC of S, morphs against the history-matched
  genuine photos (how much softer the history-matched photos are than the morphs, low = softer photos); y = median over the five
  seeds of the morph-free network's AUC in the cell. Spearman(x, y) over the 7 cells: ≥ 0.7 "consistent with overshoot", ≤ 0
  "inconsistent", otherwise "weak". The graded control of the review needs new resampling code and is not run (author item).

**(b) H-new-3, border-blanked re-score** (Athena GPU job, container image, `-A plgmultivision-gpu-a100
--exclude=t0010,t0014,t0020`, one A100).
- Blanking: every pixel outside the face ellipse set to (128, 128, 128), in every evaluation image of both classes (constant-colour
  region blanking; no other operation), written as lossless PNG inside the job (`$MEMFS`), then scored by the unchanged loader and
  TTA (the `ad4_score.py` core). Networks are rebuilt from the pack weights plus `last_trainable.pt` (`common.build_run_model`).
- Gate before reading: the same rebuilt networks score the unblanked evaluation images in the same job; each must agree with its
  registered `scores_eval.npz` within |AUC difference| ≤ 0.005 and Kendall tau ≥ 0.99 in every cell (the scorer-equivalence
  tolerance). A network that misses is reported and not read.
- **H-new-3 supported** if the morph-free seed-mean EER on blanked MorDIFF history-matched is above 15%; **falsified** if it is at
  most 5%; otherwise **mixed**. Every other cell, native and history-matched, is printed (MAD22 FaceMorpher especially), with the
  references, flag and miss rates at both fixed thresholds (thresholds recomputed on the blanked FRLL genuine photos), and intervals.

**(c) H-new-4 and H-new-5, new pools** (same Athena job; unchanged images; no blanking).
- H-new-5, the landmark ladder's (AR1) primary pool (FRGC and colorFERET, its own 512 frames from `73_delin_align`, not
  `prep_eval`): rungs R0 (camera photo, 536), R2w (warp-only), R3 (same-person morph), R4 (two-person morph), both tools (OpenCV,
  FaceMorpher), from `/mnt/t7/smad_next/AR1/manifest.csv` (pool `frgcferet`). Per tool and network: AUC(R3 vs R0), AUC(R4 vs R0),
  gap = AUC(R4 vs R0) − AUC(R3 vs R0), AUC(R4 vs R3), AUC(R3 vs R2w), AUC(R4 vs R2w). **Supported** (same-person blends flagged as
  often as two-person morphs) if the morph-free seed-mean gap is at most 0.1 for both tools; **falsified** if it is above 0.1 for
  both; otherwise **mixed**.
- H-new-4, held-out generator renders: primary pool = 1,000 SMDD evaluation genuine renders
  (`/mnt/t7/Datasety/downloads/SMDD/SMDD_release_evaluation/os25k_bf_e`, never in training; the same raw 256 x 256 form as the
  training label 0), chosen by `random.Random(2026111104).sample` of the sorted file list. Descriptive pools: the 423 StyleGAN3
  single-identity renders of the StyleGAN3 set (H3, `h3sg3/bona/orig`, our frames) and the 338 StyleGAN v1 renders of the H4b set
  (native 112 px, so resolution-confounded). Statistic per network: median logit of the pool minus the median logit of the 204
  unprocessed FRLL genuine photos. **Supported** (generator renders read as "unprocessed") if the pool median is below the FRLL
  genuine median in at least 3 of 5 morph-free seeds; **falsified** otherwise.

Order: (a) runs on the DGX now; (b) and (c) after an 8-image DGX test, an Athena smoke job (8 images per manifest) and then one
production job (estimate under 2 A100-hours). Inputs travel to Athena as one tar streamed over ssh (no local copy: `/mnt/t7` has
35 GB free, below the 50 GB rule).
