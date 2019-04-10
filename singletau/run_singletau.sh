#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_python.sh
source utils/setup_cvmfs_sft.sh

python singletau/run_singletau.py \
    --config singletau/config_${ERA}_${CHANNEL}.yaml \
    --filelist singletau/${ERA}_${CHANNEL}/filelist.yaml \
    --num-processes 10
