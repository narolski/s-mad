# Identity-shrinkage triage: how average is a morph, and what is the ceiling [ID0]

Written 11 Nov 2026, about 15:45 CET, before any ID0 statistic was computed. Read before this page: data counts
only (fit-person counts, file lists, manifest columns, AR1 gate G-b JSON, AG5 result page). No feature of any image
has been extracted for ID0 and no AUC of any ID0 statistic exists. Owner: ID0 hypothesis owner. Code `src/ID0/`,
large outputs `/mnt/t7/smad_next/ID0/`, results here.

Implements theme K6 of `ideas/CONSOLIDATED_v1.md`: physics idea 0 "Identity-subspace shrinkage test (ISS)" with
its first_experiment_tonight, and the identity lens's GEO-0 with identity ideas 0 (virtual-morph head and ceiling)
and 1 (shrink-law audit). Fixed reads and falsifiers are copied verbatim below (section F); where two entries
disagree on a threshold the stricter one is kept and this is said.

- **Hypothesis (plain words):** a morph averages two faces, so in any space where identity is roughly linear it sits
  closer to the average face than a real person does (identity variance falls to (1+c)/2 for contributor
  similarity c). A statistic fitted on genuine photos only (no morph, no render in the fit) can read this from one
  image for landmark, GAN and diffusion morphs, with a ceiling predictable from the genuine-only fit.

## Data

- **Fit persons (genuine only).** AR1's candidate frames (`src/AR1/pool.py: candidates()`, imported unchanged: the
  record's 73_delin_align 512² frames with 106-point `.tem`; train/bona_frgc, arms/r6_frgc, train/bona_feret), minus
  every person in `experiments/AR1/pool.csv` as host (pid) or partner (B_pid) (references R are photos of hosts),
  minus every validation-reserved person by the existing rule `prep_train.is_val(subject)` (sha1 "smadcvpr:<subject>"
  mod 10 == 0; key verified against the `val` column of `train.csv`: 230/230 FERET and 197/197 FRGC val rows match).
  No FRLL person (not in the candidate set). All expressions and sessions are kept (neutral-only would leave about
  one photo per person); within-person pixel duplicates dropped by AR1's rule (`pool.fp`, mean |diff| < 2).
  Counted before this page: 776 persons (FERET 710, FRGC 66), 1,720 photos before duplicate removal; 546 persons
  with at least 2 photos, but only 47 with at least 2 capture sessions. So the "within-person" covariance is
  mostly within-session (FERET fa/fb expression change, FRGC same-session stills). Disclosed as a limitation.
- **Validation-reserved persons in the AR1 pool (fact found while counting):** 8 of the 536 AR1 hosts satisfy
  `is_val`. ID0 drops every AR1 image whose host or partner is such a person from every ID0 contrast (count
  printed) and reports this to the lead; AR1 files are not touched.
- **Evaluation sets (no image is made; existing files only):**
  - AR1 primary pool (FRGC + colorFERET, 536 hosts, `/mnt/t7/smad_next/AR1/manifest.csv`): R0 = H; R2 = tool(H, H);
    R2w = warp-only; R3 = tool(H, S); R3m = mirror self-morph; R4 = tool(H, B); NC = tool(S, H); OpenCV (first
    tool) and FaceMorpher; graded FaceMorpher-library set m000 to m050 (300 hosts). Sources H, S (and B = S of the
    partner) from `pool.csv`.
  - AR1 FRLL pool (102 persons, same rungs; H = p_03, S = p_08): descriptive.
  - FRLL-Morphs published OpenCV / FaceMorpher morphs as prep_eval frames (AR1 manifest `R4f`, 1,221 / 1,222) and
    FRLL native frames (`R0f`): descriptive, benchmark side.
  - MorDIFF control set A43 (`/mnt/t7/smad_heldout/a43/data/a43/stored/`, identical storage for every group): E
    photos (204), D20 reconstructions (204), C20 same-person mixes (102), B20 two-person morphs (200), A published
    MorDIFF morphs (200); also D, C, B (100 steps). DiffAE arm only: E as DiffAE's own aligned input (X3 `a256`),
    D20 / C20 / B20 / B as the generated `png256` files (DiffAE-native 256² frames); A only as stored crops.
  - FR arm only, from `/mnt/t7/smad_heldout/a46/feat/a46_feat.npz` (existing glintr100): published MorDIFF (1,000),
    DiM-C, Greedy-DiM, Greedy-DiM-S (500 each), X3 reconstructions `rec` and aligner copies `a256`, a43_B / a43_D.
  - StyleGAN3: H3 morphs `h3_sg3` orig (423) and one-identity renders `h3_bona` orig (423) from
    `h3_sg3/data/manifests/h3sg3.csv`; A37 latent-spread-matched renders `a37spread` orig (423). Contributor
    embeddings for the FR arm: glintr100 of the existing 112² CASIA crops in `h3_sg3/work/h3_inputs.npz`.
  - Photo-history control (R0 vs R1): FRLL native frames `frllm/frll_bona/0/orig` (204) against the existing E7
    frames (`resmatch`) of eval.csv for opencv, facemorpher (frllm), stylegan (frllm), mordiff (mordiff): the four
    primary control families; dim_c, greedy_dim, greedy_dim_s, amsl, webmorph descriptive.
  - Benchmark pair similarity (glintr100 cosine of the two contributors' FRLL photos, a46 `raw` gallery): FRLL-Morphs
    (5 families, names `aaa_bbb`), MorDIFF, DiM families, corrected MAD22 (5 families, names from the directory
    listing of `marco_owncloud_20261109T103840Z/author_files/original_sorted/`), AR1 `cos_HB`, H3 pairs.

## Arms and features

| Arm | Feature x | Device |
|---|---|---|
| L, landmark shape | 106 `.tem` points, Procrustes-aligned (pixel-blind; exact shapes, no image) | CPU |
| FR | glintr100 unit embedding (512), registered X3 route via `src/AR1/fr.py` unchanged; existing embeddings reused where they exist | GPU, small |
| CLIP | timm `vit_large_patch14_clip_224.openai`, num_classes 0, pooled 1024, model's own transform, offline cache | GPU |
| DINO | timm `vit_large_patch16_dinov3.lvd1689m`, num_classes 0, pooled 1024, model's own transform at its default size | GPU |
| DiffAE | z_sem = `LitModel.encode` (EMA semantic encoder only) of the pinned DiffAE FFHQ256 checkpoint (sha 9bd2ba9e…), repo commit 00c57d3f, repo's own `ImageDataset` transform (256), run with `/mnt/t7/thirdparty/diffae_venv/bin/python -I` | GPU |

Feature extraction applies only each model's own input transform in memory; nothing is written as an image.

Landmark arm shapes (exact): R0 = tem_H; R3 = mean(tem_H, tem_S) (this is also the exact shape of R2w and of NC at
0.5); R4 = mean(tem_H, tem_B); R3m = mean(tem_H, mirror tem_H) (AR1's mirror `.tem`); dose (1−m)·tem_H + m·tem_B,
m = 0, 0.1, …, 0.5, on all hosts. Averages are taken in frame coordinates (the tools' geometry), then aligned.
Benchmark side (descriptive): exact mean shapes of FRLL-Morphs and corrected MAD22 pairs from the AR1 `frll_src`
`.tem` of the two contributors, against single FRLL shapes. Procrustes: generalised Procrustes (translation, unit
centroid size, rotation, no reflection) on the fit shapes; every other shape aligned to the final fit mean.

## The statistic (same for every arm; fitted on the fit persons only)

1. Centre by the fit-photo mean; PCA on fit photos; keep k = the smallest number of components explaining 95% of
   the variance, capped at 64. (Descriptive sensitivity: k = 32 and k = 128 where available.)
2. S_w = pooled within-person covariance (persons with at least 2 photos, dof Σ(n_p − 1)), ridge 1e-3·tr(S_w)/k;
   S_b = covariance of person means minus mean(1/n_p)·S_w. Generalised eigenproblem S_b v = λ S_w v, Vᵀ S_w V = I,
   z = Vᵀ(x − m). Under the model a single capture has variance λ_j + 1 per direction.
3. **Primary score ISS** (higher = more morph-like): J = {j : λ_j > 1} (persons differ more than sessions);
   Q = Σ_{j∈J} w_j z_j², w_j = 1/(λ_j/2 + 1) − 1/(λ_j + 1) (the log likelihood ratio "midpoint of two unrelated
   people, session unchanged" against "one capture", physics model with c0 = 0); ISS = −Q.
   Descriptive: TYP = −Σ_all z_j²/(λ_j + 1) (total typicality); SES = −Σ_{j∉J} z_j²/(λ_j + 1) (session read-out).
4. **Predicted AUC (genuine-only):** physics closed form AUC = Φ(√(d/2)·(1−s)/√(1+s²)),
   s = ((1+c)/2 + n)/(1+n), with d = |J| and n = |J| / Σ_{j∈J} λ_j; and the spectrum form: AUC of −Q between
   simulated single captures (variance λ_j + 1) and morphs (variance λ_j(1+c)/2 + 1) with the fitted λ, 200,000
   draws. Contributor similarity in the arm's own space per pair: c_pair = (z_A·z_B)_J / Σ_J λ_j (unbiased under
   the model), z of the contributors' source images; the set's c = median c_pair. Both forms printed for
   c = 0, 0.1, …, 0.9 (the ceiling curve) and at each evaluated set's own c.
5. **FR ceiling of the identity entry:** Λ = √(μᵀ Σ⁻¹ μ), μ = mean fit-set unit embedding, Σ = Ledoit-Wolf
   covariance of the fit embeddings; ceiling(c) = Φ((κ(c) − κ_neg)·Λ/√2), κ(c) = √(2/(1+c)), κ_neg = 1 (photo) or
   κ(c_twin) (same-person morph), printed per cosine bin (0 to 0.6 by 0.1) beside the benchmark pair-cosine ranges.

## GEO-0 reads (FR arm; the fidelity and linearity reads also in CLIP, DINO, DiffAE)

1. Fidelity F = cos(e_built, normalise(e_A + e_B)) per built set (R3, R4, NC, R3m with e_B = e_H, R2w, graded
   levels with weights (1−m, m), a43 B / B20 / C20, published MorDIFF and DiM, H3 morphs). In CLIP, DINO and
   DiffAE: the centred analogue cos(x_built − m, (1−a)x_A + a·x_B − m). DiffAE cycle read: the same for
   Enc(B20) against the midpoint of Enc(a256_A), Enc(a256_B), next to Enc(D20) against Enc(a256 source).
2. Mean-direction gain G = mean⟨e_built, u⟩ / mean of the sources' ⟨e, u⟩, u = unit fit-set mean direction, against
   the predictions 1.27 (R4, c = 0.23) and 1.03 (R3, c = 0.87), and against κ(c) at each set's own median cosine.
3. Virtual head: L2 logistic regression (sklearn, standardised, C = 1) on glintr100 unit embeddings of the fit
   persons only. Positives: virtual morphs normalise(e_i + e_j) of two photos of different persons of the same
   database (20,000 seeded pairs). Negatives: every single fit photo and every virtual twin normalise(e_i + e_i′) of
   two distinct photos of one person; classes weighted equally. In-domain virtual AUC: 5 folds by person (items
   built only within a fold), pooled out-of-fold; per cosine bin (virtual morph vs single photo) = the measured
   identity-only ceiling. The head fitted on all fit persons is applied unchanged to real sets.
4. Λ and the ceiling per cosine bin (above).

## Contrasts printed for every arm (positive = second-named, higher rung)

AUC with the 95% two-way person bootstrap of `a41_read.Draw` (B = 2,000, seed [20261111, 1], via `src/AR1/stats.py`
unchanged; persons = AR1 pids, FRLL persons, H3 pair index):
- control: FRLL native vs E7 (four primary families, others descriptive);
- one-photo output vs two-person morph: R2 vs R4 and **R2w vs R4** (OpenCV primary, FaceMorpher), **D20 vs B20**,
  D vs B, h3_bona vs h3_sg3, a37spread vs h3_sg3; FR also rec vs published MorDIFF and DiM families;
- same-person vs two-person morph: R3 vs R4, R3m vs R4, C20 vs B20;
- photo vs morph: R0 vs R4, E vs B20, E vs A, FRLL R0f vs published R4f; one-photo vs same-person: R2w vs R3, D20 vs C20;
- negative controls: NC vs R3 (expected 0.5), rec vs a256 (FR, from a46);
- dose: graded m000 to m050, mean score per level, Page trend test (blocks = hosts, predicted order increasing),
  AUC(m vs m000) per level; landmark arm also the exact-shape dose on all hosts;
- shrink law: Spearman ρ between the score and L = 2a(1−a)(1 − cos(A, B)) (glintr100 cosine of the contributors'
  source photos) within each morph set (AR1 R4 per tool, graded set pooled over levels, a43 B20 and B, published
  MorDIFF, H3 morphs), two-way person bootstrap; inside neutral–neutral pairs where the expression is known
  (MorDIFF/A43 names carry it). Power check: the same ρ for the reference-based oracle 1 − cos(e_built, e_ref)
  (AR1: independent reference R of the host; FRLL: the host's other-expression photo; H3: the host's source crop,
  labelled "source-photo reference").
- predicted vs observed AUC beside each photo-vs-morph and one-photo-vs-morph contrast.

## F. Fixed reads and falsifiers (verbatim; fixed before any statistic)

Physics idea 0 (ISS), falsifier, verbatim: "Best arm R2-vs-R4 AUC below 0.65 on both a43 (D20 vs B20) and AR1 (R2w
vs R4, OpenCV); or genuine R0 vs R1 (FRLL E7 frames) AUC outside 0.40 to 0.60; or no monotone rise over m000 to
m050 (Page p above 0.05). For the exact-landmark arm alone: R0 vs R4 below 0.60 kills shape shrinkage."

Physics first_experiment_tonight, verbatim: "Print for every arm: R0 vs R1 (must sit in 0.45 to 0.55), R2 vs R4,
R3 vs R4, R2 vs R3, the dose trend, and the AUC predicted from genuine-only statistics next to the observed one.
Decision: any arm at or above 0.75 on R2 vs R4 with a clean R0 vs R1 becomes the global head of the single network
and the paper has a first-principles ceiling curve; all arms below 0.65 means identity shrinkage is not readable
from these features and the generator half of the method should be declared a measured limit."
Disagreement: the R0 vs R1 band is 0.40–0.60 in the falsifier and 0.45–0.55 in the tonight text (and in GEO-0 and
identity idea 0). **The stricter band 0.45–0.55 is used**: an arm whose native-vs-E7 AUC (point estimate) leaves
0.45–0.55 in any of the four primary control families "reads history" and cannot pass. The landmark arm takes
landmark files, not images, so R0 vs R1 is 0.5 by construction there; this is stated, not counted as a pass.

GEO-0 (identity first_experiment_tonight), verbatim reads: "(1) Fidelity F = cos(embedding of the built image,
normalised sum of its two source embeddings), for twins and for morphs. At least 0.90 means the midpoint model
holds; 0.75 or less means the off-span part dominates, and then the question is whether that part is larger for
morphs than for twins. (2) Mean-direction gain of R4 and R3 relative to the host photo against the predictions
1.27 and 1.03. (3) A head fitted only on virtual morphs and virtual twins of FRGC and colorFERET source embeddings
(5 folds by person), applied unchanged to real AR1 R4 vs R3 and R4 vs host photo, to a43_B vs a43_D and to
published diffusion morphs vs reconstructions, with controls native vs E7 and reconstruction vs aligner copy. Go
for the identity component: at least 0.65 with lower bound above 0.60 on both landmark and DiffAE, controls inside
0.45 to 0.55. Kill: 0.55 or less on both. (4) Lambda and the ceiling per cosine bin, printed beside AD1's R2 vs R4
values."

Identity idea 0, falsifier, verbatim: "Virtual-trained head at or below 0.55 (upper bound below 0.60) on both AR1
R4 vs R3 and a43_B vs a43_D while its in-domain virtual AUC is at least 0.70: real morphs do not follow the midpoint
law in FR space, drop the idea and keep only the ceiling. Any control outside 0.45 to 0.55: the by-construction
claim is false." Disagreement: GEO-0's kill ("0.55 or less on both", no interval condition) fires more easily than
idea 0's ("at or below 0.55 (upper bound below 0.60)"); **the stricter, GEO-0's, is used** (point estimate ≤ 0.55
on both AR1 R4 vs R3 (OpenCV) and a43_B vs a43_D kills), with idea 0's in-domain condition (virtual AUC ≥ 0.70)
printed beside it. a43_B / a43_D are the 100-step sets (as in a46); the 20-step pair is printed beside.

Identity idea 1 (shrink law), verbatim: "For a detector's identity reading: correlation upper bound at or below
+0.10 in every generator family means no identity reading there. For the tool itself: if the reference-based
oracle's own correlation is below 0.3 in a family, the similarity range there is too narrow and the audit is void
for that family." Applied to each arm's ISS score (and to the virtual head in FR) in place of a detector score.
The released-detector audit of idea 1 (existing score files) is not part of ID0.

## Guards

- No morph, render or FRLL image in any fit; FRLL evaluation only; is_val persons excluded everywhere.
- Native vs E7 control per arm (above); NC vs R3 and rec vs a256 negative controls.
- No image is made; feature models in eval mode, frozen, offline cache; third-party code with `python -I`,
  checkpoints with `weights_only=True`.
- Pool shift disclosed: the fit pool is FRGC/colorFERET 512² eye-aligned frames; A43 (256-px DiffAE crops) and H3
  (1024² FFHQ-aligned renders) are other pools, so their absolute level against the fit mean is shifted; the
  within-set contrasts (D20 vs B20, h3_bona vs h3_sg3) are not affected by a common shift.

## Stop rule and budget

GPU at most 30 minutes in total, under 12 GB, `nvidia-smi` checked first; at most 6 CPU processes (data loaders
included); no WCSS, no Vast. If the GPU refuses allocation, retry up to 5 times, then report the arm as not run.

## Commands (each tested on 8 images with its real command line before the full run)

`src/ID0/lists.py` (fit set and evaluation lists), `src/ID0/feat.py` (glintr100 + CLIP + DINOv3, spark venv),
`src/ID0/feat_diffae.py` (DiffAE venv), `src/ID0/iss.py` (statistic), `src/ID0/analyse.py` (all reads, JSON/CSV).

## Pre-run review

Not run (owner brief does not require it for a CPU/feature triage; flagged to the lead).

## Result

`experiments/ID0_identity-shrinkage-triage/result.md`.
