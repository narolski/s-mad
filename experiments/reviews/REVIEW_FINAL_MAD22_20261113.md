# Results review: the sealed MAD22 read of the frozen candidate (FINAL), 13 Nov 2026

Reviewer: results-reviewer (Opus), read-only. Hand-back saved by the FINAL owner; the report is in the owner's report to
the lead and summarised here verbatim in substance. Corrections C1-C9 are applied in
`experiments/FINAL_sealed-benchmark-read/result.md`.

**Verdict:** sound as to numbers; needs qualification before any sentence is used. Every number in result.md matches
final_read.json (sha256 ee9b6bce…); every registered verdict is mechanically correct (precedence, Holm on families, no
adjustment on the primary and means). The reviewer reproduced the primary exactly from the result tar (c5205a58…) and
the pack manifest (48335f86…): p_ni 0.02499, p_ex 0.12194, interval [−3.51, +0.98].

**Corrections.**
- C1 (major): the primary sentence must carry the landmark-only clause (registered M4 rule); text applied in result.md.
- C2 (major): the "matched" verdict is at its threshold: 49 of 2,000 replicates beyond the margin (one more gives
  "comparable, not separated"); the standard form gives p = 0.0255; post hoc, R = 20,000 gives p = 0.023, and 74% of
  200 alternative seeds give p ≤ 0.025. The comparator choice (SelfMAD raw 4.72 against next 9.89) is not the source of
  fragility; Monte Carlo noise at the threshold is. The point advantage is not significant (p(d ≥ 0) = 0.12).
- C3 (major): every border-equalised "exceeded" is against MADation B/16, L/14 and MixFaceNet-MAD only (SelfMAD "not
  available"), resting on the MIPGAN cells; no sentence may say the network exceeds "the released detectors" or SelfMAD
  in a BE form.
- C4: AD4 MIPGAN reference lines are reversed in all seeds; AD4 withdrew their seed means; print per-seed ranges.
  ViT-L/14 FaceMorpher E7 37.7 carries "per seed 2.0 to 55.4".
- C5: F3 and the border sentence hold on point estimates; the FaceMorpher interval reaches +3.5; standard-form
  FaceMorpher rise +2.1 (not registered for F3).
- C6: add the exposure disclosure (recipe chosen after 401/402 benchmark scores; FRLL genuine scores of the frozen
  networks now exist; BENCHMARK_EXPOSURE choice 8).
- C7: MIPGAN cells read "matched" in S/H because of Holm (unadjusted p(d ≥ 0) 0.010 / 0.008; Holm 0.042 / 0.040);
  the BE flip is the change of comparator.
- C8: means are compared against the single release with the lowest mean; per-family differences against SelfMAD
  (raw) on H: MIPGAN-I −1.9, MIPGAN-II −1.4, OpenCV +1.2, Webmorph −3.3; against per-family best releases −0.7.
- C9: housekeeping (provenance wording, review status, seeds-lower note, one n table).

**May be written** (with "seen during development", the release-path sentence and the frozen-by-decision sentence):
1. the C1 primary sentence in full; 2. "The verdict is at its registered threshold (p = 0.025); on native genuine
photos the same comparison is not separated (p = 0.026)."; 3. "On OpenCV and Webmorph the frozen network is not
separated from the best released detector (2.3 against 1.0% and 10.4 against 11.0% EER, history-matched)."; 4. "On
MIPGAN-I and MIPGAN-II its EER is 0.6 and 0.3% (SelfMAD 2.5 and 1.7%); these cells are not shown to be morph-specific:
the network flags one-photo GAN renders."; 5. "On FaceMorpher, which a network trained without morphs solves (0.0%
EER), it trails MADation ViT-B/16 (2.3 against 0.0% standard, 3.7 against 0.0% history-matched)."; 6. "Equalising the
image border raises its seed-mean EER by at most 0.8 points on the history-matched form (FaceMorpher +0.8 [−2.1, +3.5])
and 2.1 points on the standard form."; 7. "With the border equalised, it is lower than the three released detectors
for which border-free rows exist on the MIPGAN cells; SelfMAD has no such rows, and on the landmark families the
difference is not separated."; 8. "Released detectors' MAD22 errors depend on the genuine photos' history: SelfMAD's
mean EER over the four families rises from 4.7 to 9.9% (Webmorph 13.7 to 29.9%) when the genuine photos pass through
our aligner." (descriptive, CB1 label).

**May not be written:** "state of the art", "outperforms", "beats", "lower than the released detectors" (primary);
"matches or exceeds"; "generalises", "shortcut-free", "detects morphing"; "detects GAN morphs"; any BE sentence implying
SelfMAD was beaten; any FaceMorpher or mean5 SOTA sentence; "border-robust" beyond sentence 6; the primary without the
landmark clause; "no difference on landmark cells".

**Next steps (0 GPU, post-read, descriptive):** 1 apply C1-C9 (done); 2 commit the fragility check as post hoc (lead);
3 SelfMAD per-row `cropped` flags per cell; 4 development seeds 401/402 against frozen seeds (no sign of seed-level
selection: OpenCV 1.93/2.94 and Webmorph 8.20/16.40 against 2.26 and 10.39); 5 register H-new-1/2; 6 NOTEBOOK: any arm
motivated after 21:08 is MAD22-informed; 7 border on SelfMAD's own crop path (author check).

**New hypotheses:** H-new-1 expression (smiling _08 photos drive errors; neutral-only EER Webmorph 10.4 → 7.6,
FaceMorpher 3.7 → 1.3); H-new-2 the BE rise is on the genuine side; H-new-3 Webmorph misses are low blend-energy
morphs; H-new-4 development AUC predicts benchmark rank over seeds 401-407.

**Risks:** a reviewer can argue the standard form ("comparable"); the MAD22 number is optimistic (recipe partly chosen
on MAD22); nothing clean is left for this method; the next selection rule must use no MAD22 number.

Reviewer scratch (not in the repo): recompute.py and extracted scores in the session scratchpad.
