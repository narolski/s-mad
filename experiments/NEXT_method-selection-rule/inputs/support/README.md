# Support metadata for next method selection

This separate pre-read extension supplies criterion (b)–(f) definitions for the approved version 3 rule. The previously committed 44-pin detection package is unchanged. `support_v3.json` contains development manifest selections and fixed metadata derived from the reviewed RZ1, AB1, C2P and TT1 reader functions. No candidate result, archive, image or checkpoint was accessed, and no model was fitted.

`src/NEXT/prepare_support.py prepare` imports only those reader definitions and calls their manifest/pool functions. It reproduces the exact storage pairs, development same-person splice and border pools, seven primary TT1 families, kernel cross-table pools, expected training metadata and refit provenance. The extension has its own `pins.sha256`: support JSON, preparation/verification code and every source manifest/reader/registration used, twenty entries. `verify` checks the pins and source hashes; `verify --require-clean` additionally requires the repository inputs and code committed in a clean tree. This is input verification, not full result-read admission.

Verified structural counts:

| Pool | Count |
|---|---:|
| Native/stored photo pairs, fm61 | 291 |
| Native/stored photo pairs, amsl112 | 290 |
| Native/stored morph pairs, fm61 | 150 |
| Native/stored morph pairs, amsl112 | 149 |
| Development same-person splice S3 | 100 |
| Border-blanked development camera rows | 1,582 |
| MEDS primary rows / person groups | 865 / 400 |
| Kernel genuine / morph rows | 7,257 / 1,000 |

The seven primary TT1 family counts are replay_attack 200, msu_mfsd 65, oulu_npu 989, casia_fasd 150, lfw_calfw 10,973, cfp_ff 4,725 and agedb_30 3,933. LFW and CALFW are concatenated into one family exactly as in the reviewed reader. The mean across seven families weights families equally, rather than pooling images.

## MEDS privacy and bootstrap order

The original private MEDS metadata is not copied into the repository. Its exact path and SHA256 are pinned. `meds_primary` contains `row_index` (zero-based position in the **full** original `meds_manifest.csv`, before the aligned-primary filter) and an opaque person group `pNNNNNN`. The `id` order of the full private manifest was verified equal to the scorer's full `meds_score.csv` order.

The person group is the rank of the original person key among sorted primary-person keys, padded to preserve lexical sort order. This preserves the original person-bootstrap draw order while exporting neither original row IDs nor subject identifiers. The reader resolves each row index to its score ID privately, checks the pinned manifests before candidate access, and emits aggregate statistics only. The required MEDS bootstrap is 2,000 draws with default_rng(20261125), not the detection component bootstrap's seed.

## Reader integration and limits

Both pin sets must be committed and verified before an applicable challenger result is opened: `../pins.sha256` for detection, and this folder's `pins.sha256` for support. The strict selection reader must refuse incomplete or drifting metadata and still verify per-arm fit/platform/gate provenance.

The fixed plain-storage control is Δflag ≥ 0.05 and positive Δmean/native sample SD; H-new-1 falsification requires stored-minus-native morph shift ≥ −0.10 native-photo SD on at least four seeds at both sizes. These definitions are source metadata, not observations that a control or challenger passed. Own-rule flags use logit > 0. RZ1 refit mappings and expected pack hashes are included, but do not stand in for the gate receipts.

This extension initially serves the native RZ1 adapter. SbFM/GX/DINOv3 loaders require their own complete registered provenance and supplemental inputs; no adaptation or eligibility is implied by the shared metadata. Interior-crop and mixed-512 kernel ruling/registration requirements remain unchanged.

Commands, using the existing environment and thread caps:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/NEXT/prepare_support.py prepare
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/NEXT/prepare_support.py verify
```

Preparation assertions and all twenty pins passed. Independent review and a clean-tree commit are still required before result admission. No cluster action or git commit was performed by the preparation agent.
