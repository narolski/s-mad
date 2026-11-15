# VIS1 source grounding record

Grounding skill read before writing inference. Local load_archive.py --list returned missing /Users/narolski/.claude/model-provenance; check_grounding.py --model SelfMAD returned no archive. Mechanical provenance-archive check is UNAVAILABLE, not PASS. No model IDs/API were recalled from memory; no downloads or model-provenance archive modifications performed. Instead exact existing approved XAI inventory/source were inspected and reused.

Inspected actual source before writing:
- experiments/AGENTIC_delivery_20261114/xai_gradient_pilot_fp32.py: own/released model construction, strict trainable-key-set and frozen-base reconstruction, noTTA float32 loader/model signatures, exact flags and checkpoint hashes. VIS1 removes gradients/maps/TTA and permits only already pinned SelfMAD/A/B.
- PN1 and A46 common.py: ImageItems816–899 constructor/load/__getitem__, PILbilinear final224/384 RGB[0,1] without augmentation; forward_logit396 and build_run_model1079–1090 actual meta/LoRA reconstruction. The original original CLIP model embeds its own normalization; no new external normalization added.
- A46 a12_released.py: RELEASES SelfMAD HRNetW18/classes2/morphindex1/res384/RGB/mean0/std1, head_logit, adapt_input, extract_state, load_release162 and build_release170. Same strict safetensors checkpoint as approved XAI.
- prep_ffhqm.py217–235: existing INTER_AREA shrink BEFORE re-alignment to512, so VIS1 explicitly retains processing/realignment confound and no JPEG-only label.

Exact inspected source files, model/base weights, environment versions and inputs are bound in INVENTORY_v2.json; preflight hashes all before any model import. Seven generated scalar tests and metadata-only preflight PASS; no GPU/model forward was executed. Full dependency closure of timm/torch is package-version-pinned rather than a vendored exhaustive source archive. Independent code review is required before root GO.
