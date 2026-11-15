# FFHQ FaceMorpher two-person morphs against one-photo renders (XF1)

Owner: PR1 owner. Development data only (FFHQ MS1 hold-out frames; DATA D12a, D1d). Status: registration draft, awaiting the pre-run check. Code: `src/XF1/`. Row list and packs on /mnt/t7/smad_next/XF1/.

## On hold (Fri Nov 13 22:20 CET; lead's ruling after the pre-run check)
The pre-run check of the draft (3abd284), saved at `experiments/reviews/PRERUN_XF1_20261113.md` (a93ae2f), returned GO WITH FIXES. Its first finding breaks the purpose of the draft:
- With identical point sets, the FaceMorpher warp is the identity. FM(H,H) is therefore the plain photo H minus one grey level on 8-19% of pixels; it is not a rendering control.
- Read 1 would then compare a two-person morph against an untouched photo. That comparison is confounded by resampling and averaging: a one-line smoothness statistic already gives 0.736.

**Lead's ruling: XF1 is not scored as drafted.** Nothing is uploaded or queued.
- The lead has asked DATA whether the approved ladder builder can make a FaceMorpher warp-only image of H toward the H-and-B mean shape, with no blending, for the 299 hosts.
- **If it can:** XF1 is revised to FM(H,B) against that warp-only image, with fixes F2-F8, and goes through a second pre-run check.
- **If it cannot:** XF1 is closed as "not run: no matched negative without the author's word".
- The packs on /mnt/t7/smad_next/XF1/ are kept, unused.
