"""Exact adopted HN native transfer policy; separate source and journal."""
EXPERIMENT='SPRINT5_2'
ARMS=('matched','self')
SEEDS=(531,532,533,534,535)
TRAIN_SOURCE='3640adc6a2204e1d82ce455167e00e433859f4b63bf63970f67d3ca0910ca793'
STEPS=100
BATCH=248
FORWARDS=24800
DRAWS=10000
RNG=2026111402
DRAW_SHA='0f045d8b9e71ebd627702a362bd473356de4091bec3aa6322bf92757c87f8dbd'
SEED_SHA='eb04e4b3ff18af8075453852642c7c0f1640b3a62e9879a01af25ccca03ab239'
POLICY_BINDING_SHA='007a6fbdb25221d9069a304b5cc25a789dcf9177ef5480e7ad4201908a54d414'
PACKET_SHA='4268acf24217e26342f64f6a0294fa60ccc911489f131825d579464a9a7fbc9b'
ONCE='/mnt/t7/smad_next/SPRINT5_2/reader_once_v1'
OUTPUT='/mnt/t7/smad_next/SPRINT5_2/reader_output_v1/RESULT.json'
ROOT='/home/narolski/smad-next'
BINDING=ROOT+'/experiments/SPRINT5_20261114/hn1/reader_implementation/PILOT_READER_BINDING.json'
POLICY_ROOT=ROOT+'/experiments/SPRINT5_20261114/pilot_reader_policy_review'
BASELINE_ARCHIVE_SHA='a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa'

def task(arm,seed):
    assert arm in ARMS and seed in SEEDS
    return f'SPRINT5_2_pilot_v1_{arm}_s{seed}'
