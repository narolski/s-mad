# Second morphing engine in training (SbFM, AB1 follow-up; strategist's TD1): registration

Written 13 Nov 2026 from 18:55 CET by the AB1 owner on the lead's instruction (18:50), with the author's explicit go
("yessss! Do this!" to "more kinds of morphs: we train on one OpenCV-style engine only; adding FaceMorpher-style morphs
with their matched negatives targets the Webmorph and FaceMorpher cells"). Binding at the git commit that adds this
file under this name, after the pre-run check `PRERUN_AB1FM_20261113.md`; no SbFM network exists at that commit.

**Status: post-freeze arm.** The author froze the candidate (Sb, seeds 403-407) at 18:28. SbFM cannot replace the frozen
method unless the author changes the freeze before the sealed read (the lead is asking him). It is a development row.

**Disclosure.** Known at writing: every AB1 result at seeds 408-412 (result.md), including Sb's landmark_combined AUC
(0.873-0.906). The engine-crossed test-ladder AUCs registered below were never seen by anyone for any network at
408-412: the AB1 reader does not compute them; one loading-path test of `ab1fm_read.py` on the real AB1 tars (18:20,
before the pre-run check) did compute them into a scratch JSON, which was deleted unopened at 18:42 (pre-run check F1);
no other run on real tars is made before this commit. The +0.02 / +0.005 bars are the lead's (strategist's TD1). The
strategist made TD1 conditional on a zero-GPU tool-gap read (Z3, gap ≥ 0.03); the author's explicit go overrides that
gate. Seeds 408-412 (not the strategist's 403-407) pair SbFM with the H100 Sb, A and B.

## Arm and training data (built: `src/AB1/mk_ab1fm.py`; `/mnt/t7/smad_next/AB1/fm/ab1fm_summary.json`)

SbFM = Sb's 5,535 unique rows + FaceMorpher-engine ladder rows of training hosts, selected by the same rules as Sb's
OpenCV ladder rows (PN1 split; catalog role "train"):
- `lad_R4fm` (attack): FaceMorpher two-person whole-frame morph R4 of the 124 hosts whose partner is also a training host;
- `lad_R2wfm` (negative): FaceMorpher warp-only image toward the host's own two-photo mean shape, 156 hosts;
- `lad_R2w4fm` (negative): FaceMorpher warp-only image toward the two-person mean shape (the engine's warped host, i.e.
  the host-side half of R4), 124 hosts.
Images: unchanged AR1 FaceMorpher outputs (`/mnt/t7/smad_next/AR1/img/frgcferet/facemorpher/`), copied; no new image
operation. 404 rows added (7.3% more unique images; 5,939 unique).

**Rows (pre-run check F2):** train_Sb.csv's 8,386 rows are kept unchanged (same rows, same order, so Sb's own repetition
is untouched), and the FaceMorpher rows are appended as a block balanced on its own within each database by the
amendment-4 rule: R4fm attacks repeated to equal the FaceMorpher negatives (FRGC 232 / 232, colorFERET 48 / 48; 560
rows, attack share exactly 0.50). The first build, which re-balanced the whole manifest, gave FaceMorpher rows an
attack share of 0.594 (an engine-identity prior) and changed Sb's repetition; it was replaced before registration.
Total 8,946 rows.

Not added, and why:
- **FaceMorpher splices (S4/S0/S3):** their seam-only negatives carry almost no seam (REVIEW_SPLICE_20261111: boundary
  colour step 1.06 for S0 against 15.83 for S4, AUC 0.999), so they would teach a trivial seam cue. File check here: the
  FaceMorpher S0 files differ from their R2w4 base by 1.67 grey levels on average (30 hosts; OpenCV 1.93), consistent
  with the review; not a seam measurement.
- **The partner-side FaceMorpher half:** it does not exist; building it would be a new engine run. R2w4fm stands for the
  host-side half; OpenCV keeps both halves (lad_half).
- **Stored-small ladder copies:** Sb has none for either engine (PN1 section 4); the AF0 stored copies are unchanged.

Row shares (% of rows): af0_u50 30.30, af0_half 16.28, af0_zero 8.16, af0_u5061 6.90, af0_photo 5.79, lad_R4 4.86,
lad_S4 4.81, af0_half61 4.06, lad_R4fm 3.13, af0_photo61 2.84, lad_half 2.77, lad_R0 1.74, lad_R2w 1.74, lad_S3 1.74,
lad_S0 1.74, lad_R2wfm 1.74, lad_R2w4fm 1.39 (Sb: lad_R4 5.19, af0_u50 32.33). FaceMorpher rows are half attacks;
OpenCV ladder rows keep Sb's shares scaled by 0.94.

**Volume:** 8,946 rows against Sb's 8,386 at fixed steps: each Sb image is seen 0.94× as often. Not volume-matched and
no separate control: the change (6%) is below the repetition differences already disclosed for Sp (8%) and Bv; stated
with every comparison. (A control would need 5 more fits; the lead asked for one only if material.)

Manifest `train_SbFM.csv` 12312044…; overlay `ab1fm_overlay.tar` 681525d8… (1,048,453,120 bytes, 3,988 files with
AB1FMSUMS: the manifest, ab1x_eval.csv and its 3,582 border images, the 404 FaceMorpher training images; adds files,
replaces none).

## Networks, platform, scoring

SbFM at seeds 408-412, FS1 recipe and train.py unchanged, 6,250 steps, last checkpoint; WCSS H100; `src/AB1/run_fm.sh`
9c04e3bd… (run_x.sh with only overlay, SUMS name, arm and results folder changed); job `src/AB1/wcss/ab1fm_fit.sbatch`
cefd29c6… (array 0-4, limit 1:15). Scored in its own fit job on all 24,859 rows of ab1x_eval.csv. Compared within seed
with AB1's H100 Sb, A and B (fit-job scores).

## Reads and rules (own rule logit > 0; development data only; FRLL, MAD22 and every closed set absent from every pack)

Seed counting as AB1 (≥ 4 of 5; 4 of 4 with n = 4; ≤ 3 "not read"); margins inclusive.
- **H-fm1 (primary): unseen landmark tool.** FFHQ landmark_combined (a Mediapipe-based warp-and-blend tool unseen by both
  arms; near transfer): SbFM − Sb AUC ≥ +0.02 on ≥ 4 of 5 → supported (a second training engine improves detection of
  morphs from an unseen landmark tool on this development set); < +0.005 on ≥ 4 of 5 → falsified ("a gain of at least
  +0.005 is not seen on 4 of 5 seeds on FFHQ landmark_combined"); otherwise inconclusive. Noise (pre-run check F7):
  between-arm seed SD about 0.013, image-bootstrap SE about 0.007; with a true effect of 0, "falsified" has probability
  about 0.43 and "supported" needs a true gain of about +0.03, so "inconclusive" is likely. Seed mean ± t interval
  printed.
- **H-fm2 (secondary, trained engine): test-ladder FaceMorpher R4 against FaceMorpher R2w** (191 test hosts): SbFM − Sb
  ≥ +0.02 on ≥ 4 of 5 → supported; < +0.005 → falsified. A seed with Sb ≥ 0.98 on this read is untestable (pre-run
  check F4, as R2's ceiling); Sb's level is printed beside each difference. Expected to be supported (FaceMorpher is now a training
  engine; FaceMorpher test hosts are disjoint persons); it is not a transfer claim.
- **H-fm3 (guard): no loss on the original engine.** Test-ladder OpenCV R4 against OpenCV R2w: SbFM − Sb ≥ −0.02 on ≥ 4 of
  5 → supported (no loss); < −0.02 on ≥ 4 of 5 → falsified (loss). Same ceiling rule (Sb ≥ 0.98 untestable).
- **Printed (engine-crossed table, per network SbFM, Sb, A, B):** test and development ladder AUCs of R4 against R2w and
  against R3 for both engines, R3 (same-person morph) placement and R4 misses for both engines; storage reads (C2P
  quantities and per-seed passes against A, as AB1); development same-person splice (S3) placement; camera-photo and
  FFHQ native flags; the border rows built for Sbx (SbFM from its fit job; Sb and B from rescoring job 6314812,
  labelled "other job", no comparison claimed); engine-prior diagnostic: development FaceMorpher R2w and R2w4
  placement and FFHQ native-photo flags, SbFM against Sb.
- Reader `src/AB1/ab1fm_read.py` (sha256 in `pins_fm.sha256`), mock-tested (no shift → H-fm1 falsified; +1 logit on
  landmark_combined morphs and on test FaceMorpher R4 → H-fm1 and H-fm2 supported). A loading-path test on the real AB1
  tars is run only after this commit.
- Read once when the 5 fits have ended, latest 15 Nov 2026 18:00 CET (author's ruling); later rows labelled late.

## Budget

5 fits × about 40 min ≈ 3.5 H100-hours.

## Pre-run check (`PRERUN_AB1FM_20261113.md`)

GO WITH FIXES; applied before this commit: F1 the loading-path output was deleted unopened, the test is repeated only
after the commit; F2 Sb's rows kept unchanged and the FaceMorpher block balanced on its own (attack share 0.50); F3
README section and pins file; F4 ceiling rule for H-fm2/H-fm3; F5 the strategist's Z3 gate and the seed choice stated;
F6 wording ("unseen landmark tool", falsified wording); F7 noise disclosure and seed-mean print; F8 mock shifting test
FaceMorpher R4. Improvement 3 (engine-prior diagnostic) printed.

Note on times (`date`: Fri Nov 13 18:48 CET 2026; relayed correction of the lead's times; nothing else changes): the lead's instruction quoted as "18:50" arrived between 18:32 and 18:46 by the machine clock (the lead's times were about 45 minutes ahead); the header's "written from 18:55" is likewise not a machine-clock time: this registration was written in the minutes before its commit at 18:43 (git 9c0ed39). The freeze ruling (18:28) is right to the minute (about 18:27). In the disclosure, the loading-path test time "18:20" is an estimate; it ran before the pre-run check, and the scratch file was deleted at 18:42 by the machine clock.
