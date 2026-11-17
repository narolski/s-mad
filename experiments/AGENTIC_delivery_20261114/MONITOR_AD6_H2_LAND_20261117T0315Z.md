# MONITOR — H2 (madation_L_v3sbr) tars landed; L scoring started — 2026-11-17T03:15Z

- B/16 + X arms COMPLETE earlier: 20/20 npz receipted (missing_ids 0), aggregate committed 3a1e72f,
  spot-check FRLL/amsl B s401 v1 recomputed 13.73 == aggregate 13.73 (final_metrics.eer, same pins).
- H2: 5/5 madation_L_v3sbr_s401..405.tar (+sidecars) on lustre results dir (mtimes 02:33-02:47Z WCSS side,
  1,711,595,520 bytes each). ViT-L/14 -> tar ~1.7G: pulled via plain `cat` streaming (NOT tar-stream; S405
  receipt warning at this size class), flock /tmp/opencode/wcss-client.lock discipline, one command per connection.
- s401: local sha256 == sidecar == far-side `sha256sum` (67081a96ff38c0520fcb49e0addb9364f0dca466077e2767ab45924918f76327).
  Sidecars for s402..405 captured. Renamed to script names madation_L_sbr_s40N.tar after verification (pull-stage
  mapping only; scoring path unchanged).
- L scoring s401 running (as madation_vitl14, GB10, one at a time); /home 8.1G free during L run (>= 6G DISK_LOW gate).
  Per-seed: pull ~5min + extract/convert + 2 scoring versions; L slower than B (~0.5-1h/seed expected).
- On L 5/5: aggregate re-run (appends L block to cohort table + dated md), tables: commit, report per-seed EER to main.
