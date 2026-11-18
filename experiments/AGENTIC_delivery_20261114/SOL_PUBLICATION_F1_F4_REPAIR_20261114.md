# F1/F4 bounded author repair — ready for independent review

Only manuscript_cvpr2027/main.tex changed, in two exact hunks (F1_F4.patch). Source was read afresh; compare-before-write asserted unchanged main and every copied input/style source before applying the repair. No commit, results, WIP, supplement, scientific score access, GPU action or cluster poll.

F1 main.tex:15: removed abstract MAD22 3.37/4.72 numbers; now: “The development-exposed MAD22 comparison establishes neither superiority nor morph-specific detection.” Full results.tex MAD22 table, landmark-only and GAN-specificity caveats remain byte-identical.

F4 main.tex:61: OpenAI Codex named with confirmed records/evidence-audit, experiment proposals, training/analysis/infrastructure code, coordination, literature, writing and experimental-data figure scope. Historical Claude/OpenCode imports are described as context. Explicit draft and author verification of historical usage remain. No model versions, invented historical extent, AI-generated source-face usage or completed author-verification claim. **F4 final compliance remains HOLD.**

Both variants compiled successfully with local installed latexmk/pdfLaTeX/BibTeX, using byte-identical current repo cvpr.sty, bibliographic style and figure inputs. The actual existing template compiled; this does not certify its identity against a freshly downloaded official template. Both have nine total pages, content ends on page8, LLM statement and references start on page8; page9 contains references only. No overfull boxes or undefined-reference warnings. All9pages rendered to contact sheets; full1500px views of1/8/9 inspected separately for each. No visible clipping, overlaps or new layout defect on inspected renders. WIP remains visible on page5.

Revised PDFs are source/main.pdf and source/main_plotly.pdf in this package; original manuscript-directory PDFs intentionally preserved pending review. Do not distribute stale original PDFs as reflecting this source edit. Root/Astra should review exact text diff, historical disclosure limitation, page1 and page8 for both variants, hash bindings and preservation of results/WIP. No submission or scientific GO.

Exact source/PDF hashes, command outcomes and scope: VERIFICATION.json; all immutable package member hashes: SHA256SUMS. SOURCE_SHA256.json binds copied input source. before/main.tex preserves prior main; F1_F4.patch is the exact two-hunk diff. The main and Plotly entry points share main.tex; main_plotly.tex itself was not changed.
