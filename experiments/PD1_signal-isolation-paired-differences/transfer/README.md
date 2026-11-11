# Signal isolation by paired differences (PD1), cross-family transfer: full record

Owner of the cross-family step of the workflow "signal isolation by paired differences (PD1)". Standard:
`DOCUMENTATION.md`. Short verdict: `result.md`. Registration: `prereg.md` (with amendment 1).

## 1. Question and current answer

11 Nov 2026, 21:15 CET: running. Question: is there one mixing direction shared by the landmark, diffusion-autoencoder
and GAN families, and does a head trained on one-person images of two families detect two-person morphs of the third?
Answer: see `result.md` once written.

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
- 21:15 Full analyses of CLIP pooled and CLIP mean patch started (`run_analysis.sh`).

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
  output `/mnt/t7/smad_next/PD1/transfer/res/<feature>.json`.

Environment: `/home/narolski/mambamorph-code/.venv-spark/bin/python -I` (timm 1.0.27; CLIP OpenAI ViT-L/14 checkpoint
`models--timm--vit_large_patch14_clip_224.openai/.../pytorch_model.bin`; DINOv3 `vit_large_patch16_dinov3.lvd1689m`),
TF32 on, 2 threads, `nice -n 10`. Seeds: bootstrap and splits 20261111; GAN in-family folds 401.

## 5. Results

Pending.

## 6. Checks

- Common-space check (8 images per cache): GAN CLIP max |difference| 1e-5 (pooled) and 0 (patch), GAN DINOv3 4e-4,
  diffusion DINOv3 8e-4, diffusion CLIP 0.0031 / 0.0016 (minimum cosine 0.9999996; TF32 off in that cache), hence
  amendment 1. Files `/mnt/t7/smad_next/PD1/transfer/feats/check_common_space_{clip,dinov3}.json`.

## 7. Dead ends and failures

- None so far.

## 8. Observations and ideas

- Pending.

## 9. Open items and next steps

- Pending.

## 10. Handover state

- 21:15: DINOv3 extraction running (background shell, log above); CLIP analyses running (two processes).

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
```
