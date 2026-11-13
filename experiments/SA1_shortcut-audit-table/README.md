# Shortcut audit table (SA1)

## 1. Question and current answer

The author asked for scientific evidence that the training protocol is shortcut-free: one row per known shortcut,
one column per training arm or released detector, every cell from a paired control (the same images with and without
the suspected cue), with seeds, intervals, source file and review status. Status 13 Nov 2026, about 09:45 CET:
version 2 (reviewed) compiled from registered results only (no scoring). Of 171 cells (19 rows x 9 columns), 79 are
reviewed (22 of them on two seeds only), 13 unreviewed, 68 empty, 11 not applicable. For our own arms, 56 of 95 cells
are empty. The best-measured row
(storage history of genuine photos, five fresh seeds) supports "reduced, not removed", not "removed". The table is
`result.md`; the cell list is `cells.csv`. Waiting for today's readings (Sp ablation, SbM3 three-source training,
contrast 2-prime storage test, TT1-FS fresh-seed block) to fill the pending cells.

## 2. Timeline

- 13 Nov 08:28: started. Read `OWNER_BRIEF.md`, `NOTEBOOK.md` (12-13 Nov), `08_CUE_MATRIX.md`, then the sources named
  in the task: PN1 (`result.md`, `BENCHMARK_EXPOSURE.md`, `tier1/*.json`, `tier_fs/fs.json`, `tier1_sb/`), TT1
  (`result.md`), MS1 (`README.md`), CB1 (`result.md`, `cb1_released_rs1_bpcer.csv`), SM1, AR1, AD4, AG1, EV1, RS1 and
  the review files in `experiments/reviews/`.
- 13 Nov 09:30: `result.md` version 1 written; `src/SA1/cells.py` writes `cells.csv` and the status counts.
- 13 Nov 09:45: version 1 committed (e96bf68) and sent to the results-reviewer agent (Opus) for a cell-by-cell check.
- 13 Nov about 10:00: review returned "needs corrections" (20 items; all numbers matched except unverifiable tier1 JSON
  values, which the reviewer did not open because those files also hold benchmark rows). Applied all 20: row 2
  headlines changed from "not used" to "not evaluable / in training"; near-trained-size qualifier on 1-B and 1-Sb;
  TT1-FS (registered, queued) added as pending; border headlines "inconclusive"; released warp-only cells "small" where
  the interval excludes 0.5; FaceMorpher splice reads dropped; 10-SelfMAD set to not measured; 4-Sp set to not measured;
  12-released in reviewed wording; fresh-seed R6 values added; citations fixed (9-Sb, amendment 9 lines, AD1 lines);
  new rows 17 (softness), 18 (processing cue in the development set's surround), 19 (operating point); claim and
  cannot-claim sections extended; ranked list fixed (C2P on L40S; JPEG pack is an author item; TT1-FS already queued).
  Version 2.

## 3. Data

No image, score file of a benchmark read, or manifest of a sealed set was opened. Opened read-only: result and review
files listed above; the PN1 tier-1 per-network JSON files (`fixed.own` placement and miss rates on the test ladder,
`h_R4_vs_R3`), `tier_fs/fs.json` (registered reader output), `tier1_sb/sp_read_test.json` (test-mode output of the Sp
reader, not an Sp result; not used as evidence), and the metadata columns of `/mnt/t7/smad_next/PN1/manifests/pn1_eval.csv`
(row counts by role and rung, to check which development rungs exist in the evaluation list; no score).

## 4. Code

`src/SA1/cells.py <out.csv>`: the status of every cell (16 rows x 9 columns) as typed from `result.md`, written to
`cells.csv`, plus the counts. Plain Python 3, no dependencies.

## 5. Results

See `result.md` (matrix, cell register with file:line and review file per cell, counts, supported claims in the
reviewers' wording, what cannot be claimed, ranked list of experiments to fill the empty cells).

## 6. Checks

- Every line reference was taken from the files at git `aead489` (working tree of 13 Nov about 09:00).
- Independent check by the results-reviewer agent (Opus), 13 Nov: needs corrections; all applied (section 2). The
  per-seed tier1 JSON values (2-A, 6-A placement, 7-A, 7-B) were not verified by the reviewer and stay labelled unreviewed.
- Not verified: CB1's results review (applied per CB1 README line 118, but no review file is in `experiments/reviews/`);
  the earlier-programme numbers taken from `08_CUE_MATRIX.md` (A36, A41) were not re-opened in their primary files.

## 7. Dead ends and failures

- `tier1_sb/sp_read_test.json` looks like an Sp result but is the reader's test mode (Bv standing in for Sp,
  `PN1/prereg.md:778`); excluded.
- Benchmark-exposure numbers of PN1 networks (FRLL JPEG pools, H1, MAD22, FRLL neutral-only) were deliberately left out;
  those cells say "not measured (exposure only)".

## 8. Observations and ideas

- Rows 6 to 9 (warp-only, same-person morph, same-person splice, seam) can get five seeds instead of two without any
  GPU: the R2w, R3, R3m, S0 and S4 rows are in the FS1 evaluation list, so a registered zero-GPU read of the existing
  FS1 score files fills them (rank 2 of the empty-cell list).
- No development JPEG pool exists for our arms; the JPEG row cannot be filled without the author's approval to run the
  registered JPEG branch on evaluation images.

## 9. Open items and next steps

- Update the table when the lead reports today's readings (Sp, SbM3 and SbV, C2P with H-new-1).
- The ranked list of fill experiments goes to the lead; none is run by this owner.

## 10. Handover state

No process running, nothing queued, no compute used (0 GPU-hours, 0 USD).

## 11. Reproduce from scratch

```
python3 src/SA1/cells.py experiments/SA1_shortcut-audit-table/cells.csv
```
The table itself is a hand compilation; every cell names its source file and line.
