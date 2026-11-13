# Retrains of released methods with the authors' code (AD5): pre-registration

Written 11 Nov 2026, 18:10 CET, before any retrain exists and before any score of this experiment exists. Owner: AD5
hypothesis owner. Code `/home/narolski/smad-next/src/AD5/`, large outputs `/mnt/t7/smad_next/AD5/`, full record
`README.md` in this folder.

Abbreviations. MAD = morphing attack detection. EER = equal error rate (%). AUC = area under the ROC curve (0.5 =
chance). SMDD = the synthetic morphing development set (Damer et al., CVPRW 2022), training split. E7 = the existing
control that gives a genuine photo the morphs' shrink-and-store history. t5 = the threshold at which at most 5% of a
detector's native genuine photos of a cell are flagged (definition as the own-crop re-score, RS1). "Release" = the
checkpoint the authors published. "Retrain" = our training run of the authors' code. FE = frozen-encoder MADation
variant. LoRA = low-rank adaptation.

## What I knew before writing this page (disclosed)

- The behaviour of the releases on our frames and partly on their own crops: the MorDIFF ladder re-read (AD1) and its
  review, the expression cue use (C1b), what the smiling half carries (C1c), the fixed-threshold re-read (EV1), and
  the predicted reproduction labels in the own-crop re-score (RS1) prereg (from A46 RGB-only numbers). I have not opened
  any RS1 score or result file (only listed the RS1 folders).
- The MADation release training logs (authors' Google Drive files): configuration, 8 GPUs, 39,730 training images,
  and the test numbers the authors' code printed at epoch 40 on the authors' own test frames.
- No retrain of the authors' code exists. Our earlier re-implementations (A12-BR M3 / M3L / M4 / M8O) used our
  pipeline, not the authors' code, and are not part of this experiment.

## Question (measurement with fixed readings)

For each method, do five retrains with the authors' own code and training set show the behaviour that the own-crop
re-score (RS1) measures for the released checkpoint, when scored through the same preprocessing and on the same images?

## Methods, code, training data

| Arm | Method | Authors' code (commit) | Training data | Release compared |
|---|---|---|---|---|
| L | MADation CLIP ViT-L/14, LoRA (`MAD_training`) | gurayozgur/MADation 0542cf86 | SMDD train, cropped (below) | `madation_vitl14` (bb452ded) |
| B | MADation CLIP ViT-B/16, LoRA | same | same | `madation_vitb16` (ddb1455b) |
| S | SelfMAD HRNet-W18 | LeonTodorov/SelfMAD 09ed0819 (code = 673d0640) | SMDD train genuine renders only (25,000), with its own landmark and face-label files | `selfmad_hrnet_w18` (0ad8db6f) |
| X | MixFaceNet-MAD | naserdamer/SMDD repository 9683229c (`main.py`) | SMDD train, cropped | `mixfacenet_mad_smdd` (3d507c8b) |
| F (optional, run last if budget allows) | MADation FE ViT-L/14 (`MAD_training_only_header`) | MADation 0542cf86 | SMDD train, cropped | `madation_fe_vitl14` (74dd7fbc) |

Order of work: L and B, then S, then X, then F. Arm F is registered now so that it is not post hoc; it is run only if
L, B, S and X are submitted and the budget allows.

**Cropped SMDD.** The SMDD repository's `image_preprocess.py` (sha256 bcaecd29…, unchanged: MTCNN, first box, 5%
margin, BGR pixels into MTCNN, unclipped indices, images whose crop fails are skipped) run once on the 25,000 genuine
and 15,000 morph training images, on an Athena A100 with facenet-pytorch 2.5.2 and torch 2.0.1 (MADation's pinned
versions). The training list keeps the order of SMDD's `train.csv` and contains every image whose crop was written.
The MADation release log reports 39,730 training images; the count we obtain is printed and is not a gate.

**SelfMAD inputs.** 25,000 genuine renders `os25k_bf_t/`; landmarks by `preprocessing/dlib_lm.py` (unchanged; dlib
frontal detector and the 81-point predictor, sha256 of the predictor printed) on the DGX; face labels by
`preprocessing/face_labels.py` (unchanged; Segformer `jonathandinu/face-parsing`, revision and hash printed) on Athena.
An image without landmarks or labels is skipped by the authors' loader; the count is printed.

## Training commands (fixed)

Seeds 401, 402, 403, 404, 405; one job per seed; nothing else differs between seeds. Last checkpoint only.

- **L:** `python -m torch.distributed.launch --nproc_per_node=8 --nnodes=1 --node_rank=0 --master_addr=localhost
  --master_port=12355 config.py --debug=True --backbone_size="ViT-L/14" --dataset_name="MADTrain"
  --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 --lora_dropout=0.2 --lora_r=2 --lora_a=8
  --batch_size=32` (the authors' `train.sh` line), run in `src/` of the patched copy, with `AD5_SEED=<seed>`,
  `AD5_TRAIN_CSV=<cropped list>`, `AD5_NO_TEST=1`, `AD5_OUT=<out>`, `AD5_CLIP_SD=<OpenAI-format CLIP file>`. 40 epochs
  (default), checkpoint `40_backbone.pth` + `40_header.pth` (the code saves nothing else).
- **B:** same with `--backbone_size="ViT-B/16" --lora_dropout=0.4 --lora_a=4`.
- **F:** same as L with `--training_type="MAD_training_only_header" --lr_model=0 --lr_header=1e-2` (the authors' line).
- **S:** `python train__.py -n ad5_s<seed> -m hrnet_w18 -b 32 -e 100 -lr 5e-4 -t SMDD -v last -SMDD_path <dir>
  -s <out>` with `AD5_SEED=<seed>`; checkpoint of epoch 100.
- **X:** `python main.py --train_csv_path <cropped list> --model_path <out>/mixfacenet_SMDD.pth --is_train True
  --is_test False --output_dir <out> --max_epoch 100 --batch_size 16` with `AD5_LAST=1 AD5_SEED=<seed>`; weights of
  epoch 100.

**Stopping rule (never a test set).** MADation: epoch 40 of 40, the code's only checkpoint. SelfMAD: epoch 100 of
100 (the shipped `testset_best` selects on FRLL/FRGC/FERET morph test sets and is not used; FF++ validation is not
used either). MixFaceNet-MAD: epoch 100 of 100 (the shipped early stopping selects on the EER of the test list and is
not used). No test image is read during training.

**Changes to the authors' code (complete list; patches in `src/AD5/*.patch`).**
1. MADation `config.py`: seed from `AD5_SEED` (authors: 777 fixed); training list from `AD5_TRAIN_CSV`; with
   `AD5_NO_TEST=1` the test lists are empty (the code would only log them at epoch 40); output root from `AD5_OUT`.
2. MADation `backbone/model.py`: CLIP built by `clip.model.build_model` from the OpenAI-format state dict in the
   Hugging Face file `timm/vit_{base_patch16,large_patch14}_clip_224.openai/pytorch_model.bin` (loaded with
   `weights_only=True`) instead of `clip.load`'s download of the TorchScript file. Checked: after the authors' fp16 to
   fp32 cast every tensor (302 for ViT-B/16, 446 for ViT-L/14) equals the authors' frozen-encoder release checkpoint
   exactly (`/mnt/t7/smad_next/AD5/checks/clip_init_equivalence_*.json`).
3. SelfMAD `train__.py`: a saving strategy `last` (no validation, no test loop, save the epoch-100 state in the
   authors' format); seed from `AD5_SEED` (authors: 5 fixed).
4. MixFaceNet-MAD `main.py`: with `AD5_LAST=1` no test list is read, no evaluation, the last epoch is saved; with
   `AD5_SEED` both the CPU and CUDA generators are seeded (authors: CUDA seed 0 only).
Environment deviations: Python 3.10 (Athena's only Python module; MADation README says 3.9); opencv-python-headless
instead of opencv-python (same versions); setuptools 69.5.1 (openai-clip 1.0.1 needs `pkg_resources.packaging`);
SelfMAD packages its env.yml does not pin are pinned by us (list in `src/AD5/env/selfmad_requirements.txt`).
MixFaceNet-MAD runs in the MADation environment (its repository pins nothing). Hardware: A100 40 GB (authors: not
stated for MADation; RTX 4090 for SelfMAD). If ViT-L/14 at 32 images per GPU does not fit in 40 GB (measured in the
smoke job), L and F run on 2 nodes x 8 GPUs at 16 per GPU, which keeps the global batch (256) and step count.

**Failures.** A run that crashes or produces a non-finite loss is rerun once with the same seed; a second failure is
reported as failed and not replaced. No seed is added, dropped or chosen on any score.

## Scoring (same images, same preprocessing as RS1)

- MADation and MixFaceNet-MAD retrains: the RS1 path for the releases, unchanged: RGB MTCNN crops of RS1 (the A46
  crops and the RS1 crops, byte-identical files), the `a12_released` adapters (BGR, (x − 0.5) / 0.5, 224), decision key
  `score_noTTA`, ranks on `logit_noTTA`, through the landmark ladder's `score.py` with a wrapper that changes only the
  weight file. MADation retrains are converted to the scoring format by `a36_madation.py convert` (the converter used
  for the releases; its CPU equivalence check must pass).
- SelfMAD retrains: `score.py --mode own` (dlib 81 landmarks, landmark box + 6.25% margin, 384, /255, softmax[:, 1])
  on the RS1 raw files and stored A43 control images. The SelfMAD release is scored through the same AD5 path once
  (reference row, compared with the RS1 / A41 numbers as a platform check).
- Image sets and cells: exactly RS1's (FRLL-Morphs five families, MorDIFF, six DiM families, corrected MAD22 five
  families; genuine class the 204 FRLL photos; raw E7 for MorDIFF, DiM-A, Greedy-DiM; aligned-frame E7 elsewhere,
  labelled; A43 control images A, B, B20, C, C20, D, D20, E).
- Statistics: RS1's functions (`src/RS1/analyse.py`, imported unchanged; its sha256 printed), same two-way person
  bootstrap (B = 2,000, seed 20261111, one draw shared by the release and all retrains), same thresholds (t5, t_eer).

## Published reference values

The RS1 table (its prereg and amendment 1), unchanged. MADation ViT-L/14 / ViT-B/16 / FE ViT-L/14: MorDIFF, FRLL five
families (ViT-L/14, ViT-B/16 only), corrected MAD22 five families. SelfMAD: FRLL five families, Greedy-DiM.
MixFaceNet-MAD: MorDIFF, FRLL five families, MAD22 five families (as quoted in MADation).

## Reproduction gate (fixed)

Window W = max(1.5 points, 0.25 x published). A retrain **reproduces the method** if its native EER (point estimate,
full cell) is within W of the published value on every gate cell. Gate cells = the cells the paper reports for that
method (list above), except cells on which the release itself is labelled "our pipeline, published number not
reproduced" in RS1: on those the published value does not validate the scoring path, so they are dropped from the gate
and printed (this exception is mine, added to the lead's rule because without it a method whose release misses one
cell could have no reproducing retrain at all). The literal all-cells gate is printed beside it. Every retrain's
native EER on every cell is printed with its window.

## Readings (taken for every retrain exactly as RS1 takes them for the release)

Per cell: (1) native EER [95% interval]; (2) EER with history-matched genuine photos, and the history effect
Δhist = EER(history-matched) − EER(native); (3) flag rates at t5 for native, history-matched, aligned-native and
stored-small (A43 E) genuine photos; (4) native and history-matched EER with neutral-only (102) and smiling-only (102)
genuine photos, and the history-matched flag rate at t5 per half; (5) on the MorDIFF control images, AUC with the
higher rung positive: stored-small photo E vs raw photo; reconstruction vs stored-small photo (D vs E, D20 vs E);
same-pair morph vs reconstruction (B vs D, B20 vs D20); descriptive rows as RS1.

## Fixed reading per method

Effects compared (null value 0): Δhist (points); Δflag-hist = flag rate at t5 of history-matched minus native genuine
photos (points); Δflag-small = the same for the stored-small photo E (MorDIFF threshold); Δsmile = native EER with
neutral-only genuine photos minus native EER with all genuine photos (points); Δladder = AUC − 0.5 for E vs raw photo,
D vs E, D20 vs E, B vs D, B20 vs D20.

**Primary readings** (one verdict each per method): Δhist on MorDIFF (raw E7); Δflag-hist on MorDIFF; Δflag-small;
Δsmile on FRLL-Morphs AMSL; Δladder for E vs raw photo, D vs E and B vs D. Every other (effect, cell) pair is a
secondary reading with the same rule, printed in full.

**Agreement of one retrain with the release on one reading.** If the release's 95% interval excludes 0, the retrain
agrees when its point estimate has the same sign and at least half the release's size. If the release's interval
includes 0 (no effect), the retrain agrees when its own 95% interval includes 0.

**Verdict.** Let n_rep be the number of reproducing retrains. If n_rep ≥ 4: "a property of the method" if at least 4
reproducing retrains agree; "a property of the checkpoint" if at most 1 does; otherwise "mixed". If n_rep ≤ 3: "not
determined (n_rep of 5 retrains reproduce)", and the same rule applied to all five retrains is printed as a secondary
line, labelled. These words are the only verdict words used; nothing is said about other groups' work beyond them.

## Budget, stop rule

Athena, account `plgrestorearc-gpu-a100`. Up to 150 GPU-hours per method without asking the lead. Estimate from the
authors' logs: L about 5 GPU-hours per seed (8 GPUs x about 35 min), B about 1.5, F about 2, S about 8 to 10 (one GPU,
100 epochs), X about 3 to 5; total about 100 GPU-hours with scoring. The estimate from the measured smoke speed is
written to the README and result.md before each production array is submitted. One smoke job per method (at most 1
GPU-hour), after the command has run on 8 images on the DGX.

## Pre-run review

Not run (lead to decide).

## Amendment 1 (11 Nov 2026, 19:50 CET; from the independent pre-run review `experiments/reviews/PRERUN_AD5_20261111.md`; before any retrain exists and before any retrain score)

State when written: no retrain has finished; the MADation arrays are queued; no score of a retrain exists; the SelfMAD
release is being scored through the AD5 path on the DGX (file not opened).

1. **Headline and reproduction gate (review finding 1).** The verdict line computed over **all five seeds** is the
   headline for every reading. The reproduction gate becomes a label per seed and per cell: "reproduced" if the native
   EER is within W = max(1.5, 0.25 x published) of the published value (RS1's rule, unchanged), and, second window,
   "matches the release" if it is within W' = max(1.5, 0.25 x release EER) of the release's own native EER through
   the same AD5 path and crop variant. Two secondary verdict lines per reading: (a) on the seeds labelled
   "reproduced" on that reading's cell, (b) on the seeds labelled "matches the release" on that cell; each line gives
   its count k and uses the rule of the registration (at least 4 agreeing: method; at most 1: checkpoint; else
   mixed; with k <= 3: "not determined (k seeds)"). Printed per method and cell: "k of 5 retrains with the authors'
   code reproduce the published numbers" (k = seeds labelled "reproduced" on every published cell of the method, the
   cells on which the release itself is "not reproduced" excluded and listed). If fewer than five seeds finish, every
   verdict reads "incomplete (k seeds)" and only descriptive rows are printed. The registration's earlier gate-first
   verdict is replaced by this rule.
2. **Primary cells by a fixed rule (finding 5).** For each primary reading, the primary cell is the first cell of the
   list below whose release row is not labelled "our pipeline, published number not reproduced" in RS1 (variant 1);
   if every listed cell is so labelled, the first cell is used and the verdict carries that label.
   - history and history flag rate (raw E7 cells): MorDIFF, Greedy-DiM, DiM-A;
   - stored-small flag rate: uses the t5 of the native FRLL photos, which is the same for every FRLL-based cell; no
     cell choice;
   - smiling half (neutral-only minus all genuine EER): FRLL-Morphs AMSL, WebMorph, OpenCV, FaceMorpher, StyleGAN2,
     Greedy-DiM;
   - MorDIFF control-image contrasts: no cell (A43 images), always primary.
3. **Added readings (finding 5), each with the registered agreement rule:**
   - JPEG quality 50: flag rate at t5 of the existing JPEG-50 FRLL frames minus that of the aligned native frames
     (`Gjpeg50_frll` minus `Galn_frll`); and the same for the existing 50% shrink-and-enlarge frames (`Gresample50_frll`).
   - Each network's own 0.5 rule (probability of morph > 0.5; MADation / MixFaceNet `score_noTTA`, SelfMAD
     softmax[:, 1]): flag rates of native, history-matched (MorDIFF raw E7), stored-small (A43 E) and JPEG-50 genuine
     photos, the differences to native as readings; and the miss rate of every morph cell at the same rule, printed
     beside the flag rates (descriptive; no verdict).
4. **Training-loss fidelity check (improvement 1), no test data.** For MADation L and B, the training loss of every
   retrain (the authors' logger, every 50 steps, `training.log`) is printed against the complete 40-epoch runs in
   the authors' release logs (`/mnt/t7/smad_next/AD5/release_logs/vit{l14,b16}_madation/training.log`; ViT-B/16: runs
   2 to 4; ViT-L/14: runs 3 and 4, its run 2 stops at epoch 35; corrected 20:05 when the parser `src/AD5/ad5_loss.py`
   was first run on the authors' logs), per epoch (mean of the logged values) and at the last epoch; a retrain whose last-epoch mean loss lies outside
   [0.5 x min, 2 x max] of the authors' complete runs is flagged "loss outside the authors' range" beside its rows. No
   such logs exist for SelfMAD and MixFaceNet-MAD; their loss curves are printed without a reference.
5. **Checkpoints kept (finding 2).** MixFaceNet-MAD saves its weights after every epoch, SelfMAD every 5 epochs.
   Epoch 100 stays the only registered reading; other epochs are descriptive and are not scored without a further
   amendment. Neither an oracle-epoch row (best epoch on a benchmark) nor the authors' early-stopping rule on any test
   list is computed; whether such a labelled row may be printed is the author's decision.
6. **Scoring (finding 4).** MADation and MixFaceNet-MAD retrains and releases are scored on RS1's own crop files
   (RS1 amendments 3 and 4: crop variant 1 = the authors' SMDD script unchanged, primary; variant 2 = the corrected
   crop, secondary), reused by sha256 from RS1's Athena result tar, so that release and retrains, native and
   history-matched photos, come from one crop run on one machine. SelfMAD: release and retrains through RS1's
   `score.py --mode own` on the DGX (one platform for all six networks), with both genuine-class definitions
   (neutral-only and all photos; RS1 amendment 2c) for the reproduction label.
7. **Budget.** The lead set 250 GPU-hours for this experiment (11 Nov 19:20).

## Amendment 2 (11 Nov 2026, 19:58 CET; the author's approval of 19:41, relayed by the lead; before any SelfMAD score of this experiment is read)

State when written: no SelfMAD retrain exists (smoke job 3545882 running); the SelfMAD release is being scored through
the AD5 path on the DGX; that file has not been opened.

**Labelled oracle-epoch row for SelfMAD (diagnostic of the public code's default selection; not a result).**
1. Inputs: for each SelfMAD retrain, the weights saved every 5 epochs (epochs 5, 10, ..., 100; amendment 1 item 5).
2. Each saved epoch is scored through the same path as the registered rows (RS1's `score.py --mode own` on the DGX)
   on the FRLL cells only: the 204 raw FRLL photos and the five FRLL-Morphs families (raw files).
3. Oracle epoch of a retrain = the saved epoch with the lowest mean native EER over the five FRLL-Morphs cells, all
   204 genuine photos (the shipped `testset_best` takes the mean over FRGC, FERET and FRLL morph cells; only FRLL is
   held here); ties go to the earliest epoch.
4. Printed, per retrain, in one clearly labelled row beside its last-epoch row: the oracle epoch, its native EER on
   the five FRLL-Morphs cells and the mean, with the label "oracle epoch: selected on the FRLL test data, as the public
   code's default does; diagnostic only". If time allows, the oracle-epoch network is also scored on every RS1 image and
   its registered readings are printed in the same labelled block.
5. It is never a headline, never enters a verdict, a reproduction label or a count, and is never computed for any of
   our own networks. The registered reading stays the last epoch (epoch 100).

**Crop storage (the lead's ruling of 19:41 for RS1, which AD5 scores through):** MADation / MixFaceNet-MAD rows use
RS1's crop files by sha256 as the RS1 owner names them: primary = the authors' crop script run unchanged (with its
quirks), secondary = the corrected crop stored as PNG. Crops re-saved as JPEG by code written in this sprint are not
scored.

## Amendment 3 (11 Nov 2026, 20:20 CET; lead's message of 20:17; before any score of a retrain)

1. **End of the experiment stage.** The stage ends on 14 Nov 2026. A SelfMAD seed that has not reached epoch 100 by
   14 Nov 18:00 CET is reported as "incomplete (epoch e reached)"; its latest saved weights (every 5 epochs) may be
   scored only as a descriptive row labelled with that epoch, never in a verdict or a count. The same applies to any
   other arm whose seed has not finished by then. With fewer than five finished seeds the verdicts read
   "incomplete (k seeds)" (amendment 1, item 1).
2. **Allowance.** 300 A100-hours for this experiment (lead, 20:17). SelfMAD seed 405 is submitted (job 3545936).
3. The SelfMAD tasks exclude the slow node t0010 (lead's instruction); this changes no setting of the training.

## Amendment 4 (12 Nov 2026, 23:20 CET; lead's instruction after the author's go-ahead; before any retrain exists)

Athena will not start the arrays before the stage ends; the retrains move to WCSS (H100 80 GB, `lem-gpu-short`), in
the order MADation ViT-B/16, MixFaceNet-MAD, MADation ViT-L/14, then SelfMAD only if GPUs remain (at most 6 of our
GPUs at once across the sprint). Changes, all fixed now:
1. **Platform.** NVIDIA H100 (recorded per job). Python 3.9 (WCSS system Python; the MADation README's version), the
   same pinned packages as wheels for cp39, built in each job's local scratch.
2. **GPUs per MADation run.** The authors' global batch of 256 is kept: ViT-B/16 on 1 GPU at batch 256, ViT-L/14 on
   2 GPUs at 128 per GPU (authors: 8 x 32). The number of updates per epoch (155) and the 40-epoch schedule are
   unchanged; CLIP has no batch normalisation, so the split only changes how one step's 256 images are distributed
   over processes (and the DistributedSampler's shuffling across replicas). If a run does not fit, the next split is
   2 x 128 (B) or 4 x 64 (L).
3. **SMDD crops.** The crop pack made by the authors' script on Athena (job 3544216, sha256 3189e52a..., 39,723
   images) is reused unchanged.
4. **Everything else** (patches, seeds 401-405, last epoch, readings, gate, verdicts, amendments 1-3) is unchanged.
   Athena tasks stay queued until a WCSS copy of the same task is verified, then that Athena task is cancelled.

## Amendment 5 (13 Nov 2026, 08:35 CET; the author's ruling of 08:30, relayed by the lead; before any retrain score)

The retrains stay on WCSS and Athena and "arrive when they arrive"; no machine is rented for them and they no longer
gate the sealed final read. This replaces item 1 of amendment 3: there is no cut-off. Retrain rows that arrive after
14 Nov 18:00 are reported as late additions and read exactly as registered (same gate, readings, agreement rule and
verdicts; "incomplete (k seeds)" while fewer than five seeds of a method have finished). The SelfMAD array is
resubmitted after its test job passes; every array stays queued on both clusters, and a task's first verified copy
(either cluster) is the one read; the twin task on the other cluster is then cancelled.

## Amendment 6 (13 Nov 14:20, before any retrain score; no result read)

CUDA build for H100. The MADation pin torch 2.0.1 / torchvision 0.15.2 is kept. On WCSS H100 the CUDA 11.8 builds
(`+cu118`, download.pytorch.org) replace the PyPI CUDA 11.7 builds, which have no sm_90 code. Model code, hyper-parameters,
seeds and data are unchanged. Applies to MADation ViT-B/16, ViT-L/14 and MixFaceNet-MAD on WCSS (all five seeds of each
method on this one platform). The Athena A100 MixFaceNet-MAD seed 401 (cu117) stays a descriptive cross-platform check.
