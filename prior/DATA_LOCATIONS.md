# Where image sets and checkpoints live on disk

Directory listings only, taken 11 Nov 2026 on the DGX Spark (`ls`, one level deep). Nothing was opened. Where a one-line description rests on a README or on `CONCLUSIONS.md`, the source is named; otherwise the description is read off the folder name and marked "from the name". Sizes were not measured (a disk-usage scan timed out). No top-level entry in these four directories carries a sealed-data marker in its name.

Terms: **T7** = the 1.8 TB data drive mounted at `/mnt/t7`. **WCSS** = the Wroclaw supercomputing cluster. **Held-out** = evaluation sets never used for training. **A41g, A43 and so on** = experiment IDs in `INDEX.md`. **H1 to H4** = held-out morph families: Poisson-blended, diffusion embedding-midpoint, StyleGAN3 and MIPGAN-I.

## /mnt/t7/smad_heldout (held-out image sets, copied scores, working dirs per experiment)

- `a37_sg3ctl/`: StyleGAN3 render controls for A37 (cluster, data, models, work); from the name.
- `a41_diffae/`: DiffAE reconstructions for A41; from the name.
- `a41g/`, `a41g2/`: working outputs of A41 amendments G and G2.
- `a42/`: A42 working outputs.
- `a43/`: A43 data, generated images, packs, logs and copy-back checksums (listing shows `data`, `gen`, `packs`).
- `a44/`: A44 and A44R outputs, logs, upload and score checksums.
- `a45/`: A45 working directory.
- `a46/`, `a46_corrective_20261108/`, `a46_rgb_only_20261108/`: A46 outputs, corrective acquisition and the RGB-only run.
- `a47/`: A47 data, packs, run directories, scores (`a47_out`) and copy-back checksum list.
- `a50/`: A50 runs.
- `arc2face/`: Arc2Face diffusion morph set (registration draft `A22_registration_draft.md` inside).
- `ffhq_morphs/`: FFHQ-Morphs external set, built 2 Nov, README says no detector had scored it at build time.
- `h1_poisson/`: H1 Poisson-blended morphs (draft `A27_registration_draft.md`).
- `h2_embmid/`: H2 embedding-midpoint diffusion morphs (draft `A28_registration_draft.md`).
- `h3_sg3/`: H3 StyleGAN3 morphs and renders (cluster, data, logs, models, scripts, work).
- `h4_mipgan1/`, `h4b_mipgan1/`: MIPGAN-I held-out sets H4 and H4b; from the name.
- `mad22_incoming/`: the two MAD22 ZIPs received 8 Nov, merge audit and the later owncloud copy (per `MAD22_WORKING_DECISION_20261108.md`).
- `mad22_canonical_E7_inputs_v3_20261109T113746Z/`: canonical E7 inputs for MAD22; from the name.
- `mad22_canonical164_production_v1/`: production pack, plans and launch material for the 164-case MAD22 run; from the name.
- `mad22_production_A23_assets_v1/`, `mad22_production_cpu_stage_v1/`: MAD22 production assets and CPU staging; from the name.
- `mad22_production_cpu_failure6295412/`, `mad22_production_cpu_partial6295571/`, `mad22_cpu_continuation86_result_6296447/`: results of failed, partial and continued MAD22 CPU jobs (job numbers in the names).
- `mad22_technical149_cost_v1/`, `mad22_technical149_cost_result_6297451/`: MAD22 technical cost run and its result (job 6297451).

## /mnt/t7/smad_research (outputs of the 11 Nov research loop; see INDEX section 7)

- `astra-e2-v1/`, `astra-e2-v2/`: Astra E2 CLIP-view probes.
- `astra-core20-v1/`: Astra CLIP core fits (first fit `seed201-C0hi`, probes, rate and header audits in the sibling `astra-core20-*` folders).
- `a37-roi-falsification-v1/`: A37 inner-ROI falsification.
- `diffae-expanded123-v1/`, `diffae-roi102-v1/`: DiffAE expanded generation (123 cases) and inner-ROI analysis (102 cases); tars of runtime assets sit inside the second.
- `gan32-vast-v1/`, `gan32-frozen-v1/`, `gan32-trainplus-v1/`, `gan32-trainplus-union-v1/`, `gan-native-heads-v1/`: GAN32 generation, frozen-head scoring and training-plus shards.
- `vast-gan32-v1-results/`, `vast-gan32-trainplus-*results/`, `vast-gan32-trainplus-shard1-failed-evidence-v1/`: copied results and failure evidence from rented hosts.
- `confirmation64-alignment-v1/`, `confirmation64-diffae-v1/`, `confirmation64-selection-v1/`, `-v2/`: fresh 64-case confirmation attempt (stopped at selection per the README).
- `roi-confirmation-inventory-v1/`, `multigenerator-dro-v1/`: inventory and multi-generator worst-group inputs; from the name.
- `group-dro-v1-inputs.tar`, `renderer-projection-v1-inputs-v2.tar` (and an empty `renderer-projection-v1-inputs.tar`): packed inputs.

## /mnt/t7/wcss_backups (copies pulled from WCSS before cleanup)

- `smadcvpr/`: archive (`local_scratch_w0`), runs (`A12BR`, `A8T`) and cleanup and verification lists dated 7 Nov.
- `demorpher/`: data, eval, outputs, runs, weights and the 7 Nov cleanup lists for the demorphing project (dated 12 Oct).
- `madation_official_upload/`: `madation_official.tar` with its checksum (the official MADation release).
- `PD-staging-retirement-20261110-v1/`: staging retired from the cluster project disk on 10 Nov (directory mode is private).
- `sol-capacity-resolution-20261110-v2/`: capacity resolution evidence, 10 Nov.

## /mnt/t7/smad_next (volatile backup made 11 Nov)

- `volatile_backup_20261111/gan_protocol/`: GAN protocol files.
- `volatile_backup_20261111/mad22_fixed_raw_manifest.json`: fixed raw MAD22 manifest.
- `volatile_backup_20261111/mambamorph-a138-algorithmic/`: copy of the A138 repository (original in `/tmp/opencode`, which does not survive a reboot).
- `volatile_backup_20261111/own-generation-GAN-canonical256-v1/`: canonical 256 px own-GAN generation material; from the name.
- `volatile_backup_20261111/r8_cv/`, `r8_fm/`: two folders of unknown content; not verified.
- `volatile_backup_20261111/README.txt`: note for the backup (not read).

## Not verified

Checkpoint (model weight) locations by experiment are not recorded here beyond these folders: `wcss_backups/smadcvpr/runs`, the `runs` and `models` subfolders inside `smad_heldout/*`, and the A47 `runs`. Which folder holds which network was not checked.
