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
