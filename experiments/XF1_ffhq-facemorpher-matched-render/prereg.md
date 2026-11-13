# FFHQ FaceMorpher two-person morphs against one-photo renders (XF1): registration DRAFT

Owner: PR1 owner (lead's assignment, 13 Nov 2026, about 22:00). Draft written Fri Nov 13 22:14 CET (`date`). Status: **DRAFT, awaiting the pre-run check**. Nothing has been scored.

## 1. Origin and timing (stated exactly)
- The measure was proposed by tonight's strategy review, `experiments/reviews/REVIEW_ADV_STAGE3_STRATEGY_20261113.md`, Part 2, rank 3 (committed 93f4210, 20:40:43), before the sealed read. It is not motivated by the MAD22 result.
- It is registered **after** the MAD22 result exists. The owner has not opened `experiments/FINAL_sealed-benchmark-read/` and does not open it before this read is done.
- Development data only. FFHQ is the development set and is never reported as a benchmark.

## 2. Data (built by DATA tonight; development FFHQ only; no training person in any list)
Three images per host, for the 299 D12a hosts:
- **FM(H,B):** FaceMorpher two-person morphs at R4, `/mnt/t7/smad_next/DATA/D12a/manifest.csv` (sha256 9df020e1…; pairs.csv b3c4bfc2…). 299 distinct pairs on MS1 FFHQ hold-out frames.
- **FM(H,H):** the one-photo FaceMorpher render of the same host from the same unchanged tool, `/mnt/t7/smad_next/DATA/D1d/manifest.csv` (1bfa13ec…). This is the D12a row's `d1d_render_host` pointer.
- **H:** the plain MS1 hold-out photo (`/mnt/t7/smad_next/MS1/ffhq/src/<key>.png`). These are the same files MS1's FFHQ hold-out rows were scored from (checked on one row by sha256).

Checks:
- All 897 images are sha256-checked against the DATA manifests by the pack builder.
- All are 512×512 RGB. No FS1 training list (`train_A`, `train_B`, `train_Sb`) contains an FFHQ row (asserted).

Row list:
- `/mnt/t7/smad_next/XF1/xf1_rows.csv` (sha256 **ef4adf5ba22847f04ccf40d054fcda5b05b1546be08dde04b277dd2b5266e317**). Columns: id, path, label, klass H/FMHH/FMHB, host, partner, component, per-row sha256, source path.
- Host ids stay on /mnt/t7.

Limitations, stated in every report:
- (a) There is no sex matching in D12a.
- (b) Each person is host once and partner once. The pairing is a permutation with **12 components** (sizes 4, 4, 4, 4, 6, 8, 20, 22, 22, 34, 66, 105), and the bootstrap resamples these components. The largest holds 105 of the 299 hosts, so intervals are coarse.
- (c) FaceMorpher is a seen engine only for the SbFM arm. None of the 15 networks read here (A, B, Sb) trained on FaceMorpher or FFHQ.
- (d) FM(H,H) and FM(H,B) share the engine, the frame, the aligner and the storage, but D12a partner cost and blend strength were not matched to anything beyond the tool's R4 defaults.

## 3. Networks and platform
- **Networks:** the 15 FS1 fresh-seed networks `PN1_{A,B,Sb}_s{403..407}` (Sb is the frozen candidate). The tar sha256 values are asserted from their `.sha256` files and match `src/PR1/nets_pins.txt` for Sb. Development scoring of these networks is what PR1 already does.
- **Platform:** Athena plgrid-now, 1 A100 GPU, under 1 hour, container `smad_torch221_cu121_v1.sif`. It reproduced the stored scores byte for byte twice tonight (NE1 job 3550470; battery smoke 3551166).

## 4. Scoring path and gate (fixed before scoring)
- **Scoring path.** Each image enters the networks through the existing registered evaluation path, imported and called unchanged.
  - The scorer is `src/PN1/rescore.py` (sha256 6f6eede7…). It uses common.build_run_model plus the trained tensors, and ImageItems at the network's resolution (512 → 224 bilinear inside the loader, as for MS1's FFHQ rows). Logit without flip, batch 64, manifest order.
  - `smadcvpr/prep_eval.py` is not touched. There is **no preparation step**: the frames are already the 512 aligned frames used by MS1 and DATA.
- **Gate.** Per network, the job first scores the 3,417 registered gate rows (NE1 `ne1_gate.csv`, TT1 fam-gate order). `xf1_gate.py` then compares them with that network's TT1-FS pn1fs reference (`TT1_A100_pn1fs_fs/scores/<net>__gate.npz`): same ids, same order, float32 bytes identical.
  - **A network whose gate fails is not scored:** the job skips its xf1 rows and the reader never sees them.
  - A, B and Sb all have references.
- **Pack.**
  - `/mnt/t7/smad_next/XF1/xf1_pack.tar` (sha256 0e598a70…), holding the FS1 code and base weights unchanged, the 897 read images, the gate images and the manifest `xf1_eval.csv` with fam `gate` / `xf1`.
  - `/mnt/t7/smad_next/XF1/xf1_nets.tar` (5a0a00be…), holding meta.json and last_trainable.pt for the 15 networks, plus the gate references.
  - Job file `src/XF1/athena_xf1.sbatch` (fc2ed33f…); task folder with rescore.py, xf1_gate.py and the sbatch, plus SHA256SUMS.

## 5. Registered reads (`src/XF1/xf1_read.py`, sha256 cafbae64…; mock-tested with random logits only)
1. **Blend detection at matched rendering:** AUC of FM(H,B) against FM(H,H), per network.
   - Paired gains g_s = AUC(Sb_s) − AUC(X_s) for X ∈ {B, A}, seed by seed.
   - Bootstrap: joint, over the 12 pairing components; 2,000 draws, numpy default_rng(20261203), the same draws for every network.
   - **"present"** if the seed-mean gain is ≥ +0.03 AND its lower 95% bound is > 0 AND g_s > 0 on ≥ 4 of 5 seeds (the AB1 amendment-4 rule).
   - **"absent"** if the upper bound is < +0.03. Otherwise **"inconclusive"**.
   - Fewer than 4 seeds with both networks gate-passed: **"not read"**.
   - Each arm's seed-mean AUC is printed with its interval.
2. **Render reaction:** AUC of FM(H,H) against H, per network and as a seed-mean per arm with the same bootstrap.
   - **"no render reaction"** if the 95% interval lies inside [0.40, 0.60].
   - **"render reaction"** if the lower bound is > 0.60.
   - **"reversed render reaction"** if the upper bound is < 0.40.
   - Otherwise **"unresolved"**.
   - Own-rule (logit > 0) flag rates on H, FM(H,H) and FM(H,B) per network (range per arm), median logits, and FM(H,B) against H are printed.
3. **Adversary.** Every number is printed beside the standing adversary's floors and its same-data learner on these rows, via `check.exceeds` (all-cue and nuisance floors) for the contrasts `xf1_FMHB_vs_FMHH` and `xf1_FMHH_vs_H`.
   - This requires the adversary's pinned files; the request goes through the lead, with the row list above.
   - **"beyond hand-made statistics trained on the same data"** may be written for an arm only if its networks exceed the all-cue same-data learner (2.5% bound of the AUC difference > 0) on ≥ 4 of 5 seeds.
   - If the floors are not delivered before the read, the read prints "floor not delivered" and that sentence may not be written.

**What each outcome licenses.**
- "present" on read 1: Sb ranks a two-person FaceMorpher morph above the same tool's one-photo render better than B (or A), on an unseen face domain at matched rendering. Development data only, not held-out evidence, and subject to the limitations in section 2.
- "absent" / "inconclusive": no such statement.
- Read 2 is descriptive. A "render reaction" means the network's flags on FaceMorpher morphs are partly a reaction to the rendering path.

## 6. Predictions (stated before scoring)
- **Read 1:**
  - Per-arm seed-mean AUC FM(H,B) vs FM(H,H) about 0.50-0.62 for A, B and Sb.
  - Sb − B and Sb − A **"inconclusive"**, with seed-means in [−0.02, +0.04]. The 12-component intervals are wide.
- **Read 2:**
  - **"render reaction"** for all three arms (seed-mean AUC FM(H,H) vs H ≥ 0.75).
  - Own-rule flags on FM(H,H) well above those on H (H < 15%).
- **Read 3:** no arm exceeds the all-cue same-data learner on read 1.

## 7. Process
1. This draft goes to the lead for the pre-run check, together with the request for the adversary's floors on the row list (sha256 above).
2. After GO and the fixes: register (commit), upload the two tars and the task folder to Athena under `smad-next/{packs,tasks}/XF1`, and put `athena_PR1_xf1.cmd` in the dispatcher's queue with the registration hash in its header.
3. Fetch and verify the result tar, then read once (`xf1_read.py`, nice 19).
4. One results review, then a report with a CLAIMS block.
