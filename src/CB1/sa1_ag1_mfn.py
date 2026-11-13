"""CB1 amendment 5, cell 14-MFN: the AG1 reader (src/AG1/ag1_read.py, imported unchanged) on the MixFaceNet-MAD 'rel'
scores; only its release list is set to this release. Same pools, contrasts, bootstrap and corrected-MAD22 threshold
(FRLL R0 vs the published MIPGAN files of the AG1 manifest) as the other releases' cells.
  python3 -I sa1_ag1_mfn.py OUT_DIR"""
import sys
sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
import ag1_read as R
R.RELEASES = ("mixfacenet_mad_smdd__rel",)
R.PRIMARY_RELEASES = ("mixfacenet_mad_smdd__rel",)
sys.argv = ["ag1_read.py", "--data", "/mnt/t7/smad_next/AG1/data", "--logs", "/mnt/t7/smad_next/AG1/results",
            "--photos", "/mnt/t7/smad_next/AG1/inputs/pack/photos.json", "--scores", "/mnt/t7/smad_next/CB1/mfn_rel/ag1_scores",
            "--out", sys.argv[1]]
R.main()
