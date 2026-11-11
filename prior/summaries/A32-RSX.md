# A32-RSX: resolution shortcut in published diffusion-morph results

Terms: EER = equal error rate. E7 = resolution-matched genuine pool. MorDIFF, Greedy-DiM = diffusion morph sets. SMDD = synthetic training set.

- **Question.** Do near-perfect published scores on MorDIFF and Greedy-DiM collapse when genuine photos are resolution-matched?
- **What was done.** Registered 4 Nov 2026, 0.1 GPU-hours. One new job scored the official SelfMAD release with its own preprocessing; everything else re-read existing score files. Compared native and E7 EER; also a MADation recipe retrain on SMDD (8 seeds), a MixFaceNet retrain (5 seeds) and 26 W3 configurations.
- **Result.** SelfMAD release, own preprocessing: MorDIFF 2.5% native to 61.3% under E7; Greedy-DiM 8.4% to 90.7%; FRLL AMSL 2.9% to 33.3%. Same release through our pipeline: MorDIFF 6.5% to 61.3%, Greedy-DiM 29.4% to 89.1%. MADation recipe (SMDD): MorDIFF 35.1% to 28.6%, never low, so not reproduced. W3 median MorDIFF change +9.32 (below the +10 bar).
- **Verdict.** Registered rule gave "neither" for the combined hypothesis: the SelfMAD release is inflated, the MADation retrain is not reproduced. The later A41 rules upgrade the SelfMAD finding (see `A41.md`).
- **Caveats.** Evaluated on our 512 px aligned PNGs, not raw benchmark files; sets were already seen in design; the A40 review changed the wording: the cue is "genuine photo processing history, cue not identified", not "resolution" or "fine-detail loss". One network.
- **Sources.** `experiments/A32-RSX_resolution-shortcut/README.md`, `meta.json`, `raw/rsx_read.md`, `raw/rsx_read.json`; `experiments/CONCLUSIONS.md`, section "What we can claim about shortcuts".
