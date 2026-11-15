# Registration TT1-M: NIST SD32 MEDS as a further unseen genuine source for the fresh-seed networks

Registered at the git commit that adds this text, before any MEDS row is scored on the scoring platform. The lead
requested it on 13 Nov at 13:40.

The only MEDS network output so far is a DGX mechanics test of the job on one network (A_s403). It ran on a platform
that fails the gate, its output was deleted unread, and it is not a TT1 score.

**Data rules (NIST terms and the author's ruling):** no MEDS image in any figure, repository or artifact. Images stay
on /mnt/t7 and inside scoring packs only. The repository holds counts, manifests of ids and hashes, and scores.

## 0. Scope and limits

- **False alarms only.** These are genuine operational mugshots; no morphs are built from MEDS now (the same-person
  cross-encounter pairs are noted for a later experiment). No miss, detection or benchmark claim.
- **MEDS is read as its own family.** It is not pooled into the seven-family mean of TT1. It resembles the sharp
  full-frame FFHQ photos, not the bordered low-resolution TT1 frames:
  - median native eye distance 104.8 px (10th-90th percentile 54.7-160.6), so enlargement to 132 px is about 1.26;
  - median black-border share 0.0001;
  - the TT1 border and crop-geometry references do not apply.
- **Not shown by any reading here:** the cause of any source effect (MEDS differs from the training sources in
  camera, compression, era and population); that one arm is better overall. No arm, seed or threshold is chosen.

## 1. Pool (built before this registration; no score)

`src/TT1/meds_build.py` (sha256 `63be4997…`).

**Selection:**
- MEDS-II images labelled "Frontal" in image_pose.csv.
- MEDS-I images whose file content (sha256) is not in MEDS-II and whose POS is "F". A blank POS means unknown pose and
  is excluded.
- Counts: 500 of 712 MEDS-I files are byte-identical to MEDS-II files; 49 MEDS-I files are excluded for POS.
- Result: 1,018 images of 446 persons (MEDS-II 855, MEDS-I 163). Person = subject id; encounter kept.

**Alignment:** `prep_eval.align` unchanged (`374408ab…`).
- **Primary pool:** prep_eval's aligned frames, 865 images of 400 persons; 157 persons have two or more encounters.
- **Secondary pool (printed):** the 153 frames that failed the frontal filter.

No enlargement band is used, because MEDS is not a crop at one fixed size. Native sizes are recorded; 156 images are
240x240.

**Files:**
- Manifest `/mnt/t7/smad_next/TT1/meds/meds_manifest.csv` (`3698bcb4…`).
- Counts: `meds_counts.json`.
- Scoring list `meds_score.csv` (`9093d5d5…`; ids, person, encounter, part; no images).

## 2. Networks and per-network gate (TT1-D3 rule, unchanged)

**Networks** (from verified local tars):
- 15 deciding networks: FS1 A, B, Sb at seeds 403-407.
- Printed only: Sp at seeds 403-405.

**Rule, verbatim:** "a deciding network that fails the gate makes the decision 'not available'; never read on one
seed." A network that fails is not scored on MEDS rows. An arm statement needs at least 4 of 5 passing seeds that
agree.

**Gate rows:**
- The 3,417 TT1 fam-gate rows (R_cam 417, R_ffhq 2,000, M_ffhq 1,000) of `tt1_score.csv` (`c0055b51…`).
- Scored on the new host by `src/PN1/rescore.py` unchanged (`6f6eede7…`; PyTorch defaults; batch 64; list order).
- These are exactly the conditions under which the same rows were scored on pn1fs in TT1-FS and TT1-X
  (`__gate.npz`, in the network tar as `gate_ref`).
- The rows span floor rows (R_cam) and mid-range and upper rows (FFHQ genuine and morphs).

**Criterion:** byte identity (float32) per network, `src/TT1/meds/gate_check_m.py`.

**Platform:**
- se1d, an A100 PCIe 40 GB (a different host from pn1fs), after the SE1 owner's seed 411 is fetched: the driver starts
  only once `SE1_DONE_411` exists.
- Image torch 2.2.1. The PN1 pip pins are installed into a separate venv in /workspace/tt1m (system site packages,
  torch held), so the SE1 environment is untouched.
- Versions are asserted and the cuDNN and TF32 flags recorded. The job checks for an A100-PCIE GPU.
- If the gate fails for a network on this host, that network is "not available". No fallback, no forcing.

**MEDS rows:** fam meds of `meds_score.csv` (1,018 rows), rescore.py unchanged, for passing networks.

**Packs:**
- `tt1_pack.tar` (`2109f742…`, code, base weights, gate images).
- `tt1m_meds.tar` (`3fb917b2…`, 1,018 aligned MEDS PNGs and the list).
- `tt1m_nets.tar` (`b5c4dd6e…`, 18 networks + gate_ref).

**Scripts:** `src/TT1/meds/remote_tt1_m.sh` (`83a47fd8…`), `drive_tt1_m.sh` (`871c0aa8…`), `build_meds_pack.py`
(`9d487eb7…`). The driver never writes RELEASE; it writes `/mnt/t7/smad_next/vast/se1d/tt1m/TT1M_DONE` after two
verified copies. Mechanics tested on the DGX with one network (test mode).

## 3. Reads (`src/TT1/meds/tt1_read_meds.py` `de62a0a6…`, mock-tested; run once)

Per network:
- MEDS own-rule flag share (primary pool) with a person bootstrap (2,000 draws, `default_rng(20261125)`, lower bound
  clipped at 0) and Clopper-Pearson.
- AUC of MEDS against R_cam and against R_ffhq (references from the same job; R_cam by host, R_ffhq by image, MEDS by
  person).
- Median logit, shift from R_cam in logits and in u.
- Spearman of logit with log Laplacian variance and with log enlargement inside MEDS.
- Printed: flag shares by part (MEDS-I / MEDS-II), for the 240x240 images, and on the secondary pool.

## 4. Hypotheses (4 of 5 seeds; deciding arms A, B, Sb; Sp printed only)

- **TT-M1, own rule on MEDS (same bar as TT1 TT-H1).** Per network: "fails" if the person-bootstrap lower bound is above
  5%; "transfers" if the upper bound is ≤ 10%; otherwise "neither".
  - Prediction (from the FFHQ genuine flags of the same networks: Sb 2.4-5.1%, B 2.5-10.8%, A 6.5-10.8%): Sb
    "transfers" on at least 4 of 5 seeds; B "transfers" on at least 4 of 5; no prediction for A.
  - Falsified for an arm if it "fails" on at least 4 of 5 seeds.
- **TT-M2, displacement.** Per network: "displaced" if AUC(MEDS vs R_cam) ≥ 0.90; "not displaced" if ≤ 0.75.
  - Prediction: "displaced" for every arm on at least 4 of 5 seeds (as for every TT1 source).
- **TT-M3, arms (descriptive; pairs B − A, Sb − A, Sb − B, B − Sb).** Per seed, the difference of MEDS flag shares with
  a paired bootstrap. The sentence "X has lower MEDS flag rates than Y on seeds 403-407" only if the difference is ≤
  −0.03 with an interval excluding 0 on at least 4 of 5 seeds. Mean ± SD and sign counts are printed. The intervals
  capture image sampling only.
- **TT-M4 (descriptive):** Spearman of logit with log sharpness and with log enlargement inside MEDS, per network.
  No rule.

## 5. Order and stop rule

Upload (no GPU) now → after `SE1_DONE_411`: start → pull loop → read once → results-reviewer (opus) → report.

No re-run after scores are seen, except one unchanged re-run after an infrastructure failure. Cost is about 0.3
A100-hours inside the lead's se1d lease.

## 6. Amendment after the pre-run check (`date`: Fri Nov 13 01:53:56 PM CET 2026; registered at the git commit that adds this section, before start and before any score)

Pre-run check (experiment-reviewer, opus): GO WITH FIXES (F1, F2 majors; F3-F7 minors). Applied:
- F1: the remote job aborts if any compute process is on the GPU (another owner), and the driver refuses to start if
  the GPU is busy or a TT1-M job is already running on the host (`start` only after SE1_DONE_411, as before).
- F2: `src/TT1/meds/gate_check_m.py` sha256 `1a62c58bbf834d73de1e71b1ff61c4480c762afd88e40e8a8ef0894b26778597`
  is part of the registration. The gate certifies the platform on batch 64 (53 full batches and a last batch of 25);
  the final MEDS batch (58 rows) has no cross-host reference, and MEDS scores have no pn1fs counterpart. Deviation
  disclosed: the DGX mechanics-test output for A_s403 (my own test files) was deleted unread, so that no non-gated MEDS
  score exists on disk.
- F3 (checked on hashes and filenames only): MEDS-I has 712 files, 710 distinct contents (2 internal duplicates); 500
  MEDS-I files have content equal to a MEDS-II file, all 500 with the same subject id (498 with the same filename), so the
  subject numbering is shared and persons are merged correctly as meds:S<id>. The 163 added MEDS-I images are MEDS-I-only
  contents with POS F.
- F4: the venv asserts torch 2.2.1, CUDA 12.1 and cuDNN 8902 (pn1fs values) besides timm, numpy and Pillow.
- F5: the reader asserts the manifest (`3698bcb4…`) and `tt1_score.csv` (`c0055b51…`) pins, the MEDS id order
  (1,018) in every MEDS score file and 3,417 rows in every gate file.
- F6: TT-M1 'neither' or 'mixed' = prediction not confirmed and not falsified.
- F7 (question to the lead): MEDS packs and aligned frames remain on se1d under /workspace/tt1m after the run; whether to
  remove them before the instance is released (NIST terms against the never-delete rule) is the lead's or author's call.
- Re-pinned: remote_tt1_m.sh `70028d9b9deccb296daf801482df40de5e2dce2a89067af4a811733a0d6ae690`; drive_tt1_m.sh
  `8b1b544e999507f718c18a6bc423b4bc01af0e78d395c64eef09fb3fb05f9b9c`; tt1_read_meds.py
  `0b5d86b154c2455f3279ded63ee9a606196140fa65b707d6a173212d0cb84b11`. Packs staged and verified on se1d at 13:50:43.
- F7 answered by the lead: after TT1M_DONE (two verified copies of the result on the DGX), the owner removes the MEDS pack
  (/workspace/tt1m/packs/tt1m_meds.tar) and the extracted MEDS frames (/workspace/tt1m/work/tt1m) from se1d, confirms,
  and the lead releases the machine. Nothing else is removed there, and nothing on the DGX.
- Operational fix (`date`: Fri Nov 13 05:05:44 PM CET 2026; before start, nothing scored): the driver's single-job guard `pgrep -f remote_tt1_m.sh`
  matched its own ssh command line, so `start` refused at 17:03:12 ("already running"; nothing was running). The guard
  now uses `pgrep -f [r]emote_tt1_m.sh`. drive_tt1_m.sh re-pinned `9006cc99d47db85503b0232ed71813eb7d8e6f0f3c2c064612ffb87ac1ca3e96`.

## 7. Post hoc follow-ups S1, S2 (`date`: Fri Nov 13 05:21:04 PM CET 2026; registered at the git commit that adds this section, before computing; zero GPU; review of the MEDS reading)

Both are written after the MEDS scores and the review's split were seen; labelled post hoc. Code `src/TT1/meds/meds_strata.py`.
Scores: the gated MEDS scores (`TT1M_se1d.tar`, se1d) and the gated TT1 scores of the same networks (`TT1_A100_pn1fs_fs.tar`,
`TT1_pn1fs_sp.tar`, pn1fs); both gates byte-identical against the same reference rows, so the two platforms give the same
numbers for these networks.
- **S1, stratified print (all 18 networks).** Primary MEDS pool split by native size group (240x240 against other) and
  part (MEDS-I, MEDS-II): n, persons, own-rule flag share with a person bootstrap (2,000 draws, default_rng(20261126),
  lower bound clipped at 0) and Clopper-Pearson; Spearman of logit with log Laplacian variance and with log enlargement
  per stratum (printed when n ≥ 20). No rule.
- **S2, MEDS-240 against the TT1 low-resolution families at matched enlargement (15 deciding networks + Sp printed).**
  Enlargement bins (fixed now): [1.2, 1.6), [1.6, 2.0), [2.0, 2.5), [2.5, 3.0), [3.0, 3.5), [3.5, 4.0), [4.0, 6.0]. TT1 pool:
  U_p frames of the seven families pooled (enlargement in the TT1 bands). For each network: MEDS-240 flag share; TT1 flag
  share reweighted to the MEDS-240 enlargement-bin distribution (bins with no TT1 frame dropped from both, reported);
  difference MEDS-240 minus reweighted TT1 with a bootstrap (MEDS persons and TT1 persons resampled, 2,000 draws,
  default_rng(20261127)). Rule (descriptive): per network "consistent with enlargement" if |difference| ≤ 0.05; arm
  sentence when at least 4 of 5 seeds agree, else "mixed". Not causal: MEDS-240 and the TT1 families also differ in
  source, JPEG coding, crop and border (TT1 frames bordered, MEDS not).
