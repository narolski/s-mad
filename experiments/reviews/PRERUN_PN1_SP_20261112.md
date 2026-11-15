# Short pre-run check: PN1 ablation arm Sp

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** Arm (a) "Sp" is cheap and worth running, but prediction 1 is degenerate as written. Fix F1–F5 in the draft before the registration commit. Nothing here needs a new fit or code beyond what the draft already plans.

What I opened: Sb s401/s402 and Bv s401 `scores_eval.npz` under `/mnt/t7/smad_next/PN1/results_rented/unpacked/`. These are results that were already read, and I took only the splice ladder rows. I opened no FS1 tar and no benchmark, sealed or valx file.

**F1 (blocker): "2x Sb's S0 share" is met automatically.**
- At its own rule, Sb flags 0/100 development-ladder S0 images at both seeds: s401 0.000 and s402 0.000, median logit -3.51 and -3.53. Test-ladder S0 is 0.016 and 0.005.
- Two times zero is zero, so prediction 1 holds for any Sp. Under no effect, the 2-of-3 rule then rests on prediction 2 alone.
- Replace line 37 with: "1. At its own rule (logit > 0), Sp flags at least 10 percentage points more of the 100 development-ladder S0 images than Sb at the same seed, and at least twice Sb's share (Sp ≥ max(2·Sb, Sb + 0.10)). Shares are counted out of 100; the bounds are inclusive."
- Add as a printed reference: B and Bv flag 0.00 of dev S0 (Bv s401: S0 0.00, S4 0.04).

**F2 (major): (a) has no rules for missing fits, non-finite runs, ties or the chance of a false hit.** The "Forks closed" list sits under (b) only. Add to (a):
- "A seed is read only if both the Sp fit and the FS1 Sb fit at that seed are finite and complete. Infrastructure failures are re-run unchanged; non-finite runs are never re-run. With fewer than 2 read pairs the arm is 'not read'. With exactly 2 read pairs, 'supported' or 'falsified' needs both. All margins are inclusive. Ties count as meeting the bound."
- "Under no effect, each margin is far outside seed noise: Sb's dev S0 flags are 0/100 at both seeds, and its dev S0-vs-S4 AUC is 0.9875 and 0.9927. So the chance of 'supported' by luck is taken as negligible. This is stated, not computed."
- Restate line 42 as: "Falsified if, on ≥ 2 of 3 read seeds, neither prediction holds."

**F3 (major): the AUC in prediction 2 is ambiguous.** `D_ii_S0_vs_S4_excess_floor3` carries both a raw `auc` and an `excess` over floor3.
- Change line 38 to: "2. Sp's raw development S0-vs-S4 AUC (field `auc` of D_ii, native OpenCV images, 100 vs 100) is at least 0.05 below Sb's at the same seed. Excess-over-floor3 and face-only AUC are printed only."
- Also print dev S3 own-rule flags for both arms. Sb's are 0.34 and 0.36, and Sp drops S3 negatives too.

**F4 (major): the intended sentence is too broad.**
- Sp is not SBI or SelfMAD-like. SBI positives are self-blends, which is closest to S3 (same-person blend inside the face). Sp drops S3 from the negatives and does not use it as a positive. Sp's positives remain two-person S4 splices.
- Sp removes S0 and S3 together, so the result cannot single out S0.
- Replace line 28 with: "Sp tests whether the constituent-matched negatives (S0 seam-only and S3 same-person splices, removed together), rather than the spliced S4 positives alone, are what stop the network from flagging seam-matched genuine composites. Sp is Sb minus those negatives; it is not a reimplementation of SBI or SelfMAD."
- Must not be claimed:
  - anything about SBI or SelfMAD;
  - S0 versus S3 attribution;
  - any benchmark, cross-source or MAD-performance effect;
  - generalisation beyond the OpenCV splice engine and FRGC/colorFERET hosts.
- Label everything as development, n = 3 seeds.

**F5 (major, operations): Sp's run must be a separate, pinned overlay.**
- The draft's single overlay (line 91) contains the changed SbHI train.py. Sp must run on the FS1 pack's train.py (`cbb2cbd1…`) unchanged.
- Add: "Sp uses its own overlay: the FS1 pack plus train_Sp.csv and its regenerated SHA256SUMS only. The sha256 values of train_Sp.csv, the list script, run.sh and the new pack are written into the registration. The pack keeps build_pack_fs's assertion that it holds no FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed row."
- `src/PN1/run.sh` line 35 currently whitelists only `A|B|Bn|C|Sb|Bv`. Sp has to be added, and the edited run.sh pinned.
- Benchmark scoring: run.sh scores only the pack's `pn1_eval.csv`. The FS1 pack's file holds development rows only (`build_pack_fs.py` docstring; `remote_fs.sh:8`). So the driver cannot score benchmark rows as long as Sp's overlay leaves pn1_eval.csv byte-equal. Add that check.

**Checked and ok:**
- **Re-balancing is fully specified.** `mkmanifests.balanced_strata` (seeds 20261111+i) runs over the same four strata, and attacks stay the smaller class in every stratum.
- **Class balance holds.** Removing 312 native negatives (S0/S3: FERET 26 hosts and FRGC 130 hosts, 2 each) gives:
  - feret|native negatives 1602 to 1550, frgc|native 1974 to 1714;
  - rows 8386 to 7762 (-7.4%);
  - frgc|native's share of rows 47.1% to 44.2%.
  - Class balance stays 50/50 in every stratum. The s61 strata are unchanged.
- **Disclose, no fix needed.** With steps fixed at 6250, each image is repeated about 8% more in Sp.
- **The development ladder is held out.** `split/ladder_split.csv` has 100 dev hosts with train_genuine = 0 and train_morph = 0, separate from the 156 training hosts. Eval rows are role 'dev' and OpenCV only.

**Question for the author:** should Sp also print S3 own-rule flags on the test ladder? Or is the test ladder (191 hosts) to stay unread for remedy arms?

Files: `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_remedies_v2_draft.md`, `/home/narolski/smad-next/src/PN1/run.sh`, `/home/narolski/smad-next/src/PN1/mkmanifests2.py`, `/home/narolski/smad-next/src/PN1/build_pack_fs.py`, `/mnt/t7/smad_next/PN1/manifests2/manifests2_summary.json`.
