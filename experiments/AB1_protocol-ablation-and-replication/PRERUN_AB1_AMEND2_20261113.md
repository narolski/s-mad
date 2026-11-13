# Pre-run check of AB1 amendment 2 (13 Nov 2026, experiment-reviewer, Opus; saved by the owner)

Verdict GO WITH FIXES. All four directions match the lead's text; the AUC direction (S4 positive, S3 negative) is right;
d_flag differences out part of the operating point; 112.7 px is untrained. Findings: F1 (major, code) the H-sp3 margin
was not inclusive at float precision (20 of 81 exact +0.20 cases fail, including Sb 0.37-0.40); compare counts; H-ab4
prediction 1 has the same flaw (lead to decide on a correction). F2 (major) H-sp2 needs A's control gate
("uninformative" if met on ≤ 3 seeds at amsl112). F3 (major) outcome meanings over-claimed; replacement wording given
(applied). F4 (minor) state n = 4 falsification (≤ 1 of 4, as R2). F5 (minor) re-pin the reader; the drop mock predates
the amendment; re-run with one seed missing. F6 (minor) coin-flip null 6/32 = 0.19 for the margin-free tests; four post
hoc tests plus H-ab4, no multiplicity correction. Disclosure adequate; no conflicts; one read unchanged. Improvements:
print Sp − Sb native and camera flag rates beside H-sp1/H-sp3; print per-seed Sp − Sb values.
Owner's action: F1-F6 and both improvements applied; H-ab4's float flaw corrected in code as an implementation fix of
the registered inclusive-margin rule (text unchanged), reported to the lead.
