# DRAFT: Multi-source training set (MS1), part 2: the training comparison

DRAFT for independent pre-run review. Nothing in this file governs anything until it is copied into `prereg.md` part 2
at a commit that comes before the first fit is submitted. No fit and no score of SbM3 or of the WCSS Sb fits exists.
No TT1 pool has been scored by any network at the time of writing (TT1 has extracted and aligned its pools only,
commit 3912ae4).

## 1. Arms, seeds, platform

- **Sb**: the PN1 spliced recipe, manifest train_Sb (sha256 `2cf3fda3…`, byte-equal to FS1's), FRGC + colorFERET.
- **SbM3**: the same recipe on three sources, manifest train_SbM3 (`885dff9d…`, 13,414 rows): train_Sb's rows unchanged
  (asserted) plus 3,263 FFHQ images (prereg part 1; the FFHQ strata balanced by the amendment-4 rule).
- Seeds 403, 404, 405, 406, 407 for both arms: ten fits.
- Training and scoring commands unchanged: `train.py` of the AD4 pack (`cbb2cbd1…`) with the PN1 flags (6,250 steps,
  batch 256, LoRA r 2 on q/v, last checkpoint), `pn1_score.py` (`737d6e35…`), both from the FS1 tree. Driver
  `src/MS1/run.sh` (`fcc9a646…`) = `src/PN1/run.sh` (`6a23a7a4…`) with three changes only: arm list `Sb|SbM3`, results folder `results/MS1`,
  default pack name (diff in the README).
- **Platform: both arms on WCSS H100 (partition lem-gpu-short, `gpu:hopper:1`), Python `~/dmenv` (torch 2.11), one
  job per fit (array of ten, `src/MS1/wcss/ms1_fit.sbatch`).** Chosen over "SbM3 on a rented A100 PCIe against FS1's Sb"
  because (i) both arms then share GPU type, software and pack, so the comparison is self-contained; (ii) five seeds per
  arm allow a 5-against-5 exact test (smallest one-sided p 1/252) instead of 3 against 5 (1/56); (iii) WCSS is free and
  has idle H100 nodes (lead, 12 Nov). GPU name and UUID are recorded per fit (`gpu.txt`). FS1's A100 Sb fits at the same
  seeds are printed beside the WCSS Sb fits as a platform reference only; they count for nothing.
- Fallback (decided by the lead, not by results): if the ten WCSS fits have not started by 13 Nov 2026 12:00 CET, SbM3
  seeds 403-405 run on one rented A100 PCIe 40 GB and are compared with FS1's Sb seeds 403-407 by the same rules
  (Mann-Whitney 3 against 5); disclosed as a mixed design if it happens.

## 2. Evaluation manifest (development data only)

`pn1_eval.csv` inside the pack = FS1's 19,797 development rows (`f0f29f22…`) + MS1 FFHQ hold-out rows (fam `ms1ffhq`,
about 1,480) + TT1 aligned genuine photos (fam `tt1`, cell = TT1 family; 21,089: replay_attack 200, msu_mfsd 65,
oulu_npu 989, casia_fasd 150, lfw_calfw 11,022, cfp_ff 4,726, agedb_30 3,937; TT1 aligned manifest `8b3c6fa9…`).
No FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace or sealed row or image (asserted by `build_pack.py`).

Labels of the FFHQ reads change with this experiment: for SbM3, FFHQ is a TRAINED source. ffhqm reads (HN2 genuine,
landmark_complete, landmark_combined) are labelled "trained source (FFHQ), development persons excluded by key, file
and identity, other alignment pipeline"; MS1 hold-out reads are labelled "trained source (FFHQ), new persons, same
pipeline". For Sb, FFHQ remains an untrained source. No sentence may call FFHQ "unseen" for SbM3. Unseen sources for
both arms: the seven TT1 families only.

## 3. Thresholds

- Own rule τ_0.5: logit > 0. Decides every primary read.
- τ_cam (printed only): FS1's rule (`fs_read.py`): the larger of the two 5%-false-alarm thresholds of development camera
  photos (development-ladder R0, 100; AF0 validation photos, 126), native only.

## 4. Reads, predictions, falsifiers (per network; then across seeds)

Per network, genuine flag share f_k = share of family k's aligned genuine photos with logit > 0.

**P1 (primary): own-rule genuine flags on unseen sources.** Statistic F = unweighted mean of f_k over the seven TT1
families.
- Supported if median(F, SbM3) ≤ 0.5 × median(F, Sb) AND the exact one-sided Mann-Whitney test (SbM3 lower) over the
  read seeds gives p ≤ 0.05 (5 against 5: U ≤ 4 of 25).
- Falsified if median(F, SbM3) ≥ 0.8 × median(F, Sb) OR p > 0.5.
- Otherwise "inconclusive, no claim".
- Floor: if median(F, Sb) < 0.03, P1 is "untestable at the own rule (floor)" and only P2 is read.
- Printed: f_k per family per network with Clopper-Pearson 95% intervals and a person-cluster bootstrap (2,000 draws,
  `default_rng(20261125)`); the number of families in which SbM3's median f_k is below Sb's.

**P2 (secondary): scale-free source offset.** Per family k, AUC_k = AUC(TT1 family k genuine against development camera
photos: development-ladder R0 100 + AF0 validation photos 126, native), TT1 positive; 0.5 = the network scores the
unseen source like the training sources' camera photos. Statistic O = mean over families of AUC_k.
- Supported if median(O, Sb) − median(O, SbM3) ≥ 0.05 AND Mann-Whitney p ≤ 0.05 (SbM3 lower).
- Falsified if median(O, SbM3) ≥ median(O, Sb).
- Otherwise "inconclusive, no claim".

**P3 (secondary): same source, new persons.** Own-rule flag share on the 300 MS1 FFHQ hold-out photos (native).
Predicted: median over SbM3 seeds ≤ 0.05; Sb printed beside it (an untrained source for Sb). Falsified for SbM3 if its
median > 0.10. Also printed: ffhqm HN2 genuine own-rule flags (2,000), and AUC of hold-out u50 against hold-out photos.

**Guards (must not get worse; each read on medians across read seeds, Mann-Whitney p printed, no claim of
improvement).**
- G1 FFHQ landmark_combined AUC (1,000 orig morphs against 2,000 resmatch genuine; FS1 contrast 1's read):
  median(SbM3) ≥ median(Sb) − 0.03.
- G2 development attack detection, FRGC / colorFERET: development-ladder R4 against R2w AUC and AF0 validation u50
  against AF0 validation photos AUC: each median(SbM3) ≥ median(Sb) − 0.02; own-rule miss on development R4 + AF0
  validation u50: median(SbM3) ≤ median(Sb) + 0.05.
- G3 storage, untrained size (two-sided, PRERUN remedies F2/F7): standardised median paired shift
  (112.7 px copy − native) / SD(native genuine logits) on development camera photos (ladder R0 and AF0 validation
  photos, pairs by id): |shift(SbM3)| ≤ |shift(Sb)| + 0.10. Printed: the same on MS1 FFHQ hold-out photos (amsl112),
  the 61.2 px reads (trained size), and FS1 contrast 2's paired storage share on ffhqm (labelled trained source for
  SbM3).
- A guard that fails is reported with the P1 sentence ("…, at a cost in …").

**Printed only:** τ_cam flag shares on every TT1 family; the FS1 A100 Sb values at seeds 403-407 beside the WCSS Sb
values (platform reference: own-rule TT1 F and landmark_combined AUC); mean training-row logit minus mean held-out logit
per kind (PN1 amendment 4 item 3); FS1 R1-R6 on landmark_combined for both arms.

## 5. Seed rules

- A seed is read only if both arms finished with finite loss and a verified result tar. A seed with a lost or
  non-finite arm is dropped from every read and not replaced. A non-finite run is never rerun; an infrastructure
  failure is rerun once, unchanged, on the same partition.
- n read seeds: 5 or 4 -> the tests above (4 against 4: smallest p 1/70); 3 or fewer -> "not read (too few seeds)".
- Ties: margins inclusive at full float precision; Mann-Whitney with ties counted half (exact distribution by
  enumeration).
- No seed may be dropped or chosen on any score.
- Deadline: fits finished and fetched by 14 Nov 2026 12:00 CET are read; later fits are not read.

## 6. Outcome sentences (development data; never a benchmark claim)

| Outcome | Sentence |
|---|---|
| P1 supported, guards hold | "Adding a third capture source, with its own morphs and matched controls, lowers genuine flag rates at the network's own rule on seven unseen development sources (5 seeds)." |
| P1 supported, a guard fails | the same, "… at a cost in <guard>" |
| P1 falsified | "One added capture source does not make the own-rule threshold transfer to unseen sources." |
| P1 untestable (floor), P2 supported | "The added source moves unseen-source genuine scores toward the training sources' camera photos (scale-free), no own-rule effect measurable." |
| anything else | "inconclusive, no claim" |

Must not claim: benchmark performance; a fixed-threshold or calibration claim on benchmarks; "source-invariant"; that
FFHQ is unseen for SbM3; any effect of splices (FFHQ adds none).

## 7. Disclosures and confounds

- Known before writing: Sb seeds 401/402 own-rule FFHQ genuine flags 5.9 / 7.0% (B 17.8 / 6.4%); FFHQ genuine
  flagged 3.5-22.5% at the own rule and 95-98% at τ_cam across PN1 networks (lead's task text). The 0.5 ratio was set
  knowing these. No TT1 score of any network is known; no FS1 fresh-seed tar has been opened by the MS1 owner.
- Data volume: SbM3 has 13,414 rows against 8,386 at the same 6,250 steps; each FRGC / colorFERET row is seen about
  0.63 times as often. A data-volume control (Sb rows repeated to 13,414) is not run; the effect, if any, is "third
  source plus more rows".
- FFHQ content: in-the-wild photos (expressions, sunglasses, occlusions) and black frame borders, in both classes;
  FFHQ frames are shrunk into the frame (native eye distance about 260 px) while TT1 frames are enlarged 1.7-3.5x;
  the fm61 stored copies are the only enlarged FFHQ training images.
- FFHQ adds no spliced images (prereg part 1, 3.3).
- Platform: WCSS dmenv (torch 2.11) differs from the Athena container and the rented hosts (torch 2.2.1); WCSS Sb is a
  new set of fits, not FS1's.

## 8. Pack, pins, cost, wall time

- Pack `/mnt/t7/smad_next/MS1/pn1_pack_ms1.tar`, sha256 `dac228f53ccb6771eb6d1f3c783b32f41a9e33fd6711d97a18108123ba8c60c2`
  (14,508,625,920 bytes, 51,272 files); evaluation manifest `d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5`
  (42,366 rows: FS1 19,797, MS1 FFHQ hold-out 1,480 (1,031 label 0, 449 label 1), TT1 21,089); built by
  `src/MS1/build_pack.py` from the FS1 tree (code, weights, train_Sb images, FS1 eval rows, each checked against FS1's
  SHA256SUMS) plus the FFHQ training images (sha256 in `SbM3_files.csv`), the MS1 hold-out rows and the TT1 frames
  (sha256 from TT1's manifest).
- Pins at the registration commit: run.sh (MS1), ms1_fit.sbatch, ms1_smoke.sbatch, the reader `src/MS1/ms1_read.py`
  (committed before any tar is pulled, tested on mock scores).
- Cost: WCSS, free. About 0.8 H100-hours per fit (training, judged from FS1's 1.2 A100-hours) plus about 10 minutes of
  scoring for the 42,000 evaluation rows: about 10 H100-hours in all. Wall time about 1.5 hours once the ten jobs
  run in parallel; queue wait unknown.
- Reader `src/MS1/ms1_read.py` sha256 `64f018b589e234328c4d9a7c39895962c6254026a41b0f29fad9b93891d75e03` (tested on random mock scores only: `ms1_read_mock.json`); ms1_fit.sbatch `be1e79b04b1403c58c54b4548f790bc5fe9884ee92e780cd07fc41484105344c`; ms1_smoke.sbatch `b82990e258d112aee2f8534c438f2212e9d2daac22c90571bc32a1c91ae412c7` (local storage 80 GB: pack 14.5 GB copied and extracted).
- DGX smoke passed (`date`: result tar written Thu Nov 12 11:19:57 PM CET 2026): run.sh (MS1) with 20 steps and 64 scoring rows on arm SbM3 seed 403 from the pinned pack: train.py read 13,414 rows, result tar complete (scores, last_trainable.pt, gpu.txt); log `/mnt/t7/smad_next/MS1/smoke/smoke_dgx.log`.
- Smoke first (`ms1_smoke.sbatch`: 20 steps, 64 scoring rows, both arms); the array is submitted only after the smoke
  passes.

## 9. Commands for the lead (one connection each, under the WCSS lock; nothing is run by the owner)

```
# 1 upload (resumable)
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a --partial -e "ssh -o BatchMode=yes" \
  /mnt/t7/smad_next/MS1/pn1_pack_ms1.tar /mnt/t7/smad_next/MS1/pn1_pack_ms1.tar.sha256 \
  /mnt/t7/smad_next/MS1/wcss_stage/run.sh /mnt/t7/smad_next/MS1/wcss_stage/run.sh.sha256 \
  /home/narolski/smad-next/src/MS1/wcss/ms1_smoke.sbatch /home/narolski/smad-next/src/MS1/wcss/ms1_fit.sbatch \
  narolski@ui.wcss.pl:/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/MS1/
# 2 smoke
flock -w 600 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl \
  'cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/MS1 && /opt/slurm/current/bin/sbatch ms1_smoke.sbatch'
# 3 after "MS1_SMOKE_DONE" in logs/ms1-smoke-<job>.out: the ten fits
flock -w 600 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl \
  'cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/MS1 && /opt/slurm/current/bin/sbatch ms1_fit.sbatch'
# 4 fetch (after the jobs end)
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a -e "ssh -o BatchMode=yes" \
  narolski@ui.wcss.pl:/lustre/pd03/hpc-narolski-1790461090/smad-next/results/MS1/ /mnt/t7/smad_next/MS1/results/
```
Result tars hold the trained weights (`last_trainable.pt`); all ten are kept on `/mnt/t7` and on WCSS PD.
