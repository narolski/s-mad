"""Print the standing adversary's floors beside an arm's statistic (lead's instruction 13 Nov, after the floors were
pinned at 35f25a7): check.exceeds on the pinned files for the all-cue ADV floor ("all") and the non-F27/non-BLEND floor
("nuisance"), plus the floor's within-BD1-D-quintile values from the floor json (or the *_withinD.json file).
Printed only; the arm's own registered rule is unchanged.
  from adv_beside import adv_print; adv_print("ri_S4_vs_S3", {row_id: score})"""
import json
import pathlib
import sys

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import check  # noqa: E402

FDIR = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors")


def adv_print(contrast, scores):
    out = dict(contrast=contrast)
    for fl in ("all", "nuisance"):
        try:
            out[fl] = check.exceeds(contrast, scores, floor=fl)
        except AssertionError as ex:
            out[fl] = dict(error=str(ex))
    rep = json.loads((FDIR / f"{contrast}.json").read_text())
    if "within_D_quintiles" in rep:
        out["floor_within_D"] = rep["within_D_quintiles"]
    w = FDIR / f"{contrast}_withinD.json"
    if w.exists():
        out["floor_within_D_file"] = json.loads(w.read_text())
    return out
