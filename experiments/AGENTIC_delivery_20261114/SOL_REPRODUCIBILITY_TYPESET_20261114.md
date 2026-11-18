# Sol supplementary typesetting handoff

Observed 2026-11-14T16:00:51.526679+00:00. **Ready for independent review; NOT final publication GO.** Responds to ASTRA_REPRODUCIBILITY_REVIEW's typeset-table/real-template requirements. No main file or existing figure/TikZ/Plotly variant, original supplement fragment or WIP changed. No GPU, scheduler query, job, reader, scientific score analysis, model/image/score/sealed payload or canonical journal access.

## Deliverables

Remote self-contained review package directory: `manuscript_cvpr2027/supplement_cvpr_review_20261114/`.

- `supplement_cvpr.pdf`:43pages, SHA256 d6edc16afd4458e884caa12a750ccb4e5fe2f4aee599574dab56f744e5ab295b.
- `supplement_cvpr.tex`: SHA256 ed66434ceca97d01418f3d95c4790ef4ef68c26355ab4167dda6de4c59ae7138.
- `TYPESET_PACKAGE_MANIFEST.json`: SHA256 9d75d613be9c1e54d883012fe330e8e0d29af84e8d440cbaf27af1c8942cd58a;21members bound and independently rehashed after copying to gx10 (allPASS). Manifest itself is22nd package member.
- `supplement_implementation_trace_manifest.json`: separate24entry implementation/report/trace/source bindings, also at manuscript_cvpr2027 root; explicitly incomplete runtime/model/data closure.
- `supplement_table_cells.json`, `TYPESET_FIDELITY_CHECKS.json`, generator, four original admitted Markdown inputs, exact cvpr.sty and WIP copy, compile logs, four all-page contact sheets and README.

Local deliverables under `/Users/narolski/Documents/Codex/2026-11-14/na/outputs/`: `smad_supplement_cvpr_review_20261114.pdf` (samehash) and `smad_supplement_cvpr_review_20261114.zip` SHA25662d11416ce76d9b1a2fa64702b462c9a4f935d84856c10299057059c8c2889c5. ZIP includes complete self-contained sources/receipts, not model or score payloads.

## Actual template and fidelity

Used exact manuscript cvpr.sty and original10pt/twocolumn/letterpaper article with review-mode CVPR2027 header, Times/fonts, standard math/table/hyperref/cleveref packages. Text remains two-column; admitted tables use standard full-width table* floats at9pt without shrink-to-fit. Wide tables split into groups of at most3metric columns with repeated network IDs and explicit source/table/column/row identifiers in every caption. Source2narrative is complete; source3/4retain generated full initial/fresh/Sp/MS1tables; source1adds already-admitted pools denominator/failure metadata. Original repeated narrative/table values remain intentionally for auditability.33source tables,84panels,2580sourcecells including headers,3124displayedcells including repeatedheaders/IDs,16displayed sourceblankcells explicitly marked[blank]. No sourcevalue rounded/imputed/recomputed. Original Unicode math converted to equivalent TeX math. One indented original table and escaped verticalbars were explicitly handled; no unparsedlongtable remains.

Checks: all7local input/style/WIP/fragment files hash-match authoritative remote manifest. Every generatedpanel's exact header and row strings were checked against original source-cell strings via formatting-only conversion; all2580sourcecells retained by deterministic grouping. All84labels unique and present once. Generated fullsource TeX compiles twice with `/Library/TeX/texbin/pdflatex` exit0; latest log nooverfull/oversizedfloat/LaTeXerror. All43pages rendered with Poppler and inspected across4contact sheets; pages1,15,33,42 additionally fullpage850px; dense33/42at1500px. No observed clipping/overlap or unreadable shrunk table. Original9pt table typography retained. Sourcebound numerical correctness rests on existing original resultreviews, not this formattingcheck. No reader rerun.

## Remaining review and publication limits

Independent reviewer should reproduce sourcehashes/cellcoverage, inspect actual PDF and spot-check footnotes, source-specific intervals, blankMEDS cells, Bn401exclusion, freshseed/platform blocks, posthoc/registered qualifiers, unrounded vector ordering and visibleWIP. Compile command: run pdflatex twice from package directory. Generator requires Python3+Pandoc only for regeneration; finalTeX requires included cvpr.sty/publication_wip.tex and standardTeXLive. Scientific inference should not be recomputed for formatting.

This43page variant deliberately keeps the full admitted internal narrative plus complete tables. It is a comprehensive review record, not a claim that this length/editorial organization is final submission form. Original internal account/provider/path metadata remain transcribed and require anonymity/disclosure editing before submission; anonymous title/header alone does not remove identifiers. WIP preserved exactly, including targets now partly addressed. No provenance limit removed: final-arm person/pair census, evaluation fallback/denominator chronology, rights, exact convertedbase/source-byte equivalence and full environmentclosure unresolved. Methodcomparison, NEXT admission/fresh413–417confirmation, closedSPRINT5actualresults and tailNI limitations remain separate. Independent review required before integration or any publicationclearance claim.
