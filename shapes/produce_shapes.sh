#!/bin/bash

BINNING=shapes/binning.yaml
ERA=$1
CHANNELS=${@:2}

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag ${ERA}_signal_categories \
    --num-threads 32 \
#    --skip-systematic-variations True
