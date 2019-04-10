#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python shapes/produce_shapes_singletau.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --channels $CHANNEL \
    --era $ERA \
    --tag ${ERA}_${CHANNEL} \
    --num-threads 10 \
