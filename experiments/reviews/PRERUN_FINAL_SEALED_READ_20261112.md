# Pre-run review: sealed final benchmark read (FINAL)

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** The draft is not ready for the author's go yet. Four blockers below must be fixed in the text before it is committed. Reviewed: `/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/prereg.md` at 71fa6e4 (sha256 44498942…; unchanged at HEAD cb1cf09). I opened no score files.

## Blockers

**B1. MorDIFF and DiM are not "clean". Their genuine side is the compromised FRLL pool.** EV1 prereg lines 35–37 says `dim_bona orig` is byte-identical to `frll_bona`, and `mordiff_bona` is the same FRLL photos aligned another way. The cue matrix also notes that MAD22 genuine = FRLL genuine. So every benchmark cell shares the same 204 photos. BPCER, own-rule and τ_dev rates on FRLL photos were seen for every PN1 network (BENCHMARK_EXPOSURE rows 3 and 6, choices 4 and 6). The diffusion cells also helped shape the recipe at program level: SM1's history-crossing arms were scored on MorDIFF ("lost MorDIFF detection"), and AD1 and RS1 built the storage-history thesis on MorDIFF. Replace §5 "Claim scope" and §6 "Clean for PN1 recipes" with:
> "MorDIFF and DiM morphs were never scored by a PN1-family network; their genuine photos are the FRLL photos seen during development, and the recipe ingredient (history crossing) was scored on MorDIFF in SM1. Label: 'morphs unseen; genuine pool seen'. No set read here is clean on both classes."

**B2. Primary and secondary are the wrong way round.** §2 puts the compromised sets (MAD22, FRLL-Morphs) as primary. BENCHMARK_EXPOSURE §4.2 itself says compromised sets go in a separate table "never as evidence of generalisation". Replace §2 with:
> "Confirmatory: the morph side of MorDIFF and DiM (and FEI gtest / sealed sets if the author assigns them). Reported, labelled 'seen during development': MAD22, FRLL-Morphs, H1."

The only set with unexposed genuine photos is FEI gtest (its own 385 genuine photos; metadata only so far). Releasing it here is an author decision (main registration). Without it, no confirmatory claim is clean on both classes.

**B3. The freeze rule refers to things that do not exist or are undefined.**
- (a) MS1 has no registered primary yet. Part 2 is `prereg_comparison_draft.md`, still a draft.
- (b) MS1 has no B arm. Sb/SbM3 only (draft lines 10–14), so "the same MS1 rule applies" (§1 item 2) cannot be applied.
- (c) "Passes" ignores MS1's guards. SbM3 could reduce flags (P1) while losing landmark_combined detection (G1) and still be frozen.
- (d) No rule covers MS1 being unread or unfinished at freeze time.

Replace with:
> "The three-source version is frozen only if MS1 P1 is 'supported' AND every MS1 guard holds, as registered in MS1 prereg.md part 2 at commit <hash> before the first fit; if MS1 is unregistered, unread, or B is frozen, the single-source arm is frozen."

**B4. "Best comparison" is ambiguous and degenerate.**
- §4 puts the morph-free AD4 networks and internal arm A in the comparison set. AD4 networks reach 0.0% EER on MorDIFF native (NOTEBOOK 11 Nov 23:43). So it is undecided whether "SOTA" is measured against a softness detector or against our own arm.
- In the controlled forms, the "lowest BPCER" detector can be one that flags nothing (BPCER 0, APCER 100).

Replace with:
> "Best comparison = lowest value among released checkpoints and AD5 retrain seed means only. Morph-free and internal networks are printed reference lines. Any cell where a morph-free network has EER ≤ 5% is labelled 'shortcut-saturated' and cannot support a SOTA claim. In the own-rule and τ_dev forms, best comparison = the released/retrain detector with lowest (mean APCER + BPCER)/2 on that cell."

## Majors

**M1. The FRLL-Morphs family mean contradicts itself.** §3 says "four non-border families (StyleGAN and AMSL included)". But AMSL, FaceMorpher, OpenCV and Webmorph are all landmark cells with the aligner's border (PN1 prereg line 142), which leaves StyleGAN as the only border-free family. Fix: the headline is StyleGAN only, and the landmark mean is printed.

**M2. Multiplicity, and choosing the best cell after the fact.** The abstract rule "matched/exceeded on MorDIFF *or* DiM" lets the claim rest on whichever of seven cells and four forms happens to look best. Fix: make one pre-specified confirmatory endpoint, the τ_dev form (APCER per family at τ_dev, BPCER on the E7 pool) on the MorDIFF + DiM family mean. Everything else is descriptive. Holm correction across the confirmatory cells.

**M3. The statistics ignore seed variance.**
- A person bootstrap of our 5-seed mean against a single checkpoint leaves out seed variance.
- The controlled "exceeded" rule ("at most half") has no interval at all.

Replace with:
> "Exceeded requires the 95% interval of a two-level bootstrap (seeds, then persons) of the difference entirely below 0 AND ≥ 4 of 5 seeds individually better. Matched (non-inferiority) = upper 95% bound of (ours − best) ≤ +1.0 point."

Apply the same rule to the BPCER ratio.

**M4. τ_dev is not the same for all detectors.** Ours comes from our training-source camera photos (R0+AF0). The releases' comes from EV1 devbona. Fix: compute both pools for every detector and print both. The decision uses R0+AF0 for all detectors.

**M5. The diffusion outcome is not pre-stated.** REVIEW_SM1_12FITS line 115 expects a shortcut-free method to be near chance on render-matched diffusion morphs (arm e MorDIFF native 34–47%). Add to §8:
> "Predicted: frozen arm E7 EER on MorDIFF/DiM ≥ 30%; releases' low standard-form EER there is read as render-path/storage detection (AD4, RS1). Under this prediction the abstract carries no SOTA claim."

Also add a §8 row: "matched on MAD22, lost on diffusion".

**M6. The scoring path for the releases is not pinned or gated.**
- The JPEG decoder build changes scores by up to 5.9 logits.
- Face-detector boxes differ across GPUs for about 1 image in 10.
- The authors' crop script fails on MorDIFF.

Fix:
- Put RS1's precomputed boxes and crops in the pack, and pin the Pillow/libjpeg build.
- Use the corrected MorDIFF crop (RS1 amendment 7).
- Add a release gate: rescore 200 RS1 rows, max |Δ| ≤ 0.05, or stop.
- State whether existing RS1/AD5 scores are reused or rescored.
- Add a table of detector × form → input path. Where an E7 pool does not exist for a path, print "not available". No new resampling code (hard rule).

**M7. Platform.** The gate is shown only for A100, but MS1 networks are trained on WCSS H100 (draft line 18). Fix: name the GPU type and software stack, and include an H100 network in the gate.

**M8. Feedback and failure handling.** Add:
> "After the read no network is trained, no recipe, threshold or freeze input is changed before the paper; later work is labelled post-read. Outputs go to a sealed file shown only after the whole job finishes; a crash is re-run unchanged with no partial output viewed. A failed gate may be repeated once after an infrastructure fix, still with no benchmark rows; a second failure → audit-only branch."

## Minor

- The neutral-only genuine pool should be printed for every cell, not only FRLL-Morphs (expression cue; C1).
- Pin one metrics function by sha for all detectors (EER interpolation, ties).
- The MS1 recipe is itself shaped by benchmark-informed threshold-transfer framing (exposure choice 6). Add this to §6.
- The lead endorsed the Sb refit after the H1 result was seen, so the lead is not blind. Disclose this, or have someone else run the read.

## Freeze-rule question (point 1)

Once B3 is fixed, the rule is mechanical and uses development data only. Its inputs are FS1 contrasts 1–2 and MS1, which are allowed model selection on FFHQ and our ladders. "No method" is a real branch: it is reached when A's positive control fails or contrast 2 is not replicated. The disclosure that matters is that the candidate set {A, B, Sb} and the margins were chosen with benchmark knowledge. §6 states this. The paper must also say it in its Experiments section, not only in a supplement.

## Missing for CVPR

- Every arm uses one backbone and one generator per family. A second backbone (at least a DINOv3 or ViT-B/16 rerun of the frozen arm) or an explicit limitation statement is needed.
- Cross-dataset protocol table: training sources against test sources.
- Ablation table: A, B, Sb, Sp, SbM3.
- Paired seed tests.
- Compute disclosure in GPU-hours, including audits and rentals.
- Limitation statement: thresholds do not transfer to unseen genuine sources unless MS1 passes, and all benchmarks share one genuine pool of 204 FRLL photos.

## Author decisions

1. Release FEI gtest and/or the sealed sets as the confirmatory set, which only matters if B2 is accepted.
2. Accept the controlled τ_dev form as the confirmatory endpoint, with the standard form secondary.
3. Who runs the read, given that the lead is not blind.
4. Wait for the AD5 retrains, or print "not available".
5. Accept that the expected outcome is no SOTA claim in the abstract.
