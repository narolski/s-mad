# Loose documents in mambamorph-code/experiments/

Documents that sit beside the per-experiment folders. Written 11 Nov 2026 from the first lines of each file. "Superseded" means a later file or the file's own text says so; where I could not confirm that, the line says "not verified". All paths are relative to `mambamorph-code/experiments/`. Dates are 8 to 10 Nov 2026 unless noted.

Terms (explained once): **ABC / A, B, C** = training arms (SMDD alone, plus genuine photos, plus our classical morphs). **CG, CD, CGD** = further arms that add GAN morphs, diffusion morphs or both. **primary80fit / primary120fit** = classifier studies with 80 or 120 fits. **A/A replay** = running the same training step twice to test repeatability. **TMPDIR** = node-local scratch storage on the cluster. **Prereview** = independent review before a run; **post-result review** = after it.

## Conclusions and ledger tooling

| File | What it is | Superseded? |
|---|---|---|
| `CONCLUSIONS.md` | Plain-English findings page, last committed 10 Nov (working copy has later edits). Snapshot of the committed version: `prior/CONCLUSIONS_snapshot.md`. | Current; the 11 Nov research loop is not yet in it |
| `CONCLUSIONS.md.bak-a36`, `.bak-a43reg`, `.bak-a47reg` | Backups taken before A36, A43 and A47 registrations. | Superseded by `CONCLUSIONS.md` |
| `README.md` | Ledger conventions: one folder per experiment, the ledger documents and never decides. | Current |
| `build_site.py` (+ `.bak-a43reg`, `.bak-a45reg`, `.bak-a47reg`) | Script that validates entries and builds `site/index.html` and `site/conclusions.html`. | Current; backups superseded |
| `dates.json` | Milestone dates (A10 read embargo, author sync, W3 freeze, end of experiments). | Partly stale: lists 2 Nov as target end of experiments |
| `plan_dla_Kamila_2026-11-08.html` | Polish-language plan page for closing the CVPR experiments, written for the co-author. | Superseded by later plans; not verified |
| `site/` | Generated HTML pages (results, conclusions, reproduction checklists). | Generated; regenerate, do not edit |

## A49 and A50 and shortcut-mitigation planning (8 Nov)

| File | What it is | Superseded? |
|---|---|---|
| `DINOv3_P1_PLAN_20261108.md` | Plan for the DINOv3 constrained-adaptation study (became A49). | Superseded by `A49_dinov3/` |
| `A50_ABC_PROSPECTIVE_PLAN_20261108.md` | Proposal for the 20 missing B/P controls. | Superseded by `A50_EXECUTION_20261108.md` and `A50_RESULTS_20261108.md` |
| `A50_EXECUTION_20261108.md` | Execution record: production admitted for 20 B/P fits. | Superseded by the results file for outcomes |
| `A50_RESULTS_20261108.md` | A50 result: modest capped effects. | Current (see `prior/summaries/A50.md`) |
| `ABC_COVERAGE_AUDIT_20261108.md` | Audit of which A/B/C cells already existed; says reuse, do not relaunch A12.4 to A12.7. | Current |
| `SHORTCUT_MITIGATION_PROSPECTIVE_PLAN_20261108T213558_CET.md` | Plan for a cross-architecture processing-consistency study. | Superseded in scope by the four-model, 120-fit design (`primary120fit/`) per `LITERATURE_TO_DESIGN_ADDENDUM_...`; not verified in full |
| `SHORTCUT_MITIGATION_COVERAGE_AUDIT_20261108T213558_CET.md` | Companion audit of architecture and baseline coverage. | Same as above |
| `LITERATURE_TO_DESIGN_ADDENDUM_20261108T214710_CET.md` | Design checks; fixes the model scope (ConvNeXt-T, VMamba-T, DeiT-S, DINOv3-L/16) and says it supersedes older 120/150-fit scope. | Current for scope |
| `AUTONOMOUS_CONTINUATION_20261108.md` | Author authorisation for automatic follow-up when results arrive. | Current standing rule |
| `WCSS_CONCURRENCY_AUTHORIZATION_20261108.md` | Author removed the four-job concurrency limit on WCSS. | Current; supersedes earlier runbooks |

## Data expansion and generation (8 Nov)

| File | What it is | Superseded? |
|---|---|---|
| `DATA_EXPANSION_FOUR_MODEL_PILOT_20261108T214911_CET.md` | Proposed four-model by GAN and diffusion data-expansion pilot; asset-blocked. | Superseded in part by the generation-readiness file |
| `DATA_EXPANSION_ASSET_INVENTORY_20261108T214911_CET.md` | Inventory: 3,000 GAN morphs exist (A28); our two-identity diffusion training pool was not located. | Possibly stale (a pool was later generated, see research loop); not verified |
| `OWN_DIFFUSION_GENERATION_READINESS_20261108T215848_CET.md` | Readiness for building our own diffusion pool; production not released. | Current at 8 Nov; not verified since |
| `PRIMARY80FIT_EXECUTION_READINESS_20261108.md` | Handoff for the 80-fit classifier package. | Superseded by the 120-fit package (`primary120fit/`) |

## MAD22

| File | What it is | Superseded? |
|---|---|---|
| `MAD22_WORKING_DECISION_20261108.md` | Author decision to use the 185 genuine and 4,069 morph subset as best confirmed. | Current |
| `MAD22_missing_from_both_downloaded_ZIPs_20261108.txt` | List of 433 missing MAD22 files. | Current |

## Independent reviews (all 8 to 9 Nov)

| File | What it is | Superseded? |
|---|---|---|
| `INDEPENDENT_REVIEW_A44R_A45_20261108.md` | A44R accepted with qualifications; A45 corrections required (reproduction failed, stray p-values). | Current; fixes stale A44 and A45 ledger entries |
| `INDEPENDENT_REVIEW_A46_20261108.md` | A46 corrections required. | Partly superseded by the corrective review and RGB-only review |
| `INDEPENDENT_REVIEW_A46_CORRECTIVE_20261108T152840_CET.md` | Go with fixes for a separate RGB-only secondary evaluation. | Superseded by the RGB-only post-result review |
| `INDEPENDENT_POSTRESULT_REVIEW_A46_RGB_ONLY_20261108T161539_CET.md` | RGB-only correction accepted with qualifications. | Current for A46 |
| `INDEPENDENT_REVIEW_A47_20261108.md` | A47 accepted with qualifications. | Current; fixes stale A47 ledger entry |
| `INDEPENDENT_PREREVIEW_A50_20261108.md` | Go with fixes for the A50 design. | Superseded by the A50 post-result review |
| `INDEPENDENT_POSTRESULT_REVIEW_A49_20261108T203455Z.md` | A49 reported faithfully; registered primary failed. | Current |
| `INDEPENDENT_POSTRESULT_REVIEW_A50_20261108T213134_CET.md` | A50 accept-qualified. | Current |
| `INDEPENDENT_PREREVIEW_SHORTCUT_MITIGATION_20261108T214152_CET.md` | Go with fixes for design, no go for production. | Superseded by the primary120fit reviews |
| `INDEPENDENT_PREREVIEW_PRIMARY120FIT_514c7d1_20261108T220512_CET.md` | Go with fixes for six-arm preparation and a timing smoke. | Superseded by the final executable review |
| `INDEPENDENT_FINAL_EXECUTABLE_REVIEW_PRIMARY120FIT_20261108T223402_CET.md` | Conditional go; launch ABC60 first once gates pass. | Superseded by the operations reviews for release status |
| `INDEPENDENT_ABC60_OPERATIONAL_DELTA_REVIEW_20261108T225844_CET.md` | Design accepted, not released; one accounting bug to fix. | Superseded by operations v2 and v3 reviews |
| `INDEPENDENT_OPERATIONS_V2_REVIEW_20261108T232656_CET.md` | Conditional go; one missing-field check left. | Superseded by v3 |
| `INDEPENDENT_OPERATIONS_V3_NARROW_REVIEW_20261108T234122_CET.md` | Code accepted for the v3 delta; production not released. | Superseded by the physical-release review |
| `INDEPENDENT_PHYSICAL_RELEASE_REVIEW_20261109T000655_CET.md` | Accepts a read-only node-OS exception; production still awaited approval. | Current at 9 Nov; ABC60 closed 10 Nov |
| `INDEPENDENT_TMPDIR_AUDIT_20261108T224038_CET.md` | Polish-language audit of node-local staging: PASS for one job, unverified for all runtime paths. | Current; evidence in `TMPDIR_AUDIT_EVIDENCE_20261108T224038_CET.txt` |
| `TMPDIR_AUDIT_EVIDENCE_20261108T224038_CET.txt` | Raw cluster output behind that audit. | Current |

## Folders without a ledger entry

| Folder | What it is | Superseded? |
|---|---|---|
| `A49_dinov3/` | A49 plan, readiness, registration pins and result. | Current |
| `primary80fit/` | Code for the 80-fit classifier package. | Superseded by `primary120fit/` |
| `primary120fit/` | 120-fit design and the ABC60 production, recovery and closure material. | Current for ABC60 |
| `NARROW_DIVERSE_PILOT_20261108T215424_CET/` | Proposal and CPU validation for a 20-fit narrow-versus-diverse generator pilot. | Not run as far as recorded; not verified |
| `own_diffusion_readiness_20261108/`, `own_generation_v1/` | Audit script and the pool builder for our own GAN and DiffAE training data; builder blocked pending review at 8 Nov. | Not verified since |
| `dataaudit/` | MAD22 acquisition state and inventories (one dated folder, 9 Nov). | Current |
| `research_loop_20261111/` | Evidence snapshot of the 11 Nov research loop (Astra, DiffAE ROI, GAN32). | Current; see section 7 of `INDEX.md` |
| `STAGE_tmpdir-staging/`, `_template/` | Ledger stubs: staging plan, blank template. | STAGE not run; template is a template |

Not listed: experiment folders whose names carry a sealed-data marker; they were not opened.
