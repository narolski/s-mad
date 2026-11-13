# Multi-source training set for threshold transfer (MS1)

## 1. Question and current answer

Do genuine photos, morphs and matched controls from a third capture source (FFHQ) in training make the decision
threshold of the protocol network (PN1 recipe, Sb manifest) carry over to genuine photos of unseen sources?
Status 12 Nov 2026 23:20 CET: build plan registered (`prereg.md`, 3d4411b); FFHQ source built (3,263 unique training
images, 1,500 hold-out images), exclusion proof passes, all pixel and path gates pass; multi-source manifest SbM3 written
(13,414 rows; FRGC / colorFERET rows equal train_Sb's). Multi-PIE unusable; FLUXSynID ruled out by the author.
Pack being built; part 2 (training comparison) to be drafted and reviewed. No fit, no score.

## 2. Timeline

- 12 Nov ~22:55 CET: author approved the build ("3. Please do build it ASAP."); 50 USD rental budget for the day.
  Owner's `date` at recording: Thu Nov 12 11:01:39 PM CET 2026.
- 12 Nov ~22:57: Multi-PIE inspected (zip listing; 3 crops through the unchanged aligner): 128 x 128 crops only, session
  01, 249 subjects, eye distance about 39 px -> unusable (prereg section 0). Lead agreed.
- 12 Nov ~22:58: FLUXSynID inventoried from the zip listing (14,889 identities; per identity one 1024 px document-style
  JPEG and three live JPEGs `live_0_{a,e,p}`; identity filter lists inside) and one identity's 4 images measured in the
  scratchpad. 23:05: author ruled "Do not use FluxSynID"; scratchpad copies deleted, zip untouched, nothing built.
- 12 Nov 23:03: plan (`prereg.md` part 1) committed at 3d4411b before any build step.
- 12 Nov 23:05-23:08: FFHQ person selection (`src/MS1/run_select.sh`: `ffhq_select.py refs`, then `select --n 900`):
  1,833 candidates attempted, 821 failed the aligner (no face or frontal filter), 112 dropped as identity duplicates
  (103 against the ffhqm references, median cosine 0.565, up to 0.92; 9 against earlier kept frames), 900 kept
  (450 af0, 150 ladder, 300 hold-out). In parallel `excl_sha.py`: sha256 of the 20,000 excluded raw files.
- 12 Nov 23:09: `gate.py path`: the MS1 wrappers reproduce 4 AF0 u50, 4 zero, 4 halves, 4 fm61 copies and 4 AR1 R4
  OpenCV files pixel for pixel (20 of 20; `gate_path.json`).
- 12 Nov 23:10: `proof.py`: exclusion proof passes (`exclusion_proof.json`): 0 overlaps by key and by raw sha256; largest
  cosine to the ffhqm references 0.396, among kept 0.391, hold-out vs training 0.374; no benchmark path in any list.
- 12 Nov 23:11: `ffhq_build.py plan` (`plan_summary.json`): 400 + 400 training pairs, 150 + 150 hold-out pairs, 1,100
  halves, 1,525 stored copies to build, 150 ladder hosts (look-alike partner cosine median 0.173).
- 12 Nov 23:12-23:14: `run_build.sh`: morph stage (1,100 pairs, 150 R4 through 78_tool_morph, 300 ladder halves, 150
  R2w4), stored copies (1,525 rows, 32 failed re-alignment and are dropped), `gate.py pixel` (8 u50, 8 zero, 8 R4: all
  equal to the unchanged engine; `gate_pixel.json`).
- 12 Nov 23:14: `mkmanifest.py` -> `/mnt/t7/smad_next/MS1/manifests/train_SbM3.csv` sha256 `885dff9d…`
  (`manifest_SbM3_summary.json`); FRGC / colorFERET rows equal train_Sb's as a multiset (asserted).
- 12 Nov 23:15-23:17: `build_pack.py` -> `/mnt/t7/smad_next/MS1/pn1_pack_ms1.tar` sha256 `dac228f5…` (14,508,625,920
  bytes, 51,272 files); evaluation manifest `d1fab6ad…` (42,366 rows: FS1 19,797, MS1 FFHQ hold-out 1,480, TT1
  21,089). Tree of symlinks `/mnt/t7/smad_next/MS1/pack_tree/`.
- 12 Nov 23:17: draft of part 2 (`prereg_comparison_draft.md`, commit cb1cf09) sent to the lead for pre-run review.
- 12 Nov 23:18-23:20: DGX smoke of `src/MS1/run.sh` (20 steps, 64 scoring rows, SbM3 seed 403, pinned pack):
  passed; result `/mnt/t7/smad_next/MS1/smoke/results/MS1smoke_SbM3_s403.tar`; work folder (14 GB, mine) deleted.
- 12 Nov 23:21: reader `src/MS1/ms1_read.py` written and tested on mock scores (`ms1_read_mock.json`); commit c1c4224.
- 12 Nov 23:21 (before commit 03198c5 at 23:22:09): inventory of new candidate sources (no build; lead's instruction), see section 8.
- 12 Nov ~23:22: pre-run review `experiments/reviews/PRERUN_MS1_COMPARISON_20261112.md`: GO WITH FIXES (B1 register,
  B2 reader before fetch, B3 sharp unseen source; M1-M5; minors). Lead rulings: CFD becomes a held-out evaluation
  source (never training), KDEF printed secondary, data-volume control arm SbV, owner may upload and submit on WCSS.
- 12 Nov 23:23-23:25: `heldout_pool.py cfd` (831 of 831 aligned, 827 persons) and `kdef` (140 of 140, 70 persons);
  `mkmanifest_vol.py` -> train_SbV (13,414 rows, `8920699f…`); run.sh: arm SbV and env.txt line; pack rebuilt with
  train_SbV.csv: `c11b16bc…` (the reviewed pack `dac228f5…` deleted after the rebuild; it differed only by that file).
- 12 Nov 23:26:12: part 2 registered in `prereg.md` at f748da4 (pins included).
- 12 Nov 23:27:54: upload of the pack and scripts to WCSS started (`/mnt/t7/smad_next/MS1/logs/upload.log`).
- 12 Nov 23:29: reader extended (P1-S, P1-T, SbV prints) and tested on mock scores incl. a supported path; commit
  de10419 (B2), sha256 `5e5ada46…`.
- 12 Nov 23:30: held-out scoring pack `ms1_heldout_pack.tar` (`06b64608…`, 971 rows: CFD 831, KDEF 140; manifest
  `b3fe4e77…`) and `wcss/ms1_heldout.sbatch`; tested locally on the smoke result (RESCORE_DONE 831 and 140).
- 12 Nov 23:27:54-~23:36: pack and scripts uploaded to WCSS; 23:43 held-out pack and job uploaded; 23:46 on WCSS:
  `sha256sum -c` OK for the pack, run.sh and the held-out pack; sbatch sha256 equal to the f748da4 pins.
- 12 Nov 23:46:29 and 23:48:05: `sbatch ms1_smoke.sbatch` refused twice ("Unable to contact slurm controller (connect
  failure)"); per the lead's rule no further retry; lead told. Nothing submitted.
- 12 Nov ~23:50: lead: do not retry; the lead pings the controller every 5 min. If WCSS does not accept jobs by 13 Nov
  01:00, MS1 switches to rented A100s: deviation MS1-D1 prepared and registered at 5eadc1b (three A100 PCIe 40 GB
  machines, whole seeds: m1 403+406, m2 404+407, m3 405; held-out step per machine; `src/MS1/rented/drive_ms1.sh`,
  `remote_ms1.sh`; remote queue tested on the DGX with stand-in tasks in `/mnt/t7/smad_next/MS1/smoke/rtest`).
- 13 Nov 00:00: lead: WCSS will not start the jobs tonight (priority); smoke job 6308826 cancelled by the lead; three
  L40S 48 GB leases rented (ms1m1, ms1m2, ms1m3). TT1-S registered (01557ce, pins ccd6319): its references added to
  the held-out step; held-out pack rebuilt (`396a7ebe…`, 7,141 rows; first version kept as
  `ms1_heldout_pack_v1.tar`). Deviation MS1-D2 registered at 86b4b69 (00:03:29). Reader prints the TT1 reference reads
  (e69e063).
- 13 Nov 00:02: `drive_ms1.sh ... setup` started for the three leases in parallel from this session (uploads allowed);
  `after_setup.sh m1|m2|m3` waits for each setup and then starts the queue and the pull loop.
- 13 Nov 00:05: upload to ms1m1 (61.206.39.5:21267) stalled (about 10 KB/s); lead told; the lead released and
  destroyed ms1m1 (0.06 USD) and rented the replacement ms1m1b (L40S, 147.124.211.53:9630, lease folder
  `/mnt/t7/smad_next/vast/ms1m1b`, cap 10 USD, 13 h), which takes queue m1 (seeds 403+406) as registered. The setup
  and after_setup processes for the old host were stopped (no fit had started there). 00:09: setup started on ms1m1b
  (about 16 MB/s); `after_setup.sh` now takes the lease folder as an optional second argument.
- 13 Nov 00:32:07 SETUP_OK ms1m1b (upload 1,282 s; GPU-c1ff3444…), queue m1 and loop 00:32:39; first fit 1.23-1.27 it/s.
- 13 Nov 00:54:58 SETUP_OK ms1m3 (upload 3,028 s; GPU-b1d985cf…), queue m3 and loop 00:55:34; first fit 1.15 it/s.
- 13 Nov 00:55:20 SETUP_OK ms1m2 (upload 3,049 s; GPU-214a6ac4…), queue m2 and loop 00:56:04; first fit 1.18 it/s.
  ms1m2 and ms1m3 are two GPUs of one host (118.163.199.123). Expected ends (fits about 1.55-1.7 h each, then the
  held-out step): m3 about 06:10, m1b about 09:50, m2 about 11:00 on 13 Nov.
- 13 Nov 05:50: ms1m3 queue ENDED (fits rc 0 at 01:25, 02:51, 04:16; held-out tar written). From 05:52 every pull
  verified the 3 fit tars and the held-out tar but its keep step failed with "log copy differs from the remote", so no
  RELEASE and no second copies; the lease idled toward its 6 USD cap (lead's report, 4.998 USD at 06:07).
  BUG (found 06:08): the files were byte-identical; the two sha256 listings differed only in ORDER, because the remote
  sorted with `sort -k2` in the C locale and the DGX in en_US (case-insensitive: `MS1_SbM3` before `MS1_Sb_` in C,
  after it in en_US). FIX (`drive_ms1.sh`): both listings sorted with `LC_ALL=C sort -k2`; the remote listing, taken
  once after ENDED, now also covers every rc file and the queue log, besides every file in logs/ (task, held-out,
  setup, pip, version, GPU and queue-driver logs: all final once the queue has ended); the remote end-marker is checked
  before re-sorting. Nothing was skipped.
- 13 Nov 06:09: the three loops were stopped while sleeping (no pull in progress; a running bash loop must not keep
  reading a script file rewritten in place) and the corrected pull was run by hand on ms1m3: 3 of 3 fits verified,
  held-out tar and 13 log files verified, second copies of all four tars verified in `/home/narolski/ms1_results_copy`,
  RELEASE written 06:09:49. Loops for ms1m1b and ms1m2 restarted at 06:10 on the corrected script (each round calls the
  script by path, `bash "$0" ... pull`, so later edits are picked up by the next round).
- 13 Nov 06:53 (lead's decision, keeps the contrast 2-prime option open, registers and scores nothing):
  `drive_ms1.sh` pull step checks `$L/HOLD` immediately before each RELEASE (after the keep step, so second copies are
  still made): "HOLD present: RELEASE deferred". Tested with a local mock of the remote (the stand-in queue in
  `/mnt/t7/smad_next/MS1/smoke/rtest`): HOLD present -> keep done, no RELEASE, both in the full and the partial
  (FAILED) branch; HOLD absent -> RELEASE (+ FAILED) as before. drive_ms1.sh sha256 `6cfd40dd…`. Loops for ms1m1b and
  ms1m2 stopped while sleeping and restarted 06:54. The lead creates `/mnt/t7/smad_next/vast/ms1m1b/HOLD`; without the
  author's decision by 11:30 the lead removes it. ms1_read.py is not run before contrast 2-prime is registered or
  declined (lead ruling).
- 13 Nov 07:03: the author approved contrast 2-prime; registered as C2P in the PN1 prereg (2715e48); FINAL section 1
  amended (6691adc). 07:04: `src/MS1/c2p/drive_c2p.sh upload` (15 FS1 tars verified on ms1m1b) and `start` (the
  remote run waits on the host lock until the MS1 queue and its held-out step end); a background loop pulls every 5 min
  until "C2P kept (45 of 45"; HOLD stays until then. While C2P runs, the MS1 keep step on ms1m1b may report "log copy
  differs" (the C2P logs in logs/ still grow); it passes once C2P ends. The hold on ms1_read.py is lifted (C2P
  registered); the MS1 read runs once all 15 fits and the three held-out tars are in.
- 13 Nov 09:10: author: "Use CeleA-HQ as a source, it is valid" (candidate fourth source; after today's two readings;
  nothing trained without a registered amendment and a pre-run check). 09:07: `src/MS1/celebahq_prep.py align` started
  in two processes (indices 0-15000, 15000-30000; frames streamed from the zip, no unpacked copy of the 37 GB archive;
  zip sha256 `bda2d6f0…` checked; unchanged 73_delin_align; glintr100 embeddings). Rate about 2.7 images/s per process;
  expected end about 10:45. Test on 8 images: 4 aligned, 4 failed the frontal filter. `celebahq_persons.py` written
  (CASIA-WebFace embeddings from its packed 112 px crops, used only to exclude persons; threshold error on labelled
  CelebA; references FFHQ, CFD, KDEF, TT1, FRGC / colorFERET; connected-component persons at cos >= 0.40; overlapping
  persons dropped); not run yet.

## 3. Data

- FFHQ-1024 raw: `/mnt/t7/Datasety/downloads/FFHQ-1024/Part{1..7}/<key>.png` (70,000).
- Exclusion lists: FFHQ-Morphs `/mnt/t7/Datasety/downloads/FFHQ_Morphs/_docs/FFHQ-Morphs/{pairs,bonafide_only}.csv`;
  ffhqm `/mnt/t7/smad_heldout/ffhq_morphs/{manifests/ffhqm_meta.csv,protocol/*.txt}`.
- Outputs under `/mnt/t7/smad_next/MS1/ffhq/`: `src/<key>.png|.tem` (900 aligned frames + 106-point landmarks),
  `select_log.csv` (every attempted key, outcome, cosines, raw and frame sha256), `persons.csv`, `emb_ref.npz`,
  `emb_kept.npz`, `excluded_raw_sha256.csv`, `lists/{af0_pairs,halves,soft,ladder}.csv`, `img/{train,hold}/{zero,u50,
  halfA,halfB}/`, `img/ladder/opencv/{R4,half,R2w4}/`, `img/soft/{fm61,amsl112}/`, `soft_log.csv`.
  Manifest `/mnt/t7/smad_next/MS1/manifests/train_SbM3.csv` and `SbM3_files.csv` (pack path, source, sha256 of every
  FFHQ training image). Gate scratch `/mnt/t7/smad_next/MS1/gate/`.

FFHQ training images in SbM3 (unique): af0_photo 450, af0_photo61 216, af0_zero 400, af0_half 800, af0_half61 198,
af0_u50 400, af0_u5061 199, lad_R0 150, lad_R4 150, lad_half 300; total 3,263 (target 3,275; 12 stored copies failed
re-alignment). Not supplied by FFHQ: lad_R2w, lad_S0, lad_S3, lad_S4 (prereg 3.3). Hold-out (MS1 FFHQ, 300 persons):
photo 300, photo fm61 291, photo amsl112 290, u50 150 (+ fm61 150, amsl112 149), zero 150.

## 4. Code

`src/MS1/` (run order): `ms1common.py` (paths, exclusion keys); `ffhq_select.py refs|select` (via `run_select.sh`);
`excl_sha.py`; `gate.py path`; `proof.py`; `ffhq_build.py plan|morph|soft` (via `run_build.sh`, which ends with
`gate.py pixel`); `mkmanifest.py`; `build_pack.py`; `run.sh` (copy of `src/PN1/run.sh`, arm list Sb|SbM3, results
folder MS1); `wcss/ms1_smoke.sbatch`, `wcss/ms1_fit.sbatch` (drafts, not submitted). Python
`/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, thread caps 2, nice 10, 2 workers. Unchanged code used,
with sha256 in `gate_path.json`: 73_delin_align (47eefed3…), 78_tool_morph, 68_hires_morph, prep_eval (374408ab…),
AF0 af_morph / soften / ghost, AR1 variants / fr, PN1 mkmanifests.

## 5. Results

none yet.

## 6. Checks

Path gate 20/20 pixel-identical (`gate_path.json`); pixel gate 24/24 (`gate_pixel.json`); exclusion proof passes
(`exclusion_proof.json`); FRGC / colorFERET rows of SbM3 equal train_Sb (asserted in `mkmanifest.py`); 8-image smoke of
every stage run before the full run. Not verified: re-alignment of an FRGC raw photo through 73_delin_align against its
recorded frame (the aligner's sha256 equals AR1's pin); duplicates of persons below glintr100 cosine 0.40.

## 7. Dead ends and failures

- Multi-PIE as held: 128 px crops, unusable (prereg section 0).
- FLUXSynID: ruled out by the author (23:05), not built.

## 8. Observations and ideas

- New candidate sources (inventory 12 Nov, before 23:22; eye distances measured with the unchanged detector on 2-8 images
  each, nothing built):
  - Chicago Face Database 3.0.1: 827 persons (CFD 597, CFD-INDIA 142, CFD-MR 88), exactly one neutral frontal photo
    each, 2444 x 1718 JPEG, eye distance 329-381 px (all 10 test images aligned); 154 CFD persons also have angry,
    fear, happy-closed and happy-open photos from the same session (CFD-INDIA 5 extra files). Same-person controls
    possible for about 154 hosts with the happy-closed photo as the second photo (the FRLL neutral + smiling
    precedent of AR1's secondary pool). Meets the resolution and count rules.
  - KDEF: 70 persons x 2 sessions (A, B), 35 photos each (7 expressions x 5 angles); neutral straight NES at
    562 x 762, eye distance about 150-153 px; two-session same-person controls for all 70, but 70 persons is below
    the minimum of 400. AKDEF holds 70 averaged faces (composites): not genuine photos, never usable as genuine.
  - MUCT: 276 persons, 5 cameras, 480 x 640 JPEG; camera a (frontal) 751 images (about 2.7 per person, lighting
    variants q-z of one session); eye distance 87-93 px (below 112.7, so frames are enlarged about 1.45x); below 400
    persons; licence forbids reproduction in public documents.
  - CelebA-HQ: downloading (11.0 of 33.9 GB at 23:18); the HQ-to-CelebA mapping file is not on disk
    (`CelebAMask-HQ/` empty). Note: CelebA-HQ images were made with JPEG-artefact removal and 4x super-resolution
    networks (Karras et al. 2018), i.e. network-processed texture.

- FFHQ contains many second photos of development persons: 103 of 1,012 face-passing candidates had glintr100 cosine
  0.40 or more (median 0.565, up to 0.92) to an ffhqm genuine image or contributor. Any experiment that trains on FFHQ
  and reads ffhqm should check identity, not only keys.
- FFHQ photos are in-the-wild (sunglasses, open-mouth smiles, hands on the face); the aligner filters pose only. FRGC /
  colorFERET training photos are neutral frontal. FFHQ frames often carry a black border at the bottom of the 512 frame
  (tight 1024 crops), in both classes.

- FLUXSynID's live images: `live_0_a` 512 px with strong expression and tight crop (frontal filter failed in the one
  test), `live_0_e` near-copy of the document image, `live_0_p` a different scene; recorded only for the record.

## 9. Open items and next steps

- Lead's pre-run review of `prereg_comparison_draft.md`; apply fixes; copy the final text into `prereg.md` part 2 and
  commit before any fit is submitted.
- Lead runs the upload, smoke and array commands (draft section 9); fetch tars; run `ms1_read.py`; post-result review.
- A fourth-source arm only after the lead confirms a source (section 8).

## 10. Handover state

13 Nov 00:10: three rented L40S 48 GB leases (lease folders `/mnt/t7/smad_next/vast/ms1m1b|ms1m2|ms1m3`, READY line in
`rent.out`, caps 10 / 10 / 6 USD set by the lead; ms1m1 replaced by ms1m1b). Per lease: setup upload running (`ms1_setup_run.out`), then
`after_setup.sh` (log `after_setup.out`) starts the queue (m1 seeds 403+406, m2 404+407, m3 405; each queue ends with
the held-out step) and the pull loop (`ms1_loop.out`, `ms1_drive.log`; RELEASE in the lease folder when every tar,
the held-out tar and the logs are fetched and verified). Results: `/mnt/t7/smad_next/MS1/results_rented/`, second
copies `/home/narolski/ms1_results_copy/`. If a setup fails: rerun `drive_ms1.sh HOST PORT LEASE Q setup` (rsync
resumes), then `after_setup.sh Q`. WCSS: staged packs remain under packs/MS1, unused for MS1 (MS1-D2).

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; cd /home/narolski/smad-next/src/MS1
./run_select.sh; $P -I excl_sha.py; $P -I gate.py path; $P -I proof.py
$P -I ffhq_build.py plan; ./run_build.sh; $P -I mkmanifest.py; $P -I build_pack.py
# smoke: see /mnt/t7/smad_next/MS1/smoke/smoke_dgx.log for the env line; fits: src/MS1/wcss/*.sbatch
$P -I ms1_read.py --results /mnt/t7/smad_next/MS1/results --out ../../experiments/MS1_multi-source-training-set/ms1_read.json
```
