# DiffAE morph of two identical photos and of a photo with its mirror image (AD1b): full record

Owner: hypothesis-owner agent (Opus), 11 Nov 2026. Requested by the lead after the author asked (1)
whether a diffusion morph of two identical photos reduces to the one-photo reconstruction in our
pipeline and (2) whether a horizontal flip changes anything for a diffusion morphing method.
`prereg.md` (fixed readings, written before any computation) and `result.md` (provisional) sit beside
this file.

Terms. DiffAE = diffusion autoencoder (Preechakul et al.), the generator behind our MorDIFF-style morphs.
z_sem = its 512-number semantic code (`LitModel.encode`); x_T = its inverted noise map
(`encode_stochastic`, 250 steps), 3×256×256. lerp = linear interpolation, slerp = spherical interpolation.
A = neutral FRLL photo of a person, A′ = their smiling photo, B = another person; flip = left-right mirror.
D20 = one-photo reconstruction at 20 decoding steps, C20 = same-person mix (A + A′), B20 = two-person morph
(the A43 arms). P_AA = morph path fed with A twice; P_AF = A mixed with flip(A).

## 1. Question and current answer

Status (11 Nov 2026, 17:40 CET): **smoke finished (4 persons); full run running** (process 1953728,
expected end about 20:00–20:30 CET, section 10). Answers so far:
1. **Identical inputs do not reduce to the reconstruction in our code.** The z lerp returns z(A) exactly,
   but the A43 slerp computes θ = arccos(cos(x_T, x_T)) = NaN (floating-point cosine ≥ 1; even at θ = 0
   it would be sin(0)/sin(0) = 0/0), so the mixed x_T and the image are NaN: every P_AA is the same
   constant image, 150.6 grey levels from D20 on average. In the mathematical limit θ → 0 the inputs equal
   those of the D20 path bit for bit.
2. **Flip yields a genuinely different second image** (provisional, n = 4): dist_z(A, flip A) 0.776 ≈
   dist_z(A, A′) 0.773 (ratio 1.11); |P_AF − D20| 11.0 vs |C20 − D20| 8.3 grey levels (ratio 1.33); and the
   mix of a face with its mirror is almost left-right symmetric (asymmetry 2.1 vs 18.3 for D20).

## 2. Timeline

- 11 Nov ~15:05: request received. Read `/home/narolski/mambamorph-code-a44/smadcvpr/a43_gen.py` (the A43
  generator, sha fc862ec6…), the A43 generation wrapper
  (`/home/narolski/mambamorph-code/experiments/A43_mordiff-two-by-two/raw/a43_run_gen.sh`), the X3 aligner
  runner and log (`/mnt/t7/smad_heldout/a41_diffae/data/scripts/run_align_unchanged.py`,
  `/mnt/t7/smad_heldout/a41_diffae/logs/x3_align.log`), the A43 identity route in `a43_build.py`
  (l.496–540) and the AR1 pool (`/mnt/t7/smad_next/AR1/pool.csv`). `nvidia-smi`: GPU 95% busy, memory N/A
  (GB10 unified memory).
- ~15:10: wrote `prereg.md` with the lead's fixed readings.
- ~15:14: selected 200 FRGC/colorFERET hosts (first 200 of `pool.csv` by sha1 of `pid`: 160 FRGC, 40
  FERET), byte-copied their H, S, B images to `/mnt/t7/smad_next/AD1b/pool_in/` (600 files), list
  `pool_selection.csv`. Copied the dlib landmark model files into `/mnt/t7/smad_next/AD1b/align_run/temp/`.
- ~15:15: smoke of the unchanged DiffAE `align.py` on 8 pool images (`smoke_in` → `smoke_a256`): 256×256 OK.
- 15:14–15:38: full alignment of the 600 pool images → `pool_a256/` (600/600; one image had two faces
  detected, "601it", the second face overwrote the first; not identified which). CPU, 23 min (shared CPU).
- ~15:20: wrote `src/AD1b/ad1b_gen.py` and `ad1b_analyze.py`. Smoke attempt 1 (`--smoke 4 --n-xt 4`) died
  with CUDA out of memory while moving the model to the GPU (log `logs/smoke_attempt1_oom.log`).
- 15:30–16:03: smoke attempt 2 completed (`smoke_gen/`, log `smoke_gen.log`): 12 x_T encodings took
  1,881 s (157 s per image, against 13 s in A43 on an idle GPU); render 198 s. Found the P_AA NaN.
- ~16:05: smoke analysis (`smoke_analysis/ad1b_result.json`, `--no-fr`): the face-recognition step
  (glintr100 via `a2f_common`, hard-coded CUDA) died with out of memory; with `CUDA_VISIBLE_DEVICES=` it
  cannot run at all, so `--no-fr` was added. Also fixed `med_iqr` for empty lists.
- ~16:08: amended the run because of the encoding speed: `--n-img 32` (x_T and renders for the first 32
  persons) and `--n-xt 16` (x_T of A′ and B for 16 persons); z_sem stays complete (102 FRLL persons, 200
  hosts). Script sha changed from 1d7acbe8… (smoke) to 515f5e54… (full).
- 16:09: full run launched (PID 1949932, log `/mnt/t7/smad_next/AD1b/gen.log`); died at model load with
  CUDA out of memory, no output.
- 16:10: relaunched under `src/AD1b/run_full.sh` (wrapper PID 1953722; Python PID 1953728), which retries
  on start-up failures. Attempt 1 loaded; at 17:02 the log showed `x_T 16/80 2411s`.
- ~16:15: provisional `result.md`; hand-back to the lead (the first hand-back wrongly said the first full
  launch was running; corrected in the second hand-back).
- ~17:40: this README.

## 3. Data

| Item | Path | n | Notes |
|---|---|---|---|
| FRLL DiffAE-aligned photos (X3 a256) | `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256/` | 204 (102 × `_03`, `_08`) | made by the unchanged DiffAE `align.py` (X3, 7 Nov); FRLL = evaluation only |
| Persons list | `/mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv` (sha 4366459d…) | 102 | the X3 self-pair list |
| Pool selection | `/mnt/t7/smad_next/AD1b/pool_selection.csv` (sha b00b08c9…) | 200 hosts | from `/mnt/t7/smad_next/AR1/pool.csv` (AR1 owner's pool) |
| Pool inputs (byte copies) | `/mnt/t7/smad_next/AD1b/pool_in/` | 600 PNG (512 px, AR1 `src/`) | names `<db>_<subject>_{H,S,B}.png` |
| Pool aligned | `/mnt/t7/smad_next/AD1b/pool_a256/` | 600 PNG 256 px | log `pool_align.log`, 0 errors |
| A43 arms (reused) | `/mnt/t7/smad_heldout/a43/gen/{D20,C20,B20}/png256/`, rows `gen_log.rows.csv` | 204 / 102 / 200 | A43 generation, 7 Nov |
| Raw FRLL photos (identity reference) | `/mnt/t7/Datasety/downloads/frll_base/extracted/neutral_front/<p>_03.jpg` | 102 | sha list `/mnt/t7/smad_heldout/a41_diffae/data/provenance/raw_frll.sha256` |
| Smoke outputs | `/mnt/t7/smad_next/AD1b/smoke_gen/` (`gen_rows.csv` 4510273c…, `gen_log.json` fbdcb879…, `codes_z.npz`, `codes_xT.npz`, `PAA/ PAF/ D20r/png256`), `smoke_analysis/ad1b_result.json` (01d2c4dc…) | 4 persons | — |
| Full-run outputs (being written) | `/mnt/t7/smad_next/AD1b/gen/` | 32 persons × 3 image sets; z codes 102 FRLL × 4 + 200 hosts × 4 | created only at the render step |

Third-party code and weights: DiffAE repository `/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4/repo`
(git commit 00c57d3f626f28bf9ed8aff58d90baab25de3af4, checked clean by the script); checkpoint
`.../checkpoints_download/ffhq256_autoenc/last.ckpt`, sha256
9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca (loaded with `weights_only=True`, the
Lightning callback entry mapped to an inert placeholder, as A43); `align.py` sha 7d7cf0d0…, run through
`run_align_unchanged.py` (sha 65009661…; restores `Image.ANTIALIAS = LANCZOS` for Pillow ≥ 10, nothing
else); dlib `shape_predictor_68_face_landmarks.dat` copied from `/mnt/t7/smad_heldout/a41_diffae/work/align_run/temp/`.
Face embedder for (d): `/mnt/t7/smad_heldout/arc2face/scripts/a2f_common.py` (sha d27701db…, glintr100),
`prep_eval.kps` from `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py` (imported, not edited).

## 4. Code

| Script | sha256 | Job |
|---|---|---|
| `/home/narolski/smad-next/src/AD1b/ad1b_gen.py` | 515f5e54… | loads DiffAE exactly as `a43_gen.py`; z_sem of A, flip(A), A′, B (FRLL) and H, flip(H), S, B (pool); x_T (`encode_stochastic(batch, encode(batch), T=250)`) of A and flip(A) for `--n-img` persons and of A′, B for `--n-xt`; renders (T = 20, batch 16) P_AA = interp(A, A), P_AF = interp(A, flip A), D20r = render(x_T(A), z(A)); `interp()` copied verbatim from `a43_gen.py` (z lerp, x_T slerp, α = 0.5); writes PNGs (torchvision `save_image`), `gen_rows.csv` (θ, finiteness, z equality, sha256), `codes_z.npz`, `codes_xT.npz`, `gen_log.json`; refuses an existing output folder |
| `/home/narolski/smad-next/src/AD1b/pool_select.py` | 758b8292… | step 1: host selection and byte copies (the inline script of 15:14, saved as a file) |
| `/home/narolski/smad-next/src/AD1b/run_full.sh` | 883fe879… | wrapper: up to 30 attempts, 300 s apart, while `/mnt/t7/smad_next/AD1b/gen` does not exist; logs `gen_attempt<i>.log` |
| `/home/narolski/smad-next/src/AD1b/ad1b_analyze.py` | d65ed4b2… | Part 1 distances (Euclidean, cosine; medians and IQR; per-person ratios); Part 2 (a) max/mean \|P_AA − D20\|, D20r vs D20; (b) mean \|·\| of P_AF, C20 vs P_AA and vs D20, B20 vs its host's D20; (c) asymmetry = mean \|img − mirror(img)\| in rows 70–220, cols 64–192; (d) glintr100 cosine to the raw photo (A43 route), skipped with `--no-fr`; applies the fixed readings; uses D20 as the pixel reference when P_AA is not finite |

Flip = `torch.flip(img, dims=[-1])` of the tensor returned by DiffAE's `ImageDataset` (lossless). Seeds:
none needed (DDIM encoding and rendering are deterministic; DiffAE prints "Seed set to 0" at load).
Environment: DiffAE venv `/mnt/t7/thirdparty/diffae_venv/bin/python -I` (Python 3.12.3, torch
2.12.1+cu130, torchvision 0.27.1+cu130), working directory the DiffAE run folder (as A43); analysis in the
spark venv (numpy 1.26.4, OpenCV 4.11.0, insightface).

Arguments used (full run): `--repo …/repo --ckpt …/last.ckpt --a256 /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256
--pool-a256 /mnt/t7/smad_next/AD1b/pool_a256 --pool-sel /mnt/t7/smad_next/AD1b/pool_selection.csv
--self-pairs /mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv --out-root /mnt/t7/smad_next/AD1b/gen
--n-img 32 --n-xt 16` (bs 16 default). Smoke: `--pool-a256 …/smoke_a256 --out-root …/smoke_gen --smoke 4 --n-xt 4`.

## 5. Results (smoke, 4 persons: 001–004; `smoke_analysis/ad1b_result.json`)

| Quantity | Value |
|---|---|
| z_sem Euclidean: A–flip A / A–A′ / A–B (median) | 0.776 / 0.773 / 1.744 |
| z_sem cosine distance: same three | 0.0073 / 0.0073 / 0.0371 |
| Per-person ratio flip / A′ (Euclidean; cosine) | 1.11; 1.25 |
| x_T Euclidean: flip / A′ / B | 624.7 / 624.1 / 627.1 (ratio 1.00) |
| x_T cosine distance: flip / A′ / B | 0.982 / 0.969 / 0.991 |
| P_AA: θ, finite | NaN for all 4; render not finite; z(mixed) == z(A) exactly (torch.equal) |
| \|P_AA − D20\| mean / max | 150.6 / 232.5 (P_AA is a constant image, identical sha256 3b93f262… for all four) |
| \|D20r − D20\| (our re-run vs stored A43) mean / max | 0.021 / 1.0 |
| \|P_AF − D20\| / \|C20 − D20\| (median of per-person means) | 11.0 / 8.3 → pixel ratio 1.33 |
| \|B20 − D20 of its host\| (15 B20 images with hosts 001–004) | 16.3 [13.3, 18.2] |
| Asymmetry: input A / D20 / C20 / B20 / P_AF | 19.6 / 18.3 / 18.7 / 12.0 / **2.1** |
| slerp angle θ for P_AF | 1.545–1.560 rad (≈ 89°, the same as between two different persons' x_T) |
| Fixed readings | flip: "flip yields a genuinely different second image" (code ratio 1.11 ≥ 0.5 and pixel ratio 1.33 ≥ 0.5); identical: "do not reduce within 1 grey level", cause = NaN in slerp |
| (d) glintr100 cosine of P_AF to A | not computed (CUDA out of memory) |
| Pool z_sem distances | not in the smoke (no smoke host matched the selection); in the full run |

Deviation from the prereg: the readings compare P_AF and C20 with **D20** instead of P_AA, because P_AA is
NaN; D20 is what P_AA would be with the slerp limit applied (z identical, x_T(A)).

## 6. Checks

Verified: the re-run of the A43 D20 path reproduces the stored A43 D20 (mean 0.021, max 1 grey level), so
the encoder, renderer and checkpoint here are the A43 ones; z lerp of identical codes is exact; the
DiffAE repo is the clean pinned commit and the checkpoint hash matches (checked inside the script); all
600 pool images aligned without error. Not verified: the pool code path in the generator (no smoke host
overlapped the selection; the tag matching was checked by reading the code); face-recognition cosines
(d); any detector score (Part 3 skipped: the A43 scoring path needs the A43 build/storage step and its
pinned manifest, and the AR1 local setup scores MTCNN RGB crops, not the A43 frames).

## 7. Dead ends and failures

- **NaN for identical inputs** (finding, not a bug in our code): the A43 `interp()` divides by sin θ with
  θ = arccos(cos(x0, x1)); for x0 = x1 the float cosine exceeds 1 and θ = NaN (exactly 1 would give 0/0).
  Not "fixed": the generator must stay unchanged, so P_AA is reported as undefined and D20 is used as its
  limit. Any future identical-input control must special-case θ = 0 (return x0) and register that change.
- CUDA out of memory at model load: smoke attempt 1 (~15:20, `logs/smoke_attempt1_oom.log`) and full
  launch 1 (16:09, PID 1949932, `gen.log`). Cause: the shared GB10 (other jobs: AG1 generation, AR1
  scoring, AD4, a DiffAE confirmation run, a CLIP training controller; free memory about 5 GB, swap full).
  Handled by retrying; `run_full.sh` automates it.
- Face-recognition step: `a2f_common.fr_model` hard-codes CUDA; out of memory on the shared GPU, and
  impossible with the GPU hidden. Added `--no-fr`; (d) remains open.
- `med_iqr` crashed on an empty list in the smoke (no B20 host in some sets); fixed to return None.
- Encoding speed 157 s per x_T image under contention (12× slower than A43) → scope cut to 32 persons
  for images and 16 for the x_T subset (registered here as an amendment).
- My first hand-back said the first full launch was running; it had already died. Corrected in the second
  hand-back the same evening.

## 8. Observations and ideas

- Mixing a face with its mirror produces an almost perfectly symmetric face (asymmetry 2.1 vs about 18 for
  real photos and reconstructions): a mirror self-morph is not a no-op, but it creates a strong, unnatural
  symmetry cue a detector could learn — unsuitable as a "same identity" control without matching symmetry.
- In x_T space the flip of a photo is as far from the photo as a different person (cosine distance about
  0.98 for all), so slerp with the mirror behaves like slerp with a stranger's noise map.
- B20 morphs are also less asymmetric (12.0) than photos: averaging two faces symmetrises them; asymmetry
  is a candidate morph cue on its own.

## 9. Open items and next steps

- Finish the full run and the analysis (section 10); add the pool z_sem distances and (d).
- Decide whether identical-input controls need a registered θ = 0 guard in `interp()`.
- Part 3 (detector AUCs) needs a registered scoring path for new DiffAE images (A43 build step) — not run.

## 10. Handover state

- **Running:** `/home/narolski/smad-next/src/AD1b/run_full.sh` (bash PID 1953722) → Python PID 1953728
  (`ad1b_gen.py`, attempt 1), DGX, started 16:10 CET. Logs: `/mnt/t7/smad_next/AD1b/run_full.log` (wrapper),
  `/mnt/t7/smad_next/AD1b/gen_attempt1.log` (generator; progress lines `x_T k/80 <s>`). At 17:02: 16 of 80
  x_T done in 2,411 s (one batch of 16 ≈ 40 min). Expected: x_T finished about 19:40, renders (6 batches)
  done about 20:00–20:30 CET; then `gen_log.json`, `gen_rows.csv`, `codes_z.npz`, `codes_xT.npz` appear in
  `/mnt/t7/smad_next/AD1b/gen/` and `run_full.log` prints "attempt 1 ok".
- **If it dies before rendering** (no `gen/` folder): the wrapper retries itself (up to 30 attempts, 5 min
  apart). x_T encodings are not checkpointed, so a crash restarts the encoding from zero.
- **If it dies during rendering** (`gen/` exists but no `gen_log.json`): the wrapper stops. Move the
  partial folder aside (`mv /mnt/t7/smad_next/AD1b/gen /mnt/t7/smad_next/AD1b/gen_failed_<time>`) and
  start `nohup /home/narolski/smad-next/src/AD1b/run_full.sh > /mnt/t7/smad_next/AD1b/run_full.log 2>&1 &`.
- **Analysis step** (CPU plus a short GPU use for glintr100):
  `cd /home/narolski/smad-next && /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AD1b/ad1b_analyze.py --gen /mnt/t7/smad_next/AD1b/gen --out /mnt/t7/smad_next/AD1b/analysis`
  (add `--no-fr` if the GPU is out of memory); then copy `analysis/ad1b_result.json` and the part CSVs
  (small) to `experiments/AD1b/` and update `result.md` with the full numbers and the readings.
- Compute so far: smoke about 0.6 GPU-h (shared GPU), full run about 4 GPU-h expected; CPU alignment
  23 min; 0 USD.

## 11. Reproduce from scratch

```bash
D=/mnt/t7/smad_next/AD1b; T=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4
# 1. pool selection and byte copies: python3 /home/narolski/smad-next/src/AD1b/pool_select.py (first 200 hosts of AR1 pool by sha1(pid))
#    -> $D/pool_selection.csv, $D/pool_in/
# 2. align (unchanged DiffAE align.py)
mkdir -p $D/align_run/temp && cp /mnt/t7/smad_heldout/a41_diffae/work/align_run/temp/shape_predictor_68_face_landmarks.dat* $D/align_run/temp/
cd $D/align_run && /mnt/t7/thirdparty/diffae_venv/bin/python -I /mnt/t7/smad_heldout/a41_diffae/data/scripts/run_align_unchanged.py \
  $T/repo/align.py 7d7cf0d0222d25800d5205a91122859b4077401b53ee33a014e4a650c8f5d27b -i ../pool_in -o ../pool_a256
# 3. generation (smoke, then full)
cd $T/run && /mnt/t7/thirdparty/diffae_venv/bin/python -I /home/narolski/smad-next/src/AD1b/ad1b_gen.py --repo $T/repo \
  --ckpt $T/checkpoints_download/ffhq256_autoenc/last.ckpt --a256 /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256 \
  --pool-a256 $D/smoke_a256 --pool-sel $D/pool_selection.csv --self-pairs /mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv \
  --out-root $D/smoke_gen --smoke 4 --n-xt 4
nohup /home/narolski/smad-next/src/AD1b/run_full.sh > $D/run_full.log 2>&1 &
# 4. analysis
cd /home/narolski/smad-next && /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AD1b/ad1b_analyze.py --gen $D/gen --out $D/analysis
```

The pool selection script (step 1) as run on 11 Nov:

```python
import csv, hashlib, shutil, pathlib
D = pathlib.Path('/mnt/t7/smad_next/AD1b')
r = sorted(csv.DictReader(open('/mnt/t7/smad_next/AR1/pool.csv')), key=lambda x: hashlib.sha1(x['pid'].encode()).hexdigest())[:200]
out = []
for x in r:
    tag = x['pid'].replace(':', '_')
    for role in ('H', 'S', 'B'):
        shutil.copyfile(x[role], D / 'pool_in' / f"{tag}_{role}.png")
    out.append({'pid': x['pid'], 'tag': tag, 'db': x['db'], 'H': x['H'], 'S': x['S'], 'B': x['B'], 'B_pid': x['B_pid']})
with open(D / 'pool_selection.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
```
