# AD6 — matched-recipe retrains of comparator architectures: pre-registration

Written 2026-11-16, ~04:00 CET (machine clock 02:59Z–04:00Z on the DGX), by the AD6 owner (continuity agent),
on the author's dispatch order of tonight ("Przygotuj i zarejestruj NOWY eksperyment AD6 … matched-recipe retrains
of comparator architectures"). **No AD6 training run, score or result exists at the time of this writing.** The
per-arm training jobs are submitted only after this file is committed (registration commit hash recorded in the
dispatch header, per the dispatcher contract).

## 0. What was known when this was written (disclosed)

- AD5 (registered `experiments/AD5_retrains-of-released-methods/prereg.md`, 11 Nov): five retrains 401–405 of each
  released method with the AUTHORS' CODE and the authors' NATIVE training data (MADation: SMDD train cropped,
  40 epochs, global batch 8×32=256; MixFaceNet-MAD: SMDD train cropped, 100 epochs, batch 16). All 10 MADation/
  MixFaceNet retrains + scoring are complete with receipts (commit 1506d1c, RETRAIN_COHORT_EER_TABLE_20261116).
- The frozen method S-MAD and its recipe: FS1 manifests; **Sb** = protocol negatives + face-spliced morphs with
  matched splice negatives (PN1 prereg §Manifest B/arms; `train_Sb.csv` sha256 `2cf3fda3affc8dd3…`, 8,386 rows,
  4,193/4,193 count-balanced; FS1 training rows of FRGC and colorFERET only). Our own ViT-B/16 (a12
  clip_vitb16_madation, LoRA qv r2 α4 dropout 0.4) trained with recipe v1: steps 6,250, global batch 256
  (sampler=prior), aug=flip, constant LR, last checkpoint (PN1 prereg line 84; AD4 prereg).
- AD5/RS1 scoring pipeline and the roster/crops (RS1 regen crops v1+v2, corrected MAD22 population, FRLL roster,
  15 Nov author-ruled read) are frozen and unchanged here.

## 1. Question

The released S-MAD detectors are weak on our frames before our recipe (S) and their own-recipe retrains stay close to
the releases (AD5 table, H_native). **Does our Sb training recipe — not the architecture — carry the gain?** Train
each comparator architecture with OUR recipe and read the before→after per family: if the recipe transfers, the
comparators should move toward our recipe's behaviour; if the architectures cannot express it, they will not.

## 2. Arms, seeds, platforms (fixed)

| Arm | Code (unchanged authors' code + AD5 patches, ad5w_code.tar) | Training data (only change) | Length | Seeds | Platform |
|---|---|---|---|---|---|
| `madation_B_sbr` | MADation ViT-B/16 LoRA (`MAD_training`, lr 1e-5/1e-4, lora_r 2, lora_a 4, dropout 0.4, scheduler cosine = authors' defaults) | **full-Sb budget list** (below) | 6,250 updates × global batch 256 = **1 materialized epoch of 1,600,000 rows**, num_epoch=1, per-GPU batch 256/NG (authors' global batch 256 preserved), checkpoint of epoch 1 only | 401–405 | WCSS, lem-gpu-short, gpu:hopper:4 per job |
| `madation_L_sbr` | same, ViT-L/14 (lora_r 2, lora_a 8, dropout 0.2) | same | same | 401–405 | WCSS, same |
| `mixfacenet_X_sbr` | SMDD `main.py` (AD5 patches: AD5_LAST=1, AD5_SEED) | same | max_epoch=1, batch_size 256 → exactly 6,250 updates, weights after epoch 1 | 401–405 | DGX GB10 (fallback WCSS if GB10 blocked; same one-experiment read) |

Nothing else differs between seeds (same as AD5: `AD5_SEED` only; the materialized training list is **one shared
file for all arms and seeds**, so seeds differ only by model init / loader shuffling).

**Naming / labelling rule for the methods table:** rows from these runs are labelled **Hsbr** (our recipe, their
architecture) — distinct from RW (released weights), H_native (AD5 authors'-recipe retrains) and our own S-MAD.
"before S → after Hsbr" per family. No verdict language beyond the registered direction test below.

## 3. Training list (the recipe, materialized)

`train_Sb_6250x256.csv` — built by `src/AD6/build_sb_budget_csv.py` from the registered `train_Sb.csv`
(sha256 `2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a`):
- exactly 1,600,000 rows = 6,250 updates × 256 (global batch), deterministic seed 400, one shared file;
- **per-batch count balance**: label-alternating blocks of 256 (128 bonafide / 128 attack everywhere; 97+97 tail
  rows never used mid-block); global 800,000/800,000 exactly;
- labels as strings `bonafide|attack` (both loaders map bonafide→1); header `image_path,label`; paths rooted at
  `CROP_ROOT` (placeholder sed'ed by the job);
- CSV sha256 `5fd26e32fcf0d6f7daebac1d1d66ce649d45e87ffa307f310b418112b59c91b3`; images tar
  `ad6_sb_pack.tar` sha256 `2b5b2880daf2f215b8dd9e41b5d95bd970d2e7d24b1d6011c373e62cd0d3c281` (FS1 `train/` tree
  + native `train_Sb.csv` manifest + csv + build report; all 5,353 unique images present, 0 missing).
- No eval-corpus row: asserted at build (no FRLL/MAD22 path substring); training rows are FS1 FRGC/colorFERET rows only.

**Recipe-mapping choices registered here (disclosed):**
1. "6,250 updates" is the recipe's optimizer-step budget (recipe v1 `--steps=6250`); materialized as
   num_epoch=1 CSV of 6,250×256 rows so the update count is exact and loader-independent (no drop_last
   dependence). Consequence: the authors' per-epoch LR schedule executes exactly once (≈ constant LR), and the
   authors' cosine scheduler runs its single cycle over 6,250 steps — closer to recipe v1's `--sched=const`
   than to their native long schedules; accepted, recorded.
2. Per-batch composition is balanced by the CSV blocks; if the authors' DataLoader reshuffles (shuffle=True),
   global 50/50 totals and even per-block balance in the file remain the recipe transfer; per-batch balance is
   then not forced at runtime (disclosed; the recipe's `sampler=prior` is not re-implemented inside the authors'
   loaders).
3. Augmentation stays the authors' (RandomHorizontalFlip) — recipe v1's `--aug=flip` matches.

## 4. What is NOT changed — and the one registered code change

Authors' code, with the reviewed AD5 patches (seed from env, train csv from env, no test lists, AD5_LAST/
AD5_EPOCH_DIR for MixFaceNet), plus **one registered AD6 change**: `build/madation_src/src/utils/logging.py`,
`CallBackModelCheckpoint.__call__` — the save guard `epoch > 1` becomes `epoch >= 0` in both its save lines
(patch `src/AD6/ad6_save_epoch1.patch`). Reason: the save guard throws away any schedule shorter than 3 epochs,
so `num_epoch=1` cannot emit a checkpoint without it; nothing about training maths changes, saves fire at the
last epoch exactly as before for any num_epoch ≥ 3. AD5 checkpoints/results are untouched (separate code pack
`ad6w_code.tar` sha256 `968001b074b43dff8867f688b8a9ab47774ab3bdb1bd143975d113f34a49acf3`; AD5's `ad5w_code.tar`
stays the AD5 provenance artefact). Test/eval lists of either codebase stay empty
(AD5_NO_TEST=1 / AD5_LAST=1); no test/eval image is read during training. Scoring pipeline, roster, crops
(RS1 regen v1/v2), metric (EER on `logit_noTTA`, ties-halved) identical to the released-rows pipeline of
RETRAIN_COHORT_EER_TABLE_20261116. Qualifiers of that table carry over.

## 5. Success criteria (registered before any AD6 score exists)

- **Primary (descriptive, for the methods table):** per-family EER (%) mean over 5 seeds ± sd for Hsbr, at the
  17 canonical cells (5×FRLL: amsl/facemorpher/opencv/stylegan/webmorph; 5×MAD22-corrected: FaceMorpher,
  OpenCV, Webmorph, MIPGAN_I, MIPGAN_II; 7×DiM/MorDiff variants), v1 primary + v2 validation, next to S and
  H_native. k=n/5 seeds recorded per family.
- **Registered direction test (recipe transfer):** count families where mean EER(Hsbr) < mean EER(H_native).
  *Recipe-transfer supported* if ≥13 of 17 families improve (sign test, one-sided p ≈ 0.0064 at 13/17);
  *not supported* if <13. Per-arm reading (B, L, X separately); also pooled as secondary.
- **Secondary:** FRLL five-family mean EER of Hsbr vs H_native.
- All gates require k=5/5 seeds completed and verified receipts (rows/uniq/finite + SHA256) for every scoring
  file. A failed run is reported, never reseeded, never replaced.

## 6. Failure / deviation policy

- No reseed, no seed replacement, no retry with a different seed. A failed job may be replayed once only if the
  failure is infrastructural (node/preemption), with the same seed and a dated note.
- Any deviation from this file gets a dated dated amendment section before the affected run starts.
- Budget: WCSS existing allocation only (no paid resource, no Vast purchase — Vast remains withdrawn);

## 7. Dispatch (recorded after jobs go in)

- WCSS: arrays `--array=401-405`, `--gres=gpu:hopper:4 -c 16 --mem=250G --time=04:00:00
  --extra=FORCE_RM_TMPDIR`, ARM=B first (nice 40), then ARM=L (nice 41); submitted through the dispatcher
  queue mechanics; results/AD6 on lustre; tars + sha256.
- GB10: MixFaceNet X×5 sequentially, same code pack (`ad5w_code.tar`, sha-verified), venv-spark environment;
  each run's npz-equivalent checkpoint → scoring by the same AD5 scoring script (release mode rel not used
  here; the retrain checkpoint mode as in the mixfacenet retrain scoring of 15 Nov).
- Scoring (after checkpoints arrive): identical pipeline/roster/crops as RETRAIN_COHORT scoring (30/30, 15 Nov
  pipeline), receipts + aggregate extension **Hsbr block appended** to RETRAIN_COHORT_EER_TABLE (v1 primary,
  v2 validation).
