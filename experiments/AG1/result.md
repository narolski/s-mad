# AG1 / AG2 / AG3: preparation result (no data image, no score yet)

Status 11 Nov 2026: tasks staged on Lustre, not in `ready/`, nothing submitted. Facts only.

## 1. Where our MIPGAN comes from and how it ran

| Item | Fact | Source |
|---|---|---|
| MIPGAN-I-style code | branch `gan1` 24cc974 of `/home/narolski/mambamorph-code-gan1`: `smadcvpr/gan/{generate_mip1.py, generate.py (mipgan), stylegan1.py, arcface.py, lpips_vgg.py}`; vendored unchanged in `src/AG1/vendor/` (sha256 = A33's MODELS.sha256 lines) | PROTOCOL A33 (2), `h4_mipgan1/data/MODELS.sha256` |
| Generator weights | StyleGAN v1 FFHQ-1024, NVIDIA `karras2019stylegan-ffhq-1024x1024.pkl` (f277a437...), PyTorch port `stylegan1_ffhq1024.pt` (4618be6e...), pack `gan_sg1.tar` 1571c1a3...; loss models in `gan_weights.tar` e06f19af... (w600k_r50 fused, VGG-16, LPIPS, pytorch_msssim 1.0.0, e4e + StyleGAN2 config-f for MIPGAN-II) | pack `.content` files |
| MIPGAN-II-style path | `generate.py --gen mipgan2` (A28): e4e + StyleGAN2, same loss; ran on WCSS (A28) and locally on GB10 (A28 gate, 41 s / image) | `/tmp/opencode/gan_protocol/gate_raw`, `GATE_RESULTS.md` |
| GAN32 inverter | StyleGAN3-T (`stylegan3-t-ffhq-1024x1024.pkl`), Vast x86 only; not used by AG1 | 10_ASSET_INVENTORY C |
| x86 only? | No. All generator code is pure PyTorch. The unchanged `generate_mip1.py` and our wrapper ran on the DGX GB10 (ARM). | this session |
| H100 rate | H4 job 6237081 (task 0-49): inversion (500 steps) median 23.3 s; one morph incl. two inversions 53.6 s, so MIPGAN-I 150 steps about 6.9 s. MIPGAN-II (A28 FERET 0-124): 9.3 s per image incl. e4e | tar `log.jsonl` |
| GB10 rate (shared at 96% with the Codex fits) | inversion 700 to 1,350 s, MIPGAN 150 steps 300 to 480 s, i.e. 15 to 60 x slower than H100 | smoke logs below |
| Output format | 1024 x 1024 RGB PNG, no ancillary chunks, FFHQ framing: same as the published MAD22 MIPGAN-I / -II files (eyes (387, 482) / (634, 481) ours vs (385, 476) / (640, 478) published). Ours are written with PNG compress_level 1 (larger files, same pixels); scoring uses re-written aligned frames for every row | `prep_eval.kps` on one file each |
| Cross-hardware | The same code on the same H4 gate pair: GB10 vs H100 PNG differ by mean 15.5, max 123 grey levels (final loss 4.78 vs 4.98). All data images must come from one platform (WCSS) | `/mnt/t7/smad_next/AG1/smoke/orig_h4gate` |
| WCSS state | Old job dirs `~/jobs/h3sg3`, `~/jobs/h2embmid` hold only array scripts and logs. The packs `gan_weights.tar`, `gan_sg1.tar` still exist in `$L/smadcvpr/packs` with matching sha256; hard-linked into `smad-next/packs/AG1` (no upload of weights). Container `/lustre/software-data/container-images/pytorch_latest.sif` unchanged since Mar 2025 (the one H4 / H4b used). `apptainer` is not on the login node PATH (it was on the compute nodes for H4). | ssh listings |
| Volatile weights | The SG1 weights and both packs existed only in `/tmp/opencode`; copied to `/mnt/t7/smad_next/AG1/packs_src/` (sha256 checked) | |

## 2. Inputs and pairs (CPU, done)

604 photos prepared, 0 dropped: FRLL 102 x 2, FERET 100 x 2 (159 eligible), FRGC 100 x 2 (442 eligible). Pairing:
FRLL 50 cycles (48 two-cycles), FERET 25, FRGC 19. Mean w600k cosine of contributors: morphs 0.140 / 0.161 / 0.170,
twins 0.905 / 0.836 / 0.862 (FRLL / FERET / FRGC). Files: `pairs.csv`, `shards.csv`, `/mnt/t7/smad_next/AG1/inputs/`.

## 3. Staged tasks (`/lustre/.../smad-next/staging/AG1/`, packs in `.../packs/AG1/`, all four sha256 verified on Lustre)

13 tasks, 3,421 images, 9.8 H100-h at measured rates, 15.6 slot-h of `est_minutes`: o00 / o01 smoke (21 / 18 min);
o02-o03 FRLL mip1 (149 / 72); o04-o07 FERET / FRGC mip1 (148 / 42 / 140 / 50); o08 FRLL mip2 (137); o09-o12 AG3 +
AG3T (40 each, need o04-o07). Results go to `.../results/AG1/<shard>.tar` + `.sha256` + `.log.csv`.

## 4. What was tested for real

- `run.sh` (unchanged logic, local root via `AG1_SN`, DGX python via `AG1_PY`) on smoke shard o00: 2 FRLL persons,
  4 inversions, 7 images (R2, R2i, R3 x 2, R4, RT, AG3 alpha 0.3), full iteration counts, exit 0, result tar with
  verified sha256. GB10 values: R2 loss 1.67, R3 2.96, R4 5.42 (glint not run; w600k generator-side cosines R4
  0.728 / 0.721, R3 0.966 / 0.965). Ran with the code before the review fixes (ag1_gen 375f5998...).
- Final code (`ag1_code.tar` 735816eb...) through `run.sh` on a dependency test shard (needs the o00 tar): extracted
  the needed latents, ran `mipgan_alpha` at alpha 0 and 0.2 and the twin dose: exit 0. Achieved dose (w600k cosine
  to B): alpha 0 0.128, 0.2 0.366, 0.3 0.502, 0.5 (R4) 0.721.
- RT vs R3 (same pair, order swapped, GB10): mean 3.9, max 133 grey levels; the symmetric loss is not bitwise
  symmetric in floating point. RT is therefore a noise floor, not a determinism check (prereg changed).
- Reader `ag1_read.py` end to end on the real design with synthetic scores and embeddings (6,421 rows, 20 cells).
- Scoring adapter `ag1_score.py` selftest in a c669666 job root: 22 checks passed (stubbed networks).
- WCSS login node: `~/dmenv/bin/python -I` imports torch 2.11 / torchvision 0.26 and the five vendored modules.

## 5. Untested

- Any run in a WCSS slot: the container (`apptainer exec --nv` of `pytorch_latest.sif`) inside the slot job, its
  torch version, the H100 timing of our wrapper. `run.sh` exits 5 if apptainer is missing.
- mip2 smoke and the `--selfcheck` (alpha 0.5 vs `generate.mipgan`): see section 6.
- `ag1_manifest.py` (frames, glint oracle, RT check, pins) and real scoring: they need the generated images.
- MixFaceNet-MAD scoring (no AG1 scorer).

## 6. Smoke completions (filled when the runs finish)
