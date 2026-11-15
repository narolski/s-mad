# Signal isolation by paired differences (PD1), cross-family transfer: full record

Owner of the cross-family step of the workflow "signal isolation by paired differences (PD1)". Standard:
`DOCUMENTATION.md`. Short verdict: `result.md`. Registration: `prereg.md` (with amendment 1).

## 1. Question and current answer

11 Nov 2026, 21:21 CET: finished, not reviewed. Question: is there one mixing direction shared by the landmark,
diffusion-autoencoder and GAN families, and does a head trained on one-person images of two families detect two-person
morphs of the third? Answer (registered readings): no shared mixing direction (cross-fitted cosines landmark-diffusion
0.15 to 0.44, landmark-GAN -0.15 to -0.04, diffusion-GAN -0.45 to -0.27); leave-one-family-out fails for all three
held-out families on all three features (one-person head 0.30 to 0.68 against floors 0.60 to 0.89; two-person heads
fail too); plain answer "no". Largest threat: family is confounded with frame, resolution and photo source, and each
family's one-person signal is a verified pipeline artefact. Details: `result.md`.

## 2. Timeline (machine clock)

- 20:56 Read the owner brief, notebook, plans, class definitions, asset inventory, the three family results and the
  verifications handed over by the workflow; inspected feature-extraction code and caches of the three families.
- 21:00 to 21:05 Counted person overlaps between the pools (landmark-diffusion 152, landmark-GAN 80, diffusion-GAN 100
  persons) and the purged training sizes; wrote `prereg.md`.
- 21:05 to 21:07 Wrote `src/PD1/transfer/tf_items.py`, `tf_feats.py`; 8-image tests: list builder; cache check
  (`--check`) for CLIP and DINOv3; extraction of 8 landmark images for each backbone.
- 21:07 Amendment 1: the diffusion CLIP cache (TF32 off) differs from the common code by up to 0.0031 (bound 1e-3), so
  diffusion images are re-extracted with the common code. List extended (sets Dtr, Dev, Df256).
- 21:07:56 Full extraction started (`run_feats.sh`): CLIP done 21:13 (9,140 images, peak 1.72 GB), DINOv3 started 21:13:33.
- 21:14 Analysis code-path test (`tf_analysis.py --feat clip_pool --quick`: B 50, 10 splits, no C range, no
  sensitivity; 7.5 s). Its numbers are a code-path test, superseded by the full run; they were seen before the full run.
- 21:15 Full analyses of CLIP pooled and CLIP mean patch started (`run_analysis.sh`); each took about 25 s.
- 21:16 Amendment 2 registered (post hoc, after the CLIP results): pairwise single-family transfer and probes of the
  mean-direction heads (`tf_posthoc.py`). DINOv3 extraction finished 21:16:54; DINOv3 analysis and the three post hoc
  runs followed (each under 30 s).
- 21:18 `tf_summary.py` wrote the tables and `readings.json`; 21:19 to 21:21 `result.md` written and checked against
  the tables.

## 3. Data

See `prereg.md` (Data). Lists: `/mnt/t7/smad_next/PD1/transfer/lists/landmark_items.csv` (9,140 rows: landmark ladder
2,680, landmark flag sets 816, landmark hosts' softened photos 400, blanked x1 and x3 2,144, matched-geometry warp-only
536, diffusion training 1,548, diffusion flag set 408, FRLL diffusion renders 608). GAN images come from the GAN
family's caches (sets G, Hr, S, Fm). Persons: real FERET / FRGC subject ids.

## 4. Code (`/home/narolski/smad-next/src/PD1/transfer/`)

- `tf_items.py`: builds the image list (read-only sources; asserts files exist and no sealed token in any path).
- `tf_feats.py`: frozen features in the common space; imports `build()` and `extract()` of
  `src/PD1/gan/pd1_feats.py` unchanged; `--check` compares 8 diffusion and 8 GAN images with their caches.
- `run_feats.sh`: sequential extraction (CLIP then DINOv3), log `/mnt/t7/smad_next/PD1/transfer/logs/feats.log`.
- `tf_lib.py`: host tables, reference sets, AUC, pigeonhole person bootstrap, flag rate, family-balanced paired heads.
- `tf_analysis.py`: (1) cosines, (2) leave one family out, in-family reference, sensitivity, readings.
- `run_analysis.sh`: full analysis per feature; logs `/mnt/t7/smad_next/PD1/transfer/logs/analysis_<feature>.log`;
  output `/mnt/t7/smad_next/PD1/transfer/res/<feature>.json` (`clip_pool_quick.json` = the code-path test).
- `tf_posthoc.py`: amendment 2 (pairwise single-family transfer, mean-direction probes) -> `res/<feature>_posthoc.json`.
- `tf_summary.py`: CSV tables and `readings.json` in this folder.

Environment: `/home/narolski/mambamorph-code/.venv-spark/bin/python -I` (timm 1.0.27; CLIP OpenAI ViT-L/14 checkpoint
`models--timm--vit_large_patch14_clip_224.openai/.../pytorch_model.bin`; DINOv3 `vit_large_patch16_dinov3.lvd1689m`),
TF32 on, 2 threads, `nice -n 10`. Seeds: bootstrap and splits 20261111; GAN in-family folds 401.

## 5. Results

All numbers with intervals are in `result.md` and the tables beside it: `cosines.csv` (1,140 rows: every pair of
directions, both spaces, three features; cross-fitted cosine, split range, disattenuated, full-data cosine,
reliabilities), `lofo.csv` (36 rows: held-out family x head x feature; AUC, CI, floor, excess, paired share, flag rates,
C and C range, reading), `infamily.csv` (18 rows), `sensitivity.csv` (81 rows), `probes.csv` (144 rows),
`pairwise_posthoc.csv` (72 rows), `readings.json`. Raw JSON per feature: `/mnt/t7/smad_next/PD1/transfer/res/`.
Item counts behind the main AUCs: landmark 536 x1 and 536 x3 images (536 persons); diffusion 516 x1 and 258 x3 (258
persons); GAN 256 x1 and 128 x3 (128 persons).

## 6. Checks

- In-family reference reproduces the families' own out-of-fold numbers where the features coincide (diffusion
  0.949 / 0.877 / 0.913 against 0.948 / 0.877 / 0.913; GAN 0.814 / 0.784 / 0.785 against 0.80 / 0.80 / 0.78), so the
  pipeline (tables, heads, bootstrap) is sound; the transfer failure is not a code artefact.
- Person purge asserted in code (no person of the held-out family in any training image); no FRLL person in any fit
  (asserted); no sealed token in any path (asserted in the list builder and the extractor).
- Code-path test (`--quick`) run before the full analysis with the same code; head point estimates identical.
- Not verified: no independent sceptic has re-run this; the GAN family itself has no delivered verification.
- Common-space check (8 images per cache): GAN CLIP max |difference| 1e-5 (pooled) and 0 (patch), GAN DINOv3 4e-4,
  diffusion DINOv3 8e-4, diffusion CLIP 0.0031 / 0.0016 (minimum cosine 0.9999996; TF32 off in that cache), hence
  amendment 1. Files `/mnt/t7/smad_next/PD1/transfer/feats/check_common_space_{clip,dinov3}.json`.

## 7. Dead ends and failures

- The registered cache check failed for the diffusion CLIP cache (TF32 off there): handled by re-extraction
  (amendment 1), no number used the failing cache.
- Two timestamps in the first draft of `prereg.md` were estimates ahead of the machine clock (written as 21:33 and
  21:24); corrected to the machine clock (21:07, 21:16) before any result was written.
- The FRLL decoding-step pairing first keyed reconstructions by person (two photos per person collide); fixed to the
  photo key before the first run (assert on 204 per arm).

## 8. Observations and ideas

- The GAN one-person mixing direction is aligned with the GAN latent-spread direction (0.56 to 0.73) and opposed to
  the diffusion mixing direction (-0.27 to -0.45); heads trained on landmark and diffusion score GAN renders whose
  latent is nearer the mean LOWER (set H x1 vs x1s 0.25 to 0.43).
- The GAN pipeline step (camera photo to render) aligns with landmark mixing (0.32 to 0.59): "rendered by a generator"
  looks like "blended" in frozen features; the transferred heads separate GAN renders from camera photos at 0.95.
- Diffusion and GAN reconstruction share a pipeline direction in CLIP pooled (0.59).
- The only transferring cell (post hoc: diffusion mean mixing direction to landmark, 0.976 CLIP pooled) reads the
  landmark surround (surround only 0.95, face only 0.54), like the landmark verifier's in-family finding.
- With the inner leave-one-family-out, C is chosen from two families whose own transfer is opposed (diffusion vs GAN
  inner criterion 0.19 to 0.26 when landmark is held out); this is why the smallest C does better for landmark held
  out (0.78 / 0.81), still below the floor.

## 9. Open items and next steps

- Independent review of this cross-family step.
- What would settle the frame confound: run the three pipelines on the same host photos in one frame (for example the
  landmark ladder's hosts through DiffAE and StyleGAN3 inversion at one resolution), surround blanked, and repeat the
  leave-one-family-out; needs new generation (author's yes).
- Face-only (surround blanked) cross-family test once blanked copies exist for diffusion and GAN images in a common
  frame (the diffusion verifier's blanked CLIP features exist; GAN has none).

## 10. Handover state

- 21:21: nothing running. No queued tasks. Compute: about 9 GPU-minutes on the DGX GB10 (peak 1.72 GB), about 3
  CPU-minutes; 0 USD. Disk: 138 MB under `/mnt/t7/smad_next/PD1/transfer/` (58 GB free on the drive).

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next/src/PD1/transfer
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 HF_HUB_OFFLINE=1
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
nice -n 10 $PY -I tf_items.py
nice -n 10 $PY -I tf_feats.py --backbone clip --check
nice -n 10 $PY -I tf_feats.py --backbone dinov3 --check
./run_feats.sh
./run_analysis.sh clip_pool clip_patch dino_pool
for f in clip_pool clip_patch dino_pool; do nice -n 10 $PY -I tf_posthoc.py --feat $f; done
nice -n 10 $PY -I tf_summary.py
```
