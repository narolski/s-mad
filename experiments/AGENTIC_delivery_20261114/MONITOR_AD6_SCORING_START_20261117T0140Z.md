# MONITOR — AD6 Hsbr scoring start — 2026-11-17T01:40Z

- GPU context: gb10 twin (redundant mixfacenet_X_sbr_s401) stopped 22:25Z by main — not restarted; GB10 free for AD6 scoring.
- Disk audit: `/home` (on /) had 1.9G free < script DISK_LOW gate (6G). Freed 5.1G of REGENERABLE package caches only:
  pip cache (2.3G), uv cache (1.0G), npm _npx/_logs (1.6G), ms-playwright (0.96G), node-gyp/tectonic/prisma tracker (0.2G).
  NOT touched: HF hub model cache (9.2G), any repo/data/receipt dirs, /tmp/claude-1000, /tmp/opencode (pinned-input scratch),
  selfmad_s405 (failure-diagnosis reference), ad6_stage transfer packs. No -rf outside caches + script's own space policy.
- WCSS pull (fetch_ad6_wcss.sh, flock discipline, one command per connection): 5/5 mixfacenet_X_sbr_s401..405.tar + .sha256
  pulled to ad6_wcss_pull/, sha256 -c OK vs far-side sidecars; independent far-side `sha256sum` cross-check == sidecars for 5/5
  (receipt: ad6_wcss_pull/FAR_SIDE_SHA256_mixfacenet_20261117.txt).
- Tar member layout verified REMOTELY (tar -tf, read-only) BEFORE pull: madation B tar has 1_backbone.pth + 1_header.pth +
  training.log (+job.json/SHA256SUMS/tensorboard/pip_freeze/gpumem); mixfacenet tar has mixfacenet_SMDD.pth — EXACTLY what
  score_ad6_dgx_20261116.sh prep() expects. NO script adaptation needed.
- Filename mapping (pull-stage only, scoring path unchanged): WCSS madation_B_v3sbr_s40N.tar will be renamed to
  madation_B_sbr_s40N.tar after per-name sha256 verification (script prep() greps ^<name>.tar$); sidecar renamed in step.
  WCSS madation_L_v3sbr tars not yet on lustre (H2 lands ~02:30-03:30Z).
- Scoring: launched 01:37Z via score_ad6_dgx_20261116.sh on the 5 mixfacenet names (one process, names sequential).
  mixfacenet_X_sbr_s401 ad6v1 scored 260s; npz ~16.5MB feat + 2.4MB scores; receipts in scores_h_sbr/RECEIPTS_sha256.csv.
- Plan: after X arm completes, pull+score madation B seeds ONE AT A TIME (600MB tar each) keeping /home >= 6G per DISK_LOW gate.
  EER aggregation per AD5 pattern commit c745230 when 20/20 npz; table update + tables: commit at 10/10.
