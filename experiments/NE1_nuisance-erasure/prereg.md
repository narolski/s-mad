# Nuisance directions in the frozen candidate's own features (NE1): registration draft

Owner: TT1 owner, on the lead's assignment (13 Nov 2026, from the IDEAS mechanism ledger, commit 6db5154, rank 2; the
lead's draft is `experiments/IDEAS_mechanism-ledger/TEST_nuisance-erasure.md`). Status: draft for the pre-run check.
It is registered at the git commit that changes this status line. At this commit no feature has been extracted and no
head has been fitted.

What NE1 is: a post-freeze diagnostic on stored and extracted features of development rows. It does not change the
frozen candidate (arm Sb, seeds 403-407) and does not touch the sealed read. It is not a new method. Any arm it licenses
is post-freeze and goes through the method-selection rule.

## 1. Question

Are two known failures of the frozen candidate separable directions in its penultimate features?
- The reaction to a blanked-in black border (TT1 Z3: Sb flags 2.9-16.3% of training-source camera photos once a
  CFP-shaped border is added, and 0% without it).
- The flags on same-person face splices (S3).

If a last-layer change removes them without losing detection on development landmark morphs, debiasing or group-robust
arms are worth H100 time. If not, the features lack a separating signal, and only new data or a new signal can help.

## 2. Networks (frozen; development rows only)

- Sb seeds 403-407, last checkpoints, from the FS1 result tars pinned in the C2P registration (2715e48): Sb 403
  `8dec83b8…`, 404 `de670689…`, 405 `3a3a53fd…`, 406 `d2cf5faa…`, 407 `865c0455…`. Full values are in
  `/mnt/t7/smad_next/PN1/results_fs/*.tar.sha256` and checked by the job.
- Features: the input of the linear head `head.cls`, an L2-normalised 512-d CLIP feature. Extracted with
  rescore.py's model build (`common.build_run_model` + `last_trainable.pt`; code from the FS1 tree, base weights
  `4b869929…`). Logit without flip, eval mode, batch 64, list order, PyTorch defaults (TF32 off).

## 3. Rows (all development; no benchmark, sealed, FRLL, MAD22, MorDIFF, DiM, H1, FEI or CASIA-WebFace row)

| Set | Rows | Source manifest |
|---|---|---|
| T (fit) | 5,535 unique images of Sb's training manifest (`train_Sb.csv`, `2cf3fda3…`; 8,386 rows with repeats). Group = `kind` (14 kinds: af0_photo, af0_photo61, af0_half, af0_half61, af0_zero, af0_u50, af0_u5061, lad_R0, lad_R2w, lad_R4, lad_half, lad_S0, lad_S3, lad_S4) | FS1 tree |
| L (landmark ladder and splices, read) | FS1 `pn1_eval.csv` (`f0f29f22…`) rows fam ladder (6,093) and splice (4,365), development and test hosts | FS1 tree |
| C (detection, read) | FFHQ landmark_combined orig morphs (1,000) and resmatch genuine (2,000), fam ffhq_lcomb | FS1 tree |
| G (gate and camera references) | the 3,417 TT1 fam-gate rows of `tt1_score.csv` (`c0055b51…`): R_cam 417, R_ffhq 2,000, M_ffhq 1,000; scored in that list's order | TT1 pack |
| B (border) | the 2,919 border-matched references R_cam^border (417 camera photos × 7 family masks, constant-colour blanking; TT1-S §2.3) | TT1 pack |
| S (storage) | MS1 FFHQ hold-out, fam ms1ffhq of the MS1 evaluation manifest (`d1fab6ad…`): native photos 300, fm61 copies 291, amsl112 copies 290 (u50 and zero rows extracted, printed only) | MS1 tree |

## 4. Person-disjoint split (fixed now)

- **Border.** The 417 R_cam photos belong to 406 hosts (FRGC / colorFERET persons; 11 hosts have two photos). Half A
  is the hosts with sha256(host) first hex digit in 0-7; half B is the rest. Every photo of a host, and its seven
  bordered copies, falls in that host's half. The eraser is fitted on half A (camera photos and their bordered copies);
  every border read and border probe uses half B only. Bootstrap units are hosts, not photos.
- **Storage.** The 300 MS1 hold-out persons are split the same way on sha256(host): half A fits the storage eraser
  (native against fm61 and amsl112 copies); reads use half B only.
- **Same-person splices and detection** (sets L, C): no eraser is fitted on them, so no split is needed. The heads are
  fitted on T only, which contains no L, C, B, G or S image and no L, C, B, G or S host (asserted by id and path in the
  pack builder; host overlap counted 0 for every set).
- **Hosts in T.** pn1lib's catalog host for AF0 and ladder ids; for the SM1 warped halves (`sm1h_<db>_<n>_h{A,B}`) and
  the training splices (`sp2_S<k>_<tool>_<db>_<n>`), the ladder pid `<db>:<n>` they were made from (asserted to be a
  ladder host). 637 hosts in T.
- **Overlap inside the read sets.** 291 of the 417 R_cam photos are also ladder R0 genuine rows of L (the same source
  image, under another path). Both are read rows; nothing is fitted on L, so this is not a leak. The border eraser's
  half-A rows include some of those photos; the border and splice reads are on different images.

## 5. Heads (all on the same extracted features of one network)

- **H0.** The original head (reference). Its logits on G are the gate.
- **H1.** Logistic refit on T, class-balanced (sklearn LogisticRegression, L2, C = 1, max_iter 5000; repeats removed,
  unique images).
- **H2.** Group-balanced refit on T: equal total weight per kind (14 groups), class-balanced within each group's label.
  C is chosen from {0.01, 0.1, 1, 10} by 5-fold cross-validation on T, grouped by host (pn1lib catalog host for AF0 and
  ladder ids), maximising worst-group accuracy.
- **H3.** Border erasure, then H1. Eraser: mean-difference projection. d = mean(feature of the bordered copies) −
  mean(feature of the unbordered photos) over half A of B and G-R_cam; d̂ = d / ‖d‖; every feature x → x − (x·d̂) d̂.
  Then the H1 refit on erased T features. Rank 1, one direction.
- **H4.** Storage erasure, the same: d = mean(stored copies) − mean(native) over half A of S. Then H1 on erased T.

**Operating point (fixed rule; no head gains by moving it).** Each head's threshold is the smallest t such that its
flag share on G-R_cam (417 camera photos) is ≤ H0's own-rule share there. H0's own threshold stays at logit 0. Flag rule:
score > t. If H0 flags k of the 417 photos, t is the (k+1)-th largest score of that head on them; if k = 0 (TT1-FS
found 0.000 for Sb on R_cam), t is the head's largest R_cam score. This makes every head's threshold rest on its
most extreme camera photo when k = 0; it is the registered rule and is printed beside each read.
- **H2 tie rule.** Equal worst-group accuracy across C values: the smaller C (stronger L2) is chosen.
- **Matched S4 recall (read 2).** For each head, the cut is the largest t with share(S4 score > t) ≥ H0's own-rule S4
  recall; the S3 share is read at that cut.

## 6. Reads per network and head

1. **Border.** Flag share on half-B bordered copies, pooled over the seven masks and per mask (CFP-FF, MSU-MFSD and
   OULU-NPU named). Border removal fraction = 1 − flags(Hk) / flags(H0), pooled, each head at its own threshold.
   Computed only if H0 has at least 10 flagged half-B bordered copies on that seed; otherwise that seed is "floor".
2. **Same-person splices.** On set L, S3 flag share at the threshold where the S4 recall equals H0's own-rule S4
   recall (dev + test hosts, OpenCV-style), and the full front (S3 flag share against S4 recall, printed).
3. **Detection.** AUC of landmark_combined orig morphs against resmatch genuine (set C).
4. **Storage.** Flag share (head threshold) on half-B stored photo copies minus that on the same persons' native
   photos, at fm61 and at amsl112 (Δf).
5. **Probes (printed).** Logistic probe AUC (5-fold, grouped by host, C = 1, class-balanced) for border presence on
   half-B bordered copies against half-B R_cam photos, before and after the H3 eraser; and for stored (fm61, amsl112)
   against native on half-B S photos, before and after the H4 eraser.
6. **Printed beside the reads.** Each head's threshold, R_cam share, own-threshold S3 share and S4 recall, the S3/S4
   front at five S4 quantiles, landmark_combined recall at the head threshold, H2's chosen C with the grouped-CV
   worst-group accuracy per C, and H0's recomputed logit against the extracted one.

## 7. Outcome table (fixed before reading; "on ≥ 4 of 5 seeds", computed over seeds that are not "floor")

| Result | Reading | Next |
|---|---|---|
| H3 removes ≥ 70% of H0's border flags AND landmark AUC within −0.01 of H0 | the border reaction is a separable direction | the lead may register a border nuisance head or erasure layer, read beside the border-crossed data arm (Sbx) |
| H3 removes < 50%, OR costs > 0.02 AUC | border and detection share features | only data or a new input treatment can help; no adversarial arm |
| Otherwise | "inconclusive (border)" | — |
| H2's S3 share at matched S4 recall ≥ 0.05 below H0's | reweighting can move the trade-off | the lead may register a group-DRO arm with strong L2 |
| H2 within 0.03 of H0 AND of H1 | the same-person-splice flags are not a weighting problem | group DRO / JTT closed for this backbone; the second-identity route needs a new signal |
| Otherwise | "inconclusive (splices)" | — |
| H4 lowers the amsl112 Δf by ≥ 0.02 below H0's with AUC within −0.01 | residual storage reaction is a separable direction | a note for the next version; no claim about the frozen network |
| Otherwise | "no separable storage direction shown" | — |

Counting. A row holds if its condition is met on at least 4 seeds. Border rows count only non-floor seeds; with fewer
than 4 non-floor seeds the border reads "floor (not testable)". Ties between "separable" and "shared" cannot occur on 5
seeds (each needs ≥ 4 and the conditions exclude each other). Comparisons use point values; the bootstrap intervals of
section 9 are printed, not used.

**Kill condition.** A network whose extraction fails (no feature file) is "not available". With fewer than 4 available
networks, NE1 reads "not available" for every row. A gate failure (section 8) does not remove a network; it labels it.

**H1 control.** If H1 alone moves a read by as much as H3 or H2, that change is attributed to refitting, not to erasure
or reweighting. The table rows compare H3 and H2 with H0, and H1 is printed beside them.

## 8. Platform and gate

- **Platform.** Athena, partition plgrid-now (A100 40 GB, sm_80), the container
  `smad_torch221_cu121_v1.sif` (`fedeff10…`; torch 2.2.1, CUDA 12.1, timm 1.0.27, numpy 1.26.4, Pillow 10.2.0). This is
  the same model and software as the stored FS1 and TT1 scores (pn1fs A100 PCIe 40 GB; a second A100 PCIe host, se1d,
  was byte-identical on the same rows today).
- **Gate per network.** H0 logits on the 3,417 G rows, scored in `tt1_score.csv` fam-gate order at batch 64, must be
  byte-identical (float32) to the same rows scored on pn1fs in TT1-FS (`TT1_A100_pn1fs_fs.tar`, `<net>__gate.npz`).
- **Also checked:** logit = feature · w + b within 1e-4 on every row (the stored feature is the head's input).
- **If the gate fails** (Athena's A100 may be SXM4; amendment 14 found PCIe and SXM4 byte-identical, but this is
  unproven here), that network's numbers are still compared only between heads on the same extracted features
  (H0-H4). No number is compared with stored logits, and the result is labelled "platform not certified". This follows
  the draft's fallback; the kill condition above applies only if extraction itself fails. NE1 compares heads on one
  set of features, so the platform affects only comparability with TT1's stored numbers, not the table's logic.
- **Job.** One 1-GPU job under 1 hour (plgrid-now limit), at most 16 CPUs and 120 GB, memfs. One pack and one network
  tar in, one result tar out with sha256; copied back to `/mnt/t7/smad_next/NE1/` and verified. The job file goes into
  the dispatcher's queue (`athena_ne1_extract.cmd`). The dispatcher submits; the owner does not.

## 9. Analysis (DGX CPU, after the result tar is verified)

`src/NE1/ne1_heads.py`, run once. Bootstrap intervals (2,000 draws, `default_rng(20261128)`, persons) are printed for
the border share, the S3 share at matched recall and the AUC; the table rows use point values on ≥ 4 of 5 seeds.

## 10. Code, inputs and job (pins at registration)

| File | sha256 |
|---|---|
| `src/NE1/build_ne1_pack.py` | `7055c7ec250880d9…` |
| `src/NE1/ne1_extract.py` | `5082d0e37f947ded…` |
| `src/NE1/ne1_gate.py` | `79f45a880f8f9602…` |
| `src/NE1/athena_ne1.sbatch` | `bdfd96ef10ed1ee9…` |
| `src/NE1/ne1_heads.py` | `8c2063ce390ef400…` |
| `ne1_pack.tar` (code, base weights, images, manifests; 8.9 GB) | `4f88b779f2229ba3…` |
| `ne1_nets.tar` (five Sb meta.json + last_trainable.pt, TT1-FS gate refs) | `010337f9482ad442…` |
| `ne1_train.csv` (5,535 rows) | `457f77d05fcb0c88…` |
| `ne1_gate.csv` (3,417 rows) | `a3df29327690f24b…` |
| `ne1_read.csv` (17,857 rows: L 10,458, C 3,000, B 2,919, S 1,480) | `06cc63160b67d2cd…` |

Full values: `/mnt/t7/smad_next/NE1/*.sha256` and `git show` of this commit.

- **Tests before the job.** ne1_extract.py on 8 rows of each manifest, one network, on the DGX: features of norm 1,
  logit = feature · w + b within 5e-7 (no score printed or read). ne1_heads.py in `--mock` mode (random unit features
  with the real manifests and H0 weights) on one network: every read and interval computed, about 2 min per network.
- **Job.** `sbatch -p plgrid-now -A plgmultivision-gpu-a100 -t 01:00:00 athena_ne1.sbatch` from the Athena task folder
  `tasks/NE1` (scripts + SHA256SUMS); inputs in `packs/NE1`; output `results/NE1/NE1_feats.tar` + `.sha256`. Expected run
  time: about 5-10 min to copy and unpack 8.9 GB into memfs, about 70-90 s of extraction per network (TT1-FS: about 80 s
  per network for 30,994 rows on an A100 PCIe), about 20 min in all; limit 1 h. Submitted by the dispatcher.
- **Analysis.** `ne1_heads.py` on the DGX CPU (thread caps 2, nice 10), sklearn 1.9.0, numpy from the analysis venv
  (`mambamorph-code/.venv-spark`), run once after the result tar is verified in two places.
