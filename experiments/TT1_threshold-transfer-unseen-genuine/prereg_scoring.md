# Registration TT1-S: scoring of the threshold-transfer experiment (TT1) on unseen genuine sources

This text is registered at the git commit that adds it. At that commit:
- no TT1 image has been scored by any network;
- no border-matched or crop-geometry-matched reference has been scored;
- the crop-geometry-matched reference (section 2.4) has not been built.

It replaces the draft `prereg_scoring_draft.md` (f4fe159). The draft went through the pre-run review
`experiments/reviews/PRERUN_TT1_SCORING_20261112.md` (commit 7c0ecb6; GO WITH FIXES). All seven majors (M1-M7), the
platform and operations list and the minors are applied below, with the reviewer's texts. The lead's rulings on the
open points (message of 12 Nov evening) are applied as R1-R5.

The only network outputs computed in TT1 so far: an 8-row DGX command test on FFHQ rows that were already scored
(`/mnt/t7/smad_next/TT1/dgxtest/`, max |Δlogit| 0.0015).

Pins that depend on images built after this commit are registered in a "pins" section, committed before any score:
the list, the pack, the network tar, the job script and the reader. If a pin section is missing, no score exists.

## 0. Scope, what each contrast identifies, and what no reading can claim

- **Scope.** The 12 PN1 networks of seeds 401/402 (A, B, Bn, C, Sb, Bv), scored on the TT1 pools and on reference
  pools. Later, as a separate block, the 16 FS1 networks (section 9). Development reads only.
- **Sources.** 23,832 frames come from `/mnt/t7/Datasety/downloads/CASIA-Webface/*.bin`. They are LFW, CALFW, CFP-FF
  and AgeDB-30 images, not CASIA-WebFace images.
  - Lead ruling R2: LFW, CALFW, CFP-FF and AgeDB are outside the CASIA-WebFace closure. They are different datasets,
    and none was used in training or in any benchmark of ours.
  - Celebrity identities in these packs may overlap with CASIA-WebFace, which supplies the H1 source identities
    (10_ASSET_INVENTORY.md:116). This was not checked, because checking would mean opening a closed set.
  - `train.rec` (CASIA-WebFace), `cfp_fp.bin` and `cplfw.bin` are never read. Every TT1 script that touches the
    folder asserts this (extract.py FORBIDDEN; build_pack.py list assert).
  - The anti-spoofing frames (Replay-Attack, MSU-MFSD, OULU-NPU, CASIA-FASD) are genuine "live" frames only.
- **What each contrast identifies** (M4):
  - U vs R_cam: everything together (source, enlargement, JPEG, sharpness, border).
  - R_cam^border vs R_cam, and R_ffhq^border vs R_ffhq: border alone. The border reference matches border geometry
    only. It does not match enlargement, resolution, compression or source.
  - U vs R_cam^border: source plus enlargement plus JPEG plus sharpness. The border is roughly removed; enlargement is
    not.
  - R_cam^geo(g) vs R_cam: crop geometry, border and enlargement of geometry group g together, on the training
    source.
  - U_s vs R_cam^geo(g(s)): source beyond crop geometry, border and enlargement, within geometry group g (g224 =
    anti-spoofing frames, g112 = packs). This includes JPEG and capture differences: U frames are JPEG, the geo
    reference is lossless.
  - Within-pack ρ and quintiles: sharpness at fixed size, as correlation only.
- **No reading can claim:**
  - any miss rate or morph detection (there are no morphs of these sources; false-alarm test only);
  - a high-resolution result;
  - a benchmark or generalisation statement;
  - a cause of any source effect;
  - a separate effect of enlargement across geometry groups (it takes two values, about 1.7x and 3.5x; M5).
- **What the paper can say:** own-rule false-alarm rates on unseen low-resolution genuine frames (1.7x and 3.5x
  enlargement, with a black border), on development sources only.

## 1. Networks (fixed)

Tars in `/mnt/t7/smad_next/PN1/results_rented/`, with sha256:

| Network | sha256 |
|---|---|
| A_s401 | 59696efdcf711381f28f3e083c8000552f3d4f95eea477ef8781eff9cb1ecda5 |
| A_s402 | 24ed27449a9a3531c9f7e6a1f35c7d7bb09c834f904a337d1f95c4f33f2c7731 |
| B_s401 | 343148a70d960dddf00a4455c9da9b130632fd9d4e8ea1c08ae521f891f40c6e |
| B_s402 | 461a54431af8a91f6dba372ec2139ec86234651a21d317a3c5424477d68d5f76 |
| Bn_s401 | 194841842c1d70c23e06c090c122268a2a4dd659aeef9cb33c9553335266207f |
| Bn_s402 | 8eda3a619445b331dc0974b439cfe8e595f164c5bb3ce8f688c984b10f03f78f |
| C_s401 | fbe4f2a395ccda4446a8e48b348cefc878fdad558e62c15268ecebf3a8a808aa |
| C_s402 | d6372e42c55c915a9122e11b2f54257cd5b1125f3423b8d39ddb3d56bfc2c6bb |
| Sb_s401 | ea96a20e9a90b38bd150f28b006d25c0e1de267e1de74320379014f76ce84eb2 |
| Sb_s402 | d2e5214683a3a6dc28de0d26ff8f6c3175d0d14942697791f659688804776d75 |
| Bv_s401 | 49ab0c0d8774130931f4853bf003ac4c8684ab7a91be73f88eef15bac58d99e2 |
| Bv_s402 | ca5eb37665028970471e9d23bcba1336b418acf36bcd3aeed304b0a756b1f52f |

- **Rebuild and score.** meta.json + last_trainable.pt on the PN1 code and base CLIP weights (FS1 tree), through
  `src/PN1/rescore.py` unchanged (sha256 `6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e`). Logit
  without flip. Own rule: flagged if logit > 0. Last checkpoint, no selection.
- **Disclosure (M7).** Seed equals machine: seed 401 was trained on pn1a and seed 402 on pn1b (two A100 hosts).
  A, B, Bn and C were trained and scored with PN1 pack 1; Sb and Bv with pack 2.
- **Arm roles.** A plain, B protocol, Sb protocol plus spliced positives. Bn, C and Bv are printed only.

## 2. Pools (exact counts)

Manifests: `/mnt/t7/smad_next/TT1/raw_manifest.csv` (`a7aebe163328d12652c512fcb169152e7c3c4c31f63833d91e1ae3d63dd12168`)
and `aligned_manifest.csv` (`8b3c6fa932ac24c13a086984468539ba841f2facc1ac883be34c89b1c6971bef`). Definitions are in
`src/TT1/tt1common.py`.

### 2.1 Unseen pools

- **U_p (primary): 21,035 frames.** aligned = 1 and enlargement in [1.2, 2.5] (224 px frames) or [2.5, 5.0] (112 px
  packs).
  - Per source: Replay-Attack 200, MSU-MFSD 65, OULU-NPU 989, CASIA-FASD 150, LFW 5,995, CALFW 4,978, CFP-FF 4,725,
    AgeDB 3,933.
  - The band excludes 54 aligned frames: LFW 40, CALFW 9, CFP-FF 1, AgeDB 4.
- **U_all: 25,241 frames.** Printed for R1 and R3 only.
- **Families.** 7, weighted equally: replay_attack, msu_mfsd, oulu_npu, casia_fasd, lfw_calfw, cfp_ff, agedb_30.
- **Persons (M2).**
  - Anti-spoofing sets: file-name person id.
  - Packs: pseudo-identity = connected component of "same" pairs. Components split true people: CFP 1,586 components
    for 500 people, AgeDB 2,338 for 568, and LFW/CALFW share people across separate components.
  - Pack half-widths are multiplied by sqrt(components / true people): cfp_ff 1.78, agedb_30 2.03, lfw_calfw
    sqrt(7,957/5,749) = 1.18 (also applied to the lfw and calfw sources separately). The interval becomes
    [p − k(p − lo), p + k(hi − p)].
  - This applies to every pack interval that enters a rule (TT-H1, TT-H4, TT-H5, TT-H6). Anti-spoofing intervals use
    k = 1.

### 2.2 Reference pools (rescored in the same job as U; reads use only that job's logits)

- **R_cam: 417 native training-source camera photos of held-out persons** (FRGC / colorFERET): development ladder R0
  100, test ladder R0 191, AF0 development photos 126. These are the strength-empty rows of the FS1 `pn1_eval.csv`
  (`f0f29f22…`). Persons = host.
- **R_ffhq.** FFHQ bona fide orig, 2,000 images (HN2 list `4c0caa89…`). One image = one person.
- **M_ffhq.** FFHQ landmark_complete orig morphs, 1,000. Used only for the unit u and the gate.

### 2.3 Border-matched references (constant-colour region blanking; approved by the lead)

- **Mask (M3).** The largest exactly-zero region connected to the frame edge, in a U_p frame: the 8-connected
  component of pixels whose maximum over channels is 0 that touches the frame edge and has the most pixels. This
  replaces "every black pixel", which also caught dark pixels inside the face.
- **Draws.** `numpy.random.default_rng(20261121)`.
  - R_cam^border(f): for each family f (order above) and each R_cam image (by id), one U_p frame of family f (frames
    by id). 2,919 images.
  - R_ffhq^border: one frame from all U_p frames per R_ffhq image (by id), after the R_cam draws. 2,000 images.
  - The masked pixels are set to (0,0,0).
- **Caveat (M3).** In U frames the edge where the black border meets the photo is softened by prep_eval's warp;
  blanking makes a hard step. Blanking also removes the reference photo's own surround.
- Script: `src/TT1/build_border_ref.py` (sha256 in the pins section). Images:
  `/mnt/t7/smad_next/TT1/border_ref/`. A first build with the "every black pixel" mask was made before this
  registration and is replaced (it was never scored).

### 2.4 Crop-geometry-matched references (amendment M4; lead ruling R1; parameters fixed here, before building)

For each of the 417 R_cam images and each geometry group g:

1. **Integer slice (lossless, no resampling)** of the R_cam canonical 512x512 frame to the median crop box of group g
   in the canonical frame. The box is measured from the non-black bounding boxes of the U_p frames by
   `src/TT1/geometry.py` → `crop_geometry.json`, before any score.
   - g224 (anti-spoofing, 1,404 frames): rows 84:476, columns 60:451 (391 x 392 px).
   - g112 (packs, 19,631 frames): rows 21:423, columns 53:455 (402 x 402 px).
   R_cam frames have the canonical eye positions, so the box applies without detection.
2. **Shrink and enlarge through the approved stored-small path, run unchanged.** `e7_branch(P, img, med_ied)` of
   `src/AF0/soften.py` (sha256 `aa90f2719e13b934b5de0171925f1cec13b22722d48f4eea5ee8a9273ded4212`; the verbatim
   E7 'resmatch' branch of prep_eval.main, used for the fm61 / amsl112 copies).
   - native IED from `prep_eval.kps`;
   - if native IED > med_ied: `prep_eval.degrade(img, "R", scale = med_ied / native IED)` (cv2.INTER_AREA);
   - then `prep_eval.align` (prep_eval.py `374408ab…`).
   Target med_ied = the group's median source IED: g224 76.94715 px, g112 37.6995 px. These are new strength values
   of the same function; no new resampling code. A crop whose detection fails is recorded and kept as prep_eval
   returns it (aligned = 0), and is excluded from the reads.
3. **Output.** R_cam^geo224 and R_cam^geo112, 417 images each (834), lossless PNG, in
   `/mnt/t7/smad_next/TT1/geo_ref/`. Script `src/TT1/build_geo_ref.py` (sha256 in the pins section).

What the geo reference does not match: JPEG history (U frames are JPEG), sensor and capture conditions, sharpness.

### 2.5 Scoring list

`tt1_score.csv`: 34,411 rows.
- fam "gate" (3,417): R_cam 417, R_ffhq 2,000, M_ffhq 1,000.
- fam "tt1" (30,994): U_all 25,241; border references 4,919; geo references 834.

### 2.6 Fixed strata

`strata_edges.json` (`4aa95f038397bd45b4446e59b3c696b03e091d042c2bfd5ff99d423fe0fdb798`).

## 3. Thresholds and scale (M6)

- **τ_0.5 (logit > 0)** is the only deciding threshold.
- **τ_cam** is printed only, labelled "saturated band (head bounded at about ±3.87)".
- **Floor.** floor = −‖w‖₂ + b of the network's linear head (from last_trainable.pt).
- **Floor-tied label.** Each pool's share within 0.05 logit of the floor is printed. An AUC read whose two pools both
  have more than 50% at the floor is labelled "floor-tied". All AUCs use mid-rank ties.
- **Unit u.** u = median logit(M_ffhq) − median logit(R_cam). Reads in u units are labelled "unit degenerate" if
  u < 1.
- **ρ reads.** For an arm whose U_p frames of a pack have more than 50% at the floor, the ρ read of that pack is
  labelled "floor-tied" and not used in TT-H4.

## 4. Platform and gate (lead ruling R4)

- **Platform.** WCSS H100: one job, `--extra=FORCE_RM_TMPDIR`, partition lem-gpu-short, 1 H100, 8 CPUs, 64 GB, time
  limit 2 h.
  - IO in $TMPDIR: the pack tar, the network tar, and the library tars pylib.tar and pylib_a12.tar (smadcvpr/packs,
    sha256-checked).
  - Container `/lustre/software-data/container-images/pytorch_latest.sif`, as the AD4 WCSS tasks.
  - One result tar back to `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/TT1/`. No PNG on Lustre except
    inside the pack tar.
  - Submitted only after the pins commit and an 8-row WCSS test job on gate rows (rows already scored). No placeholder
    or slot job.
  - If sbatch fails once, the lead is told and the fallback is the DGX GB10 with the same gate and rules.
- **Gate (G-DGX tolerances, for all 12 networks; gate rows scored first, in the same job, before any TT1 row).**
  `src/TT1/gate_check.py` writes `gate.json`. A network passes iff all of:
  - max |Δlogit| ≤ 0.02 over the 3,417 gate rows against the stored A100 logits (R_cam from each network's
    scores_eval.npz; FFHQ from the HN2 tars for A, B, Bn, C and the amendment-14 tar for Sb, Bv);
  - zero own-rule decision changes;
  - |ΔAUC(R_ffhq vs R_cam)| ≤ 0.002 (mid-ranks);
  - Kendall τ-b ≥ 0.99 between new and stored logits on R_cam (417).
  If any network fails, the job exits non-zero after writing gate.json and its log, and scores no TT1 row. Then no
  TT1 read is made, and the lead is told with the numbers.
- **Stated risk.** The 0.02-logit tolerance is close to the floor band (R_cam's 5th-95th percentile spans about
  0.03-0.10 logit), and Kendall on floor-tied R_cam logits is sensitive to small numerical differences (AD4 failed a
  rank gate this way). A gate failure is a platform finding, not a TT1 result.
- **Keep rule.** The result tar is copied to `/mnt/t7/smad_next/TT1/results/` and verified by sha256 before anything
  is removed on WCSS. The pack and network tars stay on Lustre for the FS1 block.
- **Cost.** 34,411 rows x 12 networks plus the gate. Estimated under 1 H100-hour; time limit 2 h.

## 5. Reads (every number printed for every network; U_p unless stated)

Bootstraps: 2,000 draws, `default_rng(20261122)`. Persons are resampled within each source and within R_cam (host);
R_ffhq images are resampled individually. The same draws are used for every network (paired). Pack intervals are
inflated as in 2.1.

- **R1.** Own-rule flag share per source and family.
  - Decision interval: person bootstrap (inflated). Clopper-Pearson printed only (M1).
  - Also printed: U_all, R_cam, R_ffhq, R_cam^border(f), R_cam^geo(g), and every share at τ_cam (labelled).
- **R2.** Median logit, IQR, share at the floor, and shift from R_cam's median, in logits and in u.
- **R3.** AUC (mid-ranks; "floor-tied" label as section 3):
  - (a) U_s vs R_cam;
  - (b) U_s vs R_ffhq;
  - (c) U_s vs R_cam^border(f(s));
  - (d) R_ffhq^border vs R_ffhq;
  - (e) R_cam^border(f) vs R_cam, per family (M3);
  - (f) R_cam^geo(g) vs R_cam;
  - (g) U_s vs R_cam^geo(g(s));
  - also the share of U_s above R_cam's median logit.
- **R4.**
  - (a) Within each pack: Spearman ρ(logit, log lap_var); flag share and median logit per fixed sharpness quintile.
  - (b) Anti-spoofing sets: the same per pooled quintile; per-source order of flag share against median lap_var
    (Spearman over 4 sources, printed, no test).
  - (c) Leave-one-family-out OLS of logit on z(log enlargement), z(log lap_var), border_frac, greyscale, with equal
    family weights. Prediction error e_f of the held-out family's mean logit, in u. Bootstrap refits for the interval.
    The logistic flag-share prediction is printed only. Labels (M5): enlargement takes two values between groups;
    greyscale is essentially pack-only, so AgeDB's 27.5% is extrapolated when AgeDB is held out.
  - (d) The same OLS with family indicators: indicator coefficients in u, with inflated bootstrap intervals. The
    enlargement coefficient is printed, labelled "identified by within-family detection noise", and is not
    interpreted (M5).
- **R5.** Per network: F̄ (mean of the 7 family flag shares), F̄ without MSU-MFSD (sensitivity), F_max, S_F (SD of
  family shares), Ā and S_A (mean and SD over families of R3(a)). Paired differences B − A, Sb − A, Sb − B within seed,
  with intervals.

## 6. Hypotheses, predictions, falsifiers (fixed now)

An arm verdict needs both seeds; split seeds give "mixed". Every arm statement is "on seeds 401/402 (two machines)".

- **TT-H1. The own rule does not transfer** (M1).
  - Family f fails for a network if the lower bound of the person- or pseudo-identity-bootstrap interval (inflated) of
    its own-rule flag share is above 5%. The Clopper-Pearson bound is printed only.
  - The R_cam own-rule share is printed. TT-H1 is uninformative for a network whose R_cam share exceeds 5%.
  - Prediction: A fails in ≥ 4 of 7 families on both seeds; B and Sb fail in ≥ 2 of 7 on both seeds.
  - Falsified for an arm if, on both seeds, every family's upper bound is ≤ 10%.
- **TT-H2. Unseen photos sit above the training-source floor.**
  - Prediction: R3(a) ≥ 0.90 for ≥ 6 of 8 sources, for every network.
  - Falsified for a network if R3(a) ≥ 0.75 holds for ≤ 3 sources.
  - Floor-tied reads count, with their label printed.
- **TT-H3. The border is material.**
  - "Border material" for a network if R3(c) ≤ R3(a) − 0.10 for ≥ 4 of 7 families AND R3(e) ≥ 0.65 for ≥ 4 of 7
    families AND R3(d) ≥ 0.65.
  - "Border not material" if |R3(c) − R3(a)| ≤ 0.03 for ≥ 6 of 7 families AND R3(e) ≤ 0.55 for ≥ 6 of 7 AND
    R3(d) ≤ 0.55.
  - Otherwise "inconclusive".
  - Prediction: A "border material" on both seeds.
- **TT-H4. Softer photos score higher at fixed size.**
  - Prediction for A: ρ ≤ −0.15 in ≥ 3 of 4 packs on both seeds. For B and Sb: |ρ| smaller than A's in ≥ 3 of 4 packs
    on both seeds.
  - Falsified for an arm if ρ ≥ 0 in ≥ 3 of 4 packs on both seeds.
  - Floor-tied packs (section 3) are excluded; the count is over the remaining packs, with at least 3 needed.
- **TT-H5. Source beyond geometry, enlargement and border** (within geometry group, R3(g)).
  - "Source matters beyond geometry" for a network if, for ≥ 2 of the 8 sources, R3(g) ≥ 0.75 with lower interval
    bound > 0.65 (persons of U_s and hosts of R_cam^geo resampled; inflated for packs).
  - "Geometry explains" if R3(g) lies in [0.40, 0.60] for ≥ 6 of 8 sources.
  - Otherwise "inconclusive".
  - Arm verdict: both seeds agree.
  - Prediction: "source matters" for A (JPEG and capture differences are not matched).
  - R4(c)/(d) are printed under the M5 labels and decide nothing.
  - If R3(f) ≤ 0.55 for a network, the geo reference did not reproduce the U frames' storage effect on the training
    source. TT-H5 is then printed with the label "geo reference weak".
- **TT-H6. Arms (descriptive; M7 and lead ruling R3).** Descriptive on seeds 401/402 (two machines). No arm, seed or
  threshold is chosen from TT1. FS1's frozen contrasts and the MS1 arm choice are not revisited.
  - Printed: R5 and the paired differences B − A, Sb − A, Sb − B with intervals. The intervals capture image sampling
    only, not training variance.
  - A sentence "X has lower genuine flag rates than Y on seeds 401/402" is printed only if ΔF̄ ≤ −0.03 with the paired
    interval excluding 0 on both seeds. Otherwise "not distinguished on seeds 401/402".

## 7. Guards

- No detector gates on resolution, size, format or source; U_p is an analysis pool.
- No re-run after seeing scores, except an infrastructure failure re-run unchanged.
- Reader `src/TT1/tt1_read.py`: tested on random mock scores only, sha256 in the pins section.
- **MS1 coordination (lead ruling R5).** The MS1 pack contains 21,089 TT1 aligned photos. Before any MS1 network is
  scored on TT1 pools, R_ffhq must be disjoint from MS1's FFHQ training images.
  - MS1's exclusion proof (`experiments/MS1_multi-source-training-set/exclusion_proof.json`, commit 9f02906) states
    0 overlaps by key and by raw sha256 with the 20,000-key FFHQ-Morphs universe, which contains the 2,000 R_ffhq
    keys.
  - It also states a largest glintr100 cosine to the ffhqm references of 0.3964 (cut 0.40). refs_found is 3,999 of
    4,000: one reference image was not found, a limitation to cite.
  - TT1 scores no MS1 network in this registration.

## 8. Stop rule

- One WCSS job, time limit 2 h. On an infrastructure failure, one unchanged re-run.
- DGX fallback: one GPU process, thread caps, at most 1.5 h.

## 9. FS1 block (later)

- The same pack and list, with a second network tar `tt1_nets_fs.tar` (16 FS1 networks; tar sha256 from FS1's
  `fs_kept/`), after FS1's registered read is committed.
- Gate: the same tolerances on R_cam and on FFHQ rows with stored FS1 logits (FS1 scored the HN2 list in its own
  pack).
- TT-H6 per seed 403-407, descriptive; no choice.
- Pins added by amendment before scoring.
