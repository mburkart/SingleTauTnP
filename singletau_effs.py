#!/usr/bin/python
import argparse
import logging


import ROOT as root
import SingleTauEfficiency


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", type=str,
                        help="The directory the input files are located in.")
    parser.add_argument("-o", "--output", type=str, default="output.root",
                        help="Output file")
    parser.add_argument("-e", "--era", type=str,
                        help="Era.")
    parser.add_argument("-w", "--working-points", type=str, nargs="+",
                        choices={"loose", "medium", "tight",
                                 "vtight", "vvtight"},
                        default=["loose", "medium", "tight",
                                 "vtight", "vvtight"],
                        help="Working points to be processed.")
    parser.add_argument("-s", "--store-inputs", action="store_true",
                        help="Additionally store hists used in the "
                             "efficiency calculation.")
    return parser.parse_args()


def setup_logging(lev=logging.INFO):
    logging.basicConfig(level=lev)
    return


def main():
    setup_logging()
    args = parse_args()
    if args.store_inputs:
        raise NotImplementedError

    out_file = root.TFile(args.output, "recreate")
    for tau_type in ["genTau", "eFakes", "jetFakes"]:
        for sample_type in ["MC", "DATA"]:
            if tau_type == "genTau" and sample_type == "DATA":
                continue
            st_eff = SingleTauEfficiency.SingleTauEfficiency(
                         args.era, args.working_points,
                         args.input_dir,
                         tau_type, sample_type)
            st_eff.determine_efficiencies()
    out_file.Close()


if __name__ == "__main__":
    main()
