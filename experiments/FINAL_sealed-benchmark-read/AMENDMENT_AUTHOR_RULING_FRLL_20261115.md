# AUTHOR RULING — FRLL-Morphs read unsealed (2026-11-15)

This file registers the upoważnionego autora ruling, received in this continuation session at
2026-11-15T19:16:30Z (UTC machine clock), and the execution protocol that keeps it auditable.
Verbatim ruling (operator message, translated register preserved):

> Autor autoryzuje odczyt FRLL-Morphs w celu przygotowania tabel wynikow do submisji. Motywacja:
> zamkniecie publikacji; tabela wynikow tego potrzebuje. Autor ocenia, ze nie narusza to zasad
> pracy naukowej ani wymogow CVPR.

Plus the operator's execution order (same timestamp): full closure locally on the DGX GB10
(this machine, `/home/narolski/smad-next`): amendment + this file with SHA -> reproduction
checks / roster FREEZE with SHA256 -> runtime probe on a sample -> FULL read -> results cells
with receipts; no phase gates (granted already); one-liner report after each milestone;
WAŻNE: no new training, Vast.ai stays cancelled, WCSS/Athena only if GB10 cannot run a phase.

## What this changes in the FINAL registration (experiments/FINAL_sealed-benchmark-read/prereg.md)

- Section 1 ("Scope"): the sentence "FRLL-Morphs, FEI gtest, MorDIFF, ... are not scored and not in
  the pack. They stay sealed for a later method." is **amended for FRLL-Morphs only** by the
  author's ruling above: the FRLL-Morphs read is unsealed today. FEI gtest, MorDIFF, the six DiM
  families, H1 and the FRLL benign variants **remain sealed** (untouched by this amendment).
- Section 7 ("Unavoidable exposure"): already true and retained; the FRLL-Morphs morph scores now
  additionally exist after this read. The disclosure paragraph of the paper gains the sentence:
  "The FRLL-Morphs morphs were scored only after the paper's tables were requested, on the frozen
  networks only; the 204 FRLL photos were already exposed as MAD22's genuine side."
- Section 8 comparison rows and Section 9 one-read machinery are **not changed** (they govern
  corrected MAD22). The FRLL read below is a separate registered read with its own freeze.

## Registered FRLL-Morphs read v1 (scope, fixed by this amendment before any score)

**Population (S form, native).** The external FRLL-Morphs benchmark, families AMSL, FaceMorpher,
OpenCV, StyleGAN2, Webmorph, against the 204 raw FRLL photos (102 persons, _03 neutral + _08
smiling):
- Rows and raw paths per the registered RS1 manifest `/mnt/t7/smad_next/RS1/manifest.csv`
  (sha256 bb397fea07613240bcb85796ee80bfd6492f47d9afdacc649fa228bfd2e7aa13), sets
  M_amsl (2,175), M_facemorpher (1,222), M_opencv (1,221), M_stylegan (1,222), M_webmorph
  (1,221), G_raw (204): 7,265 rows in total.
- Benign-variant rows of these families (`_jpeg*`, `_blur1`, `_chip` frames), E7/resmatch FRLL
  pools, MorDIFF and the DiM families are NOT in this read.
- Row-level SHA256 of every input and of every frame is recorded AT FREEZE (create-only receipts;
  amendment precedes any score).

**Detectors.**
1. Our frozen Sb networks, seeds 403–407, result tars pinned in the FINAL registration, section 10
   (`/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s40{3..7}.tar`). Scored through the registered
   `src/PN1/rescore.py` (pin 6f6eede7e…), no flip TTA, on the existing native aligned frames
   `smadcvpr_data/eval/frllm/<family>/<name>_orig.png` (unchanged existing aligner outputs).
2. Released detectors MADation ViT-B/16, MADation ViT-L/14, MixFaceNet-MAD (and, printed beside,
   FE/FS rows where present): the **existing registered RS1 own-crop production scores**
   `/mnt/t7/smad_next/RS1/results_rented/prod_v1_rented/scores/` and `prod_v2_rented` are READ,
   not rescored. Per RS1 result amendment 7, the FaceMorpher cell uses variant 2 only ("release
   crop script fails on these files" for variant 1). The RS1 a46 corrective files
   (`scores_rel_madation_vit{b,l}1*__a46.npz`) are printed as the variant-consistency side record.
   These scores were computed 8–12 Nov 2026 during the reviewed RS1 audit; no new exposure is
   created by reading them, and the exposure is disclosed regardless.
3. SelfMAD (hrnet_w18 release): its FRLL-Morphs morph rows do not exist (RS1 scored it on the
   genuine pool and MorDIFF ladder only). They are scored once, now, on the DGX GB10, with the
   registered RS1 score.py byte copy (pin 56bb1244…, listed in the FINAL pins) via
   `--mode own` (dlib 81 landmarks, 384 px, the release's own preprocessing), on the same raw files
   the manifest pins, no TTA.

**Metrics and thresholds (all registered sources, unchanged).**
- `src/FINAL/final_metrics.py` (pin 9c202f97…): EER (%), AUC (Mann-Whitney, ties half), exact
  Clopper–Pearson 95% intervals.
- Own rule: logit > 0 (our networks; the releases' stored key; SelfMAD probability > 0.5 form).
- τ_FFHQ (dev-frozen, FFHQ genuine pool, never a training source) from the committed
  `experiments/FINAL_sealed-benchmark-read/final_thresholds.json`
  (pin 0293c3adad2487114fded4555fd235a6ad9946c993381ea1e3f702e6851983d4): APCER/BPCER-style
  flag rates printed per family (attack-miss and genuine-FA at development thresholds).
- Uncertainty: the registered two-way person bootstrap — 102 FRLL persons, pigeonhole
  multinomial (genuine photo weighs its person; a morph weighs the product of its two
  contributors), B = 2,000, `numpy.random.default_rng(20261121)`, same draws for every detector.
- **This read is descriptive.** No superiority/verdict tests are registered on FRLL-Morphs
  (section 4 tests govern corrected MAD22 and are not moved here). No sentence may say
  "state of the art", "generalises" or "shortcut-free" on these numbers. The FRLL families carry
  no AD4 saturation statement here.

**Outputs (create-only).** `/mnt/t7/smad_next/FRLL_READ_V1/`: per-detector score npz, the frozen
manifest copy, `FRLL_READ_RESULTS.json`, `FRLL_READ_TABLES.md`, `COMPLETE.json` with sha256 of
every artifact. Reports: `experiments/AGENTIC_delivery_20261114/FRLL_READ_*` dated files with
independent numeric checks (recounts from the npz, not from the summary).

**Stop rules (unchanged).** No new training anywhere. If a phase cannot run on the GB10 the
failure is reported (WCSS/Athena fallback only for a named, registered step). Pending cells stay
pending; no numbers are imagined; the 204-photo MAD22 exposure sentence is printed regardless.

## Execution protocol (ruling obligations)

1. Freeze (manifest + row SHA256s + weight/script pins) committed BEFORE scoring; probe (8 rows,
   already-exposed genuine, selfmad own + one release, retag runtime) BEFORE the full pass;
   full read then runs without further author gates, per the operator order.
2. One-liner report after each milestone: amendment, freeze, probe, read, tables, manuscript push.
3. Manuscript targets: `results.tex` FRLL paragraph + Table 5 family cells (currently 5×5 HOLD),
   disclosure sentence of section 7 above, all qualifiers attached. Experimental receipts stay in
   smad-next; the manuscript repo receives tex-only changes.
