#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts, Weight
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations, AddWeight, ReplaceWeight, Relabel
from shape_producer.process import Process
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.channel import ETMSSM2017, MTMSSM2017, TTMSSM2017

from itertools import product
from copy import deepcopy

import argparse
import yaml

import logging
logger = logging.getLogger()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for 2017 MSSM analysis.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--num-threads",
        default=32,
        type=int,
        help="Number of threads to be used.")
    parser.add_argument(
        "--backend",
        default="classic",
        choices=["classic", "tdf"],
        type=str,
        help="Backend. Use classic or tdf.")
    parser.add_argument(
        "--tag", default="ERA_CHANNEL", type=str, help="Tag of output files.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "singletau/{0}/{0}_shapes.root".format(args.tag),
        num_threads=args.num_threads,
        skip_systematic_variations=True)

    # Era selection
    if "2017" in args.era:
        from shape_producer.estimation_methods_Fall17 import DataEstimation, ZTTEmbeddedEstimation, TTEstimation, VVEstimation, WEstimation, ggHEstimation, SUSYggHEstimation, SUSYbbHEstimation, DYJetsToLLEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    susy_masses = ["80", "90", "100", "110", "120", "130", "140", "160", "180", "200", "250", "300", "350", "400", "450", "600", "700", "800", "900", "1200", "1400", "1500", "1600", "1800", "2000", "2300", "2600", "2900", "3200"]

    tt = TTMSSM2017()
    tt_processes = {
        "data"         : Process("data_obs",    DataEstimation              (era, directory, tt, friend_directory=[])),
        "DYJetsToLL"   : Process("DYJetsToLL",  DYJetsToLLEstimation        (era, directory, tt, friend_directory=[])),
        "EMB"          : Process("EMB",         ZTTEmbeddedEstimation       (era, directory, tt, friend_directory=[])),
        "TT"           : Process("TT",          TTEstimation                (era, directory, tt, friend_directory=[])),
        "VV"           : Process("VV",          VVEstimation                (era, directory, tt, friend_directory=[])),
        "W"            : Process("W",           WEstimation                 (era, directory, tt, friend_directory=[])),
        }
    for m in susy_masses:
        if m != "160":
            tt_processes["ggH"+m] = Process("ggH"+m, SUSYggHEstimation    (era, directory, tt, m, friend_directory=[]))
        tt_processes["bbH"+m] = Process("bbH"+m, SUSYbbHEstimation    (era, directory, tt, m, friend_directory=[]))

    # Variables and categories
    # regions = {
    #     "N_st_lead": [Cut("pt_1>190&&pttrk_1>50&&pt_2<190", "region"),
    #                   Cut("trg_singletau_leading==1", "trg_selection")],
    #     "N_stdt_lead": [Cut("pt_1>190&&pttrk_1>50&&pt_2<190", "region"),
    #                     Cut("(trg_singletau_leading==1)&&((trg_doubletau_35_tightiso_tightid==1)||(trg_doubletau_40_mediso_tightid==1)||(trg_doubletau_40_tightiso==1))", "trg_selection")],
    #     "N_st_fullovlap": [Cut("pt_1>190&&pttrk_1>50&&pt_2>190&&pttrk_2>50", "region"),
    #                        Cut("((trg_singletau_leading==1)||(trg_singletau_trailing==1))", "trg_selection")],
    #     "N_stdt_fullovlap": [Cut("pt_1>190&&pttrk_1>50&&pt_2>190&&pttrk_2>50", "region"),
    #                          Cut("((trg_singletau_leading==1)||(trg_singletau_trailing==1))&&((trg_doubletau_35_tightiso_tightid==1)||(trg_doubletau_40_mediso_tightid==1)||(trg_doubletau_40_tightiso==1))", "trg_selection")],
    # }
    regions = {
        "N_st_lead": [Cut("pt_1>190&&trkpt_1>50&&pt_2>40&&pt_2<190", "region"),
                      Cut("trg_singletau_leading==1", "trg_selection")],
        "N_stdt_lead": [Cut("pt_1>190&&trkpt_1>50&&pt_2>40&&pt_2<190", "region"),
                        Cut("(trg_singletau_leading==1)&&((trg_doubletau_35_tightiso_tightid==1)||(trg_doubletau_40_mediso_tightid==1)||(trg_doubletau_40_tightiso==1))", "trg_selection")],
        "N_st_fullovlap": [Cut("pt_1>190&&trkpt_1>50&&pt_2>190&&trkpt_2>50", "region"),
                           Cut("((trg_singletau_leading==1)||(trg_singletau_trailing==1))", "trg_selection")],
        "N_stdt_fullovlap": [Cut("pt_1>190&&trkpt_1>50&&pt_2>190&&trkpt_2>50", "region"),
                             Cut("((trg_singletau_leading==1)||(trg_singletau_trailing==1))&&((trg_doubletau_35_tightiso_tightid==1)||(trg_doubletau_40_mediso_tightid==1)||(trg_doubletau_40_tightiso==1))", "trg_selection")],
    }

    # TODO: define constant variable or even a count.
    score = Variable(
            "phi_2",
            ConstantBinning(1, -10, 10),
            expression="phi_2")
    category = Category(
        "placeholder",
        tt,
        Cuts(),
        variable=score)
    tt_categories = []
    if "tt" in args.channels:
        for name, region in regions.iteritems():
            cat = deepcopy(category)
            cat.name = name
            cat.cuts.remove("trg_selection")
            for cut in region:
                cat.cuts.add(cut)
            tt_categories.append(cat)
    signal_nicks = [prod_mode+m for prod_mode in ["ggH", "bbH"] for m in susy_masses if not (prod_mode is "ggH" and m is "160")]

    # yapf: enable
    if "tt" in args.channels:
        for process, category in product(tt_processes.values(), tt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="mssm",
                    era=era,
                    variation=Nominal(),
                    mass="125"))


    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("singletau/{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
