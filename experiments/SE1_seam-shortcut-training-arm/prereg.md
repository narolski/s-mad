# Same-person blends as negatives: a training arm against the blend-inside-the-face shortcut (SE1)

Registration, written 13 Nov 2026 by the SE1 owner (Claude agent for the lead); binding at the git commit that adds it (commit message contains "registered"). That commit comes before any SE1 fit result exists and before the 27-statistic baseline of section 7.5 has been computed. Development data only.

## 1. Question and hypothesis (plain words)

**What the arm we have now already uses as negatives.** The spliced protocol network arm (Sb; PN1 manifest `train_Sb.csv`, sha256 `2cf3fda3…`, 8,386 rows, 5,535 unique images) trains on:
- negatives: AF0 camera photos 518; their 61.2 px stored copies 254; AF0 warp-only images toward the two-person mean shape ("zero") 730; the two warped halves of every AF0 two-person morph 1,456; their stored copies 363; ladder camera photos (R0) 156; ladder warp-only images (R2w) 156; ladder morph halves 248; **seam-matched splices (S0) 156; same-person splices (S3: a same-person morph pasted inside the face hull of a warp-only image) 156**;
- attacks: AF0 two-person morphs (u50) 728 and their stored copies 366; ladder two-person morphs (R4) 124; two-person splices (S4) 124.

So Sb already has same-person splices as negatives. It has **no same-person full-frame blend of any kind**: no same-person morph (R3, the host's photo blended with the host's other photo), no mirror self-morph (R3m, the photo blended with its own lossless mirror), and nothing of that kind for the 518 AF0 training persons. Same-person splices are 156 of 5,535 unique images.

**What the fresh-seed networks do with same-person blends.** Own rule, logit > 0, 100 development hosts per cell, seeds 403–407, FS1 tars. These were read by the owner while drafting and are disclosed as known:

| Development cell | A (plain) | B (protocol) | Sb (spliced protocol) |
|---|---|---|---|
| S0 seam only, OpenCV-style | 0–1% | 0–2% | 0% |
| S3 same-person splice, OpenCV | 2–7% | 2–5% | 31–41% |
| R3 same-person morph, OpenCV | 98–100% | 89–99% | 83–91% |
| R3 same-person morph, FaceMorpher | 97–100% | 92–99% | 85–92% |
| R3m mirror self-morph, OpenCV | 97–99% | 91–98% | 93–96% |
| R4 two-person morph, either engine | 100% | 100% | 100% |
| S4 two-person splice, OpenCV | 1–5% | 1–3% | 71–85% |

Sb's AUCs: S3 against S0 0.863–0.927; S4 against S3 0.781–0.816. The median Sb logit is −1.4 to −3.1 on S3 and +3.1 to +3.3 on R3. On FFHQ landmark_combined morphs the median is +0.4 to +2.4 and the lower quartile −2.2 to −0.2.

**The problem, as the lead's strategist put it (STRATEGIST_IDLE_GPUS_20261113 §0) and as the numbers above confirm:**
- It is not the seam. Sb flags no seam-only image (S0).
- Sb reads a blend inside the face, and it cannot tell whether one person or two made that blend.
- The full same-person morph is flagged as a morph by every arm in 83–100% of cases.
- S3 flags and missed landmark morphs sit in the same score band.

**Hypothesis (H-SE, "identity against same-person blend").** Adding same-person full-frame blends as negatives, matched in engine and frame to the two-person attacks, makes the network depend on two-identity content. The added images are same-person morphs and mirror self-morphs of the ladder training hosts, plus mirror self-morphs of every AF0 training person, built with the same engine as the u50 attacks. The prediction is that, on persons never trained:
- same-person splices and same-person morphs are flagged at most 10% at the own rule;
- landmark-morph detection does not fall;
- the storage reaction stays reduced.

**Prediction stated against it (strategist, adopted).** The landmark_combined AUC guard may fail. No experiment in the record shows a second-identity reading above 0.60–0.75 (AR1, AS0, FZ2, PD1, SM1 A15–A22). If that guard fails while the target is met, the paper says: "the method detects blending inside the face, not a second identity; teaching it that same-person blends are genuine costs detection of landmark morphs". The SE numbers go beside that sentence. This is not a failure of the registration. It is one of its two informative outcomes.

## 2. Status of SE1 with respect to the freeze

SE1 is an **ablation row**. FINAL section 1 (amended 13 Nov, C2P) freezes only Sb, then B, then the MS1 version. SE1 can become a candidate only under a selection clause that the author registers in FINAL **before** any SE1 result tar is pulled (the lead is asking him). This file does not assume one. If a clause exists at the time of the read, it is applied as written there, and section 8 says what SE1 contributes to it. If none exists, nothing SE1 shows changes the frozen method.

## 3. Arms

All three arms are fitted in this experiment, on one platform, at the same seeds:
- **SE** (new): train_SE.csv = the unique rows of train_Sb.csv plus these negatives (label 0, storage history native):
  - `lad_R3`: same-person morph, OpenCV-style engine (`scripts/78_tool_morph.py`, sha256 `b8a389f1…`), the same 156 ladder training hosts as Sb's R0 rows. The images already exist (AR1).
  - `lad_R3m`: mirror self-morph, OpenCV-style engine, the same 156 hosts. The images already exist (AR1).
  - `af0_selfm`: mirror self-morph of each of Sb's 518 AF0 training photos. These are new and built by `src/SE1/build_selfm.py` from approved operations only:
    - a lossless `cv2.flip`, written as PNG and read back pixel-equal;
    - the .tem text mirrored with AR1's measured 106-point permutation;
    - the unchanged OpenCV-style engine. This is the engine and the 512 frame of the AF0 u50 attacks (AF0 verified u50 equal to the engine's command-line output).
    - Check: the same code path rebuilds AR1's R3m for 8 ladder hosts pixel for pixel (`/mnt/t7/smad_next/SE1/check_r3m.json`, 8 of 8 equal in mirror image, .tem text and R3m output).
    - Precedent: AR1's registered R3m rung (`experiments/AR1/prereg.md`, item 1 of 11 Nov about 15:00: "the unchanged tool on H and its lossless left-right mirror"). The flip moves pixels and does no resampling.

  Re-balanced by the unchanged amendment-4 rule (`mkmanifests.balanced_strata`, database × storage strata, seeded repetition of the smaller class). Result: 6,365 unique images (5,023 negatives, 1,342 attacks), 10,046 rows, sha256 `c4e5aa474c87399d5e80af8afec3737a33b54afc35ae721b11385a5f5814525b`.
  - Dilution, stated: the stored (61.2 px) share of training rows falls from 14.7% (Sb) to 12.3% (SE), and draws per row at 6,250 × 256 fall from 191 to 159. This could change the storage guard G2 by itself.
  - Cue introduced, stated: every new blended negative is native, while stored blended images remain attacks (af0_u5061). SE could learn "stored blend means attack". The target therefore also reads stored same-person morphs (section 7.1).
  - Composition, stated: 674 of the 830 new negatives are mirror-symmetric images (R3m, self-morphs). Only the 156 ladder R3 are non-mirror same-person morphs. A target miss may mean too small a dose of non-mirror same-person blends, not that identity cannot be read.
  - Not added, stated: stored copies of the new negatives. These would need the face-detector soften path, which is GPU-bound and was cut on the DGX. The stored strata are therefore those of Sb, unchanged. FaceMorpher images stay out of training (held-out engine). No new splice is built.
- **Sb**: train_Sb.csv, byte-equal to FS1. It is the comparator for every SE guard.
- **A**: train_A.csv, byte-equal to FS1. It is the positive control of the storage test (C2P rule).
- **B is not fitted.** No registered read uses it. A supplies the storage control and Sb the non-inferiority comparator.
- **Why refit and not reuse.** The FS1 networks were trained on A100 40 GB with torch 2.2.1. Scores depend on GPU model and torch build: C2P's gate measures exactly that, and FS1's Sb cannot be compared with an SE fitted on another platform. Every comparison here is within one seed on one platform. AB1 (fresh-seed replication) does not fit A or Sb at these seeds: it reads this experiment's A and Sb tars (dispatcher arrangement, 13 Nov), so there is exactly one A and one Sb network per seed 408–412 and nobody can choose between duplicates. Changing or cancelling an A or Sb task needs a message to AB1 and the dispatcher first.
- **Recipe, unchanged for all arms.** FS1 train.py and flags (CLIP ViT-B/16, LoRA r2 qv, the MADation recipe, bounded linear head, batch 256, 6,250 steps, last checkpoint; README of PN1 §4). Run through `src/SE1/run.sh`, which changes only the arm list, seeds, overlay and eval manifest. Scoring is the unchanged `pn1_score.py` (logit without flip).

## 4. Seeds and platform

- Seeds 408, 409, 410, 411, 412 for A, Sb and SE: 15 fits, one network per seed and arm, last checkpoint, no seed picking, no ensembles.
- Seeds: OWNER_BRIEF lists seeds 401–405. The lead's task message (13 Nov) asked for fresh seeds other than 401–407, and the dispatcher, for the lead, assigned 408–412, shared with AB1.
- Seeds 401–407 are not reused. 408–412 are fresh for every PN1-recipe network; the A and Sb fits here are also AB1's networks (section 3).
- Platform: ONE cluster for the smoke, all 15 fits and all scoring. The order is the author's ("if not WCSS, then Athena").
  - Twin jobs are queued on both clusters:
    - WCSS H100: lem-gpu-short, `~/dmenv` torch 2.11 / CUDA 12.8, `src/SE1/wcss/*.sbatch`;
    - Athena A100: plgrid-gpu-a100, project container `smad_torch221_cu121_v1.sif`, torch 2.2.1, `src/SE1/athena/*.sbatch`.
  - The dispatcher cancels the twin on the other cluster once one cluster has started the fit array. The cluster whose fit array starts first is the platform.
  - No fit result from the other cluster is read, ever. If both start, the second array is cancelled and any tar it wrote is kept unread and labelled.
- Rented fallback (lead, via the dispatcher, 13 Nov): if neither cluster runs the fits by 10:30, the lead may move all 15 fits to rented machines. Then every lease has the same GPU model, each seed runs whole on one lease, and nothing of SE1 runs on WCSS or Athena. Scripts: `src/SE1/rented/{drive_se1.sh, remote_se1.sh}`, adapted from MS1's drivers, with the same run.sh. The platform is then "rented <GPU model>, torch 2.2.1", recorded per tar.
- Blindness of later replications: this reader computes A's and Sb's storage (C2P) statistics at seeds 408–412. A confirmatory replication of C2P that uses these seeds (AB1) is blind only if its rules are committed before the first SE1 tar is pulled. The SE1 owner pulls no tar before AB1's registration commit exists, or before the lead states in writing that no confirmatory replication uses 408–412.
- GPU UUID and versions are recorded in each tar.
- If the chosen cluster cannot finish all 15 fits, no fit moves to the other one. The seed-counting rule of section 7 applies to whatever finished there.

## 5. Data (development only)

- Training: our own FRGC / colorFERET images only (AF0 and ladder training persons). No FFHQ, FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace or sealed image or row.
- Pack: the unchanged FS1 pack `pn1_pack_fs.tar` (`96c31ae2…`, on WCSS at `packs/BB2/`, sha256-checked by run.sh), plus the SE1 overlay `se1_overlay.tar` (sha256 `de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c`, 2,738 files, `SE1SUMS` inside). The overlay only adds files: `tar --skip-old-files`, and FS1's SHA256SUMS is re-checked after it.
- Evaluation manifest `se_eval.csv`, sha256 `6dcef964d8ca3024d353aaa1e568e42ba2f2454b1f1a36442311aa5f9b598f7c`, 21,703 rows:
  - FS1's 19,797 rows, byte-equal lines (no benchmark row; checked by its builder);
  - the MS1 FFHQ hold-out, 1,480 rows (the C2P images, copied byte-equal from the MS1 pack tree);
  - development FaceMorpher S0, S3 and S4, 300 rows (AR1 images, the same 100 development hosts as FS1's OpenCV splice rows);
  - mirror self-morphs of the 126 AF0 development photos, 126 rows (persons never trained).
- The 191-host test ladder rows are scored, as in FS1, but no read of this registration uses them.
- Builders: `src/SE1/build_selfm.py`, `src/SE1/mk_se.py` (asserts the FS1 and MS1 manifest hashes and a forbidden-path list).
- Persons: development hosts and AF0 development persons are disjoint from every training person (PN1 split). FFHQ is the designated development comparison set and is never reported as a benchmark.

## 6. Reads (all at the network's own rule, logit > 0, per seed; development rows only)

- Flag rates, with Clopper–Pearson 95% intervals:
  - camera pools: development ladder R0 (100), AF0 development photos (126), FFHQ `ffhq_bona_orig` (2,000), MS1 hold-out native photos (300);
  - same-person cells: S3 and R3 for both engines, R3m for both engines, AF0 development self-morphs, S0 for both engines, R2w, R2w4, zero.
- Misses: R4 and S4 for both engines, AF0 development u50, FFHQ landmark_combined morphs, FFHQ landmark_complete morphs.
- AUCs:
  - landmark_combined orig morphs against resmatch genuine;
  - R4 against R3, S4 against S3 and R4 against R3m (both engines);
  - S3 against S0.
- Storage: the C2P statistics on the MS1 hold-out at fm61 and amsl112 (Δf, Δm, person-bootstrap upper bound, morph shift Δm_att). These use `src/PN1/c2p_read.py`'s functions (holdout, net_stats), imported unchanged, with the same bootstrap seed 20261131.
- Reader: `src/SE1/se1_read.py` (sha256 at the registration commit), mock-tested only; run once.

## 7. Pass rules (fixed now; margins inclusive at full float precision)

**Read seed:** a seed is read only if A, Sb and SE all finished with finite losses, a verified tar, every evaluation row scored, and the full recipe (task_info.txt shows `steps 6250 limit 0`). A lost or non-finite fit is not replaced. An infrastructure failure is re-run once, unchanged, on WCSS H100. Seeds finished by **13 Nov 2026, 19:00 CET** are read; the lead may move this time only before any SE1 tar is pulled. A cluster outage may make the lead move it, which is allowed under the same condition.

**Counting a rule over read seeds:**
- 5 read seeds: met on ≥ 4, not met on ≤ 1, otherwise inconclusive;
- 4 read seeds: met on 4 of 4, not met on ≤ 1, otherwise inconclusive;
- 3 or fewer: "not read (too few seeds)".

**7.1 Target T (primary).** On a seed, all of: SE flags at most 10% of development S3 (OpenCV); at most 10% of development R3 (OpenCV); and at most 20% of each of the stored copies of development R3 at 61.2 px and 112.7 px (OpenCV, 100 each; they guard the stored-blend cue of section 3).
- Verdicts: "target met" if T is met; "reduced, not removed" if T is not met but, on the same count, SE's flagged counts on native S3 and R3 are at most half of Sb's (integer comparison 2·k_SE ≤ k_Sb); otherwise "not met" or "inconclusive, no claim".
- Printed: seed means of SE − Sb flags on S3 and R3, with a 95% bootstrap interval over the 100 hosts (the same 100 hosts are read on every seed, so the five seeds show stability, not five independent samples). Stored R4 misses at 61.2 and 112.7 px for SE and Sb.
- Printed with a fixed sentence: the held-out engine. FaceMorpher S3 and R3 both at most 20% (counted the same way) gives "transfers to the held-out engine".
- R3 is added to the lead's S3-only rule because it is the cleaner same-person blend. With S3 alone, a network could pass while still flagging most full same-person morphs.

**7.2 Guard G1, two-person detection must not fall (against Sb; decided on seed means).**
Same-seed SE and Sb are effectively independent networks, so per-seed differences carry about 0.04 AUC of seed noise (pre-run check, finding 2). Each leg is therefore decided on the mean over read seeds, with a 95% bootstrap interval (2,000 draws of images within class or of the 100 hosts, `default_rng(20261142)`, the same draws for every network). A leg is "met" if the point meets the bar, "not met" if the whole interval is on the wrong side, and "inconclusive" otherwise. The legs:
- mean(AUC_SE − AUC_Sb) on landmark_combined ≥ −0.02;
- mean(miss_SE − miss_Sb) at the own rule on landmark_combined morphs ≤ +0.05;
- mean SE miss on development R4, OpenCV ≤ 0.05; the same for FaceMorpher;
- mean(miss_SE − miss_Sb) on development S4 (OpenCV) ≤ +0.05.

G1 is "met" if every leg is met, "not met" if any leg is not met, and "inconclusive" otherwise. Requires at least 4 read seeds.

**7.3 Guard G2, storage reaction must stay reduced (C2P.3 rule, unchanged, with this experiment's refit A as control).**
- Control per seed and size: Δf(A) ≥ +0.05 and Δm(A) > 0.
- SE passes (s, z) if all hold: Δf(SE) ≤ Δf(A)/3, |Δm(SE)| ≤ Δm(A)/3, Δf(SE) ≤ +0.05, and the upper 95% bound of Δf(SE) ≤ +0.08.
- "Passes" needs the pass on the required count at both fm61 and amsl112. "Uninformative" if A's control is met on fewer than the required count at either size. "Fails" if SE passes on ≤ 1 seed at either size.
- H-new-1 (storage evasion, C2P.4 rule) must be "falsified" for SE: Δm_att(SE) ≥ −0.10 on the required count at both sizes.
- G2 holds only if both conditions hold.
- Sb is read by the same rule. Attribution: if G2 fails for SE while Sb passes the same rule, the failure is attributed to SE; if Sb fails as well, the reading is "fails for Sb as well: no attribution". "Uninformative" (A's control missed) is reported as such, never as a failure.

**7.4 Guard G3, camera-photo flags must not rise.**
- Absolute legs, per seed and counted: SE flags at most 5% of development R0 and at most 5% of AF0 development photos (Sb flags 0% of both at seeds 403–407).
- Relative legs, on seed means with the 7.2 bootstrap: mean(flag_SE − flag_Sb) ≤ +0.02 on FFHQ ffhq_bona_orig, and the same on the MS1 native photos. No absolute bar on these two: Sb itself flags 2.4–5.1% of FFHQ genuine photos.
- G3 is "met" if the absolute count is met and both relative legs are met, and "not met" if any is not met. If the absolute legs fail for Sb as well, the reading is "not met for Sb as well: no attribution".

**7.5 Hand-made statistic baseline (claim wording only).**
- The baseline: the 27 statistics of `cues27.py` with the amendment-15 model (StandardScaler and logistic regression, C = 1, balanced, no tuning).
  - Trained on the ladder training hosts with SE's ladder labels: attacks R4 and S4 (OpenCV); negatives R0, R2w, S0, S3, R3, R3m.
  - Read on the same development rows: R4 against R3 and S4 against S3 (both engines), and landmark_combined.
  - Code `src/SE1/baseline27_se1.py`. Its output is computed after the registration commit and committed before any tar is pulled.
- Rule: SE "reads the identity contrast beyond simple statistics" only if, on the required count, SE's AUC exceeds the baseline's by ≥ 0.05 on both R4 against R3 (OpenCV) and S4 against S3 (OpenCV).
- Otherwise every sentence about identity says "not separated from simple statistics".

## 8. What each outcome means

| Outcome | Sentence | Freeze |
|---|---|---|
| T met, G1 met, G2 holds, G3 met | "On development persons never trained, adding same-person blends as negatives lowers same-person splice and morph flags to ≤ 10% (stored same-person morphs ≤ 20%) while landmark-morph detection, the storage reduction and camera-photo flags hold (5 seeds)". Add "beyond simple statistics" only if 7.5 holds. | SE is eligible only if the author registered a selection clause before the read (which must also amend FINAL's "networks read" to seeds 408–412 on this platform). Otherwise it is an ablation row, and FINAL is unchanged. |
| T met, G1 not met (the predicted case) | "The method detects blending inside the face, not a second identity; making same-person blends genuine costs landmark-morph detection" (numbers beside it) | Ablation row. FINAL unchanged. |
| T met, G1 inconclusive | "No claim about the cost to landmark-morph detection" | Ablation row. FINAL unchanged. |
| T met, G2 or G3 fails, attributable to SE | "Same-person flags can be removed only at the cost of [storage / camera-photo] flags" | Ablation row. FINAL unchanged. |
| T met, G2 or G3 fails for Sb as well, or G2 uninformative | "The [storage / camera] guard is not informative at these seeds" | Ablation row. FINAL unchanged. |
| T "reduced, not removed" | "Same-person blend flags are reduced but not removed" | Ablation row. FINAL unchanged. The paper reports Sb's same-person flags as a limitation. |
| T not met or inconclusive | "Same-person blends as negatives did not change the same-person flags at this dose" | As above. |
| ≤ 3 read seeds | "not read (too few seeds)" | FINAL unchanged. |

Never written: "shortcut-free", "reads identity", or any benchmark or generalisation claim. Every number here is development data.

## 9. Printed only (no verdict)

- Platform reproduction check, run by the smoke job on the chosen platform:
  - FS1's Sb seed 403 (A100, torch 2.2.1; tar `PN1_Sb_s403.tar`, sha256-checked) is rescored with the unchanged `src/PN1/rescore.py` (`6f6eede7…`) on the C2P gate rows (fam af0 1,339, ffhq 5,000).
  - It is compared with the stored FS1 logits by `c2p_read.gate`: 99th percentile |Δlogit| ≤ 0.05, maximum ≤ 0.10, own-rule agreement ≥ 99.5%.
  - Printed with "platform reproduces FS1 scores" or "platform differs".
  - It decides nothing, because every SE1 comparison is within the platform. It says whether SE1 numbers may be set beside FS1 numbers.

- Sb refit against FS1's Sb (A100): development S3 and R3 flags (platform shift, descriptive).
- Own-rule flags on each training-row kind (from scores_train.npz), beside development rows of the same kind (underfit against no generalisation: strategist Z1).
- All section 9 items are computed by `se1_read.py` (the platform check with `--platformcheck <smoke tar>`), in the same single run.
- Own-rule flags on the FFHQ HN2 history-matched genuine pool (landmark_complete_resmatch) and misses on landmark_complete morphs.

## 10. Disclosures

- The owner read FS1's development flags for A, B and Sb on every development rung (table in section 1) while designing this arm and setting the 10% bars. The strategist had read the S3, S0 and S4 values earlier.
- The mirror self-morphs are left-right symmetric. A network could learn "symmetric means genuine". The primary target reads (S3, R3) contain no mirror image; R3m and self-morph flags are printed only.
- Engine overlap: the target reads S3 and R3 (OpenCV) are image kinds present in SE's training, on unseen persons. The FaceMorpher reads are the held-out-engine check.
- The 10% bars, the −0.02 / +0.05 margins and the C2P rule come from the lead's message (13 Nov), the strategist's item #5 and C2P. The R3 co-target and the G1/G3 detail are the owner's.

## 11. Budget and stop rule

- 15 fits plus one smoke on WCSS H100: about 16 GPU-hours (about 1 h per fit including scoring; the smoke prints the step rate and the fit time limit is checked against it).
- No rented machine.
- A failed task is re-run once unchanged, never because of its values.

## 12. Commands

```
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python   # system python3 has no numpy
# images and manifests (DGX, done before this registration; images only, no statistic)
$PY -I src/SE1/build_selfm.py --check && $PY -I src/SE1/build_selfm.py
$PY -I src/SE1/mk_se.py
# WCSS (through the dispatcher queue): smoke, then fits
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SE1 && sbatch --extra=FORCE_RM_TMPDIR se1_smoke.sbatch
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SE1 && sbatch --extra=FORCE_RM_TMPDIR se1_fit.sbatch
# after the registration commit, before any tar is pulled
$PY -I src/SE1/baseline27_se1.py
# once, after the fits
$PY -I src/SE1/se1_read.py --platformcheck <SE1_platformcheck_<job>.tar> --out experiments/SE1_seam-shortcut-training-arm/se1_read.json
```

## 13. Pins at the registration commit

| File | sha256 |
|---|---|
| src/SE1/run.sh | b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb |
| src/SE1/se1_read.py (reader) | 1a8cdec630e482aa6ca5958ef860be7930444b57809554a6de4bd597ce8c8825 |
| src/SE1/baseline27_se1.py | 07d14c80f5801560f021277428f5097d09584d34b48719bacf3d263b551f2478 |
| src/SE1/build_selfm.py | be2cbfddc4c24c45750e7760cf75f1effc448eae46aff6d0e21d44b5434b92f0 |
| src/SE1/mk_se.py | fb155a1142d4e065513e663b2346c0f561184183dd688b1200676922a8aacf1c |
| src/SE1/wcss/se1_fit.sbatch | 0ba1aab483094623bae26dde048eda6c2f89b18fc3f6283ea0e869b0434a955f |
| src/SE1/wcss/se1_smoke.sbatch | d48b2c2811f7b1125f1b9456daa4f5511eeee81e7cabc7a4a5c57d8291709b29 |
| src/SE1/athena/se1_fit_athena.sbatch | a5a349c81d98bd2705afbbc9bc9e0279054ae0f3e5185f0ce4d302326706e309 |
| src/SE1/athena/se1_smoke_athena.sbatch | 57d3b7554cd2e962c6c3412678db8253d511974762ae90cf5b6a94ef24055b5e |
| src/SE1/rented/drive_se1.sh | 06a3e6938e105113fcc5fac3dd28b252bcf6e0c1a501da5bcfe76500c39390e3 |
| src/SE1/rented/remote_se1.sh | 6f773c407adddafc78d24fa620160d15581d41a9e6862c3e76e4b6622e07b150 |
| src/PN1/c2p_read.py (imported) | 45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840 |
| FS1 pack pn1_pack_fs.tar | 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 |
| SE1 overlay se1_overlay.tar | de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c |
| train_SE.csv | c4e5aa474c87399d5e80af8afec3737a33b54afc35ae721b11385a5f5814525b |
| se_eval.csv | 6dcef964d8ca3024d353aaa1e568e42ba2f2454b1f1a36442311aa5f9b598f7c |

The job files hard-code the run.sh and overlay pins (they do not trust a .sha256 file stored next to the file they check).

## 14. Pre-run check

experiment-reviewer (Opus), 13 Nov 2026: **GO WITH FIXES** (`experiments/reviews/PRERUN_SE1_20261113.md`). How each finding was handled:
1. Seed collision with AB1: AB1 reuses SE1's A and Sb (section 3), and no SE1 tar is pulled before AB1's registration or the lead's written waiver (section 4).
2. G1 noise: decided on seed means with a bootstrap interval; an "inconclusive" row was added (sections 7.2 and 8).
3. G3 absolute bar on FFHQ: dropped; only the relative leg remains for FFHQ and MS1 (section 7.4).
4. Storage cue: stored R3 at 61.2 and 112.7 px joined the target; stored R4 is printed; the dilution is disclosed (sections 3 and 7.1).
5. Attribution: made conditional on Sb; "uninformative" is reported separately (sections 7.3, 7.4 and 8).
6. Pins: section 13; the job files hard-code them.

Minor points: (a) the docstring seeds were fixed; (b) $PY is used in place of system python3; (c) a full-run check was added; (d) section 9 is in the reader; (e) the Athena twin is now registered (lead's order, section 4); (f) the seed ruling is recorded; (g) the flip precedent is cited; (h) the half rule uses integer counts; (i) the loss regex handles -inf and nan; (j) the symmetric share is disclosed; (k) the deadline note was added.

## Deviation SE1-D1 (`date`: Fri Nov 13 09:17 CET 2026; committed before any SE1 fit has started; no score of any SE1 network exists): platform moved to rented A100 PCIe 40 GB

- **Why.** WCSS gave our jobs no start (priority 681 against 10,821; smoke 6310083 forecast 15:30; fit array 6310122 without a forecast). Athena's A100 partition is reserved until about 22 Dec. The lead moved SE1 to rented machines, and the author approved the budget (13 Nov about 09:25).
- **Platform.** Every SE1 network is fitted and scored on rented A100 PCIe 40 GB machines with the image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` and FS1's pip pins (timm 1.0.27, numpy 1.26.4, pillow 10.2.0, huggingface_hub 0.36.2, safetensors 0.8.0, pyyaml 6.0.3). This is the GPU model and software stack of the FS1 networks.
  - The WCSS jobs 6310083 and 6310122 are cancelled by the dispatcher once the first rented fit has started. No WCSS or Athena result of SE1 exists or will be read.
- **Layout.** One lease = one whole seed (A, Sb, SE in this order).
  - se1a: seed 408. se1b: seed 409. se1c: seed 410.
  - Seeds 411 and 412 run on further A100 PCIe 40 GB leases only if the author approves the budget. pn1fs may be one of them.
  - A seed that cannot start by **14:15 CET** (about 0.5 h upload and setup, 0.25 h smoke, 3 × about 1.4 h fits) cannot end by the registered 19:00 deadline. Such a seed is not started, and the counting rule of section 7 applies to the seeds that finish.
- **Code.** The registered `src/SE1/run.sh` (b2a975f1) runs unchanged with the FS1 pack (96c31ae2…, uploaded from the DGX in four parallel chunks and sha256-checked on the lease) and the SE1 overlay (de26d6ce…). Rented drivers:
  - `src/SE1/rented/drive_se1.sh` (542c81a7…);
  - `remote_se1.sh` (d9ea96b3…);
  - `chain_se1.sh` (caca7866…).

  `run_rented.sh` (4f51b9a4…; MS1 base pack for the shared L40S hosts) was staged as a fallback and is not used. Its staging on the MS1 hosts was removed before any GPU use.
- **Smoke and reproduction check on every lease** (section 9, unchanged): 100 steps, 64 rows, and FS1's Sb seed 403 rescored on the gate rows. The seed's fits start only if that lease's smoke passed. The gate verdict is printed per lease.
- **AB1.** AB1 no longer reuses SE1's A and Sb networks (lead, 09:10); it fits its own on WCSS. Section 3's sentence about AB1 reusing these networks is void.
- **Fetching versus reading.** OWNER_BRIEF requires every rented output to be fetched and verified in two copies before a lease is released. The blindness rule of section 4 is therefore applied to reading: tars are fetched and hash-checked as they finish, but no SE1 score file is opened (by the reader or anyone) before AB1's registration commit exists or the lead waives the rule in writing.
- Caps and deadlines of the leases are the lead's (guard running). RELEASE is written by chain_se1.sh only after the seed's three fit tars and the lease's platform-check tar are verified in two copies (`/mnt/t7/smad_next/SE1/results`, `/home/narolski/se1_results_copy`) and the logs are fetched.

- SE1-D1 addendum (`date`: Fri Nov 13 09:38 CET 2026; fits running since 09:35; no score opened): following REVIEW_PN1_C2P_20261113 Q5/F6 (lead), the per-lease reproduction check is labelled **"precision and GPU together"**. rescore.py runs with TF32 off, while the stored FS1 A100 logits were made with TF32 on, so a miss is not a platform failure of the lease. It never gated the fits: the chain gates only on the smoke's "smoke rc 0". Reader change, print labels only and one tar per lease accepted: se1_read.py `794bed6e7257c2c69ec7a0ceb18b0942559dabceed3349b6ce5f3fee603534da`. Pass rules and every verdict are unchanged. Platform record: the fits started at 09:35:51 (se1a, seed 408) and 09:35:52 (se1b, seed 409). The WCSS jobs 6310083 and 6310122 were cancelled at 09:37 without having started. AB1 is registered at 61f7994, so the reading condition of section 4 is met.

## Deviation SE1-D2 (`date`: Fri Nov 13 12:39 CET 2026; before any seed-411 fit; no SE1 score file opened): fourth seed on a fourth A100 PCIe lease

- The lead (12:40, within the author's rental approval): seed 411 runs on pn1fs (149.248.21.7:30078). That is an A100 PCIe 40 GB, the same GPU model and image as se1a/b/c, and the machine that trained the FS1 networks.
- Pack: the FS1 pack already on that machine (`/workspace/pn1/root/packs/PN1/pn1_pack_fs.tar`, its sha256 file reads 96c31ae2…). It is read in place through a symlink and sha256-checked by remote_se1.sh and run.sh before use. Only the overlay and small files are uploaded. SE1 writes only under /workspace/se1.
- The same smoke and per-lease check (labelled "precision and GPU together") run first. The fits start only if the smoke passes.
- pip setup is not run on this host, so the shared environment is untouched. The check step asserts the pinned versions (torch 2.2.1, timm 1.0.27, numpy 1.26.4, pillow 10.2.0; already verified at 12:39).
- The lease is held by the lead. The chain writes no RELEASE there (`SE1_NO_RELEASE=1`; chain_se1.sh `9dc4e74873186e23091d85164473f91a9a1683d5aa15f39967e2f102c70fc17f`) and reports to the lead once seed 411 is verified in two copies.
- Disk: 27 GB free; one fit needs about 20 GB (pack copy, extraction and overlay).
- Seed 412 is not run. With seed 411 there are four read seeds, and section 7 then reads "met" only as 4 of 4.
- Reading (lead, 12:40): one read, after seed 411's tars are in, or at the 19:00 deadline if that comes first.

- SE1-D2 amendment (`date`: Fri Nov 13 13:13 CET 2026; before any seed-411 fit): seed 411 runs on a fresh A100 PCIe 40 GB lease **se1d** (instance 60495180, 185.130.165.20:26693, lease folder /mnt/t7/smad_next/vast/se1d) instead of pn1fs. Reason: pn1fs's uplink fell to about 0.2 MB/s with dropped connections, and the proxy route timed out (13:06–13:11). It is the same setup as se1a/b/c: the FS1 pack uploaded and sha256-checked, pip pins, a smoke with the per-lease check, then the 3 fits. It is a normal SE1 lease, so RELEASE is written after two verified copies (no SE1_NO_RELEASE). The partial files under /workspace/se1 on pn1fs are left as they are (lead: clean nothing there); nothing of seed 411 runs there.
