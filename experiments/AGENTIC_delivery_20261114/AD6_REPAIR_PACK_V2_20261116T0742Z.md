# AD6 repair — pack v2 + resubmit (2026-11-16T07:42Z)

## What happened (chain of diagnostics, all verified from job logs)
1. 08:15-08:17 CET: all three AD6 WCSS arrays (6334803 B / 6334804 L / 6334807 X) allocated H100 nodes and FAILED
   after 3-4 s: `sha256sum: ad5w_wheels39.tar.sha256: No such file or directory` — the packs-dir symlink
   `ad5w_wheels39.tar.sha256 -> ../AD5/packs/...` did not resolve in the job context.
2. Repair A: replaced BOTH wheels symlinks with hardlinks (files exist on the same lustre FS);
   `sha256sum -c ad5w_wheels39.tar.sha256` = OK on lustre.
3. Resubmit 1 (6335977-79): failed again at line 20 — `${AD6_L:?}` — I had exported `L=` instead of `AD6_L=`;
   cancelled (scancel), resubmitted with `AD6_L=...` (6335983-85).
4. 6335984 (X) got 1×H100 twice: s401 AND s402 FAILED at exactly 57 s, ExitCode 1:0, no train output, no
   `logs/keep/` — silent `set -e` death between the python-version print ("3.9.25 2.0.1+cu118") and `printf rows`.
5. Repair B (root cause): reproduced unpack on the login node — `ad6_sb_pack.tar` was BUILT ON GB10 WITH SYMLINKS:
   `manifests/train_Sb.csv -> /mnt/t7/...` (GB10-only path) AND **all 5,535 train/*.png are symlinks to
   /mnt/t7/smad_next/AR1/img/...**. On WCSS no /mnt/t7 → `[ -f $S/data/manifests/train_Sb.csv ]` failed → set -e.
   The 4 B/L resubmits would have failed the same way after the ~47 s env build.

## Pack v2 (registered amendment 2)
- Rebuilt with real file copies (cp -aL; verified 0 symlinks remaining): `/tmp/ad6_sb_real` → `ad6_sb_pack_v2.tar`,
  size 1,918,525,440 B (1.9 GB, uncompressed).
- Hashes INSIDE unchanged (registration preserved):
  - `manifests/train_Sb.csv` sha256 2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a (= prereg PN1 Sb manifest),
  - `train_Sb_6250x256.csv` sha256 5fd26e32fcf0d6f7daebac1d1d66ce649d45e87ffa307f310b418112b59c91b3 (= prereg, 1,600,000 rows + header),
  - 5,535 real png files (same resolved file objects as the GB10 tree; cp -aL preserves content byte-identity by construction —
    verified independently by sha of both CSVs and by remote extraction sha of train_Sb.csv).
- NEW pack-level sha256: c741e676f95a01e6efef75bebf2a823ac3ccba3493af7a3829ac71f0a4209227
  (replaces 2b5b2880 at pack level only; member hashes unchanged).
- Uploaded to WCSS packs `ad6_sb_pack.tar` (52 s stream) + fresh `ad6_sb_pack.tar.sha256`;
  remote sha256sum -c OK; remote extraction of ./manifests/train_Sb.csv sha = 2cf3fda3... = prereg.
- Local backup copy: /tmp/ad6_sb_pack_v2.tar (+ /tmp/ad6_sb_real tree).

## Resubmit jobs (current, AD6_L fixed)
- B = 6336013 (4×H100, nice 40 default), X = 6336014 (1×H100, nice 41, TL 1:00), L = 6336015 (4×H100, nice 42).
- Old/duplicate arrays 6335977-79, 6335983-85 all scancelled (verified not in queue).
- Status 07:42Z: all three PENDING (Resources/Priority). ACCEPT QUEUE per operator; no hold release.
- atrapa: jeżeli X padnie znów w ~57 s — czytamy pełny .out (teraz pack OK, kolejna ewentualna usterka byłaby
  już po stronie kodu SMDD, nie packa). GB10 twin X_s401 nadal działa (redundancja).
