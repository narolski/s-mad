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

---

## Revision b (DRAFT, not binding; `date`: Fri Nov 13 22:25 CET; lead's order after DATA built D12b)
This revision replaces sections 2 to 6 above. The original draft (sections 1 to 7) is kept for the record; it is on hold per `experiments/reviews/PRERUN_XF1_20261113.md`, finding F1. Nothing is uploaded or scored.

**Label (F5).** "Post-freeze development diagnostic, registered after the sealed read. It cannot change the frozen Sb recipe, its seeds or any headline claim, and it is reported in diagnostics only." The measure was proposed by the strategy review at 93f4210 (20:40:43), before the sealed read. It is registered after the MAD22 result exists, and `experiments/FINAL_sealed-benchmark-read/` has not been opened.

**Contrast.** FM(H,B) (DATA D12a, R4) against W, the matched FaceMorpher warp-only image.
- W comes from DATA D12b (21a25a2, f253a18; manifest 152a492b…). It is H warped toward the H-and-B mean shape with no blending, made by the unchanged AR1 call `variants.one(("facemorpher", …))`, on the same canvas and in the same format as FM(H,B).
- The contrast is read in two forms:
  - **whole frame**;
  - **face-only**: the surround is blanked to constant grey (128, 128, 128) on both classes. The blanking uses the unchanged AR1 call `src/AR1/blank.py` `one()` (sha256 c8d8055f…). Its hull is the convex hull of the 106-point mean geometry 0.5·tem(H) + 0.5·tem(B), from the MS1 `.tem` files, which exist for all 299 pairs.
- H is not a class in any contrast. It is kept only for the own-rule flag prints.

**DATA caveats.**
- Outside the face mask, W keeps H, while FM(H,B) averages H and B over the whole frame.
- 233 of 299 morphs carry half-grey border regions (exactly-one-black share > 0.01).
- The face-only form removes the first caveat outside the hull. It does not remove differences inside the hull.
- On the superseded rows, the adversary's same-data learner reached 0.90-0.945 and the surround alone 0.849.

**Gate before any network scoring (binding once registered).**
- The adversary computes, on CPU, the same-data shortcut learner fitted on Sb's training list, applied to the **face-only** form of FM(H,B) vs W.
- **If its AUC is ≥ 0.90**, XF1 is closed as "not run: the matched contrast is solved by hand-made statistics trained on the same data; a network read would be uninformative".
- **If it is below 0.90**, XF1 goes to a second pre-run check with fixes F2-F8, and only then to registration, upload and the dispatcher's queue.
- The learner's AUC on the whole-frame form is printed beside it and does not decide.

**Fixes from the first pre-run check, carried into this draft.**
- **F2: strata.** Read 1 per arm is printed within terciles of the exactly-one-black share and of |IED gap|, from D12b `pair_measures.csv` (29d4655a…); terciles are in the row list. Descriptive.
- **F3: bootstrap.** Decided by a cycle-block bootstrap: blocks are runs of 5 consecutive hosts along each pairing cycle, giving 64 blocks; 2,000 draws, rng 20261203. A leave-one-component-out range and a host bootstrap are printed as sensitivities.
  - Detectable gain, by the reviewer's Hanley-McNeil estimate (SE about 0.022 at AUC 0.65 with 299/299, not reduced by averaging seeds): "lower bound above 0" needs an observed gain of about +0.045; 80% power needs a true gain of about +0.06 to +0.07; "absent" needs an observed gain of about −0.015 or less. The predicted gains (−0.02 to +0.04) therefore almost guarantee "inconclusive".
- **F4: limitation.** Random-identity pairs. glintr100 cosine H–B from the existing MS1 embeddings: min −0.148, median 0.000, max 0.292 (all pairs are dissimilar by MS1's construction). About half the pairs are likely cross-sex. They are not representative of attacker-chosen pairs.
- **F5:** the label above. The predictions below were revised after the reviewer's and DATA's pixel statistics were seen, and are disclosed as such.
- **F6: platform.** Athena plgrid-now with `smad_torch221_cu121_v1.sif` reproduced the stored scores byte for byte for Sb 403-407 (NE1 3550470) and Sb 403 (battery 3551166). **A and B have never been gated on Athena.** If they fail the in-job gate, the Sb − B and Sb − A reads are "not read".
- **F7: no deletion.** The builders rename an existing output to `.bak-<stamp>` and never call rmtree. `build_xf1b_rows.py` does this already; the pack builder gets the same change before the second check.
- **F8: adversary columns.** Contrasts are selected by `klass` (FMHB = 1, WARP = 0) and by `form`, never by label. `component` is the cross-fitting unit; one component holds 105 of 299 hosts. `block` is the bootstrap unit.

**Row list (whole-frame form), pinned.** `/mnt/t7/smad_next/XF1/xf1b_rows.csv`, sha256 **e4df7801b0d589c580a561f3a422ee61b10af1269b4a01e63cb97f819eeb73f8**; built by `src/XF1/build_xf1b_rows.py`.
- 897 rows: FMHB, WARP and H × 299 hosts.
- Columns: id, path, label, klass, form, host, partner, component, block, excl_border(_t), ied_gap(_t), cos_HB, sha256, src.
- The face-only rows (FMHB and WARP, form "face") are added once the blanking step is cleared; see the operations question to the lead.

**Reads, if the gate is passed.** As in section 5, with "W" in place of "FM(H,H)" and both forms. The registered decision is on the face-only form. Read 2 is replaced by own-rule flag rates on H, W and FM(H,B), printed only. Read 3 is the adversary floors on both forms.

**Predictions (revised after seeing the reviewer's and DATA's statistics):**
- The face-only gate learner reaches about 0.80-0.92.
- If the gate is passed: arm AUCs on the face-only form 0.50-0.65, and Sb − B and Sb − A "inconclusive".

**Face-only form built** (`date`: Fri Nov 13 22:26 CET; lead's option (a)).
- **Builder:** `src/XF1/build_xf1b_face.py`.
- **Blanking call:** the unchanged `src/AR1/blank.py` `one()` (sha256 c8d8055f…, asserted), with its output root set at run time to /mnt/t7/smad_next/XF1.
- **Output:** 598 face-only copies in `/mnt/t7/smad_next/XF1/blank/bg/`. The face-blanked copies it also writes stay in `blank/face/`, unused.
- **Shared mask, asserted per pair:** the FM(H,B) copy and the W copy are grey everywhere outside the same hull of 0.5·tem(H) + 0.5·tem(B).
- **Manifest:** `blank/xf1b_face_manifest.csv` (fe5333e3…), with input, tem and output sha256 per row; `blank/SHA256SUMS` (b7d79c95…).
- **Row list re-pinned with both forms:** `/mnt/t7/smad_next/XF1/xf1b_rows.csv`, 1,495 rows (whole 897 + face 598), sha256 **4adcf914fba651f3b1b1ccfc5ea4b3e03155357aa5c84804180513da5925b271**. The previous whole-frame file was renamed to `.bak-20261113222636`.

## Revision b2 (DRAFT, not binding; `date`: Fri Nov 13 22:45 CET; fixes of the second pre-run check, `experiments/reviews/PRERUN_XF1_B_20261113.md` (44276e5), and the lead's answers)
This revision supersedes the "Reads" and "Predictions" paragraphs of revision b. Nothing is uploaded or scored.

**Label.** Post-freeze development diagnostic, registered after the sealed read. It cannot change the frozen Sb recipe, its seeds or any headline claim, and it is reported in diagnostics only.

**Gate disclosure (fix 6).**
- The gate was registered at dcb66a4 before computing and computed at 4781d01 (pinned stage 14).
- Same-data learner (train_Sb list, face-only form): gbt 0.859 [0.836, 0.882], logreg 0.856 [0.833, 0.878]. Both upper bounds are below 0.90, so XF1 runs.
- The learner on the A list gives gbt 0.885 [0.859, 0.910]; its upper bound crosses 0.90 (printed, does not decide).
- The gate is final: it was not recomputed with other learners or features.
- The face-only file-size floor is 0.666.

**DATA caveat: the halo ring (fix 3; the lead's answer).**
- About 7.6% of the face-only hull (per pair 6.8–9.0%; `/mnt/t7/smad_next/XF1/xf1b_ring.csv`, sha256 23f51cf3…, by `src/XF1/xf1b_ring.py`) is a ring outside the tool's eroded mask.
- In that ring, FM(H,B) is the unwarped H/B average (ghost edges and the seam) and W is raw H. Both facts were verified on 299 of 299 pairs.
- "Face-only" therefore means face plus the tool's halo. The lead accepts "face plus halo ring" as the deciding form, disclosed. Every read is also printed within ring-share terciles. There is no eroded-hull build now.

**Training disclosure (fix 5).**
- No arm trained on blanked copies, so the grey surround is equally unfamiliar to all three arms.
- Only Sb trained on surround-matched splices (lad_S0, S3, S4: 156, 156 and 430 rows), which have the structure of this contrast. Sb's face-only advantage, if any, is partly the transfer its recipe was built for.
- The whole-frame form is surround-dominated (surround floor 0.849, all-cue gbt 0.981), so it is printed only.
- The whole-minus-face AUC per arm is printed as the blanking-shift control.

**Rules (fix 4; decision form face-only; `src/XF1/xf1_read.py`).**
- **Contrast:** FM(H,B) (klass FMHB, label 1) against W (klass WARP, label 0), selected by klass and form.
- **Bootstrap:** 64 cycle blocks, 2,000 draws, rng 20261203; the same draws for all networks, forms and adversary sources. Leave-one-component-out ranges and a host bootstrap (rng 20261204) are printed as sensitivities.
- **Gains:** Sb − B is the **primary** pair. Sb − A is **secondary**, because A's training list has no warp-only (lad_R2w) negatives while B and Sb have 156 each. Each pair uses the AB1 amendment-4 rule:
  - **"present"** if the seed-mean is ≥ +0.03, the lower bound is > 0, and the gain is positive on ≥ 4 of 5 seeds;
  - **"absent"** if the upper bound is < +0.03;
  - otherwise **"inconclusive"**;
  - **"not read"** if fewer than 4 seeds have both networks gate-passed.
- **Precedence:** "not read", then **"all arms at ceiling"** (every arm's lower bound ≥ 0.95), then **"ceiling, not informative"** (X's seed-mean AUC ≥ 0.97, where a +0.03 gain is impossible), then the gain rule.
- **Floor rule:** an arm whose 95% interval contains 0.50 **"does not separate blend from warp"**. An interval entirely below 0.50 is printed as "below 0.50 (reversed)".
- **Licences per arm:**
  - (a) Interval containing 0.50 or below it: "this blend is not what the networks flag".
  - (b) Lower bound above 0.50 but not (c): "consistent with blending and noise averaging; no evidence beyond low-level statistics".
  - (c) The network exceeds its own training list's same-data learner, using gbt (the gate's model). "Exceeds" means the block-bootstrap 2.5% bound of AUC_net − AUC_learner is > 0. It must hold on ≥ 4 of 5 seeds, and then the licence reads "beyond hand-made statistics trained on the same list".
  - **No outcome licenses "detects identity mixing"**: there is no same-person blend control.
- **Adversary comparisons:** made against `experiments/ADV_shortcut-floors/floors/xf1b_rows_scores.csv` (stage-14 pins) using `block`. `check.exceeds` has no xf1b contrast. The reader asserts the committed learner and floor AUCs (learner_Sb gbt face 0.8591, all-cue gbt face 0.9166, file single face 0.6662). Every source is printed beside each network in both forms.
- **Printed strata:** terciles of the exactly-one-black share, |IED gap|, halo-ring share and cos_HB. Own-rule flags (logit > 0) on H, W and FM(H,B) are printed.

**Predictions (revised; disclosed as written after the reviewers' and DATA's pixel statistics):**
- Face-only arm AUCs: Sb 0.60–0.80, B 0.55–0.75, A 0.50–0.70.
- Sb − B "inconclusive".
- No arm reaches licence (c).

**Pins (all new files; the revision-a pack and rows are kept, unused).**
- Pack: `/mnt/t7/smad_next/XF1/xf1b_pack.tar` **cd57efbafc33603bf24429c257672de9185eeeeb2ec6af7436a647c0118a88a5** (1,495 xf1 rows + 3,417 gate rows; manifest xf1b_eval.csv 8f07ce77…).
- Nets: `xf1b_nets.tar` **5a0a00befd23323e4757fb4c2b9b383f3762852afc4354972db54283114523e5** (same content as revision a).
- Task folder `/mnt/t7/smad_next/XF1/tasks_XF1/`: SHA256SUMS e3c0599e…, holding rescore.py 6f6eede7…, xf1_gate.py 27b62b5a… and athena_xf1.sbatch 1105c787….
- Code (`src/XF1/SHA256SUMS`): build_xf1_pack.py 46d9733a… (no rmtree; renames to .bak-<stamp>), build_xf1b_rows.py ee37a92a…, build_xf1b_face.py 5d58c6ff…, xf1b_ring.py 6d68ab09…, xf1_read.py 729d67ed….

**Mock tests:** randomised logits only, with real adversary sources and rows. Every branch was exercised:
- "random": floor rule and licence (a); Sb − B "inconclusive"; Sb − A "absent";
- "ceiling": "all arms at ceiling";
- "ceilB": "ceiling, not informative" for Sb − B;
- "sbgain": "present" and licence (b);
- "gatefail": B 404 and 405 fail, so Sb − B is "not read" and B is "below 0.50 (reversed)".
