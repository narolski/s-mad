# Pre-run check of the standing adversary's shortcut floors (ADV, 4a0abb0), owner-launched

Experiment-reviewer (Opus), launched by the ADV owner at about 19:12 CET on 13 Nov 2026, returned about 19:19. Condensed
by the owner from the reviewer's hand-back (full wording of the findings kept; diagnostics it ran: manifests and file
listings only, no floor, no feature cache, no arm score). Applied in amendment 1 (032e8ae).

**Verdict: GO WITH FIXES.** Pins match; no closed set touched; the feature code only measures.

- **F1 (blocker).** Ladder contrasts lack `strength = ""`: `ab1x_eval.csv` holds native and stored (61, 112) copies;
  `ab1fm_read.py:72-74` reads natives (191 test / 100 development per rung). `test_fm_R4_vs_R2w` was 191 native R4
  against 573 R2w of which two thirds stored: storage cues would inflate the floor. Fix: native filter, corrected counts.
- **F2 (blocker for gd2_*).** GD2 partners taken from the ladder table; true contributors are `pa`/`pb` in
  `AG1/data/manifests/ag1.csv`; 64 of 74 R4 rows wrong or missing; 57 true components against 101 built. Fix: AG1
  manifest persons. GD1 partners match (0 mismatches).
- **F3 (major).** "Exceeds" is meaningless where both sides are genuine (border, storage); these floors approach 1 by
  construction (`edge_black_frac` measures the mask; bordered copies are written with another zlib header, so PNG size
  records the writing script). Fix: label as separability ceilings; print a pixel-only floor without file-size values.
- **F4 (major).** `train_lad_*` cannot be compared with E3's in-sample splice-fit gate; bind only for E2's probe; print
  an in-sample gbt AUC as context.
- **F5 (major).** Stage-2 floors for Sb come after Sb's read; label them, with the features designed knowing Sb's value.
- **F6 (minor).** `%.6g` rounding of held-out scores can lower the floor in `check.py`; write full precision and assert
  the floor reproduces.
- **F7 (minor).** `check.py`: reject non-finite scores, record which floor files were read.
- **F8 (minor).** DCT comb blocks offset by one pixel from the blockiness grid; weakens the floor; a limitation.
- **F9 (minor).** A fold with all-constant columns crashes; guard and return 0.5.
- **F10 (minor).** Link the partner for R2w4 rows; `af0_dev_u50_vs_photo` has 26 components (context only); E3
  deadline is 15 Nov 18:00; GX1 secondary uses R2 on s1 only; GX1's "against GD2 R2" transfer read is not covered.
- Passed: stored copies with their natives, border copies with their originals, landmark_combined contributor and
  genuine ids disjoint, no row falls back to its own id; floor definition and paired bootstrap sound; no image operation.
