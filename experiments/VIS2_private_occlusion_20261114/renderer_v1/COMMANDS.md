# Prospective renderer commands — ROOT only after NEW grant and actual fullresult admission

Source-only generatedtests now (no realdata/graphics):

    python3 -I src/VIS2/render_v1/test_contract.py

AfterOTHERprerendercode-review andOTHERactualfullnumericalpostreview, root stagesONLYauthorised4sourcePNG+3RESULTJSON replicas (neverreference00010) andcreatesNEWexactROOT_PRIVATE_MEASURED_RENDER_RELEASE.json. Fillallhashes fromactualresults/reviews; noauthoredGOtemplate orplaceholdervaluesareprovided. Suggestedactualfilelayout:data-root/inputs/<input_id>.png anddata-root/<model>/RESULT.json. Canonicaloriginpaths mustbe exactlythoseinCONFIG_MAC.json.

BeforefirstactualPDFcreation, followPDFskill marker once:

    /Users/narolski/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node /Users/narolski/.codex/plugins/cache/openai-primary-runtime/pdf/26.1111.10934/skills/pdf/container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 2 --output-format pdf

ThenexactCPUrender (source/configstagedasunchangedcopiesbyroot):

    /Users/narolski/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -I work/VIS2_measured_render_v1/source/render_measured.py --config work/VIS2_measured_render_v1/CONFIG_MAC.json --release work/VIS2_measured_render_v1/ROOT_PRIVATE_MEASURED_RENDER_RELEASE.json --data-root /Users/narolski/Documents/Codex/2026-11-14/na/work/VIS2_measured_render_v1/data --out-root /Users/narolski/Documents/Codex/2026-11-14/na/outputs/shortcut_occlusion_private_review_20261114

The sourcefoldermustincludetheexactSHA256SUMS andtest_contract.py. Config/source/code-reviewfullnumericreviewhashes, exactsource/RESULTreplicahashesanddata/outroots arevalidatedbeforeopen. No realROOTgrantprovidedbyrendererowner.

ONLYafterrealPDFscreated, rootrunsactualPopplerproofs, e.g.:

    /opt/homebrew/bin/pdftoppm -r 300 -png outputs/shortcut_occlusion_private_review_20261114/signed_color.pdf work/VIS2_measured_render_v1/color_proof
    /opt/homebrew/bin/pdftoppm -r 300 -png outputs/shortcut_occlusion_private_review_20261114/gray_sign_hatching.pdf work/VIS2_measured_render_v1/gray_proof

InspectEVERYactualpage at180mm, minfont>=8pt, values/colors/legend/sourcegridmatchCELL_RENDER_RECORDS, all12pages/models/photos/fills/zerosretained, grayscaleandrights/caption. AnOTHERreviewer mustgrant scopedprivatepresentationafteractualnumeric/print/sourcepermissionchecks. Do notshowempty/mockmaps whileawaitingfullresults. Rendering failures cannotbe called scientificfailure orpermissiontoomitweak/unfavourablemaps. Allsourceworker/prereg/VIS1/main/WIP unchanged.
