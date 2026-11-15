<!-- Pre-run check of the shared test battery v1.0.0-rc1 (761a3c7, 317adba, 364f624) by the experiment-reviewer (Opus), ordered by the lead; hand-back saved verbatim by the lead, 13 Nov 2026. Lead's answers: (1) /mnt/t7/smad_heldout/ffhq_morphs is development data (author ruling 12 Nov: FFHQ is development-only), despite the folder name; (2) node rule: byte identity, or else max |Δlogit| ≤ 1e-4 with 0 own-rule flips, labelled tolerance-gated and never pooled with byte-gated records, fixed before the smoke is read; (3) arms trained on FFHQ or new sources may use battery v1 only with the printed in-source note until the person/source table exists. -->

**Pre-run check: shared test battery v1.0.0-rc1** (smad-next, branch sprint-plan-v2, commits 761a3c7, 317adba, 364f624)

## 1. Verdict: GO WITH FIXES. Do not release yet.

The core holds up:
- The scorer copies the `pn1_score.py` loop: `ImageItems` at the network's resolution, batch 64, manifest order, eval mode, no autocast, TF32 set explicitly.
- All 12 reader pins and 2 scorer pins match the files on disk. I checked this.
- The regression test is meaningful. It recomputes every block from stored logits and compares every leaf of the reviewed JSON by `==`. Missing keys count as mismatches (`regress.py:200-232`).
- The gate refuses cleanly. On failure, `gate.json` and a `battery.json` with no logits and no "rows" are written. The reader and `--stats-only` both refuse such outputs (`run.py:146,209-214`; `read.py:37-42`).
- Rows 3, 11, 15 and 16 print an explicit "not measured" reason (`rows.py:21,63,79,81`). In `read_stored_v1.txt`, every empty statistic has a stated reason; none is silently blank.

Five things must happen before the lead declares a release: fixes F1-F6 below, the H100 smoke passed on a node other than r18-8, a new code tar built from the release commit, and the node-tolerance rule decided in advance.

## 2. Findings (most severe first)

**F1 (major): numbers are not pinned to battery code.** `battery.json` records `VERSION="1.0.0-rc1"` and the reader files. `legacy.loaded_files()` deliberately leaves out `src/battery/` (`legacy.py:82`). So a later edit to `stats.py` or `rows.py` changes numbers under the same label. This has already happened once: the smoke tar `battery_code_v1rc1.tar` (8a86676d) has a different `read.py` from HEAD (changed in 317adba).
- Fix, in `run.py` where `rec` is built:
  ```python
  BD = pathlib.Path(__file__).resolve().parent
  rec["battery_code"] = {p.name: sha(p) for p in sorted(BD.glob("*.py"))}
  rec["battery_code_sha256"] = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in rec["battery_code"].items()).encode()).hexdigest()
  ```
- Record the same hash again as `stats_code_sha256` in `--stats-only`.
- In `read.py`, print the hash in every arm header, and refuse to pool an arm whose records carry more than one hash.
- Rule: any change to battery code means a new VERSION and a rerun of the regression test.

**F2 (major): the TF32 trap, plus a wrong label.**
- The battery scores TT1 and MEDS with TF32 on (`run.py:158`). The audit table's TT1/MEDS cells and the stored TT1/MEDS records were made by `rescore.py` with TF32 off (`stored.py:152-154`). The difference is up to 0.035 logit on camera rows, at the decision boundary (`PLATFORM_PINS...md:35`). On top of that, new arms will be on H100 while those old cells are on A100: two changes at once.
- `block_tt1` writes `tf32_split_R_cam` and `tau_cam_label = "...applied to TF32-off logits"` (`stats.py:388-392`). In a battery run both sides are TF32 on, so that label is false.
- Fix: keep TF32 on everywhere (it matches the fit-job thresholds). After `stats.all_blocks` in `run.compute_stats`, add:
  ```python
  t = blocks.get("TT1", {})
  if "tf32_split_R_cam" in t:
      t["tf32_split_R_cam"]["battery_note"] = "both TF32 on, same job: batch-composition difference only, not TF32"
      t["tau_cam_label"] = "saturated band; this run's TF32-on dev scores applied to its TF32-on TT1 logits (printed only)"
  blocks["scoring"] = dict(tf32="on/on", note="TT1/MEDS not comparable with SA1 TT1/MEDS cells or stored TT1/MEDS records (TF32 off)")
  ```
- Leave `stats.py` unchanged, so the regression test still holds.
- In `read.py`, whenever stored and battery records appear in one print, put a NOTE above rows 4, 5, 10, 17 and 19.
- Rule for release: a new arm's TT1/MEDS numbers are compared only with controls the battery scored on the same platform (see Improvement 2).

**F3 (major): the gate checks the platform, not the network being scored.**
- The byte-identity gate on a reference network is a sound check of the stack: GPU, driver, kernels, torch, TF32, code, base weights, decoder. But it covers a different network only if that network has the same layer shapes.
- Nothing checks this. `meta["res"]` and the LoRA settings of the new network are never compared with the reference's.
- The fit-job load path (full `last.pt`, `backbones.py:422-427`) is not exercised. Both references and both smoke networks load `last_trainable.pt`.
- Fix, before the gate (load the new network's meta first):
  ```python
  KEYS = ("arch","res","ft","lora_r","lora_targets","lora_alpha","lora_rs","lora_train_norms")   # not arch_extra: it holds a job path
  nm = json.load(open(pathlib.Path(a.ckpt) / "meta.json"))
  if nm.get("seed") != a.seed: die(4, f"BATTERY: --seed {a.seed} != meta seed {nm.get('seed')}")
  d = {k: (rmeta.get(k), nm.get(k)) for k in KEYS if rmeta.get(k) != nm.get(k)}
  if d and not test: die(5, f"BATTERY: inference config differs from the gate reference {d}; the gate does not cover it")
  ```
- Add `--expect-eval NPZ` (the same job's `pn1_score.py` `scores_eval.npz`). Require the battery's dev logits to equal it byte for byte on every stored id, and require at least 19,797 such ids.
  - On a mismatch: rename `logits_dev.npz` to `*.bak-netcheck`, write the status, exit 6.
  - This gives the per-network gate that `PLATFORM_PINS` item 13 asks for, at no GPU cost.

**F4 (major): node-to-node identity is unknown, and there is no rule yet.**
- The H100 key is `"NVIDIA H100|torch 2.11.0+cu128|tf32 1/1"`, but its stored logits come only from r18-8 (job 6311579). The key does not include the driver (it is recorded, not keyed).
- If other nodes differ, every fit job's battery step refuses. That fails safe but produces no numbers.
- Fix:
  - Write the fallback rule into DESIGN.md now, before the smoke result is fetched. For example: "byte identity, or else max |Δlogit| ≤ 1e-4 with 0 own-rule flips, labelled tolerance-gated and never pooled with byte-gated records".
  - If 6316361 ran on r18-8, run a second smoke with `--exclude=r18-8`.

**F5 (major): the deny-list checks the path string, not where symlinks point.**
- `guard.reason` and the audit hook check the string passed to open (`guard.py:35-53,83-93`). They never call `realpath`.
- Most set images on the DGX are symlinks: 25,335 links under the dev data root, 34,412 under TT1, 1,018 under MEDS, 11,042 under GD.
- I resolved all 67,748 rows and the 4 manifests: none hits the deny-list today. But a future set, or a symlink named `valx_a.csv`, would get through. The allow check runs on the basename before anything is resolved.
- Fix: rename the current body to `_reason_str(s)` (allow check included), then:
  ```python
  def reason(p):
      if isinstance(p, int): return None
      s = os.fspath(p); s = s.decode(errors="replace") if isinstance(s, bytes) else s
      if not s: return None
      r = _reason_str(s.lower())
      if r: return r
      try: rp = os.path.realpath(s)
      except (OSError, ValueError): return None
      if rp != s:
          r = _reason_str(rp.lower())
          if r: return f"resolved {rp!r}: {r}"
      return None
  ```
  - `realpath` raises no "open" audit event, so the hook cannot recurse.
- Add a symlink case to `self_test` (a temporary link `ok.png` pointing into `/x/FRLL/` must be denied).
- Add `"gtest"` to `DENY_TOKENS`.
- Narrow `_is_library` to the `sys.prefix` roots only. A bare `/site-packages/` substring currently exempts any path.

**F6 (major): the end-to-end statistics path has never been run on battery-format output.**
- The regression test calls the `block_*` functions directly.
- `compute_stats` and `all_blocks` (the MEDS-plus-TT1-gate merge at `run.py:95-98`, `info=None`, the fresh random stream, `last_trainable` as `head_floor`) and `rows.extract` have never run on real output.
- The test at `test8_cpu` skipped statistics, and the smoke runs with `--stats no`. AB1 networks have no TT1 or MEDS logits, so the smoke cannot check those blocks either.
- Fix (CPU only, about 1 h):
  - Build battery-format output folders from stored logits: AB1_Sb_s408 (dev, train, `last_trainable`) and PN1_Sb_s403 (TT1 and MEDS from the TT1 tars, `scores_eval` from PN1).
  - Run `compute_stats` on them and compare `rows` with `/mnt/t7/smad_next/BATTERY/stored/*`.
  - In the same check, assert that every `rows.py` path resolves to a non-None value. `rows.get` returns None silently on a typo.

**F7 (major, reporting): no in-source label or cross-arm platform note.**
- The reader flags mixed platforms only within an arm (`read.py:99`).
- It cannot tell whether "FFHQ genuine" rows are unseen for an arm trained on FFHQ (`MISSING_DATA.md` row 3).
- Fix:
  - Record the sha256 of the training manifest. When it is not one of the registered FS1/AB1 manifests, print "training sources not checked against battery sets: rows 1, 4, 13, 14 may be in-source".
  - Print a NOTE when the arms in one print have different platform keys.
  - Add `--expect-seeds`. Refuse on a missing seed or a duplicate (arm, seed) pair (this guards against seed picking).

**F8 (minor):**
- `--test-gate-key` with no `--test-limit` scores empty sets, because of `[:0]` at `run.py:224`.
- The base-weight check is skipped when `--hf-home` is not given or the file is missing (`backbones.py:400-404`). Make it mandatory.
- Set `torch.backends.cudnn.benchmark = False` explicitly (`PLATFORM_PINS` item 10).
- `--test-limit` runs write ungated `logits_*.npz`. Prefix those files with `TEST_`.
- The A100 path does not verify image content: `sets.load` only checks that files exist. Run `sha256sum -c` on the packs there, as the sbatch does on WCSS.

**WCSS (item 5): OK for the smoke.**
- Present: `--extra=FORCE_RM_TMPDIR`, 8 CPUs and 64 GB, all IO in `$TMPDIR`, a refusal to work on Lustre, `~/dmenv` only run (nothing installed), copies verified by sha256.
- Missing: the in-fit-job template. It must run in a fresh `--out` (outputs are never overwritten) and fail soft, so the fit tar still comes back:
  ```bash
  ( cd "$W/code/src" && $PY -m battery.run ... --expect-eval "$RES/scores_eval.npz" --stats no ) > "$RES/battery.log" 2>&1 || echo "BATTERY rc $?" >> "$RES/battery.log"
  ```

**Data safety (item 3):**
- No MEDS identifier reaches the outputs. The manifest `host` column (`meds:S###`) is read but only counts are written, and logit ids are battery ids (`meds_#####`).
- `prep_eval.py` and `prep_gtest.py` are neither imported nor edited.

## 3. Improvements (by value per GPU-hour)

1. F6 end-to-end CPU check: 0 GPU-hours, about 1 CPU-hour. Allowed now.
2. Battery-score the AB1 A, B and Sb networks, seeds 408-412 (15 networks, `last_trainable` already on Lustre) on H100: about 2-3 GPU-hours. This gives same-platform TF32-on comparators for TT1, MEDS and GD, and dev-versus-stored byte checks for 15 networks across whatever nodes they land on. That answers F4 with data. Development data only; needs the lead's approval and must follow the "BATTERY never ahead of fits" ordering.
3. A second smoke excluding r18-8, if needed: about 0.5 GPU-hours. Lead approval.
4. An A100 PCIe smoke before any A100 use: rental cost. Author or lead decision. Until it is done, the A100 key is unreleased.

## 4. Questions for the authors

1. `/mnt/t7/smad_heldout/ffhq_morphs/eval` supplies 8,000 dev, 3,000 TT1 and 9,000 GD rows. Please confirm it is designated development data, since "heldout" is in the path.
2. Which fallback rule applies if H100 nodes are not byte-identical (F4)? It must be fixed before 6316361 is read.
3. Will arms trained on FFHQ or new sources (SbM3, GX1) use battery v1 before the person/source table in `MISSING_DATA.md` exists?

Files: `/home/narolski/smad-next/src/battery/{run,gate,guard,sets,backbones,stats,rows,read,regress,stored,smoke_check}.py`, `/home/narolski/smad-next/src/battery/wcss/battery_smoke.sbatch`, `/home/narolski/smad-next/experiments/BATTERY_shared-test-battery/`.
