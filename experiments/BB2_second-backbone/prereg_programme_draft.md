# Draft registrations for the DINOv3 programme (BB2 owner, 13 Nov 2026 18:36; DRAFT, nothing registered, nothing submitted)

Plan: `PLAN_DINOV3_PROGRAMME_20261113.md`. Common to all drafts: development data only (FS1 pack rows, MS1 FFHQ hold-out,
TT1 development pools, NIST MEDS aggregates; no FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace or sealed row);
WCSS H100, `~/dmenv` unchanged; every rescoring job runs the unchanged `src/PN1/rescore.py` through
`src/TT1/rescore_tf32.py` with `src/BB2/precision_probe.py --expect-gpu "NVIDIA H100"` and the C2P.2 gate against the
network's in-fit logits (p99 |Δ| ≤ 0.05, max ≤ 0.10, decisions agree ≥ 99.5%; a gate-failed network is not read);
read once when all jobs of the batch have ended, latest 15 Nov 2026 18:00 CET, later rows labelled late; each read
committed with its reader before any score of it exists; each draft goes through an Opus pre-run check before it is
registered; the networks are E3's 15 (frozen in `seed_mode_L.json` before any is opened). Counting: five-seed (FS1/C2P)
rules if E3's mode is five, else three-seed BB2 rules.

## D-W2a: PR1 battery on E3's networks (zero GPU)
Reads Z1-Z6 of `experiments/PR1_protocol-reads-existing-networks/prereg.md` unchanged (warp-only, same-person morphs,
same-person and seam-only splices, training-row fit, operating point, engine transfer, softness, 27-statistic floors)
from E3's stored scores; reader `src/BB2/pr1_read_bb2l.py` = `src/PR1/pr1_read.py` with E3's tar names and folders (diff
pinned); registered sentences per read as in PR1, with the label "DINOv3 ViT-L/16, E3 learning rate". Compared with
CLIP's PR1 values at the same seeds, printed beside; no new margin.

## D-W2b: GAN and diffusion families (PR1 GD0-GD2) on E3's networks
Pack `pr1_gd.tar` (3.9 GB, sha256 in `/mnt/t7/smad_next/PR1/pr1_gd.tar.sha256`) staged on WCSS `packs/BB2/`; one job
`bb2l_gd.sbatch` (copy of `bb2_c2p.sbatch`'s pattern) rescoring the 15 networks on the GD rows; reader `gd_read.py`
copy (PR1's registered GD reads and sentences: StyleGAN morph vs camera photo, morph vs one-photo render, MIPGAN one-
photo renders flagged, diffusion render path). About 1.5 H100-h.

## D-W2c: C2P (contrast 2-prime, H-new-1) on E3's networks
`bb2_c2p.sbatch` unchanged with `BB2_TASKS` = the 15 BB2L tasks, `BB2_C2P_RESULTS=/lustre/pd03/hpc-narolski-1790461090/smad-next/results/BB2L`, `BB2_C2P_OUT=BB2LC2P`;
reader `bb2l_c2p_read.py` = `bb2_c2p_read.py` with BB2L names, mode file `seed_mode_L.json` and the clip choice
`clip_choice_L.json` committed before the read (amendment 3 rule). About 0.5 H100-h.

## D-W2d: unseen genuine sources (TT1) and NIST MEDS (TT-M1) on E3's networks
TT1 pack (`tt1_pack.tar`, 8.1 GB) and the MEDS pack (`src/TT1/meds/build_meds_pack.py`; MEDS images and identifiers
never leave the pack; only aggregate shares and stratum sizes are written) rescored in one job each; readers
`tt1_read_fs.py` / `tt1_read_meds.py` copies with E3 names; TT1's registered hypotheses TT-H1 (transfer), TT-H3 (border),
TT-H4 (softness), TT-M1 (MEDS transfer) with their rules. About 2.3 H100-h.

## D-W2e: blend-difference attribution (BD1) on E3's Sb networks (zero GPU)
Existing image statistics `/mnt/t7/smad_next/BD1/d_feats.csv` and the S3/S4 rows of each E3 fit's `scores_eval.npz`;
`bd1b_read.py` / `bd1c_read.py` copies with E3's names; BD1's registered reads.

## D-W2-merged: C2P, GD, TT1 and MEDS rescoring of E3's networks in one H100 job (about 4.5 h; pre-submitted with --dependency=afterany:6313860 on the lead's go; pre-run check first; MEDS needs a new WCSS sbatch)

## D-W2f (only if E3's splice-fit gate fails on more than one seed of the read set): learning-rate selection on training rows
Arm Sb, seed 403, LoRA learning rates 3.33e-5 and 1e-4 (2 fits, 6,250 steps, everything else as E3). Chosen value: the
lowest of {1.17e-5 (E3, already fitted), 3.33e-5, 1e-4} at which Sb's training AUC lad_S4 vs lad_S3 ≥ 0.80 and its own-
rule training accuracy ≥ 0.95 with finite loss. Only training rows are read before the choice is committed; the
development scores of the two sweep fits are never read. Then A, B, Sb x 403-407 at the chosen value (15 fits), read
exactly as E3. If no value passes: "DINOv3 ViT-L/16 does not fit the splice task in this recipe" and nothing more.

## D-W3a: four arms on DINOv3 at the E3 learning rate (submitted only on the lead's and the author's go)
Arms Sp (AB1's `train_Sp.csv`, cf386dc7…), SbS (AB1, 9c7e43ff…), SE (SE1's manifest, sha256 from SE1's pins), each x
403-407, DINOv3 ViT-L/16 at LoRA lr 1.17e-5 (head 3.33e-5), the AB1 evaluation pack with the BB2 overlay (in-fit scores
include C2P, landmark_combined, S0/S3/S4); compared within seed with E3 Sb by AB1's and SE1's registered predictions and
margins (H-sp3, H-ab2/ab4, the SE target and guards). CLIP ViT-L/14 size control: A, B, Sb x 403-407 with
`a12_clip_vitl14_madation`, CLIP learning rates unchanged, FS1 pack, read with FS1's contrasts and C2P as BB2. Learning-
rate guard and seed-mode freeze as E3. About 48 H100-h. If E3's gate fails, all DINOv3 arms of this wave are read as
"under-fitted" and not interpreted.

## D-sel: DINOv3 part of the next-version selection rule (plan section 7), to be committed before E3's read, inside one programme-level rule fixed by the lead or the author across DINOv3, SbFM, GX1 and RZ1
