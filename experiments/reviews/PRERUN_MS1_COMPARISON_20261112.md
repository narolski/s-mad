# Pre-run review: MS1 training comparison (multi-source)

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** The plan has no design blocker. Two procedural blockers must be cleared before submission. As drafted, the experiment cannot answer the author's question, which is whether the threshold carries over to sharp unseen genuine photos. It can only answer it for low-resolution frames with black borders. Fix B3 below closes that gap without delaying the fits.

**What I checked and found correct:**
- `src/MS1/run.sh`: sha256 `fcc9a646…` equals the `wcss_stage` copy. The diff against PN1 is exactly the three stated changes.
- The pack tar sha256 equals `dac228f5…` (14,508,625,920 bytes).
- Exclusion proof: zero overlaps by key and by sha256. Largest cosines: 0.396 to the ffhqm references, 0.391 among kept frames, 0.374 hold-out vs training.
- The FRGC / colorFERET rows of SbM3 equal Sb's rows.
- Both sbatch files carry `--extra=FORCE_RM_TMPDIR` and keep all IO in `$TMPDIR`. Peak use is about 29 GB of the 80 GB requested.

## Blockers

**B1. Not registered yet.** The draft says it governs nothing until it is copied into `prereg.md` part 2, and that has not happened at cb1cf09. Fix: commit part 2 (with the fixes below) and pin the sha256s of `ms1_fit.sbatch` and `ms1_smoke.sbatch`, then upload.

**B2. The reader is missing.** `src/MS1/ms1_read.py` does not exist (ls fails). §8 requires it committed and tested on mock scores before any tar is pulled. Submission may go ahead; the fetch (command 4) is gated on the reader commit.

**B3. P1 cannot identify threshold transfer to sharp sources.**
- All seven TT1 families are 1.7–3.5x enlargements with a black border over 40–53% of the frame (PRERUN_TT1 M4/M5).
- SbM3 adds FFHQ frames with black bottom strips in both classes (README §8). So a P1 "support" can come from the network learning that a border means nothing, not from source diversity.
- A P1 "falsified" would not show a failure on sharp photos.
- The falsified sentence "does not make the own-rule threshold transfer to unseen sources" therefore overclaims.

Fixes:
- (a) Add **P1-S (co-primary): a sharp unseen source, the Chicago Face Database.** It is already on disk (`/mnt/t7/Datasety/downloads/ChicagoFaceDatabase/cfd/CFD Version 3.0.1`, 1,872 files, about 2444x1718 studio JPEGs). It meets the ≥132 px rule, is mostly neutral frontal, and is not in any benchmark or development set (no mention anywhere in the repo).
  - Align the neutral (`-N`) images tonight with the unchanged aligner (`73_delin_align`). Fix the pool, its sha256 and the person count before any MS1 score exists.
  - Score it after the fits from the kept `last_trainable.pt` with the unchanged `pn1_score.py`, in one separate WCSS job. Submit that job only once its pack is complete (no-placeholder rule).
  - Use the same statistic, ratio, Mann-Whitney test and floor rule as P1. Multiplicity: each co-primary at p ≤ 0.025 (5 against 5: U ≤ 2, p = 4/252).
  - Disclose: studio capture like FRGC; the frame is shrunk about 3x.
  - Cost of the choice: CFD then cannot become the fourth training source.
- (b) KDEF neutral-straight images (70 persons x 2 sessions) as a printed secondary.
- (c) Not recommended:
  - CelebA-HQ: GAN super-resolved, and its celebrity identities may overlap the CASIA-WebFace closure.
  - MUCT: 640x480, so its frames are enlarged.
- (d) Relabel the TT1 read "P1-T: unseen low-resolution sources with black borders". Score TT1's border-blanked camera photos (R_cam^border, TT1 M3) for both arms in the same later job. Print P1-T and P2 against them.

## Majors

**M1. G1 cannot catch a cost.** landmark_combined on ffhqm is now trained-source for SbM3, using a landmark morph close to the OpenCV engine. That biases the guard towards a pass. Add: "G1 is in-source for SbM3 and biased in its favour. A pass shows no cost on an unseen pipeline. No improvement may be claimed." No unseen-source attack read is left in development; say so in §7.

**M2. Confounds are not closed by per-stratum balancing.** The share of spliced images (lad_S4) among attack rows falls from about 10% to about 6%. Each FRGC / colorFERET row is seen 0.63x as often. FFHQ adds casual content and borders.
- Text: "The effect, if any, belongs to the three-source protocol (photos, morphs, controls, more rows, a smaller splice share). Nothing is attributed to source diversity alone." This matches the author's 1 Nov framing ruling.
- Print the splice share of attack rows per arm.
- Optional control (WCSS is free, needs registration now): a data-volume arm, Sb oversampled to 13,414 rows, seeds 403–407. Five more fits, about 4–5 H100-hours.

**M3. The fallback fork is open.** Replace it with:
- "Started" means all ten tasks are RUNNING or COMPLETED by 13 Nov 12:00 CET.
- Otherwise the A100 fallback runs, the WCSS array is cancelled, and WCSS fits are never read for MS1.
- The two platforms' fits are never mixed.

**M4. A printed reference does not exist.** "FS1 A100 Sb own-rule TT1 F" requires TT1 scores of FS1 networks, which nobody has. Either drop it or name the source.
- Replace with a smoke gate: compare the WCSS Sb s403 20-step losses and sample-order hash with FS1's Sb s403 `train.log`. Print the result; it decides nothing.
- Replace "training and scoring commands unchanged" with "unchanged code and flags, different software (torch 2.11 vs 2.2.1)".

**M5. Power.** 5 against 5 needs near-complete separation (U ≤ 4, p = 12/252 = 0.048). The seed spread seen so far is wide (FFHQ flags 3.5–22.5%; B 17.8 vs 6.4%). Add the sentence "the test detects only near-complete separation; 'inconclusive' is the likely result for effects below about 1.5 seed-SD".

## Minors

- `exclusion_proof.json`: `refs_found` 3999 of 4000. Name the missing reference and state that it is excluded by key.
- Pseudo-identity bootstrap: apply TT1's M2 inflation factors (or label it). Print F without MSU-MFSD (65 images).
- `ms1_fit.sbatch`: the "PN1 env" line goes only to the Lustre log. Also write the versions into `$R`, so each tar records torch and timm.
- The keep rule: a second local copy of each result tar before release. Do not write the smoke's `rm -rf` style into the result paths.

## Claims

**May be claimed:**
- Own-rule genuine flag shares on development sources, for the three-source protocol, at n = 5 seeds.
- Separate sentences for the sharp source (CFD) and the bordered low-resolution source (TT1).

**Must not be claimed:**
- Anything on benchmarks; "source-invariant".
- That FFHQ is unseen for SbM3.
- A cause (source vs volume vs border vs splice share).
- "Threshold transfers to unseen sources" in general from TT1 alone.

## Questions for the author

1. Is CFD acceptable as a held-out evaluation source, which rules it out as a training source?
2. Is the data-volume control arm wanted?

Files: `/home/narolski/smad-next/experiments/MS1_multi-source-training-set/prereg_comparison_draft.md`, `/home/narolski/smad-next/src/MS1/wcss/ms1_fit.sbatch`, `/home/narolski/smad-next/experiments/MS1_multi-source-training-set/exclusion_proof.json`.
