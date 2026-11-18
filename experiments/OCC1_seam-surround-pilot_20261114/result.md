# Actual occlusion pilot (OCC1): results awaiting independent review

Status: five complete, numerically author-verified sweeps; two failed smokes explicitly retained. **Independent post-result and print review pending; no finished user-facing panel or scientific conclusion.** Parent admitted exact-hash numeric-only in-place research. No source images/occluded images/face overlays exported; no new transformations beyond the authorized constant occlusion and standard unchanged preprocessing. No source pixels are stored in output NPZ.

| Model | Smoke | Full sweep | Full in-run seconds |
|---|---|---|---:|
| A, frozen seed403 | PASS | COMPLETE1024views |9.429|
| B, frozen seed403 | PASS | COMPLETE1024views |9.639|
| Sb, frozen seed403 | PASS | COMPLETE1024views |9.648|
| Official MADation ViT-B/16 | FAILED batch1/8parity | Not run | — |
| Official MADation ViT-L/14 | FAILED CUDA OOM duringmodel.to | Not run | — |
| Official MixFaceNet-MAD | PASS | COMPLETE1024views |6.773|
| Official SelfMAD, aligned-frame | PASS | COMPLETE1024views |15.519|

Each complete sweep contains all8fixed rungs,2fixed fills and64fixed native-grid patches:5120full occluded forwards in total, plus320completed smoke views. No failed smoke was rerun or followed by full inference. No tolerance, example, model, checkpoint, mask or fill changed. MADationB's failing numerical discrepancy/rung was not captured by its exception receipt and remains unknown. MADationL's allocation cause remains unknown. Neither is a scientific negative result.

Durable output root: `/mnt/t7/smad_next/OCC1/20261114/`. The full grids/raw scores are in each successful model's `_full/`; failure receipts in the two failed `_smoke/` directories. `baseline_scores.csv` has40rows, `regional_effects.csv`80rows, `paired_rung_effects.csv`50rows. `NUMERICAL_OUTPUT_VERIFICATION.json` SHA256 `193ec7ff4c57353b8bc79486abaf7028ff7f37659e610e48b2c8ee4d8e8495d8` binds all complete raw-file hashes and both failure dispositions. Author verification independently reconstructed CSV/NPZ delta identities, region means and paired-rung differences. Exact argv/stdout/stderr/return codes are retained in `execution_20261114.jsonl`, with initial A_smoke recorded separately in its start/result receipts.

Measured quantity is **Δz = z_occluded−z_original** for the attack-oriented noTTA logit; negative means less attack-like, not an error-rate change. Sigmoid values are uncalibrated model scores. Region17cells overlap the seam ring by>=10%, also removing other facial content. The17lexicographic surround controls match area/shape only, not texture/position. S4/S0share R2w4outside; S3outside is R2w. Both fills and every successful-model/rung response remain visible. One fixed development host cannot establish population effects, identity specificity, localization faithfulness or recipe improvement.

Print candidate revision2 at `numeric_print_v2/` supplies actual8×8tile maps and baseline/P18occluded logits for S0/S3/S4, color and grayscale, shared full-set range per model,180×210mm/minimum configured8pt. P18was fixed by geometry before scores. No source face is shown. Author checked A color and SelfMAD grayscale; all10SVGs passed mechanical font-size checks. PyMuPDF unavailable, so PDF font-span check was not run; representative PDF dimensions were verified with pdfinfo. Rejected overlapping-label revision1 remains preserved. All revision2figures still need independent print/interpretation review.

Recovery is not dispatched: parent has assigned `/root/astra_compute_unblock_plan` to plan MADationB parity and L OOM without improvised scientific changes, considering lem-gpu-interactive and permitted existing data access. Five complete sweeps must not be duplicated. Publication/source-image display rights remain a separate disposition. Full current owner handoff: `experiments/AGENTIC_delivery_20261114/FIGURES_OWNER_HANDOFF_20261114.md`.
