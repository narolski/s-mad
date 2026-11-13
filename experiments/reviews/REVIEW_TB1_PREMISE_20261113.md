<!-- Post-result review of the TB1 premise read (fdfa458) by the results-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. The reviewer's post hoc scripts are copied to experiments/reviews/scripts_tb1/. -->

**Verdict: needs qualification.** The numbers are right and the registered rule was applied as written, so "premise holds (≥ 0.70 within D)" stands as the registered verdict. The physical sentence behind it does not follow, though: "two people's texture difference has a different frequency profile from two sessions of one person at equal blend energy". My post hoc checks below use only the registered TB1 feature file and landmark files, with zero GPU. They show three things. The profile is mostly a band-limited energy measure. Its finest-band share does the work, not the mid-band "anatomy" bands. And it cannot be told apart from how far the two faces' landmarks differ. The "within G" control does nothing by construction.

## 1. Do the numbers and rule match?
- Every reported number matches `tb1_premise.json`: 0.758 [0.718, 0.795], pure-D reference 0.524, D_lin 0.707, D_dc 0.776, G 0.787, overall 0.783, eroded hull 0.809, FRGC 0.864, colorFERET 0.554, joint strata 0.61–0.84.
- I re-ran the reader's fold models on `tb1_feats.csv` and reproduced 0.7834 / 0.7576 exactly. The file's sha256 `a79980a3…` matches its pin, and both code pins in `src/TB1/SHA256SUMS` match.
- The features were written at 19:37:08, after amendment 1 (6af821f, 19:30) and before the result commit fdfa458 (19:38).
- Both T3 fixes are in the code as registered: the difference is centred by its hull mean before the FFT (`tb1_measure.py`, `diff[m7] -= diff[m7].mean()`), and the eroded-hull energies (`erode(m7, 16)`, 16 passes of a 3×3 kernel) are printed. The D_dc strata are printed too.
- T1, T2 and T4 belong to the single-image part and have not been exercised yet.
- The verdict follows the code as written: the point estimate is ≥ 0.70. No interval condition was registered for TB1.

## 2. Findings, most severe first

**F1 (major). The profile behaves like an energy measure.**
- The profile p_k drops the coarsest band (B0, which holds the shading) and the finest band (B6). D keeps both. So "equal D" does not mean equal energy in the bands the profile uses.
- The total energy E over the same five bands separates the classes at 0.804 on its own, and at 0.775 within D quintiles. Both are higher than the profile itself (0.781, and 0.758 within D).
- Within quintiles of that same energy, the profile drops to **0.619** (coverage 0.80; its strata run 0.79, 0.69, 0.68, 0.59, 0.50). That sits at the registered "no difference" line of ≤ 0.62.
- In cross-fitted models, the profile adds +0.033 over log E alone (0.804 → 0.837), and log D adds nothing.
- Within the stricter D_ac quintiles the profile reads 0.682.
- Fix: say "at equal D, not at equal band-limited energy", and print the gain over log E.

**F2 (major). The signal sits in the finest band's share, not in mid-band anatomy.**
- Two-person differences carry a smaller share of B5 (median 0.087 against 0.129 for same-person). One-band AUCs: B5 0.254, B4 0.367, B3 0.562.
- The B5 share alone gives 0.708 within D, which is most of the 0.758.
- FRGC carries this (B5 AUC 0.176); colorFERET does not (0.419). colorFERET's fine-band shares are much smaller in both classes (B5 0.05 against 0.09–0.14).
- The simplest reading: a fine-scale floor of sensor and storage noise, equal in both classes, gets diluted by the extra structured difference between two people.
- So the FRGC 0.864 against colorFERET 0.554 split looks like a source-detail (noise-floor) effect, not a session-type cue. Two FRGC checks point the same way:
  - Within FRGC, the AUC stays at 0.82–0.89 in all four cells of "same semester or not" for the host–partner and host–second-photo pairs. Semester is a proxy for the camera generation.
  - The day gap between the two same-person photos does not track the score (ρ = 0.05).
- This contradicts the mechanism ledger's M2 prediction (relatively more mid-band energy for two people).

**F3 (major). Geometry is not controlled.**
- G is one value per host: the S4 and S3 rows carry the same G, which I confirmed with `np.allclose`. So "within G 0.787 (pure reference 0.500)" and the G halves of the joint strata control nothing.
- The per-class quantity that matters is the landmark displacement W between the two source photos (mean over 106 points; H to B for two-person, H to S for same-person).
  - W separates the classes at 0.869 by itself.
  - Within W quintiles the profile reads 0.707 at coverage 0.60, and the high-W strata fall to 0.59 and 0.45. Joint D × W tertiles give 0.726.
  - Within same-person pairs, the score rises with W (ρ 0.36) and falls with face-recognition similarity (ρ −0.50).
- Both identity (face shape) and misregistration or pose stay open as explanations.
- Fix: withdraw "within G" as a control.

**F4 (minor). Cross-fitting by person changes nothing.**
- Folding by the connected components of the host–partner graph (110 components, the largest has 10 hosts; 68 pairs are reciprocal) leaves the within-D AUC at 0.757.
- A bootstrap over components widens the interval to [0.701, 0.801]. Report this interval.

**F5 (minor). The hull edge is not the driver.** Eroding the hull by 16 px raises the AUC to 0.809.

**F6 (wording). Suggested rewrite:** "At equal BD1 D, the band-limited energy and the band profile of the luminance half-difference separate two-person from same-person pairs (0.76 within D; FRGC 0.86, colorFERET 0.55). Most of it is the share of the finest band, and at equal band-limited energy it falls to 0.62. It is not separated from the larger landmark displacement between two people (0.71 within W, coverage 0.60). An oracle reading on one engine. Not a texture trace of a second identity, and not a detector."

## 3. What this allows
- **Single-image part:** it may run as registered. My prediction: in one image, the fine-band drop inside a 50% blend is mostly noise averaging, which an identity-free same-person blend has too. So the binding gain of +0.03 over the splice shortcut features (including the inside/outside sharpness ratio) is the deciding row. I expect it to fail.
- **Training arm:** nothing is licensed. Any arm would be a post-freeze ablation, and it would need new blends, which are author items.

## 4. Follow-ups, by information per GPU-hour

| # | Follow-up | GPU-h | When | What it decides | Approval needed |
|---|---|---|---|---|---|
| 1 | Register amendment 2 (labelled post hoc): profile within band-energy quintiles, gain over [log D, log E, log W], within-W and joint D×W strata, component folds | 0 | now | whether "profile" claims more than energy plus geometry. Falsified if the gain over [log E, log W] is < +0.02 | none |
| 2 | Single-image part read as registered, with the F2 prediction written down first | 0 | after the ADVERSARY floor | whether one image shows it | none |
| 3 | B capture dates from the FRGC sigset metadata (a list read). Stratify two-person rows by host–partner day gap, including same-day pairs, against same-person rows at matched gaps | 0 | before Nov 8 | identity against session. Session is the story if same-day two-person pairs drop to ≤ 0.6 | none |
| 4 | Same-person high-W subset (about 37 existing pairs) against two-person pairs at matched W | 0 | now | geometry against identity (small n, descriptive) | none |
| 5 | Same-person different-session halves from the NIST cross-encounter list, and same-day two-person splices | 0 GPU (CPU warps) | author item | the clean separation of session from identity | author: warps are author items under rule 3; no MEDS identifier may enter the repository |

**H-new-1:** the TB1 signal is the extra structured energy between two people diluting a fine-scale floor shared by both classes. Prediction: on FRGC, the profile within band-energy and W strata is ≤ 0.62. It is falsified if the gain over [log E, log W] is ≥ +0.03 with a component-bootstrap lower bound above 0.

**H-new-2:** what TB1 measures is face-shape mismatch (identity geometry), not skin texture. Prediction: same-person pairs at matched W score like two-person pairs (tests 4 and 5).

## Files
- Result being reviewed: `/home/narolski/smad-next/experiments/TB1_texture-band-profile/result.md` and `tb1_premise.json`.
- Code reviewed: `/home/narolski/smad-next/src/TB1/tb1_measure.py`, `/home/narolski/smad-next/src/TB1/tb1_read.py`.
- My post hoc analysis scripts, which only read the registered feature file and the landmark files:
  - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/a1.py`
  - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/a2.py`
  - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/a3.py`
  - `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/a4.py`

No sealed, benchmark or score files were opened.
