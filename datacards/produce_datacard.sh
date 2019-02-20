#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
JETFAKES=$2
EMBEDDING=$3
CHANNELS=${@:4}

NUMTHREADS=8

#remove output directory
rm -rf output/${ERA}_mssmhtt

#create datacards
$CMSSW_BASE/bin/slc6_amd64_gcc491/MorphingMSSMFull2017 \
    --base_path=$PWD \
    --input_folder_mt="/" \
    --input_folder_et="/" \
    --input_folder_tt="/" \
    --jetfakes=$JETFAKES \
    --channel=`echo ${CHANNELS} | sed "s/ /,/g"` \
    --output_folder=${ERA}_mssmhtt \
    --real_data=false \
    --auto_rebin=false \
    --manual_rebin=true \
    --bbH_nlo=false \
    --ggHatNLO=false \
    --zmm_fit=false \
    --ttbar_fit=false \
    --control_region=0 \
    --postfix="-Run2017-mttot" \
    --mass="MH" \
    --check_neg_bins=true \
    #--auto_rebin=true \
    #--embedding=$EMBEDDING \

