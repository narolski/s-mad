# Independent OCC1 numeric print v3 re-review

Astra, 14 November 2026. **PASS / GO_NUMERIC_ONLY_INTERNAL_PRINT_QA** for the exact ten v3 PDF pages bound below. This resolves the v2 clipping/layout repair findings only. It is not completion of the requested face-containing figure or on-image explanation, not source-face/overlay export permission, and not publication GO.

## Checks and findings

All ten actual PDFs—A, B, Sb, MixFaceNet-MAD and SelfMAD, each color and grayscale—were independently rasterized with Poppler directly from `numeric_print_v3/` and visually inspected in this review. No source-face image or occluded-image pixels were accessed. Complete right-side colorbar labels are visible on every page, including the previously clipped MixFaceNet and SelfMAD color pages. P18 numerical annotations are now separated from bottom-axis ticks; the regional summaries do not collide with the colorbar. No clipping or overlapping captions was observed. Every PDF independently reports 510.236×595.276 points, equivalent to 180×210 mm within rounding, and Poppler's actual font specifications are >=8 pt. This is screen-rendered print-layout QA, not a physical printer proof.

The newly added captions explicitly explain the uncalibrated sigmoid score, three displayed rungs out of eight, native 64×64 patch before preprocessing, common full-set limits within each model and different scales across models, seam/control abbreviations, differing S3 versus S0/S4 surroundings, area/shape-only controls, remaining fill artifacts, one fixed host and no causal/population claim. They address the prior interpretation-context requests. Grayscale magnitude plus negative hatching remains distinct from signed color. Explicit measured 8×8 cells and geometry-fixed P18 remain visible; there is no smoothing or contrast enhancement. The pale Sb cells are retained.

Independently rehashed all **50 previously reviewed numerical/v2 files** selected by the preserved audit binding: every hash is unchanged. Independently verified all 30 current figure-file hashes and checked all 30 v3 unrounded display records against the already-admitted original response arrays: baseline logits, P18 occluded logits/deltas, seam/control means and scale maxima agree exactly. No inference or fresh occlusion computation was performed. The earlier numerical PASS for five complete 1024-view sweeps remains unchanged; neither failed MADation smoke gains a map or scientific conclusion.

Unchanged absolute limits: A 5.7325520515441895; B 6.336426734924316; Sb 4.423853039741516; MixFaceNet 12.020625531673431; SelfMAD 1.6233634948730469. The renderer source continues to use all eight rungs and both fills for the per-model scale. Raw magnitudes must not be used for cross-model performance comparisons.

The owner's detailed layout measurements (minimum page margin 2.7 mm, tick/P18 gap 2.0907 mm, regional-summary/colorbar clearance 11.858 mm) remain author-generated numerical layout evidence. I reviewed the corresponding source assertions and independently confirmed the visible separation and PDF dimensions/fonts, rather than claiming an independent rerun of Matplotlib geometry measurements. No required print repair remains for this numeric-only internal candidate.

## Exact bindings

- Prior independent numerical audit: `4e9930e74212f94f053c779e9702ff89d91790586acf25d5e637e101a71bb1c3`.
- v3 renderer: `1ce9e66dda7bbadd1cf2665b74b3657dfc19d2b791fff83e6702b70afde9585a`.
- v3 author QA source: `d81fdbd72035e599a2224203e889e72fe186705b861b5d565347bbfd8f6b1432`.
- v3 figure manifest: `cd5c409f562955df89191d1b39708f2521ae40e362988750b19f34af4024bf90`.
- Display values: `d36e2bde5ed16facee85184de850f44536e4e123789c38b425b4a733113a8519`.
- Poppler author QA: `edcfbd4b9faaf5153dd52319c99b9973250ae515eaf0c72dbaae726c3c75558d`.
- Matplotlib layout QA: `a9c0c4a950097252453362e909bbc1d81570797a914b5170d73cf0eaab536137`.
- Owner report: `fe6b540c50617b528cc3dee21f2c3232ec5a51b2fff94b02d178d2abf4304490`.
- New independent checks JSON: `86c5f9f3b956187b629e58d1590122f2bc4ddf661ae2c344afa77f963700a661`.

`PRINT_V3_INDEPENDENT_CHECKS.json` records all ten PDF hashes, dimensions/fonts and the source/manifest pins; `PRINT_V3_INDEPENDENT_CHECK_SOURCE.py` records the bounded check. Existing v2/v3 figures, responses, author sources, earlier review, main manuscript and WIP were not modified. No NEXT/SPRINT candidate or sealed output was opened, no model/checkpoint was loaded, and no job/retry was submitted. Source-face rights, user-requested original-face explanatory panels and publication remain separate HOLD dispositions.
