<!-- Code re-check of XF1 revision b2 (3d20916) by the experiment-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. Verdict GO. Lead's decision on its question: fix 1 is accepted — licence (c) requires beating both the logreg and the gbt learner of the arm's own list. -->

**Verdict: GO.** I found nothing that would waste the Athena job or corrupt the read. There are three small fixes to make before registration. They cost no GPU time and need no Athena change.

**1. Pack and nets: ok**
- All hashes match the registration: pack cd57efba, nets 5a0a00be, xf1b_eval.csv 8f07ce77, xf1b_rows.csv 4adcf914. The task folder SHA256SUMS (e3c0599e) checks out, and the sbatch there is the same file as src (1105c787).
- **Read rows:** xf1b_eval.csv has 3,417 gate rows and 1,495 xf1 rows. The 1,495 split into FMHB, WARP and H whole × 299, plus FMHB and WARP face × 299, and match xf1b_rows.csv in ids, order, path, label and klass.
- **Images:** I streamed the tar. All 1,495 images match the row-list sha256 and the pack's SHA256SUMS. All 3,417 gate images are present and match SHA256SUMS. There are no extra eval files.
- **Code and weights:** the 104 entries under code/ and hf/ are identical to revision a.
- **Nets:** 15 networks (PN1_{A,B,Sb}_s403–407, each with meta.json and last_trainable.pt) plus 15 gate references. Each reference is byte-identical by sha256 to `/mnt/t7/smad_next/TT1/results/unpacked_fs/TT1_A100_pn1fs_fs/scores/<net>__gate.npz`. I read only the id arrays: their order equals the manifest's gate order, as float32 with 3,417 rows.
- **Platform caveat (disclosed in F6):** the references came from a rented A100-PCIE. Athena has reproduced them byte for byte for Sb only. A and B may fail the gate, and the job is built to handle that.

**2. sbatch: ok**
- Limits are within plgrid-now: `-c 16`, `--mem=120G`, `gpu:1`, `01:00:00`, one job.
- It is a near copy of the proven NE1 file (same account, memfs, container path, apptainer call). IO runs on memfs and nothing is installed.
- The gate runs before scoring for each network. With pipefail, a gate exit code of 3 goes to the else branch and the network is skipped (lines 41–45). The results tar gets SHA256SUMS plus its own sha256, and the copy uses `.part` then `mv`.
- **Time:** TT1 took about 29 s per network for the gate and about 0.03 s per row for scoring, so roughly 15–20 min in total.
- If rescore crashes (not a gate failure), `set -e` aborts with no tar. That is an infrastructure failure: re-run unchanged.

**3. Reader: matches b2**
- Rows are selected by klass and form, and face-only decides.
- The 64-block bootstrap uses 2,000 shared draws with rng 20261203, and the host bootstrap uses 20261204.
- The Sb − B (primary) and Sb − A (secondary) rules are as registered, in the registered order: "not read" below 4 gated seeds, then all arms' lower bound ≥ 0.95, then X's seed-mean ≥ 0.97, then the gain rule.
- The floor rule and licences (a)–(c) are as registered.
- The adversary file is pinned (86f61826) and asserted with the three committed AUCs, and every floor and learner (including learner_Sb) is printed beside each network.
- The mock ran cleanly in 42 s (gatefail: Sb − B "not read", B reversed).

**4. Deletions: ok.** There is no rmtree, unlink or rm in src/XF1 or tasks_XF1.

**5. Mock: covers everything except the result-tar loading code**
- "ceiling" also exercises licence (c), since shift 6 beats the learners, but the prereg's branch list (line 192ff) does not say so.
- Untested: the result-tar loading code (xf1_read.py:100–109) and an arm with 0 gated networks (line 153). The loading code looks right: keys id/logit, `byte_identical`, and the `XF1_scores/scores/` paths all match rescore.py, xf1_gate.py and the sbatch.
- The mocks randomise logits only. The gate JSON is synthetic, and the rows and adversary sources are real.

**On licence (c)**
- Using each arm's own training-list learner matches the wording "beyond hand-made statistics trained on the same list". The original section 5 bar (the all-cue in-distribution learner) is superseded by b2.
- But the gate needed both learners' upper bounds below 0.90. For the same reason, the bar for (c) should be the larger of logreg and gbt: the network must beat both. Otherwise the learner is chosen by fiat. On the Sb list they differ by only 0.003, but A and B are unknown. This costs nothing and b2 is still a draft.

**Fixes**
1. **Licence (c) bar** (recommended; lead/author decision, but cheap):
   - In prereg.md:176, replace "using gbt (the gate's model)" with "against both its logreg and gbt learners (the gate's rule)".
   - In xf1_read.py:137–143, compute `exceeds_own_learner_face` as the AND of the two checks `ci(boot[(n,"face")] - sboot[(f"learner_{arm}_{m}","face")])[0] > 0` for m in (logreg, gbt), and print both.
   - Re-hash xf1_read.py in src/XF1/SHA256SUMS and prereg.md:190.
2. **Real-path mock** (minor): build a synthetic `XF1_scores.tar` in the scratchpad, with rescore-format npz files (id, float32 logit, seed), gate JSONs and the sha file, for 15 networks with 2 failing. Run the real branch on it once (for example with a `--tar` override). Also note in prereg.md:192–197 that licence (c) is covered by "ceiling".
3. **Registration:** b2 is headed "DRAFT, not binding" (prereg.md:140). Make it binding and commit it before upload, and put that commit hash in the queue file header.

**Question for the authors:** do they accept fix 1 (beat both learners), or keep gbt only as drafted?

Files: `/home/narolski/smad-next/src/XF1/xf1_read.py`, `/home/narolski/smad-next/src/XF1/athena_xf1.sbatch`, `/home/narolski/smad-next/experiments/XF1_ffhq-facemorpher-matched-render/prereg.md`, `/mnt/t7/smad_next/XF1/tasks_XF1/SHA256SUMS`.
