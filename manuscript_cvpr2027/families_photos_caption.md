# families_photos — caption and results-text draft

Status: COMMITTED (figures/families_photos.tex + figures/families_photos/*.jpg
at 791adef, not push). Compile proof: /tmp/famproof/proof.pdf.

File: `figures/families_photos.tex` + `figures/families_photos/*.jpg`
Data: native rows of the corrected MAD22 corpus
`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/`
(one shared, identity-matched contributor pair `001_03` vs `010_03`, present in all five families = 489 shared pairs).

## Proposed caption

> \textbf{Real examples of the five MAD22 morph families.} Each row shows one
> retained morph from the corrected benchmark (centre) anchored by its two
> contributor photographs (left/right), for the same contributor pair in every
> family: the landmark-warping pipelines show a blending halo ring and residual
> two-face superposition, strongest for FaceMorpher (whose released images also
> carry the Luxand generator watermark, shown unretouched) and mildest for
> WebMorph's blend plus shading transfer, while the GAN-based MIPGAN-I/II rows
> look photorealistic. Rows are illustrative, not a benchmark claim; images are
> from the MAD22 release used in this work. Selection is a single shared pair
> chosen because it is retained in all five families.

## Results-text paragraph (2–3 sentences)

> `fig:families_photos` shows what the five families actually look like: for one
> contributor pair retained in all of them, the warping families (FaceMorpher,
> OpenCV, WebMorph) leave the halo ring and the ghost of the second source
> between the aligned sources, with family-specific sharpness and shading
> histories, whereas MIPGAN-I and MIPGAN-II produce photorealistic faces whose
> shortcuts live in GAN fingerprints and sharpness rather than in blend geometry.
> The figure motivates the per-family aggregation of
> Table~`tab:mad22_results` (LM2 = mean(OpenCV, WebMorph); M4 =
> mean(MIPGAN-I, MIPGAN-II)) and the zero-EER saturation of FaceMorpher
> discussed in Section `sec:mad22_results`.

## IMPORTANT manuscript-scope flag (action for parent)

`main.tex` line 32 (abstract/teaser-related statement) reads:
"All glyphs are schematic and no real-face imagery is used."
That sentence is true only for the TEASER (`figures/teaser.tex`) and the
schematic `figures/families.tex`. The NEW figure `fig:families_photos` DOES use
real corpus (MAD22) imagery of two adults. **The no-real-imagery sentence must
be scoped to the teaser**, e.g. "The teaser glyphs are schematic and use no
real-face imagery; Fig.~\ref{fig:families_photos} shows real MAD22 corpus
images." This figure does NOT use minors and shows at most two people per row;
MAD22/FFHQ-derived release permits research use with attribution.
