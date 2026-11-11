# smad-next: shortcut-free S-MAD for CVPR

Planning repository, created 11 Nov 2026. It holds the evidence, the review, the hypotheses and the
plan for the last sprint before the 16 Nov submission. No experiment has been launched from it.

S-MAD = single-image morphing attack detection: deciding from one face image whether it blends two
people.

| File | Content |
|---|---|
| `01_EVIDENCE_DOSSIER.md` | What our experiments show about existing detectors and benchmark cues, per morph family, with sources and the limits of each claim |
| `02_REVIEW_AND_SHORTCOMINGS.md` | Review of the experiment record, the OpenCode session and the literature repository |
| `03_LITERATURE_AND_METHODS.md` | Literature on shortcut mitigation and identity-based detection; seven method designs with falsifiers |
| `04_HYPOTHESES.md` | Hypotheses in plain terms, each with a test that can fail |
| `05_RESEARCH_PLAN.md` | Workstreams, day-by-day schedule, gates, and what the paper says under each outcome |
| `06_RESOURCES.md` | Compute needed, rental recommendation, how rented machines are kept busy |
| `07_DECISIONS_NEEDED.md` | Decisions made, assumptions, open questions |
| `prereg/TEMPLATE.md` | One-page pre-registration form used for every experiment |
| `08_CUE_MATRIX.md` | Every candidate benchmark cue: where present, whether detector use was tested, status |
| `09_DATASET_EXTENSION_ANALYSIS.md` | What past data-extension runs show, gaps, minimum additions |
| `10_ASSET_INVENTORY.md` | Released detectors, corrected MAD22 location, generators, photo pools |
| `11_AUDIT_PLAN.md` | Audit experiments per morph family with fixed verdict rules |
| `NOTEBOOK.md` | Live state of every idea, one line each |
| `WORKFLOW.md` | Roles, review loop, spending and cluster rules |
| `prior/INDEX.md` | Index of all experiments before 11 Nov |
| `experiments/` | One folder per new experiment |
| `src/` | Empty; code goes here once the plan is approved |

Related repositories: `mambamorph-code` (experiments and ledger), `mambamorph` (paper),
`narolski/research` (literature).
