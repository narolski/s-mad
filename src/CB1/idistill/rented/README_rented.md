# IDistill retrain (CB1) on one rented A100-class machine: prepared, NOT run

Prepared 13 Nov 2026 00:10 CET on the coordinator's request; the author decides the budget at the 09:00 report.
Nothing is rented by the CB1 owner.

- Machine: 1x A100 40/80 GB or H100, >= 16 CPU cores, >= 64 GB RAM, >= 120 GB disk, Docker image with Python 3.10
  and CUDA 11.7+ driver (e.g. `pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime`); internet for PyPI (versions pinned to
  the WCSS wheel house: torch 2.0.1, torchvision 0.15.2, numpy 1.22.4, pandas 1.5.0, scikit-learn 1.1.1,
  opencv-python-headless 4.5.5.64, facenet-pytorch 2.5.2, tensorboard 2.17.1).
- Wall time (estimate; the WCSS smoke 6308827 gives the measured step rate when it runs): crops about 20 min;
  autoencoder 300 epochs x 773 steps (batch 32) at about 20 steps/s on an A100 = about 3.3 h; latents about 10 min;
  three classifier seeds at most 250 epochs each (early stopping usually earlier), about 2-3 h each one after the other
  (or about 3 h in parallel on one GPU with >= 24 cores: DRIVE_PARALLEL=1). Total about 7-12 GPU-hours.
- Cost: at 0.8-1.5 USD/h for an A100: about 6-18 USD; cap proposed 20 USD.
- Upload (one command, lead): `bash upload.sh HOST PORT LEASE` sends idistill_code.tar, idistill_data.tar (7.0 GB),
  smdd_train_cropped.tar (2.4 GB) and their .sha256 to /root/cb1/smad-next/packs/CB1/ and the job script to
  /root/cb1/smad-next/jobs_cb1/.
- Drive: `nohup bash drive.sh HOST PORT LEASE &` runs STAGE=ae, fetches and verifies idistill_ae.tar (AE weights,
  latents, crops, logs), then STAGE=cls for seeds 401, 402, 403, fetching and verifying each result tar to
  /mnt/t7/smad_next/CB1/results_rented/ immediately.
- Keep rule (OWNER_BRIEF "nothing is released while it holds the only copy"): RELEASE is written only after every
  result tar is on /mnt/t7 with a matching sha256 recorded in the experiment folder; the trained weights (AE best,
  three classifiers x three checkpoints) are inside those tars. On any failure the driver copies remote logs and stops
  without RELEASE.
