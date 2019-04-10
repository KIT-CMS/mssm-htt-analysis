#!/usr/bin/env python

import argparse
import yaml
import os
import logging

import ROOT as root
root.PyConfig.IgnoreCommandLineOptions = True

from shape_producer.channel import *
from shape_producer.era import *


logger = logging.getLogger("write_application_filelist")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    logger.debug("Parsing arguments.")
    parser = argparse.ArgumentParser(
            description="Create file dict to include numbers depending on trigger path.")
    parser.add_argument("--directory", required=True, help="Path to Artus output files.")
    parser.add_argument("--database", required=True, help="Path to Kappa database.")
    parser.add_argument("--era", required=True, help="Experiment era.")
    parser.add_argument("--channel", required=True, help="Analysis channel.")
    parser.add_argument("--output", required=True, help="Output filelist.")
    return parser.parse_args()


def main(args):
    susy_masses = ["80", "90", "100", "110", "120", "130", "140", "160", "180", "200", "250", "300", "350", "400", "450", "600", "700", "800", "900", "1200", "1400", "1500", "1600", "1800", "2000", "2300", "2600", "2900", "3200"]
    filelist = {}
    if "2017" in args.era:
        from shape_producer.estimation_methods_Fall17 import DataEstimation, DYJetsToLLEstimation, ZTTEmbeddedEstimation, TTEstimation, VVTEstimation, WEstimation, EWKZEstimation, SUSYggHEstimation, SUSYbbHEstimation, VVEstimation, DYJetsToLLEstimation
        from shape_producer.era import Run2017
        era = Run2017(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    if "2017" in args.era and args.channel == "tt":
        channel = TTMSSM2017()
        estimations = {"DYJetsToLL": DYJetsToLLEstimation(era, args.directory, channel),
                       "EMB": ZTTEmbeddedEstimation(era, args.directory, channel),
                       "TT": TTEstimation(era, args.directory, channel),
                       "W": WEstimation(era, args.directory, channel),
                       "VV": VVEstimation(era, args.directory, channel),
                       "data_obs": DataEstimation(era, args.directory, channel),
        }
        for mass in susy_masses:
            estimations["bbH"+mass] = SUSYbbHEstimation(era, args.directory, channel, mass)
            if mass != "160":
                estimations["ggH"+mass] = SUSYggHEstimation(era, args.directory, channel, mass)
        for key, estimation in estimations.iteritems():
            filelist[key] = {}
            logger.debug("Get files for estimation method %s.", estimation.name)

            files = [str(f) for f in estimation.get_files()]

            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File %s does not exist", f)
                    raise Exception

                folders = []
                f_ = root.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[key][f] = folders

    logger.info("Write filelist to file: {}".format(args.output))
    yaml.dump(filelist, open(args.output, "w"), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
