# VIS3 prospective controlled soft-splice seam demonstration — v1

Status: SOURCE-ONLY / DESIGN REVIEW REQUIRED / ALL REAL CONSTRUCTION, INFERENCE, RENDER AND PUBLICATION HOLD.

## Purpose and limits
Finish the original request for measured seam/surround responses on actual face photographs, using a KNOWN mask that actually generated a new composite. Existing VIS2 maps are genuine-image occlusion responses and contain no morph seam. Do not relabel them. This NEW controlled demonstration is not existing benchmark evidence, an estimate of prevalence, verification of identity, a pure blur/JPEG test, or a rescue of NOT_QUALIFIED ranking results. Publication remains HOLD; sources are attributed CC BY-NC private research inputs.

## Fixed selection before new outcomes
Only FFHQ00042 and00056 already registered in VIS1/VIS2. Both host directions, every constructed condition, all three fixed GB10 models, both fills, all64cells retained. Selection of these photographs was fixed earlier; it is illustrative and potentially training-exposed, not population-representative. No seed/example search. No00010,FERET,FRGC,new photograph or metric-driven selection.

Inputs are the exact native512 RGB PNGs pinned in INVENTORY.json. Their two historical512 PNGs are ONLY the four-anchor reference and already-admitted VIS2 supporting contrasts; do not recompute historical processing or make new historical splices in this phase. Native/history crops are not identical. Histories42:1024→265→alignment512;56:1024→249→alignment512. Source-photo/person/component training overlap UNKNOWN: descriptive exposed examples, never fresh evidence. No verified age: manual adult-appearing description only.

## Source-grounded construction (prospective; requires Astra design review)
Use the exact FS1 archived morphmamba/data/selfblend.py SHA3c4b06bd4bcd1a51d36afb6bd7dff6f6dc46efa8869eee271719ab33f93ed84f. AST-extract UNCHANGED helper/function bodies and SBI_RATIOS to avoid unrelated dataset imports; source checksum and selected AST names fail closed. No source or RNG modification.

For each native photo, run the unchanged self_blend_int(image,points=None,rng=random.Random(20261115),max_shift=.04,min_shift=3,ratios=(.5,)) with global Python/Numpy seed20261115 and restore caller RNG. This is its REGISTERED FALLBACK ELLIPSE, not anatomical landmarks or an observed benchmark mask. Exact ellipse center(256,256), axes(int512*.32,int512*.42), Gaussian feather selected by registered RNG; actual captured sigma11 in generated-only geometry audit. Source is color-jittered and integer-shifted with reflect padding by original implementation. Capture actual returned source,usedalpha,shift,sigma with a scoped profile hook; assert exact equality of reconstructed result and original unmodified return. Profile hook cannot replace an existing profiler.

Four new derived arrays (same alpha/geometry, no visual edits):
1.42_samephoto: unmodified SBI result for42.
2.42_crossphoto: original registered alpha arithmetic using host42 and the actual transformed source captured from56.
3.56_samephoto: unmodified SBI result for56.
4.56_crossphoto: reciprocal recombination.

The cross-photo recombination is NEW, not an existing registered FS1 dataset generator or a certified valid identity morph. It swaps source provenance while preserving geometry and stochastic processing parameters; source-dependent texture/color remain different. Same-photo is one photograph transformed, NOT two independent photos of the same identity. Do not call this an identity-only causal manipulation. If anatomical alignment/landmark validity is required, this design must remain HOLD until reviewed evidence supplies it; do not invent landmarks/mask.

Literal native.copy() is the no-op control. Identical-source float alpha arithmetic is NOT an exact sham: synthetic fixture exposed ±1 uint8 truncation. Retain original arithmetic in substantive constructions; do not silently round or repair the image.

## Measurements after NEW phase-specific private grants and OTHER review
GB10 only, exact VIS2 model/source/weight/environment pins and model-specific input preprocessing. SelfMAD release and A403/B403 last; no501/Sb403/H100 bridge claim. Before derived-image inference, reproduce all four existing VIS1 native/history anchors within1e-5, repeated and literal-copy no-op, same FP32/noTTA/noAMP/TF32off. Failure stops, no tolerance adjustment or substitute runtime.

On each of four NEW arrays, measure unoccluded z,repeat,no-op; then both fills0/128 over all64native64×64 row-major patches. Delta_z=z_occluded−z_original; positive means hiding raises morph logit. The raw sigmoid is not a probability, threshold=None, decision_flips=None. No gradients or attribution hallucination. Full512responses/model,1536total; smoke4inputs×2fills×6cells=48/model; cell list[0,7,27,36,56,63]. Smoke and full separately released; OTHER smoke check before full. Old genuine VIS2 maps may be reused only after exact permitted read admission; no need to remeasure them. They have NO actual seam.

## Equal-area seam/surround registration
Use actual usedalpha from construction, q=alpha/.5. Actual soft transition is .10≤q≤.90, deliberately a transition band not an anatomical contour. Candidate seam patch has ≥.10 fraction transition pixels. Strict-surround candidate requires all q==0. K=min(counts); choose firstK row-major from each before any model outcome. Generated-only geometry gives seam candidates[3,4,10,13,17,22,25,30,33,38,41,46,50,53,59,60,61], surround[0,7,56,63], K4; selected seam[3,4,10,13]. Each4096px, equal4patches, total16384px per set. All64responses retained, not only regional selection. If actual savedalpha differs from generated reference orK<3, regioncontrastHOLD; never move/search patches after results.

Report every per-patch delta and arithmetic mean for each set separately for both fills/model/host/condition. Optional same-minus-cross contrast is descriptive only. No inferential test on n=2photos/patch pseudo-replication. Matched area/shape/count does NOT match position, texture, face content or erase only the seam; corners vs boundary are explicit confounds. Occlusion creates a new artifact. Fill disagreement and counterexamples retained. High seam sensitivity cannot prove reliance on blending rather than identity; decoding and reliance also differ.

## New private print panel only after actual measured results and independent review
Reuse approved VIS2 layout_v2 geometry180×279.4mm,min8.2pt,58mm large images/maps,two columns. Prefer one host per model page, two conditions(side-by-side); two fills as map rows. Show actual constructed source image and exact saved alpha transition contour separately; never paint a seam onto genuine photos. Additional pages are preferable to illegible four tiny columns. All four conditions, two fills and three models retained; no hero chosen by largest score. Raw baselinez and actualΔz; red hiding raises morph score,blue lowers. Full per-model symmetricL across ALL512new responses; no smoothing/interpolation/clipping,allzeroL transparent/no contrast fabrication. Grayscale absolute magnitude plus negativehatching. Exact regionsets marked with unobtrusive outlines, not fabricated attention.

Polish reader text: „Złożyliśmy fragment tej samej fotografii albo drugiej fotografii, używając tej samej maski. Co robi detektor, gdy zasłonimy granicę połączenia lub tło?” Caption must say controlled synthetic construction, not genuine benchmark morphology.
English: “Prospective controlled soft-splice illustration on two fixed, potentially exposed photographs. Same-photo self-blending and reciprocal two-photo recombination share the recorded mixing mask and processing parameters. Each patch is actually replaced with a constant; Δz is the measured change in raw morph logit. Equal-area boundary and exterior patches differ in position and content. These illustrative responses do not identify a unique causal mechanism or establish benchmark performance.”
