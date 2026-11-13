# Hypothesis strategist: experiments for the idle GPUs, 13 Nov 2026 (results-reviewer, Opus; read-only)

**Strategist report, 13 Nov, S-MAD sprint (read-only; no benchmark, valx.csv, FST or A12SP file opened)**

## 0. Three facts that change the plan

1. **"The seam shortcut is open" is the wrong label.**
   - Sb flags 0 of 100 development S0 images (seam present, no blend inside the face; `PN1 prereg.md:778`, seeds 401/402).
   - Sb separates S3 from S0 at 0.86–0.93 (`REVIEW_PN1_FS1_20261113.md` F6).
   - So Sb is not reading the seam. It reads "a blend inside the face", and it cannot tell whether that blend comes from one person or two (S4 against S3 is 0.78–0.82).
   - The 31–41% of S3 flagged and the 26–47% of landmark morphs missed sit in the same score band. Any threshold or training change that lowers one will raise the other.
   - The SE1 owner should register its problem as "identity against same-person blend", not "seam". My prediction: SE1 cuts S3 flags and loses landmark_combined AUC, because no experiment in the record shows a second-identity reading above 0.60–0.75 (AR1, AS0, FZ2, PD1, SM1 A15–A22).
2. **No arm started today can become the method without an author amendment.**
   - FINAL §1 freezes only Sb, then B, then the MS1 version of Sb (`FINAL/prereg.md:41-57`).
   - SE1 and every variant below are ablation rows unless the author registers, before their reads, one rule like this: "Sb is the default. A variant V replaces it only if V passes C2P and H-new-1 is falsified on its own seeds, AND V's landmark_combined AUC is at least +0.03 above Sb's, paired, on at least 4 of 5 seeds, AND V's S3 flag rate is not higher. At most one replacement, in the fixed order SE1, then Sb-long, then Sb+FM. Every arm is reported."
3. **By our own registered rules, SOTA on MAD22 and FRLL-Morphs is a descriptive claim at most.**
   - FINAL §2 labels both sets "seen during development". They are not confirmatory.
   - FINAL §4 marks any cell where a morph-free network has EER ≤ 5% as "shortcut-saturated", and such a cell cannot support a SOTA sentence. AD4's morph-free networks reach FRLL AMSL 1.1%, FaceMorpher 4.1%, Webmorph 1.0% and MAD22 FaceMorpher 0.0%.
   - That leaves FRLL OpenCV and StyleGAN, and MAD22 OpenCV, Webmorph and MIPGAN, as the only cells that could carry a SOTA sentence. StyleGAN and MIPGAN are GAN families our recipe has never trained on.
   - The author needs to hear this before the freeze. The realistic winning form is the history-matched one, where the releases lose 12–19 points (RS1). That is FINAL outcome row 3.

## 1. Zero-GPU reads first (existing FS1 tars; register as printed reads, about 20 minutes each)

| # | Read | Decides |
|---|---|---|
| Z1 | Sb's training-row logits for S3/S4 (if the tars hold them as tier 1 did; otherwise about 0.1 GPU-h to rescore 1,500 training rows). If training S3 rows are also flagged: Sb is underfit (training accuracy 0.989–0.991 against 1.000 for A and B). If they are fit: it does not generalise. | Whether Sb-long (#4) or SE1 (data) is the right lever |
| Z2 | Calibration. τ at 5% flags on a multi-source development genuine pool (FFHQ HN2 native, TT1 pools, MS1 CFD). Print APCER on landmark_combined, development S4 and FaceMorpher R4, and BPCER on each pool, per seed. Then the TT1 H-new-4 trade-off: ρ between genuine flag rate and misses over the 15 networks. | The author's F10 ruling (FINAL §10 item 9) and the replacement for τ_dev(i), which flags 96–98% of FFHQ genuine photos |
| Z3 | Tool transfer. The training engine is only the OpenCV-style one (`manifests2/train_Sb.csv`: tool = smdd on every row). Read A, B and Sb on test-ladder FaceMorpher R4 (191) against R2w/R0, beside OpenCV R4 (573). FFHQ landmark_complete against landmark_combined is already in hand. | Whether #6 is worth running; risk 3 |

## 2. H100 experiments, ranked by value for "removes named shortcuts and still detects morphs"

ViT-B/16 LoRA fit: 69–85 min on A100, about 1 H100-h with overhead. All reads are on development data only.

| # | Experiment (plain name, proposed ID) | Hypothesis; pass / fail | Arms, seeds | Data and code that exist | H100-h | Owner | What each outcome changes |
|---|---|---|---|---|---|---|---|
| 1 | **GAN and diffusion families of the development set, read with existing networks (GD0)** | Sb's landmark-trained ranking transfers to StyleGAN morphs. **Pass:** stylegan_wplus and stylegan_w against their E7 genuine pools, AUC ≥ 0.80 on ≥ 4 of 5 seeds. **Fail:** ≤ 0.65 on ≥ 4 of 5. Diffae printed only (FINAL M5 predicts render-path behaviour). The 27-statistic floor is printed beside it. | 15 FS1 checkpoints + 3 Sp, later MS1 and BB2; no training | `ffhqm.csv` (sha256 732b53c8…; 3 × 1,000 morphs, 2,000 bona fide plus per-family resmatch pools; no PN1 network has scored these families); `src/PN1/rescore.py` 6f6eede7…; `cues27.py` | 1–1.5 | C2P/PN1 owner, after C2P | Fail: the paper scopes detection to landmark families, the FRLL StyleGAN headline (FINAL M1) is pre-stated as weak, and #8 becomes relevant. Pass: GAN cells become a SOTA candidate. It also predicts FEI gtest (StyleGAN W+). |
| 2 | **Leave-one-component-out ablation of Sb (AB1)**: which negative removes which shortcut | H-ab1: the stored-small copies of both classes carry the storage reduction. Sb without them shows a C2P Δf ≥ ½ of A's on ≥ 4 of 5 seeds; falsified if ≤ ⅓ of A's. H-ab2: warp-only images carry the warp/surround reduction. Without them, development R2w flags rise ≥ 5 points. H-ab3: halves carry the softness reduction (softened-photo flags). | Sb−zero, Sb−halves, Sb−stored-small, A+stored-small (history crossing only); volume-matched like Bv; seeds 403–407 (Sp already covers Sb minus the matched splice negatives) | Manifests from `train_Sb.csv` by dropping kinds (CSV only, `mk_sp.py` as template); FS1 pack 96c31ae2…; C2P reader and MS1 hold-out | 20 | PN1 (Sp) owner | The paper's mechanism table. Without it, "the protocol removes X" cannot name which part does it. |
| 3 | **Fresh-seed replication of A, B, Sb (FS2)** | The C2P result (margins set knowing FS1's effects) and contrast 1 replicate: Sb passes C2P at amsl112 on ≥ 4 of 5 new seeds, and Sb−B ≥ +0.10 on 5 of 5. Fail: ≤ 1 of 5. | A, B, Sb at seeds 408–412 | `drive_fs.sh`, the FS1 pack, `c2p_read.py`, `fs_read.py` | 15 | FS1 owner, on WCSS | Answers "you replaced a failed gate". If the author amends FINAL "networks read" before the freeze, the sealed read uses 10 seeds (and "8 of 10 better" in place of "4 of 5"). |
| 4 | **Sb trained twice as long (SL1)**, run only if Z1 shows underfit | Sb is under-trained. **Pass:** 12,500 steps cut development S3 flags by ≥ 10 points and add ≥ +0.02 landmark_combined AUC on ≥ 4 of 5 seeds; landmark_combined > 0.886 on ≥ 4 of 5 would allow "beyond the best single statistic". **Fail:** S3 change < 3 points and AUC change < +0.01. C2P is re-read as a guard. | Sb-long, 403–407 | FS1 pack, unchanged `train.py` with a steps argument (check that it exists) | 8–10 | New owner | The only cheap lever on the 0.860 against 0.886 gap that needs no new image operation |
| 5 | **Seam-shortcut training arm (SE1)**, already drafted | Reframed: more same-person in-face blend negatives push Sb toward identity. **Pass:** S3 flags ≤ 10% on ≥ 4 of 5 seeds AND landmark_combined ≥ Sb − 0.02 AND C2P still passes. My prediction is that the AUC guard fails. | as drafted, 403–407 | SE1 owner's files | about 5 | SE1 owner | Pass: the paper can claim "not a same-person blend detector". Expected fail: the paper says the method detects in-face blending, not identity. That is honest and still publishable. |
| 6 | **Second morphing engine (Sb+FM, TD1)**, run only if Z3 shows a tool gap ≥ 0.03 | Unseen-tool misses are engine-specific. **Pass:** landmark_combined (Mediapipe, an unseen tool) +0.02 on ≥ 4 of 5 seeds. **Fail:** < +0.005. | Sb plus FaceMorpher whole-frame R4, its R2w and halves, from **training hosts only**. No FaceMorpher splices: its negatives have almost no seam (`REVIEW_SPLICE`). 403–407 | AR1 ladder images (both engines, 536 hosts); unchanged FaceMorpher outputs | 5 | PN1 or new owner | Risk 3; closes "trained on one engine" |
| 7 | **SelfMAD retrains (AD5) moved to idle WCSS H100s now** (already registered; not new) | At 15–20 h per seed on H100, ≥ 3 of 5 seeds land before 14 Nov 18:00 | SelfMAD 401–405 | `packs/AD5/code_v5` (fix under test, job 3548459) | about 90 | AD5 owner | SelfMAD is the only release that reads a face-confined blend (AR1). Without its retrain row, the comparison table has a hole at its strongest rival. |
| 8 | **GAN extension with matched one-person GAN negatives (GX1)**: only if GD0 fails, and only after an author ruling on whether a one-person GAN reconstruction is genuine | **Pass:** two-person MIPGAN above its one-person reconstruction ≥ 0.70 (AG1: 0.65–0.72), and FFHQ StyleGAN +0.05 over Sb. | Sb + AG1 FRGC/colorFERET MIPGAN-I/II morphs, with R2/R3 as negatives | AG1 aligned scoring frames (`/mnt/t7/smad_next/AG1/scoring`). Host disjointness from the test ladder and from the PN1 split's exclusions must be checked through the PN1 split files, never valx.csv. | about 5 | AG1 owner | Probably post-freeze. A GAN arm trained against camera photos only would be the render-path shortcut we audit, so it must not be a candidate. |

**Not run, and why:**
- **Morph-free / one-class variant:** AD4 already shows morph-free softness networks saturate the cells; ID0 already closed the averageness route.
- **Diffusion training arm:** FZ2 and SM1 A15–A22 show only render-path signal. A protocol-consistent arm would sit near 0.65, and a render-path arm is the shortcut itself.
- **CLIP ViT-L/14 or other capacity forks as candidates:** too many forks and winner's curse. BB2 already covers the backbone question.
- **Native-resolution crops instead of the 512→224 resize:** possibly the real cause of the gap to noise_std_face, but cropping is not on the OWNER_BRIEF list of allowed image operations. **Author item.**
- **Any further MS1 P2 work:** at ceiling (TT1 review Q7).

## 3. The three biggest risks to competitiveness on MAD22 and FRLL-Morphs, and today's development tests

1. **GAN families are untrained:** MIPGAN-I/II are 2 of the 5 MAD22 families, and StyleGAN is FINAL's headline FRLL family. Test: GD0 (#1).
2. **The decision point.**
   - At τ_dev(i), 96–98% of genuine photos are flagged. With F10 unanswered, the confirmatory endpoint reads "lost" whatever the ranking.
   - At the own rule, Sb's S3 flags and landmark misses overlap.
   - Test: Z2. The author's F10 ruling is needed **before the freeze**.
3. **Standard form against released MADation ViT-B/16 through its own crop, on landmark cells.**
   - Our training uses one engine.
   - All benchmarks share one pool of 204 FRLL genuine photos, whose smiling half carries capture detail.
   - Several cells are shortcut-saturated (fact 3).
   - Tests: Z3 and #6. A CFD neutral-against-happy genuine flag comparison from MS1 pools stands in for the smiling half.
   - Hedge: put the paper's comparison on the history-matched form.

Also note: if C2P leaves H-new-1 "not falsified", nothing is frozen. Keep B's fallback reads ready.

## 4. Compute I consider wasted or low-value

- **SE1 and every variant above without the amended selection clause (fact 2).** They can never be frozen.
- **CB1 re-implementations that do not reproduce:** FD-MAD at 6.12% published against 33–56% ours; A12BR M2, M6, M8 and M8O "worse". IDistill without released weights is likely to end the same way. These rows cannot honestly be the "best comparison"; the released checkpoints through their own crop are.
- **AD5 MixFaceNet-MAD retrains.** The release already reproduces its published numbers. Harmless if compute is free, but low value.
- **BB2's nine DINOv3 ViT-L/16 fits** (about 30 H100-h). Acceptable as a robustness row, but add GD0 and C2P to its reads rather than more fits.
- **More AD4 morph-free fits and more TT1 work on B.**

Key files:
- `/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/prereg.md` (§1, §4, §10 item 9)
- `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg.md` (lines 746–889)
- `/home/narolski/smad-next/experiments/reviews/REVIEW_PN1_FS1_20261113.md` (F6, F10)
- `/mnt/t7/smad_next/PN1/manifests2/train_Sb.csv`
- `/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv`
- `/mnt/t7/smad_next/PN1/manifests/pn1_eval.csv` (ladder FaceMorpher rows)
