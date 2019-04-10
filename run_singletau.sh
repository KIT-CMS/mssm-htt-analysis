#!/bin/bash

ERA=$1
CHANNEL=$2

if [ ! -d "singletau/${ERA}_${CHANNEL}" ]
then
    echo "[singletau] Creating directory singletau/${ERA}_${CHANNEL}/ ..."
    mkdir singletau/${ERA}_${CHANNEL}/
fi

./shapes/produce_shapes_singletau.sh $ERA $CHANNEL

./singletau/write_singletau_filelist.sh $ERA $CHANNEL

./singletau/run_singletau.sh $ERA $CHANNEL
