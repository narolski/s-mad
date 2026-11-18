"""Generate the three data figures of the rewritten supplement (figures/supp2_*.pdf, vector) from the same sources as
the tables; every plotted value is registered in printed_values_figures.json for verify_supplement_v2.py.

    python src/supplement_v2/make_figures.py [--out WORKTREE]"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive as D  # noqa: E402
import make_tables as T  # noqa: E402

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/home/narolski/work/smad-cvpr-2027-supp2"
FIG = os.path.join(OUT, "figures")
R = D.Registry()
# Okabe-Ito subset; checked with a colour-vision-deficiency validator; every series also has its own marker and label
COL = {"Sb": "#0072B2", "SelfMAD": "#E69F00", "MADation B/16": "#009E73", "MADation L/14": "#CC79A7",
       "MixFaceNet-MAD": "#56B4E9", "A": "#E69F00", "B": "#009E73"}
MK = {"Sb": "o", "SelfMAD": "s", "MADation B/16": "^", "MADation L/14": "v", "MixFaceNet-MAD": "D", "A": "s", "B": "^"}
INK, MUTED = "#222222", "#777777"
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"], "font.size": 8,
                     "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "xtick.color": INK, "ytick.color": INK,
                     "axes.labelcolor": INK, "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})


def val(spec, d=4):
    return float(R.v("Fig", spec, d))


def fig_slope():
    dets = [("Sb", "Sb", [403, 404, 405, 406, 407]), ("SelfMAD", "SelfMAD-RW", [0]), ("MADation B/16", "MADation-B16-RW", [0]),
            ("MADation L/14", "MADation-L14-RW", [0]), ("MixFaceNet-MAD", "MixFaceNet-MAD-RW", [0])]
    cols = [("OpenCV", ["OpenCV"]), ("Webmorph", ["Webmorph"]), ("MIP-I", ["MIPGAN_I"]), ("MIP-II", ["MIPGAN_II"]),
            ("M4", D.FAMS[1:])]
    fig, ax = plt.subplots(1, 5, figsize=(6.9, 2.0), sharey=False)
    for j, (title, fs) in enumerate(cols):
        a = ax[j]
        for lab, m, seeds in dets:
            y = [val(["mean", [["mean", [["t1eer", m, s, f, form] for f in fs]] for s in seeds]], 2) for form in ("S", "H")]
            a.plot([0, 1], y, color=COL[lab], marker=MK[lab], ms=4.5, lw=1.6 if lab == "Sb" else 1.1,
                   zorder=3 if lab == "Sb" else 2, label=lab)
        a.set_xticks([0, 1], ["S", "H"])
        a.set_xlim(-0.3, 1.3)
        a.set_title(title, fontsize=8, color=INK)
        a.grid(axis="y", color="#e6e6e6", lw=0.5)
        a.set_ylim(bottom=0)
    ax[0].set_ylabel("EER (%), lower is better")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.04), fontsize=7.5)
    fig.tight_layout(rect=(0, 0.1, 1, 1), w_pad=0.6)
    fig.savefig(os.path.join(FIG, "supp2_slope.pdf"))
    plt.close(fig)


def fig_paired():
    fig, ax = plt.subplots(1, 2, figsize=(6.9, 1.55), sharey=True)
    pairs = [("Sb_minus_SpV", "Sb $-$ SpV\n(with splice positives)"), ("BN_minus_BV", "BN $-$ BV\n(without)")]
    for j, (outcome, title) in enumerate((("whole", "Whole-frame morphs, $D$-stratified AUC (primary)"),
                                          ("splice", "Face-spliced morphs, AUC (secondary)"))):
        a = ax[j]
        a.axvline(0, color=MUTED, lw=0.8)
        for i, (pair, lab) in enumerate(pairs):
            yy = 1 - i
            ps = [val(T.batchc_spec(outcome, pair, s)) for s in T.CB_SEEDS]
            mn, lo, hi = (val(T.batchc_spec(outcome, pair, k)) for k in ("mean", "lo", "hi"))
            c = COL["Sb"] if i == 0 else COL["B"]
            a.plot([lo, hi], [yy, yy], color=c, lw=2.2, solid_capstyle="round", alpha=0.45)
            a.scatter(ps, [yy + 0.16] * 5, s=14, color=c, edgecolor="white", lw=0.6, zorder=3, marker=MK["Sb"] if i == 0 else MK["B"])
            a.scatter([mn], [yy], s=40, color=c, marker="D", edgecolor="white", lw=0.8, zorder=4)
        a.set_yticks([1, 0], [p[1] for p in pairs])
        a.set_ylim(-0.5, 1.55)
        a.set_title(title, fontsize=8, color=INK)
        a.set_xlabel("AUC difference (positive favours the first arm)")
        a.grid(axis="x", color="#e6e6e6", lw=0.5)
        a.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(5))
    fig.tight_layout(w_pad=1.2)
    fig.savefig(os.path.join(FIG, "supp2_paired.pdf"))
    plt.close(fig)


def fig_transfer():
    fig, ax = plt.subplots(figsize=(6.9, 2.5))
    rows = [(T.SRC_LAB[f], lambda a, s, f=f: ["tt1flag", f"PN1_{a}_s{s}", f]) for f in D.TT1_FAMS] + \
           [("MEDS-II, all", lambda a, s: ["medsflag", f"PN1_{a}_s{s}"]),
            ("MEDS-II, 240$\\times$240", lambda a, s: T.jp(T.TT1M, "nets", f"PN1_{a}_s{s}", "flag_240px", scale=100))]
    n = len(rows)
    for i, (lab, fn) in enumerate(rows):
        y = n - 1 - i
        for k, a in enumerate(("A", "B", "Sb")):
            xs = [val(fn(a, s), 3) for s in T.SB_SEEDS]
            ax.scatter(xs, [y + (k - 1) * 0.22] * 5, s=18, marker=MK[a], color=COL[a], edgecolor="white", lw=0.5,
                       label=a if i == 0 else None, zorder=3)
    ax.set_yticks(range(n), [r[0] for r in rows][::-1])
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlim(-0.1, 50)
    ax.set_xticks([0, 1, 2, 5, 10, 20, 40], ["0", "1", "2", "5", "10", "20", "40"])
    ax.set_xlabel("Genuine photographs flagged at the own threshold (%, lower is better; one marker per seed)")
    ax.grid(axis="x", color="#e6e6e6", lw=0.5)
    for y in range(n):
        ax.axhline(y - 0.5, color="#f0f0f0", lw=0.5)
    ax.axhline(1.5, color=MUTED, lw=0.6)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=7.5, handletextpad=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "supp2_transfer.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    fig_slope(); fig_paired(); fig_transfer()
    R.dump(os.path.join(os.path.dirname(os.path.abspath(__file__)), "printed_values_figures.json"))
    print(len(R.items), "plotted values registered")
