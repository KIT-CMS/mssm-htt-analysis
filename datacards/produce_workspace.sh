#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1

NUM_THREADS=8

# Collect input directories for eras and define output path for workspace
INPUT=output/${ERA}_mssmhtt/cmb
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

OUTPUT=${ERA}_workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."

# Clean previous workspace
rm -f $OUTPUT

combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel ${NUM_THREADS} -v 2 \
    -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
    --PO '"map=^.*/ggH.?$:r_ggH[0,0,200]"' \
    --PO '"map=^.*/bbH$:r_bbH[0,0,200]"'
