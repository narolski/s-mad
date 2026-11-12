# Pre-run review: DG1 amendment draft, SAME_orth / X_corr rungs

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited. Verdict: STOP as drafted.

## Pre-run review: DG1 amendment draft, SAME_orth / X_corr rungs (H-A causal test)

Read-only. Nothing in the repo was edited. My one CPU check (scratchpad copy of the shard-2 saved codes, 67 hosts) is in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/orth/ana.py`. I did not open valx.csv, FST, A12SP or any score file.

### Verdict: STOP as drafted. Run the zero-GPU analysis first, then redesign.

The orthogonalisation is mathematically clean, but it hardly changes the input and it does not remove the shared structure that H-A is about. The registered falsifier would therefore almost certainly fire because of how the rung is built, not because H-A is wrong. The cost is small (about 1 USD). The issue is that the result could not be interpreted.

### Findings, most severe first

**F1 (blocker). SAME_orth is a 1.7% change of the noise map and keeps nearly all the same-person correlation.**
- The draft projects out only the single direction a, the whole-map component (draft:23). On 67 hosts of shard 2:
  - cos(a, b) has median 0.034. Removing it changes the slerped map by a median of 1.7% of its norm (5–95%: 0.4–4.4%). X differs from SAME by 98.6%.
  - The correlation that matters survives:
    - 8×8 low-pass cosine of a and b: 0.234 before, 0.196 after (X: 0.051).
    - Lowest frequency band cosine: 0.41 before, 0.38 after (X: 0.16).
    - Only the top band flips, from 0.021 to −0.014.
- Why this happens: at α = ½ the slerp is (a+b)/(2cos(θ/2)). θ only rescales, so the "amplification" is just the coherent sum a+b. If a = s+n₁ and b = s+n₂, then b′ ≈ (1−c)s + n₂ − c·n₁ with c ≈ 0.034, so 97% of s is still added coherently.
- So SAME_orth tests the whole-map angle θ (a one-number summary), not "coherent shared structure". The expected outcome is SAME_orth ≈ SAME, which triggers "H-A falsified" through draft:45 (L on SAME vs SAME_orth within [0.40, 0.60]).
- X_corr has the same problem: a 1.55% change (median). It will look like X, so the secondary prediction (draft:48) fails by construction as well.
- **Fix:** do not register these rungs as the test of H-A. Either:
  - (a) rename the hypothesis H-A-global ("the whole-map angle, not the shared structure") and predict SAME_orth ≈ SAME; or
  - (b) redesign the manipulation to remove the correlation in every frequency band. Band-wise orthogonalisation with the power per band kept is the obvious option, but it is filtering code on the latent and needs approval (F4).

**F2 (major). A cheaper analysis would show whether the rung is worth doing at all.**
- Per host, compute the band-wise and low-pass cosines of (a, b) and (a, p) from the saved codes. Then relate them, within SAME and within X, to FZ2's Laplacian and P_XS scores, and compare how well each separates X from SAME against θ (0.916).
- Saved codes: shards s2–s6 are local (`/mnt/t7/smad_next/DG1/rented_results/DG1_addon_s{2..6}_codes.tar`, 335 hosts). s0 and s1 are on Athena.
- Cost: zero GPU, minutes of CPU. Label it post hoc and register it in FZ2 before computing.
- If low-band cosine predicts sharpness and θ adds nothing beyond it, H-A (shared structure) is supported. That is probably all the paper needs.

**F3 (major). Codes reuse versus re-encoding is contradictory, and one shard's codes are gone.**
- Draft:34 says codes are re-encoded in-process. Draft:56–57 prices reuse at 0.3 GPU-h.
- `codes_not_copied.sha256` lists s7, and there is no s7 codes tar locally. The rented machine was released (NOTEBOOK 03:13), so s7's codes exist nowhere.
- Pick one:
  - re-encode everything in-process (1.6 A100-h, self-contained shards; my recommendation); or
  - reuse s0–s6 and re-encode s7, with REC/SAME/X rendered from the same codes in the same process.
- Platform: rented re-renders match Athena byte for byte in 0 of 1,608 cases. The largest P_XS difference is 0.63 logit and the largest Laplacian difference is 2.1 (`platform_reproducibility_fz2.json`). Both are as large as the expected SAME_orth effect. So every reading must be in-process X/SAME/REC against the new rungs, never against add-on images.
  - Draft:43 says "X vs SAME_orth" without saying which X. Write "in-process X".

**F4 (major, author item). Changing the noise map before decoding is outside the approved operations.**
- The DG1 prereg (line 9) says "Generator (unchanged in every part that touches an image)". Amendment 2 (prereg ~157) allowed only halves of the unchanged `interp()` output. The noise map decides the image.
- This is not blur, resampling or JPEG code, but it is a new image-generating operation. The open question on half-exchange images (07_DECISIONS_NEEDED.md, "Still open" 3) shows that such cases go to the author.
- Ask: "May we build diagnostic-only diffusion images whose input noise map is edited (projected or band-orthogonalised) before the unchanged slerp and render? They would never be used for training or as attack or benchmark rows." Any band-wise (FFT) variant needs this answer explicitly.

**F5 (major). The reading rules need fixing before any code exists.**
- SAME vs SAME_orth is a paired contrast of near-identical images. An unpaired AUC around 0.5 says little. Register the paired difference in Laplacian and P_XS per host, with a person-bootstrap CI, plus a minimal effect such as "Laplacian drops by at least 50% of the SAME−X gap (128→96)".
- The falsifier uses point estimates only. State the interval rule for both branches.
- The FZ2 reading section must be registered in FZ2's prereg, not only in the DG1 amendment.

**F6 (minor). Numerics.**
- `interp()` recomputes θ in float32 from the cast b′ (dg1_addon.py:212). Check |cos| on the float32 tensor that interp actually receives, with a tolerance of 1e-5 rather than 1e-6.
- Pass b′ in as a synthetic source key in `xT` (for example `<S>__orth`), so that `interp()` stays byte-identical.
- Norm is preserved: SD 1.0131 → 1.0131, mixed map 1.0130 → 1.0130. At θ = π/2, sin θ = 1, so slerp is well-defined and the decoder does not leave the distribution. That part of the draft is fine.

**F7 (minor). X_corr leaks the host's map.**
- p′ adds cos θ_s·‖p‖·â, a 3.4% copy of the host's whole map (including its private noise), not structure shared with b. Document this.
- Its size is too small to matter for identity: z is unchanged and the change is 1.55%.

**F8 (minor). Operations.**
- A new lease needs its own 8-image equivalence gate (amendment 3 is per machine). Draft:35 assumes the gate already passed.
- Put the new modes in a new file, or prove that the existing modes are byte-identical by re-rendering 8 add-on items. The registered `script_sha256` is logged per run.
- The draft writes REC/SAME/X into a new `gen_run` (fine). Record the jobs-list and script sha256s in the registration.

**F9 (minor). Disk.**
- /mnt/t7 has 30 GB free (99%). That is already below the lead's "keep 50 GB free" rule (DG1 README:246), and drive.sh copies codes back only above 56 GB.
- The images are only about 0.2 GB, but the lead must waive the rule explicitly. Codes will not be copied back.

### Improvements (value per GPU-hour)
1. Band-wise and low-pass cosine analysis on the saved codes, as in F2. 0 GPU; register in FZ2. This likely settles H-A.
2. If a causal rung is still wanted after (1): band-orthogonalised SAME (the cosine of every band set to zero, power per band kept). About 1 USD. Needs the author's answer (F4) and a new registration.
3. Keep SAME_orth only as a labelled "whole-map angle" control, with the prediction SAME_orth ≈ SAME.
4. For the paper, this is a side path. "Render-path separability, one generator" is already supported by NOISES vs NOISEX (0.907). The mechanism adds one sentence, not a claim about the method.

### Questions for the author
- May noise maps be edited before the unchanged slerp and render to make diagnostic-only images (F4)?
- May new files be written while /mnt/t7 has less than 50 GB free?
