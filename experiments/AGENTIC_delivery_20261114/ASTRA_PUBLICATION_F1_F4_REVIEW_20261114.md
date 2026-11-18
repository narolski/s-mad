# Independent F1/F4 manuscript repair review

Astra, 14 November 2026. **GO_DRAFT_REPLACEMENT for the two exact newly compiled PDFs in the repair package. F4 final compliance and final publication remain HOLD.** Root may deliberately replace the stale manuscript-directory PDFs with these reviewed draft artifacts. This is not a submission release or approval to remove WIP.

## Content and scope

Independently verified all 32 SHA256SUMS entries, every source binding in SOURCE_SHA256.json, and current remote main/results/WIP/Plotly-entry hashes. Regenerated the unified diff from the preserved before/main.tex and source/main.tex: it equals F1_F4.patch exactly and contains precisely two hunks. No results, numerical tables, methods, figure sources or WIP changes are hidden in these two edits.

**F1: PASS.** The abstract replaces its abbreviated 3.37% versus4.72% MAD22 comparison with: “The development-exposed MAD22 comparison establishes neither superiority nor morph-specific detection.” This accurately avoids upgrading benchmark separation into identity-specific detection or superiority, while retaining the development-exposure qualifier. The full MAD22 table, four-family and landmark-only values, threshold-fragile NI discussion, GAN-specificity caveats and fixed-threshold limitations remain in the unchanged results source and visible page8. This repair does not conceal those results or reinterpret their estimates. The other abstract claims are outside this two-hunk review and were not newly numerically reproduced.

**F4: PASS as an explicitly provisional disclosure.** The paragraph names OpenAI Codex and its confirmed records/evidence audit, experiment proposal, training/analysis/infrastructure code, coordination, literature, writing/revision and experimental-data figure roles. These match the documented current workflow. It describes historical Claude/OpenCode records as imported context and explicitly requires the authors to verify full historical usage and extent before finalization. It invents neither model versions nor completed historical/author verification. “Figures derived from experimental data” does not claim generation of source faces. The wording must not be presented as complete historical disclosure or final venue-policy compliance; those remain HOLD.

## Both new PDF variants

Reviewed only `PUBLICATION_F1_F4_REPAIR_20261114/source/main.pdf` and `source/main_plotly.pdf`, not stale manuscript-directory PDFs. Inspected both hash-bound all-nine-page contact sheets and full page1/8/9 renders, then independently rasterized actual page8 of both PDFs with Poppler and extracted text from both actual PDFs. Both contain nine total pages: scientific content and the complete LLM Usage Statement finish on page8, references begin on page8, and page9 contains references only. WIP is visibly retained on page5. Page1 contains the repaired abstract and no removed MAD22 headline percentages. Page8 retains the MAD22 numbers and qualifications with the full new disclosure before References. No clipping, overlapping text or new layout defect was observed; both variants are suitable for author review as drafts.

The package uses the existing repository CVPR style and corresponding figure variants. This review does not certify that style against a newly retrieved official venue release, nor independently establish the current venue rules. Author build transcripts show successful final latexmk convergence. They contain initial-pass undefined-reference warnings, which occur before later successful passes; no final-pass undefined-reference issue or overfull box was found. No extra compilation or source rewrite was necessary for this bounded check. Screen inspection is not a physical print proof.

## Exact release scope and pins

| Artifact | SHA256 |
|---|---|
| main before | `146ffd5db00f6f8c80de3b8be7566c4c6ea23289d4f358140984eacebedebaf6` |
| main after/current | `75bd35e99d5254750863c40ac8af6649c403e3e059ed704062ac8ba420e5c5c6` |
| exact two-hunk patch | `cc215324e809fde4902e2a525e9cb6b0e1c9bf7ce098d1aa123de3c277f51539` |
| unchanged results.tex | `c3aeab0000bc94b4ddcdeb2fca0549540dc4c5d2beda53e10a75eb7ae08628aa` |
| unchanged publication_wip.tex | `d9a0d7e0697bf28dcd7b52031039797828e1a5944d3fbcd7fd51c89eecf3b982` |
| unchanged main_plotly.tex | `ef083eafcfb71cc54a78f020e88afe02ca554d248d10dd3c5f1340e10fe41bd2` |
| NEW source/main.pdf | `1e7a17d57c7b4d1901ef66c59e9bcbf437e737c25d58ed25b17abf6fb7d0d442` |
| NEW source/main_plotly.pdf | `2b425c099fd35a798f424692b35113b32d4990a712aea13ad973dd70373ef706` |
| package SHA256SUMS | `619e281ddbd4e39d4c56eab6a48eecaed9232ef3d7c64958fe8448fa7e546693` |

No required correction remains within the bounded F1/F4 draft repair. Remaining actions are root's explicit PDF replacement and author verification/finalization of historical disclosure; all other scientific, rights, template-provenance and publication gates remain separate. No main/WIP/author/package file was altered by this reviewer. No closed scientific payload, inference, GPU or scheduler access occurred. Local read-only package copy and independent page8 renders are in `work/publication_f1_f4/`.
