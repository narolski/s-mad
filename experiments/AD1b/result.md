# AD1b result (PROVISIONAL: smoke run, 4 FRLL persons; full run in progress)

Owner, 11 Nov 2026. Generator = A43 path unchanged (pinned DiffAE, ckpt 9bd2ba9e…, encode / encode_stochastic
T=250 / render T=20, A43 `interp()` verbatim, bs 16); only new op = lossless `torch.flip` of the input tensor.
Code `src/AD1b/ad1b_gen.py`, `src/AD1b/ad1b_analyze.py`. Smoke outputs `/mnt/t7/smad_next/AD1b/smoke_gen`,
`smoke_analysis/ad1b_result.json`. Full run: the first launch (PID 1949932) died at model load with CUDA out-of-memory on the shared GB10,
before any output; relaunched with an OOM-retry wrapper `src/AD1b/run_full.sh` (PID 1953722, logs
`/mnt/t7/smad_next/AD1b/run_full.log`, `gen_attempt<i>.log`, output `/mnt/t7/smad_next/AD1b/gen`): z_sem for all 102 FRLL persons and 200 FRGC/colorFERET hosts (DiffAE-aligned,
`pool_a256`, 600/600 aligned); x_T and renders for the first 32 persons only (deviation: x_T encoding
runs at about 157 s/image on the shared GB10 instead of A43's 13 s, so 102 persons would need about 9 h);
x_T of A′ and B for 16 persons.

## (1) Identical inputs (P_AA)

The A43 mixing path is **undefined** for identical inputs: z lerp returns z(A) exactly (torch.equal true),
but the x_T slerp computes θ = arccos(cos(x_T, x_T)) = NaN (float cosine ≥ 1), so the mixed x_T and the
rendered image are NaN; all four P_AA files are the same constant image (identical sha256), mean |P_AA − D20|
150.6 grey levels. Reading: "identical inputs do not reduce to the reconstruction" **in our code**, cause =
slerp division 0/0 (sin θ = 0) / arccos domain. Mathematically, the slerp limit (θ → 0) is x_T(A), so the
inputs would equal those of the D20 path bit for bit. D20 re-run here vs the stored A43 D20: mean 0.021,
max 1 grey level.

## (2) Flip (smoke, n = 4; descriptive)

- z_sem Euclidean: dist(A, flip A) 0.776 ≈ dist(A, A′) 0.773; dist(A, B) 1.744; per-person ratio median
  1.11 (cosine ratio 1.25). x_T (n = 4): cosine distance 0.98 (flip), 0.97 (A′), 0.99 (B), ratio 1.00.
- Pixels (reference D20, since P_AA is NaN): mean |P_AF − D20| 11.0 vs |C20 − D20| 8.3 → ratio 1.33;
  B20 vs its host's reconstruction 16.3 (n = 15).
- Left-right asymmetry (face box): input A 19.6, D20 18.3, C20 18.7, B20 12.0, **P_AF 2.1** (mix with its
  mirror gives a nearly symmetric face).
- Fixed reading on the smoke numbers: "**flip yields a genuinely different second image**" (both ratios ≥ 0.5).
- FR cosine (d): not yet computed (glintr100 route is CUDA-only and hit OOM on the shared GPU).
- Part 3 (detectors): skipped. The A43 scoring path needs the A43 build/storage step and its pinned
  manifest (not runnable unchanged on new images); AR1's local setup scores MTCNN RGB crops (A46 path).
