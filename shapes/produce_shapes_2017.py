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
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing friend trees to data files with fake factors."
    )
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--binning", required=True, type=str, help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--control", action="store_true",
            help="Produce shapes for control plots.")
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
    parser.add_argument(
        "--skip-systematic-variations",
        default=False,
        type=str,
        help="Do not produce the systematic variations.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "{}_shapes.root".format(args.tag),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2017" in args.era:
        from shape_producer.estimation_methods_Fall17 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, FakeEstimationLT, NewFakeEstimationLT, FakeEstimationTT, NewFakeEstimationTT, SUSYggHEstimation, SUSYbbHEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    ff_friend_directory = args.fake_factor_friend_directory
    susy_masses = ["80", "90", "100", "110", "120", "130", "140", "160", "180", "200", "250", "300", "350", "400", "450", "600", "700", "800", "900", "1200", "1400", "1500", "1600", "1800", "2000", "2300", "2600", "2900", "3200"]
    mt = MTMSSM2017()
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mt, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mt, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, mt, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, mt, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mt, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mt, friend_directory=[])),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, mt, friend_directory=[])),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mt, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mt, friend_directory=[])),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, mt, friend_directory=[])),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mt, friend_directory=[])),
        "W"     : Process("W",        WEstimation         (era, directory, mt, friend_directory=[])),
        #"FAKES" : Process("jetFakes", FakeEstimationLT    (era, directory, mt, friend_directory=[mt_friend_directory, ff_friend_directory])),
        }
    #mt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=[mt_friend_directory, ff_friend_directory]))
    #mt_fakes_for_uncs=Process("jetFakes", FakeEstimationLT(era, directory, mt, friend_directory=[mt_friend_directory, ff_friend_directory]))
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            mt_processes["data"], friend_directory=[], extrapolation_factor=1.00))
    mt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            mt_processes["data"], friend_directory=[], extrapolation_factor=1.00))
    for m in susy_masses:
        if m != "160":
            mt_processes["ggH"+m] = Process("ggH"+m, SUSYggHEstimation    (era, directory, mt, m, friend_directory=[])) 
        mt_processes["bbH"+m] = Process("bbH"+m, SUSYbbHEstimation    (era, directory, mt, m, friend_directory=[])) 

    et = ETMSSM2017()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, et, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, et, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, et, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, et, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, et, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, et, friend_directory=[])),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, et, friend_directory=[])),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, et, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, et, friend_directory=[])),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, et, friend_directory=[])),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, et, friend_directory=[])),
        "W"     : Process("W",        WEstimation         (era, directory, et, friend_directory=[])),
        #"FAKES" : Process("jetFakes", FakeEstimationLT    (era, directory, et, friend_directory=[et_friend_directory, ff_friend_directory])),
        }
    #et_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], et_processes["data"], friend_directory=[et_friend_directory, ff_friend_directory]))
    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=[], extrapolation_factor=1.00))
    et_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=[], extrapolation_factor=1.00))
    for m in susy_masses:
        if m != "160":
            et_processes["ggH"+m] = Process("ggH"+m, SUSYggHEstimation    (era, directory, et, m, friend_directory=[])) 
        et_processes["bbH"+m] = Process("bbH"+m, SUSYbbHEstimation    (era, directory, et, m, friend_directory=[])) 

    tt = TTMSSM2017()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, tt, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, tt, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, tt, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, tt, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, tt, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, tt, friend_directory=[])),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, tt, friend_directory=[])),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, tt, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, tt, friend_directory=[])),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, tt, friend_directory=[])),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, tt, friend_directory=[])),
        "W"     : Process("W",        WEstimation         (era, directory, tt, friend_directory=[])),
        #"FAKES" : Process("jetFakes", FakeEstimationTT    (era, directory, tt, friend_directory=[tt_friend_directory, ff_friend_directory])),
        }
    #tt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], tt_processes["data"], friend_directory=[tt_friend_directory, ff_friend_directory]))
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=[]))
    tt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=[]))
    for m in susy_masses:
        if m != "160":
            tt_processes["ggH"+m] = Process("ggH"+m, SUSYggHEstimation    (era, directory, tt, m, friend_directory=[])) 
        tt_processes["bbH"+m] = Process("bbH"+m, SUSYbbHEstimation    (era, directory, tt, m, friend_directory=[])) 

    # Variables and categories
    binning = yaml.load(open(args.binning))

    et_categories = []
    # Analysis shapes
    if "et" in args.channels:
        if args.control:
            for variable in binning["control"]["et"]:
                score = Variable(
                        variable,
                        VariableBinning(binning["control"]["et"][variable]["bins"]),
                        expression=binning["control"]["et"][variable]["expression"])
                if "cut" in binning["control"]["et"][variable].keys():
                    cuts=Cuts(Cut(binning["control"]["et"][variable]["cut"], "binning"))
                else:
                    cuts=Cuts()
                et_categories.append(
                    Category(
                        variable,
                        et,
                        cuts,
                        variable=score))
        else:
            for cat in binning["categories"]["et"]:
                category = Category(
                            cat,
                            et,
                            Cuts(Cut(binning["categories"]["et"][cat]["cuts"], "category")),
                            variable=Variable(binning["categories"]["et"][cat]["var"],
                                VariableBinning(binning["categories"]["et"][cat]["bins"]),
                                expression=binning["categories"]["et"][cat]["expression"]))
                # If category is ss wjets or qcd control region change sign cut
                if "_qcd_" in cat or "_ss_" in cat:
                    category.cuts.remove("os")
                    category.cuts.add(Cut("q_1*q_2>0", "os"))
                et_categories.append(category)

    mt_categories = []
    if "mt" in args.channels:
        if args.control:
            for variable in binning["control"]["mt"]:
                score = Variable(
                        variable,
                        VariableBinning(binning["control"]["mt"][variable]["bins"]),
                        expression=binning["control"]["mt"][variable]["expression"])
                if "cut" in binning["control"]["mt"][variable].keys():
                    cuts=Cuts(Cut(binning["control"]["mt"][variable]["cut"], "binning"))
                else:
                    cuts=Cuts()
                mt_categories.append(
                    Category(
                        variable,
                        mt,
                        cuts,
                        variable=score))
        else:
            for cat in binning["categories"]["mt"]:
                if cat == "nobtag_tight_qcd_cr":
                    category = Category(
                                cat,
                                mt,
                                Cuts(Cut(binning["categories"]["mt"][cat]["cuts"], "category")),
                                variable=Variable(binning["categories"]["mt"][cat]["var"],
                                    VariableBinning(binning["categories"]["mt"][cat]["bins"]),
                                    expression=binning["categories"]["mt"][cat]["expression"]))
                    # If category is ss wjets or qcd control region change sign cut
                    if "_qcd_" in cat or "_ss_" in cat:
                        category.cuts.remove("os")
                        category.cuts.add(Cut("q_1*q_2>0", "os"))
                    mt_categories.append(category)

    tt_categories = []
    if "tt" in args.channels:
        if args.control:
            for variable in binning["control"]["tt"]:
                score = Variable(
                        variable,
                        VariableBinning(binning["control"]["tt"][variable]["bins"]),
                        expression=binning["control"]["tt"][variable]["expression"])
                if "cut" in binning["control"]["tt"][variable].keys():
                    cuts=Cuts(Cut(binning["control"]["tt"][variable]["cut"], "binning"))
                else:
                    cuts=Cuts()
                tt_categories.append(
                    Category(
                        variable,
                        tt,
                        cuts,
                        variable=score))
        else:
            for cat in binning["categories"]["tt"]:
                tt_categories.append(
                        Category(
                            cat,
                            tt,
                            Cuts(Cut(binning["categories"]["tt"][cat]["cuts"], "category")),
                            variable=Variable(binning["categories"]["tt"][cat]["var"],
                                VariableBinning(binning["categories"]["tt"][cat]["bins"]),
                                expression=binning["categories"]["tt"][cat]["expression"])))
        #if "et" in args.channels:
        #    classes_et = ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]
        #    for i, label in enumerate(classes_et):
        #        score = Variable(
        #            "et_max_score",
        #             VariableBinning(binning["analysis"]["et"][label]))
        #        et_categories.append(
        #            Category(
        #                label,
        #                et,
        #                Cuts(
        #                    Cut("et_max_index=={index}".format(index=i), "exclusive_score")),
        #                variable=score))
        #        if label in ["ggh", "qqh"]:
        #            expression = ""
        #            for i_e, e in enumerate(binning["stxs_stage1"][label]):
        #                offset = (binning["analysis"]["et"][label][-1]-binning["analysis"]["et"][label][0])*i_e
        #                expression += "{STXSBIN}*(et_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
        #                if not e is binning["stxs_stage1"][label][-1]:
        #                    expression += " + "
        #            score_unrolled = Variable(
        #                "et_max_score_unrolled",
        #                 VariableBinning(binning["analysis"]["et"][label+"_unrolled"]),
        #                 expression=expression)
        #            et_categories.append(
        #                Category(
        #                    "{}_unrolled".format(label),
        #                    et,
        #                    Cuts(Cut("et_max_index=={index}".format(index=i), "exclusive_score"),
        #                         Cut("et_max_score>{}".format(1.0/len(classes_et)), "protect_unrolling")),
        #                    variable=score_unrolled))
        # Goodness of fit shapes


    # Nominal histograms
    #if args.gof_channel == None:
    #    signal_nicks = [
    #        "ggH", "qqH", "qqH_VBFTOPO_JET3VETO", "qqH_VBFTOPO_JET3",
    #        "qqH_REST", "qqH_PTJET1_GT200", "qqH_VH2JET", "ggH_0J",
    #        "ggH_1J_PTH_0_60", "ggH_1J_PTH_60_120", "ggH_1J_PTH_120_200",
    #        "ggH_1J_PTH_GT200", "ggH_GE2J_PTH_0_60", "ggH_GE2J_PTH_60_120",
    #        "ggH_GE2J_PTH_120_200", "ggH_GE2J_PTH_GT200", "ggH_VBFTOPO_JET3VETO",
    #        "ggH_VBFTOPO_JET3", "VH", "WH", "ZH"
    #    ]
    #else:
    #    signal_nicks = ["ggH", "qqH"]
    signal_nicks = [prod_mode+m for prod_mode in ["ggH", "bbH"] for m in susy_masses if not (prod_mode is "ggH" and m is "160")]

    # yapf: enable
    if "et" in args.channels:
        for process, category in product(et_processes.values(), et_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="mssm",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "mt" in args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="mssm",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
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

    # Shapes variations

    # MC tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_3prong_Run2017", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong_Run2017", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong1pizero_Run2017", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVL", "VVT"#, "FAKES"
                             ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong_Run2017", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong_Run2017", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pizero_Run2017", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVT", "VVL", "EMB"#, "FAKES"
                             ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Jet energy scale

    # Inclusive JES shapes
    jet_es_variations = []
    '''jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Run2017", "jecUnc", DifferentPipeline)'''

    # Splitted JES shapes
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to3_Run2017", "jecUncEta0to3", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to5_Run2017", "jecUncEta0to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta3to5_Run2017", "jecUncEta3to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal_Run2017", "jecUncRelativeBal",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_Run2017", "jecUncRelativeSample",
        DifferentPipeline)

    for variation in jet_es_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL"
        ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # MET energy scale
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn",
        DifferentPipeline)
    for variation in met_unclustered_variations:  # + met_clustered_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL"
        ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met", "metRecoilResolution",
        DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met", "metRecoilResponse",
        DifferentPipeline)
    for variation in recoil_resolution_variations + recoil_response_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W"] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_Run2017", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process_nick in ["ZTT", "ZL", "ZJ"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight",
        SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process_nick in ["TTT", "TTL", "TTJ"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # jet to tau fake efficiency
    jet_to_tau_fake_variations = []
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2017", "jetToTauFake_weight",
                  Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"), "Up"))
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2017", "jetToTauFake_weight",
                  Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"), "Down"))
    for variation in jet_to_tau_fake_variations:
        for process_nick in ["ZJ", "TTJ", "W", "VVJ"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # ZL fakes energy scale
    ele_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong_Run2017", "tauEleFakeEsOneProng",
        DifferentPipeline)
    ele_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_Run2017", "tauEleFakeEsOneProngPiZeros",
        DifferentPipeline)

    if "et" in args.channels:
        for process_nick in ["ZL"]:
            for variation in ele_fake_es_1prong_variations + ele_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run2017", "tauMuFakeEsOneProng",
        DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run2017", "tauMuFakeEsOneProngPiZeros",
        DifferentPipeline)

    if "mt" in args.channels:
        for process_nick in ["ZL"]:
            for variation in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # lepton trigger efficiency
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2017", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2017", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_mt_Run2017", "xtrg_mt_eff_weight",
                  Weight("(1.07*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_mt_Run2017", "xtrg_mt_eff_weight",
                  Weight("(0.93*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ"
        ] + signal_nicks:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2017", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2017", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_mt_Run2017", "xtrg_mt_eff_weight",
                  Weight("(1.07*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_mt_Run2017", "xtrg_mt_eff_weight",
                  Weight("(0.93*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_et_Run2017", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))", "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_et_Run2017", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))", "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_et_Run2017", "xtrg_et_eff_weight",
                  Weight("(1.07*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_et_Run2017", "xtrg_et_eff_weight",
                  Weight("(0.93*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ"
        ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_et_Run2017", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))", "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_et_Run2017", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))", "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_et_Run2017", "xtrg_et_eff_weight",
                  Weight("(1.07*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_et_Run2017", "xtrg_et_eff_weight",
                  Weight("(0.93*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    # Zll reweighting !!! replaced by log normal uncertainties: CMS_eFakeTau_Run2017 16%; CMS_mFakeTau_Run2017 26%
    '''zll_et_weight_variations = []
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run2017", "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*2.0/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*2.06) + ((abs(eta_1) >= 1.558)*2.13/1.53))",
                "eFakeTau_reweight"), "Up"))
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run2017", "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*1.6/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*1.27) + ((abs(eta_1) >= 1.558)*0.93/1.53))",
                "eFakeTau_reweight"), "Down"))
    for variation in zll_et_weight_variations:
        for process_nick in ["ZL"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    zll_mt_weight_variations = []
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run2017", "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.29/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*1.59/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.19/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*1.53/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*2.21/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Up"))
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run2017", "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.05/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*0.99/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.09/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*0.33/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*1.01/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Down"))
    for variation in zll_mt_weight_variations:
        for process_nick in ["ZL"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)'''

    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b_Run2017", "btagEff", DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b_Run2017", "btagMistag", DifferentPipeline)
    for variation in btag_eff_variations + mistag_eff_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL"
        ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Embedded event specifics
    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_3prong_Run2017", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong_Run2017", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong1pizero_Run2017", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["EMB"]:#, "FAKES"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    mt_decayMode_variations = []
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in mt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    et_decayMode_variations = []
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in et_decayMode_variations:
        for process_nick in ["EMB"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    tt_decayMode_variations = []
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2017", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in tt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to ZTT shape to use as systematic
    tttautau_process_mt = Process(
        "TTT",
        TTTEstimation(
            era, directory, mt, friend_directory=[]))
    tttautau_process_et = Process(
        "TTT",
        TTTEstimation(
            era, directory, et, friend_directory=[]))
    tttautau_process_tt = Process(
        "TTT",
        TTTEstimation(
            era, directory, tt, friend_directory=[]))
    if 'mt' in args.channels:
        for category in mt_categories:
            mt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauDown'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                    mass="125"))

            mt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauUp'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                    mass="125"))

    if "et" in args.channels:
        for category in et_categories:
            et_processes["ZTTpTTTauTauDown"] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauDown'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                    mass="125"))

            et_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauUp'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                    mass="125"))
    if 'tt' in args.channels:
        for category in tt_categories:
            tt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "EMB", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauDown'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                    mass="125"))

            tt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauUp'],
                    analysis="mssm",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                    mass="125"))

    # jetfakes
    #fake_factor_variations_et = []
    #fake_factor_variations_mt = []
    #for systematic_shift in [
    #        "ff_qcd{ch}_syst_Run2017{shift}",
    #        "ff_qcd_dm0_njet0{ch}_stat_Run2017{shift}",
    #        "ff_qcd_dm0_njet1{ch}_stat_Run2017{shift}",
    #        #"ff_qcd_dm1_njet0{ch}_stat_Run2017{shift}",
    #        #"ff_qcd_dm1_njet1{ch}_stat_Run2017{shift}",
    #        "ff_w_syst_Run2017{shift}",
    #        "ff_w_dm0_njet0{ch}_stat_Run2017{shift}",
    #        "ff_w_dm0_njet1{ch}_stat_Run2017{shift}",
    #        #"ff_w_dm1_njet0{ch}_stat_Run2017{shift}",
    #        #"ff_w_dm1_njet1{ch}_stat_Run2017{shift}",
    #        "ff_tt_syst_Run2017{shift}",
    #        "ff_tt_dm0_njet0_stat_Run2017{shift}",
    #        "ff_tt_dm0_njet1_stat_Run2017{shift}",
    #        #"ff_tt_dm1_njet0_stat_Run2017{shift}",
    #        #"ff_tt_dm1_njet1_stat_Run2017{shift}"
    #]:
    #    for shift_direction in ["Up", "Down"]:
    #        fake_factor_variations_et.append(
    #            ReplaceWeight(
    #                "CMS_%s" % (systematic_shift.format(ch='_et', shift="").replace("_dm0", "")),
    #                "fake_factor",
    #                Weight(
    #                    "ff2_{syst}".format(
    #                        syst=systematic_shift.format(
    #                            ch="", shift="_%s" % shift_direction.lower())
    #                        .replace("_Run2017", "")),
    #                    "fake_factor"), shift_direction))
    #        fake_factor_variations_mt.append(
    #            ReplaceWeight(
    #                "CMS_%s" % (systematic_shift.format(ch='_mt', shift="").replace("_dm0", "")),
    #                "fake_factor",
    #                Weight(
    #                    "ff2_{syst}".format(
    #                        syst=systematic_shift.format(
    #                            ch="", shift="_%s" % shift_direction.lower())
    #                        .replace("_Run2017", "")),
    #                    "fake_factor"), shift_direction))
    #if "et" in args.channels:
    #    for variation in fake_factor_variations_et:
    #        systematics.add_systematic_variation(
    #            variation=variation,
    #            process=et_processes["FAKES"],
    #            channel=et,
    #            era=era)
    #if "mt" in args.channels:
    #    for variation in fake_factor_variations_mt:
    #        systematics.add_systematic_variation(
    #            variation=variation,
    #            process=mt_processes["FAKES"],
    #            channel=mt,
    #            era=era)
    #fake_factor_variations_tt = []
    #for systematic_shift in [
    #        "ff_qcd{ch}_syst_Run2017{shift}",
    #        "ff_qcd_dm0_njet0{ch}_stat_Run2017{shift}",
    #        "ff_qcd_dm0_njet1{ch}_stat_Run2017{shift}",
    #        #"ff_qcd_dm1_njet0{ch}_stat_Run2017{shift}",
    #        #"ff_qcd_dm1_njet1{ch}_stat_Run2017{shift}",
    #        "ff_w{ch}_syst_Run2017{shift}", "ff_tt{ch}_syst_Run2017{shift}",
    #        "ff_w_frac{ch}_syst_Run2017{shift}",
    #        "ff_tt_frac{ch}_syst_Run2017{shift}"
    #]:
    #    for shift_direction in ["Up", "Down"]:
    #        fake_factor_variations_tt.append(
    #            ReplaceWeight(
    #                "CMS_%s" % (systematic_shift.format(ch='_tt', shift="").replace("_dm0", "")),
    #                "fake_factor",
    #                Weight(
    #                    "(0.5*ff1_{syst}*(byTightIsolationMVArun2017v2DBoldDMwLT2017_1<0.5)+0.5*ff2_{syst}*(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5))".
    #                    format(
    #                        syst=systematic_shift.format(
    #                            ch="", shift="_%s" % shift_direction.lower())
    #                        .replace("_Run2017", "")),
    #                    "fake_factor"), shift_direction))
    #if "tt" in args.channels:
    #    for variation in fake_factor_variations_tt:
    #        systematics.add_systematic_variation(
    #            variation=variation,
    #            process=tt_processes["FAKES"],
    #            channel=tt,
    #            era=era)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
