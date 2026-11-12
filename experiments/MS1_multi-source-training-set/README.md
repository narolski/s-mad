# Multi-source training set for threshold transfer (MS1)

## 1. Question and current answer

Do genuine photos, morphs and matched controls from a third capture source (FFHQ) in training make the decision
threshold of the protocol network (PN1 recipe, Sb manifest) carry over to genuine photos of unseen sources?
Status 12 Nov 2026 23:10 CET: build plan registered (`prereg.md`); FFHQ build starting; Multi-PIE found unusable;
FLUXSynID ruled out by the author. No fit, no score.

## 2. Timeline

- 12 Nov ~22:55 CET: author approved the build ("3. Please do build it ASAP."); 50 USD rental budget for the day.
  Owner's `date` at recording: Thu Nov 12 11:01:39 PM CET 2026.
- 12 Nov ~22:57: Multi-PIE inspected (zip listing; 3 crops through the unchanged aligner): 128 x 128 crops only, session
  01, 249 subjects, eye distance about 39 px -> unusable (prereg section 0). Lead agreed.
- 12 Nov ~22:58: FLUXSynID inventoried from the zip listing (14,889 identities; per identity one 1024 px document-style
  JPEG and three live JPEGs `live_0_{a,e,p}`; identity filter lists inside) and one identity's 4 images measured in the
  scratchpad. 23:05: author ruled "Do not use FluxSynID"; scratchpad copies deleted, zip untouched, nothing built.
- 12 Nov 23:0x: plan (`prereg.md` part 1) written and committed before any build step.

## 3. Data

- FFHQ-1024 raw: `/mnt/t7/Datasety/downloads/FFHQ-1024/Part{1..7}/<key>.png` (70,000).
- Exclusion lists: FFHQ-Morphs `/mnt/t7/Datasety/downloads/FFHQ_Morphs/_docs/FFHQ-Morphs/{pairs,bonafide_only}.csv`;
  ffhqm `/mnt/t7/smad_heldout/ffhq_morphs/{manifests/ffhqm_meta.csv,protocol/*.txt}`.
- Outputs: `/mnt/t7/smad_next/MS1/` (to be filled).

## 4. Code

`src/MS1/` (to be filled).

## 5. Results

none yet.

## 6. Checks

none yet.

## 7. Dead ends and failures

- Multi-PIE as held: 128 px crops, unusable (prereg section 0).
- FLUXSynID: ruled out by the author (23:05), not built.

## 8. Observations and ideas

- FLUXSynID's live images: `live_0_a` 512 px with strong expression and tight crop (frontal filter failed in the one
  test), `live_0_e` near-copy of the document image, `live_0_p` a different scene; recorded only for the record.

## 9. Open items and next steps

Build FFHQ (prereg section 3); part 2 (training comparison) registration; pre-run review.

## 10. Handover state

none running yet. Compute spent: 0.

## 11. Reproduce from scratch

to be filled.
