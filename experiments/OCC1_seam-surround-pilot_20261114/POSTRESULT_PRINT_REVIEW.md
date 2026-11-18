# Independent OCC1 numerical and print review

Reviewer: Astra, 2026-11-14. Scope: existing OCC1 admitted internal numerical results only. No inference, retry, source-face decoding/export, occluded-image reconstruction, checkpoint or NEXT/SPRINT candidate read was performed. The parent admission was checked before numerical access; it permits bounded numeric-only in-place internal research, explicitly not source-face/overlay export or publication clearance.

## Separate verdicts

- **Numerical: PASS for the five complete existing sweeps.** Independently recomputed 5,120 occlusion deltas from occluded minus baseline logits; verified complete 8×2×64 grids, finite values, per-patch CSV agreement and sigmoid scores, all 40 baseline CSV rows, 80 regional rows and 50 paired-contrast rows. Reconstructed seam and lexicographic surround membership from admitted geometric masks, obtaining 17 cells each and geometry-fixed P18 at native top-left (128,128). Independently checked all stored paired contrast maps and regional summaries. No population uncertainty or model-performance claim follows.
- **Interpretation: PASS only as qualified single-example descriptive sensitivity.** Signed logit changes, uncalibrated scores, two fills, one fixed development host, removal of other content by seam-overlapping squares, and area/shape-only controls are described correctly in result.md. Negative delta means less attack-like, not improved accuracy or proof of a causal identity cue. S3 uses a different surrounding image from S4/S0. Numeric maps are not faithful face-localization explanations; constant-mask artifacts remain possible. Failed MADation smokes are not scientific negatives.
- **Print: REPAIR REQUIRED for the current ten-page set.** All ten existing PDFs were rasterized in memory with Poppler and visually reviewed; all five color and five grayscale pages preserve visible measured 8×8 cells, two fills, S0/S3/S4, P18, logits and regional means. All PDFs are 510.236×595.276 points (180×210 mm to rounding), with actual Poppler font specifications of at least 8 pt. However, MixFaceNet color and SelfMAD color clip the rightmost vertical `Signed delta z` label. Move the colorbar/label inward and reserve a margin for the widest tick labels; rerender and inspect all ten pages. Several lower x ticks sit very close to the P18 text; adding vertical separation would improve readability. This is screen-rendered print-layout QA, not a physical printer proof.
- **Face rights / original requested panel / publication: HOLD.** Numeric-only panels do not fulfill the user's requested original faces and on-image explanations. Neither this review nor numerical PASS authorizes source FERET faces, occluded images, overlays, publication or further inference. Keep those separate release gates explicit.

## Figure fidelity and necessary caption context

The reviewed renderer uses explicit pcolormesh cells without smoothing or interpolation. Color is signed blue-to-red with zero-centered symmetric limits; grayscale uses absolute magnitude and hatching for negative cells. Each model's limit uses all eight rungs and both fills, although these print pages display only S0/S3/S4. Independently recomputed absolute limits are A 5.7325520515441895, B 6.336426734924316, Sb 4.423853039741516, MixFaceNet 12.020625531673431 and SelfMAD 1.6233634948730469. Consequently the almost-white Sb panels are not missing results. Raw logit magnitudes and colors must not be compared quantitatively between models.

Retain result.md's qualifications alongside any internal presentation. Add to the eventual standalone caption: `s = uncalibrated sigmoid(z)` (especially needed for the grayscale variant); limits are shared across all eight rungs/two fills within each model and differ between models; S3/S4 surroundings differ; only three of eight rungs are shown here. State native 64×64 patch area before model preprocessing rather than implying identical post-resize support. The underlying full response grids retain all eight rungs. Current numeric-only figures cannot support claims about where a facial identity cue is physically located.

## Failures and evidence preservation

MADation ViT-B/16 remains FAILED with `ValueError('batch1/batch8 baseline parity gate')`; its precise failed rung/discrepancy is not recoverable from this receipt. ViT-L/14 remains FAILED with a CUDA out-of-memory exception; no allocation-cause diagnosis is inferred. No corresponding full directory exists for either. Existing five full runs were not duplicated and no failed smoke was retried.

Independent executable audit: `ASTRA_POSTRESULT_AUDIT.py`. Numerical/manifest/font evidence: `ASTRA_POSTRESULT_NUMERICAL_CHECK.json`, SHA256 `4e9930e74212f94f053c779e9702ff89d91790586acf25d5e637e101a71bb1c3`. That JSON contains exact SHA256 hashes of every inspected raw NPZ, per-patch CSV, result receipt, aggregated CSV, both failure receipts, all 30 figure files and admission/source documents. No source-image files are included. The audit imported NumPy only for admitted response arrays and geometric masks, not any model.

Key exact bindings independently rehashed:

| Artifact | SHA256 |
|---|---|
| Parent admission | `9e1bd122966c6b9ac45984cdb3b6f0d9f25ba352d0e454ef6a48078270fd464c` |
| prereg.md | `e57b042df42fcfe6f0d261b2d7995d1d8699594638e39c72a4d15e11f57c484a` |
| INPUT_MODEL_PINS.json | `42f6f16c17a34b501dbb87ce98872186a6ffcb3510743a95ede29a9eda9057d4` |
| runner | `2d89d00054bdcae2a4f3f99b791b8af6280f702d3ea071a876b0307f8388776a` |
| numeric renderer v2 | `504582fdf39d975ac19db8b6180a0fa1769f35dbc6a8baf2cdbfd0ac4c36b886` |
| Figure manifest | `e44f8cf76ac4b810b14b3c54c63b36fcbf322c7f25302cf369a3e0b468b64272` |

No existing source, result, failure or figure was modified. Poppler's first XML inspection emitted an incidental numeric colorbar raster `numeric_print_v2/A_color-1_1.png`; this is a numeric-only derivative, not a source image and not a manifest figure. Subsequent XML checks used `-i` and all PDF visual renders streamed to memory. Preserve or remove this incidental derivative separately from the authoritative 30-file manifest; it is not evidence of another scientific result.
