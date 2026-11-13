# Shortcut audit table (SA1)

## 1. Question and current answer

The author asked for scientific evidence that the training protocol is shortcut-free: one row per known shortcut,
one column per training arm or released detector, every cell from a paired control (the same images with and without
the suspected cue), with seeds, intervals, source file and review status. Status 13 Nov 2026, about 09:45 CET:
version 1 compiled from registered results only (no scoring). Of 144 cells, 66 are reviewed (20 of them on two seeds
only), 12 unreviewed, 59 empty, 7 not applicable. For our own arms, 49 of 80 cells are empty. The best-measured row
(storage history of genuine photos, five fresh seeds) supports "reduced, not removed", not "removed". The table is
`result.md`; the cell list is `cells.csv`. Waiting for today's readings (Sp ablation, SbM3 three-source training,
contrast 2-prime storage test) to fill 8 pending cells.

## 2. Timeline

- 13 Nov 08:28: started. Read `OWNER_BRIEF.md`, `NOTEBOOK.md` (12-13 Nov), `08_CUE_MATRIX.md`, then the sources named
  in the task: PN1 (`result.md`, `BENCHMARK_EXPOSURE.md`, `tier1/*.json`, `tier_fs/fs.json`, `tier1_sb/`), TT1
  (`result.md`), MS1 (`README.md`), CB1 (`result.md`, `cb1_released_rs1_bpcer.csv`), SM1, AR1, AD4, AG1, EV1, RS1 and
  the review files in `experiments/reviews/`.
- 13 Nov 09:30: `result.md` version 1 written; `src/SA1/cells.py` writes `cells.csv` and the status counts.
- 13 Nov 09:45: sent to the results-reviewer agent (Opus) for a cell-by-cell check.

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
- Independent check by the results-reviewer agent: pending at the time of writing (section 9).
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

- Apply the results-reviewer's corrections; commit and push.
- Update the table when the lead reports today's readings (Sp, SbM3 and SbV, C2P with H-new-1).
- The ranked list of fill experiments goes to the lead; none is run by this owner.

## 10. Handover state

No process running, nothing queued, no compute used (0 GPU-hours, 0 USD).

## 11. Reproduce from scratch

```
python3 src/SA1/cells.py experiments/SA1_shortcut-audit-table/cells.csv
```
The table itself is a hand compilation; every cell names its source file and line.
