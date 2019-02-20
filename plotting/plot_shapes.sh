#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
JETFAKES=$2
EMBEDDING=$3
CHANNELS=${@:4}

EMBEDDING_ARG=""
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

mkdir -p ${ERA}_plots
for FILE in "2017_shapes_m3200_prefit.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes_2017.py -i $FILE -c $CHANNELS -e $ERA $OPTION $JETFAKES_ARG $EMBEDDING_ARG --linear #--normalize-by-bin-width  --linear
    done
done
