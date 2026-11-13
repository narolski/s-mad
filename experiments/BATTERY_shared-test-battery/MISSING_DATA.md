# Shared test battery (BATTERY) v1: audit rows that need data that does not exist yet

For the DATA role, through the lead. Written 13 Nov 2026. Rows and names follow the shortcut audit table (SA1,
`experiments/SA1_shortcut-audit-table/result.md`). "Battery v1 prints" = what `battery.read` shows for that row now.

| Audit row | What is missing | Why the battery needs it | Battery v1 prints |
|---|---|---|---|
| 3. JPEG history | A development JPEG pack: the same genuine photos native and re-saved as JPEG (for example the 191 test-ladder R0 photos and the 300 MS1 FFHQ hold-out photos at JPEG 90/70/50 with the registered `degrade()` branch, imported unchanged), with a manifest pairing each copy to its native photo. | No development JPEG pool exists; the only JPEG pools read for our arms are FRLL (benchmark, exposure only). Re-encoding evaluation images is an author item: the author builds the pack, agents only score it. | "not measured by the battery" |
| 16. Expression / capture detail | An aligned and packed paired expression pool: G11 found CFD 158 persons and KDEF 70 persons with neutral and happy images (`experiments/SA1_shortcut-audit-table/g11_expression_pool.json`). Needs alignment of the happy images with the unchanged aligner, a manifest pairing neutral and happy images by person, a registration and the lead's approval. | Expression is a benchmark cue only for FRLL; low priority for the protocol claim, but the row is empty for every arm. | "not measured by the battery" |
| All rows, arms trained on new sources | A person and source table for every battery set (dev, tt1, meds, gd): for each row, the persons in it and its source, in `DATA_CATALOG.md` form. | The sets are development data for the arms registered so far (FRGC/colorFERET split, FFHQ development designation, TT1 and MEDS sources unseen in training). An arm trained on other sources (for example the three-source arm, which trains on FFHQ, or GAN morphs from GX1) can have training persons or sources inside a battery set. Without the table the battery cannot mark such rows as in-source, as SA1 does by hand ("FFHQ is a trained source for SbM3"). | nothing (no in-source label yet) |
| 13 and 14 for arms with other training persons | The same host list check for the GD sets (DG1 DiffAE ladder on PN1 test hosts; AG1 MIPGAN controls on persons outside PN1 training) against each new arm's training persons. | GD rows were chosen to exclude PN1 training hosts; a new manifest may not. | the GD statistics, without an overlap check |
| 2. Storage of morphs, 5. border, 10. crop path for a second engine | Optional: the AB1 border rows and the FaceMorpher splice rows (`AB1/x/manifests/ab1x_eval.csv`) are not yet battery sets. They exist; adding them needs only a set entry and a reviewed reader pin (AB1X/AB1FM readers). | Not missing data; listed so DATA can enter them in the catalogue. | not in v1 |

Not data, but needed before the corresponding read:

- DINOv3 backbone: the BB2 overlay's `archs_a12.py` sha256 and a DINOv3 reference network per scoring platform (owner of
  the second backbone, BB2).
- A100 PCIe scoring: a smoke of the battery on a rented A100 PCIe 40 GB (driver uploads the four packs and the reference
  tar `PN1_Sb_s403.tar`).
- Row 15 (training-partner trace) is a manifest audit owned by SA1 (`src/SA1/g9_partners.py`), and row 11 (data volume)
  is a between-arm control; neither is a per-network statistic, so the battery does not compute them.
