Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Report as returned (saved by the MS1 owner; check script in
`experiments/MS1_multi-source-training-set/review_scripts/part3b/`).

# MS1 part 3b review (printed-only amendment), commit 7e367c5

Verdict: sound. The reader computes what Part 3b registers (ms1_part3b.py e93bd452… = prereg pin; ms1_part3.py
9986a870… unchanged since cff1ada); every printed number matches the earlier post hoc values (independent recompute
with scipy mannwhitneyu: largest per-kind difference 1.1e-16; training rows match manifests 5,535/5,535 and
8,798/8,798, 0 duplicate keys; A Sb 0.5408-0.5571, SbM3 0.5135-0.5353; SbM3 lower 5/5, SbV 1/5; 597 CFD models, 307 F
/ 290 M, model-code sex = GenderSelf 597/597; pooled women Sb 0.248, SbM3 0.007, SbV 0.257; men 0.097, −0.125, 0.074).

F1 (moderate): rank AUC is not a memorisation measure with a 0.5 baseline; A's 5/5 comes from a subset of kinds.
Training and held-out rows are not exchangeable: SbM3 lad_R4 0.428-0.488 on all seeds; Sb u50 0.458, R4 0.478. Per
kind SbM3 < Sb on 5/5 for photo, R0, R2w, S0, S3, S4; 4/5 photo61, R4; 2/5 zero, half, u50. Equal kind weights despite
n_train 124-1,456. The 0.625 exposure confound remains. For later arms: compare A only between arms on identical row
sets; print the per-kind table and the count of kinds below 0.5; fix kinds and weights at registration; prefer
per-seed paired differences. Rank AUC is invariant to monotone rescaling but says nothing about gap size.

F2 (moderate): within-sex medians hide large seed spread; SbM3 does not neutralise the association. Per-seed women: Sb
0.110, 0.248, 0.264, 0.312, 0.054; SbM3 −0.166, 0.007, 0.160, 0.202, −0.210. Paired by seed Sb > SbM3 on 5/5 for each
sex; SbM3 men negative 5/5 (−0.05 to −0.19). SbM3 flags 1 image in total (its ρ is about ranking deep in the genuine
region). Sb's ρ follows the seed's flag count (406: 41 flags, ρ 0.312; 407: 6 flags, ρ 0.054). Race × sex cells n
52-104 (ρ SE about 0.10-0.14). Wording: "near zero in women, negative in men", not "removes the signal".

F3 (moderate, CelebA-HQ printed guards): print per-seed ρ paired against the Sb reference with flag counts; decide now
signed ρ vs |ρ|; both guards read genuine CFD photos only and cannot detect "smooth means genuine" misses: print the
unseen-pipeline miss guard stratified by parent sex or a smoothness / make-up proxy (pool building involving warps is
an author item); repeated printing on CFD makes it a de facto development set: keep printed-only or register it as a
selection set.

F4 (minor): result.md bullet 1 lacks "printed only" and the per-kind caveat (replacement text applied by the owner).
