#!/bin/bash

CONFIG=$1
SAMPLE=$2
FILE=$3
FOLDERS=${@:4}

for FOLDER in $FOLDERS
do
    python singletau/add_singletau_numbers.py \
        $CONFIG \
        $SAMPLE \
        $FILE \
        ${FOLDER}/ntuple
done
