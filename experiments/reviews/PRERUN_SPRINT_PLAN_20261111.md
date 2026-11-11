# Pre-run review of the sprint plan (audit experiments AR1-AR7, AD1-AD5, AG1-AG5 and the TwinMAD method), by the experiment-reviewer subagent, 11 Nov 2026, 13:43 to 13:48 CET
Verdict: GO WITH FIXES (fixes F1 to F6). Final report copied verbatim below from transcript agent-abddeb219d2e716de.jsonl; how each fix was applied: /home/narolski/smad-next/docs/PLANNING_RECORD.md, section 5.

---

# Pre-run review: smad-next sprint (AR1-AR7, AD1-AD5, AG1-AG5, TwinMAD), 11 Nov 2026

## 1. Verdict: GO WITH FIXES

Nothing has been launched, and there is no code, pair list or prereg page yet, so I reviewed the design only. The twin idea is sound. Fixes F1-F6 must be in the plan files before any twin is built or any score is read; all are text changes or zero-GPU.

- **F1.** Make the verdict rules two-sided, add a benchmark-reproduction gate and a twin-validity gate.
- **F2.** Match photo composition between morphs and twins (expression, session).
- **F3.** Replace the three numbers by a five-rung ladder, so "benchmark cue" and "tool trace" are separated.
- **F4.** Replace AD4's "permute within source" by a seed-level empirical null plus a zero-step control.
- **F5.** Get an author ruling on landmark-warp generation (rule 3), and register the batch in PROTOCOL and the ledger.
- **F6.** Split selection data from final test data for TwinMAD, and score the final test once.

## 2. Findings

### Blockers

**B1. The verdict rules give wrong verdicts in cases already in the record** (`/home/narolski/smad-next/11_AUDIT_PLAN.md:21-26`).
- The T-twin rule is one-sided. A reversed AUC counts as "cue use shown". `smadcvpr/results/A43/a43_read.md` already has such cells: SelfMAD on two- vs one-identity DiffAE mixes scores 0.290 (own preprocessing 0.252). That is strong separation with twins scored higher, which means the twin carries its own artefact.
- A detector at chance everywhere (T-bench 50, T-flag 50, T-twin 0.5) also satisfies "cue use shown".
- "T-flag error within 5 points of T-bench error" is an equivalence claim. With 102 twins the EER standard error is about 3-5 points, so it cannot be established.
- "Twins flagged at no more than twice the camera-photo rate" at a 1% EER threshold means at most 2 of 102 twins. That is noise.

Paste into `11_AUDIT_PLAN.md`:
> Gates before any verdict: (G-a) T-bench reproduces the published cell within 3 points EER, else the cell is "not reproduced, descriptive". (G-b) Twin validity: FR oracle passes, and morph and twin sets match in photo composition (see F2). Verdicts use the folded value a = |AUC − 0.5| + 0.5 and report the sign. **No identity reading:** T-twin a < 0.60 with upper bound < 0.65. **Twin artefact, cell invalid:** AUC < 0.40 with upper bound < 0.5. **Identity reading:** AUC ≥ 0.75, lower bound > 0.65. The T-flag criterion is the share s = d′(T-flag)/d′(T-bench) with a person-bootstrap interval; "pipeline flagged" needs the lower bound of s ≥ 0.5. The "twice the camera rate" clause is deleted; BPCER of twins at the T-bench EER threshold is printed with its Clopper-Pearson interval.

**B2. FRLL twins mix neutral and smiling photos; benchmark morphs are neutral plus neutral.**
- FRLL has one frontal neutral and one frontal smiling photo per person (`/mnt/t7/Datasety/downloads/frll_base/extracted`: `neutral_front` 205 files, `smiling_front` 103 files).
- A43 already recorded the problem: "R2m's one-identity morphs mix two expressions of a person and carry visible interpolation artefacts"; the expression-matched check R2x was never run.
- For the MADation ViT-B/16 release the twins are not even on a monotone ladder: against the reference pool E (`D20_vs_E`, `C20_vs_E`), reconstructions score 0.930 and same-person mixes 0.731.
- So T-twin on FRLL measures expression mixing against identity mixing, for all three families.

Paste:
> T-twin always compares our own morph(A_neutral, B_smiling) with twin(A_neutral, A_smiling): same tool, same host photo A, same photo types on both sides. Published morphs enter only T-bench and a bridge number (published vs our same-pair neutral+neutral morphs, expected about 0.5, as A43 R1m 0.505). The primary pool for T-twin is FRGC / colorFERET, where A′ and B are both neutral and both from a different session than A. FRLL is the benchmark-linked secondary pool. Every B also appears in a twin (B, B′).

**B3. Three numbers cannot separate "benchmark cue" from "tool trace", and T-flag is confounded by file format.**
- Twins are tool PNGs at tool size; camera photos are camera JPEGs. A41 showed file attributes alone separate these (O = 1.000 in 10 cells). T-flag ≈ T-bench is therefore expected in advance and adds little.
- A detector that flags any warped-and-blended or generated image reads a manipulation trace. That is not a benchmark cue and not identity. For landmark morphs many would call it legitimate. The plan's two labels force it into "cue use".

Paste:
> Ladder, adjacent rungs reported as AUC and as d′ share of T-bench: R0 camera native; R1 camera history-matched (existing E7 / a37_restore output only); R2 pipeline-only (tool on one photo); R3 twin; R4 morph. Labels: R0→R1 "benchmark construction cue"; R1→R2 "tool / generator trace"; R2→R3 "two-photo blending trace"; R3→R4 "identity". The table gives the four shares per detector × family. The paper's sentence "uses a benchmark cue" is allowed only for the R0→R1 share.

**B4. AD4's "labels permuted within source" does not repair A47 I-4** (`11_AUDIT_PLAN.md:47`).
- I-4 already permuted labels uniformly over all 40,000 SMDD rows (PROTOCOL l.19251, l.19425). No label-source association survived then either.
- The control failed for other reasons:
  - A network that memorises random labels is an arbitrary function. On cells whose classes differ grossly it lands off 0.5 per seed.
  - M3 was off in the same direction in both seeds (dim_a EER 35.25..37.77), which points to the CLIP prior. A44 H-new-282 has frozen CLIP separating renders from camera at 0.922.
  - The deciding checkpoint was `es.pt`, selected on correctly labelled validation data.
  - The gate used a person bootstrap with n = 2 seeds.
- The A47 review says the same: "Randomized labels do not guarantee a chance-level trained model".

Paste:
> Chance control for AD4 = empirical null, not a chance gate. Per recipe, 5 permuted-label seeds (301-305, fresh permutation each, last.pt, no selection) plus one zero-step network (the initialised recipe, untrained). Print signed AUC per cell per seed. The morph-free result on a cell counts only if its EER is below the minimum of the five permuted seeds and of the zero-step network by ≥ 10 points. Print training accuracy on the permuted labels. AD4 reuses the registered A47 I-3 data root unchanged (`/mnt/t7/smad_heldout/a47/data47`); no new resampling is run. A1 falsifier: "error above 15% in at least 3 of 5 seeds" (now "2 of 3", `04_HYPOTHESES.md:14`).

Also reconcile three inconsistencies:
- "render vs photo" (`04_HYPOTHESES.md:10`) against "render vs its shrunk copy" (A47);
- "A1r, 3 jobs, 12 GPU-h" (`05_RESEARCH_PLAN.md:72`) against "4 recipes × 5 seeds, 20 H100-h" (`11_AUDIT_PLAN.md:47`);
- Inception and MixFaceNet recipes failed reproduction (A45), so their AD4 rows belong in the "our retrain" block only.

**B5. Compliance (hard rules 3 and 5).**
- AR1, AR2 and D2 need landmark morphs, which means piecewise-affine warps. Rule 3 forbids agents to write or run alignment warps or new resampling. The only precedent is A27, where the author approved `h1_build.py` on 2026-11-03 ("Tak, buduj."). `07_DECISIONS_NEEDED.md` has no such item. The same applies to the "one sampled post-processing chain per pair" (`05_RESEARCH_PLAN.md:46`), to AR5's "identical alignment borders", and to AR4's blanking masks.
- There is no PROTOCOL block and no ledger entry. `prereg/` holds only `TEMPLATE.md`, and `experiments/` and `src/` are empty.
- `11_AUDIT_PLAN.md`, `WORKFLOW.md` and `NOTEBOOK.md` are staged but not committed (one commit, `12848d2`). The thresholds "fixed now" are therefore not fixed anywhere.
- `08_CUE_MATRIX.md`, `09_DATASET_EXTENSION_ANALYSIS.md` and `10_ASSET_INVENTORY.md` are cited but do not exist.

Paste into `07_DECISIONS_NEEDED.md`:
> Open 3: may agents run (i) the A27-approved `h1_build.py` warp path for self-morphs, (ii) the third-party OpenCV / FaceMorpher morphers unchanged, (iii) constant-colour region blanking? No new blur, resize or JPEG code in any case; storage is PNG at tool size.
> Open 4: one PROTOCOL block "A51 smad-next" citing the smad-next commit sha and the sha256 of each prereg page, plus one ledger folder per ID, before the first run.

### Majors

**M1. The positive control is necessary but is not a power check, and it is misplaced** (`11_AUDIT_PLAN.md:68-71`).
- "Distance of the embedding to each contributor" uses contributor references. For a twin both contributors are the same person, so the score separates by construction. That validates the manipulation.
- It does not show a single-image signal exists. A46 is the precedent: the oracle passed (H-new-317) and the image-only probes failed (H-new-318).
- "A detector at 0.5 is a failure of the detector" therefore does not follow.

Paste:
> Two controls per family (AR1, AD1, AD2, AG1, AG5), computed before any detector score is opened. (P1) Manipulation check: FR oracle AUC ≥ 0.90; morphs verify against both contributors at FMR 1e-3 in ≥ 70% of cases (h4 reference: 0.905); twins verify against A. (P2) Single-image readability: a twin-trained probe on frozen features, 5-fold by person, with its interval. If P2 < 0.65, the cell's wording is "neither the released detectors nor a probe trained for it read identity blending"; never "the detector failed". Negative control: twin(A, A′) vs twin(A′, A) must sit at 0.5.

**M2. The (c) conditions are partly unachievable and partly insufficient** (`11_AUDIT_PLAN.md:89-93`).
- Unachievable:
  - "All cue-only baselines within 0.55 on the twin set" fails on legitimate grounds. File bytes alone gave 0.620 on H1 because averaging smooths texture; A27 (5) calls these "attack properties, not pipeline asymmetries". A 32-px thumbnail and the face-only crop contain the identity-average signal that hypothesis M3 predicts.
  - "Pipeline-only not flagged" excludes a detector that reads both a tool trace and identity.
- Insufficient:
  - AR1 runs on our morphs, so it says nothing about the benchmark number.
  - "Free of benchmark cues" is a universal negative.

Paste:
> Wording: "no tested benchmark cue explains the result; an identity share of X survives". Conditions: (1) identity reading (B1 rule) on both pools with composition-matched twins; (2) the detector exceeds the best non-content baseline (file attributes, border mask, background-only) by a paired lower bound > 0; the thumbnail and face-only rows are reported as content baselines, not as cues; (3) monotone dose 0.1…0.5 (Page test); (4) accuracy kept with background blanked; (5) benchmark link: bridge AUC published vs our same-tool morphs within 0.40-0.60, and at the benchmark EER threshold our morphs are detected within 10 points of the benchmark rate while twins are not; (6) R0→R1 share ≤ 0.2 under the border-matched control. **Refuted** = R0→R1 share ≥ 0.5, or the B1 "no identity reading" verdict on both pools. Otherwise "mixed", with shares.

**M3. (b): the premise in the GAN note is contradicted by the record** (`11_AUDIT_PLAN.md:56-58`).
- "A detector trained on SMDD cannot have learned GAN output = attack" does not hold as a statement about behaviour. The SMDD-only M3 recipe separates renders from camera at 0.951 / 0.956 / 0.967, and frozen CLIP does so at 0.922.
- Correct form: SMDD labels cannot supply the cue, yet the networks rank renders above camera photos; pretraining or the SMDD attack-side processing supplies it.
- Consequences:
  - AG2 can come out reversed (EER above 50), as morph-free M3 did on MIPGAN (75.5). Pre-register a two-sided reading.
  - AG2's reconstructions must come from the same MIPGAN optimiser with A = B (the R2 rung), not from another inverter. Otherwise inverter differences separate the classes.
  - In AG1, MIPGAN on one identity converges to lower loss and stays closer to the inversion manifold. Fix the iteration count, log final loss and distance of w from the mean, and report T-twin within matched bins (as X4 did for spread).
  - SelfMAD is not SMDD-trained, so the note does not apply to it.
- AG4 shows sufficiency for the cell, not use by any detector. It also uses training data that no published method used. Label it "benchmark-level". It needs a held-out generator (train on StyleGAN2 reconstructions, test MIPGAN-I on v1), the B4 null, and its own T-twin (it must be near 0.5). It is the first GAN item to cut.

**M4. Statistics.**
- With 102 twins the AUC interval is about ±0.07-0.08 (A43: ±0.08 at 200/100). "Cue use" then needs a point value ≤ 0.57 and "morph signal" ≥ 0.73. Expect many "mixed" cells; state this in the plan.
- Thresholds were set after the relevant values were seen: 0.59 (StyleGAN3), 0.706 (A43), 0.724 / 0.745 (A46). Label AG5 and AD1 ViT-B/16 "post hoc, outcome known".
- `04_HYPOTHESES.md:19` uses 0.65 where the audit plan uses 0.60 / 0.65. Unify.
- Multiplicity: name 12 primary cells (4 releases × 3 families, first tool, primary pool) with Holm; the rest are descriptive.
- Reuse the two-way person bootstrap of `a41_read.py`, since morphs cross persons.
- Gate 0 (≥ 0.60 on about 100 persons) is a coin flip. Make it advisory, or gate on the lower bound > 0.5 with 5-fold by person.

**M5. TwinMAD.**
- The held-out tool is read at Gate 1 on Thursday and again after Friday's LoRA and backbone choices. That is adaptive reuse of the test set.

Paste:
> Selection uses TwinSet-val only (FRGC / FERET persons, leave-one-tool-out). Final test = FRLL persons × held-out tool or generator, opened once on 14 Nov. FRLL persons never enter training or A3 refits.

- With two landmark tools, "hold out one" trains on a single tool. Add the A27 path as a third.
- AUC ≥ 0.60 is an EER of about 43%. It shows a signal exists; it is not a detector.

Paste:
> Tier 1 "signal": lower bound > 0.55. Tier 2 "method claim": AUC ≥ 0.80 and BPCER@APCER 10% reported.

- M1's thumbnail falsifier contradicts M3 (averageness is low-frequency). Report it as a decomposition, not a kill rule.
- G2 as written cannot pass on frozen CLIP features. Probe the score, and require the score shift under E7 to be the same for both classes.
- M5's "within 2 points on MAD22 / FRLL" contradicts the audit thesis (A47 I-1 cost +52 points). Make it descriptive.
- G1 has no pass rule.

**M6. Feasibility and operations.**
- WCSS wait is days: `02_REVIEW_AND_SHORTCOMINGS.md:45` forecasts the MAD22 start for 13 Nov 23:20.
- No x86 MIPGAN / DiM / DiffAE container exists, and the earlier x86 DiffAE build failed (`06_RESOURCES.md:49`). I found no MIPGAN generation code under `smadcvpr/`.
- The DGX is aarch64 and its GPU was 96% busy when I checked. The root disk is 97% full (33 GB free). `/mnt/t7/smad_next` does not exist; `/mnt/t7` has 356 GB free.
- Corrected MAD22 scoring (canonical164) has not run. AG1's T-bench on MIPGAN-I/II and workstream B depend on it; the fallback is the FRLL StyleGAN cell.
- Vast: uploading FRGC, colorFERET, Multi-PIE or CASIA images to rented machines needs an explicit author yes. Restrict lease V1 to FRLL.

## 3. Improvements, by value per GPU-hour

1. **Re-read A43 for AD1 (0 GPU, allowed now, post hoc label).** B20, C20 and D20 scores exist for the ViT-B/16, ViT-L/14 and SelfMAD releases; only MixFaceNet is missing. Run R2x (expression-matched) instead of 102 more smiling mixes.
2. **Zero-step networks on all cells** (minutes). They explain I-4 and belong in AD4.
3. **AR1 on FRGC / colorFERET first** (CPU; needs the F5 ruling). This is the only way to answer (c).
4. **Controls P1 and P2 plus cue baselines on every twin set** (minutes).
5. **AG5 under the new rules** (minutes).
6. **Cut order when time runs out:**
   1. AD5. A44 R-last already gives 8 MADation retrains at 4.44 vs 4.9; the SelfMAD retrain is 30 H100-h with A45-style reproduction risk.
   2. AG4.
   3. T5, T6, X3.
   4. The MADMamba arm.
   5. AD2 (needs DiM code).
   6. AR7.
   7. The 10,000-pair generator sets.
   
   Keep AR1-AR5, AD1, AD3, AD4 on M3 and M3L only (10 runs), AG1 with its pipeline-only arm, AG5, and T4 landmark heads.

## 4. Questions for the authors

1. Is a detector that flags any tool-processed image (R1→R3) counted as "benchmark cue" or as legitimate S-MAD? The headline wording for (c) depends on this.
2. Rule 3: which landmark generation paths may agents run (see F5)?
3. Does prereg in `smad-next` replace PROTOCOL and ledger registration, or is the pointer block required?
4. May a freshly trained MADMamba arm be scored on twin sets while the W3 / H3 seal on MADMamba holds?
5. May licensed images go to Vast?
6. Is the benchmark's own MIPGAN code and weights available on x86, or only the A33 re-implementation (StyleGAN v1, 326 pairs)?

Files reviewed: `/home/narolski/smad-next/{11_AUDIT_PLAN,04_HYPOTHESES,05_RESEARCH_PLAN,06_RESOURCES,07_DECISIONS_NEEDED,WORKFLOW,NOTEBOOK,01_EVIDENCE_DOSSIER,02_REVIEW_AND_SHORTCOMINGS}.md`; `/home/narolski/mambamorph-code/smadcvpr/results/A43/a43_read.md`; `/home/narolski/mambamorph-code/smadcvpr/results/A47/a47_read.md`; `/home/narolski/mambamorph-code/experiments/INDEPENDENT_REVIEW_A47_20261108.md`; `/home/narolski/mambamorph-code/smadcvpr/PROTOCOL.md` (A27 l.7715-7745, A47 l.19193-19425); `/home/narolski/mambamorph-code/experiments/CONCLUSIONS.md` (l.447-536). No `fst*`, `valx*` or A12SP file was opened.
