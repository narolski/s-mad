# Pre-run review: PN1 amendment 14 (one lease) and fresh-seed draft v3

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited. Both batches: GO WITH FIXES.

I worked read-only. I did not open valx.csv, FST, A12SP or any FFHQ landmark_combined score. The files I read were the drafts, the code, prereg.md, result.md, the reviews and the ffhqm manifest and sidecar metadata. The pins all match the drafts: rescore 6f6eede7, remote_a14 5ce2a5ce, drive14 34866f3a, build_pack14 aa21ada0, a14_read b653efba, manifest 9f199c3a, floor list e1df77a5 and pack sha file bda5fd3d. I did not re-hash the 4.4 GB tar; the remote script checks it. /mnt/t7 has 25 GB free, not 30, which is still enough.

# Batch 1 (amendment 14, one lease): GO WITH FIXES

All the fixes below are allowed now, because no amendment-14 score exists yet. Edits to the scripts change their sha256s, so put the new pins into the registration before you commit it.

**F1 (major): HN8 is not a "first read", and it is not independent of HN2.**
- From ffhqm.csv: all 1,000 landmark_combined morphs use the same pair keys as the landmark_complete morphs in HN2 (1,000 of 1,000). They share the same landmark morph process.
- The landmark_combined resmatch genuine pool is the same 2,000 FFHQ persons and source photos as HN2's landmark_complete resmatch pool. Only the shrink target differs (median eye distance 64.65 vs 64.61 px), and only 1 file is byte-identical.
- A, B, Bn and C have already scored that near-twin genuine pool, and the earlier reviewer read it.
- What is genuinely new: the combined surround (a real contributor photo), and a splice engine that is neither OpenCV (Sb's training splices) nor Poisson (H1).
- **Fix:** replace line 60 with: "New morph images built from the HN2 pairs with a real surround. The genuine pool is the HN2 persons, re-shrunk. Independent of the training splice engine and of H1, not of HN2."

**F2 (major): HN8 can hit a ceiling.**
- B's landmark_complete AUC against history-matched genuine was already 0.994 / 0.997.
- If B is at or above 0.95 on landmark_combined, "Sb − B ≥ 0.05" cannot be met, and "Sb ≤ B" would be decided by noise near 1.0.
- **Fix:** register "B ≥ 0.95 on a seed → that seed is untestable (ceiling)" (the AR1 H-D lesson).
- Also register a printed read that cannot saturate: per pair key, the logit on landmark_complete minus the logit on landmark_combined. It needs no extra GPU (complete scores exist for A, B, Bn and C, and Sb and Bv get them in HN2b). It also measures surround reliance directly, which is HN7's mechanism.

**F3 (major): the floor can silently drop out, and it compares point estimates.**
- a14_read.py:161 computes the floor only `if cf.exists()`. Otherwise it writes `floor=None` and nothing complains.
- Simple cues are strong on this set: the A8 DS diagnostic reached 0.93 on landmark_complete (ffhqm REGISTRATION_DRAFT caveat 2). Aligned PNG bytes also differ by class (medians 324k vs 341k).
- **Fix:** make the floor file mandatory (assert it exists and check its sha256). State "reads the face splice" only if Sb's bootstrap lower bound exceeds the floor, with the floor's maximum re-taken in every draw (as prereg §6(a)). Print the aligned==1 subset (excluded: 1 morph, 11 genuine).
- Also disclose that A's reading of the history-matched pool is history-driven: 72–78% of FFHQ persons rise when history-matched (review F2). That shifts the "Sb ≥ A" comparison for reasons other than face reading.

**F4 (major, operations): a single failure loses every result and never writes RELEASE.**
- In remote_a14.sh, `fail` (line 12) exits on the first failing network-and-family call. No tar is made, and the scores already written in `$W/res` are never pulled; drive14.sh:27 pulls only PN1_A14.tar.
- drive14.sh writes RELEASE only after a verified tar (lines 29–30). The pull loop gives up after 30 × 5 min, and the lease then idles until the guard's cap or deadline. The amendment registers neither value.
- **Fixes:**
  - Make each call continue on error and log it.
  - Always tar whatever exists (with an rc file) and pull it.
  - In `pull`: if rc is non-zero and the partial tar is verified, write RELEASE plus a FAILED marker.
  - Register the guard values (e.g. cap 1.5 USD, deadline at start + 2.5 h).
  - Fail early if `/workspace` has less than 15 GB free (pack plus dereferenced extract is about 9 GB).
  - Check for the A14_STARTED echo; at line 23 it is currently swallowed by `|| true`.
- Re-run an infrastructure failure unchanged, once, on the same lease type.

**F5 (major, interpretation): HN7 cannot support "sets its transfer".**
- The 12 points are 6 arms × 2 seeds. Bv is B with repeated rows, and Bn is a subsample of B, so there are about 4 independent training regimes.
- The bootstrap resamples hosts, not training, so its interval is too narrow.
- Sb is the only arm trained on splices, and it sits at the top of both axes.
- All 12 H1 values and 6 of the 12 face-only values were known when HN7 was written. My simulation shows it is not settled in advance: with the 6 unknown values random, median ρ is 0.36, P(ρ ≥ 0.6) is 0.14, and the possible range is −0.36 to 0.88. Still disclose it.
- **Fix:** label HN7 "associational, between arms". Print the arm-level ρ (seed means, n = 6) and ρ without Sb. Say that the only prediction made blind is "A's face-only AUC > B's on both seeds".

**F6 (minor): the equivalence gate.**
- The tolerances are sensible. The 5.9-logit JPEG-decoder effect and the detector-box differences do not apply here:
  - inputs are pre-aligned 512 PNGs;
  - the loader only opens the file and resizes it bilinearly (pn14/code/smadcvpr/common.py:855–859);
  - there is no detector at scoring;
  - the forward pass is fp32 with no autocast (common.py:396);
  - Pillow, numpy, timm and the torch image are pinned;
  - every GPU involved is sm_80.
- The 5-row GB10 reference is weak, but the risk is low.
- **Fixes:**
  - Bind the gate only to reads that cross platforms (HN7 mixes new-lease A, Bn and C with pn1a/pn1b B, Sb and Bv; HN2b compares against HN2). HN8 is scored entirely on the one lease and should not be voided by a gate failure.
  - Add "a failed gate is not re-run on another platform".

**Required before submission:** copy the draft into prereg.md with fixes F1–F6 and the new pins, commit it, and update the PN1 README ledger entry. Also freeze the batch-2 contrasts first (B2-F2 below).

# Batch 2 (fresh seeds v3): GO WITH FIXES, after the author approves the budget and rules on Sb

**B2-F1 (major, compliance): the case for Sb is selective, so the author should rule on it.**
- Draft lines 17–24 cite two development-ladder reads that favour Sb. They leave out the development read that killed Sb: read (i), face-blanked development 0.991 / 0.999 against B's 1.000 (result.md:126, 128).
- The recommendation to refit Sb was made after H1 had been read (batch-2 review F4: "Sb above all 8 reference seeds"). The 0.05 margin was set knowing the H1 gains of +0.13 / +0.23.
- This meets the letter of amendment 10 (prereg:457–459) but not its spirit.
- **Fix:** disclose "killed by its registered rule; refit chosen on development reads after H1 was seen". Label contrast 1 "fresh networks, re-read images, contrast set after the 401/402 H1 read". Get an explicit author ruling that refitting a killed arm is allowed.

**B2-F2 (major): batch 1 contaminates contrasts 2 and 3 unless they are frozen first.**
- Batch 1 will show Sb, B and A on landmark_combined, and Sb's paired share (from HN2b), for seeds 401 and 402.
- The networks stay clean, but the thresholds 0.05, ≥ 0 and 0.65 could be tuned afterwards.
- **Fix:** commit section 3 of v3 (contrasts, margins, seed rules), with a clause that nothing changes except budget and C, before batch 1's tar is pulled. Label landmark_combined "second read of the images (first read on 401/402 under amendment 14); genuine pool = HN2 persons". Carry over the ceiling clause from F2.

**B2-F3 (major): forks still open.**
- What happens when a seed is lost or a run is non-finite? For example, does "≥ 4 of 4" count, or is the contrast "not read"? Non-finite runs are never re-run.
- Ties at a margin.
- When C is decided: before any fresh result.
- The τ_multi list (§2, line 39) depends on the author's FEI/SMDD answers. Pin its sha256 or drop it.
- The rule for a partial result at the 14 Nov deadline.
- A table of what the paper claims under each outcome. Suggested:
  - H1 and landmark_combined replicate, with the floor exceeded: "spliced positives raise face-splice detection over protocol-only, across seeds and on a second engine".
  - H1 only: "engine-specific".
  - Neither: "the Sb lead was selection or seed noise".
  - Storage mark, with B and Sb passing and A failing: "the protocol removes the storage reaction on an unseen source, 5 seeds".

**B2-F4 (minor): power.**
- With a margin of 0, "Sb − A ≥ 0" reaches ≥ 4 of 5 with probability 0.19 under no effect.
- Pick a margin now: non-inferiority ≥ −0.02, or superiority ≥ +0.02.
- If the tier-1 gaps are real, the H1 contrasts will almost certainly replicate (reference seed SD 0.018), so they mainly test winner's curse.
- A's positive control (0.72 / 0.78 against 0.65) is likely, but not certain, to fail on ≥ 4 of 5 seeds.

**B2-F5 (minor): seeds and machines.**
- Keeping each seed whole on one machine is correct.
- HN9's single replicate fit cannot separate "machine" from run-to-run nondeterminism. Relabel it "platform plus nondeterminism".
- Print results per machine (machine 1 runs 9 fits, machine 2 runs 7).

# Improvements (value per GPU-hour)

1. Paired complete-minus-combined logit per pair (F2): 0 GPU; register it now.
2. Arm-level ρ and ρ without Sb for HN7: 0 GPU; register it now.
3. Floor lower-bound rule (F3): 0 GPU; register it now.

# Questions for the author

1. May the killed Sb arm be refitted on the grounds stated in B2-F1?
2. Is any ffhqm family (landmark_combined included) reserved as an endpoint in the main registration ("endpoint role ... fixed by the main registration", REGISTRATION_DRAFT)? If so, PN1 reading it needs your sign-off.
3. Do you approve the budget: 16 fits (about 11.6 USD) or 19 with C?

Files:
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_amendment14_draft.md
- /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_fresh_seeds_draft.md
- /home/narolski/smad-next/src/PN1/rented/remote_a14.sh
- /home/narolski/smad-next/src/PN1/rented/drive14.sh
- /home/narolski/smad-next/src/PN1/a14_read.py
- /mnt/t7/smad_heldout/ffhq_morphs/REGISTRATION_DRAFT.md
