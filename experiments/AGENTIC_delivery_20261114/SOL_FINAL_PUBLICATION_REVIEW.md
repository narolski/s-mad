# Final publication audit — bounded Sol review, 14 November 2026

**HOLD — no submission GO and no scientific release.** This audit covers publication consistency, close prior work, bibliography, anonymity, rights and current official CVPR2027 requirements. It does not reproduce numerical tables or replace Astra's independent supplement fidelity/layout and OCC1 print reviews. Findings below open specific repair tasks. Main/TikZ, Plotly, WIP, supplement source, results and canonical journals were not edited.

## Scope and evidence boundary

Read mambamorph AGENTS.md and its pointed CONTINUE.md before live smad-next AGENT_STATUS.md, NOTEBOOK.md, delivery README/WORKSTREAMS and manuscript conventions. smad-next/CLAUDE.md is absent; mambamorph/CLAUDE.md describes the historical flat IEEE manuscript, not an instruction to overwrite the current CVPR paper. Active registry at audit start: root, Astra sprint/review owner and this owner; Luna's bounded cycle completed. Parent assigns independent supplement/OCC1 review to Astra; no duplicate compilation or score QA here.

Only existing admitted result/review text, source and publication metadata read. No candidate NPZ/checkpoint, archive payload/member or still-sealed score read. No cluster queries, GPU work, submissions, rentals, scientific reader or production journal invocation. SSH only gx10 for repository text and this report. Shared dirty tree preserved. BrowserOS neo tools are absent from the available tool inventory; public primary-source verification used the available web search/open tool, with access failures recorded rather than guessed away.

## Findings, severity and concrete repair

P1 means publication/scientific blocker; P2 means bounded editorial or verification repair. A pending independent review is not a pass or a failed hypothesis.

### F1 — P1: abstract repeats primary MAD22 mean without required companion qualification

`manuscript_cvpr2027/main.tex:15` gives 3.37% versus 4.72%, with development exposure and no-superiority qualification, but omits the mandatory landmark-only companion. `experiments/FINAL_sealed-benchmark-read/result.md:57–64` binds that primary sentence to the landmark-only non-separation and GAN-specificity qualification. `results.tex:160` contains them correctly. **Repair:** in the abstract add the landmark-only result/qualification and indicate unresolved rendering specificity, or remove its benchmark numbers and use the space for the controlled-study scope. Do not replace this with “matches”, “superior”, “competitive generalization” or robust noninferiority. This affects both visual variants because `main_plotly.tex:3` inputs main.tex. The threshold-fragile NI explanation at results:160 must remain.

### F2 — P1: original-recipe joint operational contribution remains unestablished

`main.tex:29`, `results.tex:83–88,103–124,132–133` describe separate development ranking and storage effects; they do not establish improved face-splice detection at comparable false alarms together with reduced artifact response for one protocol. Current contribution 3 is deliberately narrower and should remain so. Batch-C controls row/class/positive repetition, still changes unique negative-image content/diversity by312; conditional intervals do not quantify arbitrary retraining variation. Storage's overall registered verdict is inconclusive. `SOL_OPERATIONAL_CONTRIBUTION.md` explicitly identifies missing matched-operating-point bridge, sparse support and additive reporting requirements. **Repair route:** retain the bounded contribution now; only strengthen it after exact registered/admitted operational comparisons and independent conclusions review. Existing SPRINT5 pilots concern other recipes, including shared-Sb408 warmstarts; they cannot retrospectively confirm full Sb. NEXT v3 approval dbeb940 is binding, selection remains unadmitted and fresh413–417 unconfirmed. No new scientific default, threshold or reduction margin is authorized by this audit.

### F3 — P1: supplement leaks author identity, with wider publication cleanup needed

`manuscript_cvpr2027/supplement_cvpr_review_20261114/supplement_cvpr.tex:1069` prints `/home/narolski/.../tt1_read.json` (Astra observed it on p19). Replace the absolute user path in the publication derivative with a neutral relative source identifier. Preserve the original internal record and hashes; this is an editorial derivative, not lossless-byte identity.

Additional exact locations requiring review: lines188,484,834 expose internal mount/archive paths;486 includes GPU UUID fragment, named lease and timestamp;476–478 give rental costs, lease labels and WCSS;184/200 identify infrastructure runs. These are not all direct author identifiers, and hardware/software/platform distinctions are scientifically needed. **Repair:** remove user/account identifiers and unnecessary lease/UUID/cost/run-account detail; retain GPU model, software, precision, gate failures and platform-specific scientific qualifications. Search rendered PDF text, hyperlinks/bookmarks, PDF author/creator metadata, attachments and source-package README/JSON/manifests for person/account/institution/absolute-path leaks. Do not merely patch p19: accompanying `README_TYPESET_REVIEW.md:9` already acknowledges unresolved account/provider material. Scope includes submission ZIP if supplied; private evidence ledger may retain identity. Astra owns final layout/fidelity re-review after redaction.

### F4 — P1: current LLM statement is a placeholder that does not name tools

`main.tex:60–61` has the correct heading/position but says only “An AI coding and writing assistant” and asks authors to finalize. **Repair:** author-verified names of actual systems/tools, affected research/manuscript parts and nature/extent, including code/experiments/ideation/figures where applicable. Do not invent model versions or limit disclosure to grammar when agents wrote analysis/training code and research records. Distinguish scripts drawing empirical figures from generated image content. Keep anonymous. This is a concrete 2027 requirement, not optional camera-ready polishing; official source below.

### F5 — P1: face illustration rights are not cleared by numerical/print acceptance

`FIGURES_OWNER_HANDOFF_20261114.md:11` identifies FERET host00026/partner00140, numeric-only in-place admission and separate display/publication rights. OCC1 five-model5,120-view numeric PASS does not license faces or support population/causal/localization claims. Keep source-face publication HOLD; no source pixels/occluded face/overlay export. Numeric maps without face pixels still need accurate captions and print review, owned elsewhere.

Current integrated `main.tex:34–39` and `results.tex:91–99` select conceptual schematics/statistical evidence figures, not a published source-face panel. `figures/source_manifest.json` binds report-derived numbers, not photograph permissions. If adding real examples, require exact source IDs, actual applicable agreement, redistribution/derivative permissions, attribution and changes, plus a consent/ethics disposition. The official [FFHQ repository](https://github.com/NVlabs/ffhq-dataset#licenses) distinguishes per-image licenses/credit from dataset licensing; citing StyleGAN alone does not supply image-specific credit. Its use restriction also needs a documented applicability assessment for this security research. [NIST Color FERET](https://www.nist.gov/itl/products-and-services/color-feret-database) is a primary starting point, not proof that the historically obtained agreement permits export. Do not substitute Gray FERET conditions for Color FERET. No new legal clearance asserted here.

### F6 — P1: submission administration is unknown and time-critical

No OpenReview enrollment/submission receipt was inspected; do not infer missing enrollment, and do not infer it exists. Root/author must supply the already-created paper's administrative receipt, complete profiles/conflicts/enrollment and applicable reciprocal-review eligibility/quota check. Creating a fresh paper after the enrollment deadline cannot be assumed possible. Do this before investing in a claim that a valid2027 submission is assured.

### F7 — P2: supplement exists but main does not direct readers to it

`main.tex:43–45` inputs related/method/results; `results.tex:3` correctly inputs retained WIP. No supplementary-reference pointer was found in main/method/results. `supplement_cvpr.tex:15,47` still explicitly labels an author-review draft and includes WIP. **Repair after independent acceptance:** add a precise main-text pointer to the factual loss/preprocessing, seed/pool/exposure and complete threshold-transfer sections, select the final supplement artifact, then apply the documented editorial redaction transform and re-review. Do not remove `publication_wip.tex:3–7` merely because43pages were typeset. Reproduction census/fallback/dependency/rights and operational/confirmation limitations remain. Main and Plotly require separate final pagination receipts after any edits; historical8main/9total-page receipt is not approval of a changed bundle.

### F8 — P2: bibliography “verified” header overstates this bounded audit's coverage

`references.bib:1` says all entries verified. This audit independently confirmed relevant identities/claims below but did not certify every DOI/page/venue field. Several primary publisher pages returned403, Nature redirect500 and OpenReview browser verification. Record those limits; no citation was demonstrated fabricated by this pass. Routine completion must use publisher/author records, not invented bibliographic fields. Keep the two SelfMAD variants distinct.

## Claim/evidence map

| Intended contribution/claim | Admitted evidence and manuscript location | Permitted scope / missing proof |
|---|---|---|
| Resolution/processing shortcuts | AD4 reviewed result; results:5–35; main:21 | Morph-free processing supervision suffices for native MorDIFF cell under tested preprocessing/ten networks.256→80 AREA PNG then80→224 bilinear; original256→224. Not blur-only causality, universal detector mechanism or all-domain perfect detection. |
| Blending versus two contributors | PR1 GD2; XF1 admitted result/review; results:35–79 | One-photo renders strongly activate Sb; blend-versus-warp gain Sb−B+.011[-.010,.031] inconclusive. Low-level floors.925/.917 remain viable explanations; no identity-specific mechanism or shortcut-free conclusion. |
| Qualified controlled training benefit | AB1 amendments and independently reproduced Batch-C four outcomes; results:103–130 | Primary+.0481 conditionalCI[.0269,.0722], all five seeds; secondary+.0818, adverse BN−BV retained. Content/diversity confound312images, conditional-network uncertainty, no interaction test. |
| Reduced storage flags | AB1 R1; results:132–134 | Descriptive attenuation permitted; registered overall inconclusive, no shortcut removal or preserved attack utility claim. |
| Joint operational utility (requested stronger third claim) | SOL_OPERATIONAL_CONTRIBUTION + pending distinct experiments | NOT CLOSED. Separate ranking/storage/TT1-genuine-only blocks do not establish conjunctive utility at comparable FA. |
| MAD22 comparison | FINAL result:9–20,36–64 and independent review; results:138–160 | Seen in development, FRLL204photos/102persons exposure; 3.37 vs4.72, landmark6.32 vs7.37 not separated; fragile NI, no superiority, GAN specificity unresolved. |
| TT1/MEDS transfer | admitted consolidated supplement narrative | Genuine-only transfer and platform/failure qualifiers; cannot establish attack-sensitivity preservation on those new sources. |
| OCC1 | parent numeric PASS5120; owner/result records | One fixed development host, descriptive logit response under perturbation. No population improvement, causality, attribution faithfulness or publication-rights clearance. |

## Novelty and primary bibliography verification

The narrow defensible novelty is the linked empirical audit/control/training study. No “first”, new backbone, first synthetic MAD training, first blending supervision, or established identity-mechanism claim is supported by this bounded search. `related.tex:7–20` mostly makes this distinction correctly.

- `references.bib:22–24`, related:8: [MADation author paper](https://arxiv.org/abs/2501.03800) confirms CLIP+LoRA+classification-header precedent. CVF publisher endpoint returned403 here; pages/DOI not freshly independently certified.
- bib:25–30, related:10: [SelfMAD author paper](https://arxiv.org/abs/2504.05504), [official SelfMAD repository](https://github.com/LeonTodorov/SelfMAD), [official SelfMAD++ repository](https://github.com/LeonTodorov/SelfMADpp) confirm separate methods; latter supplies Information Fusion127,103921,2026 metadata. Results against released SelfMAD are not results against SelfMAD++.
- bib:49–57, related:17–18: [Face X-ray author paper](https://arxiv.org/abs/1912.13458) and [Self-Blended Images author paper](https://arxiv.org/abs/2204.08376) establish prior boundary/self-blend supervision. The current negative-control target is a meaningful distinction, not proof of globally first use of same-person controls. Both CVF HTML endpoints returned403; bibliographic page ranges remain routine verification.
- bib:58–61, related:15: [Printed and Scanned](https://arxiv.org/abs/2610.35682) exists, submitted26Oct2026; authors/title match. It evaluates print/scan degradation and multiple scanners, different from the present matched processing-specificity tests. It is not proof that this paper discovers processing vulnerability first.
- bib:33–41: [SMDD author paper](https://arxiv.org/abs/2203.06691), [SYN-MAD2022 author paper](https://arxiv.org/abs/2208.07337) confirm synthetic training and benchmark provenance. [MorDIFF authors](https://github.com/naserdamer/MorDIFF) confirm title/author list and cite underlying SYN-MAD; registration/publication metadata should remain linked to that primary record.
- bib:9–14,62–64: [CLIP publisher](https://proceedings.mlr.press/v139/radford21a.html) confirms author list,2021,pages8748–8763; [rsLoRA author paper](https://arxiv.org/abs/2312.03732) confirms scaling/title/author/year. LoRA OpenReview endpoint challenged; verify via authors' original paper before certifying full metadata.
- bib:15–17: [NTNU MIPGAN source](https://www.ntnu.edu/nbl/software_mipgan) confirms title/author list and controlled code-license distribution. Does not confer arbitrary source-picture display rights.
- bib:67–79: [NIST FRGC](https://www.nist.gov/publications/overview-face-recognition-grand-challenge), [NIST Color FERET](https://www.nist.gov/itl/products-and-services/color-feret-database) and [FFHQ authors](https://github.com/NVlabs/ffhq-dataset) are relevant data provenance records. FRLL Figshare returned403; Magic Passport repository403; Geirhos Nature redirect500. These remaining primary metadata checks are unresolved, not evidence the entries are incorrect.

Additional primary precedent worth a small related-work sentence, not a new experiment: [Borghi et al., A Double Siamese Framework for Differential Morphing Attack Detection](https://www.mdpi.com/1424-8220/21/10/3466), Sensors21(10):3466,2021, separates identity and artifact modules and discusses compression. Explain its D-MAD trusted-reference setting versus this S-MAD control framework. [Automated Artifact Retouching in Morphed Images With Attention Maps](https://doi.org/10.1109/ACCESS.2021.3117718),2021, is relevant to prior artifact concern; it does not reproduce the present same-person diagnostic. No exhaustive literature-search/novelty clearance claimed.

## Current official 2027 rules verified14November2026

Primary [CVPR2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines): eight content pages; references and mandatory LLM Usage Statement excluded. Statement follows main text, precedes references, names tools, affected parts and extent, remains anonymous. Supplement must be anonymous and self-contained; external links cannot expand review content. Profile/enrollment, fixed author list and reciprocal-review quotas apply. Authors must address human-data consent/ethics or explain absent review. Work first public on/after15September2026 is generally contemporaneous, but influencing work is prior work. Use current 2027 template; the local style's2027 header alone does not verify official-template identity. Root should bind downloaded official template/style hashes and actual paper ID before final formatting approval. No2026 rule or assumed supplement page/MB cap is certified here.

Primary [CVPR2027 dates](https://cvpr.thecvf.com/Conferences/2027/Dates): enrollment10November2026, paper16November, supplement23November, Anywhere on Earth. Dates do not extend NEXT's separate15November18:00CET archive deadline. Supplement later deadline does not establish permission to introduce post-paper-deadline experiments: obtain current explicit policy disposition if relying on new later results.

## Ordered executable handoff

1. Root/author verify existing OpenReview/enrollment receipt now; evidence unknown, not presumed failed.
2. Publication writer repair abstract F1 and prepare complete factual LLM disclosure F4; no main edit made by reviewer.
3. Supplement owner prepare an anonymized publication derivative with exact redaction log, neutral paths and preserved scientific platform distinctions; Astra rechecks fidelity/layout. Never mutate admitted internal reports.
4. Rights owner deliver source-specific image/derivative/consent disposition before any real face integration; otherwise retain schematics and permissible numeric-only plots.
5. Root keep operational bridge/NEXT/fresh-seed gates explicit; admit/review results only through existing scientific process. Do not strengthen contribution3 to satisfy a rhetorical target.
6. Complete bounded bibliographic holes/near-prior citation above, bind official 2027 template and paperID, add supplement pointers, independently review final text/PDF/source package across both variants. Keep WIP until its actual targets are resolved or transparently narrowed by author/reviewer disposition.

## Snapshot bindings

SHA256 of audited sources (shared tree may change after this snapshot):

- main.tex — 146ffd5db00f6f8c80de3b8be7566c4c6ea23289d4f358140984eacebedebaf6
- main_plotly.tex — ef083eafcfb71cc54a78f020e88afe02ca554d248d10dd3c5f1340e10fe41bd2
- method.tex — f0dfc2d59793c6c6be3577afb2fdc6bc6f6f39d058d073bb128c8afbe25d9b24
- results.tex — c3aeab0000bc94b4ddcdeb2fca0549540dc4c5d2beda53e10a75eb7ae08628aa
- related.tex — 55f6f19015412fdf1573475474704842b04fe85f1f00a197b96eb03464edc91f
- references.bib — 27c290e4bd045c68f0adc04502543834b0208645dd28c7cf5ec817795c27e470
- publication_wip.tex — d9a0d7e0697bf28dcd7b52031039797828e1a5944d3fbcd7fd51c89eecf3b982
- supplement_cvpr.tex — ed66434ceca97d01418f3d95c4790ef4ef68c26355ab4167dda6de4c59ae7138

Bounded audit delivered. No final GO, sealed access or benchmark release.
