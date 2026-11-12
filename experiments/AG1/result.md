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

## 3. Staged tasks

Athena (target since 11 Nov evening): single pack `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AG1/ag1_pack.tar`
(sha256 c6b9d2c9...), scripts in `.../tasks/AG1/`; 14 shards (2 smoke, 8 core, 4 AG3 / AG3T), 3,833 images, 912
inversions, 12.7 H100-h at the WCSS rates (A100 rate to be measured). Mirror rung (R3m) included for all 302 hosts.
Jobs (Athena, account plgrestorearc-gpu-a100): smoke 3544188 failed (node-local disk 4 GB; 0.06 GPU-h); smoke
3544209 passed (19 / 19 images, 0.17 GPU-h); production 3544797 (core, 8 tasks), 3544798 / 3544799 (graded mixing,
dependent), submitted 11 Nov 19:05, about 19.9 GPU-h expected.
WCSS (superseded): 13 task dirs in `/lustre/.../smad-next/staging/AG1/`, never in ready/.

## 4. What was tested for real

- WCSS `run.sh` logic on the DGX GB10 with local roots: smoke mip1 7 / 7 images and smoke mip2 4 / 4 images, exit 0
  (code before amendment 1). Final loss mip1 R2 1.67, R3 2.96, R4 5.42; mip2 R2 2.43, R3 3.29, R4 5.66.
- Final code through `run.sh` on an AG3-type shard that reads the smoke result tar: exit 0; achieved dose (w600k
  cosine to B) alpha 0 0.128, 0.2 0.366, 0.3 0.502, 0.5 0.721.
- `mipgan_alpha(0.5)` objective equals `generate.mipgan`'s exactly (forward); trajectories differ by max |w| 0.65,
  of the order of `generate.mipgan`'s own run-to-run spread (0.379).
- RT vs R3: mean 3.9, max 133 grey levels (not a determinism check; noise floor).
- Output format: 1024 x 1024 RGB PNG, no ancillary chunks, FFHQ framing as the published MIPGAN files.
- Reader on the real design with synthetic scores (6,825 rows, 20 cells, exit 0); scoring adapter selftest (22
  checks); WCSS dmenv import of the vendored modules.

## 5. Untested

- Anything on Athena: environment build, A100 timing and peak memory, the task script. The smoke job tests these.
- The mirror rung on a GPU (crops built and checked lossless on the DGX; no R3m image generated yet).
- `ag1_manifest.py` and real scoring (need images); MixFaceNet-MAD scoring (no AG1 scorer); SelfMAD release is held
  on T7 (AR1 copy, sha256 0ad8db6f...).

Full record: `README.md`.

## Rented platform (12 Nov)

First check on the rented A100 (amendment 4) failed: frll_001 R2 final loss 1.847 vs Athena 1.665 (10.9% > 10%); the
other 9 optimised images within 0.4-1.7%. Amendment 5's rule did not decide (reruns 1.879 and 1.777). The lead accepted
the platform under rule (b) after seeing all three runs (amendment 6): a decision, not a registered pass. All three
rented runs of that image lie above Athena, so a small platform offset is not excluded. Every reading is reported
pooled and without rented shards; the conservative one stands. Driver: drive_v2.sh (PID 3091276), lease
/mnt/t7/smad_next/vast/ag1, A100-SXM4-40GB at 0.51 USD/h.

## Facts table (12 Nov, before interpretation; sent to the lead)

Full table: `read/facts.md`; machine-readable `read/ag1_read.json`, `read/gates.json`, `read/ag1_ladder.csv`. Scores:
`/mnt/t7/smad_next/AG1/scoring/a41g_out/ag1/<release>/<mode>/scores_ag1.npz` (7,229 rows each; manifest ag1.csv
5892c918...). Correction (review of 12 Nov, finding 9): the gates were NOT computed or committed before scores
existed. Score files were written 12 Nov 11:34:07, 11:36:38, 11:40:33 and 11:42:33 CET; the gate stage first ran at about
11:47 (it crashed on render-only rows, was fixed and rerun), and the current `read/gates.json` is dated 12:05:38, written
again by the full reader run. The gate code (`ag1_read.py`, function `gates`) reads only the manifest, the oracle
embeddings, rt_check.json and the shard logs; it reads no score file. Gates and read/ outputs were first committed
after the review. No interpretation is written here; the lead draws conclusions.
