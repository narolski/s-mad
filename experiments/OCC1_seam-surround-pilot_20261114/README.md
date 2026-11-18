# Seam/surround constant-occlusion pilot (OCC1): current record

14 November2026. User requested actual occlusion-response maps and score changes. **Five complete actual sweeps passed; two models failed smoke and were not swept. Independent post-result/numerical and print review remain PENDING. Do not present this as a finished user-facing figure.** Parent released exact-hash numeric-only in-place internal research after independent method/code GO. No source face pixels were copied, exported or saved by OCC1; no closed challenger/benchmark payload was accessed. Existing files and earlier experiments remain unchanged.

## Prepared package

- `prereg.md`: prospective fixed source/geometry/mask/fill/target/control plan.
- `INPUT_MODEL_PINS.json`, SHA256 `42f6f16c17a34b501dbb87ce98872186a6ffcb3510743a95ede29a9eda9057d4`: metadata-only candidate selection, exact8existing input and7checkpoint/source pins; no numerical outcomes read.
- `/home/narolski/smad-next/src/OCC1/occlusion_runner.py`, SHA256 `2d89d00054bdcae2a4f3f99b791b8af6280f702d3ea071a876b0307f8388776a`: numeric-only runner, original/occluded source pixels never saved. It independently enforces original source compositing, preprocessing equality, finite outputs, repeat/no-op and batch-size parity.
- `/home/narolski/smad-next/src/OCC1/prepare_inventory.py`: deterministic metadata/file-hash pinning, no decoded pixels/models/scores.
- `GEOMETRY_ONLY_PREFLIGHT.json`:106point metadata only, no image/model access. Candidate has17seam-overlapping64px cells,30pure-surround cells and6pure-interior cells; equal-count17surround controls available.

Synthetic test passed through the DGX interpreter under `-I`, thread limits2/nice10: exact4096pixel support; no source-array mutation; identical outside-mask pixels; identity-sham equality; linear-score signed delta; full64cell non-overlapping tiling. Independent reviewer reran it and inspected exact source/pins.

Candidate metadata: first lexicographic complete development host `feret:00026`, H/S from different sessions, other-person partner `feret:00140`. Inputs are existing R0/H, R2w, R2w4, R3, R4 and **same-R4-hull amendment7b** S0/S3/S4. Source pixels will be checked in place before any model score. The old S3 native-hull construction is not substituted. S4/S0 share R2w4 surround; S3 uses R2w surround, so all3surrounds are not identical.

## Independent review cautions and arithmetic correction

Reviewer: GO method/code at the hashes above, conditional on parent rights/admission release. Caption must say **seam-overlapping64px patches** (>=10% of native patch in ring), not isolated-seam erasure: the remainder of a patch can remove facial content. Lexicographically chosen surround controls match area/shape only, not content/position/texture. Two constant fills and same-rung/paired-rung comparisons diagnose replacement artifacts without eliminating them. No population or causal conclusion is authorized.

Workload correction to the initial prereg estimate: **7models×8rungs×64cells×2fills=7168occluded forwards**, not7728; smokes/baselines/no-op/repeats add extra forwards. This arithmetic correction changes no scientific input, mask, statistic or gate. Smoke is8fixedviews/rung for each model, then exact full128views/rung; output namespace is create-only and failures persist.

## Rights investigation and current boundary

The local complete release agreement found initially belongs to **Gray FERET2001**, while these inputs derive from **Color FERET**. The Gray document requires written image-release permission; it must not silently be treated as the complete applicable Color grant.

The current official [Color FERET source page](https://www.nist.gov/itl/products-and-services/color-feret-database) links the [Color release agreement](https://www.nist.gov/document/colorferetreleaseagreementpdf). Checked14Nov2026: access is case-by-case for face-recognition research; further dataset dissemination is restricted. Operative section2 discusses use in technical face-recognition documents, with at most15images/publication; section3 prescribes acknowledgement/citations. Its introductory approved-release language remains. These public terms do not establish the exact agreement accepted by this project or unrestricted image redistribution.

Consequently parent distinguishes existing internal research-input authority from image export/publication authority. Parent reports no separate written FERET publication permission. The recorded parent admission now releases **numeric-only, source-in-place** analysis under the user's explicit existing-project research authority; the runner refuses an inventory that enables source-pixel export. No original image/occluded image/face overlay is saved even in NPZ. Future face-containing figures require a separate documented disposition; current code cannot silently enable them. Private use is not invented as an exception to an applicable restriction.

## Licensed alternatives checked without outcome peeking

`/mnt/t7/smad_next/XF1/xf1b_rows.csv` has actual existing FFHQ two-person FaceMorpher, matched warp and source-host triplets (first metadata hostffhq:00290, partnerffhq:10472). These are genuine candidate display alternatives for a **narrower blend/warp comparison**, not complete S0/S3/S4same-person control coverage. Earlier one-photo FaceMorpher control was invalid as a same-person morph and must not be revived. MS1selected900source keys are disjoint from the existing FFHQ-Morphs attribution subset; individual attribution for those XF1keys was not found in the checked local records.

`/mnt/t7/smad_heldout/ffhq_morphs/licence/` has CCnoncommercial dataset terms and individual attribution for its4,000contributors/bona-fide references, plus existing face-spliced landmark_combined and landmark_complete images. No complete matched S0/S3/S4+warps for those licensed/attributed examples was established. The earlier image00010 genuine-history trio has no constructed splice seam and is unsuitable as a replacement seam example. A complete freely reproducible same-person panel would need documented additional display rights or a separately registered existing-image construction with legitimate same-person source photographs; no construction or transformation was performed here.

## Registered command (now executed under recorded admission)

After parent admission and independent GO, first model A smoke:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 \
 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/OCC1/occlusion_runner.py \
 --inventory experiments/OCC1_seam-surround-pilot_20261114/INPUT_MODEL_PINS.json \
 --model A --smoke --out /mnt/t7/smad_next/OCC1/20261114/A_smoke
```

Run from `/home/narolski/smad-next`; corresponding full namespaces were created only after smoke pass. The runner checked>=50GiB free, offline checkpoint loading, noTTA aligned-frame conventions and all source/model pins. Full output:8×2×8×8delta-logit grid, baseline/occluded raw logits and uncalibrated scores, masks/category/area metadata, paired regional/rung responses and all failed gates. No source-image arrays are included. Scientific conclusions and actual180mm/8pt print output need independent post-run review.

## Actual execution milestone

Admission receipt `PARENT_INTERNAL_RESEARCH_ADMISSION_20261114.json` SHA256 `9e1bd122966c6b9ac45984cdb3b6f0d9f25ba352d0e454ef6a48078270fd464c`; independent pre-run review SHA256 `e4494f0021934c90ff89f26348cf5ec9c073467893708060df4f633dab6ddb0f`. Before execution all three exact source/protocol/inventory pins passed, /mnt/t7 had155GiB-class free space (df155G), GPU was idle0% with no other compute PIDs. No rental/submission/cancellation occurred. Outputs are durable at `/mnt/t7/smad_next/OCC1/20261114/`.

- A/B/Sb, MixFaceNet and SelfMAD each completed64view smoke, then1024view full sweep;5120full occluded views total, plus320smoke views. Full in-run elapsed times9.429/9.639/9.648/6.773/15.519seconds respectively, excluding launch overhead. Every source-compositing, preprocessing, finite-score, no-op/repeat and batch-parity gate passed for these complete sweeps.
- MADation ViT-B/16 failed its smoke at the fixed batch1/batch8 parity gate. The receipt does not capture the failing rung or numerical discrepancy, so those details remain unknown. No full sweep or retry.
- MADation ViT-L/14 failed its smoke with CUDA OOM during `model.to(dev)`. Root cause unresolved; no full sweep or retry. A later read-only snapshot found no GPU compute PIDs,108GiB OS available memory and12GiB swap used; that does not establish the allocation state/cause at failure.
- All failures and unchanged execution argv/stdout/stderr/return codes are retained. No outcome-driven repair or tolerance change occurred. Missing model maps are explicit failures, not scientific negative results.

`NUMERICAL_OUTPUT_VERIFICATION.json` SHA256 `193ec7ff4c57353b8bc79486abaf7028ff7f37659e610e48b2c8ee4d8e8495d8` binds five full results and two failed-smoke receipts. The verifier reproduced exact CSV/NPZ delta identities,1024distinct cells/model, regional means and paired-rung differences; checked finite full grids and permitted NPZ keys with no source-image pixels. Summary files: `baseline_scores.csv` (40rows), `regional_effects.csv` (80), `paired_rung_effects.csv` (50). These are descriptive single-host data, not population inference.

Print candidates `numeric_print_v2/` contain five model-specific color and grayscale figures, each180×210mm with configured minimum8pt text, actual8×8tile values, shared per-model range across all8rungs/twofills, original/P18occluded logits and regional means. Source photographs are withheld. P18 was the first seam-overlapping cell fixed by pre-score geometry, not selected by score. The10actual SVGs were mechanically checked for minimum8text units and page geometry; representative PDF page size180×210mm was verified with pdfinfo. PyMuPDF was unavailable, so PDF font-span QA was not run. Author visually inspected A color and SelfMAD grayscale v2. Independent numeric/interpretive/print review remains required. Initial `numeric_print/` v1 had overlapping text and is retained as a rejected layout; use v2 only for review.
