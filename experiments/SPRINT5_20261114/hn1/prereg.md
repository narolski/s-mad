# Geometry-matched same-person negatives [SPRINT5-2]: bounded build registration

MAD22-informed new cycle, outside NEXT. Author explicitly authorizes the new direct matched composite. This registration authorizes metadata preparation and, after independent pre-run approval, exactly8eligible training-host pairs as a construction smoke. It does not authorize detector fitting, candidate reads or changing413–417. No sealed inputs or score archive is used.

Use D13(a) only: target L=(lmH+lmB)/2 with fixed frame corners and ONE cached indexed Delaunay triangulation; existing unchanged68_hires_morph._warp_tri applied exactly once to H,S,B. Both P=.5WH+.5WB and N=.5WH+.5WS are built new, with each warped layer clipped/converteduint8 once, then identicalfloat32halfblend/clipping/uint8PNG. The cached WH object is shared. No extra donor prewarp, resize, re-encode, independent target triangulation or reusedoldR4 positive. Unchanged triangle kernel and exactsource/input metadata hashes are enforced in builder.

Re-derived ladder eligibility:124training hosts whose partners are also training;32training→historicaltest-partner hosts excluded. Select first8sorted eligiblehosts prospectively. Preserve H,S,B and landmark hashes, target/triangles hash, WHidentity, warpcount, PNG/pixel hashes, secondsperpair, failures and source. Save WH/WS/WB alone as nuisance diagnostics. Every output is native existing frame geometry, PNG lossless; no stored-small copy in THIS boundedpilot. A full pilot must later include identical existing registered stored-small path on both classes, without writing new resampling code.

Success here means all8paired constructions pass identical-target/shared-host/one-warp, exact PNG reread, finite landmarks and dimensions; it is not evidence of nuisance independence. Any paired failure stops full generation and retains everyfailure. Do not use one surviving label from a failed group.

Historical dev100 hosts have51historicaltest and49excluded B suppliers; they cannot be relabelled whollydevelopment or independentheldout. Full evaluation requires a prospectively constructed disjoint-person pool/split and separate review before generation. This is a provenance blocker, not a model loss. No full detector fit registration exists yet.

Beforefit: source/processing/D-stratum matched all-cue and luma cross-fitted floorpilot, with person-componentCI. Bothpointfloors<=.60 permitfit; either>=.75 constructionleak/hold; intermediate onlyqualifiedfitbesidefrozenfloor. Exact floorpopulation, Dmeasure, component folds, fit reference/control and family/exposure matching must be separately pinned and independently reviewed before any fit. A successful geometry smoke does not satisfy thisfloor gate. Same-source capture/texture/FR-distance remain alternatives even if rendering is matched.

Commands prepared, owner does not submitclusterjobs:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python /home/narolski/smad-next/src/SPRINT5/hn1/build_pilot.py --out /mnt/t7/smad_next/SPRINT5_2/metadata_v1
# Only after independent review of this bounded image build:
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python /home/narolski/smad-next/src/SPRINT5/hn1/build_pilot.py --out /mnt/t7/smad_next/SPRINT5_2/pilot8_v1 --build-smoke
```

Expectedsmallpilot<100MB, noGPU. Timing unknown untilsmoke. CheckT7>=50GBreserve before largerbuilds. Noexistingoutput is overwritten. Metadata/read preparation is authorized; boundednewimagebuild awaits independent reviewer, not another userpermission question.
