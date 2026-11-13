"""BB2 amendment 4: copy of freeze_mode.py for the E3 fits (BB2L_* tars in /mnt/t7/smad_next/BB2/results_L, mode file
seed_mode_L.json; the text below is the original docstring with BB2/results and seed_mode.json read accordingly). BB2 amendment 2 (fix 1): freeze the seed mode before any reader runs on real tars.
Allowed when (a) all 15 fit tars are present and verified in /mnt/t7/smad_next/BB2/results, or (b) every missing fit
is listed with --failed (a remote-confirmed failure: no tar after its one rerun), or (c) it is 14 Nov 2026 18:00 CET
or later. Mode = five if all six tars of seeds 406 and 407 are present and verified, else three (bb2_read.seed_mode).
Writes experiments/BB2_second-backbone/seed_mode.json (mode, the tars of the read set with sha256, the fetch log's
sha256 and its last lines, the time and the reason); the owner commits it before any reader runs.
  python3 -I freeze_mode.py [--failed BB2_X_sNNN ...]"""
import argparse
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "PN1"))
sys.path.insert(0, str(HERE))
import bb2l_read as BR  # noqa: E402

RF = pathlib.Path("/mnt/t7/smad_next/BB2/results_L")
CUT = datetime.datetime(2026, 11, 14, 18, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--failed", nargs="*", default=[])
    a = ap.parse_args()
    if BR.MODE_FILE.exists():
        sys.exit("refused: the mode is already frozen")
    allt = [f"BB2L_{arm}_s{s}" for s in BR.SEEDS5 for arm in BR.ARMS]
    ok = {t for t in allt if (RF / f"{t}.tar").exists() and (RF / f"{t}.tar.sha256").exists()
          and BR.F.sha(RF / f"{t}.tar") == (RF / f"{t}.tar.sha256").read_text().split()[0]}
    now = datetime.datetime.now()
    missing = [t for t in allt if t not in ok]
    if not missing:
        reason = "all 15 fits present and verified"
    elif set(missing) <= set(a.failed):
        reason = f"every missing fit is a remote-confirmed failure: {missing}"
    elif now >= CUT:
        reason = f"cut-off 14 Nov 18:00 reached; missing {missing}"
    else:
        sys.exit(f"refused: fits still missing and not confirmed failed ({missing}); before the cut-off")
    seeds, mode = BR.seed_mode(RF)
    read = [f"BB2L_{arm}_s{s}" for s in seeds for arm in BR.ARMS]
    fl = RF / "fetch.log"
    rec = dict(mode=mode, seeds=list(seeds), reason=reason, frozen_at=now.isoformat(timespec="seconds"),
               tars={f"{t}.tar": BR.F.sha(RF / f"{t}.tar") for t in read if t in ok},
               missing_in_read_set=[t for t in read if t not in ok], failed_confirmed=a.failed,
               fetch_log_sha256=BR.F.sha(fl) if fl.exists() else None,
               fetch_log_tail=fl.read_text().splitlines()[-20:] if fl.exists() else None)
    json.dump(rec, open(BR.MODE_FILE, "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("mode", "reason", "frozen_at")}))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
