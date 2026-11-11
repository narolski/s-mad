# MIPGAN one-person controls (AG1, with AG2 and AG3): full record

Owner: AG1 owner (Opus agent). Started 11 Nov 2026, 14:22 CET. Record started 11 Nov ~17:45 CET; dated lines are added
below as work goes on, history is not rewritten. Short verdict file: `result.md`; registration: `prereg.md`.

## 1. Question and current answer

Question: on the MIPGAN benchmark cells (corrected MAD22 MIPGAN-I and MIPGAN-II; FRLL StyleGAN as fallback), do
released morphing-attack detectors react to "this image came out of the generator" or to the morph? The ladder: R0
camera photo, R1 existing E7 control, R2 = MIPGAN optimiser on one photo twice (A = B), R3m = one photo with its own
mirror image (added 11 Nov evening), R3 = two photos of one person, R4 = two persons; plus a bridge to the published
MIPGAN files. AG2 replaces camera photos by their R2 images; AG3 grades two-person mixing 0 to 0.4 (AG3T: the same
on twin pairs).

Status 11 Nov evening: **no data image and no score exist yet.** Inputs, pairs, shard plans, generation code and the
analysis code are built and tested on the DGX. The single pack is uploaded to Athena. **Blocked:** Athena's Slurm does
not accept the account yet (no association for the user); the lead's watcher tests every 20 minutes and will tell
the owner. Nothing may be submitted or probed until then.

## 2. Timeline (11 Nov 2026, CET)

- 14:22 Task received (lead). Read OWNER_BRIEF, 11_AUDIT_PLAN, 10_ASSET_INVENTORY, 12_STATE_AT_HANDOVER, NOTEBOOK.
- 14:25 Located our MIPGAN implementation (section 4): branch gan1 24cc974 of `/home/narolski/mambamorph-code-gan1`,
  used for H4 (A33, WCSS job 6237081) and H4b (A34, job 6237487). Timings read from the H4 tars. Weights and packs
  existed only in `/tmp/opencode`; copied to `/mnt/t7/smad_next/AG1/packs_src/` (sha256 equal).
- 14:28 WCSS listing (lock, one command): `~/jobs/h3sg3` and `~/jobs/h2embmid` hold only array scripts and logs;
  `$L/smadcvpr/packs/{gan_weights.tar, gan_sg1.tar}` still present with the registered sha256; container
  `pytorch_latest.sif` dated Mar 2025.
- 14:29-14:46 GB10 run of the unchanged `generate_mip1.py` on the H4 gate pair: completes (994 s on the shared GB10),
  so the code is not x86-only; its PNG differs from the H100 gate PNG by mean 15.5, max 123 grey levels.
- 14:35-14:58 `build_inputs.py select` and `prep`: 604 photos prepared, 0 dropped.
- 14:58-15:00 `pair`, `shards`; WCSS packs and task directories built (`make_tasks.sh`).
- 14:59-16:37 Local test of the WCSS `run.sh` on smoke shard o00 (2 FRLL persons, 7 images): exit 0 (section 6).
- 15:01-15:05 Uploaded to WCSS: `smad-next/packs/AG1/` (gan packs hard-linked, ag1_inputs, ag1_code, SHA256SUMS
  verified with `sha256sum -c`), login-node import test with `~/dmenv/bin/python -I` (vendored modules import).
- 15:05 Pre-registration written (`prereg.md`). Pre-run review (experiment-reviewer subagent): GO WITH FIXES.
- 15:10-16:30 Amendment 1 (all fixes of the review, section 7 lists the bugs): readings A and B, matched bins on
  non-identity terms, session-gap sensitivity, AG2 bridge gate, G-b extensions, cuDNN deterministic, finiteness
  checks, dmenv fallback removed, RT on 152 persons, AG3 alpha 0, AG3T twin-dose arm, pooled primary pool, FERET
  decode fix. Shards rebuilt; WCSS packs and 13 task dirs re-uploaded to `smad-next/staging/AG1/` (not in ready/).
- 16:39-17:02 Dependency-path test (AG3-type shard reading the o00 result tar) with the final code: exit 0.
- 16:55 Self-check `mipgan_alpha(0.5)` vs `generate.mipgan`: max |w| difference 0.65 (section 6, open).
- ~17:10 Lead: generation moves to Athena (A100), WCSS unreachable, add the mirror rung for every host.
- 17:12-17:20 Mirror crops built (302), shards rebuilt (14), single Athena pack built and uploaded with the Athena
  scripts.
- 17:22 `sbatch tasks/AG1/ag1_smoke.sbatch` refused: "Invalid account or account/partition combination"; one
  `--test-only` for each of plgmultivision-gpu-a100 and plgrestorearc-gpu-a100: same. `sshare -U`: no association.
  Reported to the lead; no further probing (lead's rule).
- ~17:35 Lead: account will be plgrestorearc-gpu-a100; sbatch files changed and re-uploaded. Amendment 2 written.

## 3. Data

| Item | Path | Count | Hash / note |
|---|---|---|---|
| FRLL photos (R0 of the benchmark) | `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/BonaFide/NNN_{03,08}.jpg` | 102 x 2 | byte-identical to `frll_base` (checked on 001_03) |
| colorFERET | `/mnt/t7/Datasety/colorferet/dvd{1,2}/data/images/*/*_fa*.ppm.bz2`, gender from `ground_truths/name_value` | 100 persons x 2 dates (of 159 eligible: >= 2 fa dates, not val10, gender known) | |
| FRGC 2.0 | `/mnt/t7/Datasety/FRGC-2.0/FRGC-2.0-dist/nd1/...`; metadata `bbaselite_FRGC_2.0/bbaselite_data_frgc2.1.sql` (env nd1E00004/5 controlled, rec_subject emotiontype BlankStare, capture date, subject gender) | 100 persons x 2 dates (of 442 eligible) | |
| Selection | `/mnt/t7/smad_next/AG1/inputs/select.json` | 250 candidates + 102 FRLL | fc561e98... |
| Prepared crops (512, FFHQ-aligned) + 5 points | `/mnt/t7/smad_next/AG1/inputs/pack/{crops/, photos.json}` | 604 + 302 mirrored (`__s1m`) | photos.json dd070722... (after mirror); before mirror kept as `inputs/photos_before_mirror.json` |
| w600k embeddings (pairing only) | `/mnt/t7/smad_next/AG1/inputs/emb_w600k.npz` | 604 | 26efc2a2... |
| Pairs | `/mnt/t7/smad_next/AG1/inputs/{pairs.csv, sigma.json}`; copy `experiments/AG1/pairs.csv` | 302 | pairs.csv 19145659..., sigma.json 415c06f4... |
| Shard plans | `/mnt/t7/smad_next/AG1/inputs/shards/*.json`; table `experiments/AG1/shards.csv` | 14 shards, 3,833 images | shards.csv a870e61c... |
| Athena pack | DGX `/mnt/t7/smad_next/AG1/athena/ag1_pack.tar`; Athena `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AG1/ag1_pack.tar` | 2.9 GB | c6b9d2c9fce9ae589b7929bd0f0e03048e1b24cb88f7ff8b3babf7700bbbb406; inner: gan_weights.tar e06f19af..., gan_sg1.tar 1571c1a3..., ag1_code.tar 8504079b..., ag1_inputs.tar 58de590d... |
| Weight packs (registered, A28 / A33) | `/mnt/t7/smad_next/AG1/packs_src/{gan_weights.tar, gan_sg1.tar}` (+ .content); also WCSS `$L/smadcvpr/packs/` | | e06f19af..., 1571c1a3... |
| WCSS staging (superseded by Athena) | `/lustre/pd03/hpc-narolski-1790461090/smad-next/{packs,staging}/AG1/` | 13 task dirs, not in ready/ | ag1_inputs 7771484e..., ag1_code 735816eb... (pre-mirror) |
| Local tests | `/mnt/t7/smad_next/AG1/{smoke, localtest, tests}/` | | not data; never enter a manifest |

Dropped: none at prep (0 of 604). Mirror: all 302 hosts got a face on the mirrored crop.
Pool facts: FRLL 50 cycles (48 two-cycles); FERET 25 cycles; FRGC 19 cycles. Contributor w600k cosine, morphs / twins:
FRLL 0.140 / 0.905, FERET 0.161 / 0.836, FRGC 0.170 / 0.862. Reflect padding in the input alignment: FERET 145 / 200,
FRGC 13 / 200, FRLL 0. Session gap morph vs twin (reviewer, from photos.json): median 306 vs 121 days FERET, 160 vs
64 FRGC; only about 72 of 200 primary morphs have B within 60 days of the twin's A'.

Shard table (est = WCSS H100 estimate x 1.3 + 12 min; A100 rate unknown until the smoke job):

| Order | Shard | Inversions | Images | Est min | Needs |
|---|---|---|---|---|---|
| 0 | AG1_smoke_mip1 | 6 | 11 | 22 | |
| 1 | AG1_smoke_mip2 | 6 (e4e) | 8 | 19 | |
| 2-3 | AG1_mip1_frll_00 / _01 | 159 / 147 | 480 / 444 | 149 / 139 | |
| 4-5 | AG1_mip1_feret_00 / _01 | 174 / 126 | 421 / 304 | 147 / 109 | |
| 6-7 | AG1_mip1_frgc_00 / _01 | 177 / 123 | 428 / 297 | 149 / 107 | |
| 8-9 | AG1_mip2_frll_00 / _01 | 288 / 18 (e4e) | 678 / 42 | 149 / 21 | |
| 10-13 | AG1_mip1_{feret,frgc}_ag3_{00,01} | 0 | 180 each | 40 each | the two core shards of the pool |

Rung counts (incl. smoke): mip1 R2 606, R2i 605, R3 304, R3m 304, R4 304, RT 153, BR 108, AG3 401, AG3T 320;
mip2 R2 206, R3 104, R3m 104, R4 104, RT 102, BR 108.

## 4. Code (`/home/narolski/smad-next/src/AG1/`)

Run order: `build_inputs.py select -> prep -> pair -> mirror -> shards` (DGX CPU, `.venv-spark` python) ->
`athena/make_athena_pack.sh` -> upload -> `athena/ag1_smoke.sbatch` -> `athena/ag1_array.sbatch` (core list, then AG3
list with afterok) -> copy back -> `ag1_manifest.py frames | oracle | rt | pins` (DGX) -> scoring
(`make_score_root.sh` + `ag1_score.py`, GPU) -> `ag1_read.py --gate-only`, commit gates, then `ag1_read.py`.

| File | sha256 (first 8) | Job |
|---|---|---|
| build_inputs.py | 8fad6a50 | selection, input prep (H4 path), pairing (cycle cover), mirror crops, shard plans |
| ag1_gen.py | b2dc54eb | GPU generation of one shard; vendored gan1 code; `mipgan_alpha`; logs; peak memory |
| vendor/*.py | A33 hashes | generate.py 30dd21c0, generate_mip1.py dac17110, stylegan1.py 8e565643, arcface.py 6b68fc3a, lpips_vgg.py 264a4c58 (unchanged from gan1 24cc974) |
| athena/ag1_task.sh | 1d5036f4 | one shard on Athena: pack checks, needs, run, format check, result tar |
| athena/ag1_smoke.sbatch | e7d6579e | builds envs/AG1 (pinned), runs both smoke shards |
| athena/ag1_array.sbatch | 036c337e | production array over a list file |
| athena/make_athena_pack.sh | 4a631d12 | builds ag1_pack.tar and core.txt / ag3.txt |
| run.sh, make_tasks.sh | 544e4902, b27e7753 | WCSS slot-queue versions (superseded) |
| ag1_manifest.py | 9fcb826b | frames (prep_eval.align), FERET decode to lossless PNG, glint oracle, RT pixel check, pins |
| ag1_score.py | 29a87898 | A43 adapter copy (a43 -> ag1) over a41g_score.py f53612cb |
| make_score_root.sh | 10269d98 | job root from mambamorph-code c669666 + ag1_score.py |
| ag1_read.py | b1c80b8f | gates, ladder, readings A / B, shares, matched bins, session gap, AG2, AG3 / AG3T, Holm |
| test_reader_synthetic.py | c6daf46f | synthetic manifest for the reader test |
| test_alpha_equiv.py | ee5f247d | alpha-0.5 objective equality and run-to-run spread test |

Environment. DGX: `/home/narolski/mambamorph-code/.venv-spark/bin/python` (torch 2.12.1+cu130, GB10). Athena (to be
built by the smoke job): `/net/pr2/projects/plgrid/plggrestoration/smad-next/envs/AG1`, module Python/3.10.4, torch
2.2.1 (cu121), torchvision 0.17.1, numpy 1.26.4, pillow 10.2.0, pip 24.0; versions to `envs/AG1/versions.txt` and
`pip_freeze.txt`. pytorch_msssim 1.0.0 comes from the weights pack. Weights: StyleGAN v1 FFHQ-1024 (NVIDIA
karras2019 pkl f277a437..., PyTorch port 4618be6e...), e4e FFHQ + StyleGAN2 config-f, w600k_r50 fused, VGG-16
(torchvision 397923af), LPIPS v0.1. All loaded with `weights_only=True` (forced, also where vendored code asks
otherwise; e4e loads fine that way). Generator settings: inversion 500 Adam steps lr 0.02; MIPGAN 150 steps lr 0.03 x
0.95 / 6; TF32 off; cuDNN deterministic; `torch.manual_seed(0)`.

## 5. Results

None yet (no data image generated, no score read).

## 6. Checks

Verified:
- Vendored files equal the A33-registered hashes (checked at every `ag1_gen.py` start).
- Code runs on ARM: unchanged `generate_mip1.py` on the H4 gate pair (GB10, 994 s), `/mnt/t7/smad_next/AG1/smoke/`.
- WCSS `run.sh` logic on smoke shard o00 (GB10, local roots via `AG1_SN` / `AG1_PY`): 7 / 7 images, exit 0, tar
  sha256 0b1293bc... Logs `/mnt/t7/smad_next/AG1/localtest/AG1_o00-smoke-mip1_s0.stdout.log`. Per image: R2 901 s
  (incl. 1 inversion), R3 1,040 s, R4 1,522 s, RT 311 s, AG3 384 s on the shared GB10. Final loss: R2 1.67, R3 2.96,
  R4 5.42, RT 2.98, AG3(0.3) 4.82. Generator-side w600k cosines: R4 0.728 / 0.721; R3 0.966 / 0.965; AG3(0.3) 0.892 /
  0.502. Inversion cosine 0.987 to 0.993. Contact sheet `/mnt/t7/smad_next/AG1/localtest/smoke_sheet.jpg` looks right.
- Final code (ag1_code 735816eb, = the Athena code except the peak-memory lines) through `run.sh` on a dependency
  shard: needed latents extracted from the o00 tar, alpha 0 / 0.2 and AG3T 0.2 run, exit 0. Achieved dose (cosine to
  B): alpha 0 0.128, 0.2 0.366, 0.3 0.502, 0.5 0.721; AG3T 0.2 cosine to A' 0.932.
- Output format: 1024 x 1024 RGB PNG without ancillary chunks, FFHQ framing as the published MAD22 MIPGAN files
  (eyes ours (387, 482) / (634, 481), published MIPGAN-I (385, 476) / (640, 478)). `ag1_task.sh` checks every PNG.
- Mirror crops: written and read back, `fliplr(read) == original` asserted for all 302.
- Reader on the real design with synthetic scores: `/mnt/t7/smad_next/AG1/tests/reader_synthetic/` (exit 0).
- Scoring adapter selftest in a c669666 job root: 22 checks passed, `/mnt/t7/smad_next/AG1/tests/score_adapter/`.
- WCSS packs `sha256sum -c` OK on Lustre; dmenv import of the vendored modules OK.

Not verified:
- Anything on Athena: the environment build, the A100 timing and memory, the container-free path. The smoke job is
  exactly this test.
- mip2 path with the final code: the local mip2 smoke (old code) was still running at 17:45 (2 of 4 images done:
  R2 loss 2.43, R3 3.29; e4e loads under forced weights_only).
- `mipgan_alpha(0.5)` equal to `generate.mipgan`: the self-check gave max |w| difference 0.65 after 150 steps. Test
  `test_alpha_equiv.py` (exact forward equality + run-to-run spread of `generate.mipgan`) running, log
  `/mnt/t7/smad_next/AG1/localtest/alphatest/log.txt`.
- `ag1_manifest.py` and real scoring (need images). MixFaceNet-MAD has no AG1 scorer.

## 7. Dead ends and failures

- Cross-hardware: same code and inputs, GB10 vs H100: PNG mean |diff| 15.5, max 123 (H4 gate pair). Consequence: one
  platform for all data.
- RT (order-reversed twin) differs from R3 by mean 3.9, max 133 grey levels on the GB10: MIPGAN's loss is symmetric
  mathematically but not in floating-point summation order, and 150 steps amplify the difference. RT was first planned
  as a determinism check; changed to a run-to-run noise floor (prereg).
- The reviewer's bugs, all fixed in amendment 1: FERET sources are `.ppm.bz2` and `cv2.imread` would return None in
  the manifest builder (now decoded once to lossless PNG); main-verdict folded interval used only the lower bound
  (fixed to max(hi, 1 - lo)); G-b computed but never used (now gates every cell); matched bins on final loss would
  compare a biased subset (now non-identity terms, coverage >= 50%, also-reported only); FERET and FRGC shared the
  same bootstrap seed (now per pool); aligned flag wrong on re-runs (now stored); no finiteness check (added); dmenv
  fallback could mix torch stacks (removed); docstring claimed the input alignment was "imported unchanged" (the
  call sequence is re-typed from h4_prep.py; corrected and flagged).
- `python -I` ignores PYTHONPATH: the first GB10 run failed on `pytorch_msssim`; `ag1_gen.py` inserts the pack's
  `py/` directory itself.
- WCSS slot-queue plan (13 tasks staged 15:05 / 16:40) superseded by Athena; tasks remain in
  `smad-next/staging/AG1/` on Lustre, never in ready/.
- Athena submission refused (account association missing), 17:22; see section 10.
- A synthetic G-b result once printed as "{}": only my grep filter dropped the indented JSON; no bug.

## 8. Observations and ideas

- The GB10 can generate (15 to 60 x slower than an H100 while shared); a fallback only.
- With 48 two-cycles, FRLL R4 is about 50 dyads; FRLL cells will be wide.
- The twin-dose arm (AG3T) costs about 37 GPU-min and separates "second photo" from "second identity" in the dose
  reading; the reviewer's further idea, a GAN mirror twin on the primary pool, is now the R3m rung.
- SelfMAD's release file is held only on WCSS (`A12REL/selfmad_hrnet_w18`): scoring SelfMAD needs WCSS or a copy.
  MADation releases are local (`/mnt/t7/wcss_backups/madation_official_upload/madation_official.tar`).

## 9. Open items and next steps

1. Wait for the lead's message that Athena accepts plgrestorearc-gpu-a100; then submit the smoke job (section 10).
2. Smoke passes: record A100 seconds per image, peak memory, final losses, format check; message the lead; submit
   core array, then AG3 array with afterok; record job IDs and GPU-hours in `result.md`.
3. Copy result tars back with hash checks; `ag1_manifest.py frames / oracle / rt / pins`; author picks reading A or B;
   `ag1_read.py --gate-only`; scoring on GPU; `ag1_read.py`.
4. Open author questions: R2 class (A or B); approval of the H4 input alignment (blur / resampling); which SelfMAD row
   is primary; is ViT-B/16 alone deciding; is R3m a morph.
5. Finish the alpha-0.5 equivalence reading (test running).

## 10. Handover state (11 Nov ~17:45 CET)

- Athena: `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AG1/ag1_pack.tar` (+ .sha256) and
  `.../tasks/AG1/{ag1_task.sh, ag1_smoke.sbatch, ag1_array.sbatch, core.txt, ag3.txt}` uploaded; `results/AG1/`,
  `envs/` created; no job submitted (0 GPU-hours spent).
- Start command once the account works (one connection, with the lock):
  `flock -w 120 /tmp/smadnext-athena.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl 'cd /net/pr2/projects/plgrid/plggrestoration/smad-next && sbatch tasks/AG1/ag1_smoke.sbatch'`
  Log: `.../smad-next/logs/AG1smoke-<jobid>.out`; results `results/AG1/AG1_smoke_mip{1,2}.tar`.
- Then: `sbatch --array=0-7 tasks/AG1/ag1_array.sbatch tasks/AG1/core.txt` and
  `sbatch --array=0-3 --dependency=afterok:<core job id> tasks/AG1/ag1_array.sbatch tasks/AG1/ag3.txt`.
- If a task fails: its log is `.../logs/AG1-<job>_<index>.out`; tasks are idempotent (a verified result tar makes them
  exit 0), so resubmitting the same index is safe. Exit codes: 2 pack hash, 3 missing core tar, 4 copy hash, 5 (WCSS
  only), 6 no environment.
- DGX processes of this owner: local mip2 smoke (`/mnt/t7/smad_next/AG1/localtest/run_local.sh`, log
  `.../localtest/AG1_o01-smoke-mip2_s0.stdout.log`, about 30 more minutes) and `test_alpha_equiv.py` (log above).
  Both are tests only; if they die nothing is lost.
- WCSS: 13 superseded task dirs in `smad-next/staging/AG1/` (not in ready/); packs in `smad-next/packs/AG1/`.
- Compute spent: 0 cluster GPU-hours; DGX GB10 about 3 GPU-hours of shared tests; 0 USD.

## 11. Reproduce from scratch

```bash
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AG1
$P build_inputs.py select && $P build_inputs.py prep && $P build_inputs.py pair && $P build_inputs.py mirror && $P build_inputs.py shards
bash athena/make_athena_pack.sh                      # -> /mnt/t7/smad_next/AG1/athena/{ag1_pack.tar, tasks/}
flock -w 1800 /tmp/smadnext-athena.lock rsync -a /mnt/t7/smad_next/AG1/athena/ag1_pack.tar* plgpnarolski@athena.cyfronet.pl:/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AG1/
flock -w 600 /tmp/smadnext-athena.lock rsync -a /mnt/t7/smad_next/AG1/athena/tasks/ plgpnarolski@athena.cyfronet.pl:/net/pr2/projects/plgrid/plggrestoration/smad-next/tasks/AG1/
# on Athena: sbatch tasks/AG1/ag1_smoke.sbatch; then the two arrays (section 10)
# back on the DGX, after copying results/AG1/*.tar(+.sha256) to /mnt/t7/smad_next/AG1/results/:
$P ag1_manifest.py frames && $P ag1_manifest.py oracle && $P ag1_manifest.py rt && $P ag1_manifest.py pins
$P -I ag1_read.py --data /mnt/t7/smad_next/AG1/data --logs /mnt/t7/smad_next/AG1/results/x --photos /mnt/t7/smad_next/AG1/inputs/pack/photos.json --out /home/narolski/smad-next/experiments/AG1/read --gate-only
```
Note: `select` draws seeded (20261111) candidates; `prep` depends on the CPU detector and reproduces the crops only
up to onnxruntime numerics; the committed `photos.json` hash is the reference.
