Reviewer: experiment-reviewer (Opus), 13 Nov 2026, read-only. Pre-run check of the TT1 MEDS extension (prereg_meds_block.md at 4ca7755). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089). Fixes were registered in f5389a3.

**Verdict: GO WITH FIXES.** Fixes F1 and F2 should go in before `start`. Neither costs any GPU time.

I worked read-only and opened no MEDS image or sealed file. The registered sha256 prefixes match the files at HEAD 4ca7755: meds_build 63be4997, build_meds_pack 9d487eb7, drive 871c0aa8, remote 83a47fd8, reader de62a0a6, rescore 6f6eede7, meds_score.csv 9093d5d5 (1,018 rows + header), manifest 3698bcb4, packs 2109f742 / 3fb917b2 / b5c4dd6e. The counts add up: 712 − 500 − 49 = 163 MEDS-I, plus 855 MEDS-II = 1,018. SE1_DONE_411 does not exist yet. Staging has started; only `df` output is logged so far (tt1m_stage.out).

## Findings

**F1 (major): the driver never checks that the GPU is idle.** `start` only tests for the SE1_DONE_411 file (drive_tt1_m.sh:28). The SE1 chain accepts seed 412 (src/SE1/rented/chain_se1.sh:36), and 411-412 were waiting on the author's budget word. If 412 is approved on se1d, TT1-M would share the owner's GPU, which breaks "no GPU use before" and the one-owner-per-GPU rule. Fix: add this to remote_tt1_m.sh right after line 26:
```
[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] || abort "GPU busy (another owner)"
```
In the driver, also refuse to start if a later `SE1_DONE_412`/chain log shows a running seed.

**F2 (major): registration gaps.**
- gate_check_m.py has no sha256 in prereg_meds_block.md §2, although it decides the gate. Its hash is `1a62c58b…`. Fix: add "`gate_check_m.py` (`1a62c58b…`)" to §2's Scripts line.
- The gate covers batch shapes of 64 and a last batch of 25 (3,417 = 53×64 + 25). The MEDS last batch is 58 rows (1,018 = 15×64 + 58), a shape the gate never tested. result.md:27 shows that batch composition alone has already changed bits on another platform (tt1a). Fix: add to §2 "The gate certifies the platform on batch 64; the final MEDS batch (58 rows) has no cross-host reference; MEDS scores have no pn1fs counterpart."
- §5 says the DGX test output was "deleted". That conflicts with the never-delete rule. Disclose it as a deviation.

**F3 (minor): the deduplication count wording may be wrong.**
- In meds_build.py:61-63, MEDS-I files that duplicate each other also land in `I_in_II_by_content`. So "500 of 712 are byte-identical to MEDS-II" may overstate the overlap.
- Persons are merged across MEDS-I and MEDS-II as `meds:S<id>` (line 85). That is only right if the two releases number subjects the same way.
- Within MEDS-II the order of the frontal test and the `seen` set does not matter, because `II_dup_content` = 0.
- Fix: a CPU check on hashes and filenames only (no pixels). For the 500 pairs, confirm the subject ids in the MEDS-I and MEDS-II filenames are equal, and count the MEDS-I duplicates separately. Correct the wording if needed.

**F4 (minor): the version asserts are weaker than the recorded stack.**
- remote:33 asserts only torch 2.2.1, timm, numpy and PIL. CUDA, cuDNN and the TF32 flags are recorded (line 37) but not asserted.
- The venv cannot change torch or cuDNN: `-c constraints.txt` pins torch and torchvision to the image versions, and `--system-site-packages` reuses them. The venv also stays in /workspace/tt1m and leaves the SE1 environment alone. The byte-identity gate is the binding check in any case.
- Cheap hardening: assert `torch.version.cuda=='12.1' and torch.backends.cudnn.version()==8902`. These are pn1fs's values (result.md:242). The image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` (lease.json) should match.

**F5 (minor): the reader has no input checks.** tt1_read_meds.py:52-55 reads the manifest and `T.OUT/tt1_score.csv` without checking hashes or ids. Fix: assert the manifest sha `3698bcb4…` and the score list sha `c0055b51…`. Assert that each `__meds.npz` id list equals the manifest ids in order (1,018) and each gate npz has 3,417 rows.
- Otherwise the reader matches the registration. The own rule is logit > 0, as in tt1_read.py:149. The bootstrap is by person, uses `default_rng(20261125)` with 2,000 draws, and clips the lower bound at 0. The pairs are paired, because the same Wm is used for every network. The 4-of-5 rule and "not available" handling are implemented. TT-M2 is one-sided P(MEDS > R_cam), consistent with TT1's displacement read. Sp is printed only.
- The mock uses `hash(n)`, so mock runs are not reproducible. Cosmetic only.

**F6 (minor): status after a "neither" outcome is undefined.** TT-M1 says when a prediction is falsified, but not what happens when an arm comes out "neither" or "mixed". Fix: add to §4 "'neither'/'mixed' = prediction not confirmed, not falsified."
- The predictions are honest given the known FFHQ flags. For B at seeds 403-407 the FFHQ flags are 0.052, 0.108, 0.061, 0.038, 0.025 (result.md:383). So the B "transfers" prediction is a real risk: s404 alone would miss the bar. Nothing in the batch picks an arm, seed or threshold.

**F7 (minor, author): MEDS images stay on the rented host.** The PNGs and packs remain on se1d (/workspace/tt1m/packs, work/tt1m) after the run. The author has allowed data on rented machines. Still, NIST terms call for removal before the instance goes back to Vast. That needs the author's or lead's word, since the never-delete rule applies. No image goes into the repository: git holds only ids, counts, the mock JSON and code, and the result tar holds scores, logs and gpu.txt.

**Driver: ok.**
- It never writes RELEASE, and it writes TT1M_DONE only after two verified copies.
- Uploads are one rsync stream at a time.
- The pull loop runs 60 × 2 min, which fits about 0.3 GPU-hours, and the lease deadline is 19:12 CET.
- Minor: if `start` fails to see TT1M_STARTED after the remote job has launched, a retry could start a second instance. Fix: before launching, check `pgrep -f remote_tt1_m.sh` on the remote.

## Improvements (zero GPU)
1. F1's GPU-idle guard. Highest value; does not need a registration change.
2. F3's id-consistency check. CPU only; a wording correction can go in before scoring.
3. F2, F5 and F6 as a short amendment commit before `start`.

## Questions for the authors
- Should the MEDS packs and frames be removed from se1d before it is released (NIST terms against the never-delete rule)?
- If seed 412 is approved, does it run on se1d before or after TT1-M?
