# H5 — MAD22 n/a cells in SelfMAD retrain scoring: diagnosis + registered fix

Written 2026-11-16T08:30 CET (07:30Z) by the continuity agent, task from HOLDS_20261116.md (H5), operator present.
Scheduled for the next free GPU window on GB10 (twin X_sbr_s401 finishing); smoke test already PASSED (below).

## 1. Diagnosis (verified on data, not from notes)

Symptom: in RETRAIN_COHORT_EER_TABLE_20261116.md the SelfMAD block (s401–s404, own-mode) has n/a for
MAD22/FaceMorpher, OpenCV, Webmorph, MIPGAN_I, MIPGAN_II.

Root cause — REGISTRATION SCOPE, not a scoring bug and not an id-space mismatch:
- The own-mode SelfMAD scoring list (`run_selfmad_dgx.sh`) was built from `/mnt/t7/smad_next/RS1/manifest.csv`
  rows **where `src_path` is non-empty** (raw source images; own mode = the release's dlib-81 preprocessing
  applied to raws). The RS1 manifest contains **no `M22_*` and no `G22_*` rows at all** (verified: set counter —
  48 sets, zero MAD22/G22). Hence 23 145 scored images (vs 28 253 in the v1 pack).
- The MAD22 families live in the OTHER registered id space: `RS1/regen_pack/manifests/athena_manifest.csv`
  (`M22_*` morphs = 1000/984/500/1000/999 + `G22_raw`/`G22_aln` = 204+204), scored for released weights
  (`scores_rel_<det>__v1/v2.npz`) and for B/L/X retrains on the GB10-regen crops (`score_v1/v2.csv`,
  28 253/29 049 rows). Verified: **both regen manifests join 100% to the athena tags** (unmatched 0).
- The aggregate's `mad22_negative="FF_orig"` override only changes the negative pool; with no `M22_*` positives
  in the score file the five cells are necessarily empty → `None` → n/a.

Verdict: **deliberate pack-scope decision of the 11 Nov own-mode run** (own-mode pack was registered for the
FRLL read + DiM/MorDiff families), surfaced as n/a — an open cell, not a lost number.

## 2. Technical path (exists, smoke-tested)

SelfMAD's checkpoint is ALSO loadable in the common-protocol path: `a12_released.RELEASES["selfmad_hrnet_w18"]`
(arch hrnet_w18, 2 classes, morph idx 1, res 384, /255 scaling) → score.py `--mode rel` on the SAME GB10-regen
crops used for the released-weights MAD22 rows. Smoke test 2026-11-16T08:23 CET — **PASS**:
`ad5_score_dgx.py --name selfmad_hrnet_w18 --mode rel --manifest score_v1.csv --limit 8` →

    smoke_rel: 8 images, feat dim 2048, 2.9s (2.8 img/s); scores written, not opened
    weights sha256 0ad8db6f8f156cb21606e03ab32c88d122640cb835f7a93c77cca30c01386a26 (matches C6 receipt), strict load OK.

## 3. Registered fix (dispatch script ready: src/AD5/score/selfmad_m22_dgx_20261116.sh)

Score 6 networks × 2 variants on the regen crops: `selfmad_hrnet_w18` (a released-weights row; note the AD5
RWS released row for SelfMAD was already computed from the registered prod npz — this adds the regen-crops
companion) + `selfmad_S_s401..s405` (405 as soon as its training/scoring completes). 12 npz total,
`/home/narolski/ad6_stage/scores_selfmad_m22/` with RECEIPTS_sha256.csv; retrains re-converted from
sha256-verified tars (`convert_selfmad.py` asserts keys+shapes vs release).
Qualifiers to be recorded in the aggregate (append-only):
- SelfMAD MAD22 cells = **common-protocol (regen crops) scoring**, NOT own-mode preprocessing; own-mode FRLL
  rows stay the registered SelfMAD rows for FRLL; both blocks labelled distinctly.
- Same metric pin: EER on `logit_noTTA`, ties-halved, no threshold fitting; negatives = G22 raw+aln (408).
- v1 primary / v2 validation, matching the rest of the table.

Cost estimate: conversions ~2 min CPU/seed (one-time) + ~12 GPU scoring runs of 28–29 k images
(~4–8 min each at measured 47–110 img/s) → **~1.0–1.5 h total**, GPU-light (HRNet-W18, bs 32).
No training, no new data, no crops generated beyond the frozen regen set — within all standing GO rules
(validation/inference/analysis only, append-only, receipts kept, caveats preserved).

## 4. Dispatch plan

Window: after the GB10 twin finishes (~13:09 CET) and right after the 12:50 CET s405 scoring — both are on
this machine; the script skips completed npz, so it can be re-invoked safely at any cycle.
After 12/12 npz: extend the aggregate with the SelfMAD MAD22 block + qualifier rewrite (separate dated commit).
