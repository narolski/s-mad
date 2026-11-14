# VIS2 exact local commands — prospective; no GPU phase authorized

CPUgeneratedfixtures:

    /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/VIS2/v1/test_geometry.py

CPUmetadata-only (hashes4oldsourcePNGandactualsourcefiles, packageversionmetadata; never modelweights/GPU/occlusion):

    /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/VIS2/v1/occlusion_worker.py --inventory /home/narolski/smad-next/experiments/VIS2_private_occlusion_20261114/v1/INVENTORY.json --metadata-only

Root after OTHERpre-review+cleancommit+NEWgrant may run ONE fixedmodel/phasecommand, recording nativeexit andallstdout/stderr:

    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 timeout --signal=TERM --kill-after=30s 15m nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/VIS2/v1/occlusion_worker.py --inventory /home/narolski/smad-next/experiments/VIS2_private_occlusion_20261114/v1/INVENTORY.json --release /home/narolski/smad-next/experiments/VIS2_private_occlusion_20261114/v1/ROOT_SMOKE_RELEASE.json --model selfmad_hrnet_w18 --phase smoke

SamefixedsmokecommandwithmodelAthenB, onlyifnewrootreleaseexactmodelslistincludesallthree. No automaticmodel selection. Allthreecomplete/failedsmokes reviewedbyOTHER. SeparateROOT_FULL_RELEASE.json thenphasefullsamecommandselfmad,A,B; noautomaticpromotion. Fixedoutputpathsderivedfrominventory/phase/model. NeitherROOTreleaseexistsfromauthor.

RequiredROOTreleasefields: decision=GO_VIS2_NUMERIC_OCCLUSION_ONLY,author,distinctreviewer,independent_review_path/SHA,inventory_sha256,prereg_sha256,source_manifest_sha256,source_commit,phase,models,new_private_occlusion_transform_allowed=true,source_pixel_export_allowed=false,new_overlay_render_allowed=false. Fullalso requires smoke_postreview_path/SHA. Commit source/inputauthorityfirst, thenreleasewithsource_commitpointingthatpriorboundsourcecommit, commitrelease and keepallownedpaths+releaseclean. This avoids selfreferentialcommitSHA. Otherunrelatedsharedrepochangesarepreserved.

No new501/Sb403commandisofferedasrunnable:501_EXTENSION_HOLD.json containsconcretesource/archive/runtimeconditions. No checkpoint/read/runtimeadmission is fabricated; anynativeH100phase needs its ownreviewedpackageandnewgrant. PRINT_LAYOUT_SPEC isnotpermissiontorendermaps. Actualnewnumericresults must existandbeindependentlyadmittedbeforefutureoverlayrendererreceivesnewprivaterendergrant.
