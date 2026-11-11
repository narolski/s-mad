# Proposed deletions on the data drive (/mnt/t7), awaiting the author's approval

Started 11 Nov 2026 20:42 after the drive reached 100%. Nothing on this list has been deleted. Every entry is a
second copy: the place of the verified copy is given. Owners add their lists through the lead.

| Experiment | Path | Size | Verified copy |
|---|---|---|---|
| Morph-free networks (AD4) | /mnt/t7/smad_next/AD4/ad4_pack.tar | 11.2 GB | Athena packs/AD4 (sha256 1ad170be..., checked in every job); also on both rented machines |
| Morph-free networks (AD4) | /mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401 | 11 GB | unpacked copy of the same pack from the stopped owner's local test; outputs of that test are in experiments/AD4 |
| Morph-free networks (AD4) | /mnt/t7/smad_next/AD4/test/work/task_AD4_m3lperm_s402 | 12 GB | as above |
| Own-crop re-score (RS1) | /mnt/t7/smad_next/RS1/athena/rs1a_pack.tar | 9.0 GiB | Athena packs/RS1 (sha256 c1cf34dd..., checked in jobs 3544220 and 3545869) |
| Own-crop re-score (RS1) | /mnt/t7/smad_next/RS1/athena/rs1a_pack_amend.tar | 2.4 GiB | Athena packs/RS1 (sha256 6cdce864..., job 3545869) |
| Own-crop re-score (RS1) | /mnt/t7/smad_next/RS1/athena/rs1a_pack_raw.tar | 0.64 GiB | Athena packs/RS1 (sha256 3d8a359c..., job 3545869) |
| Own-crop re-score (RS1) | /mnt/t7/smad_next/RS1/athena/fetch/rs1a_smoke_3544220.tar, rs1a_smoke_3545869.tar | 0.15 GiB | Athena results/RS1; unpacked copies kept locally |
| SMDD rebuild (SM1) | /mnt/t7/smad_next/SM1/wcss/packs/SM1/sm1_c_pack_STALE_preA5.tar | 3.0 GB | superseded pack, marked stale by its owner |
| MIPGAN controls (AG1) | /mnt/t7/smad_next/AG1/athena/ag1_pack.tar | 2.8 GB | Athena packs/AG1/ag1_pack.tar (sha256 c6b9d2c9...); rebuilt deterministically by make_athena_pack.sh |
| MIPGAN controls (AG1) | /mnt/t7/smad_next/AG1/athena/pack/ag1_inputs.tar, ag1_code.tar | 0.33 GB | inside the Athena pack |
| MIPGAN controls (AG1) | /mnt/t7/smad_next/AG1/staging/packs | 0.21 GB | superseded WCSS packs; copy on WCSS Lustre smad-next/packs/AG1 |
| Retrains (AD5) | /mnt/t7/smad_next/AD5/packs/smdd_train_raw.tar | 4.6 GB | Athena packs/AD5 (hash checked by jobs 3544216, 3545882); source data also in Datasety/downloads/SMDD |
| Retrains (AD5) | /mnt/t7/smad_next/AD5/packs/wheels_madation.tar, wheels_selfmad.tar, wheels_score.tar | 8.2 GB | Athena copies hash-checked by jobs 3544216, 3545882, 3545948 |
| Retrains (AD5) | /mnt/t7/smad_next/AD5/wheels/ | 7.8 GB | the unpacked sources of those three tars |
| Retrains (AD5) | /mnt/t7/smad_next/AD5/packs/code | 2.6 GB | Athena copies checksum-compared; 2.3 GB of it are CLIP files also in ~/.cache/huggingface |
| SMDD rebuild (SM1) | /mnt/t7/smad_next/SM1/gpupack/: sm1gpu_img_test.tar (10.7 GB), sm1gpu_img_armsc.tar (6.6), sm1gpu_img_armsb.tar (6.5), sm1gpu_img_base.tar (5.5), sm1gpu_img_armf.tar (2.8), sm1gpu_code.tar (1.7), sm1gpu_code_v2.tar (1.7), sm1gpu_img_audit.tar (1.5), sm1gpu_img_arme.tar (0.6), sm1gpu_img_jpegeval.tar (0.2), sm1lora_manifests.tar, sm1lora_manifests_v2.tar | 38 GB | Athena packs/SM1, same names, each checked with sha256sum inside jobs 3545820, 3545893, 3544789 |
| SMDD rebuild (SM1) | /mnt/t7/smad_next/SM1/lease/sm1_c_out.tar (6.3 GB), sm1_b_out.tar (6.1), sm1_a_out.tar (1.6) | 14 GB | contents unpacked locally in /mnt/t7/smad_next/SM1/img/ (the copies on the rented machine are volatile) |
| SMDD rebuild (SM1) | /mnt/t7/smad_next/SM1/wcss/packs/SM1/sm1_c_pack.tar (2.9 GB), sm1_b_pack.tar (0.8), sm1_a_pack.tar (0.5) | 4.2 GB | CPU-build packs; their sources (SMDD renders, landmark files) still exist locally |
| SMDD rebuild (SM1) | /mnt/t7/smad_next/SM1/athena/sm1gpu_feats_full_3545820.tar (0.85 GB), sm1gpu_feats_f_3545893.tar (0.14) | 1.0 GB | extracted locally beside the tar; originals in Athena results/SM1 |

Still to be listed by their owners: the protocol-network tests (PN1, pack of 10 GB), the diffusion generation (DG1, pack of 3 GB).

Total on this list: about 135 GB.

Note, 11 Nov: owners removed their own rebuildable temporary files (test work folders, build intermediates): the MIPGAN controls owner 20 GB, the protocol-network owner 12 GB, the frozen-features owner 2.4 GB. Working copies of result tars fetched from Athena only for processing may be removed after processing when the hash of the Athena copy is recorded.
