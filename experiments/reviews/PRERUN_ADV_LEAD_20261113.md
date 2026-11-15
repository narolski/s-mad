# Pre-run check of the standing adversary's shortcut floors (ADV, 4a0abb0), lead-ordered

Independent experiment-reviewer (Opus), ordered by the lead; condensed by the lead from the reviewer's hand-back, 13 Nov 2026. The owner's own review led to amendment 1 (032e8ae); this is the second, independent one.

**Verdict: GO WITH FIXES. No blockers.** Verified: code pins match; all 35 contrasts reproduce the registered row counts; person grouping is sound (own-group fallback fires on 0 rows; no person on both sides; training and test splice persons disjoint); no feature uses labels, paths or manifest columns; no closed-benchmark or MEDS rows; measurements only, no image operation.

Fixes to register before any floor is committed:
- **F1 (major, timing).** Second-engine (SbFM), border-crossed (Sbx) and RZ1 arms may be readable before stage 1 exists. Compute stage-1 rows first (lcomb and the test ladder, about 15 min); the lead holds every SbFM, Sbx and RZ1 read until the stage-1 commit hash is posted in the ADV README; a read before that makes the floor "after the arm's read".
- **F2 (major, integrity).** Freeze floor files: each stage commit adds floors/pins_stage<k>.sha256 over every contrast JSON and held-out CSV; check.exceeds refuses a floor file whose hash is not in a committed pins file.
- **F3 (major, wording).** ADV's bar is called "the ADV floor" everywhere. An arm's own registered floor (RZ1 0.886, GX1's F, RI1/TB1's) remains the only floor in that arm's verdict; the ADV floor is printed beside it and never replaces it. Regression gate: on lcomb the in-sample best single statistic must reproduce 0.886 (noise_std_face) to 3 decimals, otherwise no floor is committed.
- **F4 (major, meaning).** The all-cue floor contains blending statistics, i.e. morph signal, so "within the floor" would not mean "uses a shortcut". Add a second, **nuisance floor** over border + resolution + storage + render features only; report "not beyond hand-made morph statistics; not explained by nuisance cues" when an arm is within the all-cue floor but beyond the nuisance floor.
- **F5 (major).** train_lad floors are context only; exceeds() is not applied to E3's in-sample training-AUC gate; for E2's probe only if E2 uses the ADV components and fold seed.
- **F6 (major).** Amendment for RI1/TB1 rows (all291_S4_vs_S3, R4_vs_R0, R0s61_vs_R0, S0_vs_R0, R2w4_vs_R0, D-quintile strata) before any RI1/TB1 read; pending until committed.
- **F7 (minor).** Arm differences also printed as AUC difference within floor-score quintiles.
- **F8 (minor).** Stage-2 floors on the frozen candidate's audit rows labelled post hoc.
- **F9 (minor).** check.py: assert finite scores; rank with numpy (no scipy on the cluster); pin cue_floor.py and build_border_ref.py.
- **F10 (minor).** Add PNG container metadata features to the storage family (parsed from file bytes); disclose that the bootstrap holds folds fixed.

Lead's answers to the reviewer's questions: (2) yes, the lead holds the SbFM, Sbx and RZ1 reads until the stage-1 hash is posted; (3) "within the ADV floor" is internal-record wording only until the author decides on paper prose.
