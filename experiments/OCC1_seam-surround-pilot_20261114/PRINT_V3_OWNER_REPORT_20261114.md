# OCC1 numeric print repair v3 — owner handoff

2026-11-14, source/QA snapshot at 17:00:53+01:00 (gx10-c326 clock). **Author QA passes all ten v3 PDF pages; independent print reapproval PENDING.** This is a numeric-only layout repair, not completion of the user's requested figure with original faces/on-image explanations. Face/overlay export and publication rights remain HOLD. Main/WIP/manuscript files were not changed.

## Response to the independent review

Read `POSTRESULT_PRINT_REVIEW.md` and its pinned numerical audit `ASTRA_POSTRESULT_NUMERICAL_CHECK.json` (SHA256 `4e9930e74212f94f053c779e9702ff89d91790586acf25d5e637e101a71bb1c3`). That review independently passed the existing five sweeps of 1,024 views and 30 v2 figure hashes, but required print repairs.

Changes are confined to the new renderer and output directory:

- Moved colorbar/vertical label inward from normalized x=.925 to .86, reserving space for the widest ticks and complete `Signed delta z` label, including MixFaceNet and SelfMAD color pages.
- Increased tick-to-P18 separation; reflowed row heights/spacing and shortened the regional label to `Mean delta S/C`, with the abbreviation explicitly defined in the footer. No numeric value or rounding changed.
- Retained 180×210 mm, all fonts >=8 pt, explicit 8×8 measured cells, signed color and grayscale magnitude/negative hatching, P18 fixed before scores, and the common scale across all 8 rungs and both fills within each model.
- Added the review's standalone context to every page: `s = uncalibrated sigmoid(z)`, three of eight rungs displayed, native 64×64 patch before preprocessing, limits shared across the full set within each model and differing between models, differing S3 versus S0/S4 surrounds, area/shape-only controls and residual fill artifacts.

No model inference, scheduler operation, checkpoint load, source-image decode/export, SPRINT/NEXT payload access, or new occlusion/scoring occurred. Only already-admitted OCC1 numerical artifacts were read. No source face or overlay appears in the outputs.

## Exact candidate and sources

Candidate: `/mnt/t7/smad_next/OCC1/20261114/numeric_print_v3/`.

Ten pages: A, B, Sb, MixFaceNet and SelfMAD, each color and grayscale, in PDF/SVG/PNG (30 authoritative figure files). The same two MADation failed-smoke dispositions remain explicit; no maps were invented or retried.

| Artifact | SHA256 |
|---|---|
| `src/OCC1/render_numeric_v3.py` | `1ce9e66dda7bbadd1cf2665b74b3657dfc19d2b791fff83e6702b70afde9585a` |
| `src/OCC1/qa_numeric_v3.py` | `d81fdbd72035e599a2224203e889e72fe186705b861b5d565347bbfd8f6b1432` |
| `numeric_print_v3/FIGURE_MANIFEST.json` | `cd5c409f562955df89191d1b39708f2521ae40e362988750b19f34af4024bf90` |
| `numeric_print_v3/DISPLAY_VALUES.json` | `d36e2bde5ed16facee85184de850f44536e4e123789c38b425b4a733113a8519` |
| `numeric_print_v3/MPL_LAYOUT_QA.json` | `a9c0c4a950097252453362e909bbc1d81570797a914b5170d73cf0eaab536137` |
| `numeric_print_v3/POPPLER_PRINT_QA.json` | `edcfbd4b9faaf5153dd52319c99b9973250ae515eaf0c72dbaae726c3c75558d` |

The renderer binds the independent audit, verifies 50 reviewed numerical/v2 files against its exact recorded hashes before and after rendering, and asserts the five scale maxima exactly. `DISPLAY_VALUES.json` preserves unrounded source numbers behind the unchanged displayed rounding. All v2 files, original responses/scores and their recorded hashes remain unchanged.

Unchanged absolute limits: A 5.7325520515441895; B 6.336426734924316; Sb 4.423853039741516; MixFaceNet 12.020625531673431; SelfMAD 1.6233634948730469. The pale Sb cells are retained without artificial contrast enhancement.

## All-ten-page QA completed by the author

- Actual Poppler `pdfinfo` and XML font inspection on all 10 PDFs: 180×210 mm to rounding; minimum actual font specification 8 pt.
- All visible Matplotlib text bounding boxes within the page, minimum page margin 2.7 mm across the ten figures; no right-label clipping.
- Minimum tick-to-P18 text gap 2.0907 mm; minimum regional-summary-to-colorbar clearance 11.858 mm. Numeric captions no longer crowd the colorbar.
- All ten actual PDFs were rasterized to 150 dpi proofs in `numeric_print_v3/qa_pdf150/`; author visually inspected all ten color/grayscale pages. Complete `Signed delta z` and `Absolute delta z` labels are visible, including the two previously clipped color pages. Text, hatch sign and measured grid remain readable in the screen-rendered print-layout check.
- No physical printer proof is claimed. These are author checks, not independent approval.

Validation history: an initial author-layout draft was preserved as `numeric_print_v3_author_draft1/` after shortening the regional annotation for additional colorbar clearance. Its paths/manifest are historical, not the current candidate. An initial QA helper invocation stopped before PDF checks due to a string-versus-Path helper error; the helper was corrected and all ten final PDFs were checked successfully. This affected no numerical data, v2files, inference or scientific gate.

Commands from `/home/narolski/smad-next`, with OMP/OpenBLAS/MKL/NumExpr thread limits of 2 and `nice -n 10`:

```bash
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/OCC1/render_numeric_v3.py
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/OCC1/qa_numeric_v3.py
```

Both final commands exited 0; source/output paths are create-only. Do not rerun into an existing output directory or replace preserved v2/data.

## Required independent recheck

Re-engage the author-independent reviewer for the ten canonical v3 PDFs and their 150 dpi proofs, sources and manifests. Verify the clipped-label repair, tick/P18/summary spacing, 180 mm/8 pt font checks, exact preservation of data/display values/scales and v2 hashes, and the added caption qualifications. Prior numerical PASS applies to unchanged data; this step needs a new **print** disposition. Return a separately pinned print GO/GO_WITH_FIXES/NO_GO. Original-face figure/publication remains HOLD regardless of numeric print approval.
