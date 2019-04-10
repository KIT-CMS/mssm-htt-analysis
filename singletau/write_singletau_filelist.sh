#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

python singletau/write_singletau_filelist.py \
    --directory ${ARTUS_OUTPUTS} \
    --database ${KAPPA_DATABASE} \
    --channel ${CHANNEL} \
    --era ${ERA} \
    --output singletau/${ERA}_${CHANNEL}/filelist.yaml
