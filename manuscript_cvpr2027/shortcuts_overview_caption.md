# Caption draft — `figures/shortcuts_overview.tex` (`fig:shortcuts_overview`)

\textbf{A verdict map of non-identity shortcut traits in single-image morph detection.} A
morph candidate (center) can be separated from genuine photographs by traits that have
nothing to do with combining two identities; the four quadrants and the lower band group
the trait families our controls isolate. \textbf{(1)}~Processing \& storage: morph-free
networks trained only on shrink-and-enlarge copies of synthetic faces reach 0.0\% EER on
the native MorDIFF cell (10/10 networks), while the registered combined storage verdict
remains inconclusive with false alarms attenuated, not removed. \textbf{(2)}~Rendering:
the generative render path alone is a registered \emph{used} cue (5/5 seeds; 78--90\% of
one-photo reconstructions flagged), and low GAN-family EER is not established as
morph-specific. \textbf{(3)}~Blending: warp traces, the morph tool's halo ring and
noise/variance averaging drive blend-versus-warp discrimination, but the registered
verdict for the matched $+0.011$~AUC blend gain is inconclusive and low-level statistics
remain a viable explanation. \textbf{(4)}~Splice construction: matched seam-only and
same-person splice negatives control the insertion cue, same-person splice flags drop
from 70--74\% to 36--41\% while staying nonzero, and the count-balanced full recipe gains
$+0.048$~AUC (5/5 seeds). \textbf{(5)}~Contributor dependence remains open: 85\% of
same-person whole-frame morphs are still flagged at the own rule, so detection is not
shown to be identity-specific. Each trait carries its instrument---morph-free training
(MF), the matched-control ladder (MC), or the count-balanced training ablation
(CB)---and its registered verdict; passing one control does not certify the next. All
glyphs are schematic; no real-face imagery is used (a companion figure shows real
examples).
