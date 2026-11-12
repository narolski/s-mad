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

## Supported summary (the independent reviewer's paragraph, 12 Nov, adopted unchanged)

On MIPGAN-style morphs we generated from 200 FERET and FRGC persons, three released detectors rank two-person morphs
well above one-person MIPGAN reconstructions (AUC 0.82–0.95) and above reconstructions moved closer to the generator's
mean latent (0.87–0.94), so averageness does not explain their scores. Most of this separation already appears when
MIPGAN blends two photographs of the same person (0.72–0.81); the second identity adds a modest step (same-person
against two-person morph, 0.65–0.72), and 87–100% of same-person morphs are flagged at the benchmark threshold. Our
morphs are not exchangeable with the published MAD22 MIPGAN files for most detectors, so these controls describe
responses to MIPGAN-style generation, not the benchmark cells themselves.

## Corrected statements (review `experiments/reviews/REVIEW_AG1_20261112.md`)

- **Readings A and B (non-primary).** Both are printed side by side; the author never selected one before scores
  (prereg l.71-73 not met). Reading A: mixed / mixed / "reads the benchmark" / mixed (ViT-B/16 / ViT-L/14 / SelfMAD
  own crop / SelfMAD our pipeline). Reading B: the threshold is met in all four rows (R2 vs R4 AUC >= 0.75 with lower
  bound > 0.65); this says that two photos blended by MIPGAN score above one photo, and most of that separation is
  already present between one photo and two photos of the same person. R3 vs R4: mixed in all four rows.
- **Graded mixing.** Both the two-person arm (AG3) and the same-person arm (AG3T) ramp; the registered meaning of a ramp
  in both arms is the second photo. The two-person minus same-person difference at matched alpha (80 hosts; post hoc)
  grows from about 0 at alpha 0.1 to +0.09 (ViT-B/16) / +0.13 (ViT-L/14) / +0.12 (SelfMAD own crop) at alpha 0.5
  (table below). Platform caveat: levels 0 to 0.4 come from the rented A100, the 0.5 endpoint mostly from Athena.
- **Excess over the best simple baseline.** The registered excess (detector AUC minus the best baseline) is kept, but it
  is not attribution: within quintile strata of each baseline the detectors keep nearly all of their separation
  (post hoc; table below), e.g. R2s>R4 within thumbnail-probe strata 0.850 / 0.919 / 0.856, R2>R4 within file-size
  strata 0.849 / 0.943 / 0.857. A small or negative excess says the rungs also differ in simple ways, not that the
  detector uses them.
- **Platform.** On the 159 Athena hosts alone the readings are identical to the pooled ones for all four rows (table
  below). The ViT-L/14 R3>R4 excess (+0.097 [0.016, 0.179] pooled) does not survive with rented hosts excluded
  (+0.095 [-0.001, 0.189]); by amendment 6 the conservative reading stands (no excess shown). R2s, AG3 / AG3T and all
  MIPGAN-II images are rented-only and cannot be platform-separated.
- **Reproducibility.** For 41 of 200 primary hosts, all MIPGAN-II images, the graded-mixing and the spread-matched
  images, only the 512-pixel detector inputs are retained; the generator outputs and latents were deleted by a pipeline
  error (their SHA-256 are logged). Results are fully reproducible from the retained inputs, not from the generator
  outputs. The five Athena shards' originals now have a second verified copy
  (`/net/pr2/projects/plgrid/plggrestoration/smad-next/backup/AG1_originals/`, sha256 matched to the ledger by
  streaming, `athena_backup_verify.txt`).
- **R1 on FRLL.** The E7 frames of the MIPGAN cells are identical to the native frames (score and file-size difference
  0; R0>R1 AUC 0.500 exactly), so the R0 -> R1 / R1 -> R2 split is void.
- **Flag rates** must be read beside the camera-photo flag rate at the same threshold (corrected-MAD22 EER threshold):
  on FERET / FRGC camera photos 8.5% (ViT-B/16), 4.8% (ViT-L/14), 31.8% (SelfMAD own crop); same-person morphs R3 are
  flagged 95.5 / 87.0 / 100%, two-person morphs R4 98.5 / 99.0 / 100%. Under the class ruling same-person morphs are
  morphs: their flags are not false alarms.
- **Mirror rung.** The symmetry statistic beats every detector (symmetry AUC 0.950 for R2 vs R3m); the mirror rows say
  nothing beyond symmetry.
- **Naming.** Always "MIPGAN-style" (our re-implementation; the bridge to the published files fails for most rows).

## Post-hoc facts (amendment 7; computed after all scores were read; `read/posthoc.json`, `read_athena_only/`)

Primary pool, MIPGAN-I; rows ViT-B/16 | ViT-L/14 | SelfMAD own crop.

Quintile-stratified AUCs [95%]:

| Contrast | file size | Laplacian var. | HF band | symmetry | thumbnail probe |
|---|---|---|---|---|---|
| R2>R4 ViT-B/16 | 0.849 [0.787, 0.897] | 0.843 | 0.899 | 0.873 | 0.892 |
| R2>R4 ViT-L/14 | 0.943 [0.893, 0.968] | 0.940 | 0.955 | 0.940 | 0.946 |
| R2>R4 SelfMAD own | 0.857 [0.801, 0.899] | 0.823 | 0.828 | 0.823 | 0.818 |
| R2s>R4 ViT-B/16 | 0.856 | 0.845 | 0.878 | 0.867 | 0.850 [0.758, 0.907] |
| R2s>R4 ViT-L/14 | 0.935 | 0.926 | 0.936 | 0.938 | 0.919 [0.836, 0.956] |
| R2s>R4 SelfMAD own | 0.877 | 0.861 | 0.869 | 0.880 | 0.856 [0.762, 0.913] |
| R3>R4 ViT-B/16 | 0.626 [0.557, 0.696] | 0.627 | 0.670 | 0.641 | 0.667 |
| R3>R4 ViT-L/14 | 0.701 [0.633, 0.765] | 0.711 | 0.730 | 0.714 | 0.717 |
| R3>R4 SelfMAD own | 0.654 [0.582, 0.725] | 0.642 | 0.651 | 0.657 | 0.654 |
| R0>R2 ViT-B/16 | 0.893 | 0.901 | 0.884 | 0.896 | 0.886 |
| R0>R2 ViT-L/14 | 0.782 | 0.788 | 0.783 | 0.792 | 0.719 |
| R0>R2 SelfMAD own | 0.912 | 0.920 | 0.912 | 0.933 | 0.907 |

d' decomposition of R2>R4 (share [95%]): second photo (R2>R3) 0.67 [0.58, 0.79] | 0.55 [0.47, 0.64] | 0.61 [0.50, 0.76];
second identity (R3>R4) 0.34 [0.23, 0.44] | 0.36 [0.27, 0.45] | 0.42 [0.26, 0.57].

Matched-alpha AG3 minus AG3T (AUC against R2 of the same 80 hosts), difference [95%]:

| alpha | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
|---|---|---|---|---|---|
| ViT-B/16 | +0.016 [-0.076, 0.104] | +0.042 | +0.064 | +0.090 [0.013, 0.154] | +0.093 [0.035, 0.144] |
| ViT-L/14 | +0.003 [-0.103, 0.100] | +0.023 | +0.079 | +0.115 [0.031, 0.178] | +0.127 [0.068, 0.183] |
| SelfMAD own | -0.025 [-0.120, 0.073] | +0.094 [0.004, 0.185] | +0.121 | +0.122 | +0.117 [0.038, 0.187] |
| glint cosine to B (AG3) / to A' (AG3T) | 0.24 / 0.84 | 0.34 / 0.86 | 0.46 / 0.89 | 0.56 / 0.89 | 0.66 / 0.91 |

Spread-matched control: R2s>R2 0.588 [0.565, 0.614] | 0.466 [0.440, 0.490] | 0.466 [0.442, 0.489] (R2s does not score
above R2 for ViT-L/14 and SelfMAD; slightly for ViT-B/16); within-rung Spearman of score with latent distance -0.05 to
+0.26 (wrong sign for an averageness cue); R2s>R4 in the latent-distance band 5.9-6.3 (26 R4, 35 R2s): 0.895 [0.776,
0.973] | 0.910 [0.810, 0.982] | 0.826 [0.642, 0.954].

Athena hosts only (159 primary hosts; rented-only rungs left out): reading A mixed / mixed / benchmark / mixed; reading
B threshold met in all four; R3 vs R4 mixed in all four. R2>R4 0.881 [0.833, 0.922] | 0.938 [0.910, 0.962] | 0.822
[0.768, 0.870] (SelfMAD our pipeline 0.883); R3>R4 0.663 | 0.711 | 0.656 (0.659); R3>R4 excess +0.047 [-0.041, 0.137]
| +0.095 [-0.001, 0.189] | +0.041 [-0.063, 0.147].

H-new-1 (registered in amendment 7 before computing): Spearman of R4 score with contributor w600k cosine -0.015 |
-0.100 | -0.013; R3>R4 by shape-distance tertile 0.673 / 0.680 / 0.632 | 0.691 / 0.757 / 0.714 | 0.632 / 0.649 / 0.690.
Registered verdict: neither (not falsified only because ViT-L/14 sits at |rho| = 0.1001; prediction rho <= -0.15 not met
in any row; no consistent rise with shape distance).

H-new-2: R2>R3 by tertile of pose difference 0.814 / 0.800 / 0.776 | 0.777 / 0.804 / 0.828 | 0.702 / 0.736 / 0.767; by
illumination difference 0.800 / 0.779 / 0.797 | 0.849 / 0.783 / 0.786 | 0.718 / 0.791 / 0.698. Registered verdict: not
falsified (max - min >= 0.05 in some rows); the predicted increase holds only for pose in ViT-L/14 and SelfMAD.

G-a (published MAD22 values from `docs/sources`, original release; ours on the corrected copy): MADation ViT-B/16
18.71 vs 33.37 (MIPGAN-I), 13.27 vs 22.21 (MIPGAN-II): not reproduced, descriptive; ViT-L/14 11.68 vs 20.32: not
reproduced; 9.81 vs 9.06: reproduced. SelfMAD: cannot be evaluated (no published MAD22 MIPGAN value in docs/sources).
