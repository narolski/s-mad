# Concrete shortcut visual examples — first bounded handoff

Status: private illustrative catalogue ready; publication selection and new computation remain review-gated. Nine exact metadata-selected cases and every source path/hash/model pin are in SHORTCUT_VISUAL_EXAMPLE_MANIFEST.json. No new detector inference, attribution, scientific reader, candidate/sealed scores or checkpoint contents were accessed. Only already-admitted XAI result JSON summaries were interpreted; image-byte hashes and dataset/source metadata were read. Existing OCC1 source faces were never exported.

## What should be understood in five seconds

Show the same face twice, a visible controlled change, and the actual detector response. Maps are secondary. Main labels: “Co zmieniliśmy?” / “Jak zareagował detektor?”; English “What changed?” / “How did the detector respond?”. Do not lead with model/layer/experiment acronyms. Headline: “Ta sama osoba. Zmieniliśmy tylko obraz.” / “Same person. We changed only the image.” Same-person controls do not automatically satisfy document acceptability.

## Hero available now, with a critical scope limit

FFHQ00010 (IDs fq005000/fq005001): the source photograph and its existing landmark_complete resampling/storage-history counterpart. It was fixed lexicographically before the original pilot scores; choosing SelfMAD for the hero after seeing its response is explicitly post-hoc illustrative model selection. The independently reviewed SelfMAD response is logit −1.690469622612→+2.109729290009, sigmoid model score0.155714079738→0.891845226288. No second contributor was added. Scores are not calibrated attack probabilities, and no approved operational threshold is bound for this illustration. Therefore the preview shows score change, not an accept/reject verdict. Do not imply “the model is89% sure”. The transformation combines resampling/processing history: it does NOT isolate JPEG, blur, compression or resolution as the unique cause.

Private face-containing preview: /mnt/t7/smad_next/VISUAL_EXAMPLES_20261114/hero_private_review.png (1600×1120; 180mm target width, smallest26px text≈8.29pt; inspected visually). It reuses exact existing image bytes at native512px display, no generated faces/maps or new source transformation. It contains no new heatmap because the immediate visual argument is the controlled image plus actual score. Local copy: work/shortcut_visual_examples/hero_private_review.png. Do not show it as a completed publication figure. The source visibly depicts a child; despite documented CC BY-NC2.0/Anjul Sahu attribution and earlier private descriptive display admission, a publication likeness/privacy disposition is unresolved. Prefer an adult-source replacement after source/consent review and new prospectively fixed scoring, rather than treating image licence as consent.

Mandatory counterexamples travel with the hero: A_s403 on the SAME photo/history has Δlogit−0.00890, while SelfMAD's border-only counterpart has onlyΔlogit+0.15750. MixFaceNet changes by+13.00903 under history but remains at very negative logits: a large numeric response need not cross a decision boundary. All seven already-reviewed models/three conditions are preserved in the manifest, including Sb's approved FP64 repair. This hero is not typicality evidence, a robustness ranking, proof of a facial region, or a new benchmark result.

## Nine exact candidates, selected without score fishing

| Cases | Specific sources | Why selected / what is available | Missing before publication |
|---|---|---|---|
| Existing history,3 cases | FFHQ00010,00042,00056; original and landmark_complete resmatch pairs; exact IDs/paths/attribution in JSON | First three lexicographic attributed bona-fide keys. Existing pilot numbers/maps only for00010; effects for00042/56 unknown.00042 is preferred adult-source candidate subject to actual review, not an inferred identity/consent fact. | New fixed scoring for2other cases; geometry/rights/person-overlap review. Author-specific CC BY-NC2.0 credits are present for all3. |
| Rendering/blending/surround,3 cases | XF1hosts65572→65542,30319→34314,63202→33222; each Hwhole/WARPwhole/FMHBwhole/WARPface/FMHBface | Exact25/50/75% ranks in299hosts ordered by excl_border thenhost, floor((n−1)q); not score quantiles. Morph/warp face vs whole comparisons can expose surround sensitivity. Existing aggregate XF1 is admitted; individual response has NOT been extracted. | Per-image attribution absent in checked local4000-key attribution list for these contributors; retain export HOLD, locate full official FFHQ metadata. Do not borrow00010's licence or maps. Whole vs grey-face blanking is a substantial distribution change. |
| Seam/surround,3 cases | OpenCV development hosts FERET00026→00140,00107 and00146 (partners in JSON); exact same-hull S0/S3/S4 | First3lexicographicdevhosts with allthreeexistingnative controls. Only00026 already has real admitted OCC1 grids for5models; other2have no newly-read scores/maps. | FERET source-pixel export/publication HOLD. Other2need new registered in-place numeric sweeps. Same-personS3 has different surround fromS0/S4; retain R2w/R2w4 references. |

These geometry/lexicographic cases are input-representative strata, not known typical detector responses. A “typical” response must be established against the entire registered population, or labelled unknown. Do not rename a convenient failure as a statistical counterexample. No benchmark image, sealed score or seed selection is needed.

## Separate the unsupported categories

Resolution versus blur must be isolated by a new matched factorial test. Storage-history is not JPEG-only. The current catalogue has no already-verified pure-JPEG decision flip and no causal random-face-part shortcut. Label these panels “not yet computed”; do not create plausible explanatory maps or insert aggregate rates next to an unscored face. AD4's morph-free native MorDIFF separation is strong admitted population evidence for processing-cue sufficiency under its pipeline; the nine faces above are NOT its training examples or per-image benchmark proof.

## Concrete captions

Hero PL: “Nie dodano drugiej osoby. Po istniejącym przetworzeniu tego samego zdjęcia wynik SelfMAD wzrósł z0,156 do0,892. Wynik nie jest prawdopodobieństwem; pojedyncza ilustracja, historia łączy kilka operacji.”
Hero EN: “No second person was added. An existing processing-history variant of the same photo changes SelfMAD's score from0.156 to0.892. Uncalibrated score; one illustrative example; several processing operations are combined.”
Seam PL/EN: “Ten sam szew, inny kontekst: pokazujemy zmianę wyniku po zasłonięciu fragmentu obrazu.” / “Same seam, different context: measured score changes under patch occlusion.” Append the unequal-surround/64pxmask/onehost/twofills caveats, not “the network recognizes the seam”.
Layer panel PL/EN: “Czy z reprezentacji da się odczytać sposób przeskalowania?” / “Can resize history be decoded from the representation?” A second panel must ask “Czy detektor wykorzystuje tę informację?” / “Does the detector use that information?”. Decoding alone cannot answer the second question.

## Next action

Root may route the exact catalogue and preview for independent evidence/rights/print review. Best short path: inspect source00042/00056 and exact history bytes, resolve overlap and publication likeness/licence conditions, freeze a small whole-population response census plus the illustrative cases, then obtain independent pre-run GO. Keep00010 as private proof-of-concept with its existing single-case limitations. Separate storage/JPEG panels and approved numeric OCC1 remain separate. Do not integrate any preview into main yet.


Vector companion: /mnt/t7/smad_next/VISUAL_EXAMPLES_20261114/hero_private_review.svg (180×126mm, exact input PNGs embedded; font min8.29pt). PREVIEW_RECEIPT.json records file hashes, numeric source and private/privacy scope. PNG visually checked; vector companion has not been independently rasterized, so no vector print GO claimed.
