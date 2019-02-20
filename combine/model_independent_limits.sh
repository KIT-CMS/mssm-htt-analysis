#!/bin/bash

ERA=$1
MODE=$2

NUM_THREADS=10

source utils/setup_cmssw.sh

if [[ $MODE == "mod_indep" ]]
then
    # ggPhi limits
        #"80,90,100,110,120,130,140,180,200,250,350,400,450,600,700,800,900,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200" \
    combineTool.py -m \
        "200" \
        -M Asymptotic --rAbsAcc 0 --rRelAcc 0.0005 --boundlist input/mssm_boundaries.json -t -1 \
        --setPhysicsModelParameters r_ggH=0,r_bbH=0 --redefineSignalPOIs r_ggH -d output/${ERA}_mssmhtt/cmb/${ERA}_workspace.root \
        --there -n ".ggH" --parallel ${NUM_THREADS}
    #combineTool.py -m \
    #    "80,90,100,110,120,130" \
    #    -M Asymptotic --rAbsAcc 0 --rRelAcc 0.0005 --boundlist input/mssm_boundaries.json \
    #    --setPhysicsModelParameters r_ggH=0,r_bbH=0,ggHt_frac=0,ggHb_frac=0 -t -1 --parallel ${NUM_THREADS} \
    #    --redefineSignalPOIs r_ggH -d output/${ERA}_mssmhtt/*/${ERA}_workspace.root --there -n ".ggH.tonly"
    #combineTool.py -m \
    #    "80,90,100,110,120,130" \
    #    -M Asymptotic --rAbsAcc 0 --rRelAcc 0.0005 --boundlist input/mssm_boundaries.json \
    #    --setPhysicsModelParameters r_ggH=0,r_bbH=0,ggHt_frac=0,ggHb_frac=1 -t -1 --parallel ${NUM_THREADS} \
    #    --redefineSignalPOIs r_ggH -d output/${ERA}_mssmhtt/*/${ERA}_workspace.root --there -n ".ggH.bonly"
    # bbPhi limits
    combineTool.py -m \
        "80,90,100,110,120,130,140,180,200,250,350,400,450,600,700,800,900,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200" \
        -M Asymptotic --rAbsAcc 0 --rRelAcc 0.0005 --boundlist input/mssm_boundaries.json -t -1 \
        --setPhysicsModelParameters r_ggH=0,r_bbH=0 --redefineSignalPOIs r_bbH -d output/${ERA}_mssmhtt/cmb/${ERA}_workspace.root \
        --there -n ".bbH" --parallel ${NUM_THREADS}
    # Collecting the output
    combineTool.py -M CollectLimits \
        output/${ERA}_mssmhtt/cmb/higgsCombine.ggH*.root --use-dirs -o "2017_mssmhtt_ggH.json"
    combineTool.py -M CollectLimits \
        output/${ERA}_mssmhtt/cmb/higgsCombine.bbH*.root --use-dirs -o "2017_mssmhtt_bbH.json"
fi

if [[ $MODE == "mod_dep" ]]
then
    echo "Not yet implemented. Skipping..."
fi
