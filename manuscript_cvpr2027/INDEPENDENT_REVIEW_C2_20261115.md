# Independent Review C2 — CVPR 2027 manuscript `manuscript_cvpr2027`

Reviewer: independent reviewer C2 (fresh pass; own opinion formed before reading the prior session digest).
Date: 2026-11-15.

## Reviewed state

- Repository `/home/narolski/smad-next`, **HEAD `1dc1581c734a30d015d4ee9da8dc263994f76e1e`** ("Release reviewed controlled-splice full numeric inference", 2026-11-15 19:27:35 +0100).
- `main.tex`, `method.tex`, `results.tex`, `related.tex` are **tracked and byte-identical to HEAD** (working tree == HEAD for all manuscript .tex). Reviewed from HEAD accordingly.
- `preamble.tex` (template stub, not `\\input` by main.tex), `supplement_reproducibility.tex`, `references.bib`, `figures/`, `publication_wip.tex`, `supplement_threshold_transfer.md` are **untracked**; the working-tree copies are the only available state and were reviewed as such. Tracked modifications elsewhere (`ATHENA.md`, `NOTEBOOK.md`, `experiments/SPRINT5_20261114/breadth/prereg.md`) do not affect the manuscript.
- All bibliography keys cited by main/method/related/results resolve in `references.bib` (19/19 checked).
- Compiled PDF (`main.pdf`, 9 pages: ~8 content + references page) corresponds to this text.

## Verdict

**MAJOR REVISION — not submittable in the current state** (CVPR practice: the scientific core would be a borderline-positive review, but the manuscript fails submission completeness and contains placeholder material that must not be seen by reviewers).

- Science verdict (if the blockers below were removed): **weak accept**. The evidence discipline (pre-registration, once-only reads, adversarial floors, retained negative results, honest exposure labeling) is exceptional and the controlled-evaluation framework is a real contribution.
- BUT the compiled paper contains literal WIP editorial notes, a missing promised appendix, an unpopulated HOLD table, an unintegrated reproducibility supplement, a draft title/LLM disclosure, and unresolved dataset rights. These are submission blockers, not review preferences.

## Numeric verification (step 2 of the procedure) — PASS

Every value–source pair in `results.tex` and `supplement_reproducibility.tex` was traced to an admitted report. **No numeric discrepancy found.** Sample of verified pairs (~60 values checked individually):

| Manuscript value (results.tex) | Source (admitted) | Match |
|---|---|---|
| Blend Table 1: A .864 [.848,.881], B .879 [.862,.894], Sb .889 [.873,.908]; Sb−B +.011 [−.010,+.031], 3/5 seeds; seed-level [−.027,+.049]; 64 blocks / 299 hosts | `experiments/XF1_ffhq-facemorpher-matched-render/result.md` | ✔ |
| 0.0 % EER on native MorDIFF, 10/10 networks, B/16+L/14, seeds 401–405, 25k+25k, scale .3125, 6,250 steps | `experiments/reviews/REVIEW_AD4_CLUSTER_20261113.md`; `AD4/prereg.md` (25,000 natives + copies, `prep_eval.degrade(„R",0.3125)`, 6,250 steps) | ✔ |
| MIPGAN: 227/238/119/74 rows; .992–.998 (R2 vs R0); .619–.690 (R4 vs R3); 78–90 % render flags | `experiments/PR1_protocol-reads-existing-networks/result.md` (rows R0 227, R2 238, R2s/R3/R3m 119, R4 74; tables & GD2) | ✔ |
| Sb−B +0.042 [.019,.070], 99.5 % [.008,.081]; Sb−Sp +0.049 [.028,.073], 99.5 % [.019,.083]; Sp−B −0.008 [−.033,+.022]; FS1 re-read +0.051; 85 % / 92 % / 98 % own-rule flags | `AB1_protocol-ablation-and-replication/result.md` amendments 4/5 tables | ✔ |
| Splice ranking stratified +0.118 [.069,.245], 1,246/2,000 readable (37.7 %); unstratified +0.169 [.136,.204]; Sp→Sb splice flags 70–74 % → 36–41 % | same report (amendment 4/5b) | ✔ |
| Table 2 (executed components): all unique/row counts (1526/1992 … 5535/8386, 2146/2850), S4/S3 AUC ranges (e.g. Sb .755–.804, Sp .691–.722, SbZ .754–.805, SbH .773–.814, SbS .761–.804, A .559–.598, AS .577–.612), S3 flag ranges — every cell | same report per-network table | ✔ |
| Component hypotheses: SbS|.054 [.038,.070]; AS 0/5 C2P; SbS|dsoft +.018 [.013,.023]; H-ab2/H-ab3 falsified | same report secondary attribution table + registered verdicts | ✔ |
| Storage: A 26.5–38.5 pp vs Sb 0–4.5 pp (trained), 5.5–15.2 vs 0–2.1 pp (untrained); Sb 5/5 trained, 3/5 untrained, score-toward-genuine failures | same report (C2P Δf tables, R1 verdict) | ✔ |
| Count-balanced Table 3: Sb−SpV +0.0481 [.0269,.0722]; BN−BV −0.0030 [−.0089,.0045]; splice +0.0818 [.0535,.1083]; −0.0247 [−.0455,−.0050]; 99.5 % secondary [−.0538,.0031]; 151/51 components; 5/5 and 0/5 positive seeds; Sb/SpV/BN/BV unique 5,535/5,223/5,411/5,099 | `experiments/reviews/REVIEW_AB1_BATCHC_OPENCODE_20261114.md` (values match to 9 decimals) | ✔ |
| Table 4: breadth .511249→.511334, +.000085 [−.023717,+.023769], 32 images; HN .665198→.658733, −.006465 [−.017472,+.000017], 0/5; paired BCE +.009395 [−.001253,+.029119]; ranking +.021194 [−.016593,+.059224]; tail FA 7.69 %→0 %, S4 89.41 %→76.47 %, own-calibrated 64.71 %/54.12 %; +.0195 [−.1134,.1395] floor; 2 % of 10,000 draws; 47/5/67 (52 sparse) guards, 5 TT1 FRGC border/geo failures; 65.6→55.6 % vs 96.2→94.4 % | `SPRINT5_20261114/breadth/BREADTH_POSTRESULT_INDEPENDENT_REVIEW_20261114.md`, `SPRINT5_20261114/hn1/HN_POSTRESULT_INDEPENDENT_REVIEW_20261114.md`, `SPRINT5_20261114/paired_ranking/full15_metadata_packet_20261114/INDEPENDENT_SCIENTIFIC_POSTREVIEW_20261114.md`, `SPRINT5_20261114/tail/baseline_aux_reader_v1/BASELINE_AUX_POSTRESULT_INDEPENDENT_REVIEW_20261114.md` | ✔ |
| MAD22 Table 5: all 70 EER cells (Sb S/H, MADation B/16, L/14, MixFaceNet, SelfMAD × FM/OpenCV/Webmorph/MIP-I/MIP-II/LM2/M4); counts 1000/984/500/1000/999, 204 genuine, 102 persons; −1.4 [−3.51,0.98]; p=0.02499 vs 0.025; −1.0 [−4.7,3.0]; Webmorph misses 24–58 %, FA 0–2.5 %; SelfMAD raw lowest comparator mean | `experiments/FINAL_sealed-benchmark-read/result.md` (all cells match exactly) | ✔ |
| Supplement: arm inventories, 536/8/191/100/156/124 hosts, AF0 663/67/481/115 (consistent: 663−67=596=481+115), 11-of-80 shape-linked hosts, MAD22 4,483 morphs (sums exactly) | `AGENTIC_delivery_20261114/SOL_REPRODUCIBILITY.md`, `manuscript_cvpr2027/OPENCODE_REPRODUCIBILITY_AUDIT_20261114.md`, `AB1/prereg.md`, `PR1/…`, `AF0/README.md`, `AB1/REVIEW_*` | ✔ |
| Figure 1 (tikz) values: 0 % EER 10/10; −0.049 AUC | AB1/AD4 as above | ✔ |

Timed-out note: the FULL independent recomputation of AUCs/bootstraps from raw scores was **not** performed (and could not be — the admitted Batch-C output contains no row logits; its own post-review explicitly states this verification boundary: `REVIEW_AB1_BATCHC_OPENCODE_20261114.md`, „Verification boundary"). Verification here is manuscript↔admitted-report consistency plus internal arithmetic, which is what the procedure asks.

## Blockers (each: place, source of truth, why blocking)

1. **WIP editorial notes compiled into the paper body.** `results.tex:3` (`\\input{publication_wip}`) pulls `publication_wip.tex:1–7`, which renders blue `[WIP–TRANSFER]`, `[WIP–CONFIRMATION]`, `[WIP–REPRODUCIBILITY]` notes into the Experiments section; `publication_wip.tex:1` says "Remove before submission." Truth: the file itself. **Blocks submission** (reviewers must not see internal to-do notes; the WIP–TRANSFER note also admits a required threshold-transfer paragraph is missing).
2. **Promised companion appendix does not exist.** `results.tex:76` ("remain in the companion appendix"), `results.tex:114` ("The appendix retains all 119 cells, 15 networks and both threshold policies"), `results.tex:132`, `results.tex:173` ("Full operating errors and protocol coverage appear in the companion appendix"). No appendix file exists anywhere in the manuscript directory. The `results.tex:114` appendix is load-bearing for the NOT_QUALIFIED operational claim. **Blocks submission** (evidence referenced but not shipped).
3. **Reproducibility supplement is not integrated.** `supplement_reproducibility.tex:1–2`: "Proposed supplement fragment; no main file inputs this yet." `main.tex` never inputs it, and no supplement PDF exists. CVPR requires a supplement/checklist; all exposure mapping and the threshold-transfer record (`supplement_threshold_transfer.md`) currently live outside the submission. **Blocks submission.**
4. **Placeholder HOLD panel inside Table 5.** `results.tex:162–173`: a 5-methods × 5-families table whose every cell is "HOLD", with "new reads remain gated". Publishing an all-placeholder table advertises planned experiments without data. Either fill from admitted reads or delete the panel and state the gate in one sentence. **Blocks submission** (placeholder material).
5. **Draft title and draft LLM-usage disclosure.** `main.tex:10` carries the subtitle "Integration review draft"; `main.tex:58–59` states "This is a draft disclosure … the authors must verify … and finalize this statement before submission." The AI-usage disclosure is mandatory (CVPR 2026+ policy); an explicitly unverifiable draft is not acceptable. **Blocks submission.**
6. **Dataset rights and ethics unfinished.** `supplement_reproducibility.tex:24`: "dataset rights remain unresolved." The paper trains/evaluates on FRGC, colorFERET, FFHQ, SMDD, FRLL and evaluates against FRLL-photograph-based MAD22. There is no ethics/broader-impact statement for a face-morph *attack* method. For CVPR this must be resolved or explicitly and honestly declared (license terms per dataset, no contributor identification beyond public research photos, attack disclosure intent). **Blocks submission** as an open compliance item.
7. **Untraceable „registered composite rendering verdict".** `results.tex:15`: "The registered composite rendering verdict remains inconclusive." No admitted report defines or prints a *composite* rendering verdict. PR1's registered verdicts are: GD1 „render path used" (5/5), GD2 „one-person render flagged like a morph", Z2a joint operational 2/5 — none is „composite/inconclusive". The underlying numbers are correct (verified above), but the sentence attributes to a registration a verdict that does not exist. Fix: cite the actual registered verdicts or define the composite with its source. **Blocks submission in the loosest sense (misattribution of a registered result); a one-line fix.**

None of these seven is a numeric error. Items 1–6 are completeness/compliance; item 7 is a wording-accuracy defect in a load-bearing sentence.

## Significant improvements (do not block, but should be made)

1. **Re-introduce the render-controls table.** `results.tex:15` quotes bare ranges (.992–.998, .619–.690, 78–90 %). The abandoned `PUBLICATION_F1_F4_REPAIR` draft had `tab:render_controls`; a compact 3-arm × {R2-vs-R0, R4-vs-R3, flags} table would restore verifiability.
2. **Abstract wording on storage attenuation.** `main.tex` abstract: "The full protocol attenuates storage-induced false alarms." The registered storage verdict is **inconclusive** (Sb passes 5/5 seeds at the trained size but only 3/5 untrained, failing on score movement toward genuine; AB1 result R1). The body reports this correctly; the abstract should carry a qualifier („at the trained size; registered combined verdict inconclusive").
3. **Readability of qualification density.** The manuscript is exceptionally honest but qualification saturation (nearly every sentence carries a „not X" clause) makes the argument hard to follow even for an expert. A single „registered-verdicts summary" table (claim → verdict → population → interval type) would help reviewers enormously.
4. **State the population relationship once, centrally.** The 11-of-80 shape-link caveat appears in method.tex; the clean80 screening, the 69-host sensitivity and the dev/clean split should be summarized in one place (currently spread over method.tex §Evaluation, results.tex §training_results and the unintegrated supplement).
5. **Figure 1 is a text-box schematic.** All three panels are prose in boxes. If VIS1 example images remain gated, at least render the D-proxy/stratification or the construction ladder graphically; the current tikz adds little.
6. **MAD22 table ergonomics.** Add per-seed SD for Sb, mark the per-family Holm verdicts, and visually separate the S/H forms; currently the reader must trust the caption that „no global winner is highlighted".

## Nice to have

- Rebuild `main.pdf` after the fix pass (current PDF predates the last text edits by hours and its mtimes should not drift from sources).
- Repo hygiene before packaging: remove `results.tex.orig`, `main_plotly.*`, `legacy_references.bib`, local review directories from the submission bundle; unify the three duplicate supplement fragments in `supplement_*_review_20261114/`.
- State in the supplement that intervals condition on five fitted networks **and** that component counts (151/51 etc.) are saved denominators, mirroring the Batch-C review's verification boundary.
- Consider one paragraph positioning vs 2026 concurrent morph-specific work beyond MADation/SelfMAD (the related-work section is accurate but thin on non-CLIP detectors).
- Given every number already has a source hash chain, add a machine-checkable evidence manifest mapping paper sentences → admitted report files (a skeleton exists as `evidence_manifest.json`).

## Cross-check with the prior session digest

(`…/scratchpad/cvpr2027-session-digest.md`, session `01a1d9c6`; read **after** the independent assessment above.)

- The digest's headline result — **„Numeric GO: all paired values, source rows, descriptive paragraph match admitted reports"** — is independently confirmed by my verification: I found zero numeric discrepancies.
- The digest's single pending fix (caption „These suppress specified processing mismatches" → „test sensitivity to …"): the phrase does **not occur** in the current HEAD text or in `supplement_threshold_transfer.md`; the relevant content (threshold-transfer paragraph) is simply absent (my blocker 1/supplement 3). Nothing to apply, but it corroborates that the threshold-transfer material never made it in.
- All blockers 1–7 found above are **NEW** relative to the digest (the earlier session audited numeric consistency, not submission completeness): WIP insert, missing appendix, unintegrated supplement, HOLD panel, draft title/LLM statement, unresolved dataset rights, and the untraceable „composite rendering verdict" sentence.

## Bottom line

- **What blocks submission:** items 1–7 above (placeholders, missing promised evidence artifacts, draft disclosure/ethics state). All are mechanical except items 2 (assembly work) and 6 (rights/ethics, needs an author decision).
- **What does not block:** the scientific content. Claims in abstract/intro are covered by the executed, admitted evidence with correct qualifiers; control design (warp-only, same-person, seam-only, D-stratification, adversary floors) is sound and honestly limited; pending cells (FRLL-Morphs HOLD) are marked; negative and inconclusive results are retained; the MAD22 comparison is explicitly and correctly labeled development-exposed; anonymity of the submission is preserved.

Reviewer recommendation: **major revision / not yet submittable; on resubmission with blockers resolved, a defensible weak-accept paper.**
