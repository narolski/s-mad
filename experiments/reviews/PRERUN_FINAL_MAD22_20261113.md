# Pre-run review: the sealed MAD22 read of the frozen candidate (FINAL v3)

Reviewer: experiment-reviewer (Opus), 13 Nov 2026, about 19:10-19:20 by the machine clock. Read-only. Report as
returned, unedited. The owner's handling of each finding is in `experiments/FINAL_sealed-benchmark-read/README.md`,
item 12.

**Verdict: GO WITH FIXES.** The gate, the one-start guards, the border-equalised copies and the metric code hold up. Before the registration commit, one fairness blocker and four majors need fixing. All of them are text or code edits that cost no GPU. prereg v3 is still uncommitted, so they are cheap now and impossible after the read.

What I ran, all allowed: the metrics self-test (passes); sha256 of every pinned file (all 30 pins match `final_pins.json`); the stored dev-score ids and metadata, without logits; the metadata columns of the release file, without logits; a pixel-only check of the border-equalised copies. I created no score and opened no sealed file.

## Findings

**B1 (blocker) – The release H-form is not history-matched, and half of `mean4` uses the same genuine pool in both forms only for us.**
- **Evidence:** `final_read.py:170-171` builds release H from `M22_<fam>` against `E7aln22_<fam>`.
  - In `athena_manifest.csv`, `M22_*` are the raw JPEG morphs (`author_files/original_sorted/...jpg`).
  - `E7aln22_*` are our aligned PNG frames (`mad22_canonical.../e7/...png`).
  - So for the releases, genuine photos get our aligner, resampling and PNG; morphs stay raw JPEG. Our H has aligned frames on both sides.
- **Size:** PROCESSED_SHA256SUMS shows e7 equals native for MIPGAN-I 204/204, MIPGAN-II 204/204, OpenCV 108/204 and Webmorph 104/204.
  - So our MIPGAN H is the same as our S, but the release MIPGAN H is "aligned native", not its S.
  - CB1 `result.md:236` puts this aligner-only step at +5.3/+5.4 EER points for MixFaceNet on MIPGAN, and −3.9 to +0.1 for ViT-L/14 (line 230). Both are larger than the 1-point margin, and the direction depends on the release.
- **Fix** (author or lead choice, before commit):
  - (A, recommended, conservative) Score each release in both forms (G22_raw and E7aln22), and take the best comparison as the minimum over releases and both forms.
  - (B) At minimum, use G22_raw as the release H pool where our E7 pool equals native (MIPGAN). Also print the release's G22_aln row and the aligner-step difference beside the primary result. Add a disclosure sentence: raw JPEG morphs against aligned PNG genuine photos for the releases.

**M1 (major) – The reader can use up the one read before it checks its inputs.**
- `final_read.py:427` creates the marker before `load()`, which does the pin asserts (lines 94, 99) and the KeyError-prone lookups.
- If the pin commit forgets `--selfmad` or `--beststat` in `final_pins.json`, or the reader hits any bug, the run dies and no second run is allowed.
- **Fix:** verify every pin and parse every input before `marker.mkdir()`. Register that a crash which writes no output can be rerun once, with the lead's word, unchanged inputs and the traceback kept.

**M2 (major) – Checks that score nothing run after `STARTED` is created, so they use up the one start.**
- `remote_final.sh:20` creates `STARTED` first. The GPU model, disk space, pip install (needs internet) and versions are only checked afterwards (lines 41-54).
- The name check `grep A100-PCIE` matches only "A100-PCIE-40GB". An "A100 80GB PCIe" lease would abort after `STARTED` exists.
- prereg §9 covers only a failed gate and a crash after the gate. A failure before the gate is not covered.
- **Fix:** move `STARTED` to just before the gate is scored, or register that a failure before the gate (no score yet) allows a fresh lease. Tell the lead to rent "A100-PCIE-40GB" exactly; that is the stored run's device in `info.json`.

**M3 (major) – prereg and code disagree.**
- §3.2 says the releases' aligned native row (G22_aln) is printed; the reader never uses it.
- §4 says the morph-free networks are printed; the reader never loads them.
- §5 F3 ("≤ 2 points") gets no held or falsified verdict; only the 3-point caveat is computed (lines 334-342).
- `LAB_SAT` (line 40) says "≤ 5% EER"; C4 says 0.0%.
- **Fix:** bring the code in line with the text, re-pin, rerun the mocks.

**M4 (major) – Half of the primary endpoint is cells the prereg calls "not shown to be morph-specific".**
- A `mean4` win could come from flagging GAN renders.
- **Fix:** register a landmark-only mean (OpenCV plus Webmorph) as a secondary result with its own verdict. Add a sentence rule: if its verdict differs from `mean4`, the primary sentence must say so.

**Minors**
- **m1, best-release choice:** the best release is picked once by point EER (line 300) and then held fixed. This favours the release, which over-reports "lost". Pick the minimum per replicate, or disclose.
- **m2, missing intervals:** there are no absolute EER intervals per detector, only intervals of the difference. Add percentile intervals from `rep` for every detector and cell; the paper needs them.
- **m3, non-finite logits:** nothing checks for them. Assert finite logits, and treat a failure as "no read" under the never-re-run rule.
- **m4, gate check:** `gate_check_final.py` does not check that the stored npz order and `manifest_sha256` match. I checked offline: all five tars match `pn1_eval` order (19,797 unique rows) with manifest sha `f0f29f22`, `limit` 0, A100-PCIE-40GB, host `e8bf0b3abe77`. Add the assert, or record this in the README.
- **m5, power:** with 102 persons, the paired difference interval is probably ±2-3 points, so "matched" needs about a 1.5-2 point advantage. State this detectable difference in §4, so that "comparable" is read as expected rather than as a failure.
- **m6, border wording:** `rs1_border.csv:36` shows black pixels in 26.5% of MIPGAN-I morph crops against 1% of genuine (maximum fraction 0.0000). Write "under 0.01% of pixels", not "no border".
- **m7, pin commit:** `make_pins.py` rewrites §10 of the registered text. Append the later pins as a dated addendum instead.
- **m8, disclose:** `beststat_limit8.npz` already exists (noise statistic on 8 MAD22 genuine rows, before registration). Harmless, but say so in the README.
- **m9, v1 crop failures:** 66 FFHQ photos are dropped from the release thresholds (n = 1,934). This affects secondary results only; say so.

**Checked and sound (your points 1, 4, 5)**
- **Gate:**
  - The kept rows are batches with index ≡ 0 mod 3 of the full manifest.
  - `rescore.py` filters `fam == gate` and uses batch 64, so every batch has the same members as in the stored `pn1_score.py` run (full manifest, in order, batch 64, TF32 on).
  - The last batch (index 309, 21 rows) is included.
  - Byte identity is the right test for the same stack.
  - No benchmark row can be scored before the gate passes.
  - A second start is refused by both the host `STARTED` file and the local directory lock.
- **Border-equalised copies:** I PIL-decoded 135 sampled copies. All are identical to the source outside the mask and zero inside it, and all sources are plain RGB. Near-black pixels left outside the mask in morph copies: 0-10 across 15 images per family. The mask's share of the central face box is 0.
- **Thresholds:** the stored "logit" is the morph log-odds for every release (`head_logit` with `morph_index` 0 for MADation and MixFaceNet; out[:,1]−out[:,0] for SelfMAD, `morph_index` 1). SelfMAD's threshold and its scores use the same key.
- **Statistics:** signs, the pairing (one count matrix shared by all detectors), seed resampling, Holm, the p-values, the order of precedence and the sentence signs are all correct.

## Improvements, ranked
1. **B1 option A** (0 GPU). Needs the author's or lead's decision now.
2. **A dry run of the gate on the lease before the start** (dev rows only; `FINAL_TEST_STOP_AFTER_GATE` already exists). A failing card then costs a new lease, not the read. It can't bias the result because no benchmark row is involved, but it needs prereg text.
3. **Optionally, register a tolerance fallback before seeing any gate.** For example: max |Δ| ≤ 1e-4 and zero flips at the own rule and at τ_FFHQ; read proceeds, labelled. EER is not sensitive at that level. Author decision.
4. **M1-M4 and m1-m4:** code and text edits, about an hour, then re-pin and rerun the mocks.

## Questions for the authors
1. Which comparator for the release H-form: option A, option B, or keep the current one with disclosure?
2. Do you accept a gate dry run on the lease, and/or a tolerance fallback registered in advance?
