"""Immutable experiment-specific constants; no arbitrary arm/seed CLI overrides."""
EXPERIMENT='SPRINT5_4'
ARMS=('narrow_more_variants','broad_fewer_variants')
SEEDS=(511,512,513,514,515)
TRAIN_SOURCE='debbea9496cdcd553cf2b18671f0868452cfdc9cc16fa7ee66b0e81b97361a04'
STEPS=100
BATCH=32
FORWARDS=3200
DRAWS=10000
RNG=2026111404
ONCE='/mnt/t7/smad_next/SPRINT5_4/reader_once_v1'
OUTPUT='/mnt/t7/smad_next/SPRINT5_4/reader_output_v1/RESULT.json'
BINDING='/home/narolski/smad-next/experiments/SPRINT5_20261114/breadth/reader_implementation/PILOT_READER_BINDING.json'
ROOT='/home/narolski/smad-next'


def task(arm,seed):
    assert arm in ARMS and seed in SEEDS
    return f'SPRINT5_4_pilot_v1_{arm}_s{seed}'
