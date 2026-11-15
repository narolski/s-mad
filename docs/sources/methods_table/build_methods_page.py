"""Build methods_page.html from the two final markdown files (read-only inputs).

Numbers come only from methods_table_final.md and shortcut_per_method_final.md;
the hand-written section text below repeats their numbers verbatim.
"""
import re
import sys
from pathlib import Path

import markdown

D = Path(__file__).resolve().parent
TABLE_MD = (D / "methods_table_final.md").read_text(encoding="utf-8")
NOTE_MD = (D / "shortcut_per_method_final.md").read_text(encoding="utf-8")
FIND = (D.parent / "findings.html").read_text(encoding="utf-8")
OUT = D / "methods_page.html"

LIST_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s")


def fix_lazy(md: str) -> str:
    """Put a blank line before a list item that follows an indented paragraph line,
    so Python-Markdown does not swallow it as lazy continuation."""
    out = []
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        if i and LIST_RE.match(ln):
            prev = lines[i - 1]
            if prev.strip() and not LIST_RE.match(prev) and not prev.lstrip().startswith("|"):
                out.append("")
        out.append(ln)
    return "\n".join(out)


def dbl(md: str) -> str:
    """The sources nest lists by 2 spaces; Python-Markdown wants 4."""
    return "\n".join(re.sub(r"^( +)", lambda m: " " * (2 * len(m.group(1))), ln) for ln in md.split("\n"))


def md(text: str) -> str:
    return markdown.markdown(dbl(fix_lazy(text)), extensions=["tables", "sane_lists"])


VERDICT = [
    ("partly holds", "v-part"),
    ("does not hold", "v-no"),
    ("not shown", "v-ns"),
    ("holds", "v-yes"),
]


def post_table(html: str, cls: str, ncol: int) -> str:
    html = html.replace("<table>", f'<div class="tw"><table class="{cls}">').replace("</table>", "</table></div>")
    # group rows: bold label in first cell, all other cells empty
    html = re.sub(
        r"<tr>\s*<td><strong>([^<]+)</strong></td>(?:\s*<td></td>)+\s*</tr>",
        lambda m: f'<tr class="grp"><td colspan="{ncol}">{m.group(1)}</td></tr>',
        html,
    )
    return html


def chips(html: str) -> str:
    for word, c in VERDICT:
        html = html.replace(f"<strong>{word}</strong>", f'<span class="chip {c}">{word}</span>')
    return html


def section(text: str, start: str, end: str | None) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start)) if end else len(text)
    return text[i:j]


def table_block(text: str, header_start: str) -> str:
    i = text.index(header_start)
    lines = []
    for ln in text[i:].split("\n"):
        if not ln.startswith("|"):
            break
        lines.append(ln)
    return "\n".join(lines)


# ---------------------------------------------------------------- pieces from the files
cmp_table = table_block(TABLE_MD, "| # | Method (networks) | Regular (landmark) morphs")
floor_table = table_block(TABLE_MD, "| Control | Floors (AUC) | Rule |")
count_table = table_block(TABLE_MD, "| Morph type | holds | partly holds | does not hold |")
sc_table = table_block(NOTE_MD, "| # | Method (networks) | Shortcut test outcome")

note_s1 = section(NOTE_MD, "## 1. What the registered bar requires", "## 2. Table")
bar_part = section(note_s1, "The program's registered bar", "**Even the top grade would not")
doubt_part = section(note_s1, "**Even the top grade would not", "**Three statements")
three_part = section(note_s1, "**Three statements", None)
note_key = section(NOTE_MD, "**Key**", "| # | Method (networks)")
note_notes = section(NOTE_MD, "**Notes to the table**", "## 3. Method by method")
note_s3 = section(NOTE_MD, "## 3. Method by method", "## 4. What would strengthen")
note_s4 = section(NOTE_MD, "## 4. What would strengthen", "## 5. Flags")
note_flags = section(NOTE_MD, "## 5. Flags", None)
note_status = section(NOTE_MD, "**A42 amendment 1 and A43: status**", "## 1. What the registered bar")
tbl_notshow = section(TABLE_MD, "## 4. What this does not show", "## 5. Flags for the author")
tbl_flags = section(TABLE_MD, "## 5. Flags for the author", "## 6. Sources")
tbl_sources = section(TABLE_MD, "## 6. Sources", None)
note_sources = section(NOTE_MD, "**Sources**", "**Scope**")


def drop_heading(s: str) -> str:
    return s.split("\n", 1)[1] if s.startswith("#") else s


# per-method cards from note §3
cards = []
across = ""
body3 = drop_heading(note_s3).strip()
parts = re.split(r"^\*\*(\d+)\. ([^*]+?)\*\*\s*$", body3, flags=re.M)
# parts: [pre, num, name, body, num, name, body, ...]
for k in range(1, len(parts), 3):
    num, name, body = parts[k], parts[k + 1].rstrip("."), parts[k + 2]
    if "**Across rows.**" in body:
        body, across = body.split("**Across rows.**", 1)
    cards.append((num, name, body.strip()))

# ---------------------------------------------------------------- hand-written sections
INTRO = """You asked two things. First, how the competing detectors do on regular (landmark), GAN and diffusion morphs once the benchmarks' construction shortcuts are taken away. Second, for each method, which shortcut was found, and what it would take to show it beyond doubt. This page joins the two answers. Section 2 is the comparison table; section 3 is the shortcut-per-method table; section 4 says what is still missing."""

SCOPE = """- **One network per release.** The official releases are the authors' weights, one network each. Their claims are about those checkpoints, not the SelfMAD or MADation methods.
- **Our frames.** Releases are scored on our 512-px eye-aligned frames unless a row says otherwise. Only the SelfMAD release was also scored with its own crop on the raw files.
- **Recipes are our re-implementations**, trained on SMDD only; most did not reproduce the published numbers.
- **MADMamba is sealed** and not on this page ("MADMamba not evaluated on H3 (sealed)"). No W3, E10 or FST number is used, and no `fst*` file, `manifests/valx.csv` or `A12SP` path was opened.
- **Wording awaits the author's sign-off** (Sun 8 Nov 12:00), which can only drop or weaken it."""

S1 = """**The problem.** A morph detector has to tell morphs (one face image built from two people) from genuine photos of one person. On the standard benchmarks the two classes were also made in different ways:

- The genuine photos are large, high-quality camera JPEG files.
- The morphs are files of other sizes and formats. In most families their faces are also smaller. The exceptions are MAD22 OpenCV and Webmorph and FRLL StyleGAN, where the face sizes already match.
- Several landmark families also carry black alignment borders. Border fraction alone separates several evaluation families almost perfectly (AUC 0.99–1.00; E07 README).
- GAN and diffusion morphs are generator output, while the genuine photos come from a camera.
- **Claim B.** In ten registered cells (the seven FRLL diffusion families and MAD22 MIPGAN-I, MIPGAN-II and FaceMorpher), one documented file attribute alone separates morphs from genuine photos: "Morph and bona fide files differ in documented construction attributes that alone separate the classes (O = 1.000 per decision cell)."

FRLL is the Face Research Lab London set; MAD22 is the SYN-MAD 2022 benchmark. The networks never see file headers. They see decoded pixels, so file attributes matter only through what they leave in the pixels.

So a detector can score well by noticing how the file or picture was made, without noticing that two identities were blended. This page calls such a difference a **construction difference**. The word **shortcut** is kept for A41's registered definition, which so far applies to C1 only. Under it, three things must all hold:

1. A property separates the classes.
2. The property can be put into genuine photos without morphing.
3. A control that removes it removes at least half of the separation.

No control removes every difference: E7 leaves the borders, and H1 leaves file size. To see what a detector does without a given difference, we either **change the genuine side** so that it shares one construction property with the morphs (face size in E7, the generator family in X3), or **build a new set** in which both classes are made the same way and only the number of identities differs (H1, H2, H3, H4b). Then we score the same networks again."""

S1_NUMBERS = """- **Equal error rate (EER, %)** is thresholded: the error rate where missed morphs and false alarms are equally frequent. 0 is perfect and 50 is chance. Above 50 means the detector rates the genuine images as more morph-like than the morphs ("inverted"). The threshold is re-chosen for each comparison, so EER does not show how a deployed detector behaves; the flag rates at a fixed threshold do.
- **Area under the curve (AUC)** is threshold-free: the chance that a random morph scores above a random comparison image. 0.5 is chance; below 0.5 means the comparison images look more morph-like than the morphs.
- **Floors.** Some controls have a floor: the AUC a simple statistic (file size, eye position, or a combination) reaches on the same comparison. A detector shows something beyond that statistic only if it clearly beats the floor."""

S1_TESTS_REG = """- **Shrunk genuine photos (E7).** Each genuine photo is shrunk (area averaging) to the family's median morph face size before the same alignment: ~1.0x for MAD22 OpenCV and Webmorph, 3.3x for MAD22 FaceMorpher. This matches face size only, not processing history, and the alignment borders remain.
- **The controlled Poisson set (H1).** A fifth landmark tool (MediaPipe Delaunay warp plus Poisson blend) on CASIA-WebFace identities at 112 px; 598 pairs. Both classes share source photos, size, the ~40% black border and post-processing. The only known remaining difference is file size (morphs are 3–5% smaller PNGs): floor 0.620 on `orig` and 0.681 on `pp`. `orig` is the registered primary variant."""

S1_TESTS_GAN = """- **H3.** StyleGAN3 two-person latent-average morphs against single-person renders of the same generator. Its classes differ in latent spread by construction.
- **X4.** The same morphs against renders matched to the morphs' latent spread; little power against a two-identity signal by construction.
- **H4b.** StyleGAN v1 MIPGAN-I-style morphs against single-identity renders of the host; file size alone gives 0.912.
- **Renders vs camera (H-new-83).** A separate check of whether a detector scores generator output above camera photos. Registered verdict "neither"; per-pool AUCs descriptive."""

S1_TESTS_DIF = """- **Shrunk genuine photos (E7).** Each diffusion family has its own dose; the DiM pools average 3.19x. For the SelfMAD release it was also run on the raw files with its own crop, with three shrinking methods: one result, not three replications.
- **Genuine photos through the morphs' generator family (X3).** DiffAE reconstructions of the genuine photos, photos only resized by DiffAE's aligner, and one-person "morphs". Releases only. Its positive control failed (FE ViT-L/14 0.636 ≤ 0.65): "assay sensitivity not shown".
- **Other diffusion generators (H2, Arc2Face).** H2 is low-potency (1.1% of morphs verify against both contributors); Arc2Face is the potent set (94.7%). Both columns are descriptive."""

S2_READ = """- **Cells.** "→" joins a benchmark number and its controlled number of the same metric (EER → EER). " | " separates different tests or metrics.
- **Rows.** Releases are the authors' official weights, one network each. Recipes are our re-implementations, trained on SMDD only (d0); their numbers are means over the stated number of networks (seeds).
- **‡** marks the 12 primary rows of the registered GAN test (C3). Rows 4–8 are descriptive and outside C3.
- **Verdict words** ("holds", "partly holds", "does not hold", "not shown") are post hoc labels of this note, not A41 grades. "Partly holds" is not the dropped phrase "partly carried"."""

S2_NOTES = """- **Regular, benchmark [a].** EER %, FRLL families in the order FaceMorpher / OpenCV / AMSL / WebMorph, each against the 204 FRLL genuine photos (102 persons). MAD22 FaceMorpher is against the 185 MAD22 genuine photos (byte copies of FRLL photos); every MAD22 number is on our 185 + 4,069 MAD22 files, against the published 204 + 4,483. A12.4 calls the recipes' benchmark pool "an eval-pipeline diagnostic, never a detection result".
- **Regular, controlled [b].** E7 shrinking factors: FRLL FM 1.47x, OCV 1.56x, AMSL and WebMorph 1.80x, MAD22 FaceMorpher 3.30x. MAD22 OpenCV and Webmorph are left out (~1.0x, so E7 tests nothing there). Person-clustered 95% CIs (A41 S3): SelfMAD FRLL FM 4.8 [1.95, 7.34] and OCV 3.9 [1.41, 5.85]; ViT-B/16 FRLL FM 4.42 [2.12, 6.93] and OCV 4.42 [2.08, 7.37]; MAD22 FM SelfMAD 0.11 [0.00, 0.89] and ViT-B/16 5.94 [3.25, 10.62].
- **H1 label rule** (A36 amendment 1). "Above the floor" needs a point margin D ≥ +0.05, a one-sided Bonferroni lower bound of D > 0, and a seed-CI lower bound of AUC − floor > 0. Labels on the 11 primary rows are registered; the others are descriptive; all were set post-freeze. The SelfMAD own-crop `orig` 0.872 and `pp` 0.821 are point estimates.
- **GAN, benchmark [c].** MIPGAN-I is EER % on MAD22 MIPGAN-I (generator PNG against camera JPEG). ViT-B/16 18.4 [13.4, 23.6] and ViT-L/14 11.9 [8.0, 15.6] (person 95%, DC-8). The G-test is held-out StyleGAN2 latent-average morphs of FEI pairs against FEI frontal captures; its morphs are scaled to the genuine photos' face size by construction. C4: "These sets compare generator output (PNG) with camera photos (JPEG)."
- **GAN, controlled [d].** H3 floors: bytes 0.526, eye geometry 0.560, combined covariates 0.607–0.617; "reversed" means the 95% pair CI lies below 0.5. A row would count as "shown" only if H3 is above its combined floor by its CI and X4 is above 0.5 by its CI. No row meets this: the highest H3 is M2 at 0.591 [pair 90% 0.572, 0.610], the highest X4 is M4 at 0.517 [95% 0.493, 0.541].
- **Diffusion, benchmark [e].** EER on the FRLL diffusion families against the original genuine photos. Recipes show UA8c: the mean EER over the seven held-out diffusion families, each capped at 50. The cap hides inversion, so the uncapped UA8 under E7 is shown beside it.
- **Diffusion, controlled [f].** Person-clustered 95% CIs exist only for the SelfMAD own-crop, SelfMAD our-pipeline, ViT-B/16, ViT-L/14 and FE ViT-L/14 releases. X3 values are Greedy-DiM / MorDIFF unless a family is named; the Greedy-DiM vs reconstruction comparison is floor-limited (file bytes alone 0.987–0.998). H2 (IP-Adapter-FaceID SD 1.5; floors 0.522 / 0.518) and Arc2Face (every row 0.482–0.539) are descriptive."""

S2_RULES = """- **Regular.** *holds*: under E7 the EER is ≤ 10% on at least two FRLL landmark families and no FRLL landmark family or MAD22 FaceMorpher rises by more than 3 points, **and** H1 `orig` is labelled above its floor. *partly holds*: exactly one of the two. *does not hold*: neither. Descriptive tags: *inverted natively* (native EER above 50% on at least two FRLL landmark families), *weak natively* (≥ 25% on all four, not inverted), *collapses under E7* (a family at ≤ 35% natively rises by at least 10 points).
- **GAN.** *shown / not shown*, as in [d]. Every row is "not shown". It does not mean the detector is blind to two identities.
- **Diffusion.** E7 "holds" on a family when the E7 EER is within 5 points of native and at most 25%. *holds*: E7 holds on at least one family and H2 or Arc2Face is clearly above its floor (no row qualifies). *partly holds*: E7 holds on at least one family. *does not hold*: on no family. X3 is left out of the verdicts: its positive control failed, and C2 calls the one separating row "open"."""

S2_STATUS = """- **Registered decision cells.** SelfMAD MAD22 FaceMorpher under E7 (F4 (i), supported); ViT-B/16 FRLL FaceMorpher under E7 (F4 (ii)); SelfMAD Greedy-DiM and MorDIFF (C1, "strong (final)"); ViT-B/16 MorDIFF (C2, "descriptive row (final)"; the refuter F7 fired); ViT-L/14 Greedy-DiM as the negative control (F4 (iii), supported); FE ViT-L/14 as the X3 positive-control gate (failed, 0.636 ≤ 0.65).
- **Registered tests.** H3 and X4 on the ‡ rows: C3, "strong (narrow)". Claim B: "meets its registered criterion". C4: "construction sentence".
- **Registered labels without a grade.** The H1 `orig` labels on the 11 primary rows; H4b through A36 H-new-72 ("neither"); renders vs camera, H-new-83 ("neither"); "CLIP carries the render cue", H-new-84 ("neither").
- **Everything else is descriptive**, including every verdict word, every `pp` H1 label and every recipe number. A41's rules were written after earlier estimates on the same questions had been seen; never call A41 "confirmatory"."""

S3_INTRO = """The comparison table says how each detector does under the controls. This section asks the stricter question: for each method, was a shortcut found under A41's registered rules, and how far does the evidence go?"""

S4_INTRO = """This section names what is still missing for each claim. None of it can change a grade."""

# ---------------------------------------------------------------- assemble
m = re.search(r"<link rel=\"preconnect\".*?</style>", FIND, flags=re.S)
if not m:
    sys.exit("could not find findings.html head block")
head = m.group(0)
# keep the :root token blocks, fonts link and base typography; drop findings-only component rules after `.tw`
fonts = head[: head.index("<style>")]
css_src = head[head.index("<style>") + len("<style>"): head.rindex("</style>")]
tokens = css_src[: css_src.index("body{")]
base = css_src[css_src.index("body{"): css_src.index(".lede")]

PAGE_CSS = tokens + base + """
/* Layout: one reading column (74ch) for prose; tables run to the 1120px wrap and scroll inside their own frame. */
.label{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.lede{color:var(--muted);max-width:68ch;margin:6px 0 0}
header.top{display:flex;flex-direction:column;gap:10px}
.facts{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:1px 9px;font-size:.78rem;
border:1px solid transparent;white-space:nowrap;font-weight:600}
.k-asof{background:var(--sunk);color:var(--ink);border-color:var(--line)}
.k-read{background:var(--info-soft);color:var(--info)}
.k-pend{background:var(--warn-soft);color:var(--warn)}
.k-seal{background:var(--violet-soft);color:var(--violet)}
.v-yes{background:var(--good-soft);color:var(--good)}
.v-part{background:var(--warn-soft);color:var(--warn)}
.v-no{background:var(--bad-soft);color:var(--bad)}
.v-ns{background:var(--grey-soft);color:var(--muted)}
nav.toc{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;border-top:1px solid var(--line);
border-bottom:1px solid var(--line);padding-block:10px}
nav.toc a{color:var(--accent);text-decoration:none}
nav.toc a:hover{text-decoration:underline}
nav.toc b{font-family:"IBM Plex Mono",monospace;font-weight:600;color:var(--muted);margin-right:4px}
section.s{display:flex;flex-direction:column;gap:14px;min-width:0;scroll-margin-top:12px}
section.s>h2{padding-top:18px;border-top:1px solid var(--line)}
section.s h2 .n{font-family:"IBM Plex Mono",monospace;color:var(--accent);margin-right:8px}
.prose{max-width:74ch;min-width:0}
.prose p,.prose li{line-height:1.62}
.prose p{margin:0 0 10px}
.prose ul,.prose ol{padding-left:1.3em;margin:0 0 10px;display:flex;flex-direction:column;gap:4px}
.prose li>ul,.prose li>ol{margin:4px 0 0}
.prose li>p{margin:0 0 4px}
.prose h3{margin:16px 0 6px}
code{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;background:var(--sunk);padding:0 4px;
border-radius:4px;font-size:.88em}
a{color:var(--accent)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px 22px}
.cols>div{min-width:0}
.cols h3{font-size:.98rem;margin:0 0 6px}
.cols ul{padding-left:1.2em;margin:0;display:flex;flex-direction:column;gap:5px;font-size:.92rem;line-height:1.55}
.callout{background:var(--accent-soft);border-left:3px solid var(--accent);border-radius:6px;padding:12px 16px;
max-width:74ch}
.callout p:last-child,.callout ul:last-child{margin-bottom:0}
.status{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 16px;max-width:74ch}
.status ul{margin-bottom:0}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface);
-webkit-overflow-scrolling:touch}
.tw:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:.82rem;font-variant-numeric:tabular-nums}
th,td{padding:6px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.45}
th{background:var(--sunk);font-weight:600;position:sticky;top:0}
tbody tr:last-child td{border-bottom:none}
tr.grp td{background:var(--sunk);font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;font-size:.9rem;
padding-block:8px}
td:first-child{font-family:"IBM Plex Mono",monospace;color:var(--muted);white-space:nowrap}
table.cmp{min-width:1060px}
table.cmp td:nth-child(2){min-width:190px;font-weight:600}
table.cmp td:nth-child(n+3){min-width:250px}
table.sc{min-width:2350px}
table.sc th{white-space:normal}
table.sc td:nth-child(2),table.sc th:nth-child(2){min-width:180px;position:sticky;left:0;z-index:1;
background:var(--surface);box-shadow:1px 0 0 var(--line)}
table.sc th:nth-child(2){background:var(--sunk);z-index:2}
table.sc td:nth-child(2){font-weight:600}
table.sc td:nth-child(3){min-width:360px}
table.sc td:nth-child(4){min-width:150px}
table.sc td:nth-child(n+5){min-width:230px}
table.small{width:auto;min-width:0}
table.small td:first-child{font-family:inherit;color:var(--ink);white-space:normal}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 14px;min-width:0;
display:flex;flex-direction:column;gap:6px}
.card h3{font-size:.98rem;display:flex;gap:8px;align-items:baseline}
.card h3 .n{font-family:"IBM Plex Mono",monospace;color:var(--accent);font-size:.85rem}
.card ul{padding-left:1.1em;margin:0;display:flex;flex-direction:column;gap:4px;font-size:.88rem;line-height:1.5}
.card li>ul{margin-top:3px}
.card p{margin:0;font-size:.88rem;line-height:1.5}
.card em{font-style:normal;font-weight:600;color:var(--muted)}
details.src{background:var(--surface);border:1px solid var(--line);border-radius:8px}
details.src>summary{cursor:pointer;padding:10px 14px;font-weight:600}
details.src[open]>summary{border-bottom:1px solid var(--line)}
details.src>div{padding:12px 16px;font-size:.88rem;overflow-wrap:anywhere}
footer{color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);padding-top:12px}
@media (max-width:640px){
h1{font-size:1.5rem}
table.sc td:nth-child(2),table.sc th:nth-child(2){position:static;box-shadow:none}
.cards{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""


def sec(num: int, sid: str, title: str, inner: str) -> str:
    return f'<section class="s" id="{sid}">\n<h2><span class="n">{num}</span>{title}</h2>\n{inner}\n</section>'


def prose(text: str) -> str:
    return f'<div class="prose">{md(text)}</div>'


parts_html = []

# header
parts_html.append(f"""<header class="top">
<div class="label">S-MAD resubmission · competing detectors under construction controls · prepared for Paweł Narolski and co-author</div>
<h1>Detectors without construction shortcuts</h1>
<p class="lede">{INTRO}</p>
<div class="facts">
<span class="chip k-asof">As of 2026-11-07, 18:47 CET</span>
<span class="chip k-seal">MADMamba sealed, not shown</span>
<span class="chip k-read">A42 amendment 1: read, post hoc</span>
<span class="chip k-pend">A43: pending</span>
</div>
</header>""")
parts_html.append(prose("**Scope**\n\n" + SCOPE))
parts_html.append("""<nav class="toc" aria-label="Sections">
<a href="#s1"><b>1</b>What "without shortcuts" means</a>
<a href="#s2"><b>2</b>Comparison table</a>
<a href="#s3"><b>3</b>Shortcut per method</a>
<a href="#s4"><b>4</b>What would make it beyond doubt</a>
<a href="#s5"><b>5</b>What this does not show</a>
<a href="#sources">Sources</a>
</nav>""")

# section 1
s1 = prose(S1)
s1 += prose("### The two kinds of number\n\n" + S1_NUMBERS)
s1 += post_table(md(floor_table), "small", 3)
s1 += '<div class="prose"><h3>How each morph type was tested</h3></div>'
s1 += '<div class="cols">'
s1 += f'<div><h3>Regular (landmark) morphs</h3>{md(S1_TESTS_REG)}</div>'
s1 += f'<div><h3>GAN morphs</h3>{md(S1_TESTS_GAN)}</div>'
s1 += f'<div><h3>Diffusion morphs</h3>{md(S1_TESTS_DIF)}</div>'
s1 += "</div>"
parts_html.append(sec(1, "s1", 'What "without shortcuts" means, and how it was tested', s1))

# section 2
s2 = prose("### How to read the table\n\n" + S2_READ)
s2 += chips(post_table(md(cmp_table), "cmp", 5))
s2 += prose("### Notes to the table (condensed)\n\n" + S2_NOTES)
s2 += prose("### Verdict rules (post hoc, not A41 grades)\n\n" + S2_RULES)
s2 += post_table(md(count_table), "small", 4)
s2 += prose("The GAN column has no count. It is \"not shown\" in every row, and C3 is the only allowed summary.\n\n### Status of the numbers\n\n" + S2_STATUS)
parts_html.append(sec(2, "s2", "Comparison table: regular, GAN and diffusion morphs under the controls", s2))

# section 3
s3 = prose(S3_INTRO)
s3 += prose("### The registered bar (A41)\n\n" + bar_part)
s3 += f'<div class="callout">{md(three_part)}</div>'
s3 += prose("### Reading the table\n\n" + note_key.replace("**Key**", "", 1))
s3 += post_table(md(sc_table), "sc", 10)
s3 += prose("### Notes to the table\n\n" + note_notes.replace("**Notes to the table**", "", 1))
s3 += '<div class="prose"><h3>Method by method: what was found, how we know, how sure</h3></div>'
s3 += '<div class="cards">'
for num, name, body in cards:
    s3 += f'<article class="card"><h3><span class="n">{num}</span>{name}</h3>{md(body)}</article>'
s3 += "</div>"
s3 += f'<div class="callout"><p><strong>Across rows.</strong></p>{md(across.strip())}</div>'
parts_html.append(sec(3, "s3", "Shortcut per method, against the registered bar", s3))

# section 4
s4 = prose(S4_INTRO + "\n\n" + doubt_part)
s4 += f'<div class="status">{md(note_status)}</div>'
s4 += prose(drop_heading(note_s4))
parts_html.append(sec(4, "s4", 'What would make it beyond doubt', s4))

# section 5
s5 = prose(drop_heading(tbl_notshow))
s5 += prose("### Flags for the author\n\n" + drop_heading(tbl_flags).strip() + "\n\n" + drop_heading(note_flags).strip().replace("1. **CONCLUSIONS", "8. **CONCLUSIONS").replace("2. **The name", "9. **The name").replace("3. **Staged", "10. **Staged"))
parts_html.append(sec(5, "s5", "What this does not show", s5))

# sources
src = md(note_sources.replace("**Sources**", "**For the shortcut section**", 1)) + md(drop_heading(tbl_sources).replace("Paths are under", "**For the comparison table.** Paths are under", 1))
parts_html.append(f'<details class="src" id="sources"><summary>Sources</summary><div class="prose">{src}</div></details>')
parts_html.append('<footer>Built from <code>methods_table_final.md</code> and <code>shortcut_per_method_final.md</code> (scratchpad, read-only gathers of logged reader outputs). No number on this page was computed for it, apart from the E7 − native differences and ranges carried over from those files.</footer>')

page = (
    "<title>Detectors Without Shortcuts</title>\n"
    '<meta name="claude:viewport-fit-sides" content="cover">\n'
    + fonts.strip() + "\n<style>\n" + PAGE_CSS.strip() + "\n</style>\n"
    + '<div class="wrap">\n' + "\n".join(parts_html) + "\n</div>\n"
)
OUT.write_text(page, encoding="utf-8")
print(OUT, len(page))
