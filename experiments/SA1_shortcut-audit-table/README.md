# Shortcut audit table (SA1)

## 1. Question and current answer

The author asked for scientific evidence that the training protocol is shortcut-free: one row per known shortcut,
one column per training arm or released detector, every cell from a paired control (the same images with and without
the suspected cue), with seeds, intervals, source file and review status. Status 13 Nov 2026, about 09:45 CET:
version 2 (reviewed) compiled from registered results only (no scoring). After the PR1 part-1, C2P and MS1 readings (13 Nov about 10:00), of 180 cells (20 rows x 9 columns) 122 are reviewed
(2 of them on two seeds only), 16 unreviewed, 27 empty, 15 not applicable (about 15:00, after AB1; unchanged at 17:45: SE1 and BB2 sit in separate arm tables). For our own arms, 42 of 100 cells are empty. The best-measured row
(storage history of genuine photos, five fresh seeds) supports "reduced, not removed", not "removed". The table is
`result.md`; the cell list is `cells.csv`. Waiting for today's readings (Sp ablation, SbM3 three-source training,
contrast 2-prime storage test, TT1-FS fresh-seed block) to fill the pending cells.

## 2. Timeline

- 13 Nov 08:28: started. Read `OWNER_BRIEF.md`, `NOTEBOOK.md` (12-13 Nov), `08_CUE_MATRIX.md`, then the sources named
  in the task: PN1 (`result.md`, `BENCHMARK_EXPOSURE.md`, `tier1/*.json`, `tier_fs/fs.json`, `tier1_sb/`), TT1
  (`result.md`), MS1 (`README.md`), CB1 (`result.md`, `cb1_released_rs1_bpcer.csv`), SM1, AR1, AD4, AG1, EV1, RS1 and
  the review files in `experiments/reviews/`.
- 13 Nov (stamps below corrected to the machine clock; earlier drafts said 09:30 to 10:10 by estimate) 08:40: `result.md` version 1 committed (e96bf68); `src/SA1/cells.py` writes `cells.csv` and the status counts.
- 13 Nov 08:40: sent to the results-reviewer agent (Opus) for a cell-by-cell check.
- 13 Nov 08:4x: review returned "needs corrections" (20 items; all numbers matched except unverifiable tier1 JSON
  values, which the reviewer did not open because those files also hold benchmark rows). Applied all 20: row 2
  headlines changed from "not used" to "not evaluable / in training"; near-trained-size qualifier on 1-B and 1-Sb;
  TT1-FS (registered, queued) added as pending; border headlines "inconclusive"; released warp-only cells "small" where
  the interval excludes 0.5; FaceMorpher splice reads dropped; 10-SelfMAD set to not measured; 4-Sp set to not measured;
  12-released in reviewed wording; fresh-seed R6 values added; citations fixed (9-Sb, amendment 9 lines, AD1 lines);
  new rows 17 (softness), 18 (processing cue in the development set's surround), 19 (operating point); claim and
  cannot-claim sections extended; ranked list fixed (C2P on L40S; JPEG pack is an author item; TT1-FS already queued).
  Version 2 committed 08:48:58 (347e8be).
- 08:50: lead's instruction: save the review verbatim (`experiments/reviews/REVIEW_SA1_20261113.md`); do gap items 9 and 11; registered G9 and G11 in `prereg.md` (3a0065e) before computing.
- 08:52-08:56: G9 (`src/SA1/g9_partners.py` -> `g9_partners.json`): "partner structure present" by the registered 1% rule (largest share 1.6-3.1%, AF0 FRGC persons in up to 25 morphs); far weaker than SMDD's 5 partners. G11 (`src/SA1/g11_expression_pool.py` -> `g11_expression_pool.json`): "a paired expression pool exists" (CFD 158, KDEF 70 persons). Note: the G11 code also accepts a combined count of 100; CFD alone meets the registered rule, so the reading is the same.

- 09:40-09:50: lead's message: PR1 part 1 (`experiments/PR1_protocol-reads-existing-networks/result.md`, review
  REVIEW_PR1_PART1_20261113) and C2P (`PN1/c2p_result.md`, review REVIEW_PN1_C2P_20261113) entered from the files and
  reviews: rows 6-9 go to five seeds, row 19 gets the τ5 read, new row 20 (engine, ceiling read), rows 1 and 2 get the
  C2P wording (Sb evasion falsified on 4 of 4 read seeds; A and B not read; C2P-R pending). Also the SM1 A14/A23 partner
  trace (row 15, 15b).
- about 10:00: MS1 read and reviewed (result 31ea7a4, REVIEW_MS1_20261113): SbM3 column and SbV control filled from
  the files, with the review's F1 cost (landmark_combined own-rule miss 0.271 -> 0.585, AUC unchanged) beside the CFD
  result and the review's cannot-claim lines.
- about 10:15: CB1 released-detector gap cells (result section "SA1 gap item 10", review REVIEW_CB1_SA1CELLS_20261113,
  814c279) copied as given; the review's border caveat added to the table notes.
- about 10:35: Sp ablation (PN1 result Sp section, ee61116; REVIEW_PN1_SP) entered as registered verdict plus printed
  reads; released-detector storage cells relabelled "aligned-frame history (our aligner + history)" with the aligned-only
  step beside them (CB1 "Black frame vs storage history", REVIEW_CB1_BORDER_HISTORY); MS1 parts 3/3b (REVIEW_MS1_PART3).
- about 12:00: TT1-FS block, Z1-Z4 and TT1-X parts 1-2 (TT1 result b16dba4; REVIEW_TT1_FS and the Z review, cdb79b4)
  entered with the review's may-say / may-not-say wording (rows 4, 5, 10, 17 to seven seeds; Sb border finding; B's FFHQ
  rate; Sp and SbM3 printed cells). PR1 part 2 (GD0-GD2, 5a10e33) entered as unreviewed in rows 13 and 14.
- about 12:30: PR1 part 2 review applied (d6cf22c, REVIEW_PR1_PART2): rows 13 and 14 reviewed with the review's wording;
  Z2b-τ5 in row 19; row 15b now the five-seed cell 0.723 ± 0.032 (8f044b2, REVIEW_SM1_VITL_5SEED). Note: commit 5fea9bf
  had captured only part of the 12:00 update because another owner's stash held my unstaged edits during a pull; the
  full version is committed now.
- about 15:00: AB1 (a423637, REVIEW_AB1) entered: second seed block on H100 in rows 1, 2, 6, 8, 9, 18 (B's evasion cell
  filled on that block; Sp printed cells), and a separate leave-one-component-out table (SbZ, SbH, SbS, AS, Sp) with the
  review's mechanism wording and cannot-claim lines.
- about 17:45: SE1 A100 block (f302cfa, 4d21dde; REVIEW_SE1_A100) and BB2 part 1 (6dcbdf9; REVIEW_BB2_PART1) added as
  separate arm tables with the reviews' wording; SE1 H100 block and BB2 E2/E3 marked pending; matrix counts unchanged.
- about 18:30: NIST MEDS block (TT1-M and S1/S2; corrections c4c2233, bf774cb) added to row 4 with the review's may-say
  sentence; aggregates only, no MEDS image, file name or person identifier; matrix counts unchanged.

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
