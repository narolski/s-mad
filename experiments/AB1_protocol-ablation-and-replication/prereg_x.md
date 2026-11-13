# Border-crossed protocol network (Sbx, AB1 follow-up): registration

Written 13 Nov 2026 from 18:05 CET by the AB1 owner on the lead's instruction (17:55; strategist's evening synthesis
`experiments/reviews/STRATEGIST_EVENING_20261113.md`, section 3, experiment 5). Binding at the git commit that adds this
file under this name, after the pre-run check `PRERUN_AB1X_20261113.md`; no Sbx network exists at that commit. A
post-freeze remedy row: it cannot become the method.

**Background (reviewed; TT1 result.md, follow-up Z3, A100 PCIe, seeds 403-407):** once a constant-colour border shaped
like a CFP-FF frame's is blanked into training-source camera photos, Sb flags 2.9-16.3% of them and the protocol-only
arm B 0-1.9%; neither flags any without the border. Averaged over all seven mask families (the quantity this rule
reads), Sb's A100 border flag share was only 4.0 / 2.8 / 2.7 / 1.4 / 5.2% and B's 0-0.9% (`tt1_read_fs.json`), so on
H100 with new networks and 226 development photos the control may well fail and "uninformative" is a likely outcome;
the bar is not moved for that. **Disclosure:** the rule below was set knowing those A100 numbers
and the AB1 H100 results; the H100 border level of Sb at 408-412 is not known at this commit.

## Arm and training data (built: `src/AB1/mk_ab1x.py`; `/mnt/t7/smad_next/AB1/x/ab1x_summary.json`)

- **Sbx** = Sb's 5,535 unique training rows + border-blanked copies of 25% of the unique rows of every row kind (1,385
  copies: af0_half 364, af0_half61 91, af0_photo 130, af0_photo61 64, af0_u50 182, af0_u5061 92, af0_zero 182, lad_R0
  39, lad_R2w 39, lad_R4 31, lad_S0 39, lad_S3 39, lad_S4 31, lad_half 62; 1,049 negatives, 336 attacks, the same 25%
  rate in every kind), chosen and masked with `numpy.random.default_rng(20261161)`.
- **Image operation:** constant-colour region blanking only (approved): pixels under a border mask set to (0,0,0), with
  the mask function `edge_mask` of `src/TT1/build_border_ref.py` imported unchanged (largest exactly-black region
  connected to the frame edge of an aligned 512 px frame). Lossless PNG.
- **Which border:** each copy gets the mask of one TT1 primary unseen-source frame (U_p) drawn from the 17,374 U_p frames
  that are **not** the mask of any TT1 border reference, so no evaluation mask frame is a training mask frame (pre-run check: 0 of 3,002 bit-identical; median masked fraction
0.416 in training, 0.425 and 0.416 in the evaluation rows, the same for training negatives and attacks). Most mask
families are well represented in training; MSU-MFSD (no training mask) is the only unseen-family read and is named as
the key printed share. **Embargo:** Sbx is never read on TT1 unseen-source rows (fam tt1), because the border geometry
of 1,325 TT1 U_p frames is in its training. Mask
  families drawn: LFW/CALFW 738, CFP-FF 333, AgeDB 259, Oulu-NPU 50, CASIA-FASD 4, Replay-Attack 1, MSU-MFSD 0 (the
  pool's composition). Per-copy log: `/mnt/t7/smad_next/AB1/x/border_train_log.csv` (copy id, source id, kind, label,
  mask id, mask family, masked fraction, sha256). Only mask geometry enters training; no TT1 image does.
- **Class balance of bordered rows:** bordered rows get history "<hist>_border" and so form their own database ×
  history strata (frgc/feret × native_border/s61_border); the unchanged amendment-4 balance makes each stratum exactly
  half attacks, so bordered rows are class-balanced (2,098 of 10,484 rows after the balance, 20%). Not volume-matched
  (the copies are new images; 6,920 unique against Sb's 5,535).
- Manifest `train_Sbx.csv` 4e403717…; overlay `ab1x_overlay.tar` e5886e72… (1,180,651,520 bytes, 4,969 files incl.
  AB1XSUMS; adds files, replaces none).

## Evaluation rows (in the overlay; added to the pack)

`ab1x_eval.csv` 5257fb63… = ab1_eval.csv (21,277 rows, unchanged) + 3,582 border rows copied unchanged from the TT1
border references (sha256 checked): `R_cam_border` of development persons only (development-ladder R0 100 and AF0
development photos 126, each with one mask from each of 7 unseen-source families: 1,582) and `R_ffhq_border` (2,000
FFHQ HN2 development photos, one mask each). Test-ladder references are not added (AB1 does not read the test ladder).
The unseen-source genuine frames of TT1 (fam tt1) are **not** in this pack; the "unseen-source development reads" asked
for would need the TT1 pack rows added (about 21,000 images) and are not part of this registration.

## Networks, platform, scoring

- Sbx at seeds 408-412, FS1 recipe and `train.py` unchanged, 6,250 steps, last checkpoint; WCSS H100;
  `src/AB1/run_x.sh` (0051ba1f…; a copy of run_b2.sh with only overlay, SUMS name, arm list, evaluation manifest and
  results folder changed); job `src/AB1/wcss/ab1x_fit.sbatch` (3b019353…, array 0-4, limit 1:15). Each Sbx network is
  scored in its own fit job on all 24,859 rows.
- Comparison networks: AB1's H100 Sb (and B, printed) at the same seed. Their landmark_combined, S3 and C2P scores come
  from their AB1 fit jobs; their border-row scores come from one H100 rescoring job (`src/AB1/wcss/ab1x_rescore.sbatch`
  b5b4da1c…; unchanged rescore.py through rescore_tf32.py, TF32 on, same software build), which also rescores
  landmark_combined as a job-path check (printed: 99th percentile and maximum |Δlogit| against the fit-job scores).
  Every statistic of a network comes from one job. The rescoring job needs no Sbx output and is submitted with the fits.

## Hypothesis H-x1 and rule (own rule, logit > 0)

Read: share of the 1,582 development camera photos with a blanked-in border that the network flags (counts compared as
integers: ≤ 2% means count × 50 ≤ 1,582).
- **Control:** AB1's Sb must flag more than 2% of them on ≥ 4 of 5 read seeds; otherwise "uninformative (nothing to
  remove on this platform)".
- **Supported (pass):** Sbx flags ≤ 2% AND at most half as many as Sb at the same seed (count × 2 ≤ Sb's count) AND
  Sbx − Sb landmark_combined ≥ −0.02, on ≥ 4 of 5 seeds: border crossing removes
  the border reaction at the decision rule on unseen border shapes at little detection cost (development data; a
  remedy row, post-freeze).
- **Falsified:** on ≥ 4 of 5 seeds, Sbx flags at least as many as Sb at the same seed, OR its landmark_combined falls by
  more than 0.02: border crossing does not reduce the reaction, or only at a detection cost.
- Otherwise "inconclusive, no claim". With 4 read seeds: 4 of 4; ≤ 3: "not read (too few seeds)".
- **Job-path check (binding):** Sb's border scores come from the rescoring job and Sbx's from its fit job. For every read
  seed, Sb's landmark_combined scores from the rescoring job must match its fit-job scores to max |Δlogit| ≤ 0.01 with no
  own-rule flip; otherwise H-x1 is "job path unverified, no claim".
- **Printed only:** per-family border flag shares with B as the floor (MSU-MFSD, never drawn in training, is the key
  share; Replay-Attack and CASIA-FASD almost never drawn), FFHQ border flags (2,000), the unbordered camera-photo and FFHQ native flags, B's border flags, Sbx's
  C2P quantities and C2P per-seed passes against A, development same-person splice (S3) placement, landmark_combined,
  and the job-path check.
- Builder `src/AB1/mk_ab1x.py`, reader `src/AB1/ab1x_read.py` (sha256 of both in `pins_x.sha256`); the reader was
  mock-tested with Sbx border logits shifted −3, 0, +3 (supported, inconclusive, falsified as intended). Local DGX test
  of run_x.sh (20 steps, 8 rows): rc 0, 10,484 training items; all 3,582 border evaluation PNGs load as 512×512×3 (the
  8-row test did not reach the border rows); read once when the 5 fits and the rescoring
  job have ended, latest 15 Nov 2026 18:00 CET (author's ruling, 13 Nov 17:15); later rows labelled late.

## Budget

5 fits × about 40 min + one rescoring job (about 15 min) ≈ 3.5-4 H100-hours.

## Pre-run check (`PRERUN_AB1X_20261113.md`)

GO WITH FIXES; applied before this commit: F1 supported also needs Sbx ≤ ½ × Sb's count; F2 A100 all-family shares
disclosed, "uninformative" likely; F3 job-path check binding (max |Δ| ≤ 0.01, no flip; threshold 0.01 rather than the
suggested 1e-3 because batch composition alone moved scores by more than 1e-3 in TT1's gates); F4 wording ("no
evaluation mask frame is a training mask frame"), MSU-MFSD named, TT1 embargo; F5 pins file; F6 border PNGs checked to
load; F7 shifted mocks. Not taken: a McNemar print (optional).

Note on times (`date`: Fri Nov 13 18:48 CET 2026; relayed correction of the lead's times; nothing else changes): the author's cut-off ruling quoted as "13 Nov 17:15" was committed at about 17:11 by the machine clock. The header's "written from 18:05" and "the lead's instruction (17:55)" were not machine-clock times: this registration was committed at 17:56 (git 7e4a974) and written in the half hour before; the lead's instruction arrived before that.
