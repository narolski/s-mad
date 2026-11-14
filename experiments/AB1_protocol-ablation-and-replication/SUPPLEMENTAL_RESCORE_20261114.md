# Supplementary genuine-source and border scoring for the second-engine arm (SbFM)

Execution registration proposal, 14 November 2026. This supplies inputs already required by the approved next-method selection rule, sections 5(c), 5(d) and 12 question 2. The author instructed Codex to proceed on the necessary work after binding version 3. The lead records the actual registration commit and independent pre-run review before submission. Nothing in the approved selection rule or in the existing arm's hypotheses changes.

## Fixed scope

Ten existing last-checkpoint networks, paired at seeds 408–412: the second-engine arm SbFM and the original H100 Sb comparators. No fit, new seed, checkpoint choice, transformation, blur, resize, augmentation, threshold, metric or benchmark read. The task produces development row-ID-keyed scores; statistical interpretation remains held until full reader admission.

The five SbFM tar hashes come from the opaque, SHA256-verified recovery collection receipt at `/mnt/t7/smad_next/recovery_20261114_MAIN/COLLECTION_VERIFIED.json`. The five comparator hashes are the exact hard pins used in the registered DINOv3 wave-2 comparator path. They are fixed in `src/recovery_20261114/sbfm_supplement/config.json`. This author did not open any candidate archive to prepare the job.

One WCSS H100, existing `$HOME/dmenv` software build, eight CPUs, 64 GB RAM and 200 GB local scratch; 2-hour hard limit (at most two H100-hours). Expected under two hours for ten whole-manifest gates plus 320,120 supplementary rows total. The 2-hour estimate is conservative, not a changed training budget. Any partial completion stays explicitly partial; no gate failure is retried with changed precision or batch size.

## Exact gate and scoring path

1. Before extracting any network tar, verify the immutable clean-input receipt SHA256 `9a02d57b1decb4035360992c1f89a777d9d03cc282121ef1ad7ff1f00ae17bd0`, source commit `8d009968d902801c47970ca1cd45c0464cdc8462`, the 44 detection pins, 20 support pins and the privacy-safe support JSON hash. Verify all ten opaque network tar hashes, all package hashes and every unchanged gate/scorer source hash. The result namespace must not already exist.
2. Unpack the pinned FS1 package, AB1 overlay v2 and SbFM overlay v2 into local scratch. Check original FS1 and both overlay content sums, including another original-FS1 check after all additions. Overlays add data/manifests; they must not change fit code or base images. Unpack the original TT1 and MEDS packages unchanged and check internal sums and canonical scoring-manifest hashes.
3. Compare each fit's recorded Python, torch/CUDA, timm, numpy and Pillow versions with the current compute process and require H100. Refuse rather than substitute a changed software build.
4. Run **unchanged** `src/BB2/bb2_gate.py` (`08d430dc6451b10f66754ad7185a3a96d01ea9788aececd033d17dc92e73f168`) on every network. The generic implementation derives the member prefix from the tar basename and takes an unrestricted `--manifest`; it has no DINOv3-specific architecture or arm branch. It rebuilds from `meta.json`, requires the loaded tensor names to equal the exact trainable-key set and missing keys to equal frozen keys, then calls the original `common.ImageItems`/`forward_logit` at the stored resolution, batch 64, full manifest order, TF32 on and no flip. It compares the original manifest SHA, ID order and every float32 logit by `np.array_equal`.
5. For SbFM, the full fit manifest is `ab1x_eval.csv` (24,859 rows); for AB1 Sb, `ab1_eval.csv` (21,277 rows). Both are present with their original images in the merged gate root. A gate passes only with zero differing values and zero maximum difference, the expected GPU, exact row count and model tar hash. A failed or missing gate prevents all supplementary scoring of that network. Preserve every refusal and exit the job nonzero if any network/family is refused.
6. After the first successful gate, perform the unchanged real scorer CLI on eight existing TT1 rows as a plumbing diagnostic. It trains no model, changes no image and adds no gate threshold. Its output remains scratch-only; only the technical row-count/finite check is retained. Then score each admitted network on TT1 family `tt1` (30,994 rows) and MEDS family `meds` (1,018 rows), using unchanged `src/PN1/rescore.py` through unchanged `src/TT1/rescore_tf32.py`, batch 64 and TF32 on. The primary TT1 seven-family lists and MEDS primary/person grouping are fixed by the committed support metadata.
7. Each supplementary output must have the exact expected manifest-family ID order, expected seed, one finite logit per row and the exact row count. Validation prints no score values. The TT1 output includes all 1,582 specific development camera-border IDs required by version 3, so both arms' border rows come through this same gated scoring path. Do not replace those IDs with an aggregate over all TT1 border references.

The generic gate is source-equivalent to the already registered full-manifest identity path in DINOv3 wave 2. Its actual success for each SbFM network is established only by the new compute-time gate, not inferred from the old DINOv3 smoke. No model fit or source score was inspected by the agent to assert that success in advance.

## Files and admission

Adapter directory: `src/recovery_20261114/sbfm_supplement/`. It contains `config.json`, `run_supplement.py`, `validate_family.py`, and `ab1fm_supplement.sbatch`. The launcher hard-pins the configuration and both helpers. The configuration hard-pins the original package/gate/scorer files, model tars and pre-read receipt. Local validation: Python compilation, `bash -n`, configuration/source-pin consistency, and synthetic validator checks; the eight-real-row CLI diagnostic runs inside the allocated job before full scoring.

Stage that directory under `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AB1FMSUPP/`, adding the immutable root-owned `pre_read_receipt.json` and the exact privacy-safe `support_v3.json`. Verify every staged hash before submission. Root alone submits after the dated registration/review commit, duplicate-receipt check and input presence checks:

```bash
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AB1FMSUPP
/opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR ab1fm_supplement.sbatch
```

Output is `results/AB1FMSUPP/AB1FMSUPP_20261114.tar` plus SHA256. Never overwrite an existing result or partial file. Gate working files, fit-time scores, weights and input manifests remain outside the output directory. No MEDS image or original subject identifier is exported; MEDS scores are keyed only by the original scoring pack's own opaque row IDs, as in the existing wave-2 path. Paper/report readers emit aggregate MEDS results only.

After each completed family and each completed or refused model, the job creates a separately named, SHA256-verified durable diagnostic partial under `results/AB1FMSUPP/diagnostic_partials/AB1FMSUPP_20261114_job<jobid>/`. Each has an explicit `PARTIAL_STATUS.json` with `partial: true` and `final_admission: false`; it never overwrites an earlier checkpoint or a final output. A timeout or early failure therefore retains prior completed work despite local-scratch cleanup. These partials are preservation receipts only and cannot satisfy final admission or be substituted for missing seeds/families. The final archive excludes the scratch partial-status file.

Admission after completion requires scheduler COMPLETED/exit zero, all ten exact gates, twenty finite/complete family outputs, the successful scratch-only eight-row plumbing check, and a durable archive with matching SHA256. Failure or missing families remain failures/partial; no silent seed exclusion. Collection and technical gate inspection do not constitute selection or a benchmark result. Full selection reader, own registration guards and separate eligibility review still govern interpretation.
