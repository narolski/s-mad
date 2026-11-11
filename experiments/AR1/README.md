# Landmark-morph ladder with self-morph twins (AR1, with AR2 dose, AR3 baselines, AR4 blanking) — full record

Owner: hypothesis-owner agent for AR1-AR4, first round. Machine: DGX (GB10, ARM), no cluster jobs.
Short verdict file: `experiments/AR1/result.md` (written when scoring ends). Registration: `experiments/AR1/prereg.md`
(written 11 Nov about 14:45 CET, before any AR1 detector score existed).

## 1. Question and current answer

Question: when released morphing-attack detectors score landmark morphs (OpenCV, FaceMorpher) well, do they react to
benchmark construction, to tool processing of a genuine photo, to morphing two photos of one person, or to a second
identity? Author ruling: a processed genuine image called a morph is an error; a same-person morph counts as a morph.

Status 11 Nov 2026, about 21:20 CET: **released detectors read; result.md written**; AR4 for ViT-L/14, the A46
platform check, M3L seeds 1-5 and some retrain extra rows still scoring (run_master.sh). Earlier status (18:00):
**running**. Images built, gates G-b (face-recognition twin validity) computed
and passed, gate G-c (probe readability) computed for 4 of 16 networks, detector scoring in progress on the shared GPU.
No detector score file has been opened yet. Answer: none yet.

Facts already established (no detector involved):
- "Tool run on one photo" (rung R2) is the untouched photo for OpenCV (bit-identical) and within 1 grey level for
  FaceMorpher. R2 vs R4 is therefore "untouched photo vs morph". Two extra one-photo rungs were added on the lead's
  request: warp-only (R2w, R2wm) and the mirror self-morph (R3m).
- The negative control "twin(A, A') vs twin(A', A)" (NC) is degenerate for both tools: both are symmetric at 50% mixing,
  so NC is pixel-identical to R3 (40 of 40 checked, max difference 0). Any NC number is 0.5 by construction.
- FRLL smiling files differ from neutral files in capture detail (lead, 11 Nov): every FRLL rung that uses a smiling
  file is confounded and gets no verdict.

## 2. Timeline (11 Nov 2026, CET)

- 14:00-14:25 Read OWNER_BRIEF, 11_AUDIT_PLAN, 08_CUE_MATRIX, 10_ASSET_INVENTORY (A, C, D), 12_STATE_AT_HANDOVER.
  Located: r8 self-morphs (`/mnt/t7/smad_next/volatile_backup_20261111/r8_{cv,fm}`, pairs in
  `/dev/shm/smad_arms/r8_pairs.csv`), the faithful two-person training arms (`mambamorph-code/smadcvpr_data/train/
  {cv,fm}_{feret,frgc}`, pair lists e.g. `mambamorph-code/baselines/webmorph/morphs_opencv/feret/pairs.tsv`), scoring
  code of A36/A41/A46 (frozen runtime `/home/narolski/mambamorph-code-a46`), FR model (glintr100), a41_read bootstrap.
  Decision: the r8 and training-arm sets are not composition-matched (different host photos, no session / expression
  control); fresh composition-matched sets were built instead. No E7 (history-matched) output exists for these frames.
- 14:27 SelfMAD release fetched from WCSS with one locate command and one rsync through the flock lock:
  `/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors`, sha256 0ad8db6f... (matches
  the record). (WCSS has since been closed to our address; not used again.)
- 14:33 Pool built (`src/AR1/pool.py`): 536 hosts. 14:40 FRLL aligned and pooled (`src/AR1/frll_prep.py`).
- 14:35-14:55 Smoke test of the builds on 8 hosts; found OpenCV R2 = H bit-exactly, FaceMorpher R2 within 1 level.
  Graded FaceMorpher driver failed at first (importing `locator.py` loads a missing dlib 68-point file); fixed by
  executing only the unchanged `weighted_average_points` source from `locator.py`.
- 14:45 prereg.md written (before any score).
- 14:35-15:00 Full builds (`build.py`, `graded_fm.py`), FRLL builds and bridges. `manifest.py` -> 15,687 rows.
- 14:50 Smoke test of crops and all four scoring modes on 8 images (scores written, not opened).
- 14:56-15:14 Gate G-b computed (`gate_b.py`): passed in all four cells.
- 14:58 First crop run at 1 image/s (shared GPU, swap full, kcompactd at 100%); killed. Second try with 3 shards also
  slow (about 66/min total); killed. Lead message 1 (15:00): add warp-only R2w and mirror self-morph R3m.
- 15:00-15:20 Mirror permutation measured (`mirror_perm.py`), R2w / R3m built (`variants.py`, `build.py --rungs R3m`),
  manifest extended to 18,239 rows (rows appended; earlier ids unchanged, checked).
- 15:25 Crop runs restarted with batched MTCNN (`crop_rgb.py` rewrite): about 250-300 images/min, finished after 80 min
  (18,239 of 18,239 retained, 0 without face).
- 15:30 SelfMAD own scoring of all 18,239 images finished (32 min). First attempt had segfaulted (dlib detector in a
  thread pool); fixed by the record's fork Pool order (workers started before CUDA, as `a41g_score.run_own`).
- 15:35-16:40 FR checks of R2w / R3m (`verify_variants.py`; two CUDA out-of-memory failures, retried): passed.
- 16:45 Lead message 2: FRLL smiling confound. Added R2wm (warp toward H's own mirrored shape, neutral file only),
  FRLL clean ladder (R0 neutral, R2wm, R3m, R4nn = our neutral+neutral two-person morphs of the published pairs),
  neutral-only genuine class on the FRLL benchmark side. Manifest extended to 19,515 rows (appended).
- 16:40-17:50 G-c for SelfMAD and M3 seed 1; ViT-B/16 scored (18,239 images, 24 min). MixFaceNet scoring failed twice
  with CUDA out of memory (16 owners' processes on the GPU, 103 of 121 GB RAM used); retry wrappers added to all chains.
- 17:20 Author instruction: this README.
- about 19:00 Lead (ID0): 8 hosts are validation-reserved persons; `pool_person_split.csv` written; sensitivity line.
- about 19:45 Lead (ideation round 3): amendment 4-6 registered in prereg.md, then R2w4 built (`variants.py warp2`,
  536 + 536 images, 11 s / 34 s), warp check (`verify_warp.py`: 8 hosts, then all), manifest appended to 20,587 rows
  (`manifest_extra2.csv`, ids 019515-020586), chain D `run_extra2.sh` started; baselines extended with band power and
  Laplacian variance (`baselines.py --feats band,lapvar`, then `--only R2w4`; log `baselines2.log`).

Amendments to the registration (all before any score was opened): R2w, R3m (lead 15:00), R2wm and FRLL clean ladder
(lead 16:45), FRLL genuine class neutral-only, G-c extended with R4 vs R3m, MTCNN batching (speed; boxes equal to
0.04 px), retrain bridge dropped (it would compare two different frame pipelines).

## 3. Data

All under `/mnt/t7/smad_next/AR1/` (T7 drive on the DGX) unless stated. No copies elsewhere.

| Item | Path | Items | Built by | Hash (sha256) |
|---|---|---|---|---|
| Source frames (byte copies of the record's 73_delin_align frames + `.tem`) | `src/<db>/<subject>/` | 1,606 png + tem | `pool.py` | per-file equal to the originals (checked at copy) |
| Primary host table | `pool.csv` (copy `experiments/AR1/pool.csv`) | 536 rows (FRGC 427, FERET 109) | `pool.py` | 861019781e79... |
| Pool with mirror paths | `pool_m.csv`, `pool_frll_m.csv` | 536 / 102 | `variants.py mirror` | cee5cfe3... / 47750744... |
| FRLL aligned photos | `frll_src/` | 204 (102 neutral _03, 102 smiling _08) | `frll_prep.py` (unchanged 73_delin_align, sha 47eefed3...) | - |
| FRLL host table | `pool_frll.csv` | 102 | `frll_prep.py` | c69a96df... |
| Bridge pair lists | `bridge_frll_{opencv,facemorpher}.csv` | 1,221 / 1,222 | `frll_prep.py` | 323c8aba... / 30105e2d... |
| Built images | `img/<pool>/<tool>/<rung>/<pid>.png` | see below | `build.py`, `variants.py`, `graded_fm.py` | - |
| Mirror images (lossless flip) + mirrored `.tem` | `mirror/<pool>/` | 536 + 102 | `variants.py mirror` | pixel-equal to cv2.flip(H) (asserted) |
| Mirror index permutation | `mirror_perm106.json` (copy in experiments/AR1) | 106 indices | `mirror_perm.py` | ed919081... |
| Master manifest | `manifest.csv` | 19,515 rows | `manifest.py` | 9c69d44f... (v1 15,687 rows 1443120c..., v2 18,239 rows 2dbf4c00..., appended rows `manifest_extra.csv` 1,276, 26da4450...) |
| Blanked copies (constant grey 128) | `blank/{bg,face}/<id>.png`, `blank/blank_manifest.csv` | 9,570 pairs | `blank.py` | - |
| RGB-MTCNN crops | `crops/main/<id>.png`, `crops/main/crops_*of3.csv`, `crops/main/boxes_*of3.jsonl`, merged `crops/boxes_main.json` | 18,239 | `crop_rgb.py` | boxes_main e95ec83a... |
| Blanked crops (original boxes) | `crops/{bg,face}/` | 8,294 each (the 1,276 R2wm rows have no box yet) | `crop_rgb.py --boxes-in` | - |
| Scores and features | `scores/scores_<tag>.npz`, `scores/feat_<tag>.npz` | per tag | `score.py` | - |
| FR embeddings | `pool_src_emb.npz`, `frll_src_emb.npz`, `fr_emb_built.npz`, `fr_emb_variants.npz` | 1,606 / 204 / 3,828 / new rungs | `pool.py`, `frll_prep.py`, `gate_b.py`, `verify_variants.py` | - |
| Contact sheets | `sheets/`, `variants_sheet.png` | - | ad hoc | - |

Rungs (built per host, per tool unless stated; PNG 512 x 512, the tools' own frame):
- R0, the camera photo: host photo H (neutral, session s1).
- R1, photo with matched history: not built; on our builds morphs and photos share the same aligned frame, so the E7
  rule is the identity. Measured only on the FRLL benchmark side with the record's E7 frames.
- R2, tool run on one photo: tool(H, H). Identical to R0 for OpenCV.
- R2w, warp-only toward the same person's other photo: H warped by the tool's own warp to the mean shape of H and S,
  texture from H only.
- R2wm, warp-only toward its own mirror shape: H warped to the mean shape of H and its mirror, H file only.
- R2w4, warp-only toward the two-person mean shape (primary pool only): H warped to the mean shape of H and B (the
  same geometry as R4), H texture only. R4 vs R2w4 differs only by the blended second texture.
- R3, twin: tool(H, S), S = the same person, neutral, another session (FRLL: neutral + smiling, confounded).
- R3m, mirror self-morph: tool(H, mirror of H) with the mirrored, re-indexed landmarks.
- R4, morph: tool(H, B), B = another person's S photo (FRLL: another person's smiling photo, confounded).
- R4nn (FRLL only): our tool(a_03, b_03) for every published FRLL-Morphs pair (the bridge set).
- NC: tool(S, H) (pixel-identical to R3, see section 7).
- G (AR2): FaceMorpher library graded mixing m = 0, 0.1, ..., 0.5 of (H, B), 300 hosts.

Counts: primary pool R0 536, each of R2, R2w, R2wm, R3, R3m, R4, NC 536 per tool; graded 1,800; FRLL R0 102 and 102 per
rung and tool; bridge 2,443; FRLL benchmark side 204 raw photos, 2,443 published raw morphs, prep_eval frames 204 bona,
408 E7, 2,443 published.

Dropped: 510 pixel-duplicate candidate frames (same capture re-aligned); 2 hosts without an independent FR reference
photo (excluded from G-b only); no image failed a build or a crop.

Person split (added 11 Nov about 19:00 at the lead's request, from the identity-shrinkage triage (ID0)):
`experiments/AR1/pool_person_split.csv` (person, database, is_val, n_host_images = manifest rows with that host),
made with the record's rule `prep_train.is_val(subject)` (imported unchanged from `mambamorph-code/smadcvpr`), CPU
only, no score opened. 8 of the 536 hosts are validation-reserved persons: feret:00468, 00705, 00706, 00712, 00720,
00771, 00797, 00894 (their photos came from `train.csv` bona_feret rows flagged val = 1; `pool.py` did not apply the
rule). The other 528 hosts are training-split persons of our own training data. Nothing was rebuilt; results carry a
sensitivity line without these 8 hosts (as host or as B).

Identity overlap: FRGC / FERET persons are unseen for the released detectors (SMDD-trained; SelfMAD's training set not
verified) and for M3 / M3L (R x d0, SMDD only). They are training identities of our d1 / A8-W1F networks, which are not
scored here. FRLL persons are the benchmark bona fide; never trained on.

## 4. Code (`/home/narolski/smad-next/src/AR1/`, run order)

| Script | Job |
|---|---|
| `ar1_common.py` | paths, weight paths and sha256 pins, forbidden-path check |
| `fr.py` | glintr100 embeddings via the registered route (prep_eval.kps, norm_crop, a2f_common 'glint'; pins checked) |
| `pool.py` | candidates, sessions, expressions, hosts, Hungarian B assignment; copies sources |
| `frll_prep.py` | FRLL alignment (unchanged 73_delin_align), FRLL pool, bridge lists |
| `build.py` | runs unchanged `scripts/78_tool_morph.py` (OpenCV) and `scripts/96_facemorpher_tool.py` (FaceMorpher) |
| `graded_fm.py` | AR2 graded mixing with the unchanged face_morpher library functions |
| `mirror_perm.py` | measures the 106-point left-right permutation |
| `variants.py` | `mirror` (flip + mirrored tem), `warp` (R2w), `warpmirror` (R2wm), `warp2` (R2w4) |
| `verify_warp.py` | checks that warp-only images averaged with the matching partner-side warp reproduce the tool's R4 / R3 |
| `verify_variants.py` | pixel difference and FR cosine of R2w / R2wm / R3m vs R3 / R4 |
| `manifest.py` | master manifest (rows appended, ids stable) |
| `blank.py` | constant-colour blanking with the landmark hull |
| `crop_rgb.py` | A46 RGB-MTCNN crop path (unchanged functions of a46_corrective_crop.py), batched |
| `lists.py` | score lists |
| `score.py` | features + scores (rel / own / nets modes; record functions imported unchanged) |
| `gate_b.py`, `gate_c.py` | gates |
| `baselines.py` | AR3 baselines |
| `stats.py` | a41_read.Draw, a36_read.wauc, a41_read.dprime / ci (imported unchanged) |
| `analyse.py`, `tables.py` | reader and markdown tables |
| `check_a46.py` | platform check against the A46 RGB-only score files |
| `run_rel.sh`, `run_own_nets.sh`, `run_extra.sh`, `run_extra2.sh` | scoring chains A, B, C (R2wm rows), D (R2w4 rows); `run_scoring.sh` is the superseded first chain |

Environment: `/home/narolski/mambamorph-code/.venv-spark/bin/python` (Python 3.12, torch 2.12.1+cu130, timm, insightface,
dlib, scikit-learn, scipy); MTCNN in `/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv` (facenet_pytorch 2.6.0).
Record code imported unchanged from `/home/narolski/mambamorph-code-a46/smadcvpr` (a12_released 839f0cd4...,
a41g_score f53612cb..., a41_read, a36_read, a46_corrective_crop, rsx_selfmad_own, common) and
`/home/narolski/mambamorph-code` (scripts 68 71643aad..., 78, 96, 73 47eefed3..., prep_eval 374408ab...,
baselines/face_morpher warper 76c0d1ac..., blender 7b98a8d5..., locator 8a745b1e...). a2f_common d27701db....
Weights: MADation ViT-B/16 ddb1455b..., ViT-L/14 bb452ded... (staged copies in
`/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/`), MixFaceNet-MAD 3d507c8b...
(`/mnt/t7/mixfacenet_mad_official/`), SelfMAD 0ad8db6f... (fetched), M3 seeds 1-8 / M3L seeds 1-5 last.pt from
`/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/` with meta.json from `mambamorph-code/smadcvpr_runs/A12_scored/A12BR/`.
dlib 81-point model `/mnt/t7/thirdparty/dlib81_wcss_20261107/shape_predictor_81_face_landmarks.dat`.
Seeds: pool 20261111, graded subset 20261112, bootstrap [20261111, 1] (detectors, baselines), [20261111, 2] (G-b),
[20261111, 3] (G-c), [20261111, 4] (bridge); B = 2,000.

## 5. Results (so far)

Gate G-b (twin validity), `experiments/AR1/gate_b.json`. Oracle = 1 - glintr100 cosine to the host's independent photo;
tau at false-match rate 1/1,000 = 0.283 (primary, 193,244 impostor pairs), 0.254 (FRLL, source-photo reference).

| Pool / tool | n R3 / R4 | Oracle AUC morph vs twin [95% CI] | Morphs verify both | Twins verify host | NC vs R3 | G-b |
|---|---|---|---|---|---|---|
| FRGC+FERET / OpenCV | 534 / 532 | 0.998 [0.996, 1.000] | 99.2% [98.1, 99.8] | 100% [99.3, 100] | 0.500 (degenerate) | pass |
| FRGC+FERET / FaceMorpher | 534 / 532 | 0.998 [0.996, 0.999] | 99.1% [97.8, 99.7] | 100% | 0.500 (degenerate) | pass |
| FRLL / OpenCV | 102 / 102 | 1.000 | 100% | 100% | 0.500 | pass, but source-photo reference and smiling confound |
| FRLL / FaceMorpher | 102 / 102 | 1.000 | 100% | 100% | 0.500 | as above |

R2w / R2wm / R3m checks (`experiments/AR1/variants_check.json`, all hosts): median glintr100 cosine to H (and to the
independent reference R), median mean |difference| to H in grey levels, images identical to H:

| Pool / tool | R2w | R2wm | R3m | R3 | R4 | R3m gate (cos H >= R3) |
|---|---|---|---|---|---|---|
| FRGC+FERET / OpenCV | 0.976 (0.871), 3.76, 0 | 0.988 (0.878), 4.11, 0 | 0.954 (0.849), 9.62, 0 | 0.946 (0.894), 15.08 | 0.689 (0.619), 18.81 | pass |
| FRGC+FERET / FaceMorpher | 0.966 (0.861), 1.23, 0 | 0.981 (0.872), 1.20, 0 | 0.942 (0.836), 9.14, 0 | 0.938 (0.889), 14.64 | 0.669 (0.605), 18.20 | pass (narrow) |
| FRLL / OpenCV | 0.958, 3.36, 0 | 0.990, 3.78, 0 | 0.963, 8.96, 0 | 0.953, 5.69 | 0.633, 16.87 | pass |
| FRLL / FaceMorpher | 0.953, 1.35, 0 | 0.984, 1.16, 0 | 0.952, 8.70, 0 | 0.950, 5.54 | 0.628, 16.42 | pass |

Note: against the independent reference R, R3m (0.849 / 0.836) is below R3 (0.894 / 0.889): R3 contains a second real
photo of the person, R3m does not. The registered gate (cosine to H) passes.

Gate G-c (probe on frozen features, R4 vs R3, 5-fold by host), so far (`experiments/AR1/gate_c.json`):
SelfMAD 0.909 [0.883, 0.931] (FRGC+FERET OpenCV), 0.931 [0.909, 0.948] (FaceMorpher); M3 seed 1 0.889 / 0.878;
FRLL cells 0.988-0.995 (confounded). All readable (>= 0.65). Remaining tags pending.

Warp check (amendment 4), 8 hosts (`experiments/AR1/warp_check_smoke.json`; all hosts in `warp_check.json`):
R2w4 and R2w averaged with the partner-side warp reproduce the tool's R4 / R3 to at most 0.5 grey level over the whole
frame (OpenCV; the 0.5 is the halving of an odd sum) and exactly (0) inside the face mask (FaceMorpher).

Detector results (opened after G-b and each network's G-c): all tables in `experiments/AR1/result_tables.md`
(from `result_tables.json`, analysis v2, `/mnt/t7/smad_next/AR1/analyse_v2.log`); summary and verdicts in
`experiments/AR1/result.md`. Platform check: `experiments/AR1/a46_platform_check.json`. Baselines (strict folds):
`experiments/AR1/baselines.json`, out-of-fold scores `/mnt/t7/smad_next/AR1/scores/baselines_oof.npz`.

Pool facts: cos(H, S) median 0.868; cos(H, B) median 0.234; 7 FERET hosts have a greyscale H or S.

## 6. Checks

Done: smoke tests on 8 images for every command; source copies hash-equal; mirror flip pixel-equal; mirror permutation
an involution after one correction (section 7); manifest appends keep earlier rows byte-equal (checked twice); batched
vs single MTCNN boxes on 32 frames: max 0.04 px, median 0.006 px; G-a read from the A46 RGB-only result (prereg).
Pending: `check_a46.py` (rescore the A46 crops with score.py and compare with the A46 RGB-only score files).
Not verified: which expression the published FRLL-Morphs pairs used (assumed neutral-neutral from the AMSL file names);
SelfMAD's training identities; whether 73_delin_align on FRLL matches prep_eval frames (different pipelines; not mixed).

## 7. Dead ends and failures

- OpenCV R2 = H bit-exact, FaceMorpher R2 within 1 level: the planned R2 rung carries no processing trace (registered
  in the prereg before scoring; the lead added R2w / R3m).
- NC (tool(S, H)) is pixel-identical to R3 for both tools (both symmetric at 50%): the registered negative control is
  degenerate; the probe and oracle NC values of exactly 0.5 carry no information.
- Graded FaceMorpher: importing `locator.py` fails (loads `baselines/face_morpher/data/shape_predictor_68_face_landmarks.dat`,
  absent); fixed by executing only `weighted_average_points` from its source text (unchanged).
- Mirror permutation: majority vote gave index 34 -> 88 (88 is already the partner of 38); corrected to 92, the only
  unpaired index, which makes the map a bijective involution (recorded in mirror_perm106.json).
- First background chain killed by my own `pkill -f run_scoring.sh` matching the shell that ran it (exit 144); later
  kills done by PID only.
- MTCNN crops at 1 image/s (shared GPU, swap 16/16 GB, kcompactd 100%); CPU MTCNN was 14x faster but gave boxes up to
  10.6 px different on 1 of 30 frames, so CPU was rejected; batched GPU detection adopted (max 0.04 px).
- SelfMAD own scoring segfaulted in a thread pool (dlib); fixed with the record's fork Pool.
- Repeated CUDA out-of-memory (FR checks, MixFaceNet scoring) while 16+ processes of other owners share the GPU; fixed by
  retry wrappers (6 tries, 90 s apart).
- `build.py` overwrote `img/frgcferet/build_log.json` when R3m was built; the main build timings survive in
  `/mnt/t7/smad_next/AR1/build_all.log`.
- `verify_variants.py --smoke` failed with CUDA OOM; the full run (which includes the 8 smoke hosts) passed instead.

## 8. Observations and ideas

- For landmark tools at tool size, "processing a genuine photo" is nothing (OpenCV) or almost nothing (FaceMorpher);
  the benchmark-side processing (resize to 431 x 513, JPEG) is a separate cue not reproduced by the tool.
- R3 (two sessions) shows a ghosted background / clothing outline like R4; R3m and R2wm do not change background.
- FRLL smiling files are larger and noisier (lead's review); FRLL R3 / R4 / R2w therefore confounded.
- Build speed: OpenCV about 2,000-3,200 images/min with 12 processes, FaceMorpher 330-1,030/min (load-dependent),
  warp-only driver 1,900-6,900/min; the bottleneck on the shared DGX is GPU work (crops about 250-300/min, ViT-B/16
  scoring 12.5 images/s).
- Any network WE train must exclude the ladder persons (pool.csv hosts; FRLL persons anyway) from its training data,
  or be scored on the ladder out-of-fold by person (lead, 11 Nov). The probes of gate G-c and the AR3 baselines are
  already out-of-fold by host person.
- No softness measurement was made by this owner. A process `soften.py build --list ar1soft_src` seen on the DGX
  belongs to another owner.

## 9. Open items and next steps

Finish scoring (MixFaceNet, ViT-L/14, blanked variants, R2wm extra rows, retrains), G-c for every tag, then baselines,
`analyse.py`, `tables.py`, `check_a46.py compare`, result.md. AR4 for R2wm not planned (no blanked crops).

## 10. Handover state (DGX)

Current (11 Nov about 21:50 CET, at the owner's hand-back):

| Process | PID | Log | Expected end | If it fails / next step |
|---|---|---|---|---|
| `run_master.sh` (two lanes, thread caps, nice 10) | 2365185 | `/mnt/t7/smad_next/AR1/run_master.log` | about 00:30 CET 12 Nov (M3L seeds 2-5 at about 7 images/s, then the R2wm rows of the retrains) | rerun `nohup bash src/AR1/run_master.sh > run_master.log &` (finished files are skipped) |
| lane 2 `run_own_nets.sh` (M3L seeds 2-5) | 2438540 | `run_own_nets.log` | as above | same |
| lane 1 `run_extra2.sh` (R2w4 rows of M3L), then `run_extra.sh` (R2wm rows of the retrains; waits for OWN_NETS_DONE) | 2546174 | `run_extra2.log`, `run_extra.log` | as above | same |

After MASTER_DONE: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 nice -n 10 $P -I src/AR1/gate_c.py --tags
nets_M3L_s1,nets_M3L_s2,nets_M3L_s3,nets_M3L_s4,nets_M3L_s5` (one process; it rewrites gate_c.json with all tags),
then `analyse.py`, `tables.py > experiments/AR1/result_tables.md`, and update the retrain block of result.md.
Compute so far: about 8 GPU-hours on the shared GB10 (crops, scoring, FR), CPU several hours; no USD.

Earlier table (18:00 CET, superseded):

| Process | PID | Log | Expected end | If it fails |
|---|---|---|---|---|
| NOTE 20:45: rows below superseded by `run_master.sh` (log `run_master.log`) and `run_cpu.sh` (log `run_cpu.log`) | | | | rerun the same scripts; finished files are skipped |
| chain A `run_rel.sh` (MixFaceNet, ViT-L/14 main, then bg/face, then a46check) | 2086549 | `/mnt/t7/smad_next/AR1/run_rel.log` | several hours (shared GPU) | rerun `bash src/AR1/run_rel.sh >> run_rel.log`; finished files are skipped |
| chain C `run_extra.sh` (R2wm rows: crop, rel, own, nets) | 2086237 | `run_extra.log` | after chains A and B (waits for REL_DONE and OWN_NETS_DONE) | rerun the same way |
| chain B `run_own_nets.sh` | stopped (parent killed by me at about 17:40 to free the GPU; M3 s1-s3 done, SelfMAD main / bg / face done) | `run_own_nets.log` | restart after chain A: `nohup bash src/AR1/run_own_nets.sh >> run_own_nets.log &` | - |
| `baselines.py` | 1854285 | `baselines.log` | about 1 h | rerun; then a second pass for the R2wm contrasts |
| `gate_c.py` (ViT-B/16, SelfMAD, M3 s1-s2 with the extended contrasts) | 2085481 | `gate_c_1.log` | minutes | rerun the same command |

Compute: DGX only; about 3 GPU-hours so far on a shared GB10; no USD.

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
cd /tmp
$P -I $S/pool.py
$P -I $S/frll_prep.py
$P -I $S/build.py --pool $O/pool.csv --name frgcferet --workers 12
$P -I $S/graded_fm.py --pool $O/pool.csv --n 300 --workers 12
$P -I $S/build.py --pool $O/pool_frll.csv --name frll --workers 12
$P -I $S/build.py --pairs $O/bridge_frll_opencv.csv --name frll_bridge --tools opencv --workers 12
$P -I $S/build.py --pairs $O/bridge_frll_facemorpher.csv --name frll_bridge --tools facemorpher --workers 12
$P -I $S/mirror_perm.py --n 24          # then apply the index-34 correction recorded in mirror_perm106.json
$P -I $S/variants.py mirror; $P -I $S/variants.py warp --workers 12; $P -I $S/variants.py warpmirror --workers 10
$P -I $S/variants.py warp2 --workers 10; $P -I $S/verify_warp.py
$P -I $S/build.py --pool $O/pool_m.csv --name frgcferet --rungs R3m --workers 12
$P -I $S/build.py --pool $O/pool_frll_m.csv --name frll --rungs R3m --workers 12
$P -I $S/manifest.py > $O/manifest.log
$P -I $S/blank.py --pools frgcferet,frll --rungs R0,R2,R3,R4,NC,R2w,R3m,R2wm
$P -I $S/gate_b.py; $P -I $S/verify_variants.py
bash $S/run_rel.sh; bash $S/run_own_nets.sh; bash $S/run_extra.sh; bash $S/run_extra2.sh
$P -I $S/gate_c.py --tags <all feature tags>      # before opening any score
$P -I $S/baselines.py; $P -I $S/baselines.py --only R2wm; $P -I $S/baselines.py --feats band,lapvar
$P -I $S/baselines.py --only R2w4; $P -I $S/analyse.py; $P -I $S/tables.py; $P -I $S/check_a46.py compare
```

## Log of README updates
- 11 Nov about 22:50 CET: review applied (`experiments/reviews/REVIEW_AR1_20261111.md`).
  - Post hoc addendum P1-P4, amendment 8 (softened AF0 copies) and amendment 7 / 7b (spliced inner-face morph, one R4
    hull per host, arms S4 / S3 / S0) were registered in prereg.md before running.
  - New code: `src/AR1/posthoc.py`, `splice.py`, `soft_splice.py`; chains `run_add.sh`, `run_add3.sh` (`run_add2.sh`
    superseded and killed).
  - Outputs: `experiments/AR1/posthoc.json`, `soft_splice.json`, `splice_seam_pixels.csv`;
    `/mnt/t7/smad_next/AR1/manifest_splice2.csv` (13,936 rows), `img/frgcferet/<tool>/{S4,S3,S0}`, `blank_splice2/`,
    `manifest_soft.csv`.
  - Superseded and unread: the first splice (`manifest_splice.csv`, `blank_splice/`, scores `*__splice*.npz`). The
    SelfMAD runs on those files were stopped.
  - M3L seeds 1-5 finished with G-c 0.90-0.92 (MASTER_DONE 22:00). Analysis v3 (`analyse_v3.log`) renames the side
    verdict for warp-only vs same-person morph to "blend reading".
  - result.md rewritten in the review's wording; the previous version is at
    `/mnt/t7/smad_next/AR1/result_v1_before_review.md`.
  - No AR1 process is running. Disk: /mnt/t7 at 98%, about 48 GB free.
- 11 Nov about 21:50 CET: A46 platform check done (AUC agreement within 0.0004, Kendall tau 0.966-0.973 < 0.99: not
  image-identical); AR4 complete for all four releases; analysis v2 (`analyse_v2.log`); result.md updated; owner
  hands back with M3L scoring still running (section 10).
- 11 Nov about 21:20 CET: strict baselines finished (`run_cpu.log`, CPU_DONE); full analysis v1 (`analyse_v1.log`,
  `experiments/AR1/result_tables.json`, `result_tables.md`); `result.md` written. M3 seed 8 was read in that pass about
  10 minutes before its G-c existed (G-c then 0.899 / 0.903, readable); `analyse.py` now refuses networks without G-c.
  R2wm rows for the releases scored ahead of lane order (`run_extra_rel.sh`). Remaining: lane 1 (ViT-L/14 bg / face,
  a46check, extra2 nets, extra nets), lane 2 (M3L seeds 1-5). When they finish: run `gate_c.py --tags
  nets_M3L_s1,...,nets_M3L_s5` (with thread caps), then `analyse.py`, `tables.py > result_tables.md`,
  `check_a46.py compare`, and update result.md (AR4 ViT-L/14 row, retrain block, platform check).
- 11 Nov about 20:15 CET: gates complete for the four releases and M3 seeds 1-7 (strict folds; G-c all >= 0.65,
  MixFaceNet lowest 0.68 / 0.69 on the primary pool). Release scores opened (after G-b and G-c) for a preliminary read
  with the leaky baselines still in place (`/mnt/t7/smad_next/AR1/result_tables_prelim.json`; its baseline columns are
  superseded). Preliminary picture, primary pool, releases: R0 -> R2 AUC 0.49-0.50 for all (identical images);
  R2 -> R3 (blend of two photos of one person) 0.86-0.98; R3 -> R4 (second identity) 0.60-0.75; R2w vs R4 0.89-0.99;
  R2w vs R2w4 0.49-0.52 (warp size alone does nothing); R2w4 vs R4 0.89-0.99 (blending a second photograph, geometry
  equal); twins flagged at the FRLL benchmark threshold in 64-100% vs morphs 76-100%. Face-blanked SelfMAD still
  separates R2w from R4 at 0.89 / 0.92 (frame / periphery). Final numbers in result.md after the remaining scoring.
- 11 Nov about 20:45 CET: lead's load note (load average 189): my baselines.py (950% CPU) and gate_c.py (540%) were
  thread-oversubscribed. Both killed; reviewers' note (PLANNING_RECORD section 15 item 7) confirmed a real leak: folds
  by host only put morph(H_p, S_q) and twin(H_q, S_q), which share the photo S_q, on opposite sides of a fold. New
  `src/AR1/folds.py`: strict person folds, units = cycles of the host -> B assignment (largest primary cycle 163 of 536
  persons; folds 163/93/94/94/92; FRLL 46/17/13/14/12), bridge pairs tested only when both persons share the test fold.
  Leaky outputs kept aside, not used: `/mnt/t7/smad_next/AR1/gate_c_leaky_v1.json`, `baselines_leaky_v2.json`,
  `scores/baselines_oof_leaky_v2.npz` (and the older `baselines_v1.json`, `baselines_oof_v1.npz`). G-c and baselines
  rerun as one sequential process with OMP/OPENBLAS/MKL/NUMEXPR threads = 2 and nice 10 (`run_cpu.sh`, log
  `run_cpu.log`). All chains replaced by `run_master.sh` (same caps; two lanes; waits until the uncapped in-flight
  score.py runs end). `pkill -f <pattern>` killed my own shell twice more (exit 144); use PIDs only.
- 11 Nov about 20:00 CET: R2w4, amendments 4-6, warp check, chain D, extra baselines.
- 11 Nov about 18:00 CET: first version.
- 11 Nov about 19:00 CET: person split table and the 8 validation-reserved hosts (section 3); training rule (section 8);
  `analyse.py` gains a sensitivity line without those 8 hosts.
- 11 Nov about 18:40 CET: baselines (AR3) finished for all contrasts except R2wm (`experiments/AR1/baselines.json`,
  226 entries; copy of that version `/mnt/t7/smad_next/AR1/baselines_v1.json`); an incremental pass
  `baselines.py --only R2wm` merges the R2wm contrasts (log `baselines_r2wm.log`). G-c run crashed once on M3 seed 1
  FRLL (the retrains have no bridge features, so the clean-FRLL probe had one class); fixed (empty class -> "not
  scored") and rerun for ViT-B/16, SelfMAD, M3 s1-s3 (`gate_c_1.log`), then MixFaceNet (`gate_c_2.log`). Gate files are
  written by one process at a time (concurrent runs would overwrite each other's tags). MixFaceNet scored (18,239,
  29 min). Chain B restarted at about 18:20 (PID see `ps -ef | grep run_own_nets`); its `frames.csv` now includes the
  R2wm rows, so seeds 4+ score them natively; chain C adds them for seeds 1-3. `analyse.py` was tested end to end on
  synthetic random scores (`AR1_SCORES_DIR` override; scratch output only) before any real score was opened.
