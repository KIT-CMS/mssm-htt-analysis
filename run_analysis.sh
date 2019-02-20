#!/bin/bash

# Error handling to ensure that script is executed from top-level directory of
# this repository                                                                                                                                                                                                   
for DIRECTORY in shapes plotting utils datacards combine
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

## Clean-up workspace
./utils/clean.sh

# Parse arguments
ERA=$1               # options: 2017
CHANNELS=${@:2}      # options: et, mt, tt

## Create shapes of systematics
./shapes/produce_shapes.sh $ERA $CHANNELS
#
## Convert to sync shape format.
./shapes/convert_to_synced_shapes.sh $ERA


# Create datacards.
JETFAKES=0      # options: 0, 1
EMBEDDING=0     # options: 0, 1
./datacards/produce_datacard.sh $ERA $JETFAKES $EMBEDDING $CHANNELS

# Create workspace.
./datacards/produce_workspace.sh $ERA | tee ${ERA}_produce_workspace.log

# Run statistical inference.
MODE="mod_indep"     # switch for model dependent and independent limits, options: mod_indep, mod_dep
./combine/model_independent_limits.sh $ERA $MODE | tee ${ERA}_model_independent_limits.log
