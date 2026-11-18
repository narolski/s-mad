# Independent private VIS1 figure review — 2026-11-14

Reviewer: Astra, independent of shortcut_visual_examples (author).
Decision: **GO_PRIVATE_PACKAGE_ONLY** for the exact panel together with caption_en.txt and manifest.json, under the existing root private-render grant. **PUBLICATION HOLD** remains. No must-fix identified for this scoped private presentation. This is digital print QA, not a physical-printer test, age certification, consent determination or public rights clearance.

## Exact binding

- PDF: `49ae8e4a86d8b667660c43adc4f2bbdfa3e59eb079f77c78fe1efeba6350d879`
- PNG: `59d5cb8d6bf5f8f74742c44c8f0df873c092c022ad7016fce6dc091e21ea44ac`
- SVG: `bbe47d41dc6eaa697afd318f8f60241dbd2b638e8dc32e7e1ced36aef7691102`
- Manifest: `3c0c8778c4db768aac962a88a6c24a3e272471e15c2613c0ffede21b07327b67`
- English caption: `074a13a7b77988f5cf607bde9f1698ecbb5d04f187d3489007a9948fc27828c5`
- Renderer: `e0f958cc36b9f4b12aa1b3be3858d58c96982bb09b182dac8d5ea7bb4a897039`
- Root private grant: `65f93232fe6439106a6555f54a5fd799eaa88e691bdae76b6016ee7f1a63f79d`
- Independent all-three-model numeric review: `ff9d1a19e2ad57ac1592803abc746314199c7f7b9d040ed641e86ad2181b5e81`
- Admitted RESULT JSON SelfMAD: `a0c7793f2596e6ddc6f653a0a6e971fcfb63dc6410bd8f66478ce274d12e1d7e`; A: `18c46b3d3fced82f6162bcd2a5542601a72a08739675aa7b0421e1d82fa5bc62`; B: `35fa6ad2f0a74c152ca8b8437d543942c06a51423fc15c0393fe90898d456214`.

Read AGENTS/CONTINUE, exact private grant and prior numerical review, author HANDOFF/OWNER_HANDOFF, caption/manifest, authorized local source replicas and admitted RESULT JSONs. `/home/narolski/smad-next/CLAUDE.md` was absent on this check; no manuscript changes were made. No actual inference, candidate archive, checkpoint, sealed benchmark, FERET image or reference00010 image was accessed. Existing numeric reference00010 metadata in the already-admitted JSON was not rendered or used for selection.

## Independent identity and arithmetic checks

The PDF has exactly four decoded 512×512 RGB images. All four pixel arrays match the authorized source copies; the SVG contains exactly their four original PNG byte streams. Verified input SHA256s:

- 42 native: `dbd11bb9c9545524c01eafd4d0f4e1478faa5aa9c9ca04d8f4643124f92592d1`
- 42 history: `a1e4c13cc32bba5450e3a9b36fa19a6e1fffa130907f0f62b18d2e0002207a97`
- 56 native: `c07df69f9421404b37f76d05d23242d0b5c25b9584dee273cf5973d467cf22fa`
- 56 history: `04629c855318c47c764bb6d5f84b5a41306203ba636bcdd511e298e77576fe16`

Verified every full-precision manifest logit, sigmoid score and delta against the hash-bound admitted model JSON; verified three-decimal formatting and actual PDF text. All six fixed pairs retained:

| Photo | Model | Displayed sigmoid before → after | Displayed logit delta |
|---|---|---|---|
| 42 | SelfMAD | 0.581 → 0.985 | +3.887 |
| 42 | A | 0.033 → 0.029 | −0.137 |
| 42 | B | 0.043 → 0.033 | −0.284 |
| 56 | SelfMAD | 0.177 → 0.396 | +1.114 |
| 56 | A | 0.031 → 0.030 | −0.036 |
| 56 | B | 0.033 → 0.030 | −0.091 |

All four A/B negative effects remain visible, with the same table hierarchy beneath both photographs. No selective omission. Null operational thresholds/decision flips verified in admitted JSONs. Different 224/384 model inputs and distinct logit units preclude robustness ranking.

## Print and layperson review

Independently rendered the actual PDF via Poppler at 150 dpi color/grayscale and 300 dpi grayscale. Personally inspected actual color and grayscale proofs. Actual page dimensions are 179.999993×280.000004 mm, one page; actual minimum font is 8.1 pt. Every PDF text character is within the page. No clipping, overlap, unreadable contrast or reliance on color to distinguish outcomes was observed in the 300 dpi grayscale print proof. Use the PDF at 100% physical size; reducing it can invalidate the minimum-font claim. SVG pixel fidelity passes, but font substitution in arbitrary SVG viewers is not independently certified; PDF remains the print master.

The headline and immediate paired portraits communicate the five-second message: the same source photograph can receive a different detector output after processing. The subtitle names resizing and alignment, not a single isolated cause. Nontechnical readers need not understand logits to compare before/after scores. An optional future explanatory gloss could call logit a raw internal detector value; this is not required for private display and must not turn it into a probability or threshold claim.

## Scope, interpretation and credits

Exact histories are correctly retained in the companion English caption and manifest: 42 is 1024→265→separate alignment512; 56 is 1024→249→separate alignment512. The panel explicitly states crops differ and the intervention combines resizing and realignment, neither JPEG-only nor blur-only. It does not prove an isolated blur/JPEG mechanism, identity causality, benchmark shortcut prevalence, utility, accuracy, population effects or decision flips. The two cases were fixed before their new scores; the caption discloses SelfMAD's earlier pilot-based demonstration choice and unknown full-training/person/component exposure. Treat these as potentially exposed development illustrations.

The displayed sigmoid is explicitly not an attack probability; no calibrated probability or decision threshold is asserted. Both fixed cases and all three models are included. No heatmap or causal localization is invented.

The package retains Rebecca Brown / “Shirtless, bearded Josh.” / FFHQ42 and RAFFI YOUREDJIAN / “MANGAGAN-7” / FFHQ56, both CC BY-NC 2.0, source Flickr URLs and license URL in caption/manifest; panel footer retains names/IDs/license/change description. Dataset-documentation BY-NC-SA 4.0 is distinguished from per-image licensing. **Keep caption and manifest accompanying private delivery: printed panel alone omits the full source URLs and exact intermediate widths.** Ages are only manually adult-appearing under the prior scope, not certified. OWNER_HANDOFF overstates that the literal adult-appearing qualification appears in the English caption: it does not; the manifest instead disclaims an adulthood claim. This does not grant adulthood/consent/publication clearance and is not a blocker to the existing narrowly authorized private package.

## Reproduction receipt

Independent verification script and VERIFICATION.json accompany this review in its independent_review subdirectory. Eleven Boolean checks pass: artifact hashes, grant, prior review, source hashes, four PDF pixel identities, four SVG PNG identities, six numerical pairs, displayed values in actual PDF text, bounds, minimum font and physical page dimensions. Proof hashes are included in VERIFICATION.json. Author sources and outputs were not edited. No scientific or public release is implied by this private presentation review.
