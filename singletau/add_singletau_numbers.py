#!/usr/bin/env/python

import argparse
import yaml
import os
from array import array

import ROOT as root
root.PyConfig.IgnoreCommandLineOptions = True
root.gErrorIgnoreLevel = root.kError


def parse_arguments():
    parser = argparse.ArgumentParser("Write number of triggered events to trees.")
    parser.add_argument("config", help="Path to the output directory.")
    parser.add_argument("estimation", help="The estimation method the numbers are used for.")
    parser.add_argument("input", help="Path to the input file.")
    parser.add_argument("tree", help="Tree in the input file.")
    return parser.parse_args()


def parse_config(filename):
    return yaml.load(open(filename, "r"))


def main(args):
    # Load the input file and the corresponding tree.
    file_input = root.TFile(args.input)
    if file_input is None:
        raise Exception("Requested input file {} does not exist.".format(
            args.input))

    tree_input = file_input.Get(args.tree)
    if tree_input is None:
        raise Exception("Tree {} does not exist in file {}.".format(
            args.tree, args.input))

    config = parse_config(args.config)
    basename = os.path.basename(os.path.dirname(args.input))
    output_directory = os.path.join(config["output_directory"], basename)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_filename = os.path.join(config["output_directory"], basename,
                                   "{}.root".format(basename))
    if os.path.exists(output_filename):
        file_output = root.TFile(output_filename, "update")
    else:
        file_output = root.TFile(output_filename, "recreate")
    tree_dir = os.path.dirname(args.tree)
    if file_output.mkdir(tree_dir) is None:
        raise Exception("Directory {} already exists in file {}".format(
                        tree_dir, args.input))
    file_output.cd(tree_dir)
    tree_output = root.TTree(os.path.basename(args.tree),
                             os.path.dirname(args.tree))

    # Add branches to the output tree.
    n_lead_ovlap_st = array("f", [-999])
    tree_output.Branch("N_st_lead_MC",
                       n_lead_ovlap_st,
                       "N_st_lead_MC/F")
    n_lead_ovlap_standdt = array("f", [-999])
    tree_output.Branch("N_stdt_lead_MC",
                       n_lead_ovlap_standdt,
                       "N_stdt_lead_MC/F")
    n_trail_ovlap_st = array("f", [-999])
    tree_output.Branch("N_st_trail_MC",
                       n_trail_ovlap_st,
                       "N_st_trail_MC/F")
    n_trail_ovlap_standdt = array("f", [-999])
    tree_output.Branch("N_stdt_trail_MC",
                       n_trail_ovlap_standdt,
                       "N_stdt_trail_MC/F")

    n_lead_ovlap_st_data = array("f", [-999])
    tree_output.Branch("N_st_lead_Data",
                       n_lead_ovlap_st_data,
                       "N_st_lead_Data/F")
    n_lead_ovlap_standdt_data = array("f", [-999])
    tree_output.Branch("N_stdt_lead_Data",
                       n_lead_ovlap_standdt_data,
                       "N_stdt_lead_Data/F")
    n_trail_ovlap_st_data = array("f", [-999])
    tree_output.Branch("N_st_trail_Data",
                       n_trail_ovlap_st_data,
                       "N_st_trail_Data/F")
    n_trail_ovlap_standdt_data = array("f", [-999])
    tree_output.Branch("N_stdt_trail_Data",
                       n_trail_ovlap_standdt_data,
                       "N_stdt_trail_Data/F")

    # Open shape output file.
    shape_input = root.TFile(config["shape_input"], "read")
    if shape_input is None:
        raise Exception("Shape inputs {} not found.".format(
                config["shape_input"]))
    # Get shape corresponding to estimation method and calculate the
    # number of events triggered by the single tau trigger and the overlap
    # with the di-tau trigger.
    # Note: we are using unweighted events to estimate the probability for
    #       the overlap.

    # Category names:  N_st_lead
    #                  N_stdt_lead
    #                  N_st_fullovlap
    #                  N_stdt_fullovlap
    name_template = "#tt#{{CATEGORY}}#{PROCESS}#mssm#Run2017ReReco31Mar#phi_2#125#".format(PROCESS=args.estimation)
    name_template_data = "#tt#{CATEGORY}#data_obs#mssm#Run2017ReReco31Mar#phi_2#125#"

    n_lead_ovlap_st[0] = shape_input.Get(
            name_template.format(CATEGORY="tt_N_st_lead")).GetEntries()
    n_lead_ovlap_standdt[0] = shape_input.Get(
            name_template.format(CATEGORY="tt_N_stdt_lead")).GetEntries()
    n_trail_ovlap_st[0] = shape_input.Get(
            name_template.format(CATEGORY="tt_N_st_fullovlap")).GetEntries()
    n_trail_ovlap_standdt[0] = shape_input.Get(
            name_template.format(CATEGORY="tt_N_stdt_fullovlap")).GetEntries()
    n_lead_ovlap_st_data[0] = shape_input.Get(
            name_template_data.format(CATEGORY="tt_N_st_lead")).GetEntries()
    n_lead_ovlap_standdt_data[0] = shape_input.Get(
            name_template_data.format(CATEGORY="tt_N_stdt_lead")).GetEntries()
    n_trail_ovlap_st_data[0] = shape_input.Get(
            name_template_data.format(CATEGORY="tt_N_st_fullovlap")).GetEntries()
    n_trail_ovlap_standdt_data[0] = shape_input.Get(
            name_template_data.format(CATEGORY="tt_N_stdt_fullovlap")).GetEntries()

    # Loop over events and add the numbers to the tree.
    for i_event in xrange(tree_input.GetEntries()):
        tree_input.GetEntry(i_event)

        tree_output.Fill()

    file_input.Close()
    file_output.Write()
    file_output.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
