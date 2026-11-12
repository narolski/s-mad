# Threshold transfer on unseen genuine sources (TT1)

Owner: TT1 owner agent (started by the lead, 12 Nov 2026). Folder created `date`: Thu Nov 12 10:54:00 PM CET 2026, at
git `dac4d99b2d8d42f24fc8c32c5dba0ab7c07671a8` (branch sprint-plan-v2).

## 0. Author's approval

- The author asked on the evening of 12 Nov which genuine data we have, and approved running the aligner on new unseen
  genuine sources, his words: "Run the aligner, of course!" (relayed by the lead in the owner's task message; the time
  of the author's message is not known to the owner; recorded here at `date` Thu Nov 12 10:54:00 PM CET 2026).
- The 12 Nov ruling holds: no set used to benchmark methods (FRLL, MAD22, MorDIFF, DiM, H1, FEI, sealed sets; also
  CASIA-WebFace, the source of H1) is used in development. The sources below are not benchmarks of this sprint, and
  none of them was used to train any network of the sprint.

## 1. Question (plain words)

Our candidate detectors (CLIP ViT-B/16 + LoRA, the protocol network first tests (PN1)) put morphs above genuine photos
well, but a fixed threshold does not carry over to genuine photos from a source they never saw: photos of the training
databases (FRGC, colorFERET) sit on the floor of a bounded score range, other sources sit higher. TT1 asks, on genuine
photos only, how often each network flags photos of unseen sources, whether that false-alarm rate follows the image's
enlargement (how much a small source face is blown up to the canonical 132 px eye distance) and sharpness or the source
itself, and which training arm gives the lowest and most uniform false-alarm rates. There are no morphs of these
sources, so TT1 is a false-alarm test only.

## 2. Step 2 (pool building; no score is computed in this step)

- Sources and rules: `src/TT1/extract.py` (docstring is the specification). Genuine anti-spoofing frames ("Bona fide"
  in each set's `metadata.json`, asserted equal to the documented file-name convention on every row) and distinct images
  of four face-verification validation packs (lfw, calfw, cfp_ff, agedb_30), loaded only with a restricted unpickler.
  Not used: CASIA-WebFace `train.rec`, `cplfw.bin`, `cfp_fp.bin`.
- Alignment: `src/TT1/align.py` calls `align()` of `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py` unchanged
  (sha256 `374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628`), the function every genuine pool of PN1,
  AR1, AF0 and FFHQ-Morphs went through.
- The scoring experiment is registered separately (draft `prereg_scoring_draft.md`, for independent pre-run review);
  nothing is scored before that registration is committed.
