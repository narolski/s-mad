# Nuisance directions in the frozen candidate's own features (NE1): registration draft

Owner: TT1 owner, on the lead's assignment (13 Nov 2026, from the IDEAS mechanism ledger, commit 6db5154, rank 2; the
lead's draft is `experiments/IDEAS_mechanism-ledger/TEST_nuisance-erasure.md`). Status: registered (this commit changes the status line; draft 2a31a56, pre-run check GO WITH FIXES at 653a766, fixes
F1-F8 applied). At this commit no feature has been extracted and no head has been fitted.

What NE1 is: a post-freeze diagnostic on stored and extracted features of development rows. It does not change the
frozen candidate (arm Sb, seeds 403-407) and does not touch the sealed read. It is not a new method. Any arm it licenses
is post-freeze and goes through the method-selection rule.

## 1. Question

Are two known failures of the frozen candidate separable directions in its penultimate features?
- The reaction to a blanked-in black border (TT1 Z3: Sb flags 2.9-16.3% of training-source camera photos once a
  CFP-shaped border is added, and 0% without it).
- The flags on same-person face splices (S3).

If a last-layer change removes them without losing detection on development landmark morphs, debiasing or group-robust
arms are worth H100 time. If not, NE1 shows only that a rank-1 linear eraser or a last-layer reweighting does not
remove them (section 7 wording); it does not show what else could. Last-layer refits on held-out data follow deep
feature reweighting (Kirichenko et al., 2023), which retrains the last layer on held-out, group-balanced data: here
H1d/H2d on L's development hosts.

## 2. Networks (frozen; development rows only)

- Sb seeds 403-407, last checkpoints, from the FS1 result tars pinned in the C2P registration (2715e48): Sb 403
  `8dec83b8…`, 404 `de670689…`, 405 `3a3a53fd…`, 406 `d2cf5faa…`, 407 `865c0455…`. Full values are in
  `/mnt/t7/smad_next/PN1/results_fs/*.tar.sha256` and checked by the job.
- Features: the input of the linear head `head.cls`, an L2-normalised 512-d CLIP feature. Extracted with
  rescore.py's model build (`common.build_run_model` + `last_trainable.pt`; code from the FS1 tree, base weights
  `4b869929…`). Logit without flip, eval mode, batch 64, list order, PyTorch 2.2 defaults (matmul TF32 off, cuDNN TF32 on), as
  rescore.py ran in TT1-FS; the gate checks the match.

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
- **Same-person splices** (set L): H1d, H1dc and H2d are fitted on L's 100 development hosts and every splice read
  uses L's 191 test hosts (disjoint, asserted). No eraser is fitted on L or C.
- **T.** The T-fitted heads contain no L, C, B, G or S image or host (ids, paths and hosts asserted disjoint in the pack
  builder, F6).
- **Hosts in T.** pn1lib's catalog host for AF0 and ladder ids; for the SM1 warped halves (`sm1h_<db>_<n>_h{A,B}`) and
  the training splices (`sp2_S<k>_<tool>_<db>_<n>`), the ladder pid `<db>:<n>` they were made from (asserted to be a
  ladder host). 637 hosts in T.
- **Overlap inside the read sets.** 291 of the 417 R_cam photos are also ladder R0 genuine rows of L (the same source
  image, under another path). The border eraser's half-A rows include some of those photos, whose derived splices sit
  in L. So the splice reads of heads with an eraser use half-B test hosts only (F7). The reference pool P (section 6)
  holds L's R0 rows of development hosts, which H1d/H2d are fitted on; P is used only for the border and storage
  ranks of the T-fitted heads.

## 5. Heads (all linear, on the same extracted features of one network)

Pre-run check (PRERUN_NE1_20261113.md, 653a766, GO WITH FIXES) fixes F1-F8 are applied in this section and below.

| Head | Eraser | Fit |
|---|---|---|
| H0 | none | the original head (reference; its logits on G are the gate) |
| H0e | border, half A | H0's w, b on erased features, no refit |
| H0e4 | storage, half A | H0's w, b on erased features, no refit |
| H0ec | border, half B (ceiling) | H0's w, b, no refit |
| H0em | morph direction of T | H0's w, b, no refit (erasure-works check) |
| H1 | none | logistic refit on T, class-balanced, C = 1 |
| H1c | none | as H1, at H2's chosen C |
| H2 | none | group-balanced refit on T (equal total weight per kind, 14 kinds), C by grouped CV |
| H3 | border, half A | H1 refit on erased T |
| H3c | border, half B (ceiling) | H1 refit on erased T |
| H4 | storage, half A | H1 refit on erased T |
| N00-N19 | 20 random directions | H1 refit on erased T (null) |
| H1d | none | logistic refit on the development hosts of L, class-balanced, C = 1 |
| H1dc | none | as H1d, at H2d's chosen C |
| H2d | none | group-balanced refit on the development hosts of L (equal weight per L kind, 32 kinds), C by grouped CV |

- **Logistic fits.** sklearn 1.9.0 LogisticRegression, L2, lbfgs, max_iter 5000. T is used with repeats removed.
- **Development hosts of L** (lead's answer 1; binding for the splice rows): 100 hosts, 3,200 rows (32 kinds × 100:
  ladder R0 at three strengths, R2w, R3, R3m, R2w4, R4 at the native and resized strengths, and the splice kinds S0,
  S3, S4 with their _bg/_face variants and the R2w/R2w4/R4 blends). All splice reads are on the 191 test hosts of L
  only. The test and development hosts are disjoint (asserted).
- **C choice (H2, H2d).** C from {0.01, 0.1, 1, 10} by 5-fold GroupKFold on hosts, group-balanced weights, maximising
  worst-group accuracy at decision 0. Ties: the smaller C. T's worst-group accuracy is printed for every C. If it is
  ≥ 0.98 for every C on ≥ 4 seeds, the training-list splice row reads "not testable on in-sample features".
- **Erasers (rank 1, mean-difference projection; x → x − (x·d̂) d̂).**
  - Border (H3, H0e): d = mean(half-A bordered copies) − mean(half-A R_cam photos).
  - Ceiling (H3c, H0ec): the same on half B, i.e. on the rows the border is read on. It shows the most a rank-1
    mean-difference eraser can remove.
  - Storage (H4, H0e4): d = mean(half-A fm61 and amsl112 photo copies) − mean(half-A native photos) in S.
  - Morph check (H0em): d = mean(T morphs) − mean(T genuine).
  - Null (N00-N19): 20 directions drawn from N(0, Cov(T features)), `default_rng(20261129)`, one stream across
    networks in seed order.

## 6. Reads per network and head

**Reference pool and units (F1; lead's answer 2).** P = R_cam (417) ∪ L ladder R0 at all three strengths (873):
1,290 camera photos, 406 hosts. A score is converted to a mid percentile rank in the head's own scores on P.

1. **Border shift (primary, threshold-free).** For each half-B bordered copy: rank(copy) − rank(the same unbordered
   photo). Averaged within each host, then over half-B hosts. Removal(Hk vs ref) = 1 − shift(Hk) / shift(ref). The
   reported removals are H3 vs H1, H0e vs H0, H3c vs H1, H0ec vs H0, H1 vs H0, and each null N vs H1. A seed is "floor"
   if shift(H0) or shift(H1) ≤ 0.01.
2. **Border flags (secondary).** Every head, H0 included, is cut at the 99th and the 95th percentile of its own scores
   on P. Printed at each cut: flag share on the half-B bordered copies (pooled and per mask), flag share on their
   unbordered photos, and landmark_combined recall. The old rule (H0 at logit 0, other heads at the (k+1)-th largest
   R_cam score) is printed only.
3. **Same-person splices (test hosts of L only).** S3 flag share at the cut where each head's S4 recall equals H0's
   own-rule (logit 0) S4 recall on the same hosts. The S4-vs-S3 AUC is printed. For heads with an eraser (H0e*, H3,
   H3c, H4, nulls), the splice reads use half-B test hosts only (F7), with H0's matched recall recomputed on those hosts.
4. **Detection.** AUC of landmark_combined orig morphs against resmatch genuine (set C). C and S are FFHQ, and T has
   no FFHQ, so for every refitted head these reads are cross-domain.
5. **Storage shift (threshold-free).** On half-B S persons: rank(copy) − rank(the same person's native photo) in P
   units, at fm61 and at amsl112, averaged within each host and then over hosts. Δf at the 99th and 95th percentile
   cuts is printed. A seed is storage "floor" if H0's amsl112 shift ≤ 0.02.
6. **Erasure-works check (F3).** AUC(H0) − AUC(H0em) must be ≥ 0.05. Where it is not, the AUC guards on that seed are
   labelled "AUC guard insensitive".
7. **Probes (printed).** Logistic probe AUC (5-fold, grouped by host) for border presence (half-B bordered copies
   against half-B R_cam photos) before and after the H3 eraser, and for stored against native (half-B S photos) before
   and after the H4 eraser.

## 7. Outcome table (fixed before reading; a row holds on ≥ 4 seeds)

| Result (per seed; counted over available, non-floor seeds) | Reading | Next |
|---|---|---|
| H3 removes ≥ 70% of H1's border shift AND H0e removes ≥ 50% of H0's AND AUC(H3) ≥ AUC(H1) − 0.01 AND H3's removal exceeds the largest of the 20 null removals | the border shift is a separable rank-1 direction, beyond refitting and the random-direction null | the lead may register a border nuisance head or erasure layer, read beside the border-crossed data arm (Sbx) |
| else: the ceiling eraser H3c removes < 70% of H1's shift | rank-1 erasure cannot test this | a richer eraser (LEACE, rank-k) on the saved features; no GPU needed |
| else: H3 removes < 50% of H1's shift, OR AUC(H3) < AUC(H1) − 0.02 | the border shift is not removable by a rank-1 linear eraser; gradient-reversal arms get no support from NE1 | data or input-treatment arms only, as far as NE1 informs |
| Otherwise | "inconclusive (border)" | — |
| H2d's S3 share at matched S4 recall ≥ 0.05 below H0's (binding: fitted on development hosts, read on test hosts) | reweighting can move the trade-off | the lead may register a group-DRO arm with strong L2; if H1dc also moves ≥ 0.05, attributed to refitting |
| H2d within 0.03 of H0 AND of H1dc | reweighting the last layer on held-out development features does not move the trade-off | the group DRO / JTT route gets no support from NE1 on this backbone |
| Otherwise | "inconclusive (splices)" | — |
| The same two rows with H2 and H1c (fitted on T) | printed only; "not testable on in-sample features" if T's worst-group accuracy is ≥ 0.98 for every C | — |
| H4's amsl112 storage shift ≥ 0.02 below H1's AND H0e4's ≥ 0.02 below H0's AND AUC(H4) ≥ AUC(H1) − 0.01 | residual storage reaction is a separable direction | a note for the next version; no claim about the frozen network |
| Otherwise | "no separable storage direction shown" | — |

Counting. The border rows are checked in the order listed: the first that holds on ≥ 4 non-floor seeds is the
reading. With fewer than 4 non-floor seeds the border reads "floor (not testable)", and the same applies to storage.
Comparisons use point values. The bootstrap intervals of section 9 are printed, not used.

**Kill condition.** A network whose extraction fails (no feature file) is "not available". With fewer than 4 available
networks, NE1 reads "not available" for every row. A gate failure (section 8) does not remove a network; it labels it.

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

`src/NE1/ne1_heads.py`, run once. Bootstrap intervals (2,000 draws, `default_rng(20261128)`, hosts) are printed for:
- the border shift of H0, H0e, H1, H3 and H3c, and the differences H3 − H1 and H0e − H0. Hosts of P are redrawn, and
  the reference ranks are recomputed in every draw.
- the S3 share at matched recall for H0, H1d, H1dc, H2d, H1, H1c and H2, and each minus H0. Test hosts are redrawn, and
  the matched cut is recomputed in every draw.
- the landmark_combined AUC of H0, H1, H3, H4 and H0em, and the differences H3 − H1 and H4 − H1.

The table rows use point values on ≥ 4 of 5 seeds. All features stay saved, so later erasers (LEACE, rank-k) need no
new GPU slot.

## 10. Code, inputs and job (pins at registration)

| File | sha256 |
|---|---|
| `src/NE1/build_ne1_pack.py` | `20b1a0088ca96267…` |
| `src/NE1/ne1_extract.py` | `5082d0e37f947ded…` |
| `src/NE1/ne1_gate.py` | `79f45a880f8f9602…` |
| `src/NE1/athena_ne1.sbatch` | `bdfd96ef10ed1ee9…` |
| `src/NE1/ne1_heads.py` | `5c6fdcd2173d7fb9…` |
| `ne1_pack.tar` (code, base weights, images, manifests; 8.9 GB) | `6456f550bb6d8f58…` |
| `ne1_nets.tar` (five Sb meta.json + last_trainable.pt, TT1-FS gate refs) | `010337f9482ad442…` |
| `ne1_train.csv` (5,535 rows) | `39125d0ff1141101…` |
| `ne1_gate.csv` (3,417 rows) | `98c4d808ebf86728…` |
| `ne1_read.csv` (17,857 rows: L 10,458, C 3,000, B 2,919, S 1,480; L rows carry role dev/test) | `ea1a5ca8b59ddfe6…` |

Full values: `/mnt/t7/smad_next/NE1/*.sha256` and `git show` of this commit.

- **Tests before the job.** ne1_extract.py on 8 rows of each manifest, one network, on the DGX: features of norm 1,
  logit = feature · w + b within 5e-7 (no score printed or read). ne1_heads.py in `--mock` mode (random unit features
  with the real manifests and H0 weights) on all five networks after the F1-F8 fixes: every read and interval computed,
  1 min 42 s in all. Every branch of the outcome table was exercised with synthetic values (separable, ceiling-fail,
  not removable, null beats H3, splice moves / no change, storage). The pack was rebuilt after F6 (role column, host
  assert); the extraction code and job script are unchanged since 2a31a56.
- **Job.** `sbatch -p plgrid-now -A plgmultivision-gpu-a100 -t 01:00:00 athena_ne1.sbatch` from the Athena task folder
  `tasks/NE1` (scripts + SHA256SUMS); inputs in `packs/NE1`; output `results/NE1/NE1_feats.tar` + `.sha256`. Expected run
  time: about 5-10 min to copy and unpack 8.9 GB into memfs, about 70-90 s of extraction per network (TT1-FS: about 80 s
  per network for 30,994 rows on an A100 PCIe), about 20 min in all; limit 1 h. Submitted by the dispatcher.
- **Analysis.** `ne1_heads.py` on the DGX CPU (thread caps 2, nice 10), sklearn 1.9.0, numpy from the analysis venv
  (`mambamorph-code/.venv-spark`), run once after the result tar is verified in two places.
