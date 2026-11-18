# Plotly and JavaScript publication figures

Dedicated visual-design task completed as comparison candidate; independent parent review requested.

Integrated current manuscript: `manuscript_cvpr2027/main_plotly.tex` defines UsePlotlyFigures and inputs main.tex. main.tex and results.tex each have one conditional figure switch. Default main.tex retains original TikZ, whose files are unchanged. Both PDFs have9pages, references beginpage8. New exports: figures/plotly_js/controls_overview_js.pdf and paired_evidence_plotly.pdf. Additional count_balanced_plotly.pdf is a standalone Table4 companion, intentionally not duplicated in main text.

Sources/dependency lock/rebuild directions are in figures/plotly_js/source/. Numerical provenance: existing figures/paired_evidence.csv/source_manifest.json for6contrasts; independent Batch-C reconstruction review for4values. No new raw score reads or experiments. Conceptual diagram updates obsolete unbalanced ablation number to count-balanced +0.048 with content/diversity limitation retained. This content delta is disclosed; not a pure style comparison.

Validation: alternate compile PASS, no overfull/unresolved references; existing lineno.sty UTF8 warning only. Rendered actual pages2/7 checked in color andpage7 grayscale. Embedded Arial ensures Unicode math symbols and readable vectors; source and rendered PDF inspected. Text sizes about8.2pt; exact extracted sizes in figures/plotly_js/verification.json. No face exports, generated evidence or unreviewed OCC1 maps.

Local deliverables: /Users/narolski/Documents/Codex/2026-11-14/na/outputs/publication_visual_design/ contains manuscript_plotly_js.pdf, manuscript_tikz.pdf, individual PDF/SVG/PNG/HTML figures, source ZIP and verification receipt. New plot export runtime uses Plotly.js offline+Puppeteer+SVG-to-PDFKit because local Kaleido failed initialization; no remote website automation. Future exports on a different font/Chrome host need visual QA.

Next: parent independently checks numerical mapping, scientific qualifications, print legibility, and chooses default figure route; do not call publication-ready merely from this author handoff. Existing WIP and scientific gates unchanged.
