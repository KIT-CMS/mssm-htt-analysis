#!/bin/bash

ERA=$1

# Samples Run2017
#ARTUS_OUTPUTS_2017=/ceph/mburkart/Artus/artusjobs_Data_and_MC_Fall17v2MC_ReReco31Mar2018_VBFAndSingleTauTrigger_01_27_2019/merged/
ARTUS_OUTPUTS_2017=/ceph/mburkart/Artus/artusjobs_Data_and_MC_Fall17v2MC_ReReco31Mar2018_MSSM_shifts/merged/
ARTUS_FRIENDS_FAKE_FACTOR_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_NovPU/fake_factor_friends_njets_mvis_NEW_NN_Dec11

# Error-handling
if [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2017
else
    echo "[ERROR] Era $ERA is not implemented." 1>&2
    read -p "Press any key to continue... " -n1 -s
fi

# Kappa database
KAPPA_DATABASE=/portal/ekpbms1/home/mburkart/workdir/Analysis/CMSSW_9_4_9/src/Kappa/Skimming/data/datasets.json
