
#!/bin/bash

BINNING=shapes/binning_control.yaml
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
    --control \
    --era $ERA \
    --tag $ERA \
    --num-threads 32 \
    --skip-systematic-variations True
