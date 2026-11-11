# Identity-shrinkage triage: how average is a morph, and what is the ceiling [ID0] — full record

Owner: ID0 hypothesis owner (agent). Started 11 Nov 2026 about 15:30 CET. This README follows
`/home/narolski/smad-next/DOCUMENTATION.md`. Dated lines are added below; history is not rewritten.
Short verdict: `result.md` (same folder). Pre-registration: `prereg.md` (sha256 3ee8588b…, written before any
statistic, committed by the lead in 5a19286).

Terms. AUC = area under the ROC curve (0.5 = chance; the second-named group is the positive class). ISS =
identity-subspace shrinkage score (defined in section 4). FR = face recognition. glintr100 = ArcFace ResNet-100
trained on Glint360K (FR network). CLIP = OpenAI CLIP ViT-L/14 image tower. DINOv3 = Meta DINOv3 ViT-L/16.
DiffAE = diffusion autoencoder (FFHQ-256 checkpoint); z_sem = its 512-d semantic code. E7 = the existing control
that gives genuine photos the morphs' shrink-and-enlarge history. Rungs (AR1 ladder): R0 photo, R2 tool on one
photo, R2w warp-only, R3 same-person morph, R3m mirror self-morph, R4 two-person morph, NC = tool(S, H).

---------------------------------------------------------------------------------------------------------

## 1. Question and current answer

Question: a morph averages two faces, so in a space where identity is roughly linear it should sit closer to the
average face than a real person (identity variance falls to (1+c)/2 for contributor similarity c). Is that
measurable from one image for landmark, GAN and diffusion morphs, with a statistic fitted on genuine photos only,
and what are the predicted and observed ceilings?

Status 11 Nov 17:31 CET: **running**. Landmark arm finished; CLIP and DiffAE arms finished on the tier-1 sets;
DINOv3 being recomputed (first run produced non-finite features, section 7); glintr100 (FR) features for the
remaining sets being computed (CPU-bound face detection); FR arm with the GEO-0 reads not yet analysed.

Current answer (facts so far, no verdict yet):
- Exact landmark shapes (no image): two-person mean shape vs host shape AUC 0.725 [0.689, 0.758] on 520 AR1
  hosts; warp-only/same-person mean shape vs two-person 0.687 [0.650, 0.720]; dose rises monotonically
  (Page p ≈ 4e-234). The arm's kill line (R0 vs R4 < 0.60) is not reached.
- CLIP ViT-L/14: landmark morphs score *less* average than photos (AR1 OpenCV R0 vs R4 0.391); MorDIFF 20-step
  reconstruction vs two-person morph 0.698 [0.616, 0.775] but same-person mix vs two-person morph 0.419; the
  native-vs-E7 MorDIFF control is 0.582 [0.543, 0.621] (outside 0.45–0.55): the arm reads history.
- DiffAE z_sem: AR1 OpenCV R2w vs R4 0.692 [0.657, 0.729]; dose monotone (p ≈ 9e-99); MorDIFF on DiffAE-native
  256 frames D20 vs B20 0.688 [0.626, 0.749], C20 vs B20 0.747 [0.685, 0.807]; but the native-vs-E7 MorDIFF
  control is 0.000 (complete separation), so the arm reads history on that family.
- The physics closed form overshoots wherever the identity space is high-dimensional (CLIP, DiffAE: predicted
  0.99 at c = 0 against observed ≤ 0.70) and the pre-registered per-pair c estimator breaks on pool offsets
  (c > 1). Details in sections 5 and 7.

## 2. Timeline

- 15:30 Read OWNER_BRIEF.md, NOTEBOOK.md, 11_AUDIT_PLAN.md, 10_ASSET_INVENTORY.md, 12_STATE_AT_HANDOVER.md,
  ideas/CONSOLIDATED_v1.md (K6), ROUND1_raw.json physics idea 0 + first_experiment_tonight, identity GEO-0 +
  ideas 0 and 1, AR1 prereg/pool/gate_b, AG5 result.
- 15:35 Counted candidate fit persons (AR1 `pool.candidates()`, imported unchanged): 1,399 persons, 95 of them
  `is_val`; outside the AR1 pool and not `is_val`: 776 persons, 1,720 photos, only 47 with ≥ 2 sessions. Verified
  the `is_val` key against `train.csv` (230/230 FERET, 197/197 FRGC val rows match). Found 8 AR1 hosts that are
  `is_val` (AR1 does not filter them; reported, not touched).
- 15:45 Wrote `prereg.md` (before any feature or statistic).
- 15:42–15:55 `lists.py` → `fit.csv` (1,395 photos after the duplicate rule), `items.csv` (20,186 items),
  `lists_summary.json`. Fixed the DiffAE photo input to `a41diffae/a256/png256` (the encoder's input) before use.
- 15:43 First 8-image test of `feat.py`: CUDA out-of-memory on model load (shared GB10). Changed load order to
  `.half().to(dev)` and added `run_feat.sh` (5 retries, log files).
- 15:50 Landmark arm smoke run (B = 200) to /mnt/t7/smad_next/ID0/test: worked; 13 min because of BLAS
  thread contention; reran with OMP/OPENBLAS threads = 2: 4.5 min.
- 15:55–16:08 8-image tests passed for DiffAE encoder and spark features (glint + CLIP + DINOv3).
- 16:05 Landmark arm full run (B = 2,000) → `arm_landmark.json`, `contrasts_landmark.csv`.
- 16:06–16:21 First full feature runs in items.csv order: far too slow (1.4–3 img/s) and the decisive sets came
  last; killed (only one glint part, items 0–511 = fit photos, was kept; its order was verified identical to the
  later order).
- 16:20 `bench_sim.py` → `bench_similarity.json`.
- 16:22 Added tier ordering (`id0_common.tier`, `ordered`), partial-safe merges, part files per 256/512 items,
  DataLoader workers for DiffAE; re-tested both extractors on 8 images (16:30 OK).
- 16:30 Launched DiffAE (all tiers), CLIP+DINOv3 (all tiers), glint (subset without existing embeddings).
- 16:35 Glint detection runs on CPU at about 1 img/s: added `glint_rank` (fit, A43, AR1 OpenCV R2w/R3m,
  StyleGAN3, primary E7, graded) and restarted; paused it to embed the 1,200 H3 CASIA crops (`h3crops.py`).
- 16:58 DiffAE reached the end of tier 1 (21 parts, 10,752 rows): stopped, merged. Glint split into 3 shards
  (`--shard i/3`).
- 17:12 CLIP+DINOv3 reached the end of tier 1 (19 parts, 9,728 rows): stopped, merged.
- 17:13 Analyses for DiffAE, CLIP, DINOv3 started. DINOv3 crashed: every DINOv3 feature is non-finite (fp16
  overflow). CLIP and DiffAE finished (`arm_clip.json`, `arm_diffae.json`).
- 17:20 Added `--dtype` (fp16/bf16/fp32) and a non-finite check that refuses to save a part; DINOv3 bf16
  8-image test finite (17:22); full DINOv3 tier-1 run launched 17:28 (tag `dn`).
- 17:30 Author's documentation instruction received; this README written.

Amendments to the registration (all after the prereg, none after reading a decisive number unless stated):
1. Feature sets reduced to "tier 1" for CLIP, DINOv3 and DiffAE (throughput on the shared machine); tier 1 holds
   every set the fixed falsifiers need (fit, AR1 OpenCV R0/S/R2w/R3/R3m/R4, A43 E/D20/C20/B20/A, DiffAE-native
   a256/D20/C20/B20, StyleGAN3 three sets, FRLL native + four primary E7 families, graded set). FaceMorpher
   rungs, R2/NC, A43 B/C/D (100 steps), FRLL AR1 pool, published FRLL-Morphs frames and the descriptive E7
   families are missing in these three arms (partly present: the first 432–118 items of tier 2).
2. DINOv3 precision changed from fp16 to bf16 after fp16 gave non-finite output (before any DINOv3 statistic).
3. Added (descriptive, genuine-only): a 5-fold virtual-midpoint check per arm (`virtual_in_domain`).
4. The pre-registered per-pair similarity estimator c_pair is reported but fails (values > 1, section 7); a
   pool-centred variant is planned as a descriptive replacement (not yet computed).

## 3. Data

Inputs (read only):
- AR1 pool and builds: `/home/narolski/smad-next/experiments/AR1/pool.csv` (536 hosts), `/mnt/t7/smad_next/AR1/
  pool_m.csv`, `pool_frll_m.csv`, `manifest.csv`, `src/` (frames + 106-point `.tem`), `mirror/`, `img/frgcferet/
  {opencv,facemorpher}/{R2,R2w,R3,R3m,R4,NC}` (536 each), `img/frgcferet/fm_graded/m000…m050` (300 each),
  `img/frll/…` (102 each), `frll_src/` (204 FRLL frames + `.tem`). Existing glintr100: `pool_src_emb.npz`
  (1,606), `frll_src_emb.npz` (204), `fr_emb_built.npz` (3,828: R3, R4, NC both tools and pools).
- Fit candidates: AR1 `src/AR1/pool.py: candidates()` over `/home/narolski/mambamorph-code/smadcvpr_data/
  {train/bona_frgc, arms/r6_frgc → /dev/shm/smad_arms/r6_frgc, train/bona_feret}` (read in place; not copied —
  see section 9: the /dev/shm frames are volatile).
- A43 MorDIFF control set: `/mnt/t7/smad_heldout/a43/data/a43/stored/{A,B,B20,C,C20,D,D20,E}` (200/200/200/102/
  102/204/204/204), generated DiffAE frames `/mnt/t7/smad_heldout/a43/gen/{B,B20,C20,D20}/png256` and the X3
  inputs `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256` (204).
- a46 features: `/mnt/t7/smad_heldout/a46/feat/a46_feat.npz` (5,146 keys; glintr100 `emb`, CLIP `clip`).
- StyleGAN3: `/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv` (h3_sg3 orig 423, h3_bona orig 423),
  `/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv` (orig 423), contributor crops
  `/mnt/t7/smad_heldout/h3_sg3/work/h3_inputs.npz` (1,200 × 112² RGB).
- FRLL native and E7 frames: `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` rows
  frllm/frll_bona/0/orig and `resmatch` of opencv, facemorpher, stylegan (frllm), mordiff, dim_c, greedy_dim,
  greedy_dim_s, amsl, webmorph (204 each). The old MAD22 rows of eval.csv are not used.
- Benchmark pair names: FRLL-Morphs `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/morph_*`, corrected
  MAD22 directory listing `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/
  original_sorted/<family>` (names only, no image read).

Produced (all under `/mnt/t7/smad_next/ID0/`):
- `fit.csv` sha256 e52de0c3…a340: 1,395 photos, 776 persons (FERET 710, FRGC 66), 325 within-person duplicates
  dropped, 87 `is_val` persons excluded, 471 persons with ≥ 2 photos (619 within dof), 47 with ≥ 2 sessions.
- `items.csv` sha256 558004f4…2fee: 20,186 evaluation items (group counts in `lists_summary.json`).
- `feat/diffae.npz` sha256 8e2eee43…92 (10,752 rows, tier 1 + start of tier 2), `feat/clip_cd.npz` sha256
  0ddf8bf7…7a (9,728 rows), `feat/dino_cd.npz` (9,728 rows, all non-finite: unusable, kept as evidence),
  `feat/h3crops_glint.npz` sha256 30aed8fa…7d (1,200), `feat/glint_gl.npz` (in progress), `feat/dino_dn.npz`
  (in progress), part files `feat/part*_*.npz`, logs `logs/*.log`, landmark smoke output `test/`.
- Small results in this folder: `lists_summary.json`, `bench_similarity.json`, `arm_landmark.json`,
  `contrasts_landmark.csv`, `arm_clip.json`, `contrasts_clip.csv`, `arm_diffae.json`, `contrasts_diffae.csv`.
- Dropped items: every AR1 item whose host or partner is `is_val` (AR1 primary pool: 520 R4 hosts of 536; 528
  single-person items); glint items without a detected face are excluded (count printed per arm).

## 4. Code (`/home/narolski/smad-next/src/ID0/`, sha256 at 17:30 in brackets)

Run order: `lists.py` → `feat.py` / `feat_diffae.py` / `h3crops.py` (via `run_feat.sh`) → `bench_sim.py` →
`analyse.py --arm …` → `summarize.py`, `verdicts.py`.
- `id0_common.py` (fdff884d…): paths, `is_val`, `forbidden`, `read_tem`, tier order (`tier`, `ordered`,
  `glint_rank`), `existing_glint()` (maps AR1 and a46 glintr100 embeddings onto item keys by path / photo).
- `lists.py` (4f9eec6c…): fit and item lists.
- `feat.py` (1adfc976…): glintr100 (AR1 `fr.py` unchanged: pinned prep_eval.kps → norm_crop → a2f_common
  'glint'), CLIP and DINOv3 via timm (offline cache, eval, `--dtype`), parts per chunk, `--shard i/n`,
  `--merge-only`, `--max-tier`. Refuses to save non-finite parts.
- `feat_diffae.py` (e005f763…): DiffAE z_sem = `ema_model.encoder(x)` (= LitModel.encode), pinned repo commit
  00c57d3f and checkpoint sha 9bd2ba9e…, repository's own ImageDataset transform; parts, `--merge-only`.
- `h3crops.py` (c79d70f5…): glintr100 of the H3 CASIA crops (RGB → BGR, as h3_finalise.py does).
- `iss.py` (e0cf053f…): the statistic. PCA (95% variance, at most 64 components), pooled within-person S_w
  (ridge 1e-3·tr/k), S_b = cov(person means) − mean(1/n_p)·S_w, generalised eigenproblem S_b v = λ S_w v.
  ISS = −Σ_{λ>1} w z², w = 1/(λ/2+1) − 1/(λ+1); TYP = −Σ z²/(λ+1); SES = −Σ_{λ≤1} z²/(λ+1). Predictions:
  physics closed form Φ(√(d/2)(1−s)/√(1+s²)), s = ((1+c)/2+n)/(1+n), d = #{λ>1}, n = d/Σλ_J; spectrum
  simulation (100,000 draws in the result tables).
- `analyse.py` (bdab8075…): every read per arm (contrasts with two-way person bootstrap through AR1's
  `stats.py` = a41_read.Draw + a36_read.wauc, B = 2,000, seed [20261111, 1]; Page trend test; shrink law with
  weighted Spearman; fidelity; c_pair; virtual check; GEO-0 for glint: Λ, ceiling table, gain, virtual head,
  oracle power check).
- `bench_sim.py` (a6af68b5…), `summarize.py` (4f41511d…), `verdicts.py` (24f7ccc5…), `run_feat.sh` (27a540cb…).

Environment: DGX GB10 (ARM). Spark venv `/home/narolski/mambamorph-code/.venv-spark/bin/python` (Python 3.12.3,
numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0, torch 2.12.1+cu130, timm 1.0.27, opencv 4.11.0, insightface
1.0.1); DiffAE venv `/mnt/t7/thirdparty/diffae_venv/bin/python` (Python 3.12.3, torch 2.12.1+cu130). Weights:
CLIP `timm/vit_large_patch14_clip_224.openai` (HF cache blob eb70c15b…), DINOv3
`timm/vit_large_patch16_dinov3.lvd1689m` (blob 45172f20…), glintr100 `~/.insightface/models/antelopev2/
glintr100.onnx` (sha256 4ab1d643…), DiffAE `/mnt/t7/thirdparty/diffae_00c57d3f…/checkpoints_download/
ffhq256_autoenc/last.ckpt` (9bd2ba9e…). Seeds: lists 20261111 (AR1 rule), bootstrap [20261111, 1], virtual
pairs 20261111, spectrum 20261111.

## 5. Results (so far)

### Benchmark pair similarity (glintr100 cosine of the two contributors' photos) — `bench_similarity.json`
| Set | n | median [10%, 90%] |
|---|---|---|
| FRLL-Morphs (opencv, facemorpher, webmorph, stylegan; amsl 2,175) | 1,221–1,222 | 0.037 [−0.066, 0.144] |
| corrected MAD22 (all five families) | 500–1,000 | 0.114 [0.048, 0.188] |
| published MorDIFF | 1,000 | 0.114 [0.048, 0.188] |
| DiM-C / Greedy-DiM / Greedy-DiM-S | 500 | 0.116 [0.053, 0.190] |
| AR1 pool, two-person (look-alike assignment) | 536 | 0.234 [0.163, 0.310] |
| AR1 pool, same-person | 536 | 0.868 [0.804, 0.918] |
H3 StyleGAN3 pairs: to be added when the glint arm runs (crops embedded).

### Landmark arm (exact shapes) — `arm_landmark.json`
See `result.md` (final table). Fit k = 11, d = 10, n = 0.175; ceiling (closed / spectrum): c=0 0.795/0.781,
0.3 0.707/0.689, 0.5 0.646/0.630, 0.7 0.585/0.574. Virtual check 0.834. AR1 (520 hosts): R0 vs R4 0.725
[0.689, 0.758]; R3 (= R2w shape) vs R4 0.687 [0.650, 0.720]; R3m vs R4 0.651 [0.614, 0.687]; R0 vs R3 0.548
[0.536, 0.559]; R0 vs R3m 0.572 [0.565, 0.581]; TYP R0 vs R4 0.746 [0.711, 0.779]. Dose AUC vs m = 0:
0.574/0.637/0.685/0.714/0.724, Page p 4e-234. FRLL AR1 pool R0 vs R4 0.797 [0.721, 0.869]. Benchmark pair
means: FRLL-Morphs 0.731–0.737, MAD22 0.736–0.758. Shrink law ρ: AR1 R4 +0.083 [−0.085, 0.236], FRLL-Morphs
pairs −0.064 [−0.179, 0.061].

### CLIP ViT-L/14 (tier 1) — `arm_clip.json`
Fit k = 64 (of 230 for 95%; 81% variance), d = 57, n = 0.034; closed-form ceiling 0.989 at c = 0, 0.848 at 0.5.
Virtual check 0.965.
| Contrast | ISS | TYP |
|---|---|---|
| AR1 OpenCV R0 vs R4 (528/520) | 0.391 [0.350, 0.431] | 0.209 |
| AR1 OpenCV R2w vs R4 | 0.364 [0.323, 0.404] | 0.193 |
| AR1 OpenCV R3 vs R4 | 0.362 [0.323, 0.402] | 0.259 |
| AR1 OpenCV R3m vs R4 | 0.558 [0.511, 0.603] | 0.539 |
| AR1 OpenCV R0 vs R2w | 0.528 [0.524, 0.533] | 0.526 |
| MorDIFF stored E vs B20 (204/200) | 0.635 [0.555, 0.714] | 0.644 |
| MorDIFF stored D20 vs B20 | 0.698 [0.616, 0.775] | 0.667 |
| MorDIFF stored C20 vs B20 (102/200) | 0.419 [0.343, 0.498] | 0.455 |
| MorDIFF stored D20 vs C20 | 0.756 [0.716, 0.803] | 0.703 |
| MorDIFF stored E vs D20 | 0.465 [0.422, 0.508] | 0.505 |
| MorDIFF stored E vs A (published) | 0.633 [0.552, 0.713] | 0.641 |
| StyleGAN3 h3_bona vs h3_sg3 (423/423) | 0.542 [0.511, 0.572] | 0.583 |
| StyleGAN3 a37spread vs h3_sg3 | 0.534 [0.506, 0.560] | 0.565 |
| a46 CLIP (fp32, raw files): rec vs published MorDIFF (204/1,000) | 0.619 [0.562, 0.680] | 0.519 |
| a46: rec vs DiM-C / Greedy-DiM | 0.514 / 0.519 | |
| a46: a256 vs rec (negative control) | 0.521 [0.505, 0.540] | |
Controls native vs E7 (ISS): opencv 0.531 [0.527, 0.539], facemorpher 0.526, stylegan 0.500 [0.500, 0.500]
(identical frames, see 7), mordiff 0.582 [0.543, 0.621] (TYP 0.377): outside 0.45–0.55. Dose (294 hosts):
Page p = 1.0, mean ISS falls with m (AUC vs m0: 0.530, 0.517, 0.439, 0.387, 0.362). Shrink law ρ: AR1 R4
−0.149 [−0.310, 0.023]; graded pooled −0.280 [−0.374, −0.180]; A43 B20 +0.034 [−0.205, 0.270]; published
MorDIFF −0.063 [−0.186, 0.068]. Midpoint fidelity (centred cosine to the contributors' feature midpoint, median):
R4 0.564 (host 0.480), B20 0.690 (host 0.598), D20 0.783.

### DiffAE z_sem (tier 1) — `arm_diffae.json`
Fit k = 64 (of 144; 85%), d = 58, n = 0.056; closed-form ceiling 0.988 at c = 0, 0.845 at 0.5. Virtual 0.982.
| Contrast | ISS | TYP |
|---|---|---|
| AR1 OpenCV R0 vs R4 | 0.695 [0.659, 0.732] | 0.690 |
| AR1 OpenCV R2w vs R4 | 0.692 [0.657, 0.729] | 0.686 |
| AR1 OpenCV R3 vs R4 | 0.676 [0.637, 0.715] | 0.669 |
| AR1 OpenCV R3m vs R4 | 0.807 [0.772, 0.840] | 0.805 |
| AR1 OpenCV R0 vs R2w | 0.506 [0.503, 0.510] | |
| MorDIFF DiffAE-native a256 vs B20 | 0.687 [0.612, 0.757] | 0.706 |
| MorDIFF DiffAE-native D20 vs B20 | 0.688 [0.626, 0.749] | 0.651 |
| MorDIFF DiffAE-native C20 vs B20 | 0.747 [0.685, 0.807] | 0.753 |
| MorDIFF DiffAE-native D20 vs C20 | 0.445 [0.414, 0.475] | 0.404 |
| MorDIFF DiffAE-native a256 vs D20 | 0.497 [0.466, 0.530] | 0.551 |
| MorDIFF stored (small crops, resized by the encoder) E vs B20 / D20 vs B20 / E vs A | 0.324 / 0.462 / 0.312 | |
| StyleGAN3 h3_bona vs h3_sg3 | 0.597 [0.568, 0.627] | 0.606 |
| StyleGAN3 a37spread vs h3_sg3 | 0.503 [0.476, 0.531] | 0.513 |
Controls native vs E7: opencv 0.515 [0.510, 0.523], facemorpher 0.514, stylegan 0.500 (identical frames),
mordiff 0.000 [0.000, 0.000] (complete separation). Dose (294 hosts): Page p 9e-99, monotone; AUC vs m0 0.585 /
0.650 / 0.691 / 0.714 / 0.720. Shrink law ρ: AR1 R4 +0.098 [−0.076, 0.261]; graded pooled +0.195 [0.104, 0.283];
A43 B20 +0.083 [−0.173, 0.315]; DiffAE-native B20 +0.028 [−0.240, 0.282]. Cycle read (centred cosine of
Enc(image) to the midpoint of Enc(a256 sources), median): B20 0.821 (to host alone 0.767), C20 0.822, D20 (to
its own source) 0.846; on the 512 AR1 frames R4 0.940 (host 0.863).

### FR (glintr100) arm and GEO-0, DINOv3 arm
Pending (section 10).

## 6. Checks

Verified: `is_val` key against the train.csv `val` column; the kept glint part (items 0–511) has the same key
order in the old and the new item order (checked programmatically); 8-image tests of every extractor command;
CLIP feature norms (median 33.0) match a46's CLIP norms (33.0–33.3); DiffAE and CLIP features finite; DiffAE
load: 0 missing / 0 unexpected keys; NC vs R3 and rec vs a256 negative controls are in the tables.
Not verified: whether `Enc(Dec(lerp(z_A, z_B)))` returns `lerp(z_A, z_B)` in the generator's own run (the a43
codes were not saved; my Enc(a256) equals the generation's encode only if the same precision path was used:
not checked); fp16 CLIP vs fp32 a46 CLIP equivalence on identical files (not compared); whether FRLL-Morphs
self-pairs (061_061 …) are intended.

## 7. Dead ends and failures

- **DINOv3 in fp16 gives non-finite features for every image** (`feat/dino_cd.npz`, 9,728 rows); the analysis
  crashed with "SVD did not converge". Fix: `--dtype bf16`, 8-image test finite (norms about 7), and `feat.py`
  now refuses to save a non-finite part. The fp16 smoke test at 16:08 did not check finiteness (lesson).
- **First full feature runs (16:06–16:21) too slow and in the wrong order** (decisive sets last); killed. Cause:
  the GB10 GPU is time-shared by about 12 processes (95% utilisation by others) and the CPU load average was
  70–145; glint face detection (prep_eval.kps, insightface on CPUExecutionProvider) runs at about 1 img/s.
  Fix: tier order, parts, shards for glint.
- **CUDA out-of-memory on model load** (shared GB10) twice; retried by `run_feat.sh`.
- **Killing a wrapper with `pkill -f` matched my own shell** (exit 144) and the Python child kept running; later
  kills are by PID after checking the command line.
- **Landmark analysis took 13 min** in the first run because numpy BLAS spun many threads on the loaded machine;
  OMP/OPENBLAS threads limited to 1–2 since.
- **The pre-registered contributor-similarity estimator c_pair = (z_A·z_B)/Σλ breaks**: medians 0.37 (landmark),
  0.64 (CLIP), 1.40 (DiffAE) for AR1 pairs, 1.65 for A43 stored pairs, i.e. above 1. Cause: the evaluation pools
  sit off the fit mean (the fit set is 92% FERET persons, the AR1 pool 80% FRGC; FRLL, A43 and H3 are other
  sources), and a common offset adds to every z_A·z_B. The "predicted at own c" columns are therefore not usable
  in the image arms (e.g. 0.26 predicted for DiffAE). A pool-centred c (centre by the pool's own source mean) is
  the planned descriptive replacement.
- **E7 stylegan frames are identical to the native frames** for every FRLL photo in these arms (AUC 0.500 with
  a zero-width interval): the stylegan resmatch leaves the photos unchanged in our frames, so that control carries
  no information. Not a bug of ID0; reported.
- **DiffAE on the stored A43 crops** (about 190 × 150 px, resized to 256 by DiffAE's own transform) inverts the
  ordering (E vs B20 0.324); on DiffAE-native 256 frames the same comparison is 0.687. The stored crops are out
  of the encoder's alignment; the native frames are the registered DiffAE-arm input (prereg).
- Old glint part `part_gl_000000.npz` (chunk 512) from the killed run reused; order verified identical.

## 8. Observations and ideas

- CLIP ranks landmark morphs as *less* typical than photos (and less with rising m), while DiffAE and exact
  shapes rank them *more* typical: CLIP reacts to the blend's texture, not to its identity position.
- In CLIP and DiffAE the same-person diffusion mix (C20, neutral + smiling of one person) is not separated from
  the two-person morph the same way: CLIP scores C20 as more average than B20 (0.419), DiffAE-native as less
  average (0.747). Expression averaging is a candidate explanation for CLIP (not tested).
- The mirror self-morph R3m is the most separable rung in DiffAE (R3m vs R4 0.807): a mirror self-morph is more
  typical than the two-person morph in z_sem, unlike exact shapes (0.651).
- The H3 one-identity renders `h3_bona` are renders of one of the two contributors (h3_prepare.py: "bona k =
  G(w_C), C = pairs.csv bona_of"), not of a third person as `10_ASSET_INVENTORY.md` states.
- 8 AR1 hosts are `is_val` persons (AR1 pool.py does not apply the val10 rule).
- FRLL-Morphs file names pair a person with themselves in 2–3 files per family (061_061, 096_096, 036_036;
  not AMSL).

## 9. Open items and next steps

- Glint arm: finish features (shards running), run `analyse.py --arm glint` (GEO-0 reads: fidelity, gain, virtual
  head, Λ and ceiling table, oracle power check), then `bench_sim.py` again (adds H3 pair similarity).
- DINOv3 arm in bf16: finish tier 1, run `analyse.py --arm dino`.
- Pool-centred c and predictions at the benchmark glintr100 cosine (descriptive).
- `verdicts.py` (falsifier table), then `result.md` final.
- Done 17:31: the 136 fit frames (+ `.tem`) that existed only in `/dev/shm/smad_arms/r6_frgc` were copied
  byte-identically (sha256 checked) to `/mnt/t7/smad_next/ID0/src_shm_copy/<pid>/`, manifest
  `COPY_MANIFEST.csv` (sha256 c89adf30…). `fit.csv` still names the original paths; map through the manifest
  if /dev/shm is gone. The other 1,259 fit frames are on disk under `mambamorph-code/baselines/webmorph/aligned`.
- Not done by design: released-detector shrink-law audit (identity idea 1's own target), BPCER per demographic
  group (no labels at hand).

## 10. Handover state (17:31 CET)

Running on the DGX (all started by this owner; logs in `/mnt/t7/smad_next/ID0/logs/`):
- glintr100 shards: PIDs 2060459 (shard 1/3), 2060461 (0/3), 2060462 (2/3); wrappers `run_feat.sh spark
  … --shard i/3`; logs `feat_gl_s{0,1,2}.log`; parts `feat/part_gl_*.npz` (33 of 53 at 17:28; expected end about
  18:00). If they fail: rerun the same command (`run_feat.sh` resumes from parts), then
  `feat.py --models glint --tag gl --merge-only`.
- DINOv3 bf16: PID 2088377 (wrapper `run_feat.sh spark /mnt/t7/smad_next/ID0/logs/feat_dn.log --models dino
  --tag dn --workers 1 --bs 32 --chunk 512 --dtype bf16 --max-tier 1`), parts `feat/part_dn_*.npz`, 19 parts
  expected, end about 18:05. If it fails: rerun the same line.
Compute spent so far: GPU processes about 2.5 h of wall time in total on a GPU shared with about 12 other
processes (actual GPU work estimated well under 30 GPU-minutes: about 20k forward passes of ViT-L-class models
and the DiffAE encoder); no WCSS, no Vast, no USD.

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next/src/ID0
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
$PY -I lists.py                                    # fit.csv, items.csv, lists_summary.json
./run_feat.sh diffae LOG --bs 32 --workers 1 --chunk 512 [--max-tier 1]     # DiffAE z_sem
./run_feat.sh spark LOG --models clip --tag cd --workers 2 --bs 32 --chunk 512 [--max-tier 1]
./run_feat.sh spark LOG --models dino --tag dn --workers 1 --bs 32 --chunk 512 --dtype bf16 --max-tier 1
./run_feat.sh spark LOG --models glint --tag gl --workers 0 --bs 32 --chunk 256 --shard i/3   # i = 0, 1, 2
$PY -I feat.py --models glint --tag gl --merge-only
$PY -I h3crops.py
$PY -I bench_sim.py
for a in landmark clip dino diffae glint; do OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 $PY -I analyse.py --arm $a --B 2000; done
$PY -I verdicts.py; $PY -I summarize.py
```
Note: the CLIP run of record used `--models clip,dino --tag cd` (fp16); its DINOv3 half is unusable.
